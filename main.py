# provide api key is the format: API_KEY = Bearer KEY HERE
import os
import io
import uvicorn
from typing import List
import zipfile
from fastapi import FastAPI, HTTPException, Header, status, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends

from models.pdf_processor import PDFProcessor
from models.compressor import ImageCompressor
from models.logger import logger

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI()
API_KEY = os.getenv('API_KEY')

# Enhanced CORS Configuration for WordPress
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shaukat.tech"],  # Your WordPress domain
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS", "HEAD"],  # Explicitly allow both
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Content-Disposition"]  # Required for file downloads
)


async def verify_api_key(authorization: str = Header(...)):
    """Validate Authorization header with Bearer token"""
    if not API_KEY:
        logger.error("API_KEY environment variable not set")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error"
        )
    
    if not authorization.startswith("Bearer "):
        logger.warning(f"Invalid authorization header format: {authorization}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    token = authorization.split(" ")[1]
    if token != API_KEY:
        logger.warning(f"Invalid API key attempt: {token}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )

@app.post("/compress")
async def compress_pdf(
    file: UploadFile = File(...),
    authorization: str = Header(...)
) -> StreamingResponse:
    """
    Process PDF file from WordPress with API key validation
    """
    try:
        # Verify API key first
        await verify_api_key(authorization)
        
        logger.info(f'Processing request for file: {file.filename}')
        
        # Validate file input
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are accepted"
            )

        # Process PDF
        file_path = await save_uploaded_file(file)
        images = process_pdf(file_path)

        if not images:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No images found in PDF"
            )

        return generate_zip_response(images)

    except HTTPException as he:
        logger.error(f"HTTP Error {he.status_code}: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Processing failed"
        )

# Existing helper functions remain the same
async def save_uploaded_file(file: UploadFile) -> str:
    name = 'uploaded_pdf.pdf'
    file_path = os.path.join(UPLOAD_FOLDER, name)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return file_path

def process_pdf(file_path: str) -> List[bytes]:
    processor = PDFProcessor(file_path)
    compressor = ImageCompressor()

    if not processor.validate_pdf():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF file"
        )

    images = processor.extract_images()
    return compressor.compress_images(images)

def generate_zip_response(images_bytes: List[bytes]) -> StreamingResponse:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for idx, img_bytes in enumerate(images_bytes):
            zip_file.writestr(f"page_{idx + 1}.png", img_bytes)
    zip_buffer.seek(0)
    headers = {"Content-Disposition": "attachment; filename=compressed_images.zip"}
    logger.info('Compression complete')
    return StreamingResponse(zip_buffer, media_type="application/zip", headers=headers)

@app.get("/health")
async def health_check():
    """Endpoint for service health monitoring"""
    return {"status": "healthy", "service": "pdf-compressor"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)