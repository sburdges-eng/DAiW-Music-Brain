/**
 * DAiW Memory Manager - PMR-based Memory Management
 *
 * Provides efficient memory allocation with Side A (Work) / Side B (Dream) states.
 * Uses C++17 polymorphic memory resources for zero-overhead switching.
 */

#pragma once

#include <memory_resource>
#include <atomic>
#include <mutex>
#include <vector>
#include <string>

#include "daiw/core.hpp"

namespace daiw {
namespace memory {

/**
 * MemoryManager - Dual-state memory allocation system.
 *
 * Side A (Work State): Normal operation, persistent allocations
 * Side B (Dream State): Temporary allocations that can be bulk-released
 *
 * This enables instant memory cleanup when switching states,
 * perfect for creative exploration modes.
 */
class MemoryManager {
public:
    static MemoryManager& getInstance() {
        static MemoryManager instance;
        return instance;
    }

    MemoryManager(const MemoryManager&) = delete;
    MemoryManager& operator=(const MemoryManager&) = delete;

    // =========================================================================
    // State Management
    // =========================================================================

    enum class State {
        SideA_Work,     // Normal persistent allocations
        SideB_Dream     // Temporary, bulk-releasable allocations
    };

    /**
     * Get current memory state.
     */
    State getCurrentState() const {
        return currentState_.load(std::memory_order_acquire);
    }

    /**
     * Switch to Side A (Work State).
     * This purges all Side B allocations.
     */
    void switchToSideA() {
        std::lock_guard<std::mutex> lock(stateMutex_);

        if (currentState_.load() == State::SideB_Dream) {
            purgeDreamState();
        }
        currentState_.store(State::SideA_Work, std::memory_order_release);

        DBG("Switched to Side A (Work State)");
    }

    /**
     * Switch to Side B (Dream State).
     * Allocations in this state can be bulk-released.
     */
    void switchToSideB() {
        std::lock_guard<std::mutex> lock(stateMutex_);
        currentState_.store(State::SideB_Dream, std::memory_order_release);

        DBG("Switched to Side B (Dream State)");
    }

    /**
     * Purge all Dream State memory.
     * INSTANTLY releases all memory used by Side B allocations.
     */
    void purgeDreamState() {
        std::lock_guard<std::mutex> lock(sideBMutex_);

        // Release all Side B memory at once
        sideB_buffer_.release();
        sideBAllocations_ = 0;
        sideBBytesUsed_ = 0;

        DBG("Side B Memory Purged. Heap is clean.");
    }

    // =========================================================================
    // Allocators
    // =========================================================================

    /**
     * Get allocator for current state.
     */
    std::pmr::memory_resource* getAllocator() {
        if (currentState_.load() == State::SideB_Dream) {
            return getSideBAllocator();
        }
        return getSideAAllocator();
    }

    /**
     * Get Side A (persistent) allocator.
     */
    std::pmr::memory_resource* getSideAAllocator() {
        return &threadSafePool_;
    }

    /**
     * Get Side B (temporary) allocator.
     */
    std::pmr::memory_resource* getSideBAllocator() {
        return &sideB_buffer_;
    }

    // =========================================================================
    // Statistics
    // =========================================================================

    struct Stats {
        size_t sideBAllocations;
        size_t sideBBytesUsed;
        State currentState;
    };

    Stats getStats() const {
        return {
            sideBAllocations_.load(),
            sideBBytesUsed_.load(),
            currentState_.load()
        };
    }

    /**
     * Track an allocation (call from custom allocators).
     */
    void trackSideBAllocation(size_t bytes) {
        sideBAllocations_.fetch_add(1, std::memory_order_relaxed);
        sideBBytesUsed_.fetch_add(bytes, std::memory_order_relaxed);
    }

private:
    MemoryManager()
        : threadSafePool_()
        , sideB_buffer_(&threadSafePool_)
        , currentState_(State::SideA_Work)
        , sideBAllocations_(0)
        , sideBBytesUsed_(0)
    {}

    // Upstream: Thread-safe system allocator
    std::pmr::synchronized_pool_resource threadSafePool_;

    // Downstream: Wipeable buffer for Side B (attached to pool for thread safety)
    std::pmr::monotonic_buffer_resource sideB_buffer_;

    // State tracking
    std::atomic<State> currentState_;
    std::mutex stateMutex_;
    std::mutex sideBMutex_;

    // Statistics
    std::atomic<size_t> sideBAllocations_;
    std::atomic<size_t> sideBBytesUsed_;
};

// =============================================================================
// PMR-Enabled Containers for Side B
// =============================================================================

/**
 * String type that uses the current memory state's allocator.
 */
using pmr_string = std::pmr::string;

/**
 * Vector type that uses the current memory state's allocator.
 */
template<typename T>
using pmr_vector = std::pmr::vector<T>;

/**
 * Create a Side B string (will be released on state switch).
 */
inline pmr_string makeDreamString(const char* str) {
    return pmr_string(str, MemoryManager::getInstance().getSideBAllocator());
}

/**
 * Create a Side B vector (will be released on state switch).
 */
template<typename T>
pmr_vector<T> makeDreamVector() {
    return pmr_vector<T>(MemoryManager::getInstance().getSideBAllocator());
}

// =============================================================================
// RAII State Guard
// =============================================================================

/**
 * RAII guard that switches to Dream State and auto-purges on destruction.
 */
class DreamStateGuard {
public:
    DreamStateGuard() {
        MemoryManager::getInstance().switchToSideB();
    }

    ~DreamStateGuard() {
        MemoryManager::getInstance().switchToSideA();
    }

    DreamStateGuard(const DreamStateGuard&) = delete;
    DreamStateGuard& operator=(const DreamStateGuard&) = delete;
};

} // namespace memory
} // namespace daiw
