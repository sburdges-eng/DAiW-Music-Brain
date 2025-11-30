#pragma once

#include <array>
#include <atomic>
#include <cstddef>
#include <memory>
#include <new>

namespace daiw {

/**
 * Lock-free memory pool for real-time safe allocations.
 *
 * Pre-allocates a fixed number of objects that can be acquired/released
 * without blocking. All operations are wait-free.
 *
 * Usage:
 *   MemoryPool<MyObject, 64> pool;
 *   auto* obj = pool.acquire();
 *   // use obj...
 *   pool.release(obj);
 */
template<typename T, size_t Capacity>
class MemoryPool {
public:
    MemoryPool() {
        // Initialize free list
        for (size_t i = 0; i < Capacity - 1; ++i) {
            slots_[i].next.store(i + 1, std::memory_order_relaxed);
        }
        slots_[Capacity - 1].next.store(INVALID_INDEX, std::memory_order_relaxed);
        free_head_.store(0, std::memory_order_release);
        allocated_count_.store(0, std::memory_order_relaxed);
    }

    ~MemoryPool() {
        // Destruct any objects still in use (shouldn't happen in normal use)
        for (size_t i = 0; i < Capacity; ++i) {
            if (slots_[i].in_use.load(std::memory_order_acquire)) {
                std::destroy_at(reinterpret_cast<T*>(&slots_[i].storage));
            }
        }
    }

    // Non-copyable, non-movable
    MemoryPool(const MemoryPool&) = delete;
    MemoryPool& operator=(const MemoryPool&) = delete;

    /**
     * Acquire an object from the pool.
     * Returns nullptr if pool is exhausted.
     * Thread-safe and wait-free.
     */
    template<typename... Args>
    T* acquire(Args&&... args) {
        size_t head;
        size_t new_head;

        do {
            head = free_head_.load(std::memory_order_acquire);
            if (head == INVALID_INDEX) {
                return nullptr;  // Pool exhausted
            }
            new_head = slots_[head].next.load(std::memory_order_relaxed);
        } while (!free_head_.compare_exchange_weak(
            head, new_head,
            std::memory_order_release,
            std::memory_order_relaxed));

        // Mark slot as in use
        slots_[head].in_use.store(true, std::memory_order_release);
        allocated_count_.fetch_add(1, std::memory_order_relaxed);

        // Construct object in place
        return new (&slots_[head].storage) T(std::forward<Args>(args)...);
    }

    /**
     * Release an object back to the pool.
     * Thread-safe and wait-free.
     */
    void release(T* ptr) {
        if (!ptr) return;

        // Find slot index
        auto* slot_ptr = reinterpret_cast<Slot*>(
            reinterpret_cast<char*>(ptr) - offsetof(Slot, storage));
        size_t index = slot_ptr - slots_.data();

        if (index >= Capacity) {
            return;  // Invalid pointer
        }

        // Destruct object
        std::destroy_at(ptr);

        // Mark as not in use
        slots_[index].in_use.store(false, std::memory_order_release);
        allocated_count_.fetch_sub(1, std::memory_order_relaxed);

        // Add back to free list
        size_t head;
        do {
            head = free_head_.load(std::memory_order_acquire);
            slots_[index].next.store(head, std::memory_order_relaxed);
        } while (!free_head_.compare_exchange_weak(
            head, index,
            std::memory_order_release,
            std::memory_order_relaxed));
    }

    /// Number of currently allocated objects
    size_t allocated() const {
        return allocated_count_.load(std::memory_order_relaxed);
    }

    /// Number of available slots
    size_t available() const {
        return Capacity - allocated();
    }

    /// Total capacity
    static constexpr size_t capacity() { return Capacity; }

private:
    static constexpr size_t INVALID_INDEX = ~size_t(0);

    struct Slot {
        alignas(T) std::byte storage[sizeof(T)];
        std::atomic<size_t> next{INVALID_INDEX};
        std::atomic<bool> in_use{false};
    };

    std::array<Slot, Capacity> slots_;
    std::atomic<size_t> free_head_{0};
    std::atomic<size_t> allocated_count_{0};
};

} // namespace daiw
