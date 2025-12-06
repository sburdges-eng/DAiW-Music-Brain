/**
 * @file audio_buffer.cpp
 * @brief Audio buffer implementation
 */

#include "daiw/types.hpp"
#include <algorithm>
#include <cstring>

namespace daiw {

class AudioBuffer {
public:
    AudioBuffer(size_t numChannels, size_t numSamples)
        : numChannels_(numChannels)
        , numSamples_(numSamples)
        , data_(numChannels * numSamples, 0.0f)
    {}

    Sample* getChannelData(size_t channel) {
        if (channel >= numChannels_) return nullptr;
        return data_.data() + (channel * numSamples_);
    }

    const Sample* getChannelData(size_t channel) const {
        if (channel >= numChannels_) return nullptr;
        return data_.data() + (channel * numSamples_);
    }

    void clear() {
        std::fill(data_.begin(), data_.end(), 0.0f);
    }

    size_t getNumChannels() const { return numChannels_; }
    size_t getNumSamples() const { return numSamples_; }

private:
    size_t numChannels_;
    size_t numSamples_;
    std::vector<Sample> data_;
};

}  // namespace daiw
