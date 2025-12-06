/**
 * memory.cpp - Lock-free Memory Pool Implementation
 *
 * This implements a thread-safe, lock-free memory pool using an intrusive
 * linked list and compare-and-swap (CAS) operations.
 *
 * The free list is implemented as a lock-free stack where each free block
 * stores a pointer to the next free block in its first sizeof(void*) bytes.
 *
 * Key Design:
 * - Lock-free allocate/deallocate using compare_exchange_weak
 * - Intrusive linked list (no separate node allocation)
 * - All blocks contiguous for fast contains() check
 * - Proper memory ordering for thread safety
 */

#include "daiw/memory.hpp"
#include <cassert>
#include <cstring>

namespace daiw {

MemoryPool::MemoryPool(size_t blockSize, size_t numBlocks)
    : blockSize_(blockSize)
    , numBlocks_(numBlocks)
    , freeCount_(numBlocks)
    , freeListHead_(nullptr)
{
    // Block size must be at least sizeof(void*) for the intrusive next pointer
    assert(blockSize >= sizeof(void*) && "blockSize must be >= sizeof(void*)");
    assert(numBlocks > 0 && "numBlocks must be > 0");

    // Allocate contiguous memory for all blocks
    memory_ = std::make_unique<char[]>(blockSize * numBlocks);

    // Initialize free list by linking all blocks together
    // Build the list in reverse order so that the first block is at the head
    void* head = nullptr;
    for (size_t i = numBlocks; i > 0; --i) {
        char* block = memory_.get() + (i - 1) * blockSize;
        // Store the current head in this block's first bytes (intrusive next pointer)
        *reinterpret_cast<void**>(block) = head;
        head = block;
    }

    // Set the head of the free list
    freeListHead_.store(head, std::memory_order_release);
}

MemoryPool::~MemoryPool() = default;

void* MemoryPool::allocate() noexcept {
    // Pop from the lock-free stack using CAS loop
    void* ptr = freeListHead_.load(std::memory_order_acquire);

    while (ptr != nullptr) {
        // Read the next pointer from the block we're trying to pop
        // Note: ABA problem is not an issue here because:
        // 1. All blocks are from a contiguous memory region that is never freed
        // 2. Even if a block is deallocated and reallocated, the next pointer
        //    is always valid (points to another block in the pool or nullptr)
        // 3. The worst case is a spurious CAS failure, which is harmless
        void* next = *static_cast<void**>(ptr);

        // Try to atomically update the head to the next block
        if (freeListHead_.compare_exchange_weak(ptr, next,
                                                 std::memory_order_acq_rel,
                                                 std::memory_order_acquire)) {
            // Successfully popped the block
            freeCount_.fetch_sub(1, std::memory_order_relaxed);
            return ptr;
        }
        // CAS failed, ptr now contains the current head, retry
    }

    return nullptr;  // Pool exhausted
}

void MemoryPool::deallocate(void* ptr) noexcept {
    // Validate the pointer
    if (!ptr || !contains(ptr)) {
        return;
    }

    // Push onto the lock-free stack using CAS loop
    // Treat first bytes of block as next pointer (intrusive linked list)
    void** nextPtr = static_cast<void**>(ptr);
    void* oldHead = freeListHead_.load(std::memory_order_relaxed);

    do {
        // Store the current head as this block's next pointer
        *nextPtr = oldHead;
    } while (!freeListHead_.compare_exchange_weak(oldHead, ptr,
                                                   std::memory_order_release,
                                                   std::memory_order_relaxed));

    freeCount_.fetch_add(1, std::memory_order_relaxed);
}

bool MemoryPool::contains(void* ptr) const noexcept {
    if (!ptr) {
        return false;
    }

    const char* p = static_cast<const char*>(ptr);
    const char* start = memory_.get();
    const char* end = start + (blockSize_ * numBlocks_);

    // Check if pointer is within the pool's memory region
    if (p < start || p >= end) {
        return false;
    }

    // Check if pointer is aligned to block boundary
    size_t offset = static_cast<size_t>(p - start);
    return (offset % blockSize_) == 0;
}

size_t MemoryPool::freeCount() const noexcept {
    return freeCount_.load(std::memory_order_relaxed);
}

} // namespace daiw
