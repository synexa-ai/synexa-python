import os
import time
import json
import asyncio
import httpx
from typing import Dict, List, Optional, Union, AsyncIterator, Iterator
from dataclasses import dataclass

@dataclass
class FileOutput:
    url: str
    _client: httpx.Client = None

    def __post_init__(self):
        self._client = httpx.Client()

    def read(self) -> bytes:
        response = self._client.get(self.url)
        response.raise_for_status()
        return response.content

class ModelError(Exception):
    def __init__(self, message: str, prediction: Dict = None):
        super().__init__(message)
        self.prediction = prediction

class Prediction:
    def __init__(self, data: Dict, client):
        self._data = data
        self._client = client
        
    def __getattr__(self, name):
        return self._data.get(name)
        
    def __dict__(self):
        return self._data
        
    def reload(self):
        """Refresh the prediction's data from the API."""
        response = httpx.get(
            f"{self._client.base_url}/predictions/{self.id}",
            headers=self._client.headers
        )
        response.raise_for_status()
        self._data = response.json()
        return self
        
    def wait(self, timeout: int = 60):
        """Wait for the prediction to complete."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.reload()
            if self.status == "succeeded":
                return self
            if self.status == "failed":
                raise ModelError(f"Prediction failed: {self.error}", self._data)
            time.sleep(1)
        raise TimeoutError(f"Prediction did not complete within {timeout} seconds")

    def stream(self) -> Iterator[str]:
        """Stream the prediction output."""
        while True:
            self.reload()
            if self.status == "succeeded":
                for output in self.output:
                    yield output
                break
            if self.status == "failed":
                raise ModelError(f"Prediction failed: {self.error}", self._data)
            if self.logs:
                yield self.logs
            time.sleep(0.1)

class Predictions:
    def __init__(self, client):
        self._client = client

    def create(
        self,
        model: str,
        input: Dict,
        stream: bool = False,
    ) -> Union[Prediction, Iterator[str]]:
        """Create a new prediction."""
        response = httpx.post(
            f"{self._client.base_url}/predictions",
            headers=self._client.headers,
            json={"model": model, "input": input}
        )
        response.raise_for_status()
        prediction = Prediction(response.json(), self._client)
        
        if stream:
            return prediction.stream()
        return prediction

class Synexa:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("SYNEXA_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in SYNEXA_API_KEY environment variable")
        
        self.base_url = "https://api.synexa.ai/v1"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        self.predictions = Predictions(self)

    def run(
        self,
        model: str,
        input: Dict,
        wait: Union[bool, int] = True,
        use_file_output: bool = True
    ) -> Union[List[FileOutput], List[str]]:
        """
        Run a prediction on the specified model.
        
        Args:
            model: The model identifier (e.g., "black-forest-labs/flux-schnell")
            input: Dictionary of input parameters
            wait: If True or int, wait for prediction to complete. If int, specifies timeout in seconds.
            use_file_output: If True, return FileOutput objects. If False, return URLs as strings.
        
        Returns:
            List of FileOutput objects or URLs depending on use_file_output parameter
        """
        prediction = self.predictions.create(model=model, input=input)
        
        if not wait:
            return []

        # Wait for completion
        timeout = 60 if wait is True else wait
        prediction.wait(timeout)
        
        if use_file_output:
            return [FileOutput(url) for url in prediction.output]
        return prediction.output

    async def async_run(
        self,
        model: str,
        input: Dict,
        wait: Union[bool, int] = True,
        use_file_output: bool = True
    ) -> Union[List[FileOutput], List[str]]:
        """Async version of run()."""
        async with httpx.AsyncClient() as client:
            # Create prediction
            response = await client.post(
                f"{self.base_url}/predictions",
                headers=self.headers,
                json={"model": model, "input": input}
            )
            response.raise_for_status()
            prediction_data = response.json()
            
            if not wait:
                return []

            # Wait for completion
            timeout = 60 if wait is True else wait
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                response = await client.get(
                    f"{self.base_url}/predictions/{prediction_data['id']}",
                    headers=self.headers
                )
                response.raise_for_status()
                prediction_data = response.json()

                if prediction_data["status"] == "succeeded":
                    if use_file_output:
                        return [FileOutput(url) for url in prediction_data["output"]]
                    return prediction_data["output"]
                
                if prediction_data["status"] == "failed":
                    raise ModelError(f"Prediction failed: {prediction_data.get('error')}", prediction_data)
                
                await asyncio.sleep(1)
                
            raise TimeoutError(f"Prediction did not complete within {timeout} seconds")

    def stream(
        self,
        model: str,
        input: Dict,
    ) -> Iterator[str]:
        """Stream output from a prediction."""
        return self.predictions.create(model=model, input=input, stream=True)

# Create default client
client = Synexa()

# Convenience functions to use default client
def run(*args, **kwargs):
    return client.run(*args, **kwargs)

async def async_run(*args, **kwargs):
    return await client.async_run(*args, **kwargs)

def stream(*args, **kwargs):
    return client.stream(*args, **kwargs)
