cmake_minimum_required(VERSION 3.18)

project(iDAW_Core
    VERSION 1.0.0
    DESCRIPTION "iDAW C++ Core - Real-time audio processing and Python bridge"
    LANGUAGES CXX
)

# C++17 required for std::pmr and structured bindings
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Export compile commands for IDE support
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Options
option(IDAW_BUILD_TESTS "Build unit tests" ON)
option(IDAW_BUILD_PYTHON_BINDINGS "Build pybind11 Python bindings" ON)
option(IDAW_BUILD_JUCE_PLUGIN "Build JUCE plugin targets" OFF)
option(IDAW_USE_OSC "Enable OSC communication" ON)
option(IDAW_ENABLE_SANITIZERS "Enable address and undefined behavior sanitizers" OFF)

# Set default build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler warnings
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
    add_compile_options(-Wall -Wextra -Wpedantic -Wno-unused-parameter)
    if(IDAW_ENABLE_SANITIZERS)
        add_compile_options(-fsanitize=address,undefined)
        add_link_options(-fsanitize=address,undefined)
    endif()
elseif(MSVC)
    add_compile_options(/W4 /permissive-)
endif()

# Release optimizations
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
        add_compile_options(-O3 -march=native)
    endif()
endif()

# ============================================================================
# Dependencies
# ============================================================================

# Find or fetch pybind11
if(IDAW_BUILD_PYTHON_BINDINGS)
    find_package(pybind11 CONFIG QUIET)
    if(NOT pybind11_FOUND)
        message(STATUS "pybind11 not found, fetching from GitHub...")
        include(FetchContent)
        FetchContent_Declare(
            pybind11
            GIT_REPOSITORY https://github.com/pybind/pybind11
            GIT_TAG        v2.11.1
        )
        FetchContent_MakeAvailable(pybind11)
    endif()
endif()

# Find or fetch nlohmann/json for JSON parsing
find_package(nlohmann_json CONFIG QUIET)
if(NOT nlohmann_json_FOUND)
    message(STATUS "nlohmann_json not found, fetching from GitHub...")
    include(FetchContent)
    FetchContent_Declare(
        json
        GIT_REPOSITORY https://github.com/nlohmann/json
        GIT_TAG        v3.11.3
    )
    FetchContent_MakeAvailable(json)
endif()

# OSC library (liblo) - optional
if(IDAW_USE_OSC)
    find_package(PkgConfig QUIET)
    if(PkgConfig_FOUND)
        pkg_check_modules(LIBLO liblo)
    endif()
endif()

# ============================================================================
# Core Library
# ============================================================================

set(IDAW_CORE_SOURCES
    src/MemoryManager.cpp
    src/PythonBridge.cpp
    src/DreamStateComponent.cpp
    src/harmony/HarmonyEngine.cpp
    src/groove/GrooveEngine.cpp
    src/diagnostics/DiagnosticsEngine.cpp
    src/osc/OSCManager.cpp
)

set(IDAW_CORE_HEADERS
    include/MemoryManager.h
    include/PythonBridge.h
    include/DreamStateComponent.h
    include/SafetyUtils.h
    include/Version.h
    include/harmony/HarmonyEngine.h
    include/harmony/Chord.h
    include/harmony/Progression.h
    include/groove/GrooveEngine.h
    include/groove/GrooveTemplate.h
    include/diagnostics/DiagnosticsEngine.h
    include/osc/OSCManager.h
)

add_library(idaw_core STATIC ${IDAW_CORE_SOURCES} ${IDAW_CORE_HEADERS})

target_include_directories(idaw_core 
    PUBLIC 
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_link_libraries(idaw_core 
    PUBLIC 
        nlohmann_json::nlohmann_json
)

if(IDAW_USE_OSC AND LIBLO_FOUND)
    target_compile_definitions(idaw_core PUBLIC IDAW_HAS_OSC)
    target_include_directories(idaw_core PUBLIC ${LIBLO_INCLUDE_DIRS})
    target_link_libraries(idaw_core PUBLIC ${LIBLO_LIBRARIES})
endif()

# ============================================================================
# Python Bindings Module
# ============================================================================

if(IDAW_BUILD_PYTHON_BINDINGS)
    pybind11_add_module(idaw_bridge
        src/bindings/PyBindings.cpp
        src/bindings/PyHarmony.cpp
        src/bindings/PyGroove.cpp
        src/bindings/PyDiagnostics.cpp
    )
    
    target_link_libraries(idaw_bridge PRIVATE idaw_core)
    
    # Install Python module to the music_brain package
    install(TARGETS idaw_bridge
        LIBRARY DESTINATION ${CMAKE_INSTALL_PREFIX}/music_brain
    )
endif()

# ============================================================================
# Tests
# ============================================================================

if(IDAW_BUILD_TESTS)
    enable_testing()
    
    # Fetch GoogleTest
    include(FetchContent)
    FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest
        GIT_TAG        v1.14.0
    )
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(googletest)
    
    # Test executable
    add_executable(idaw_tests
        tests/test_harmony.cpp
        tests/test_groove.cpp
        tests/test_diagnostics.cpp
        tests/test_memory_manager.cpp
        tests/test_ring_buffer.cpp
    )
    
    target_link_libraries(idaw_tests PRIVATE
        idaw_core
        GTest::gtest_main
    )
    
    include(GoogleTest)
    gtest_discover_tests(idaw_tests)
endif()

# ============================================================================
# JUCE Plugin (Optional)
# ============================================================================

if(IDAW_BUILD_JUCE_PLUGIN)
    find_package(JUCE CONFIG REQUIRED)
    
    juce_add_plugin(iDAW
        PLUGIN_MANUFACTURER_CODE DAIW
        PLUGIN_CODE IDAW
        FORMATS AU VST3 Standalone
        PRODUCT_NAME "iDAW"
    )
    
    target_sources(iDAW PRIVATE
        plugins/PluginProcessor.cpp
        plugins/PluginEditor.cpp
    )
    
    target_link_libraries(iDAW PRIVATE
        idaw_core
        juce::juce_audio_utils
        juce::juce_audio_processors
    )
endif()

# ============================================================================
# Installation
# ============================================================================

include(GNUInstallDirs)

install(TARGETS idaw_core
    EXPORT idaw_core-targets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/idaw
)

install(EXPORT idaw_core-targets
    FILE idaw_core-config.cmake
    NAMESPACE idaw::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/idaw_core
)

# ============================================================================
# Summary
# ============================================================================

message(STATUS "")
message(STATUS "=== iDAW Core Configuration ===")
message(STATUS "  Version:         ${PROJECT_VERSION}")
message(STATUS "  Build type:      ${CMAKE_BUILD_TYPE}")
message(STATUS "  C++ Standard:    ${CMAKE_CXX_STANDARD}")
message(STATUS "  Python bindings: ${IDAW_BUILD_PYTHON_BINDINGS}")
message(STATUS "  JUCE plugin:     ${IDAW_BUILD_JUCE_PLUGIN}")
message(STATUS "  OSC support:     ${IDAW_USE_OSC}")
message(STATUS "  Tests:           ${IDAW_BUILD_TESTS}")
message(STATUS "===============================")
message(STATUS "")
