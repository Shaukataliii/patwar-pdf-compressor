import io
import os
import math
from PIL import Image

class ImageCompressor:
    def __init__(self, target_size=250 * 1024, initial_quality=100, test_quality=99, min_quality=30):
        """
        Initializes the ImageCompressor with default or user-defined settings.
        """
        self.target_size = target_size
        self.initial_quality = initial_quality
        self.test_quality = test_quality
        self.min_quality = min_quality
        self.image_path = None

    def compress(self, image_path: str):
        """
        Compresses an image to approximately the target size using heuristic adaptive compression.
        """
        image = self._read_image_as_jpg(image_path)
        raw_size = self._get_image_size(image)
        print(f'Raw image size is: {self._convert_b_to_kb(raw_size)} KB.')
        
        if not self._is_compression_required(raw_size):
            print('Raw size is less than target size. Skipping compression.')
            return self._compress_image(image, self.initial_quality)

        test_size = self._test_compression(image)
        final_quality = self._compute_optimal_quality(raw_size, test_size)
        compressed = self._compress_image(image, final_quality)

        print(f'Final compressed image size is: {self._convert_b_to_kb(len(compressed))} KB.')
        return compressed


    def _read_image_as_jpg(self, image_path: str) -> Image.Image:
        image = Image.open(image_path)

        format = image.format
        if format == "PNG":
            image = self._convert_png_to_jpeg(image)
        
        return image
    
    def _get_image_size(self, image: Image.Image) -> int:
        """Returns the size of an image in bytes."""
        return len(self._compress_image(image, self.initial_quality))

    def _convert_png_to_jpeg(self, image):
        """Converts a PNG (with transparency) to JPEG format by removing the alpha channel."""
        if image.mode in ("RGBA", "LA"):
            background = Image.new("RGB", image.size, (255, 255, 255))  # White background
            background.paste(image, mask=image.split()[3])  # Apply alpha channel as mask
            return background
        return image.convert("RGB")

    def _is_compression_required(self, raw_size: int) -> bool:
        if raw_size < self.target_size:
            return False
        return True

    def _test_compression(self, image):
        """Performs a test compression to estimate size reduction per test quality percentage."""
        test_compressed = self._compress_image(image, self.test_quality)
        return len(test_compressed)

    def _compress_image(self, image, quality):
        """Compresses an image to the given quality and format, returning its bytes."""
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
        return buffer.getvalue()

    def _compute_optimal_quality(self, raw_size, test_size):
        """Computes the estimated quality reduction required to reach the target size."""
        size_reduction_per_percent = raw_size - test_size
        print(f'Size reduction per percent is: {self._convert_b_to_kb(size_reduction_per_percent)} KB.')

        if size_reduction_per_percent <= 0:
            return self.initial_quality  # No meaningful reduction possible

        reduction_needed = raw_size - self.target_size
        print(f'Unupdated reduction needed: {self._convert_b_to_kb(reduction_needed)}')

        estimated_compression = math.ceil(reduction_needed / size_reduction_per_percent)
        print(f'Estimated compression quality: {estimated_compression}')
        
        estimated_compression_bytes = estimated_compression * size_reduction_per_percent
        print(f'Estimated compression is: {self._convert_b_to_kb(estimated_compression_bytes)} KB.')

        # Ensure compression does not go below the minimum allowed quality
        return (self.initial_quality - estimated_compression)

    def _convert_b_to_kb(self, byts: int) -> int:
        return int(byts / 1024)
    
    def _convert_kb_to_b(self, kbs: int) -> int:
        return int(kbs * 1024)




# Example usage
if __name__ == "__main__":
    compressor = ImageCompressor()
    image_path = "sample2.png"  # Test with PNG or JPEG
    compressed_bytes = compressor.compress(image_path)
