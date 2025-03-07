import io
import zipfile
import fitz  # PyMuPDF
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI()

# Constants
TARGET_TOTAL_SIZE = 3 * 1024 * 1024  # 3 MB in bytes
INITIAL_QUALITY = 85
MIN_QUALITY = 25
QUALITY_STEP = 10

def extract_images_from_pdf(pdf_bytes: bytes):
    """
    Extracts images from the PDF and returns a list of tuples: (PIL Image, original extension).
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
            # Load image via Pillow
            try:
                image = Image.open(io.BytesIO(image_bytes))
                # Convert to RGB for JPEG compression if needed
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")
                images.append((image, base_image.get("ext", "jpg")))
            except Exception as e:
                print(f"Error processing image: {e}")
    return images

def compress_images(images, quality):
    """
    Compresses each image to JPEG with the given quality.
    Returns a list of tuples (filename, compressed_bytes) and the total size.
    """
    compressed_images = []
    total_size = 0
    for idx, (img, _) in enumerate(images, start=1):
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        img_bytes = buffer.getvalue()
        total_size += len(img_bytes)
        # Size in kilobytes for logging/debugging: len(img_bytes) / 1024
        compressed_images.append((f"image_{idx}.jpg", img_bytes))
    return compressed_images, total_size

@app.post("/process")
async def process_pdf(file: UploadFile = File(...)):
    """
    Endpoint to upload a PDF, extract & compress its images,
    and return a zip file with the compressed images.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    
    pdf_bytes = await file.read()
    images = extract_images_from_pdf(pdf_bytes)
    
    if not images:
        raise HTTPException(status_code=400, detail="No images found in the provided PDF.")
    
    # Start compression at the initial quality level.
    quality = INITIAL_QUALITY
    compressed_images, total_size = compress_images(images, quality)
    
    # Iteratively reduce quality until the total size is within the target,
    # or until the quality reaches the minimum allowed.
    while total_size > TARGET_TOTAL_SIZE and quality > MIN_QUALITY:
        quality -= QUALITY_STEP
        compressed_images, total_size = compress_images(images, quality)
    
    # Optional: Log total size in kilobytes for reference.
    print(f"Final total size: {total_size / 1024:.2f} KB at quality {quality}")

    # Package compressed images into a zip file in memory.
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


