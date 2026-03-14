#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <cstdint>

#include "filters.h"

namespace py = pybind11;


PYBIND11_MODULE(imgproc_cpp, m) {
    m.doc() = "C++ Image Processing Library";

    m.def("grayscale", &imgproc::grayscale,
          "Convert image to grayscale",
          py::arg("input"), py::arg("width"), py::arg("height"));

    m.def("brightness", &imgproc::brightness,
          "Adjust image brightness",
          py::arg("input"), py::arg("width"), py::arg("height"), py::arg("value"));

    m.def("contrast", &imgproc::contrast,
          "Adjust image contrast",
          py::arg("input"), py::arg("width"), py::arg("height"), py::arg("factor"));

    m.def("invert", &imgproc::invert,
          "Invert image colors",
          py::arg("input"), py::arg("width"), py::arg("height"));

    m.def("sepia", &imgproc::sepia,
          "Apply sepia filter",
          py::arg("input"), py::arg("width"), py::arg("height"));

    m.def("flip_horizontal", &imgproc::flip_horizontal,
          "Flip image horizontally",
          py::arg("input"), py::arg("width"), py::arg("height"));

    m.def("flip_vertical", &imgproc::flip_vertical,
          "Flip image vertically",
          py::arg("input"), py::arg("width"), py::arg("height"));

    m.def("box_blur", &imgproc::box_blur,
          "Apply box blur",
          py::arg("input"), py::arg("width"), py::arg("height"), py::arg("radius"));

    m.def("gaussian_blur", &imgproc::gaussian_blur,
          "Apply Gaussian blur",
          py::arg("input"), py::arg("width"), py::arg("height"), py::arg("radius"));

    m.def("sharpen", &imgproc::sharpen,
          "Sharpen image",
          py::arg("input"), py::arg("width"), py::arg("height"));

    m.def("edge_detect", &imgproc::edge_detect,
          "Detect edges using Sobel operator",
          py::arg("input"), py::arg("width"), py::arg("height"));
}