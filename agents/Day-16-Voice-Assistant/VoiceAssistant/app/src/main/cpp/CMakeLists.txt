cmake_minimum_required(VERSION 3.22.1)
project(whisper_android)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DANDROID_STL=c++_shared")

# Add whisper.cpp as a git submodule
include(FetchContent)
FetchContent_Declare(
    whisper
    GIT_REPOSITORY https://github.com/ggerganov/whisper.cpp.git
    GIT_TAG master
)
FetchContent_MakeAvailable(whisper)

# Include directories
include_directories(${whisper_SOURCE_DIR})

# Create the native library
add_library(whisper_android SHARED
    whisper_jni.cpp
)

# Link against the whisper library
target_link_libraries(whisper_android
    whisper
    log
    android
)
