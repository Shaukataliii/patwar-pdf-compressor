# 📄 PDF Image Extractor & Compressor 🚀

A FastAPI-based service to **extract and compress images** from PDFs while ensuring:  
✅ Each image is **< 300 KB**  
✅ Total compressed images are **< 3 MB**  
✅ Adaptive, proportional compression for best quality  

---

## 🚀 Features  
- **Extracts all images** from a PDF  
- **Compresses images adaptively** to fit size constraints  
- **Ensures quality preservation** while reducing file size  
- **Returns a ZIP file** containing the compressed images  
- **Fast & scalable** using FastAPI  

---

## 🛠️ Installation  

### **1⃣ Clone the repository**
```sh
git clone https://github.com/Shaukataliii/patwar-pdf-compressor
cd patwar-pdf-compressor
```

---

### Create a virtual environment (optional but recommended)
```sh
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### Install dependencies
```sh
pip install -r requirements.txt
```

## ▶️ Usage

### **1⃣ Run the FastAPI server**
```sh
uvicorn main:app --reload
```
By default, the API runs at http://127.0.0.1:8000.

### **2⃣ Use the API**
Go to http://127.0.0.1:8000/docs to access Swagger UI.
Use the `/process` endpoint to upload a PDF file.

#### Example API Call (cURL)
```sh
curl -X 'POST' 'http://127.0.0.1:8000/process' \
     -H 'accept: application/zip' \
     -H 'Content-Type: multipart/form-data' \
     -F 'file=@sample.pdf' \
     --output compressed_images.zip
```

## 📚 API Documentation

### 🔹 POST /process
Uploads a PDF, extracts images, compresses them, and returns a ZIP file.

#### Request
- **Method:** POST
- **URL:** /process
- **Headers:** Content-Type: multipart/form-data
- **Body:**
  - `file` (PDF file)

#### Response
- **Success:** `200 OK` – Returns a ZIP file containing the compressed images.
- **Errors:**
  - `400 Bad Request` – If the file is not a PDF or has no images.
  - `500 Internal Server Error` – If an unknown error occurs.

## ⚙️ Tech Stack
- **Python** 🐍
- **FastAPI** 🚀
- **PyMuPDF (fitz)** 📄 (for extracting images)
- **Pillow (PIL)** 🎨 (for image processing)

## 🤝 Contributing
Feel free to contribute! Fork the repository and submit a pull request.

## 🐟 License
This project is licensed under the MIT License.