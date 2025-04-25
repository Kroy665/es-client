# src/codefast_client/client.py

import requests
import json
import os
import logging # Use logging instead of print for libraries
from typing import Union

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Custom Exceptions for better error handling
class CodeFastError(Exception):
    """Base exception for CodeFastClient errors."""
    pass

class AuthenticationError(CodeFastError):
    """Raised when authentication fails."""
    pass

class UploadError(CodeFastError):
    """Raised when file upload fails."""
    pass

class CodeFastClient:
    """
    A client for interacting with the CodeFast AI v2 API.

    Args:
        email (str): User email for authentication.
        team_slug (str): Team slug for authentication.
        api_key (str): API key for authentication.
        base_url (str, optional): The base URL for the CodeFast API.
                                   Defaults to 'https://dev-ai-v2.codefast.ai'.
    """
    DEFAULT_BASE_URL = 'https://dev-ai-v2.codefast.ai'
    TOKEN_ENDPOINT = '/token'
    UPLOAD_ENDPOINT = '/api/v2/es/upload'

    def __init__(self, email: str, team_slug: str, api_key: str, base_url: str = None):
        if not all([email, team_slug, api_key]):
            raise ValueError("Email, team_slug, and api_key must be provided.")

        self.email = email
        self.team_slug = team_slug
        self.api_key = api_key
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self._token = None
        log.info(f"CodeFastClient initialized for email {self.email} on {self.base_url}")

    def _get_token(self) -> str:
        """
        Retrieves the authentication token from the API.
        Caches the token internally.

        Returns:
            str: The access token.

        Raises:
            AuthenticationError: If token retrieval fails.
        """
        # Simple caching - could add expiry check later if needed
        if self._token:
            return self._token

        token_url = self.base_url + self.TOKEN_ENDPOINT
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        payload = {
            "email": self.email,
            "teamSlug": self.team_slug,
            "apikey": self.api_key
        }

        log.info(f"Requesting token from {token_url} for {self.email}")
        try:
            response = requests.post(token_url, headers=headers, json=payload)
            response.raise_for_status() # Raises HTTPError for bad status codes

            try:
                response_data = response.json()
                token = response_data.get("access_token")
                if not token:
                    log.error(f"Token retrieval failed: 'access_token' not in response. Response: {response.text}")
                    raise AuthenticationError("'access_token' not found in API response.")
                self._token = token
                log.info("Successfully retrieved access token.")
                return self._token
            except json.JSONDecodeError:
                log.error(f"Failed to decode JSON response from token endpoint: {response.text}")
                raise AuthenticationError("Invalid JSON response received from token endpoint.")

        except requests.exceptions.RequestException as e:
            log.error(f"Network error during token request: {e}", exc_info=True)
            raise AuthenticationError(f"Network error occurred during authentication: {e}") from e
        except Exception as e:
            log.error(f"An unexpected error occurred during token retrieval: {e}", exc_info=True)
            raise AuthenticationError(f"An unexpected error occurred during authentication: {e}") from e


    def upload_file(self, file_path: str = None, file_name: str = None, file_content: Union[str, bytes] = None) -> dict:
        """
        Uploads a file to the CodeFast API.

        Args:
            file_path (str, optional): The path to the file to upload. Defaults to None.
            file_name (str, optional): The name of the file to upload. Defaults to None.
            file_content (str, optional): The content of the file to upload. Defaults to None.

        Returns:
            dict: The JSON response from the server upon successful upload.

        Raises:
            FileNotFoundError: If the specified file_path does not exist.
            UploadError: If the upload fails due to API or network issues.
            AuthenticationError: If obtaining the token fails.
        """
        upload_url = self.base_url + self.UPLOAD_ENDPOINT

        try:
            token = self._get_token() # Get token (will request if not cached)
            headers = {
                'accept': 'application/json',
                'token': token,
                # Content-Type for multipart/form-data is set automatically by requests
            }

            if not file_path and not file_content:
                log.error("No file path or file content provided.")
                raise ValueError("Either file_path or file_content must be provided.")

            if not file_path:
                # Using file_content approach
                log.info("Using provided file content instead of file path")
                if not file_name:
                    log.error("File name not provided when using file content.")
                    raise ValueError("File name must be provided when using file content.")
                
                # 1. Prepare file content (ensure it's bytes)
                file_bytes: bytes = file_content
                content_type: str = 'text/plain; charset=utf-8'
                if isinstance(file_content, str):
                    try:
                        file_bytes = file_content.encode('utf-8')
                        # If no content type provided and it's text, default to text/plain
                    except UnicodeEncodeError as e:
                        raise ValueError(f"Could not encode string content to UTF-8: {e}") from e
                # else:
                #     raise TypeError(f"file_content must be bytes or str, not {type(file_content).__name__}")

                # 2. Prepare file metadata
                files = {
                    'file': (file_name, file_bytes, content_type)
                }

                log.info(f"Uploading '{file_name}' to {upload_url}...")
                response = requests.post(upload_url, headers=headers, files=files)

                log.info(f"Upload response status code: {response.status_code}")
                if not response.ok:
                    # Log detailed error response from server
                    log.error(f"Upload failed. Status: {response.status_code}, Response: {response.text}")

                response.raise_for_status() # Raises HTTPError for 4xx/5xx responses

                try:
                    response_data = response.json()
                    log.info(f"File '{file_name}' uploaded successfully.")
                    return response_data
                except json.JSONDecodeError:
                    log.error(f"Failed to decode JSON response from upload endpoint: {response.text}")
                    raise UploadError("Invalid JSON response received from upload endpoint after successful status.")



            else:
                # Check if file exists before attempting to open it
                if not os.path.isfile(file_path):
                    log.error(f"File not found at path: {file_path}")
                    raise FileNotFoundError(f"File not found at path: {file_path}")
                    
                with open(file_path, 'rb') as f:
                    # Use provided file_name or extract from path
                    actual_file_name = file_name or os.path.basename(file_path)
                    files = {
                        'file': (actual_file_name, f, 'application/octet-stream') # Explicit MIME type often helps
                    }

                    log.info(f"Uploading '{actual_file_name}' to {upload_url}...")
                    response = requests.post(upload_url, headers=headers, files=files)

                    log.info(f"Upload response status code: {response.status_code}")
                    if not response.ok:
                        # Log detailed error response from server
                        log.error(f"Upload failed. Status: {response.status_code}, Response: {response.text}")

                    response.raise_for_status() # Raises HTTPError for 4xx/5xx responses

                    try:
                        response_data = response.json()
                        log.info(f"File '{actual_file_name}' uploaded successfully.")
                        return response_data
                    except json.JSONDecodeError:
                        log.error(f"Failed to decode JSON response from upload endpoint: {response.text}")
                        raise UploadError("Invalid JSON response received from upload endpoint after successful status.")

        except requests.exceptions.HTTPError as http_err:
            # HTTP errors (like 4xx, 5xx) are caught here after raise_for_status
            log.error(f"HTTP error during upload: {http_err}", exc_info=True)
            # Check for specific auth errors if possible (e.g., 401 Unauthorized)
            if http_err.response.status_code == 401:
                 self._token = None # Clear potentially invalid token
                 raise AuthenticationError(f"Authentication failed during upload (status 401). Token might be invalid or expired. Response: {http_err.response.text}") from http_err
            raise UploadError(f"HTTP error occurred during upload: {http_err}. Response: {http_err.response.text}") from http_err
        except requests.exceptions.RequestException as req_err:
            log.error(f"Network error during upload: {req_err}", exc_info=True)
            raise UploadError(f"Network error occurred during upload: {req_err}") from req_err
        except FileNotFoundError:
            raise # Re-raise the specific FileNotFoundError caught earlier
        except AuthenticationError:
            raise # Re-raise errors from _get_token()
        except Exception as e:
            log.error(f"An unexpected error occurred during upload: {e}", exc_info=True)
            raise UploadError(f"An unexpected error occurred during upload: {e}") from e