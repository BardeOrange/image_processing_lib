#include <vector>
#include <cstdint>
#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <numeric>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

namespace imgproc {

    using Image = std::vector<uint8_t>;

    static uint8_t clamp(double value) {
        return static_cast<uint8_t>(std::max(0.0, std::min(255.0, value)));
    }

    static void validate(const Image& input, int width, int height, int channels = 3) {
        if (input.size() != static_cast<size_t>(width * height * channels)) {
            throw std::invalid_argument("Image size doesn't match dimensions");
        }
        if (width <= 0 || height <= 0) {
            throw std::invalid_argument("Width and height must be positive");
        }
    }

    Image grayscale(const Image& input, int width, int height) {
        validate(input, width, height);
        Image output(width * height * 3);
        for (int i = 0; i < width * height; ++i) {
            uint8_t r = input[i * 3];
            uint8_t g = input[i * 3 + 1];
            uint8_t b = input[i * 3 + 2];
            uint8_t gray = clamp(0.299 * r + 0.587 * g + 0.114 * b);
            output[i * 3] = gray;
            output[i * 3 + 1] = gray;
            output[i * 3 + 2] = gray;
        }
        return output;
    }

    Image brightness(const Image& input, int width, int height, int value) {
        validate(input, width, height);
        Image output(input.size());
        for (size_t i = 0; i < input.size(); ++i) {
            output[i] = clamp(static_cast<double>(input[i]) + value);
        }
        return output;
    }

    Image contrast(const Image& input, int width, int height, double factor) {
        validate(input, width, height);
        Image output(input.size());
        for (size_t i = 0; i < input.size(); ++i) {
            output[i] = clamp(factor * (static_cast<double>(input[i]) - 128.0) + 128.0);
        }
        return output;
    }

    Image invert(const Image& input, int width, int height) {
        validate(input, width, height);
        Image output(input.size());
        for (size_t i = 0; i < input.size(); ++i) {
            output[i] = 255 - input[i];
        }
        return output;
    }

    Image sepia(const Image& input, int width, int height) {
        validate(input, width, height);
        Image output(input.size());
        for (int i = 0; i < width * height; ++i) {
            double r = input[i * 3];
            double g = input[i * 3 + 1];
            double b = input[i * 3 + 2];
            output[i * 3]     = clamp(0.393 * r + 0.769 * g + 0.189 * b);
            output[i * 3 + 1] = clamp(0.349 * r + 0.686 * g + 0.168 * b);
            output[i * 3 + 2] = clamp(0.272 * r + 0.534 * g + 0.131 * b);
        }
        return output;
    }

