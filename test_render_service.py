import requests

# Replace this with your actual deployed app URL
APP_URL = "https://patwar-pdf-compressor.onrender.com/compress"

# Path to the PDF file you want to compress
PDF_FILE_PATH = "awais-baay-fard-docs-2.pdf"

# Path to save the received ZIP file
ZIP_FILE_PATH = "compressed_images.zip"

# Open the PDF file and send the request
with open(PDF_FILE_PATH, "rb") as pdf_file:
    files = {"file": pdf_file}
    response = requests.post(APP_URL, files=files)

# Check if request was successful
if response.status_code == 200:
    with open(ZIP_FILE_PATH, "wb") as zip_file:
        zip_file.write(response.content)
    print(f"✅ ZIP file saved as {ZIP_FILE_PATH}")
else:
    print(f"❌ Failed! Status Code: {response.status_code}, Response: {response.text}")
