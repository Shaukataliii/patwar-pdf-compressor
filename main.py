import os
import io
from typing import  List
import zipfile
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse

from models.pdf_processor import PDFProcessor
from models.compressor import ImageCompressor
from models.logger import logger

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI()


@app.post("/compress", summary="Extract and compress PDF images")
async def compress_pdf(file: UploadFile = File(...)) -> StreamingResponse:
    """
    Accepts a PDF upload, extracts images, compresses them,
    packs them into a ZIP file, and returns the ZIP for download.
    """
    logger.info('\nRequest received.')
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid file provided"
        )

    file_path = await save_uploaded_file(file)
    images = process_pdf(file_path)

    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No images extracted from PDF"
        )

    return generate_zip_response(images)


async def save_uploaded_file(file: UploadFile) -> str:
    """
    Saves the uploaded file to disk and returns its path.
    """
    name = 'uploaded_pdf.pdf'
    file_path = os.path.join(UPLOAD_FOLDER, name)

    # update this if wanna save the uploaded pdf.
    # name = file.filename
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return file_path


def process_pdf(file_path: str) -> List[bytes]:
    """
    Processes the PDF: validates, extracts images, and compresses them.
    """
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
    """
    Creates a ZIP file from a list of image bytes and returns it as a StreamingResponse.

    Parameters:
        images_bytes (List[bytes]): A list containing PNG image data in bytes.

    Returns:
        StreamingResponse: A response object with the zipped images for download.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for idx, img_bytes in enumerate(images_bytes):
            zip_file.writestr(f"page_{idx + 1}.png", img_bytes)
    zip_buffer.seek(0)
    headers = {"Content-Disposition": "attachment; filename=images.zip"}

    logger.info('Compression done. Returning zip file.')
    return StreamingResponse(zip_buffer, media_type="application/zip", headers=headers)