    Image flip_horizontal(const Image& input, int width, int height) {
        validate(input, width, height);
        Image output(input.size());
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int src = (y * width + x) * 3;
                int dst = (y * width + (width - 1 - x)) * 3;
                output[dst]     = input[src];
                output[dst + 1] = input[src + 1];
                output[dst + 2] = input[src + 2];
            }
        }
        return output;
    }

    Image flip_vertical(const Image& input, int width, int height) {
        validate(input, width, height);
        Image output(input.size());
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int src = (y * width + x) * 3;
                int dst = ((height - 1 - y) * width + x) * 3;
                output[dst]     = input[src];
                output[dst + 1] = input[src + 1];
                output[dst + 2] = input[src + 2];
            }
        }
        return output;
    }

    Image box_blur(const Image& input, int width, int height, int radius) {
        validate(input, width, height);
        if (radius <= 0) throw std::invalid_argument("Blur radius must be positive");
        Image output(input.size());
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                double r = 0, g = 0, b = 0;
                int count = 0;
                for (int dy = -radius; dy <= radius; ++dy) {
                    for (int dx = -radius; dx <= radius; ++dx) {
                        int nx = x + dx;
                        int ny = y + dy;
                        if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
                            int idx = (ny * width + nx) * 3;
                            r += input[idx];
                            g += input[idx + 1];
                            b += input[idx + 2];
                            count++;
                        }
                    }
                }
                int idx = (y * width + x) * 3;
                output[idx]     = clamp(r / count);
                output[idx + 1] = clamp(g / count);
                output[idx + 2] = clamp(b / count);
            }
        }
        return output;
    }

    Image gaussian_blur(const Image& input, int width, int height, int radius) {
        validate(input, width, height);
        if (radius <= 0) throw std::invalid_argument("Blur radius must be positive");
        int size = 2 * radius + 1;
        std::vector<double> kernel(size * size);
        double sigma = radius / 2.0;
        double sum = 0.0;
        for (int dy = -radius; dy <= radius; ++dy) {
            for (int dx = -radius; dx <= radius; ++dx) {
                double value = std::exp(-(dx * dx + dy * dy) / (2.0 * sigma * sigma));
                kernel[(dy + radius) * size + (dx + radius)] = value;
                sum += value;
            }
        }
        for (auto& v : kernel) v /= sum;
        Image output(input.size());
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                double r = 0, g = 0, b = 0;
                for (int dy = -radius; dy <= radius; ++dy) {
                    for (int dx = -radius; dx <= radius; ++dx) {
                        int nx = std::clamp(x + dx, 0, width - 1);
                        int ny = std::clamp(y + dy, 0, height - 1);
                        double weight = kernel[(dy + radius) * size + (dx + radius)];
                        int idx = (ny * width + nx) * 3;
                        r += input[idx] * weight;
                        g += input[idx + 1] * weight;
                        b += input[idx + 2] * weight;
                    }
                }
                int idx = (y * width + x) * 3;
                output[idx]     = clamp(r);
                output[idx + 1] = clamp(g);
                output[idx + 2] = clamp(b);
            }
        }
        return output;
    }

    Image sharpen(const Image& input, int width, int height) {
        validate(input, width, height);
        Image output(input.size());
        const int kernel[3][3] = {
            { 0, -1,  0},
            {-1,  5, -1},
            { 0, -1,  0}
        };
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                double r = 0, g = 0, b = 0;
                for (int dy = -1; dy <= 1; ++dy) {
                    for (int dx = -1; dx <= 1; ++dx) {
                        int nx = std::clamp(x + dx, 0, width - 1);
                        int ny = std::clamp(y + dy, 0, height - 1);
                        int weight = kernel[dy + 1][dx + 1];
                        int idx = (ny * width + nx) * 3;
                        r += input[idx] * weight;
                        g += input[idx + 1] * weight;
                        b += input[idx + 2] * weight;
                    }
                }
                int idx = (y * width + x) * 3;
                output[idx]     = clamp(r);
                output[idx + 1] = clamp(g);
                output[idx + 2] = clamp(b);
            }
        }
        return output;
    }

    Image edge_detect(const Image& input, int width, int height) {
        validate(input, width, height);
        Image gray = grayscale(input, width, height);
        Image output(input.size());
        const int gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
        const int gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                double sx = 0, sy = 0;
                for (int dy = -1; dy <= 1; ++dy) {
                    for (int dx = -1; dx <= 1; ++dx) {
                        int nx = std::clamp(x + dx, 0, width - 1);
                        int ny = std::clamp(y + dy, 0, height - 1);
                        double pixel = gray[(ny * width + nx) * 3];
                        sx += pixel * gx[dy + 1][dx + 1];
                        sy += pixel * gy[dy + 1][dx + 1];
                    }
                }
                uint8_t edge = clamp(std::sqrt(sx * sx + sy * sy));
                int idx = (y * width + x) * 3;
                output[idx]     = edge;
                output[idx + 1] = edge;
                output[idx + 2] = edge;
            }
        }
        return output;
    }

} // namespace imgproc


// ============ PYBIND11 BINDINGS ============

PYBIND11_MODULE(imgproc_cpp, m) {
    m.doc() = "C++ Image Processing Library";

    m.def("grayscale", &imgproc::grayscale,
          py::arg("input"), py::arg("width"), py::arg("height"));
    m.def("brightness", &imgproc::brightness,
          py::arg("input"), py::arg("width"), py::arg("height"), py::arg("value"));
    m.def("contrast", &imgproc::contrast,
          py::arg("input"), py::arg("width"), py::arg("height"), py::arg("factor"));
    m.def("invert", &imgproc::invert,
          py::arg("input"), py::arg("width"), py::arg("height"));
    m.def("sepia", &imgproc::sepia,
          py::arg("input"), py::arg("width"), py::arg("height"));
    m.def("flip_horizontal", &imgproc::flip_horizontal,
          py::arg("input"), py::arg("width"), py::arg("height"));
    m.def("flip_vertical", &imgproc::flip_vertical,
          py::arg("input"), py::arg("width"), py::arg("height"));
    m.def("box_blur", &imgproc::box_blur,
          py::arg("input"), py::arg("width"), py::arg("height"), py::arg("radius"));
    m.def("gaussian_blur", &imgproc::gaussian_blur,
          py::arg("input"), py::arg("width"), py::arg("height"), py::arg("radius"));
    m.def("sharpen", &imgproc::sharpen,
          py::arg("input"), py::arg("width"), py::arg("height"));
    m.def("edge_detect", &imgproc::edge_detect,
          py::arg("input"), py::arg("width"), py::arg("height"));
}