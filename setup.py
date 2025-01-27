from setuptools import setup, find_packages

setup(
    name="synexa",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "httpx>=0.24.0",
    ],
    author="Synexa",
    author_email="support@synexa.ai",
    description="Python client for Synexa AI API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://synexa.ai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
