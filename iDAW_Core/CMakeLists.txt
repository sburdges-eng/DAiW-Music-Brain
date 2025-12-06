# ==============================================================================
# iDAW Core - CMake Build System
# ==============================================================================
#
# DAiW-Music-Brain C++ Core Library
# Dual Engine Architecture with Python Bridge
#
# Build targets:
#   - idaw_core: Core C++ library (static)
#   - idaw_bridge: pybind11 Python extension module
#   - idaw_tests: Test executable
#
# Usage:
#   mkdir build && cd build
#   cmake .. -DCMAKE_BUILD_TYPE=Release
#   cmake --build .
#
# Options:
#   -DIDAW_BUILD_TESTS=ON       Build test suite (default: ON)
#   -DIDAW_BUILD_BRIDGE=ON      Build Python bridge (default: ON)
#   -DIDAW_ENABLE_JUCE=OFF      Enable JUCE integration (default: OFF)
#   -DIDAW_ENABLE_OSC=ON        Enable OSC support (default: ON)
#
# ==============================================================================

cmake_minimum_required(VERSION 3.16)

project(iDAW_Core
    VERSION 1.0.0
    DESCRIPTION "Intelligent Digital Audio Workstation - C++ Core Library"
    LANGUAGES CXX
)

# ==============================================================================
# Build Options
# ==============================================================================

option(IDAW_BUILD_TESTS "Build the test suite" ON)
option(IDAW_BUILD_BRIDGE "Build Python bridge module" ON)
option(IDAW_ENABLE_JUCE "Enable JUCE framework integration" OFF)
option(IDAW_ENABLE_OSC "Enable OSC communication support" ON)

# ==============================================================================
# C++ Standard and Compiler Flags
# ==============================================================================

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Export compile commands for IDE support
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Position independent code for shared libraries
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Compiler-specific flags
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
    add_compile_options(
        -Wall
        -Wextra
        -Wpedantic
        -Wno-unused-parameter
    )
    
    # Enable SSE for denormal flushing
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
        add_compile_options(-msse -msse2)
    endif()
    
    # Release optimizations
    if(CMAKE_BUILD_TYPE STREQUAL "Release")
        add_compile_options(-O3 -DNDEBUG)
    endif()
    
