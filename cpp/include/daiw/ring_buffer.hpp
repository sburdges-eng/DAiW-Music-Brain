#pragma once

#include <array>
#include <atomic>
#include <cstddef>
#include <cstring>

namespace daiw {

/**
 * Lock-free ring buffer for audio data.
 *
 * Optimized for streaming audio between threads.
 * Single-producer single-consumer (SPSC).
 */
template<typename T, size_t Capacity>
class RingBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be power of 2");

public:
    RingBuffer() : read_pos_(0), write_pos_(0) {}

    /**
     * Write samples to the buffer.
     * Returns number of samples actually written.
     */
    size_t write(const T* data, size_t count) {
        const size_t write_pos = write_pos_.load(std::memory_order_relaxed);
        const size_t read_pos = read_pos_.load(std::memory_order_acquire);

        const size_t available = Capacity - (write_pos - read_pos);
        const size_t to_write = (count < available) ? count : available;

        if (to_write == 0) return 0;

        const size_t pos = write_pos & MASK;
        const size_t first_part = (Capacity - pos < to_write) ? (Capacity - pos) : to_write;

        std::memcpy(&buffer_[pos], data, first_part * sizeof(T));

        if (first_part < to_write) {
            std::memcpy(&buffer_[0], data + first_part, (to_write - first_part) * sizeof(T));
        }

        write_pos_.store(write_pos + to_write, std::memory_order_release);
        return to_write;
    }

    /**
     * Read samples from the buffer.
     * Returns number of samples actually read.
     */
    size_t read(T* data, size_t count) {
        const size_t read_pos = read_pos_.load(std::memory_order_relaxed);
        const size_t write_pos = write_pos_.load(std::memory_order_acquire);

        const size_t available = write_pos - read_pos;
        const size_t to_read = (count < available) ? count : available;

        if (to_read == 0) return 0;

        const size_t pos = read_pos & MASK;
        const size_t first_part = (Capacity - pos < to_read) ? (Capacity - pos) : to_read;

        std::memcpy(data, &buffer_[pos], first_part * sizeof(T));

        if (first_part < to_read) {
            std::memcpy(data + first_part, &buffer_[0], (to_read - first_part) * sizeof(T));
        }

        read_pos_.store(read_pos + to_read, std::memory_order_release);
        return to_read;
    }

    /**
     * Peek at samples without consuming.
     */
    size_t peek(T* data, size_t count) const {
        const size_t read_pos = read_pos_.load(std::memory_order_relaxed);
        const size_t write_pos = write_pos_.load(std::memory_order_acquire);

        const size_t available = write_pos - read_pos;
        const size_t to_read = (count < available) ? count : available;

        if (to_read == 0) return 0;

        const size_t pos = read_pos & MASK;
        const size_t first_part = (Capacity - pos < to_read) ? (Capacity - pos) : to_read;

        std::memcpy(data, &buffer_[pos], first_part * sizeof(T));

        if (first_part < to_read) {
            std::memcpy(data + first_part, &buffer_[0], (to_read - first_part) * sizeof(T));
        }

        return to_read;
    }

    /**
     * Skip samples (advance read position without copying).
     */
    size_t skip(size_t count) {
        const size_t read_pos = read_pos_.load(std::memory_order_relaxed);
        const size_t write_pos = write_pos_.load(std::memory_order_acquire);

        const size_t available = write_pos - read_pos;
        const size_t to_skip = (count < available) ? count : available;

        read_pos_.store(read_pos + to_skip, std::memory_order_release);
        return to_skip;
    }

    /// Number of samples available to read
    size_t available_read() const {
        return write_pos_.load(std::memory_order_acquire) -
               read_pos_.load(std::memory_order_relaxed);
    }

    /// Number of samples available to write
    size_t available_write() const {
        return Capacity - available_read();
    }

    /// Check if buffer is empty
    bool empty() const { return available_read() == 0; }

    /// Check if buffer is full
    bool full() const { return available_write() == 0; }

    /// Clear the buffer
    void clear() {
        read_pos_.store(0, std::memory_order_relaxed);
        write_pos_.store(0, std::memory_order_release);
    }

    static constexpr size_t capacity() { return Capacity; }

private:
    static constexpr size_t MASK = Capacity - 1;

    alignas(64) std::array<T, Capacity> buffer_;
    alignas(64) std::atomic<size_t> read_pos_;
    alignas(64) std::atomic<size_t> write_pos_;
};

} // namespace daiw
