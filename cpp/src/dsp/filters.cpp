/**
 * @file filters.cpp
 * @brief Audio filter implementations
 */

#include "daiw/types.hpp"
#include <cmath>

namespace daiw {
namespace filters {

/**
 * @brief Simple one-pole lowpass filter
 */
class OnePoleLP {
public:
    explicit OnePoleLP(float cutoff = 0.5f) : a0_(0.0f), b1_(0.0f), z1_(0.0f) {
        setCutoff(cutoff);
    }

    void setCutoff(float cutoff) {
        b1_ = std::exp(-2.0f * 3.14159265f * cutoff);
        a0_ = 1.0f - b1_;
    }

    float process(float input) {
        z1_ = input * a0_ + z1_ * b1_;
        return z1_;
    }

    void reset() { z1_ = 0.0f; }

private:
    float a0_, b1_, z1_;
};

/**
 * @brief Biquad filter (second-order IIR)
 */
class Biquad {
public:
    enum class Type { LowPass, HighPass, BandPass, Notch, Peak };

    Biquad() { reset(); }

    void setCoefficients(float a0, float a1, float a2, float b0, float b1, float b2) {
        a0_ = a0; a1_ = a1; a2_ = a2;
        b0_ = b0; b1_ = b1; b2_ = b2;
    }

    void setLowPass(float freq, float q, float sampleRate) {
        float omega = 2.0f * 3.14159265f * freq / sampleRate;
        float sinOmega = std::sin(omega);
        float cosOmega = std::cos(omega);
        float alpha = sinOmega / (2.0f * q);

        float a0 = 1.0f + alpha;
        b0_ = ((1.0f - cosOmega) / 2.0f) / a0;
        b1_ = (1.0f - cosOmega) / a0;
        b2_ = b0_;
        a0_ = 1.0f;
        a1_ = (-2.0f * cosOmega) / a0;
        a2_ = (1.0f - alpha) / a0;
    }

    float process(float input) {
        float output = b0_ * input + b1_ * x1_ + b2_ * x2_
                     - a1_ * y1_ - a2_ * y2_;
        x2_ = x1_; x1_ = input;
        y2_ = y1_; y1_ = output;
        return output;
    }

    void reset() {
        x1_ = x2_ = y1_ = y2_ = 0.0f;
    }

private:
    float a0_ = 1.0f, a1_ = 0.0f, a2_ = 0.0f;
    float b0_ = 1.0f, b1_ = 0.0f, b2_ = 0.0f;
    float x1_ = 0.0f, x2_ = 0.0f;
    float y1_ = 0.0f, y2_ = 0.0f;
};

}  // namespace filters
}  // namespace daiw
