import io
import zipfile
import fitz  # PyMuPDF
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from typing import Tuple

app = FastAPI()

# Constants
TARGET_TOTAL_SIZE = 3 * 1024 * 1024  # 3 MB in bytes
MAX_IMAGE_SIZE = 300 * 1024  # 300 KB per image
INITIAL_QUALITY = 85
MIN_QUALITY = 25
QUALITY_STEP = 5  # Reduce in smaller steps for better control

def extract_images(pdf_bytes: bytes):
    """
    Extracts images from the PDF and returns a list of tuples: (PIL Image, original size in bytes).
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    
    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        image_list = page.get_images(full=True)
        
        for img_info in image_list:
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            original_size = len(image_bytes)
            
            try:
                image = Image.open(io.BytesIO(image_bytes))
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")
                images.append((image, original_size))
            except Exception as e:
                print(f"Error processing image: {e}")
    
    return images

def compress_image(image, quality):
    """
    Compresses a single image to the given quality and returns its bytes.
    """
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()

def compress_images_adaptive(images: Tuple[Image.Image, bytes]):
    """
    Compresses images adaptively to ensure:
    - Each image is < 300 KB
    - Total size is < 3 MB
    """
    total_size = sum(size for _, size in images)
    compression_ratios = [size / total_size for _, size in images]  # Proportional weights
    
    compressed_images = []
    quality_levels = [INITIAL_QUALITY] * len(images)
    
    while total_size > TARGET_TOTAL_SIZE:
        for idx, (image, _) in enumerate(images):
            if quality_levels[idx] > MIN_QUALITY:
                quality_levels[idx] -= QUALITY_STEP * compression_ratios[idx]  # Proportional quality reduction
                quality_levels[idx] = max(quality_levels[idx], MIN_QUALITY)
        
        compressed_images = [(f"image_{idx + 1}.jpg", compress_image(image, int(quality_levels[idx]))) for idx, (image, _) in enumerate(images)]
        total_size = sum(len(img_bytes) for _, img_bytes in compressed_images)
    
    # Ensure each image is < 300 KB
    for idx, (filename, img_bytes) in enumerate(compressed_images):
        quality = int(quality_levels[idx])
        while len(img_bytes) > MAX_IMAGE_SIZE and quality > MIN_QUALITY:
            quality -= QUALITY_STEP
            img_bytes = compress_image(images[idx][0], quality)
        compressed_images[idx] = (filename, img_bytes)
    
    return compressed_images

@app.post("/process")
async def process_pdf(file: UploadFile = File(...)):
    """
    Endpoint to upload a PDF, extract & compress its images, and return a zip file with the compressed images.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    
    pdf_bytes = await file.read()
    images = extract_images(pdf_bytes)
    
    if not images:
        raise HTTPException(status_code=400, detail="No images found in the provided PDF.")
    
    compressed_images = compress_images_adaptive(images)
    
    # Package compressed images into a zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for filename, img_bytes in compressed_images:
            zip_file.writestr(filename, img_bytes)
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=compressed_images.zip"}
    )
