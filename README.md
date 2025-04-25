# CodeFast AI Client

A Python client library for interacting with the CodeFast AI v2 API (specifically token generation and file upload).

## Installation

You can install this package directly from GitHub using pip:

```bash
pip install git+https://github.com/Kroy665/es-client.git
```

## Usage

```python
from es_client import CodeFastClient

client = CodeFastClient(email="your_email@example.com", team_slug="your_team_slug", api_key="your_api_key")

# Get token 
client._get_token()

# Upload file
client.upload_file(file_path="path/to/your/file.txt", file_name="file.txt", file_content=None)

# Upload file from bytes
client.upload_file(file_path=None, file_name="file.txt", file_content=b"This is a test file.")

# Upload file from string
client.upload_file(file_path=None, file_name="file.txt", file_content="This is a test file.")
```

