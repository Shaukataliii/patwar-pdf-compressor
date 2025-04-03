import time
import requests

s_time = time.perf_counter()

# APP_URL = "https://patwar-pdf-compressor.onrender.com/compress"
APP_URL = "http://127.0.0.1:8000/compress"
API_KEY = '84dd553da57d8a845861f07ed502c093'
TARGET_SIZE = 2097152
SINGLE_IMG_TARGET_SIZE = 204800


PDF_FILE_PATH = "docs.pdf"
ZIP_FILE_PATH = "compressed_images.zip"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Referer": "https://shaukat.tech/",
    "target-size": str(TARGET_SIZE),
    "single-img-target-size": str(SINGLE_IMG_TARGET_SIZE)
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