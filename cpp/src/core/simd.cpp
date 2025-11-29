/**
 * DAiW SIMD Implementation
 *
 * SIMD-optimized DSP primitives with runtime dispatch.
 */

#include "daiw/simd.hpp"
#include "daiw/core.hpp"

#include <cstring>

namespace daiw {
namespace simd {

// =============================================================================
// CPU Feature Detection
// =============================================================================

namespace {

#if defined(__x86_64__) || defined(_M_X64) || defined(__i386__) || defined(_M_IX86)

#ifdef _MSC_VER
#include <intrin.h>
#else
#include <cpuid.h>
#endif

struct CPUFeatures {
    bool sse2 = false;
    bool sse4_1 = false;
    bool sse4_2 = false;
    bool avx = false;
    bool avx2 = false;
    bool avx512f = false;
    bool fma = false;

    CPUFeatures() {
        int info[4];

#ifdef _MSC_VER
        __cpuid(info, 0);
        int max_id = info[0];

        if (max_id >= 1) {
            __cpuid(info, 1);
            sse2 = (info[3] & (1 << 26)) != 0;
            sse4_1 = (info[2] & (1 << 19)) != 0;
            sse4_2 = (info[2] & (1 << 20)) != 0;
            avx = (info[2] & (1 << 28)) != 0;
            fma = (info[2] & (1 << 12)) != 0;
        }

        if (max_id >= 7) {
            __cpuid(info, 7);
            avx2 = (info[1] & (1 << 5)) != 0;
            avx512f = (info[1] & (1 << 16)) != 0;
        }
#else
        unsigned int eax, ebx, ecx, edx;

        if (__get_cpuid(1, &eax, &ebx, &ecx, &edx)) {
            sse2 = (edx & (1 << 26)) != 0;
            sse4_1 = (ecx & (1 << 19)) != 0;
            sse4_2 = (ecx & (1 << 20)) != 0;
            avx = (ecx & (1 << 28)) != 0;
            fma = (ecx & (1 << 12)) != 0;
        }

        if (__get_cpuid_count(7, 0, &eax, &ebx, &ecx, &edx)) {
            avx2 = (ebx & (1 << 5)) != 0;
            avx512f = (ebx & (1 << 16)) != 0;
        }
#endif
    }
};

#elif defined(__aarch64__) || defined(_M_ARM64)

struct CPUFeatures {
    bool neon = true;  // NEON is always available on ARM64

    CPUFeatures() {}
};

#else

struct CPUFeatures {
    // Fallback: no SIMD
    CPUFeatures() {}
};

#endif

static CPUFeatures g_cpu_features;

} // anonymous namespace

// =============================================================================
// Runtime Dispatch Functions
// =============================================================================

SimdLevel get_simd_level() {
#if defined(__x86_64__) || defined(_M_X64) || defined(__i386__) || defined(_M_IX86)
    if (g_cpu_features.avx512f) return SimdLevel::AVX512;
    if (g_cpu_features.avx2) return SimdLevel::AVX2;
    if (g_cpu_features.sse4_2) return SimdLevel::SSE4_2;
    if (g_cpu_features.sse2) return SimdLevel::SSE2;
#elif defined(__aarch64__) || defined(_M_ARM64)
    return SimdLevel::NEON;
#endif
    return SimdLevel::Scalar;
}

const char* get_simd_level_name() {
    switch (get_simd_level()) {
        case SimdLevel::AVX512: return "AVX-512";
        case SimdLevel::AVX2: return "AVX2";
        case SimdLevel::SSE4_2: return "SSE4.2";
        case SimdLevel::SSE2: return "SSE2";
        case SimdLevel::NEON: return "NEON";
        case SimdLevel::Scalar: return "Scalar";
        default: return "Unknown";
    }
}

// =============================================================================
// Fallback Scalar Implementations
// =============================================================================

namespace scalar {

void apply_gain(float* data, size_t n, float gain) {
    for (size_t i = 0; i < n; ++i) {
        data[i] *= gain;
    }
}

void mix_buffers(float* dst, const float* src, size_t n, float gain) {
    for (size_t i = 0; i < n; ++i) {
        dst[i] += src[i] * gain;
    }
}

float find_peak(const float* data, size_t n) {
    float peak = 0.0f;
    for (size_t i = 0; i < n; ++i) {
        float abs_val = data[i] < 0 ? -data[i] : data[i];
        if (abs_val > peak) peak = abs_val;
    }
    return peak;
}

void copy_buffer(float* dst, const float* src, size_t n) {
    std::memcpy(dst, src, n * sizeof(float));
}

void clear_buffer(float* data, size_t n) {
    std::memset(data, 0, n * sizeof(float));
}

void apply_ramp(float* data, size_t n, float start_gain, float end_gain) {
    if (n == 0) return;
    float delta = (end_gain - start_gain) / static_cast<float>(n);
    float gain = start_gain;
    for (size_t i = 0; i < n; ++i) {
        data[i] *= gain;
        gain += delta;
    }
}

void interleave_stereo(float* dst, const float* left, const float* right, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        dst[i * 2] = left[i];
        dst[i * 2 + 1] = right[i];
    }
}

void deinterleave_stereo(float* left, float* right, const float* src, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        left[i] = src[i * 2];
        right[i] = src[i * 2 + 1];
    }
}

} // namespace scalar

// =============================================================================
// Dispatched Functions
// =============================================================================

// These call the appropriate SIMD or scalar implementation based on runtime CPU detection.
// For simplicity, we use the inline header implementations which auto-detect at compile time.
// Runtime dispatch can be added here if needed for specific use cases.

} // namespace simd
} // namespace daiw
