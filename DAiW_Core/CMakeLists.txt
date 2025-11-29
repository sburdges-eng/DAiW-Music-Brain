# DAiW_Core - JUCE 8 Audio Plugin with Python Bridge
# Phase 1: Foundation Infrastructure
cmake_minimum_required(VERSION 3.22)

project(DAiW_Core VERSION 1.0.0 LANGUAGES CXX)

# C++20 for std::pmr and modern features
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Debug)
endif()

# Find JUCE - can be installed via git submodule or system package
# For development, use FetchContent if not found locally
find_package(JUCE CONFIG QUIET)

if(NOT JUCE_FOUND)
    include(FetchContent)
    FetchContent_Declare(
        JUCE
        GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
        GIT_TAG 8.0.0
        GIT_SHALLOW TRUE
    )
    FetchContent_MakeAvailable(JUCE)
endif()

# Find pybind11 for Python bridge
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG QUIET)

if(NOT pybind11_FOUND)
    include(FetchContent)
    FetchContent_Declare(
        pybind11
        GIT_REPOSITORY https://github.com/pybind/pybind11.git
        GIT_TAG v2.11.1
        GIT_SHALLOW TRUE
    )
    FetchContent_MakeAvailable(pybind11)
endif()

# Define the plugin target
juce_add_plugin(DAiW_Core
    COMPANY_NAME "DAiW"
    IS_SYNTH FALSE
    NEEDS_MIDI_INPUT TRUE
    NEEDS_MIDI_OUTPUT TRUE
    PLUGIN_MANUFACTURER_CODE DAiW
    PLUGIN_CODE DaiW
    FORMATS AU VST3 Standalone
    PRODUCT_NAME "DAiW Core"
)

# Source files - Core module
target_sources(DAiW_Core PRIVATE
    Source/Core/PluginProcessor.cpp
    Source/Core/PluginEditor.cpp
)

# Source files - Memory module (Critical)
target_sources(DAiW_Core PRIVATE
    Source/Memory/MemoryManager.cpp
    Source/Memory/DAiW_Buffer.cpp
)

# Source files - UI module
target_sources(DAiW_Core PRIVATE
    Source/UI/MainComponent.cpp
    Source/UI/WorkStateComponent.cpp
    Source/UI/DreamStateComponent.cpp
    Source/UI/LookAndFeel_Metal.cpp
    Source/UI/LookAndFeel_Blueprint.cpp
)

# Source files - Python Bridge
target_sources(DAiW_Core PRIVATE
    Source/PythonBridge/PythonBridge.cpp
)

# Header files
target_include_directories(DAiW_Core PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/Source
    ${CMAKE_CURRENT_SOURCE_DIR}/Source/Core
    ${CMAKE_CURRENT_SOURCE_DIR}/Source/Memory
    ${CMAKE_CURRENT_SOURCE_DIR}/Source/UI
    ${CMAKE_CURRENT_SOURCE_DIR}/Source/PythonBridge
)

# JUCE modules
target_compile_definitions(DAiW_Core PUBLIC
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0
    # Memory configuration
    DAIW_IRON_HEAP_SIZE=4294967296  # 4GB
    DAIW_PLAYGROUND_INITIAL_SIZE=268435456  # 256MB initial
)

# Link JUCE modules
target_link_libraries(DAiW_Core
    PRIVATE
        juce::juce_audio_basics
        juce::juce_audio_devices
        juce::juce_audio_formats
        juce::juce_audio_processors
        juce::juce_audio_utils
        juce::juce_core
        juce::juce_data_structures
        juce::juce_events
        juce::juce_graphics
        juce::juce_gui_basics
        juce::juce_gui_extra
        juce::juce_opengl
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags
)

# pybind11 module for Python bridge
pybind11_add_module(daiw_logic
    Source/PythonBridge/PythonModule.cpp
)

target_link_libraries(daiw_logic PRIVATE
    DAiW_Core
    juce::juce_core
)

# Compiler-specific flags
if(MSVC)
    target_compile_options(DAiW_Core PRIVATE /W4)
else()
    target_compile_options(DAiW_Core PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Installation
install(TARGETS DAiW_Core DESTINATION lib)
install(TARGETS daiw_logic DESTINATION lib/python)
