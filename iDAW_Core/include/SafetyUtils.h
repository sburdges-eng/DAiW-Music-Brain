/**
 * SafetyUtils.h - Safety Utilities for iDAW Dual Engine
 * 
 * Provides safety functions to prevent:
 * - Buffer overflows
 * - NaN/Infinity propagation
 * - Denormal CPU spikes
 * - Memory allocation in audio thread
 * - Plugin flip memory issues
 */

#pragma once

#include <cmath>
#include <limits>
#include <algorithm>
#include <string>
#include <atomic>

#if defined(__SSE__) || defined(_M_X64) || defined(_M_IX86)
#include <xmmintrin.h>
#endif

namespace iDAW {
namespace Safety {

// =============================================================================
// DSP SAFETY
// =============================================================================

/**
 * Enable denormal-as-zero and flush-to-zero modes for current thread.
 * Call at start of audio processing to prevent CPU spikes from denormal numbers.
 */
inline void disableDenormals() {
    #if defined(__SSE__) || defined(_M_X64) || defined(_M_IX86)
    _MM_SET_DENORMALS_ZERO_MODE(_MM_DENORMALS_ZERO_ON);
    _MM_SET_FLUSH_ZERO_MODE(_MM_FLUSH_ZERO_ON);
    #endif
}

/**
 * Check if a float value is safe for processing (not NaN, Inf, or denormal)
 */
inline bool isSafeFloat(float value) {
    return std::isfinite(value) && std::fpclassify(value) != FP_SUBNORMAL;
}

/**
 * Sanitize a float value, replacing unsafe values with a default
 */
inline float sanitizeFloat(float value, float defaultValue = 0.0f) {
    if (!std::isfinite(value) || std::fpclassify(value) == FP_SUBNORMAL) {
        return defaultValue;
    }
    return value;
}

/**
 * Clamp DSP parameter to safe range with NaN protection
 */
template<typename T>
inline T safeDSPClamp(T value, T minVal, T maxVal, T defaultVal) {
    if (!std::isfinite(static_cast<float>(value))) {
        return defaultVal;
    }
    return std::clamp(value, minVal, maxVal);
}

// =============================================================================
// COMPRESSOR SAFETY LIMITS
// =============================================================================

namespace Compressor {
    constexpr float MIN_ATTACK_MS = 0.1f;      // 0.1ms minimum (anti-click)
    constexpr float MIN_RELEASE_MS = 10.0f;    // 10ms minimum (physics limit)
    constexpr float MAX_ATTACK_MS = 500.0f;
    constexpr float MAX_RELEASE_MS = 5000.0f;
    constexpr float MIN_RATIO = 1.0f;          // 1:1 = no compression
    constexpr float MAX_RATIO = 100.0f;        // Brick wall limiting
    constexpr float MIN_THRESHOLD_DB = -60.0f;
    constexpr float MAX_THRESHOLD_DB = 0.0f;
    
    inline float safeReleaseMs(float releaseMs) {
        return std::max(MIN_RELEASE_MS, sanitizeFloat(releaseMs, 100.0f));
    }
    
    inline float safeAttackMs(float attackMs) {
        return std::clamp(sanitizeFloat(attackMs, 10.0f), MIN_ATTACK_MS, MAX_ATTACK_MS);
    }
}

// =============================================================================
// DELAY SAFETY LIMITS
// =============================================================================

namespace Delay {
    constexpr float MIN_TIME_MS = 0.0f;
    constexpr float MAX_TIME_MS = 5000.0f;     // 5 second max delay
    constexpr float MIN_FEEDBACK = 0.0f;
    constexpr float MAX_FEEDBACK = 0.99f;      // Prevent infinite feedback
    
    inline float safeDelayTime(float timeMs) {
        float safe = sanitizeFloat(timeMs, 100.0f);
        // Prevent negative delay (time travel!)
        return std::clamp(safe, MIN_TIME_MS, MAX_TIME_MS);
    }
    
    inline float safeFeedback(float feedback) {
        return std::clamp(sanitizeFloat(feedback, 0.5f), MIN_FEEDBACK, MAX_FEEDBACK);
    }
}

// =============================================================================
// REVERB SAFETY LIMITS
// =============================================================================

namespace Reverb {
    constexpr float MIN_DECAY = 0.1f;
    constexpr float MAX_DECAY = 30.0f;         // 30 seconds max
    constexpr float MIN_MIX = 0.0f;
    constexpr float MAX_MIX = 1.0f;
    
