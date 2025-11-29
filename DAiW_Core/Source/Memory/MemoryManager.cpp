/**
 * MemoryManager.cpp - Implementation of dual allocator system
 *
 * Phase 1: The Foundation - Memory Architecture (CRITICAL)
 */

#include "MemoryManager.h"
#include <cassert>
#include <iostream>

namespace daiw {
namespace memory {

// =============================================================================
// MemoryManager Implementation
// =============================================================================

MemoryManager& MemoryManager::getInstance() {
    static MemoryManager instance;
    return instance;
}

MemoryManager::MemoryManager() {
    initialize();
}

MemoryManager::~MemoryManager() {
    // Resources cleaned up by unique_ptr
    m_initialized = false;
}

void MemoryManager::initialize() {
    std::lock_guard<std::mutex> lock(m_initMutex);

    if (m_initialized) {
        return;
    }

    // Allocate Iron Heap buffer (4GB)
    // Using aligned allocation for optimal performance
    try {
        m_ironHeapBuffer = std::make_unique<std::byte[]>(IRON_HEAP_SIZE);

        // Create monotonic buffer resource with our pre-allocated memory
        m_ironHeap = std::make_unique<std::pmr::monotonic_buffer_resource>(
            m_ironHeapBuffer.get(),
            IRON_HEAP_SIZE,
            std::pmr::null_memory_resource()  // Never fall back to heap
        );

        // Create synchronized pool for Playground
        std::pmr::pool_options options;
        options.max_blocks_per_chunk = 128;
        options.largest_required_pool_block = 1024 * 1024;  // 1MB max block

        m_playground = std::make_unique<std::pmr::synchronized_pool_resource>(
            options,
            std::pmr::get_default_resource()  // Falls back to default allocator
        );

        m_initialized = true;

    } catch (const std::bad_alloc& e) {
        // Log error - in production would use proper logging
        std::cerr << "MemoryManager: Failed to allocate Iron Heap: "
                  << e.what() << std::endl;
        throw;
    }
}

void* MemoryManager::allocate(std::size_t bytes, SideID side,
                               std::size_t alignment) {
    assert(m_initialized && "MemoryManager not initialized");

    if (bytes == 0) {
        return nullptr;
    }

    void* ptr = nullptr;

    switch (side) {
        case SideID::IronHeap: {
            // Check remaining capacity
            std::size_t remaining = IRON_HEAP_SIZE - m_ironHeapUsed.load();
            if (bytes > remaining) {
                throw std::bad_alloc();
            }

            ptr = m_ironHeap->allocate(bytes, alignment);
            m_ironHeapUsed.fetch_add(bytes, std::memory_order_relaxed);
            break;
        }

        case SideID::Playground: {
            ptr = m_playground->allocate(bytes, alignment);
            std::size_t newUsed = m_playgroundUsed.fetch_add(
                bytes, std::memory_order_relaxed) + bytes;

            // Update peak usage
            std::size_t peak = m_playgroundPeak.load(std::memory_order_relaxed);
            while (newUsed > peak &&
                   !m_playgroundPeak.compare_exchange_weak(
                       peak, newUsed, std::memory_order_relaxed)) {
                // Retry
            }
            break;
        }
    }

    if (ptr) {
        m_allocationCount.fetch_add(1, std::memory_order_relaxed);
    }

    return ptr;
}

void MemoryManager::deallocate(void* ptr, std::size_t bytes, SideID side) {
    if (ptr == nullptr || bytes == 0) {
        return;
    }

    switch (side) {
        case SideID::IronHeap:
            // NO-OP: Iron Heap is monotonic, no deallocation
            // Memory only reclaimed during resetIronHeap()
            break;

        case SideID::Playground:
            m_playground->deallocate(ptr, bytes);
            m_playgroundUsed.fetch_sub(bytes, std::memory_order_relaxed);
            m_deallocationCount.fetch_add(1, std::memory_order_relaxed);
            break;
    }
}

std::pmr::memory_resource* MemoryManager::getResource(SideID side) {
    assert(m_initialized && "MemoryManager not initialized");

    switch (side) {
        case SideID::IronHeap:
            return m_ironHeap.get();
        case SideID::Playground:
            return m_playground.get();
    }

    return nullptr;  // Should never reach
}

void MemoryManager::resetIronHeap() {
    std::lock_guard<std::mutex> lock(m_initMutex);

    // WARNING: This invalidates ALL Iron Heap pointers!
    // Only call when safe (no audio processing in progress)

    // Recreate the monotonic resource
    m_ironHeap = std::make_unique<std::pmr::monotonic_buffer_resource>(
        m_ironHeapBuffer.get(),
        IRON_HEAP_SIZE,
        std::pmr::null_memory_resource()
    );

    m_ironHeapUsed = 0;
}

bool MemoryManager::isInitialized() const noexcept {
    return m_initialized.load(std::memory_order_acquire);
}

MemoryStats MemoryManager::getStats() const noexcept {
    return MemoryStats{
        .iron_heap_used = m_ironHeapUsed.load(std::memory_order_relaxed),
        .iron_heap_capacity = IRON_HEAP_SIZE,
        .playground_used = m_playgroundUsed.load(std::memory_order_relaxed),
        .playground_peak = m_playgroundPeak.load(std::memory_order_relaxed),
        .allocation_count = m_allocationCount.load(std::memory_order_relaxed),
        .deallocation_count = m_deallocationCount.load(std::memory_order_relaxed)
    };
}

std::size_t MemoryManager::getIronHeapRemaining() const noexcept {
    return IRON_HEAP_SIZE - m_ironHeapUsed.load(std::memory_order_relaxed);
}

// =============================================================================
// AllocationGuard Implementation
// =============================================================================

AllocationGuard::AllocationGuard(std::size_t bytes, SideID side)
    : m_bytes(bytes), m_side(side) {
    m_ptr = MemoryManager::getInstance().allocate(bytes, side);
}

AllocationGuard::~AllocationGuard() {
    if (m_ptr) {
        MemoryManager::getInstance().deallocate(m_ptr, m_bytes, m_side);
    }
}

AllocationGuard::AllocationGuard(AllocationGuard&& other) noexcept
    : m_ptr(other.m_ptr), m_bytes(other.m_bytes), m_side(other.m_side) {
    other.m_ptr = nullptr;
    other.m_bytes = 0;
}

AllocationGuard& AllocationGuard::operator=(AllocationGuard&& other) noexcept {
    if (this != &other) {
        if (m_ptr) {
            MemoryManager::getInstance().deallocate(m_ptr, m_bytes, m_side);
        }
        m_ptr = other.m_ptr;
        m_bytes = other.m_bytes;
        m_side = other.m_side;
        other.m_ptr = nullptr;
        other.m_bytes = 0;
    }
    return *this;
}

void* AllocationGuard::release() noexcept {
    void* ptr = m_ptr;
    m_ptr = nullptr;
    m_bytes = 0;
    return ptr;
}

} // namespace memory
} // namespace daiw
