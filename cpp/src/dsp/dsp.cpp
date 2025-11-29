/**
 * DAiW DSP Module Implementation
 *
 * Digital signal processing utilities for audio.
 */

#include "daiw/simd.hpp"
#include "daiw/types.hpp"
#include "daiw/core.hpp"

#include <cmath>
#include <algorithm>

namespace daiw {
namespace dsp {

// =============================================================================
// Constants
// =============================================================================

constexpr float PI = 3.14159265358979323846f;
constexpr float TWO_PI = 2.0f * PI;
constexpr float HALF_PI = PI / 2.0f;

// =============================================================================
// Basic DSP Operations
// =============================================================================

/**
 * Convert linear amplitude to decibels.
 */
float linear_to_db(float linear) {
    if (linear <= 0.0f) return -144.0f;  // Silence threshold
    return 20.0f * std::log10(linear);
}

/**
 * Convert decibels to linear amplitude.
 */
float db_to_linear(float db) {
    return std::pow(10.0f, db / 20.0f);
}

/**
 * Convert MIDI note to frequency (A4 = 440Hz).
 */
float midi_to_freq(float midi_note) {
    return 440.0f * std::pow(2.0f, (midi_note - 69.0f) / 12.0f);
}

/**
 * Convert frequency to MIDI note.
 */
float freq_to_midi(float freq) {
    return 69.0f + 12.0f * std::log2(freq / 440.0f);
}

/**
 * Soft clip distortion.
 */
float soft_clip(float x) {
    if (x > 1.0f) return 1.0f;
    if (x < -1.0f) return -1.0f;
    return 1.5f * x - 0.5f * x * x * x;
}

/**
 * Hard clip.
 */
float hard_clip(float x, float threshold = 1.0f) {
    return std::clamp(x, -threshold, threshold);
}

// =============================================================================
// Envelope Follower
// =============================================================================

class EnvelopeFollower {
public:
    EnvelopeFollower(SampleRate sample_rate = 44100)
        : sample_rate_(sample_rate)
        , envelope_(0.0f)
    {
        set_attack_ms(10.0f);
        set_release_ms(100.0f);
    }

    void set_attack_ms(float ms) {
        attack_coef_ = std::exp(-1.0f / (sample_rate_ * ms * 0.001f));
    }

    void set_release_ms(float ms) {
        release_coef_ = std::exp(-1.0f / (sample_rate_ * ms * 0.001f));
    }

    float process(float input) DAIW_RT_SAFE {
        float abs_input = std::abs(input);

        if (abs_input > envelope_) {
            envelope_ = attack_coef_ * (envelope_ - abs_input) + abs_input;
        } else {
            envelope_ = release_coef_ * (envelope_ - abs_input) + abs_input;
        }

        return envelope_;
    }

    void reset() {
        envelope_ = 0.0f;
    }

private:
    SampleRate sample_rate_;
    float attack_coef_;
    float release_coef_;
    float envelope_;
};

// =============================================================================
// Simple Filters
// =============================================================================

/**
 * One-pole lowpass filter (6dB/oct).
 */
class OnePoleFilter {
public:
    OnePoleFilter() : z1_(0.0f), a0_(1.0f), b1_(0.0f) {}

    void set_cutoff(float freq, SampleRate sample_rate) {
        float fc = freq / sample_rate;
        b1_ = std::exp(-TWO_PI * fc);
        a0_ = 1.0f - b1_;
    }

    float process(float input) DAIW_RT_SAFE {
        z1_ = input * a0_ + z1_ * b1_;
        return z1_;
    }

    void reset() {
        z1_ = 0.0f;
    }

private:
    float z1_;
    float a0_, b1_;
};

/**
 * Biquad filter (12dB/oct).
 */
class BiquadFilter {
public:
    enum class Type {
        Lowpass,
        Highpass,
        Bandpass,
        Notch,
        Peak,
        LowShelf,
        HighShelf
    };

    BiquadFilter() {
        reset();
        a0_ = 1.0f; a1_ = 0.0f; a2_ = 0.0f;
        b0_ = 1.0f; b1_ = 0.0f; b2_ = 0.0f;
    }

