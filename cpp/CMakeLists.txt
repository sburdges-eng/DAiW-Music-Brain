# =============================================================================
# DAiW C++ Core - CMake Build Configuration
# =============================================================================
#
# This CMake configuration provides:
# - JUCE 8 Plugin scaffolding (VST3, AU, Standalone)
# - Core libraries: daiw_core, daiw_dsp, daiw_midi, daiw_harmony
# - SIMD-optimized DSP with AVX2/FMA support
# - pybind11 Python bindings for groove and harmony
# - Catch2 test suite and benchmarks
# - Real-time safe memory management
#
# Build:
#   mkdir build && cd build
#   cmake .. -DCMAKE_BUILD_TYPE=Release
#   cmake --build .
#
# =============================================================================

cmake_minimum_required(VERSION 3.21)
project(DAiW_Core VERSION 1.0.0 LANGUAGES CXX)

# =============================================================================
# C++ Standard and Compiler Settings
# =============================================================================
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Position independent code for shared libraries
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# =============================================================================
# Build Options
# =============================================================================
option(DAIW_BUILD_TESTS "Build the test suite" ON)
option(DAIW_BUILD_BENCHMARKS "Build benchmarks" OFF)
option(DAIW_BUILD_PYTHON "Build Python bindings" ON)
option(DAIW_BUILD_PLUGINS "Build VST3/AU plugins" ON)
option(DAIW_ENABLE_SIMD "Enable SIMD optimizations" ON)
option(DAIW_ENABLE_ASAN "Enable AddressSanitizer" OFF)

# =============================================================================
# Compiler Flags
# =============================================================================
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
    add_compile_options(
        -Wall
        -Wextra
        -Wpedantic
        -Wno-unused-parameter
    )

    if(DAIW_ENABLE_SIMD)
        # Check for AVX2/FMA support
        include(CheckCXXCompilerFlag)
        check_cxx_compiler_flag("-mavx2" COMPILER_SUPPORTS_AVX2)
        check_cxx_compiler_flag("-mfma" COMPILER_SUPPORTS_FMA)

        if(COMPILER_SUPPORTS_AVX2 AND COMPILER_SUPPORTS_FMA)
            add_compile_options(-mavx2 -mfma)
            add_compile_definitions(DAIW_HAS_AVX2 DAIW_HAS_FMA)
            message(STATUS "SIMD: AVX2 and FMA enabled")
        else()
            message(STATUS "SIMD: AVX2/FMA not supported, using fallback")
        endif()
    endif()

    if(DAIW_ENABLE_ASAN)
        add_compile_options(-fsanitize=address -fno-omit-frame-pointer)
        add_link_options(-fsanitize=address)
    endif()
endif()

if(MSVC)
    add_compile_options(/W4 /permissive-)
    if(DAIW_ENABLE_SIMD)
        add_compile_options(/arch:AVX2)
        add_compile_definitions(DAIW_HAS_AVX2 DAIW_HAS_FMA)
    endif()
endif()

# =============================================================================
# Dependencies
# =============================================================================

# JUCE (for plugin builds)
if(DAIW_BUILD_PLUGINS)
    # Find JUCE - users should set JUCE_DIR or add JUCE as a submodule
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/JUCE/CMakeLists.txt")
        add_subdirectory(JUCE)
        message(STATUS "JUCE: Using bundled JUCE")
    elseif(DEFINED ENV{JUCE_DIR})
        add_subdirectory($ENV{JUCE_DIR} JUCE)
        message(STATUS "JUCE: Using JUCE from JUCE_DIR")
    else()
        message(WARNING "JUCE not found. Set JUCE_DIR or add JUCE submodule. Plugin build disabled.")
        set(DAIW_BUILD_PLUGINS OFF)
    endif()
endif()

# pybind11 (for Python bindings)
if(DAIW_BUILD_PYTHON)
    find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
    include(FetchContent)
    FetchContent_Declare(
        pybind11
        GIT_REPOSITORY https://github.com/pybind/pybind11.git
        GIT_TAG v2.11.1
    )
    FetchContent_MakeAvailable(pybind11)
    message(STATUS "pybind11: Enabled for Python ${Python3_VERSION}")
endif()

# Catch2 (for tests)
if(DAIW_BUILD_TESTS)
    include(FetchContent)
    FetchContent_Declare(
        Catch2
        GIT_REPOSITORY https://github.com/catchorg/Catch2.git
        GIT_TAG v3.4.0
    )
    FetchContent_MakeAvailable(Catch2)
    list(APPEND CMAKE_MODULE_PATH ${catch2_SOURCE_DIR}/extras)
    include(CTest)
    include(Catch)
    message(STATUS "Catch2: Test framework enabled")
endif()

# =============================================================================
# Core Library: daiw_core
# =============================================================================
add_library(daiw_core STATIC
    src/core/types.cpp
    src/core/memory.cpp
    src/core/logging.cpp
)

