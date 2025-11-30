#pragma once
/**
 * DAiW_Buffer.h - Audio buffer wrapper using MemoryManager
 *
 * DAiW Phase 1: The Foundation
 *
 * This wrapper ensures all audio buffers use the correct allocator
 * based on their SideID. It provides a safe interface for audio
 * processing that prevents accidental use of std::malloc/new.
 *
 * Usage:
 *   // For critical audio path (Iron Heap - no deallocation during runtime)
 *   DAiW_Buffer<float> audioBuffer(1024, SideID::IronHeap);
 *
 *   // For creative/experimental features (Playground - can deallocate)
 *   DAiW_Buffer<float> scratchBuffer(512, SideID::Playground);
 */

#include "MemoryManager.h"
#include <span>
#include <cstring>
#include <algorithm>

namespace daiw {
namespace memory {

/**
 * DAiW_Buffer - Type-safe audio buffer using MemoryManager
 *
 * Template Parameters:
 * - T: Element type (float for audio, int for MIDI ticks, etc.)
 *
 * Thread Safety:
 * - Construction/destruction: Not thread-safe (do in main thread)
 * - read/write operations: Thread-safe for Iron Heap buffers
 */
template<typename T>
class DAiW_Buffer {
public:
    using value_type = T;
    using size_type = std::size_t;
    using pointer = T*;
    using const_pointer = const T*;
    using reference = T&;
    using const_reference = const T&;
    using iterator = T*;
    using const_iterator = const T*;

    /**
     * Construct buffer with specified size and side
     *
     * @param size Number of elements
     * @param side Which allocator to use
     */
    DAiW_Buffer(size_type size, SideID side)
        : m_size(size), m_side(side), m_data(nullptr) {
        if (size > 0) {
            std::size_t bytes = size * sizeof(T);
            void* ptr = MemoryManager::getInstance().allocate(bytes, side, alignof(T));
            m_data = static_cast<T*>(ptr);

            // Zero-initialize for audio safety
            std::memset(m_data, 0, bytes);
        }
    }

    /**
     * Destructor - deallocates only for Playground buffers
     */
    ~DAiW_Buffer() {
        if (m_data) {
            MemoryManager::getInstance().deallocate(
                m_data, m_size * sizeof(T), m_side);
        }
    }

    // Delete copy (audio buffers should be moved, not copied)
    DAiW_Buffer(const DAiW_Buffer&) = delete;
    DAiW_Buffer& operator=(const DAiW_Buffer&) = delete;

    // Move operations
    DAiW_Buffer(DAiW_Buffer&& other) noexcept
        : m_size(other.m_size), m_side(other.m_side), m_data(other.m_data) {
        other.m_data = nullptr;
        other.m_size = 0;
    }

    DAiW_Buffer& operator=(DAiW_Buffer&& other) noexcept {
        if (this != &other) {
            // Deallocate current (if any)
            if (m_data) {
                MemoryManager::getInstance().deallocate(
                    m_data, m_size * sizeof(T), m_side);
            }

            m_data = other.m_data;
            m_size = other.m_size;
            m_side = other.m_side;

            other.m_data = nullptr;
            other.m_size = 0;
        }
        return *this;
    }

    // Element access
    [[nodiscard]] reference operator[](size_type index) noexcept {
        return m_data[index];
    }

    [[nodiscard]] const_reference operator[](size_type index) const noexcept {
        return m_data[index];
    }

    [[nodiscard]] reference at(size_type index) {
        if (index >= m_size) {
            throw std::out_of_range("DAiW_Buffer index out of range");
        }
        return m_data[index];
    }

    [[nodiscard]] const_reference at(size_type index) const {
        if (index >= m_size) {
            throw std::out_of_range("DAiW_Buffer index out of range");
        }
        return m_data[index];
    }

    // Data access
    [[nodiscard]] pointer data() noexcept { return m_data; }
    [[nodiscard]] const_pointer data() const noexcept { return m_data; }

