#pragma once
/**
 * MemoryManager.h - Dual Allocator Memory Architecture
 *
 * DAiW Phase 1: The Foundation
 *
 * AI Roles:
 * - AI-1 (Orchestrator): Routes memory requests based on SideID
 * - AI-2 (Logic): Handles allocation math, never touches audio buffers directly
 * - AI-4 (Data/Validation): Validates allocations, prevents memory leaks
 *
 * CRITICAL: No use of standard malloc/new for audio objects.
 * All audio buffers must go through MemoryManager.
 *
 * Architecture:
 * - Side A (Iron Heap): Monotonic buffer for audio processing
 *   - Pre-allocated 4GB at startup
 *   - NO DEALLOCATION during runtime (prevents fragmentation)
 *   - Reset only between sessions
 *
 * - Side B (Playground): Thread-safe pool for dynamic allocations
 *   - Expandable, used for creative/experimental features
 *   - Can grow/shrink as needed
 */

#include <memory_resource>
#include <mutex>
#include <atomic>
#include <cstdint>
#include <stdexcept>
#include <array>

namespace daiw {
namespace memory {

/**
 * Side ID enumeration - determines which allocator to use
 */
enum class SideID : uint8_t {
    IronHeap = 0,     // Side A: Monotonic, no-free, 4GB preallocated
    Playground = 1     // Side B: Thread-safe pool, expandable
};

/**
 * Memory statistics for monitoring
 */
struct MemoryStats {
    std::size_t iron_heap_used{0};
    std::size_t iron_heap_capacity{0};
    std::size_t playground_used{0};
    std::size_t playground_peak{0};
    std::size_t allocation_count{0};
    std::size_t deallocation_count{0};  // Should be 0 for Iron Heap
};

/**
 * MemoryManager - Singleton dual-allocator system
 *
 * Thread Safety:
 * - Side A (Iron Heap): Thread-safe via monotonic design (no sync needed)
 * - Side B (Playground): Thread-safe via synchronized_pool_resource
 *
 * Usage:
 *   auto& mm = MemoryManager::getInstance();
 *   void* ptr = mm.allocate(1024, SideID::IronHeap);
 *   // For Playground: mm.deallocate(ptr, 1024, SideID::Playground);
 */
class MemoryManager {
public:
    // Singleton access
    static MemoryManager& getInstance();

    // Delete copy/move
    MemoryManager(const MemoryManager&) = delete;
    MemoryManager& operator=(const MemoryManager&) = delete;
    MemoryManager(MemoryManager&&) = delete;
    MemoryManager& operator=(MemoryManager&&) = delete;

    /**
     * Allocate memory from specified side
     *
     * @param bytes Size in bytes to allocate
     * @param side Which allocator to use
     * @param alignment Memory alignment (default: max_align_t)
     * @return Pointer to allocated memory
     * @throws std::bad_alloc on failure
     */
    void* allocate(std::size_t bytes, SideID side,
                   std::size_t alignment = alignof(std::max_align_t));

    /**
     * Deallocate memory (only valid for Playground)
     *
     * For Iron Heap, this is a no-op to prevent fragmentation.
     * Memory is only reclaimed during reset().
     *
     * @param ptr Pointer to deallocate
     * @param bytes Size that was allocated
     * @param side Which allocator (Playground only)
     */
    void deallocate(void* ptr, std::size_t bytes, SideID side);

    /**
     * Get the memory resource for a specific side
     *
     * @param side Which side's resource to return
     * @return Polymorphic memory resource pointer
     */
    std::pmr::memory_resource* getResource(SideID side);

    /**
     * Reset the Iron Heap (reclaims all memory)
     *
     * WARNING: This invalidates ALL pointers allocated from Iron Heap!
     * Only call between sessions when no audio is being processed.
     */
    void resetIronHeap();

    /**
     * Check if initialized
     */
    [[nodiscard]] bool isInitialized() const noexcept;

    /**
     * Get current memory statistics
     */
    [[nodiscard]] MemoryStats getStats() const noexcept;

    /**
     * Get remaining capacity in Iron Heap
     */
    [[nodiscard]] std::size_t getIronHeapRemaining() const noexcept;

    // Configuration constants - can be overridden via compile-time defines
#ifdef DAIW_IRON_HEAP_SIZE
    static constexpr std::size_t IRON_HEAP_SIZE = DAIW_IRON_HEAP_SIZE;
#else
    static constexpr std::size_t IRON_HEAP_SIZE = 4ULL * 1024 * 1024 * 1024;  // 4GB default
#endif

#ifdef DAIW_PLAYGROUND_INITIAL_SIZE
    static constexpr std::size_t PLAYGROUND_INITIAL_SIZE = DAIW_PLAYGROUND_INITIAL_SIZE;
#else
    static constexpr std::size_t PLAYGROUND_INITIAL_SIZE = 256 * 1024 * 1024; // 256MB default
#endif

private:
    MemoryManager();
    ~MemoryManager();

    void initialize();

    // Iron Heap (Side A) - monotonic, no-free
    std::unique_ptr<std::byte[]> m_ironHeapBuffer;
    std::unique_ptr<std::pmr::monotonic_buffer_resource> m_ironHeap;
    std::atomic<std::size_t> m_ironHeapUsed{0};

    // Playground (Side B) - synchronized pool
    std::unique_ptr<std::pmr::synchronized_pool_resource> m_playground;
    std::atomic<std::size_t> m_playgroundUsed{0};
    std::atomic<std::size_t> m_playgroundPeak{0};

    // Statistics
    std::atomic<std::size_t> m_allocationCount{0};
    std::atomic<std::size_t> m_deallocationCount{0};

    // State
    std::atomic<bool> m_initialized{false};
    mutable std::mutex m_initMutex;
};

/**
 * RAII-style allocation guard for automatic cleanup
 *
 * Usage:
 *   {
 *     AllocationGuard guard(1024, SideID::Playground);
 *     void* ptr = guard.get();
 *     // Use ptr...
 *   } // Automatically deallocated
 */
class AllocationGuard {
public:
    AllocationGuard(std::size_t bytes, SideID side);
    ~AllocationGuard();

    // Delete copy
    AllocationGuard(const AllocationGuard&) = delete;
    AllocationGuard& operator=(const AllocationGuard&) = delete;

    // Allow move
    AllocationGuard(AllocationGuard&& other) noexcept;
    AllocationGuard& operator=(AllocationGuard&& other) noexcept;

    [[nodiscard]] void* get() const noexcept { return m_ptr; }
    [[nodiscard]] void* release() noexcept;

private:
    void* m_ptr{nullptr};
    std::size_t m_bytes{0};
    SideID m_side{SideID::IronHeap};
};

} // namespace memory
} // namespace daiw
