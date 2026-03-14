import sys
from pathlib import Path

import pytest
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

import imgproc_cpp
from python.image_processor import ImageProcessor


# ============ HELPER ============

def make_image(width, height, r=128, g=128, b=128):
    """Create a solid color test image."""
    data = []
    for _ in range(width * height):
        data.extend([r, g, b])
    return data


# ============ C++ FILTER TESTS ============

class TestGrayscale:
    def test_pure_red(self):
        data = make_image(2, 2, r=255, g=0, b=0)
        result = imgproc_cpp.grayscale(data, 2, 2)
        # Red grayscale = 0.299 * 255 ≈ 76
        assert result[0] == 76
        assert result[1] == 76
        assert result[2] == 76

    def test_pure_white(self):
        data = make_image(2, 2, r=255, g=255, b=255)
        result = imgproc_cpp.grayscale(data, 2, 2)
        assert result[0] == 255

    def test_pure_black(self):
        data = make_image(2, 2, r=0, g=0, b=0)
        result = imgproc_cpp.grayscale(data, 2, 2)
        assert result[0] == 0

    def test_output_size(self):
        data = make_image(10, 10)
        result = imgproc_cpp.grayscale(data, 10, 10)
        assert len(result) == len(data)


class TestBrightness:
    def test_increase(self):
        data = make_image(2, 2, r=100, g=100, b=100)
        result = imgproc_cpp.brightness(data, 2, 2, 50)
        assert result[0] == 150

    def test_decrease(self):
        data = make_image(2, 2, r=100, g=100, b=100)
        result = imgproc_cpp.brightness(data, 2, 2, -50)
        assert result[0] == 50

    def test_clamp_max(self):
        data = make_image(2, 2, r=200, g=200, b=200)
        result = imgproc_cpp.brightness(data, 2, 2, 100)
        assert result[0] == 255

    def test_clamp_min(self):
        data = make_image(2, 2, r=50, g=50, b=50)
        result = imgproc_cpp.brightness(data, 2, 2, -100)
        assert result[0] == 0


class TestContrast:
    def test_double_contrast(self):
        data = make_image(2, 2, r=192, g=192, b=192)
        result = imgproc_cpp.contrast(data, 2, 2, 2.0)
        # 2.0 * (192 - 128) + 128 = 256 → clamped to 255
        assert result[0] == 255

    def test_zero_contrast(self):
        data = make_image(2, 2, r=200, g=100, b=50)
        result = imgproc_cpp.contrast(data, 2, 2, 0.0)
        # 0.0 * (x - 128) + 128 = 128 for all
        assert result[0] == 128
        assert result[1] == 128
        assert result[2] == 128


class TestInvert:
    def test_invert_black(self):
        data = make_image(2, 2, r=0, g=0, b=0)
        result = imgproc_cpp.invert(data, 2, 2)
        assert result[0] == 255
        assert result[1] == 255
        assert result[2] == 255

    def test_invert_white(self):
        data = make_image(2, 2, r=255, g=255, b=255)
        result = imgproc_cpp.invert(data, 2, 2)
        assert result[0] == 0

    def test_double_invert(self):
        data = make_image(2, 2, r=100, g=150, b=200)
        result = imgproc_cpp.invert(data, 2, 2)
        result = imgproc_cpp.invert(result, 2, 2)
        assert result == data


class TestSepia:
    def test_output_size(self):
        data = make_image(5, 5)
        result = imgproc_cpp.sepia(data, 5, 5)
        assert len(result) == len(data)

    def test_values_in_range(self):
        data = make_image(5, 5, r=200, g=150, b=100)
        result = imgproc_cpp.sepia(data, 5, 5)
        assert all(0 <= v <= 255 for v in result)


