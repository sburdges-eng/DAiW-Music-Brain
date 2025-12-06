/**
 * DAiW Audio I/O Module
 *
 * Audio device management and streaming interfaces.
 * Designed to integrate with JUCE for cross-platform support.
 * Assigned to: Copilot
 *
 * Features:
 * - Audio device enumeration and selection
 * - Real-time audio streaming
 * - Sample rate conversion
 * - Latency management
 * - Audio file I/O
 */

#pragma once

#include "daiw/types.hpp"
#include "daiw/ring_buffer.hpp"

#include <vector>
#include <string>
#include <functional>
#include <memory>
#include <atomic>
#include <cstring>

namespace daiw {
namespace audio_io {

// =============================================================================
// Constants
// =============================================================================

constexpr SampleRate DEFAULT_SAMPLE_RATE = 44100;
constexpr BlockSize DEFAULT_BLOCK_SIZE = 512;
constexpr ChannelCount DEFAULT_CHANNELS = 2;
constexpr size_t MAX_CHANNELS = 64;

// =============================================================================
// Audio Device Info
// =============================================================================

/**
 * Information about an audio device.
 */
struct DeviceInfo {
    std::string name;
    std::string identifier;

    std::vector<SampleRate> supported_sample_rates;
    std::vector<BlockSize> supported_block_sizes;

    ChannelCount max_input_channels = 0;
    ChannelCount max_output_channels = 0;

    SampleRate default_sample_rate = DEFAULT_SAMPLE_RATE;
    BlockSize default_block_size = DEFAULT_BLOCK_SIZE;

    double latency_ms = 0.0;
    bool is_default = false;
};

/**
 * Audio device configuration.
 */
struct DeviceConfig {
    std::string device_identifier;
    SampleRate sample_rate = DEFAULT_SAMPLE_RATE;
    BlockSize block_size = DEFAULT_BLOCK_SIZE;
    ChannelCount input_channels = 0;
    ChannelCount output_channels = DEFAULT_CHANNELS;
};

// =============================================================================
// Audio Callback
// =============================================================================

/**
 * Audio processing callback interface.
 * Implement this to process audio in real-time.
 */
class AudioCallback {
public:
    virtual ~AudioCallback() = default;

    /**
     * Called from the audio thread to process audio.
     *
     * @param input_data  Input audio buffers (may be nullptr if no inputs)
     * @param output_data Output audio buffers (must write to these)
     * @param num_samples Number of samples to process
     * @param context     Processing context with timing info
     */
    virtual void process(const float* const* input_data,
                        float** output_data,
                        BlockSize num_samples,
                        const ProcessContext& context) = 0;

    /**
     * Called when audio device settings change.
     */
    virtual void prepare(SampleRate sample_rate, BlockSize block_size) {}

    /**
     * Called when audio is about to start.
     */
    virtual void start() {}

    /**
     * Called when audio has stopped.
     */
    virtual void stop() {}
};

// =============================================================================
// Audio Buffer
// =============================================================================

/**
 * Multi-channel audio buffer with interleaved and non-interleaved access.
 */
class AudioBuffer {
public:
    AudioBuffer() : num_channels_(0), num_samples_(0) {}

    AudioBuffer(ChannelCount channels, BlockSize samples)
        : num_channels_(channels)
        , num_samples_(samples)
        , data_(channels * samples, 0.0f)
    {
        // Set up channel pointers
        channel_ptrs_.resize(channels);
        for (ChannelCount ch = 0; ch < channels; ++ch) {
            channel_ptrs_[ch] = data_.data() + ch * samples;
        }
    }

    /// Resize buffer (clears content)
    void resize(ChannelCount channels, BlockSize samples) {
        num_channels_ = channels;
        num_samples_ = samples;
        data_.resize(channels * samples);
        data_.assign(data_.size(), 0.0f);

        channel_ptrs_.resize(channels);
        for (ChannelCount ch = 0; ch < channels; ++ch) {
            channel_ptrs_[ch] = data_.data() + ch * samples;
        }
    }

    /// Clear all samples to zero
    void clear() {
        std::fill(data_.begin(), data_.end(), 0.0f);
    }

    /// Get number of channels
    ChannelCount num_channels() const { return num_channels_; }

