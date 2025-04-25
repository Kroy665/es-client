# src/codefast_client/__init__.py

# Make the main class and exceptions available when the package is imported
from .client import CodeFastClient, CodeFastError, AuthenticationError, UploadError

# Define the package version (read dynamically or defined here)
# Option 1: Define directly
__version__ = "0.1.0"

# Option 2 (More robust, requires Python 3.8+): Read from pyproject.toml
# import importlib.metadata
# try:
#     __version__ = importlib.metadata.version("codefast_client") # Use the 'name' from pyproject.toml
# except importlib.metadata.PackageNotFoundError:
#     __version__ = "0.0.0" # Default if not installed