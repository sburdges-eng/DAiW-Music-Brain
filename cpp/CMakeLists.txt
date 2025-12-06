cmake_minimum_required(VERSION 3.20)

project(DAiW
    VERSION 1.0.0
    DESCRIPTION "Digital Audio intelligent Workstation - Professional DAW Plugin"
    LANGUAGES CXX
)

# =============================================================================
# Build Options
# =============================================================================

option(DAIW_BUILD_TESTS "Build test suite" ON)
option(DAIW_BUILD_BENCHMARKS "Build benchmarks" ON)
option(DAIW_BUILD_VST3 "Build VST3 plugin" ON)
option(DAIW_BUILD_AU "Build Audio Unit plugin" ON)
option(DAIW_BUILD_PYTHON "Build Python bindings" ON)
option(DAIW_ENABLE_SIMD "Enable SIMD optimizations" ON)
option(DAIW_ENABLE_ASAN "Enable AddressSanitizer" OFF)

# =============================================================================
# C++ Standard & Compiler Settings
# =============================================================================

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Export compile_commands.json for LSP
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Position independent code (required for shared libs)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# =============================================================================
# Compiler Warnings
# =============================================================================

include(cmake/CompilerWarnings.cmake)

# =============================================================================
# Sanitizers (Debug builds)
# =============================================================================

if(DAIW_ENABLE_ASAN)
    include(cmake/Sanitizers.cmake)
endif()

# =============================================================================
# Dependencies
# =============================================================================

# CPM.cmake for package management
include(cmake/CPM.cmake)

# JUCE Framework
CPMAddPackage(
    NAME JUCE
    GITHUB_REPOSITORY juce-framework/JUCE
    GIT_TAG 7.0.9
    OPTIONS
        "JUCE_BUILD_EXAMPLES OFF"
        "JUCE_BUILD_EXTRAS OFF"
)

# fmt for formatting
CPMAddPackage(
    NAME fmt
    GITHUB_REPOSITORY fmtlib/fmt
    GIT_TAG 10.1.1
)

# spdlog for logging
CPMAddPackage(
    NAME spdlog
    GITHUB_REPOSITORY gabime/spdlog
    GIT_TAG v1.12.0
    OPTIONS
        "SPDLOG_FMT_EXTERNAL ON"
)

# Catch2 for testing
if(DAIW_BUILD_TESTS)
    CPMAddPackage(
        NAME Catch2
        GITHUB_REPOSITORY catchorg/Catch2
        GIT_TAG v3.4.0
    )
endif()

# pybind11 for Python bindings
if(DAIW_BUILD_PYTHON)
    CPMAddPackage(
        NAME pybind11
        GITHUB_REPOSITORY pybind/pybind11
        GIT_TAG v2.11.1
    )
endif()

# =============================================================================
# Core Library
# =============================================================================

add_library(daiw_core STATIC
    src/core/types.cpp
    src/core/memory_pool.cpp
    src/core/lock_free_queue.cpp
    src/core/ring_buffer.cpp
    src/core/logger.cpp
)

