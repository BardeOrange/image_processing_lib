import numpy as np
from PIL import Image
from pathlib import Path
import imgproc_cpp


class ImageProcessor:
    """
    A Python-friendly wrapper around the C++ image processing library.

    Usage:
        processor = ImageProcessor("photo.jpg")
        processor.grayscale()
        processor.save("photo_gray.jpg")
    """

    def __init__(self, image_path: str = None):
        """Initialize with an image file path."""
        self._width = 0
        self._height = 0
        self._data = []
        self._original_data = []

        if image_path:
            self.load(image_path)

    def load(self, image_path: str) -> "ImageProcessor":
        """Load an image from file."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        img = Image.open(path).convert("RGB")
        self._width, self._height = img.size
        self._data = list(np.array(img).flatten())
        self._original_data = self._data.copy()
        return self

    def save(self, output_path: str) -> None:
        """Save the processed image to file."""
        arr = np.array(self._data, dtype=np.uint8).reshape(
            (self._height, self._width, 3)
        )
        img = Image.fromarray(arr)
        img.save(output_path)
        print(f"Saved: {output_path}")

    def show(self) -> None:
        """Display the current image using matplotlib."""
        import matplotlib.pyplot as plt

        arr = np.array(self._data, dtype=np.uint8).reshape(
            (self._height, self._width, 3)
        )
        plt.imshow(arr)
        plt.axis("off")
        plt.show()

    def compare(self) -> None:
        """Show original vs processed side by side."""
        import matplotlib.pyplot as plt

        original = np.array(self._original_data, dtype=np.uint8).reshape(
            (self._height, self._width, 3)
        )
        processed = np.array(self._data, dtype=np.uint8).reshape(
            (self._height, self._width, 3)
        )

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        ax1.imshow(original)
        ax1.set_title("Original")
        ax1.axis("off")
        ax2.imshow(processed)
        ax2.set_title("Processed")
        ax2.axis("off")
        plt.tight_layout()
        plt.show()

    def reset(self) -> "ImageProcessor":
        """Reset to original image."""
        self._data = self._original_data.copy()
        return self

    @property
    def size(self) -> tuple:
        """Return (width, height) of the image."""
        return self._width, self._height

    # ============ FILTERS ============

    def grayscale(self) -> "ImageProcessor":
        """Convert to grayscale."""
        self._data = imgproc_cpp.grayscale(self._data, self._width, self._height)
        return self

    def brightness(self, value: int) -> "ImageProcessor":
        """Adjust brightness. Value: -255 to 255."""
        self._data = imgproc_cpp.brightness(
            self._data, self._width, self._height, value
        )
        return self

    def contrast(self, factor: float) -> "ImageProcessor":
        """Adjust contrast. Factor: 0.0 to 3.0."""
        self._data = imgproc_cpp.contrast(
            self._data, self._width, self._height, factor
        )
        return self

    def invert(self) -> "ImageProcessor":
        """Invert colors."""
        self._data = imgproc_cpp.invert(self._data, self._width, self._height)
        return self

    def sepia(self) -> "ImageProcessor":
        """Apply sepia tone."""
        self._data = imgproc_cpp.sepia(self._data, self._width, self._height)
        return self

    def flip_horizontal(self) -> "ImageProcessor":
        """Flip image horizontally."""
        self._data = imgproc_cpp.flip_horizontal(
            self._data, self._width, self._height
        )
        return self

    def flip_vertical(self) -> "ImageProcessor":
        """Flip image vertically."""
        self._data = imgproc_cpp.flip_vertical(
            self._data, self._width, self._height
        )
        return self

    def box_blur(self, radius: int = 2) -> "ImageProcessor":
        """Apply box blur. Radius: 1+."""
        self._data = imgproc_cpp.box_blur(
            self._data, self._width, self._height, radius
        )
        return self

    def gaussian_blur(self, radius: int = 2) -> "ImageProcessor":
        """Apply Gaussian blur. Radius: 1+."""
        self._data = imgproc_cpp.gaussian_blur(
            self._data, self._width, self._height, radius
        )
        return self

    def sharpen(self) -> "ImageProcessor":
        """Sharpen the image."""
        self._data = imgproc_cpp.sharpen(self._data, self._width, self._height)
        return self

    def edge_detect(self) -> "ImageProcessor":
        """Detect edges using Sobel operator."""
        self._data = imgproc_cpp.edge_detect(
            self._data, self._width, self._height
        )
        return self