    void set_params(Type type, float freq, float q, float gain_db, SampleRate sample_rate) {
        float A = std::pow(10.0f, gain_db / 40.0f);
        float w0 = TWO_PI * freq / sample_rate;
        float cos_w0 = std::cos(w0);
        float sin_w0 = std::sin(w0);
        float alpha = sin_w0 / (2.0f * q);

        switch (type) {
            case Type::Lowpass:
                b0_ = (1.0f - cos_w0) / 2.0f;
                b1_ = 1.0f - cos_w0;
                b2_ = (1.0f - cos_w0) / 2.0f;
                a0_ = 1.0f + alpha;
                a1_ = -2.0f * cos_w0;
                a2_ = 1.0f - alpha;
                break;

            case Type::Highpass:
                b0_ = (1.0f + cos_w0) / 2.0f;
                b1_ = -(1.0f + cos_w0);
                b2_ = (1.0f + cos_w0) / 2.0f;
                a0_ = 1.0f + alpha;
                a1_ = -2.0f * cos_w0;
                a2_ = 1.0f - alpha;
                break;

            case Type::Bandpass:
                b0_ = alpha;
                b1_ = 0.0f;
                b2_ = -alpha;
                a0_ = 1.0f + alpha;
                a1_ = -2.0f * cos_w0;
                a2_ = 1.0f - alpha;
                break;

            case Type::Notch:
                b0_ = 1.0f;
                b1_ = -2.0f * cos_w0;
                b2_ = 1.0f;
                a0_ = 1.0f + alpha;
                a1_ = -2.0f * cos_w0;
                a2_ = 1.0f - alpha;
                break;

            case Type::Peak:
                b0_ = 1.0f + alpha * A;
                b1_ = -2.0f * cos_w0;
                b2_ = 1.0f - alpha * A;
                a0_ = 1.0f + alpha / A;
                a1_ = -2.0f * cos_w0;
                a2_ = 1.0f - alpha / A;
                break;

            case Type::LowShelf: {
                float sqrtA = std::sqrt(A);
                b0_ = A * ((A + 1.0f) - (A - 1.0f) * cos_w0 + 2.0f * sqrtA * alpha);
                b1_ = 2.0f * A * ((A - 1.0f) - (A + 1.0f) * cos_w0);
                b2_ = A * ((A + 1.0f) - (A - 1.0f) * cos_w0 - 2.0f * sqrtA * alpha);
                a0_ = (A + 1.0f) + (A - 1.0f) * cos_w0 + 2.0f * sqrtA * alpha;
                a1_ = -2.0f * ((A - 1.0f) + (A + 1.0f) * cos_w0);
                a2_ = (A + 1.0f) + (A - 1.0f) * cos_w0 - 2.0f * sqrtA * alpha;
                break;
            }

            case Type::HighShelf: {
                float sqrtA = std::sqrt(A);
                b0_ = A * ((A + 1.0f) + (A - 1.0f) * cos_w0 + 2.0f * sqrtA * alpha);
                b1_ = -2.0f * A * ((A - 1.0f) + (A + 1.0f) * cos_w0);
                b2_ = A * ((A + 1.0f) + (A - 1.0f) * cos_w0 - 2.0f * sqrtA * alpha);
                a0_ = (A + 1.0f) - (A - 1.0f) * cos_w0 + 2.0f * sqrtA * alpha;
                a1_ = 2.0f * ((A - 1.0f) - (A + 1.0f) * cos_w0);
                a2_ = (A + 1.0f) - (A - 1.0f) * cos_w0 - 2.0f * sqrtA * alpha;
                break;
            }
        }

        // Normalize
        b0_ /= a0_;
        b1_ /= a0_;
        b2_ /= a0_;
        a1_ /= a0_;
        a2_ /= a0_;
        a0_ = 1.0f;
    }

    float process(float input) DAIW_RT_SAFE {
        float output = b0_ * input + b1_ * x1_ + b2_ * x2_ - a1_ * y1_ - a2_ * y2_;
        x2_ = x1_;
        x1_ = input;
        y2_ = y1_;
        y1_ = output;
        return output;
    }

    void reset() {
        x1_ = x2_ = y1_ = y2_ = 0.0f;
    }

private:
    float a0_, a1_, a2_;
    float b0_, b1_, b2_;
    float x1_ = 0.0f, x2_ = 0.0f;
    float y1_ = 0.0f, y2_ = 0.0f;
};

// =============================================================================
// Delay Line
// =============================================================================

/**
 * Simple delay line with linear interpolation.
 */
class DelayLine {
public:
    DelayLine(size_t max_delay_samples = 48000)
        : buffer_(max_delay_samples, 0.0f)
        , write_pos_(0)
        , max_delay_(max_delay_samples)
    {}

    void write(float sample) DAIW_RT_SAFE {
        buffer_[write_pos_] = sample;
        write_pos_ = (write_pos_ + 1) % max_delay_;
    }

    float read(float delay_samples) const DAIW_RT_SAFE {
        float read_pos = static_cast<float>(write_pos_) - delay_samples;
        while (read_pos < 0.0f) read_pos += max_delay_;

        size_t pos1 = static_cast<size_t>(read_pos) % max_delay_;
        size_t pos2 = (pos1 + 1) % max_delay_;
        float frac = read_pos - std::floor(read_pos);

        return buffer_[pos1] * (1.0f - frac) + buffer_[pos2] * frac;
    }

    void clear() {
        std::fill(buffer_.begin(), buffer_.end(), 0.0f);
    }

private:
    std::vector<float> buffer_;
    size_t write_pos_;
    size_t max_delay_;
};

} // namespace dsp
} // namespace daiw
