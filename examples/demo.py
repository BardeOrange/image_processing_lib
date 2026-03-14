import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from python.image_processor import ImageProcessor


def main():
    """
    Demo: apply various filters to an image.
    Usage: python examples/demo.py <image_path>
    """
    if len(sys.argv) < 2:
        print("Usage: python examples/demo.py <image_path>")
        print("Example: python examples/demo.py photo.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    output_dir = Path("examples/output")
    output_dir.mkdir(exist_ok=True)

    filters = [
        ("grayscale", lambda p: p.grayscale()),
        ("bright", lambda p: p.brightness(60)),
        ("dark", lambda p: p.brightness(-60)),
        ("high_contrast", lambda p: p.contrast(2.0)),
        ("invert", lambda p: p.invert()),
        ("sepia", lambda p: p.sepia()),
        ("flip_h", lambda p: p.flip_horizontal()),
        ("box_blur", lambda p: p.box_blur(3)),
        ("gaussian_blur", lambda p: p.gaussian_blur(3)),
        ("sharpen", lambda p: p.sharpen()),
        ("edges", lambda p: p.edge_detect()),
    ]

    # Method chaining demo
    print("Applying filters...\n")

    for name, apply_filter in filters:
        processor = ImageProcessor(image_path)
        apply_filter(processor)
        output_path = output_dir / f"{name}.jpg"
        processor.save(str(output_path))

    # Chaining example
    print("\nMethod chaining example:")
    processor = ImageProcessor(image_path)
    processor.grayscale().contrast(1.5).sharpen()
    processor.save(str(output_dir / "chained.jpg"))

    print(f"\nAll images saved to {output_dir}/")


if __name__ == "__main__":
    main()