class TestFlip:
    def test_flip_horizontal(self):
        # 2x1 image: Red | Blue
        data = [255, 0, 0, 0, 0, 255]
        result = imgproc_cpp.flip_horizontal(data, 2, 1)
        # Should be: Blue | Red
        assert result == [0, 0, 255, 255, 0, 0]

    def test_flip_vertical(self):
        # 1x2 image: Red (top) / Blue (bottom)
        data = [255, 0, 0, 0, 0, 255]
        result = imgproc_cpp.flip_vertical(data, 1, 2)
        # Should be: Blue (top) / Red (bottom)
        assert result == [0, 0, 255, 255, 0, 0]

    def test_double_flip_horizontal(self):
        data = make_image(5, 5, r=100, g=150, b=200)
        result = imgproc_cpp.flip_horizontal(data, 5, 5)
        result = imgproc_cpp.flip_horizontal(result, 5, 5)
        assert result == data

    def test_double_flip_vertical(self):
        data = make_image(5, 5, r=100, g=150, b=200)
        result = imgproc_cpp.flip_vertical(data, 5, 5)
        result = imgproc_cpp.flip_vertical(result, 5, 5)
        assert result == data


class TestBlur:
    def test_box_blur_uniform(self):
        """Blurring a solid color image should return the same image."""
        data = make_image(5, 5, r=100, g=100, b=100)
        result = imgproc_cpp.box_blur(data, 5, 5, 1)
        assert result == data

    def test_gaussian_blur_uniform(self):
        data = make_image(5, 5, r=100, g=100, b=100)
        result = imgproc_cpp.gaussian_blur(data, 5, 5, 1)
        assert all(abs(result[i] - data[i]) <= 1 for i in range(len(data)))

    def test_box_blur_invalid_radius(self):
        data = make_image(5, 5)
        with pytest.raises(Exception):
            imgproc_cpp.box_blur(data, 5, 5, 0)

    def test_gaussian_blur_invalid_radius(self):
        data = make_image(5, 5)
        with pytest.raises(Exception):
            imgproc_cpp.gaussian_blur(data, 5, 5, 0)


class TestSharpen:
    def test_output_size(self):
        data = make_image(5, 5)
        result = imgproc_cpp.sharpen(data, 5, 5)
        assert len(result) == len(data)

    def test_uniform_unchanged(self):
        """Sharpening a solid color should keep it mostly the same."""
        data = make_image(5, 5, r=100, g=100, b=100)
        result = imgproc_cpp.sharpen(data, 5, 5)
        assert all(abs(result[i] - data[i]) <= 1 for i in range(len(data)))


class TestEdgeDetect:
    def test_output_size(self):
        data = make_image(5, 5)
        result = imgproc_cpp.edge_detect(data, 5, 5)
        assert len(result) == len(data)

    def test_uniform_no_edges(self):
        """A solid color image should have no edges (all ~0)."""
        data = make_image(10, 10, r=128, g=128, b=128)
        result = imgproc_cpp.edge_detect(data, 10, 10)
        assert all(v < 10 for v in result)


# ============ VALIDATION TESTS ============

class TestValidation:
    def test_invalid_dimensions(self):
        data = [128] * 30  # 10 pixels * 3 channels
        with pytest.raises(Exception):
            imgproc_cpp.grayscale(data, 5, 5)  # Expects 75 values

    def test_empty_image(self):
        with pytest.raises(Exception):
            imgproc_cpp.grayscale([], 0, 0)


# ============ PYTHON WRAPPER TESTS ============

class TestImageProcessor:
    def test_load_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            ImageProcessor("nonexistent.jpg")

    def test_method_chaining(self):
        """Verify method chaining returns self."""
        data = make_image(5, 5)
        proc = ImageProcessor()
        proc._width = 5
        proc._height = 5
        proc._data = data.copy()
        proc._original_data = data.copy()

        result = proc.grayscale().invert().sharpen()
        assert result is proc

    def test_reset(self):
        data = make_image(5, 5, r=100, g=150, b=200)
        proc = ImageProcessor()
        proc._width = 5
        proc._height = 5
        proc._data = data.copy()
        proc._original_data = data.copy()

        proc.grayscale()
        assert proc._data != proc._original_data

        proc.reset()
        assert proc._data == proc._original_data

    def test_size(self):
        proc = ImageProcessor()
        proc._width = 100
        proc._height = 200
        assert proc.size == (100, 200)