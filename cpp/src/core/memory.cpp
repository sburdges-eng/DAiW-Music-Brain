/**
 * @file memory.cpp
 * @brief Implementation of memory management utilities
 */

#include "daiw/memory.hpp"
#include <cassert>
#include <algorithm>

namespace daiw {

// =============================================================================
// MemoryPool Implementation
// =============================================================================

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
    }

    return nullptr;  // Pool exhausted
}

void MemoryPool::deallocate(void* ptr) noexcept {
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
