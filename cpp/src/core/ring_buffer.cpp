/**
 * DAiW Ring Buffer Implementation
 *
 * Lock-free ring buffer for audio streaming between threads.
 */

#include "daiw/ring_buffer.hpp"
#include "daiw/core.hpp"

namespace daiw {

// Template implementations are header-only.
// This file can contain specialized implementations or utilities.

namespace ring_buffer {

// Utility functions for common ring buffer operations

/**
 * Calculate optimal buffer size for given latency requirements.
 *
 * @param sample_rate Audio sample rate
 * @param latency_ms Desired latency in milliseconds
 * @param channels Number of audio channels
 * @return Recommended buffer size (power of 2)
 */
size_t calculate_buffer_size(SampleRate sample_rate, double latency_ms, ChannelCount channels) {
    size_t samples_needed = static_cast<size_t>((sample_rate * latency_ms) / 1000.0);
    samples_needed *= channels;

    // Round up to next power of 2
    size_t power = 1;
    while (power < samples_needed) {
        power *= 2;
    }

    // Add some headroom
    return power * 2;
}

/**
 * Calculate the latency in milliseconds for a given buffer size.
 */
double calculate_latency_ms(size_t buffer_size, SampleRate sample_rate, ChannelCount channels) {
    size_t samples = buffer_size / channels;
    return (static_cast<double>(samples) / sample_rate) * 1000.0;
}

} // namespace ring_buffer
} // namespace daiw
