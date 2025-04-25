from es_client import CodeFastClient

client = CodeFastClient(email="kroy963@gmail.com", team_slug="demo", api_key="es-815cdI5FrGmnNinLqKRHEVA7t5M8")

# Get token 
client._get_token()

# Upload file
client.upload_file("test.txt")