    // Iterators
    [[nodiscard]] iterator begin() noexcept { return m_data; }
    [[nodiscard]] iterator end() noexcept { return m_data + m_size; }
    [[nodiscard]] const_iterator begin() const noexcept { return m_data; }
    [[nodiscard]] const_iterator end() const noexcept { return m_data + m_size; }
    [[nodiscard]] const_iterator cbegin() const noexcept { return m_data; }
    [[nodiscard]] const_iterator cend() const noexcept { return m_data + m_size; }

    // Capacity
    [[nodiscard]] size_type size() const noexcept { return m_size; }
    [[nodiscard]] size_type sizeBytes() const noexcept { return m_size * sizeof(T); }
    [[nodiscard]] bool empty() const noexcept { return m_size == 0; }

    // Get as std::span for interop
    [[nodiscard]] std::span<T> span() noexcept { return {m_data, m_size}; }
    [[nodiscard]] std::span<const T> span() const noexcept { return {m_data, m_size}; }

    // Properties
    [[nodiscard]] SideID side() const noexcept { return m_side; }
    [[nodiscard]] bool isIronHeap() const noexcept { return m_side == SideID::IronHeap; }
    [[nodiscard]] bool isPlayground() const noexcept { return m_side == SideID::Playground; }

    // Operations
    void clear() noexcept {
        std::memset(m_data, 0, m_size * sizeof(T));
    }

    void fill(const T& value) noexcept {
        std::fill(begin(), end(), value);
    }

    /**
     * Copy from another buffer
     *
     * @param source Source buffer to copy from
     * @param count Number of elements to copy (default: all)
     */
    void copyFrom(const DAiW_Buffer& source, size_type count = 0) {
        size_type n = count == 0 ? std::min(m_size, source.m_size) : count;
        n = std::min(n, std::min(m_size, source.m_size));
        std::memcpy(m_data, source.m_data, n * sizeof(T));
    }

    /**
     * Copy from raw pointer
     *
     * @param source Source pointer
     * @param count Number of elements to copy
     */
    void copyFrom(const T* source, size_type count) {
        size_type n = std::min(count, m_size);
        std::memcpy(m_data, source, n * sizeof(T));
    }

private:
    size_type m_size{0};
    SideID m_side{SideID::IronHeap};
    T* m_data{nullptr};
};

// =============================================================================
// Type Aliases for Common Use Cases
// =============================================================================

/// Audio sample buffer (32-bit float)
using AudioBuffer = DAiW_Buffer<float>;

/// Audio sample buffer (64-bit double)
using AudioBuffer64 = DAiW_Buffer<double>;

/// MIDI tick buffer
using MidiTickBuffer = DAiW_Buffer<int32_t>;

/// Stereo interleaved audio buffer helper
struct StereoBuffer {
    AudioBuffer left;
    AudioBuffer right;

    StereoBuffer(std::size_t size, SideID side)
        : left(size, side), right(size, side) {}

    [[nodiscard]] std::size_t size() const noexcept { return left.size(); }
    [[nodiscard]] SideID side() const noexcept { return left.side(); }
};

/// Multi-channel audio buffer
class MultiChannelBuffer {
public:
    MultiChannelBuffer(std::size_t channels, std::size_t samplesPerChannel, SideID side)
        : m_channels(channels), m_samplesPerChannel(samplesPerChannel), m_side(side) {
        m_buffers.reserve(channels);
        for (std::size_t i = 0; i < channels; ++i) {
            m_buffers.emplace_back(samplesPerChannel, side);
        }
    }

    [[nodiscard]] AudioBuffer& operator[](std::size_t channel) {
        return m_buffers[channel];
    }

    [[nodiscard]] const AudioBuffer& operator[](std::size_t channel) const {
        return m_buffers[channel];
    }

    [[nodiscard]] std::size_t numChannels() const noexcept { return m_channels; }
    [[nodiscard]] std::size_t samplesPerChannel() const noexcept { return m_samplesPerChannel; }
    [[nodiscard]] SideID side() const noexcept { return m_side; }

    void clear() {
        for (auto& buffer : m_buffers) {
            buffer.clear();
        }
    }

private:
    std::size_t m_channels;
    std::size_t m_samplesPerChannel;
    SideID m_side;
    std::vector<AudioBuffer> m_buffers;
};

} // namespace memory
} // namespace daiw
