cmake_minimum_required(VERSION 3.16)
project(imgproc_cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Fix the warning: use modern Python finder
set(PYBIND11_FINDPYTHON ON)

find_package(pybind11 REQUIRED)

pybind11_add_module(imgproc_cpp
    cpp/src/filters_all.cpp
)