    /// Get number of samples per channel
    BlockSize num_samples() const { return num_samples_; }

    /// Get pointer to channel data
    float* channel(ChannelCount ch) {
        return (ch < num_channels_) ? channel_ptrs_[ch] : nullptr;
    }

    const float* channel(ChannelCount ch) const {
        return (ch < num_channels_) ? channel_ptrs_[ch] : nullptr;
    }

    /// Get array of channel pointers
    float** data() { return channel_ptrs_.data(); }
    const float* const* data() const { return channel_ptrs_.data(); }

    /// Get sample at position
    float& sample(ChannelCount ch, BlockSize idx) {
        return channel_ptrs_[ch][idx];
    }

    float sample(ChannelCount ch, BlockSize idx) const {
        return channel_ptrs_[ch][idx];
    }

    /// Copy from another buffer
    void copy_from(const AudioBuffer& other) {
        if (num_channels_ != other.num_channels_ || num_samples_ != other.num_samples_) {
            resize(other.num_channels_, other.num_samples_);
        }
        std::copy(other.data_.begin(), other.data_.end(), data_.begin());
    }

    /// Add another buffer (mixing)
    void add(const AudioBuffer& other, float gain = 1.0f) {
        ChannelCount channels = std::min(num_channels_, other.num_channels_);
        BlockSize samples = std::min(num_samples_, other.num_samples_);

        for (ChannelCount ch = 0; ch < channels; ++ch) {
            float* dst = channel_ptrs_[ch];
            const float* src = other.channel_ptrs_[ch];
            for (BlockSize i = 0; i < samples; ++i) {
                dst[i] += src[i] * gain;
            }
        }
    }

    /// Apply gain to all channels
    void apply_gain(float gain) {
        for (float& s : data_) {
            s *= gain;
        }
    }

    /// Get peak level across all channels
    float peak_level() const {
        float peak = 0.0f;
        for (float s : data_) {
            peak = std::max(peak, std::abs(s));
        }
        return peak;
    }

private:
    ChannelCount num_channels_;
    BlockSize num_samples_;
    std::vector<float> data_;
    std::vector<float*> channel_ptrs_;
};

// =============================================================================
// Audio Stream
// =============================================================================

/**
 * Buffered audio stream for non-real-time to real-time bridging.
 * Uses a ring buffer for thread-safe communication.
 */
class AudioStream {
public:
    AudioStream(ChannelCount channels, size_t buffer_samples)
        : channels_(channels)
        , buffer_(buffer_samples * channels)
        , temp_buffer_(channels)
    {}

    /// Write samples to stream (non-RT thread)
    size_t write(const float* const* data, size_t num_samples) {
        // Interleave into temp buffer
        temp_buffer_.resize(num_samples * channels_);
        for (size_t i = 0; i < num_samples; ++i) {
            for (ChannelCount ch = 0; ch < channels_; ++ch) {
                temp_buffer_[i * channels_ + ch] = data[ch][i];
            }
        }
        return buffer_.write(temp_buffer_.data(), temp_buffer_.size()) / channels_;
    }

    /// Read samples from stream (RT thread)
    size_t read(float** data, size_t num_samples) {
        // Read interleaved
        temp_buffer_.resize(num_samples * channels_);
        size_t read_count = buffer_.read(temp_buffer_.data(), temp_buffer_.size());
        size_t samples_read = read_count / channels_;

        // De-interleave
        for (size_t i = 0; i < samples_read; ++i) {
            for (ChannelCount ch = 0; ch < channels_; ++ch) {
                data[ch][i] = temp_buffer_[i * channels_ + ch];
            }
        }

        return samples_read;
    }

    /// Get available samples to read
    size_t available() const {
        return buffer_.available() / channels_;
    }

    /// Get space available for writing
    size_t space() const {
        return buffer_.space() / channels_;
    }

    /// Clear the buffer
    void clear() {
        buffer_.clear();
    }

private:
    ChannelCount channels_;
    RingBuffer<float> buffer_;
    std::vector<float> temp_buffer_;
};

// =============================================================================
// Sample Rate Converter (Simple Linear Interpolation)
// =============================================================================

/**
 * Simple sample rate converter using linear interpolation.
 * For production use, consider a higher quality algorithm.
 */
class SampleRateConverter {
public:
    SampleRateConverter(SampleRate source_rate, SampleRate target_rate)
        : source_rate_(source_rate)
        , target_rate_(target_rate)
        , ratio_(static_cast<double>(target_rate) / source_rate)
        , position_(0.0)
        , last_sample_(0.0f)
    {}