target_include_directories(daiw_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_compile_definitions(daiw_core PUBLIC
    DAIW_VERSION_MAJOR=${PROJECT_VERSION_MAJOR}
    DAIW_VERSION_MINOR=${PROJECT_VERSION_MINOR}
    DAIW_VERSION_PATCH=${PROJECT_VERSION_PATCH}
)

# =============================================================================
# DSP Library: daiw_dsp
# =============================================================================
add_library(daiw_dsp STATIC
    src/dsp/audio_buffer.cpp
    src/dsp/simd_ops.cpp
    src/dsp/filters.cpp
)

target_include_directories(daiw_dsp PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(daiw_dsp PUBLIC daiw_core)

# =============================================================================
# MIDI Library: daiw_midi
# =============================================================================
add_library(daiw_midi STATIC
    src/midi/midi_engine.cpp
    src/midi/groove.cpp
    src/midi/humanizer.cpp
)

target_include_directories(daiw_midi PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(daiw_midi PUBLIC daiw_core)

# =============================================================================
# Harmony Library: daiw_harmony
# =============================================================================
add_library(daiw_harmony STATIC
    src/harmony/chord.cpp
    src/harmony/progression.cpp
    src/harmony/voice_leading.cpp
)

target_include_directories(daiw_harmony PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(daiw_harmony PUBLIC daiw_core)

# =============================================================================
# Python Bindings
# =============================================================================
if(DAIW_BUILD_PYTHON)
    pybind11_add_module(daiw_logic
        src/python/bindings.cpp
        src/python/groove_bindings.cpp
        src/python/harmony_bindings.cpp
    )

    target_link_libraries(daiw_logic PRIVATE
        daiw_core
        daiw_midi
        daiw_harmony
    )

    # Install to the music_brain package location
    install(TARGETS daiw_logic
        LIBRARY DESTINATION ${CMAKE_INSTALL_PREFIX}/lib
    )
endif()

# =============================================================================
# VST3/AU Plugin
# =============================================================================
if(DAIW_BUILD_PLUGINS AND TARGET juce::juce_audio_plugin_client)
    juce_add_plugin(DAiWPlugin
        COMPANY_NAME "DAiW"
        IS_SYNTH FALSE
        NEEDS_MIDI_INPUT TRUE
        NEEDS_MIDI_OUTPUT TRUE
        IS_MIDI_EFFECT FALSE
        EDITOR_WANTS_KEYBOARD_FOCUS TRUE
        COPY_PLUGIN_AFTER_BUILD TRUE
        PLUGIN_MANUFACTURER_CODE Daiw
        PLUGIN_CODE Dawi
        FORMATS VST3 AU Standalone
        PRODUCT_NAME "DAiW Brain"
    )

    target_sources(DAiWPlugin PRIVATE
        src/plugin/vst3/PluginProcessor.cpp
        src/plugin/vst3/PluginEditor.cpp
    )

    target_compile_definitions(DAiWPlugin PUBLIC
        JUCE_WEB_BROWSER=0
        JUCE_USE_CURL=0
        JUCE_VST3_CAN_REPLACE_VST2=0
    )

    target_link_libraries(DAiWPlugin PRIVATE
        juce::juce_audio_basics
        juce::juce_audio_devices
        juce::juce_audio_formats
        juce::juce_audio_plugin_client
        juce::juce_audio_processors
        juce::juce_audio_utils
        juce::juce_core
        juce::juce_data_structures
        juce::juce_events
        juce::juce_graphics
        juce::juce_gui_basics
        juce::juce_gui_extra
        daiw_core
        daiw_dsp
        daiw_midi
        daiw_harmony
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags
    )
endif()

# =============================================================================
# Tests
# =============================================================================
if(DAIW_BUILD_TESTS)
    add_executable(daiw_tests
        tests/test_main.cpp
        tests/test_memory.cpp
        tests/test_simd.cpp
        tests/test_groove.cpp
        tests/test_harmony.cpp
    )

    target_link_libraries(daiw_tests PRIVATE
        daiw_core
        daiw_dsp
        daiw_midi
        daiw_harmony
        Catch2::Catch2WithMain
    )

    catch_discover_tests(daiw_tests)
endif()

# =============================================================================
# Benchmarks
# =============================================================================
if(DAIW_BUILD_BENCHMARKS)
    add_executable(daiw_benchmarks
        benchmarks/bench_main.cpp
        benchmarks/bench_simd.cpp
        benchmarks/bench_groove.cpp
    )

    target_link_libraries(daiw_benchmarks PRIVATE
        daiw_core
        daiw_dsp
        daiw_midi
    )
endif()

# =============================================================================
# Installation
# =============================================================================
install(TARGETS daiw_core daiw_dsp daiw_midi daiw_harmony
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY include/daiw
    DESTINATION include
)

# =============================================================================
# Summary
# =============================================================================
message(STATUS "")
message(STATUS "DAiW C++ Core v${PROJECT_VERSION}")
message(STATUS "===============================")
message(STATUS "Build type:      ${CMAKE_BUILD_TYPE}")
message(STATUS "Tests:           ${DAIW_BUILD_TESTS}")
message(STATUS "Benchmarks:      ${DAIW_BUILD_BENCHMARKS}")
message(STATUS "Python bindings: ${DAIW_BUILD_PYTHON}")
message(STATUS "Plugins:         ${DAIW_BUILD_PLUGINS}")
message(STATUS "SIMD:            ${DAIW_ENABLE_SIMD}")
message(STATUS "")
