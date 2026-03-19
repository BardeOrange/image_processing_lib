import time
import numpy as np
import imgproc_cpp


def python_grayscale(data: list, width: int, height: int) -> list:
    """Pure Python grayscale — SLOW on purpose for comparison."""
    output = [0] * len(data)
    for i in range(width * height):
        r = data[i * 3]
        g = data[i * 3 + 1]
        b = data[i * 3 + 2]
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        gray = max(0, min(255, gray))
        output[i * 3] = gray
        output[i * 3 + 1] = gray
        output[i * 3 + 2] = gray
    return output


def python_invert(data: list, width: int, height: int) -> list:
    """Pure Python invert — SLOW on purpose for comparison."""
    output = [0] * len(data)
    for i in range(len(data)):
        output[i] = 255 - data[i]
    return output


def python_box_blur(data: list, width: int, height: int, radius: int) -> list:
    """Pure Python box blur — VERY SLOW for comparison."""
    output = [0] * len(data)
    for y in range(height):
        for x in range(width):
            r, g, b, count = 0, 0, 0, 0
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        idx = (ny * width + nx) * 3
                        r += data[idx]
                        g += data[idx + 1]
                        b += data[idx + 2]
                        count += 1
            idx = (y * width + x) * 3
            output[idx] = r // count
            output[idx + 1] = g // count
            output[idx + 2] = b // count
    return output


def benchmark(func_python, func_cpp, args_python, args_cpp, name, runs=3):
    """Run both versions and compare speed."""
    # Warm up
    func_python(*args_python)
    func_cpp(*args_cpp)

    # Benchmark Python
    times_python = []
    for _ in range(runs):
        start = time.perf_counter()
        func_python(*args_python)
        times_python.append(time.perf_counter() - start)

    # Benchmark C++
    times_cpp = []
    for _ in range(runs):
        start = time.perf_counter()
        func_cpp(*args_cpp)
        times_cpp.append(time.perf_counter() - start)

    avg_python = sum(times_python) / runs
    avg_cpp = sum(times_cpp) / runs
    speedup = avg_python / avg_cpp if avg_cpp > 0 else float("inf")

    print(f"\n{'=' * 50}")
    print(f"  {name}")
    print(f"{'=' * 50}")
    print(f"  Python:  {avg_python:.4f}s")
    print(f"  C++:     {avg_cpp:.4f}s")
    print(f"  Speedup: {speedup:.1f}x")

    return {
        "name": name,
        "python_time": avg_python,
        "cpp_time": avg_cpp,
        "speedup": speedup
    }


def run_all_benchmarks(width=800, height=600):
    """Run all benchmarks with a random image."""
    print("Generating random test image...")
    print(f"Size: {width}x{height} ({width * height:,} pixels)\n")

    # Convert to regular Python ints to avoid uint8 overflow
    data = [
        int(x) for x in np.random.randint(0, 256, size=width * height * 3)
    ]

    results = []

    results.append(benchmark(
        python_grayscale, imgproc_cpp.grayscale,
        (data, width, height), (data, width, height),
        "Grayscale"
    ))

    results.append(benchmark(
        python_invert, imgproc_cpp.invert,
        (data, width, height), (data, width, height),
        "Invert"
    ))

    results.append(benchmark(
        python_box_blur, imgproc_cpp.box_blur,
        (data, width, height, 2), (data, width, height, 2),
        "Box Blur (radius=2)"
    ))

    # Summary
    print(f"\n{'=' * 50}")
    print("SUMMARY")
    print(f"{'=' * 50}")
    print(f"  {'Filter':<25} {'Python':>8} {'C++':>8} {'Speedup':>8}")
    print(f"  {'-' * 49}")
    for r in results:
        print(
            f"  {r['name']:<25} "
            f"{r['python_time']:>7.4f}s "
            f"{r['cpp_time']:>7.4f}s "
            f"{r['speedup']:>7.1f}x"
        )


if __name__ == "__main__":
    run_all_benchmarks()