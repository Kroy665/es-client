from es_client import CodeFastClient
# from PIL import Image
# import io

client = CodeFastClient(email="kroy963@gmail.com", team_slug="demo", api_key="es-815cdI5FrGmnNinLqKRHEVA7t5M8")

# Get token 
client._get_token()

# Upload file
print(client.upload_file(file_path="test.txt", file_name="test.txt"))

# --- Example Usage ---

# if __name__ == '__main__':
#     # Create a simple red image in memory
#     img = Image.new('RGB', (60, 30), color = 'red')
#     # Save the image to an in-memory bytes buffer
#     img_byte_arr = io.BytesIO()
#     img.save(img_byte_arr, format='PNG')
#     img_bytes = img_byte_arr.getvalue() # Get the raw bytes

#     # Upload the image
#     try:
#         response = client.upload_file(
#             file_content=img_bytes,
#             file_name="red_image.png"
#         )
#         print("Image uploaded successfully:")
#         print(response)
#     except Exception as e:
#         print(f"Failed to upload image: {e}")

# --- Test ---
# create a csv FILE and upload it
# try:
#     # create a csv file
#     with open("test.csv", "w") as f:
#         f.write("name,age\n")
#         f.write("John,30\n")
#         f.write("Jane,25\n")
#     # upload the csv file
#     response = client.upload_file(file_path="test.csv", file_name="test.csv")
#     print("File uploaded successfully:")
#     print(response)
# except Exception as e:
#     print(f"Failed to upload file: {e}")
    