    inline float safeDecay(float decay) {
        // Prevent infinite reverb
        if (!std::isfinite(decay) || decay > 1000.0f) {
            return 2.0f;  // Default 2 second decay
        }
        return std::clamp(decay, MIN_DECAY, MAX_DECAY);
    }
}

// =============================================================================
// SATURATION SAFETY LIMITS
// =============================================================================

namespace Saturation {
    constexpr float MIN_DRIVE_DB = 0.0f;
    constexpr float MAX_DRIVE_DB = 48.0f;      // 48dB max drive (not 1000!)
    
    inline float safeDrive(float driveDb) {
        return std::clamp(sanitizeFloat(driveDb, 0.0f), MIN_DRIVE_DB, MAX_DRIVE_DB);
    }
}

// =============================================================================
// FFT SAFETY
// =============================================================================

namespace FFT {
    constexpr int MIN_WINDOW_SIZE = 64;
    constexpr int MAX_WINDOW_SIZE = 8192;
    
    inline int safeWindowSize(int size) {
        // Ensure power of 2
        int safe = std::max(MIN_WINDOW_SIZE, std::min(size, MAX_WINDOW_SIZE));
        // Round to nearest power of 2
        int power = 1;
        while (power < safe) power <<= 1;
        return power;
    }
    
    /**
     * Sanitize FFT bin magnitude - prevent erasure of ALL frequencies
     * Test 25: Eraser Singularity
     */
    inline float safeBinMagnitude(float magnitude, int binIndex, int totalBins) {
        // Never allow complete DC (bin 0) erasure
        if (binIndex == 0 && magnitude == 0.0f) {
            return 0.001f;  // Minimal DC offset
        }
        
        // Never allow complete Nyquist erasure
        if (binIndex == totalBins - 1 && magnitude == 0.0f) {
            return 0.001f;
        }
        
        return sanitizeFloat(magnitude, 0.0f);
    }
}

// =============================================================================
// SHADER UNIFORM SAFETY
// =============================================================================

namespace Shader {
    /**
     * Safe uniform value for shader rendering
     * Prevents NaN/Infinity from crashing GPU
     */
    inline float safeUniform(float value, float minVal, float maxVal, float defaultVal = 0.5f) {
        if (!std::isfinite(value)) {
            return defaultVal;
        }
        return std::clamp(value, minVal, maxVal);
    }
    
    /**
     * Test 17: Infinity Knob protection
     */
    inline float safeChaos(float chaos) {
        return safeUniform(chaos, 0.0f, 1.0f, 0.5f);
    }
    
    /**
     * Test 20: Scribble Max protection
     */
    inline float safeSketchDensity(float density) {
        return safeUniform(density, 0.0f, 10.0f, 1.0f);  // Max 1000% = 10.0
    }
    
    /**
     * Test 19: Resolution Crunch protection
     */
    inline int safeResolution(int width, int height) {
        // Minimum 16x16 pixels
        return std::max(16, std::min(width, 16384)) * 
               std::max(16, std::min(height, 16384));
    }
}

// =============================================================================
// PLUGIN LIFECYCLE SAFETY
// =============================================================================

/**
 * Test 05: Zombie Plugin protection
 * 
 * Use this pattern instead of dynamic allocation:
 * 
 * BAD:  void flip() { eraser = new EraserProcessor(); }
 * GOOD: Use bypass flags
 */
class PluginState {
public:
    void setBypassed(bool bypassed) { m_bypassed.store(bypassed); }
    bool isBypassed() const { return m_bypassed.load(); }
    
    void setValid(bool valid) { m_valid.store(valid); }
    bool isValid() const { return m_valid.load(); }
    
private:
    std::atomic<bool> m_bypassed{false};
    std::atomic<bool> m_valid{true};
};

// =============================================================================
// OUTPUT SAFETY
// =============================================================================

namespace Output {
    constexpr float MAX_OUTPUT_DB = 6.0f;      // +6dB hard limit
    constexpr float MAX_OUTPUT_LINEAR = 2.0f;  // ~+6dB
    
    /**
     * Test 30: Palette Mud protection
     * Prevent output clipping > 0dB (or +6dB with headroom)
     */
    inline float softClipOutput(float sample) {
        // Soft clip using tanh for musical limiting
        if (std::abs(sample) > 1.0f) {
            return std::tanh(sample);
        }
        return sample;
    }
    
    inline float hardLimitOutput(float sample) {
        return std::clamp(sample, -MAX_OUTPUT_LINEAR, MAX_OUTPUT_LINEAR);
    }
}

} // namespace Safety
} // namespace iDAW
