# Synexa Python Client

This is a Python client for [Synexa AI](https://synexa.ai). It lets you run AI models from your Python code or Jupyter notebook.

## Requirements

- Python 3.8+

## Installation

```sh
pip install synexa
```

## Authentication

Before running any Python scripts that use the API, you need to set your Synexa API key in your environment:

```sh
export SYNEXA_API_KEY=your-api-key
```

Alternatively, you can pass the API key directly when creating a client:

```python
client = synexa.Synexa(api_key="your-api-key")
```

## Usage

Here's a simple example of how to use the client:

```python
import synexa

# Run a model
output = synexa.run(
    "black-forest-labs/flux-schnell",
    input={"prompt": "An astronaut riding a rainbow unicorn, cinematic, dramatic"}
)

# Save the generated image
for i, img in enumerate(output):
    with open(f'output_{i}.webp', 'wb') as f:
        f.write(img.read())
```

### Async Support

The client supports both synchronous and asynchronous operations. By default, it will wait for the prediction to complete (up to 60 seconds). You can modify this behavior:

```python
# Don't wait for completion
output = synexa.run(
    "black-forest-labs/flux-schnell",
    input={"prompt": "An astronaut riding a rainbow unicorn"},
    wait=False
)

# Wait with custom timeout (in seconds)
output = synexa.run(
    "black-forest-labs/flux-schnell",
    input={"prompt": "An astronaut riding a rainbow unicorn"},
    wait=30
)
```

### Error Handling

The client will raise exceptions for various error conditions:

- `ModelError`: Raised when the prediction fails
- `TimeoutError`: Raised when the prediction doesn't complete within the specified timeout
- `ValueError`: Raised when required parameters are missing or invalid
- `httpx.HTTPError`: Raised for HTTP-related errors

Example error handling:

```python
from synexa import ModelError

try:
    output = synexa.run(
        "black-forest-labs/flux-schnell",
        input={"prompt": "An astronaut riding a rainbow unicorn"}
    )
except ModelError as e:
    print(f"Prediction failed: {e}")
    if e.prediction:
        print(f"Prediction ID: {e.prediction['id']}")
```

## License

MIT License