    /// Convert a block of mono audio
    size_t convert(const float* input, size_t input_samples,
                  float* output, size_t output_capacity) {
        size_t output_samples = 0;

        while (position_ < input_samples && output_samples < output_capacity) {
            size_t idx = static_cast<size_t>(position_);
            double frac = position_ - idx;

            float sample1 = (idx > 0) ? input[idx] : last_sample_;
            float sample2 = input[std::min(idx + 1, input_samples - 1)];

            output[output_samples++] = static_cast<float>(sample1 + frac * (sample2 - sample1));
            position_ += 1.0 / ratio_;
        }

        // Save state for next block
        if (input_samples > 0) {
            last_sample_ = input[input_samples - 1];
        }
        position_ -= input_samples;

        return output_samples;
    }

    /// Reset converter state
    void reset() {
        position_ = 0.0;
        last_sample_ = 0.0f;
    }

    /// Get conversion ratio
    double ratio() const { return ratio_; }

private:
    SampleRate source_rate_;
    SampleRate target_rate_;
    double ratio_;
    double position_;
    float last_sample_;
};

// =============================================================================
// Latency Compensation
// =============================================================================

/**
 * Manages latency compensation for plugin chains.
 */
class LatencyCompensator {
public:
    LatencyCompensator(size_t max_latency_samples = 8192)
        : max_latency_(max_latency_samples)
        , current_latency_(0)
    {}

    /// Set the latency to compensate for
    void set_latency(size_t samples) {
        current_latency_ = std::min(samples, max_latency_);

        // Resize delay buffers if needed
        for (auto& buffer : delay_buffers_) {
            if (buffer.size() < current_latency_) {
                buffer.resize(current_latency_, 0.0f);
            }
        }
    }

    /// Get current latency
    size_t latency() const { return current_latency_; }

    /// Process a buffer (adds delay)
    void process(AudioBuffer& buffer) {
        if (current_latency_ == 0) return;

        // Ensure we have enough delay buffers
        while (delay_buffers_.size() < buffer.num_channels()) {
            delay_buffers_.emplace_back(current_latency_, 0.0f);
            write_positions_.push_back(0);
        }

        // Apply delay to each channel
        for (ChannelCount ch = 0; ch < buffer.num_channels(); ++ch) {
            float* data = buffer.channel(ch);
            auto& delay = delay_buffers_[ch];
            size_t& write_pos = write_positions_[ch];

            for (BlockSize i = 0; i < buffer.num_samples(); ++i) {
                // Read from delay buffer
                float delayed = delay[write_pos];

                // Write to delay buffer
                delay[write_pos] = data[i];

                // Output delayed sample
                data[i] = delayed;

                // Advance position
                write_pos = (write_pos + 1) % current_latency_;
            }
        }
    }

    /// Reset all delay buffers
    void reset() {
        for (auto& buffer : delay_buffers_) {
            std::fill(buffer.begin(), buffer.end(), 0.0f);
        }
        for (auto& pos : write_positions_) {
            pos = 0;
        }
    }

private:
    size_t max_latency_;
    size_t current_latency_;
    std::vector<std::vector<float>> delay_buffers_;
    std::vector<size_t> write_positions_;
};

// =============================================================================
// Audio Device Manager Interface
// =============================================================================

/**
 * Abstract interface for audio device management.
 * Concrete implementation will use JUCE or platform-specific APIs.
 */
class AudioDeviceManager {
public:
    virtual ~AudioDeviceManager() = default;

    /// Get list of available devices
    virtual std::vector<DeviceInfo> get_devices() const = 0;

    /// Get default device
    virtual DeviceInfo get_default_device() const = 0;

    /// Open a device with configuration
    virtual bool open(const DeviceConfig& config) = 0;

    /// Close current device
    virtual void close() = 0;

    /// Start audio processing
    virtual bool start(AudioCallback* callback) = 0;

