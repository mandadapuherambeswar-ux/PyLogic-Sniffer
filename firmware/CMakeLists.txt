cmake_minimum_required(VERSION 3.10)
project(PyLogicSnifferFirmware C)

set(CMAKE_C_STANDARD 11)

# Include Header Directories
include_directories(include)

# Add Executable Source Files
add_executable(pylogic_firmware
    src/main.c
    src/capture_engine.c
)
