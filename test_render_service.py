import time
import requests

s_time = time.perf_counter()

APP_URL = "https://patwar-pdf-compressor.onrender.com/compress"
API_KEY = 'THE KEY'
PDF_FILE_PATH = "awais-baay-fard-docs-2.pdf"
ZIP_FILE_PATH = "compressed_images.zip"

headers = {
    "API-Key": API_KEY,
    "Referer": "https://shaukat.tech/"
}

with open(PDF_FILE_PATH, "rb") as pdf_file:
    files = {"file": pdf_file}
    response = requests.post(APP_URL, files=files, headers=headers)

if response.status_code == 200:
    with open(ZIP_FILE_PATH, "wb") as zip_file:
        zip_file.write(response.content)
    print(f"✅ ZIP file saved as {ZIP_FILE_PATH}")
else:
    print(f"❌ Failed! Status Code: {response.status_code}, Response: {response.text}")

print(f'Time taken: {(time.perf_counter() - s_time):.2f} secs.')