elseif(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
    add_compile_options(
        /W4
        /permissive-
        /Zc:__cplusplus
    )
    
    # Enable SSE
    add_compile_options(/arch:SSE2)
endif()

# ==============================================================================
# Dependencies
# ==============================================================================

# Find threads (required for lock-free ring buffer and async operations)
find_package(Threads REQUIRED)

# Find pybind11 for Python bridge
if(IDAW_BUILD_BRIDGE)
    find_package(Python3 COMPONENTS Interpreter Development NumPy QUIET)
    find_package(pybind11 QUIET)
    
    if(NOT pybind11_FOUND)
        message(STATUS "pybind11 not found via CMake, attempting to fetch...")
        include(FetchContent)
        FetchContent_Declare(
            pybind11
            GIT_REPOSITORY https://github.com/pybind/pybind11.git
            GIT_TAG v2.11.1
        )
        FetchContent_MakeAvailable(pybind11)
    endif()
endif()

# Find nlohmann_json for JSON parsing
find_package(nlohmann_json QUIET)
if(NOT nlohmann_json_FOUND)
    message(STATUS "nlohmann_json not found, fetching...")
    include(FetchContent)
    FetchContent_Declare(
        nlohmann_json
        GIT_REPOSITORY https://github.com/nlohmann/json.git
        GIT_TAG v3.11.3
    )
    FetchContent_MakeAvailable(nlohmann_json)
endif()

# JUCE Framework (optional)
if(IDAW_ENABLE_JUCE)
    find_package(JUCE QUIET)
    if(JUCE_FOUND)
        message(STATUS "JUCE found: ${JUCE_VERSION}")
    else()
        message(STATUS "JUCE not found - building without JUCE support")
        set(IDAW_ENABLE_JUCE OFF)
    endif()
endif()

# ==============================================================================
# Source Files
# ==============================================================================

set(IDAW_CORE_HEADERS
    include/Version.h
    include/MemoryManager.h
    include/PythonBridge.h
    include/SafetyUtils.h
    include/HarmonyCore.h
    include/GrooveCore.h
    include/DiagnosticsCore.h
    include/OSCHandler.h
)

set(IDAW_CORE_SOURCES
    src/MemoryManager.cpp
    src/PythonBridge.cpp
    src/HarmonyCore.cpp
    src/GrooveCore.cpp
    src/DiagnosticsCore.cpp
    src/OSCHandler.cpp
)

# ==============================================================================
# Core Library Target
# ==============================================================================

add_library(idaw_core STATIC
    ${IDAW_CORE_SOURCES}
    ${IDAW_CORE_HEADERS}
)

target_include_directories(idaw_core
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_link_libraries(idaw_core
    PUBLIC
        Threads::Threads
        nlohmann_json::nlohmann_json
)

# Platform-specific libraries
if(WIN32)
    target_link_libraries(idaw_core PUBLIC ws2_32)
elseif(APPLE)
    find_library(COREFOUNDATION_LIBRARY CoreFoundation)
    target_link_libraries(idaw_core PUBLIC ${COREFOUNDATION_LIBRARY})
endif()

# Add compile definitions
target_compile_definitions(idaw_core
    PUBLIC
        IDAW_VERSION_MAJOR=${PROJECT_VERSION_MAJOR}
        IDAW_VERSION_MINOR=${PROJECT_VERSION_MINOR}
        IDAW_VERSION_PATCH=${PROJECT_VERSION_PATCH}
)

if(IDAW_ENABLE_OSC)
    target_compile_definitions(idaw_core PUBLIC IDAW_ENABLE_OSC=1)
endif()

# ==============================================================================
# Python Bridge Module
# ==============================================================================

if(IDAW_BUILD_BRIDGE AND pybind11_FOUND)
    pybind11_add_module(idaw_bridge
        src/PythonBridge.cpp
        src/HarmonyCore.cpp
        src/GrooveCore.cpp
        src/DiagnosticsCore.cpp
    )
    
    target_include_directories(idaw_bridge
        PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/include
    )
    
    target_link_libraries(idaw_bridge
        PRIVATE
            nlohmann_json::nlohmann_json
            Threads::Threads
    )
    
    target_compile_definitions(idaw_bridge
        PRIVATE
            IDAW_BUILDING_PYTHON_MODULE=1
    )
    
    # Install the Python module - use configurable destination
    set(IDAW_PYTHON_MODULE_DEST "${CMAKE_CURRENT_SOURCE_DIR}/../music_brain" 
        CACHE PATH "Installation directory for Python bridge module")
    
    install(TARGETS idaw_bridge
        LIBRARY DESTINATION ${IDAW_PYTHON_MODULE_DEST}
    )
endif()

# ==============================================================================
# Test Target
# ==============================================================================

if(IDAW_BUILD_TESTS)
    enable_testing()
    
    add_executable(idaw_tests
        tests/StressTestSuite.h
        tests/test_main.cpp
    )
    
    target_include_directories(idaw_tests
        PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/include
            ${CMAKE_CURRENT_SOURCE_DIR}/tests
    )
    
    target_link_libraries(idaw_tests
        PRIVATE
            idaw_core
    )
    
    # Register tests with CTest
    add_test(NAME StressTests COMMAND idaw_tests)
endif()

# ==============================================================================
# JUCE Plugin Targets (Optional)
# ==============================================================================

if(IDAW_ENABLE_JUCE AND JUCE_FOUND)
    # Add JUCE plugin targets here when JUCE is available
    message(STATUS "JUCE integration enabled - plugin targets available")
    
    # Example JUCE plugin configuration (commented out until JUCE is properly configured)
    # juce_add_plugin(iDAW_Eraser
    #     VERSION 1.0.0
    #     COMPANY_NAME "DAiW"
    #     PLUGIN_MANUFACTURER_CODE DAIW
    #     PLUGIN_CODE ERAS
    #     FORMATS AU VST3 Standalone
    #     PRODUCT_NAME "The Eraser"
    # )
endif()

# ==============================================================================
# Installation
# ==============================================================================

install(TARGETS idaw_core
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY include/
    DESTINATION include/idaw
    FILES_MATCHING PATTERN "*.h"
)

# ==============================================================================
# Summary
# ==============================================================================

message(STATUS "")
message(STATUS "╔══════════════════════════════════════════════════════════════╗")
message(STATUS "║                   iDAW Core Build Summary                    ║")
message(STATUS "╠══════════════════════════════════════════════════════════════╣")
message(STATUS "║  Version:        ${PROJECT_VERSION}")
message(STATUS "║  Build Type:     ${CMAKE_BUILD_TYPE}")
message(STATUS "║  C++ Standard:   C++${CMAKE_CXX_STANDARD}")
message(STATUS "║  Platform:       ${CMAKE_SYSTEM_NAME} (${CMAKE_SYSTEM_PROCESSOR})")
message(STATUS "╠══════════════════════════════════════════════════════════════╣")
message(STATUS "║  Options:                                                    ║")
message(STATUS "║    Build Tests:       ${IDAW_BUILD_TESTS}")
message(STATUS "║    Build Bridge:      ${IDAW_BUILD_BRIDGE}")
message(STATUS "║    Enable JUCE:       ${IDAW_ENABLE_JUCE}")
message(STATUS "║    Enable OSC:        ${IDAW_ENABLE_OSC}")
message(STATUS "╚══════════════════════════════════════════════════════════════╝")
message(STATUS "")
