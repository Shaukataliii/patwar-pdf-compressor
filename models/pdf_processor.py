import os
import magic  # For MIME type checking
from pdf2image import convert_from_path
from PIL import Image
from typing import List


class PDFProcessor:
    """Handles PDF validation and image extraction from PDFs as whole pages."""

    def __init__(self, file_path: str, output_folder: str = "extracted_images", dpi: int = 300):
        """Initialize with a PDF file path and output folder for images."""
        self.file_path = file_path
        self.output_folder = output_folder
        self.dpi = dpi  # Image resolution

    def validate_pdf(self) -> bool:
        """Validates whether the provided file is a PDF."""
        if not self._is_valid_pdf_format():
            return False

        print("Validation Passed: PDF is valid.")
        return True

    def extract_images(self) -> List[Image.Image]:
        """Extracts each page as an image and saves them."""
        os.makedirs(self.output_folder, exist_ok=True)
        images = convert_from_path(self.file_path, dpi=self.dpi, poppler_path=r'C:\Program Files\poppler-24.02.0\Library\bin')  # Convert each page to an image

        return images
        # for page_num, image in enumerate(images, start=1):
        #     image_path = os.path.join(self.output_folder, f"page_{page_num}.png")
        #     image.save(image_path, "PNG")

        # print(f"Page extraction completed. Images saved in '{self.output_folder}'.")

    def _is_valid_pdf_format(self) -> bool:
        """Checks if the file is a valid PDF format using MIME type detection."""
        if not os.path.exists(self.file_path):
            print("Validation Failed: File does not exist.")
            return False

        mime_type = magic.Magic(mime=True).from_file(self.file_path)
        if mime_type != "application/pdf":
            print("Validation Failed: File is not a valid PDF.")
            return False
        return True


# Example Usage
if __name__ == "__main__":
    pdf_extractor = PDFProcessor("afzal-fard.pdf")
    if pdf_extractor.validate_pdf():
        images = pdf_extractor.extract_images()
        print(f'Got images, their type: {type(images)}')
