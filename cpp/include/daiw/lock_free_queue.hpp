#pragma once

#include <array>
#include <atomic>
#include <cstddef>
#include <optional>

namespace daiw {

/**
 * Lock-free Single-Producer Single-Consumer (SPSC) queue.
 *
 * Perfect for audio thread communication:
 * - Main thread pushes commands
 * - Audio thread pops and processes
 *
 * Wait-free for both push and pop operations.
 */
template<typename T, size_t Capacity>
class SPSCQueue {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be power of 2");

public:
    SPSCQueue() : head_(0), tail_(0) {}

    // Non-copyable
    SPSCQueue(const SPSCQueue&) = delete;
    SPSCQueue& operator=(const SPSCQueue&) = delete;

    /**
     * Push an item (producer side).
     * Returns false if queue is full.
     */
    bool push(const T& item) {
        const size_t tail = tail_.load(std::memory_order_relaxed);
        const size_t next_tail = (tail + 1) & MASK;

        if (next_tail == head_.load(std::memory_order_acquire)) {
            return false;  // Queue full
        }

        buffer_[tail] = item;
        tail_.store(next_tail, std::memory_order_release);
        return true;
    }

    /**
     * Push with move semantics.
     */
    bool push(T&& item) {
        const size_t tail = tail_.load(std::memory_order_relaxed);
        const size_t next_tail = (tail + 1) & MASK;

        if (next_tail == head_.load(std::memory_order_acquire)) {
            return false;
        }

        buffer_[tail] = std::move(item);
        tail_.store(next_tail, std::memory_order_release);
        return true;
    }

    /**
     * Pop an item (consumer side).
     * Returns nullopt if queue is empty.
     */
    std::optional<T> pop() {
        const size_t head = head_.load(std::memory_order_relaxed);

        if (head == tail_.load(std::memory_order_acquire)) {
            return std::nullopt;  // Queue empty
        }

        T item = std::move(buffer_[head]);
        head_.store((head + 1) & MASK, std::memory_order_release);
        return item;
    }

    /**
     * Peek at front item without removing.
     */
    const T* peek() const {
        const size_t head = head_.load(std::memory_order_relaxed);

        if (head == tail_.load(std::memory_order_acquire)) {
            return nullptr;
        }

        return &buffer_[head];
    }

    /**
     * Check if queue is empty.
     */
    bool empty() const {
        return head_.load(std::memory_order_acquire) ==
               tail_.load(std::memory_order_acquire);
    }

    /**
     * Approximate size (may not be exact due to concurrent access).
     */
    size_t size_approx() const {
        const size_t head = head_.load(std::memory_order_relaxed);
        const size_t tail = tail_.load(std::memory_order_relaxed);
        return (tail - head) & MASK;
    }

    static constexpr size_t capacity() { return Capacity - 1; }

private:
    static constexpr size_t MASK = Capacity - 1;

    alignas(64) std::array<T, Capacity> buffer_;
    alignas(64) std::atomic<size_t> head_;
    alignas(64) std::atomic<size_t> tail_;
};

/**
 * Multi-Producer Single-Consumer (MPSC) queue.
 *
 * Multiple threads can push, single thread pops.
 * Useful for collecting events from multiple sources.
 */
template<typename T, size_t Capacity>
class MPSCQueue {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be power of 2");

public:
    MPSCQueue() : head_(0), tail_(0) {}

    /**
     * Push an item (can be called from multiple threads).
     */
    bool push(const T& item) {
        size_t tail;
        size_t next_tail;

        do {
            tail = tail_.load(std::memory_order_relaxed);
            next_tail = (tail + 1) & MASK;

            if (next_tail == head_.load(std::memory_order_acquire)) {
                return false;  // Queue full
            }
        } while (!tail_.compare_exchange_weak(
            tail, next_tail,
            std::memory_order_release,
            std::memory_order_relaxed));

        buffer_[tail] = item;
        return true;
    }

    /**
     * Pop an item (single consumer only).
     */
    std::optional<T> pop() {
        const size_t head = head_.load(std::memory_order_relaxed);

        if (head == tail_.load(std::memory_order_acquire)) {
            return std::nullopt;
        }

        T item = std::move(buffer_[head]);
        head_.store((head + 1) & MASK, std::memory_order_release);
        return item;
    }

    bool empty() const {
        return head_.load(std::memory_order_acquire) ==
               tail_.load(std::memory_order_acquire);
    }

private:
    static constexpr size_t MASK = Capacity - 1;

    alignas(64) std::array<T, Capacity> buffer_;
    alignas(64) std::atomic<size_t> head_;
    alignas(64) std::atomic<size_t> tail_;
};

} // namespace daiw
