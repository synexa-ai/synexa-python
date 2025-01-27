import os
import asyncio
import synexa

# Set your API key
os.environ["SYNEXA_API_KEY"] = "YOUR_API_KEY"  # Replace with your actual API key

def sync_example():
    """Example of synchronous usage"""
    # Basic usage
    output = synexa.run(
        "black-forest-labs/flux-schnell",
        input={"prompt": "An astronaut riding a rainbow unicorn, cinematic, dramatic"}
    )

    # Save the generated image
    for i, img in enumerate(output):
        with open(f'output_{i}.webp', 'wb') as f:
            f.write(img.read())
        print(f"Image saved as output_{i}.webp")

    # Example with custom timeout
    try:
        output = synexa.run(
            "black-forest-labs/flux-schnell",
            input={"prompt": "A space station orbiting Earth"},
            wait=30  # 30 second timeout
        )
    except TimeoutError as e:
        print(f"Prediction timed out: {e}")

    # Run in background (non-blocking)
    prediction = synexa.client.predictions.create(
        model="black-forest-labs/flux-schnell",
        input={"prompt": "A futuristic city at night"}
    )
    print(f"Started prediction: {prediction.id}")
    
    # Check status
    prediction.reload()
    print(f"Status: {prediction.status}")
    
    # Wait for completion
    try:
        prediction.wait()
        print("Prediction completed!")
    except synexa.ModelError as e:
        print(f"Prediction failed: {e}")

    # Stream logs and output
    for event in synexa.stream(
        "black-forest-labs/flux-schnell",
        input={"prompt": "A cyberpunk street scene"}
    ):
        print(str(event), end="")

async def async_example():
    """Example of async usage"""
    # Run multiple predictions concurrently
    prompts = [
        f"A {animal} in space"
        for animal in ["cat", "dog", "rabbit", "hamster"]
    ]

    # Create tasks for concurrent execution
    tasks = [
        synexa.async_run(
            "black-forest-labs/flux-schnell",
            input={"prompt": prompt}
        )
        for prompt in prompts
    ]

    # Run all tasks concurrently
    results = await asyncio.gather(*tasks)
    print(f"Generated {len(results)} images")

    # Save the generated images
    for i, result in enumerate(results):
        for j, img in enumerate(result):
            with open(f'async_output_{i}_{j}.webp', 'wb') as f:
                f.write(img.read())
            print(f"Saved async_output_{i}_{j}.webp")

if __name__ == "__main__":
    # Run sync example
    sync_example()
    
    # Run async example
    asyncio.run(async_example())
