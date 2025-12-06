/*
 * iDAW_Core Version Header
 * ========================
 * 
 * Intelligent Digital Audio Workstation
 * Dual Engine Architecture
 * 
 * Copyright (c) 2025 Sean Burdges
 * MIT License
 */

#pragma once

#define IDAW_VERSION_MAJOR 1
#define IDAW_VERSION_MINOR 0
#define IDAW_VERSION_PATCH 0

#define IDAW_VERSION_STRING "1.0.0"
#define IDAW_VERSION_CODENAME "Dual Engine"
#define IDAW_VERSION_FULL "iDAW " IDAW_VERSION_STRING " (" IDAW_VERSION_CODENAME ")"

#define IDAW_COPYRIGHT "Copyright (c) 2025 Sean Burdges"
#define IDAW_LICENSE "MIT"

// Build configuration
#define IDAW_BUILD_DATE __DATE__
#define IDAW_BUILD_TIME __TIME__

// Feature flags
#define IDAW_FEATURE_SIDE_A_MEMORY      1  // 4GB monotonic buffer (RT-safe)
#define IDAW_FEATURE_SIDE_B_MEMORY      1  // synchronized_pool (AI/UI)
#define IDAW_FEATURE_PYTHON_BRIDGE      1  // pybind11 integration
#define IDAW_FEATURE_GHOST_HANDS        1  // AI-driven knob automation
#define IDAW_FEATURE_DA_VINCI_SHADERS   1  // OpenGL fragment shaders
#define IDAW_FEATURE_RING_BUFFER        1  // Lock-free MIDI transfer

// Plugin versions
#define IDAW_PLUGIN_001_VERSION "1.0.0"  // The Eraser
#define IDAW_PLUGIN_002_VERSION "1.0.0"  // The Pencil
#define IDAW_PLUGIN_003_VERSION "1.0.0"  // The Press
#define IDAW_PLUGIN_004_VERSION "1.0.0"  // The Smudge
#define IDAW_PLUGIN_005_VERSION "1.0.0"  // The Trace
#define IDAW_PLUGIN_006_VERSION "1.0.0"  // The Palette
#define IDAW_PLUGIN_007_VERSION "1.0.0"  // The Parrot

// Platform detection
#if defined(__APPLE__)
    #define IDAW_PLATFORM_MACOS 1
    #define IDAW_PLATFORM_STRING "macOS"
#elif defined(_WIN32) || defined(_WIN64)
    #define IDAW_PLATFORM_WINDOWS 1
    #define IDAW_PLATFORM_STRING "Windows"
#elif defined(__linux__)
    #define IDAW_PLATFORM_LINUX 1
    #define IDAW_PLATFORM_STRING "Linux"
#else
    #define IDAW_PLATFORM_UNKNOWN 1
    #define IDAW_PLATFORM_STRING "Unknown"
#endif

// Architecture detection
#if defined(__x86_64__) || defined(_M_X64)
    #define IDAW_ARCH_X64 1
    #define IDAW_ARCH_STRING "x64"
#elif defined(__aarch64__) || defined(_M_ARM64)
    #define IDAW_ARCH_ARM64 1
    #define IDAW_ARCH_STRING "ARM64"
#else
    #define IDAW_ARCH_UNKNOWN 1
    #define IDAW_ARCH_STRING "Unknown"
#endif

// Debug/Release
#if defined(DEBUG) || defined(_DEBUG) || !defined(NDEBUG)
    #define IDAW_DEBUG 1
    #define IDAW_BUILD_TYPE "Debug"
#else
    #define IDAW_RELEASE 1
    #define IDAW_BUILD_TYPE "Release"
#endif

namespace iDAW {
    
    /**
     * Get the full version string with codename
     */
    inline const char* getVersion() { return IDAW_VERSION_FULL; }
    
    /**
     * Get version components
     */
    inline int getVersionMajor() { return IDAW_VERSION_MAJOR; }
    inline int getVersionMinor() { return IDAW_VERSION_MINOR; }
    inline int getVersionPatch() { return IDAW_VERSION_PATCH; }
    
    /**
     * Get build information
     */
    inline const char* getBuildDate() { return IDAW_BUILD_DATE; }
    inline const char* getBuildTime() { return IDAW_BUILD_TIME; }
    inline const char* getBuildType() { return IDAW_BUILD_TYPE; }
    
    /**
     * Get platform information
     */
    inline const char* getPlatform() { return IDAW_PLATFORM_STRING; }
    inline const char* getArchitecture() { return IDAW_ARCH_STRING; }
    
    /**
     * Print version info to console
     */
    inline void printVersionInfo() {
        std::cout << "╔══════════════════════════════════════════════════════════════╗\n";
        std::cout << "║                                                              ║\n";
        std::cout << "║     ██╗██████╗  █████╗ ██╗    ██╗                           ║\n";
        std::cout << "║     ██║██╔══██╗██╔══██╗██║    ██║                           ║\n";
        std::cout << "║     ██║██║  ██║███████║██║ █╗ ██║                           ║\n";
        std::cout << "║     ██║██║  ██║██╔══██║██║███╗██║                           ║\n";
        std::cout << "║     ██║██████╔╝██║  ██║╚███╔███╔╝                           ║\n";
        std::cout << "║     ╚═╝╚═════╝ ╚═╝  ╚═╝ ╚══╝╚══╝                            ║\n";
        std::cout << "║                                                              ║\n";
        std::cout << "║           Intelligent Digital Audio Workstation              ║\n";
        std::cout << "║                   " << IDAW_VERSION_FULL << "                         ║\n";
        std::cout << "║                                                              ║\n";
        std::cout << "╚══════════════════════════════════════════════════════════════╝\n";
        std::cout << "\n";
        std::cout << "  Platform: " << IDAW_PLATFORM_STRING << " (" << IDAW_ARCH_STRING << ")\n";
        std::cout << "  Build: " << IDAW_BUILD_TYPE << " - " << IDAW_BUILD_DATE << " " << IDAW_BUILD_TIME << "\n";
        std::cout << "\n";
    }

} // namespace iDAW