    /// Stop audio processing
    virtual void stop() = 0;

    /// Check if device is open
    virtual bool is_open() const = 0;

    /// Check if audio is running
    virtual bool is_running() const = 0;

    /// Get current configuration
    virtual DeviceConfig get_config() const = 0;

    /// Get current latency in samples
    virtual size_t get_latency_samples() const = 0;

    /// Get current latency in milliseconds
    double get_latency_ms() const {
        auto config = get_config();
        if (config.sample_rate == 0) return 0.0;
        return (get_latency_samples() * 1000.0) / config.sample_rate;
    }
};

// =============================================================================
// Null Audio Device (for testing)
// =============================================================================

/**
 * Null audio device that generates silence.
 * Useful for testing and offline rendering.
 */
class NullAudioDevice : public AudioDeviceManager {
public:
    std::vector<DeviceInfo> get_devices() const override {
        DeviceInfo info;
        info.name = "Null Device";
        info.identifier = "null";
        info.max_output_channels = 2;
        info.supported_sample_rates = {44100, 48000, 96000};
        info.supported_block_sizes = {64, 128, 256, 512, 1024, 2048};
        return {info};
    }

    DeviceInfo get_default_device() const override {
        return get_devices()[0];
    }

    bool open(const DeviceConfig& config) override {
        config_ = config;
        is_open_ = true;
        return true;
    }

    void close() override {
        stop();
        is_open_ = false;
    }

    bool start(AudioCallback* callback) override {
        if (!is_open_ || is_running_) return false;
        callback_ = callback;
        is_running_ = true;
        if (callback_) {
            callback_->prepare(config_.sample_rate, config_.block_size);
            callback_->start();
        }
        return true;
    }

    void stop() override {
        if (is_running_ && callback_) {
            callback_->stop();
        }
        is_running_ = false;
        callback_ = nullptr;
    }

    bool is_open() const override { return is_open_; }
    bool is_running() const override { return is_running_; }
    DeviceConfig get_config() const override { return config_; }
    size_t get_latency_samples() const override { return config_.block_size; }

    /// Process one block (call from test code)
    void process_block(AudioBuffer& output) {
        if (!is_running_ || !callback_) return;

        ProcessContext ctx;
        ctx.sample_rate = config_.sample_rate;
        ctx.block_size = config_.block_size;
        ctx.bpm = 120.0;
        ctx.beat_position = 0.0;
        ctx.is_playing = false;
        ctx.transport_changed = false;

        callback_->process(nullptr, output.data(), output.num_samples(), ctx);
    }

private:
    DeviceConfig config_;
    AudioCallback* callback_ = nullptr;
    bool is_open_ = false;
    bool is_running_ = false;
};

// =============================================================================
// Audio File Format
// =============================================================================

/**
 * Audio file format descriptor.
 */
struct AudioFileFormat {
    std::string extension;      // "wav", "aiff", "flac", etc.
    SampleRate sample_rate;
    ChannelCount channels;
    int bit_depth;              // 16, 24, 32
    bool is_float;              // true for 32-bit float
    size_t num_samples;         // Total samples per channel
};

/**
 * Abstract interface for audio file I/O.
 * Concrete implementation will use JUCE or libsndfile.
 */
class AudioFileReader {
public:
    virtual ~AudioFileReader() = default;

    /// Open file for reading
    virtual bool open(const std::string& path) = 0;

    /// Close file
    virtual void close() = 0;

    /// Get format info
    virtual AudioFileFormat format() const = 0;

    /// Read samples into buffer
    virtual size_t read(AudioBuffer& buffer, size_t num_samples) = 0;

    /// Seek to sample position
    virtual bool seek(size_t sample_position) = 0;

    /// Get current position
    virtual size_t position() const = 0;
};

class AudioFileWriter {
public:
    virtual ~AudioFileWriter() = default;

    /// Create file for writing
    virtual bool create(const std::string& path, const AudioFileFormat& format) = 0;

    /// Close file
    virtual void close() = 0;

    /// Write samples from buffer
    virtual size_t write(const AudioBuffer& buffer) = 0;

    /// Flush pending writes
    virtual void flush() = 0;
};

} // namespace audio_io
} // namespace daiw
