cmake_minimum_required(VERSION 3.14)
project(daiw_core VERSION 1.0.0 LANGUAGES CXX)

# Require C++17 for atomic operations and std::unique_ptr
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Thread support
find_package(Threads REQUIRED)

# Library target
add_library(daiw_core
    src/core/memory.cpp
)

target_include_directories(daiw_core
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_link_libraries(daiw_core
    PUBLIC
        Threads::Threads
)

# Enable testing
option(DAIW_BUILD_TESTS "Build tests" ON)

if(DAIW_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()
