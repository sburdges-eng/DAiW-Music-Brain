/**
 * MemoryManager.cpp - Implementation of Dual Heap Memory Architecture
 */

#include "MemoryManager.h"
#include <cassert>
#include <stdexcept>
#include <thread>

namespace iDAW {

// ============================================================================
// SideAAllocator Implementation
// ============================================================================

SideAAllocator::SideAAllocator() {
    // Pre-allocate 4GB buffer
    m_buffer = std::make_unique<std::byte[]>(MemoryConfig::SIDE_A_SIZE);
    
    // Create monotonic buffer resource - no upstream, no deallocation
    m_resource = std::make_unique<std::pmr::monotonic_buffer_resource>(
        m_buffer.get(),
        MemoryConfig::SIDE_A_SIZE,
        std::pmr::null_memory_resource()  // Fail if exhausted, don't go upstream
    );
}

SideAAllocator::~SideAAllocator() = default;

void* SideAAllocator::allocate(size_t bytes, size_t alignment) {
    // Check if we can allocate without blocking
    size_t currentUsed = m_bytesUsed.load(std::memory_order_relaxed);
    if (currentUsed + bytes > MemoryConfig::SIDE_A_SIZE) {
        return nullptr;  // Pool exhausted
    }
    
    try {
        void* ptr = m_resource->allocate(bytes, alignment);
        m_bytesUsed.fetch_add(bytes, std::memory_order_relaxed);
        return ptr;
    } catch (const std::bad_alloc&) {
        return nullptr;
    }
}

std::pmr::memory_resource* SideAAllocator::getResource() noexcept {
    return m_resource.get();
}

size_t SideAAllocator::getBytesUsed() const noexcept {
    return m_bytesUsed.load(std::memory_order_relaxed);
}

size_t SideAAllocator::getBytesRemaining() const noexcept {
    return MemoryConfig::SIDE_A_SIZE - getBytesUsed();
}

float SideAAllocator::getUsagePercent() const noexcept {
    return static_cast<float>(getBytesUsed()) / MemoryConfig::SIDE_A_SIZE * 100.0f;
}

bool SideAAllocator::canAllocate(size_t bytes) const noexcept {
    return getBytesRemaining() >= bytes;
}

// ============================================================================
// SideBAllocator Implementation
// ============================================================================

SideBAllocator::SideBAllocator() {
    // Create synchronized pool resource with default upstream (new/delete)
    std::pmr::pool_options options;
    options.max_blocks_per_chunk = 1024;
    options.largest_required_pool_block = 1024 * 1024;  // 1MB max block
    
    m_resource = std::make_unique<std::pmr::synchronized_pool_resource>(
        options,
        std::pmr::new_delete_resource()
    );
}

SideBAllocator::~SideBAllocator() = default;

void* SideBAllocator::allocate(size_t bytes, size_t alignment) {
    // This may block - never call from audio thread
    void* ptr = m_resource->allocate(bytes, alignment);
    m_bytesAllocated.fetch_add(bytes, std::memory_order_relaxed);
    return ptr;
}

void SideBAllocator::deallocate(void* ptr, size_t bytes, size_t alignment) {
    m_resource->deallocate(ptr, bytes, alignment);
    m_bytesAllocated.fetch_sub(bytes, std::memory_order_relaxed);
}

std::pmr::memory_resource* SideBAllocator::getResource() noexcept {
    return m_resource.get();
}

size_t SideBAllocator::getApproximateBytesUsed() const noexcept {
    return m_bytesAllocated.load(std::memory_order_relaxed);
}

// ============================================================================
// MemoryManager Implementation
// ============================================================================

MemoryManager& MemoryManager::getInstance() {
    static MemoryManager instance;
    return instance;
}

MemoryManager::MemoryManager() 
    : m_audioThreadId(std::thread::id{}) {
    // Allocators are constructed by their default constructors
}

MemoryManager::~MemoryManager() = default;

bool MemoryManager::isAudioThread() const noexcept {
    return std::this_thread::get_id() == m_audioThreadId.load(std::memory_order_relaxed);
}

void MemoryManager::registerAudioThread() {
    m_audioThreadId.store(std::this_thread::get_id(), std::memory_order_relaxed);
}

void MemoryManager::assertNotAudioThread() const {
    assert(!isAudioThread() && "Blocking operation called from audio thread!");
}

} // namespace iDAW
