/**
 * memory.hpp - Lock-free Memory Pool for DAiW
 *
 * This header defines a thread-safe, lock-free memory pool implementation
 * using intrusive linked list and compare-and-swap (CAS) operations.
 *
 * Thread Safety:
 * - All operations are lock-free and safe for concurrent access
 * - Uses atomic operations with proper memory ordering
 * - Implements an intrusive lock-free stack for the free list
 */

#pragma once

#include <atomic>
#include <cstddef>
#include <memory>

namespace daiw {

/**
 * MemoryPool - Lock-free memory pool for fixed-size allocations
 *
 * Implements a lock-free stack using compare-and-swap operations.
 * The free list is intrusive - each free block stores a pointer to
 * the next free block in its first bytes.
 *
 * Requirements:
 * - blockSize must be >= sizeof(void*) for the intrusive next pointer
 * - All blocks are contiguous in memory for fast contains() check
 */
class MemoryPool {
public:
    /**
     * Construct a memory pool with fixed-size blocks.
     * @param blockSize Size of each block in bytes (must be >= sizeof(void*))
     * @param numBlocks Number of blocks in the pool
     */
    MemoryPool(size_t blockSize, size_t numBlocks);

    /**
     * Destructor - releases the underlying memory.
     */
    ~MemoryPool();

    // Non-copyable, non-movable
    MemoryPool(const MemoryPool&) = delete;
    MemoryPool& operator=(const MemoryPool&) = delete;
    MemoryPool(MemoryPool&&) = delete;
    MemoryPool& operator=(MemoryPool&&) = delete;

    /**
     * Allocate a block from the pool (lock-free).
     * @return Pointer to allocated block, or nullptr if pool exhausted
     *
     * Thread-safe: Uses CAS loop to pop from lock-free stack.
     */
    void* allocate() noexcept;

    /**
     * Return a block to the pool (lock-free).
     * @param ptr Pointer previously returned by allocate()
     *
     * Thread-safe: Uses CAS loop to push onto lock-free stack.
     * Note: ptr must point to a block from this pool (checked via contains()).
     */
    void deallocate(void* ptr) noexcept;

    /**
     * Check if a pointer belongs to this pool.
     * @param ptr Pointer to check
     * @return true if ptr is within the pool's memory region
     */
    bool contains(void* ptr) const noexcept;

    /**
     * Get the number of free blocks (approximate).
     * @return Approximate count of available blocks
     *
     * Note: This value may be stale in concurrent scenarios.
     */
    size_t freeCount() const noexcept;

    /**
     * Get the total number of blocks in the pool.
     * @return Total block count
     */
    size_t totalBlocks() const noexcept { return numBlocks_; }

    /**
     * Get the size of each block.
     * @return Block size in bytes
     */
    size_t blockSize() const noexcept { return blockSize_; }

private:
    size_t blockSize_;                      ///< Size of each block
    size_t numBlocks_;                      ///< Total number of blocks
    std::unique_ptr<char[]> memory_;        ///< Underlying memory buffer
    std::atomic<void*> freeListHead_;       ///< Head of lock-free free list stack
    std::atomic<size_t> freeCount_;         ///< Approximate count of free blocks
};

} // namespace daiw
