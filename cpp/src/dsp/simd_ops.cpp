/**
 * @file simd_ops.cpp
 * @brief SIMD-optimized operations for DSP
 */

#include "daiw/types.hpp"

#if defined(DAIW_HAS_AVX2) && defined(DAIW_HAS_FMA)
#include <immintrin.h>
#endif

namespace daiw {
namespace simd {

/**
 * @brief Multiply-add: result = a * b + c
 */
void multiplyAdd(const float* a, const float* b, const float* c,
                 float* result, size_t count) {
#if defined(DAIW_HAS_AVX2) && defined(DAIW_HAS_FMA)
    // Process 8 floats at a time with AVX2/FMA
    size_t i = 0;
    for (; i + 8 <= count; i += 8) {
        __m256 va = _mm256_loadu_ps(a + i);
        __m256 vb = _mm256_loadu_ps(b + i);
        __m256 vc = _mm256_loadu_ps(c + i);
        __m256 vr = _mm256_fmadd_ps(va, vb, vc);
        _mm256_storeu_ps(result + i, vr);
    }
    // Scalar remainder
    for (; i < count; ++i) {
        result[i] = a[i] * b[i] + c[i];
    }
#else
    // Scalar fallback
    for (size_t i = 0; i < count; ++i) {
        result[i] = a[i] * b[i] + c[i];
    }
#endif
}

/**
 * @brief Scale buffer: result = input * gain
 */
void scale(const float* input, float gain, float* output, size_t count) {
#if defined(DAIW_HAS_AVX2)
    __m256 vgain = _mm256_set1_ps(gain);
    size_t i = 0;
    for (; i + 8 <= count; i += 8) {
        __m256 vin = _mm256_loadu_ps(input + i);
        __m256 vout = _mm256_mul_ps(vin, vgain);
        _mm256_storeu_ps(output + i, vout);
    }
    for (; i < count; ++i) {
        output[i] = input[i] * gain;
    }
#else
    for (size_t i = 0; i < count; ++i) {
        output[i] = input[i] * gain;
    }
#endif
}

/**
 * @brief Add two buffers: result = a + b
 */
void add(const float* a, const float* b, float* result, size_t count) {
#if defined(DAIW_HAS_AVX2)
    size_t i = 0;
    for (; i + 8 <= count; i += 8) {
        __m256 va = _mm256_loadu_ps(a + i);
        __m256 vb = _mm256_loadu_ps(b + i);
        __m256 vr = _mm256_add_ps(va, vb);
        _mm256_storeu_ps(result + i, vr);
    }
    for (; i < count; ++i) {
        result[i] = a[i] + b[i];
    }
#else
    for (size_t i = 0; i < count; ++i) {
        result[i] = a[i] + b[i];
    }
#endif
}

}  // namespace simd
}  // namespace daiw