target_include_directories(daiw_core
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_link_libraries(daiw_core
    PUBLIC
        fmt::fmt
        spdlog::spdlog
)

set_target_warnings(daiw_core)

# =============================================================================
# DSP Module
# =============================================================================

add_library(daiw_dsp STATIC
    src/dsp/simd_primitives.cpp
    src/dsp/audio_buffer.cpp
    src/dsp/envelope.cpp
    src/dsp/filters.cpp
)

target_link_libraries(daiw_dsp
    PUBLIC
        daiw_core
)

# SIMD flags
if(DAIW_ENABLE_SIMD)
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        target_compile_options(daiw_dsp PRIVATE -mavx2 -mfma)
    elseif(MSVC)
        target_compile_options(daiw_dsp PRIVATE /arch:AVX2)
    endif()
endif()

set_target_warnings(daiw_dsp)

# =============================================================================
# MIDI Module
# =============================================================================

add_library(daiw_midi STATIC
    src/midi/midi_types.cpp
    src/midi/midi_buffer.cpp
    src/midi/groove_engine.cpp
    src/midi/humanizer.cpp
)

target_link_libraries(daiw_midi
    PUBLIC
        daiw_core
        daiw_dsp
)

set_target_warnings(daiw_midi)

# =============================================================================
# Harmony Module
# =============================================================================

add_library(daiw_harmony STATIC
    src/harmony/chord.cpp
    src/harmony/progression.cpp
    src/harmony/voice_leading.cpp
)

target_link_libraries(daiw_harmony
    PUBLIC
        daiw_core
)

set_target_warnings(daiw_harmony)

# =============================================================================
# VST3 Plugin
# =============================================================================

if(DAIW_BUILD_VST3)
    juce_add_plugin(DAiWPlugin
        COMPANY_NAME "DAiW"
        PLUGIN_MANUFACTURER_CODE Daiw
        PLUGIN_CODE Daiw
        FORMATS VST3 AU Standalone
        PRODUCT_NAME "DAiW"

        IS_SYNTH FALSE
        NEEDS_MIDI_INPUT TRUE
        NEEDS_MIDI_OUTPUT TRUE
        IS_MIDI_EFFECT FALSE

        VST3_CATEGORIES "Fx" "Tools"
        AU_MAIN_TYPE "kAudioUnitType_MusicEffect"
    )

    target_sources(DAiWPlugin
        PRIVATE
            src/plugin/vst3/PluginProcessor.cpp
            src/plugin/vst3/PluginEditor.cpp
    )

    target_link_libraries(DAiWPlugin
        PRIVATE
            daiw_core
            daiw_dsp
            daiw_midi
            daiw_harmony
            juce::juce_audio_utils
            juce::juce_dsp
        PUBLIC
            juce::juce_recommended_config_flags
            juce::juce_recommended_warning_flags
    )

    # Real-time safe: no exceptions in audio thread
    target_compile_definitions(DAiWPlugin
        PRIVATE
            JUCE_WEB_BROWSER=0
            JUCE_USE_CURL=0
    )
endif()

# =============================================================================
# Python Bindings
# =============================================================================

if(DAIW_BUILD_PYTHON)
    pybind11_add_module(_daiw_cpp
        src/python/bindings.cpp
        src/python/groove_bindings.cpp
        src/python/harmony_bindings.cpp
    )

    target_link_libraries(_daiw_cpp
        PRIVATE
            daiw_core
            daiw_dsp
            daiw_midi
            daiw_harmony
    )
endif()

# =============================================================================
# Tests
# =============================================================================

if(DAIW_BUILD_TESTS)
    enable_testing()

    add_executable(daiw_tests
        tests/test_main.cpp
        tests/test_memory_pool.cpp
        tests/test_lock_free_queue.cpp
        tests/test_simd.cpp
        tests/test_groove.cpp
    )

    target_link_libraries(daiw_tests
        PRIVATE
            daiw_core
            daiw_dsp
            daiw_midi
            Catch2::Catch2WithMain
    )

    include(CTest)
    include(Catch)
    catch_discover_tests(daiw_tests)
endif()

# =============================================================================
# Benchmarks
# =============================================================================

if(DAIW_BUILD_BENCHMARKS)
    add_executable(daiw_benchmarks
        benchmarks/benchmark_main.cpp
        benchmarks/benchmark_simd.cpp
        benchmarks/benchmark_groove.cpp
    )

    target_link_libraries(daiw_benchmarks
        PRIVATE
            daiw_core
            daiw_dsp
            daiw_midi
    )
endif()

# =============================================================================
# Installation
# =============================================================================

install(TARGETS daiw_core daiw_dsp daiw_midi daiw_harmony
    EXPORT DAiWTargets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(DIRECTORY include/ DESTINATION include)

install(EXPORT DAiWTargets
    FILE DAiWTargets.cmake
    NAMESPACE DAiW::
    DESTINATION lib/cmake/DAiW
)
