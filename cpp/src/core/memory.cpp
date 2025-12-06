/**
 * @file memory.cpp
 * @brief Implementation of memory management utilities
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
#include <algorithm>

namespace daiw {

// =============================================================================
// MemoryPool Implementation
// =============================================================================

#include <cstring>

namespace daiw {

MemoryPool::MemoryPool(size_t blockSize, size_t numBlocks)
    : blockSize_(blockSize)
    , numBlocks_(numBlocks)
    , freeCount_(numBlocks)
{
    // Allocate contiguous memory for all blocks
    memory_ = std::make_unique<std::byte[]>(blockSize_ * numBlocks_);

    // Build free list
    freeList_.reserve(numBlocks_);
    for (size_t i = 0; i < numBlocks_; ++i) {
        freeList_.push_back(memory_.get() + (i * blockSize_));
    }
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
    size_t expected = freeCount_.load(std::memory_order_acquire);

    while (expected > 0) {
        if (freeCount_.compare_exchange_weak(expected, expected - 1,
                                              std::memory_order_acq_rel)) {
            // Successfully decremented, pop from list
            void* ptr = freeList_[expected - 1];
            return ptr;
        }
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

    size_t count = freeCount_.load(std::memory_order_acquire);
    freeList_[count] = ptr;
    freeCount_.fetch_add(1, std::memory_order_release);
}

bool MemoryPool::contains(void* ptr) const noexcept {
    auto* bytePtr = static_cast<std::byte*>(ptr);
    auto* start = memory_.get();
    auto* end = start + (blockSize_ * numBlocks_);
    return bytePtr >= start && bytePtr < end;
}

size_t MemoryPool::availableBlocks() const noexcept {
    return freeCount_.load(std::memory_order_acquire);
}

// =============================================================================
// LockFreeQueue Implementation
// =============================================================================

template<typename T>
LockFreeQueue<T>::LockFreeQueue() {
    // Create sentinel node
    auto* sentinel = new QueueNode<T>(T{});
    head_.store(sentinel, std::memory_order_relaxed);
    tail_ = sentinel;
}

template<typename T>
LockFreeQueue<T>::~LockFreeQueue() {
    // Drain the queue
    T item;
    while (pop(item)) {}

    // Delete sentinel
    delete tail_;
}

template<typename T>
void LockFreeQueue<T>::push(const T& item) {
    auto* node = new QueueNode<T>(item);

    // Atomically swap the head
    QueueNode<T>* prevHead = head_.exchange(node, std::memory_order_acq_rel);
    prevHead->next.store(node, std::memory_order_release);
}

template<typename T>
bool LockFreeQueue<T>::pop(T& item) {
    QueueNode<T>* next = tail_->next.load(std::memory_order_acquire);

    if (next == nullptr) {
        return false;  // Empty
    }

    item = next->data;

    delete tail_;
    tail_ = next;
    return true;
}

template<typename T>
bool LockFreeQueue<T>::empty() const noexcept {
    return tail_->next.load(std::memory_order_acquire) == nullptr;
}

// Explicit instantiations for common types
template class LockFreeQueue<int>;
template class LockFreeQueue<float>;
template class LockFreeQueue<NoteEvent>;

}  // namespace daiw
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
