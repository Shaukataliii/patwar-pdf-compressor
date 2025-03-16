import io
import math
from typing import List
from PIL import Image

from models.logger import logger

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

    def compress_images(self, images: List[Image.Image], combine_max_size: int= 3072 * 1024) -> List[Image.Image]:
        c_images = []

        sizes = self._get_images_size(images)
        if sum(sizes) < combine_max_size:

            for image in images:
                compressed = self.compress_it(image)
                c_images.append(compressed)

        else:
            required_sizes = self._compute_required_sizes(combine_max_size, sizes)
            
            for image, required_size in zip(images, required_sizes):
                self.target_size = required_size    # to compress the image upto this size

                compressed = self.compress_it(image)
                c_images.append(compressed)

        logger.info(f'Returning {len(c_images)} compressed images.')
        return c_images

    def _get_images_size(self, images: List[Image.Image]) -> List[int]:
        raw_size = []
        for image in images:
            raw_size.append(self._get_image_size(image))

        return raw_size
    
    def _compute_required_sizes(self, combine_max_size: int, sizes: List[int]) -> List[int]:
        """Returns a list of sizes that makes sure that the combine size of those is not more than the combine_max.
        """
        scaling_factor = combine_max_size / sum(sizes)
        target_sizes = [int(size * scaling_factor) for size in sizes]
        return target_sizes

    def compress_it(self, image: Image.Image):
        """
        Compresses an image to approximately the target size using heuristic adaptive compression. Skips compression if size is less than target size.
        """
        raw_size = self._get_image_size(image)
        logger.info(f'Image size is: {self._convert_b_to_kb(raw_size)}')
        
        if not self._is_compression_required(raw_size):
            logger.info('Raw size is less than target size. Skipping compression.')
            return self._compress_image(image, self.initial_quality)

        compression_per_percent = self._test_compression(image)
        final_quality = self._compute_optimal_quality(raw_size, compression_per_percent)
        compressed = self._compress_image(image, final_quality)

        # handling any remaining compression
        if self._is_compression_required(len(compressed)):
            compressed = self._do_iterative_compression(compressed, final_quality)
        
        logger.info(f'Final compressed image size is: {self._convert_b_to_kb(len(compressed))} KB.')
        return compressed
    
    def _is_compression_required(self, raw_size: int) -> bool:
        if raw_size > self.target_size:
            return True
        return False

    def _get_image_size(self, image: Image.Image) -> int:
        """Returns the size of an image in bytes."""
        return len(self._compress_image(image, self.initial_quality))

    def _convert_bytes_to_pil(self, bytes_image: bytes) -> Image.Image:
        return Image.open(io.BytesIO(bytes_image))

    def _do_iterative_compression(self, bytes_image: bytes, image_quality: int) -> bytes:
        image = self._convert_bytes_to_pil(bytes_image)

        while self._is_compression_required(len(bytes_image)):
            image_quality = image_quality - 1
            bytes_image = self._compress_image(image, image_quality)

            image = self._convert_bytes_to_pil(bytes_image)

        return bytes_image

    def _test_compression(self, image):
        """Performs a test compression to estimate size reduction per test quality percentage."""
        test_compressed = self._compress_image(image, self.test_quality)
        return len(test_compressed)

    def _compress_image(self, image: Image.Image, quality: int) -> bytes:
        """Compresses an image to the given quality and format, returning its bytes."""
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
        return buffer.getvalue()

    def _compute_optimal_quality(self, raw_size, test_size):
        """Computes the estimated quality reduction required to reach the target size."""
        size_reduction_per_percent = raw_size - test_size
        logger.info(f'Size reduction per percent is: {self._convert_b_to_kb(size_reduction_per_percent)} KB.')

        if size_reduction_per_percent <= 0:
            return self.initial_quality  # No meaningful reduction possible

        reduction_needed = raw_size - self.target_size
        estimated_compression = math.ceil(reduction_needed / size_reduction_per_percent)

        return (self.initial_quality - estimated_compression)

    def _convert_b_to_kb(self, byts: int) -> int:
        return int(byts / 1024)
    
    def _convert_kb_to_b(self, kbs: int) -> int:
        return int(kbs * 1024)




# Example usage
if __name__ == "__main__":
    compressor = ImageCompressor(target_size=150*1024)
    image_path = "sample.jpg"
    image = Image.open(image_path)
    compressed_bytes = compressor.compress_it(image)
