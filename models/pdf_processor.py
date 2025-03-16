import os
import io
import magic  # For MIME type checking
import fitz
from PIL import Image
from typing import List

from models.logger import logger


class PDFProcessor:
    """Handles PDF validation and image extraction from PDFs as whole pages."""

    def __init__(self, file_path: str, dpi: int = 300):
        """Initialize with a PDF file path and output folder for images."""
        self.file_path = file_path
        self.dpi = dpi  # Image resolution

    def validate_pdf(self) -> bool:
        """Validates whether the provided file is a PDF."""
        if not self._is_valid_pdf_format():
            return False

        logger.info("Validation Passed: PDF is valid.")
        return True

    def extract_images(self) -> List[Image.Image]:
        """Extracts each page as an image and saves them."""
        doc = fitz.open(self.file_path)
        images = []
        for page in doc:
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            images.append(img)

        logger.info(f'Returning {len(images)} extracted images.')
        return images

    def _is_valid_pdf_format(self) -> bool:
        """Checks if the file is a valid PDF format using MIME type detection."""
        if not os.path.exists(self.file_path):
            logger.info("Validation Failed: File does not exist.")
            return False

        mime_type = magic.Magic(mime=True).from_file(self.file_path)
        if mime_type != "application/pdf":
            logger.info("Validation Failed: File is not a valid PDF.")
            return False
        return True


# Example Usage
if __name__ == "__main__":
    pdf_extractor = PDFProcessor("afzal-fard.pdf")
    if pdf_extractor.validate_pdf():
        images = pdf_extractor.extract_images()
        print(f'Got {len(images)} images.')