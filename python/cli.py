import argparse
import sys
from pathlib import Path
# Add parent directory to path so we can import our module
sys.path.insert(0, str(Path(__file__).parent.parent))
from python.image_processor import ImageProcessor


def main():
    parser = argparse.ArgumentParser(
        description="Image Processing CLI — Powered by C++"
    )
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output image path")
    parser.add_argument(
        "--filter", "-f",
        required=True,
        choices=[
            "grayscale", "invert", "sepia", "sharpen",
            "edge_detect", "box_blur", "gaussian_blur",
            "flip_horizontal", "flip_vertical",
            "brightness", "contrast"
        ],
        help="Filter to apply"
    )
    parser.add_argument(
        "--value", "-v",
        type=float,
        default=None,
        help="Value for brightness (-255 to 255) or contrast (0.0 to 3.0)"
    )
    parser.add_argument(
        "--radius", "-r",
        type=int,
        default=2,
        help="Radius for blur filters (default: 2)"
    )

    args = parser.parse_args()

    # Validate input file
    if not Path(args.input).exists():
        print(f"Error: File not found: {args.input}")
        sys.exit(1)

    # Process
    print(f"Loading: {args.input}")
    processor = ImageProcessor(args.input)
    print(f"Size: {processor.size[0]}x{processor.size[1]}")
    print(f"Applying: {args.filter}")

    filter_name = args.filter

    if filter_name == "brightness":
        value = int(args.value) if args.value is not None else 50
        processor.brightness(value)
    elif filter_name == "contrast":
        value = args.value if args.value is not None else 1.5
        processor.contrast(value)
    elif filter_name == "box_blur":
        processor.box_blur(args.radius)
    elif filter_name == "gaussian_blur":
        processor.gaussian_blur(args.radius)
    else:
        getattr(processor, filter_name)()

    processor.save(args.output)
    print("Done!")


if __name__ == "__main__":
    main()
