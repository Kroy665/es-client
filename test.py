import requests
import json
import os

os.environ["email"] = "kroy963@gmail.com"
os.environ["teamSlug"] = "demo"
os.environ["apikey"] = "es-815cdI5FrGmnNinLqKRHEVA7t5M8"

def get_token():
    url = 'https://dev-ai-v2.codefast.ai/token'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    payload = {
        "email": os.environ["email"],
        "teamSlug": os.environ["teamSlug"],
        "apikey": os.environ["apikey"]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        try:
            response_data = response.json()
            return response_data["access_token"]
        except json.JSONDecodeError:
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def upload_file(file_path):
    url = 'https://dev-ai-v2.codefast.ai/api/v2/es/upload'

    token = get_token()
    headers = {
        'accept': 'application/json',
        'token': token,
    }
    try:
        if not os.path.exists(file_path):
            print(f"Error: File not found at '{file_path}'")
            return None

        with open(file_path, 'rb') as f:
            file_name = os.path.basename(file_path)
            files = {
                'file': (file_name, f)
            }

            print(f"Uploading '{file_name}' to {url}...")
            print(f"Headers being sent (excluding Content-Type added by requests): {headers}")
            print(f"Files dict structure: {{'file': ('{file_name}', <file object>)}}")

            response = requests.post(url, headers=headers, files=files)

            print(f"Response Status Code: {response.status_code}")

            try:
                print(f"Response Body:\n{response.text}")
            except Exception as print_err:
                print(f"Could not print response body: {print_err}")

            response.raise_for_status()

            return response.json()

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred during the request: {req_err}")
        return None
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

my_file = "test.txt"

result = upload_file(my_file)

if result:
    print("\nUpload successful!")
    print("Server Response JSON:")
    print(result)
else:
    print("\nUpload failed.")