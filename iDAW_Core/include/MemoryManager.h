/**
 * MemoryManager.h - Dual Heap Memory Architecture for iDAW
 * 
 * iDAW (Intelligent Digital Audio Workstation) - Dual-Engine Audio Application
 * Framework: JUCE 8 (C++) + Python 3.11 (Embedded)
 * 
 * ARCHITECTURAL OVERVIEW:
 * Two distinct memory/logic states ("Side A" and "Side B") connected by a 3D "Flip" transition.
 * 
 * Side A ("Work State"): 
 *   - Uses std::pmr::monotonic_buffer_resource
 *   - Pre-allocates 4GB at startup
 *   - NO deallocation allowed
 *   - Thread-safe for Real-time Audio
 * 
 * Side B ("Dream State"):
 *   - Uses std::pmr::synchronized_pool_resource
 *   - Dynamic allocation allowed
 *   - Used for AI generation and UI strings
 * 
 * CONSTRAINT: Side B logic must NEVER lock Side A audio threads.
 */

#pragma once

#include <memory_resource>
#include <memory>
#include <array>
#include <atomic>
#include <mutex>
#include <string>
#include <vector>

namespace iDAW {

// Forward declarations
class SideAAllocator;
class SideBAllocator;

/**
 * Configuration constants for the Dual Heap
 */
struct MemoryConfig {
    static constexpr size_t SIDE_A_SIZE = 4ULL * 1024 * 1024 * 1024;  // 4GB pre-allocated
    static constexpr size_t SIDE_B_INITIAL_SIZE = 512 * 1024 * 1024;  // 512MB initial
    static constexpr size_t SIDE_B_MAX_SIZE = 2ULL * 1024 * 1024 * 1024;  // 2GB max
    static constexpr size_t RING_BUFFER_SIZE = 64 * 1024;  // 64KB ring buffer for MIDI
};

/**
 * Side A Allocator - Work State (Real-time Audio)
 * 
 * Uses monotonic_buffer_resource for lock-free, deterministic allocation.
 * Pre-allocates 4GB at startup. NO deallocation during runtime.
 * Thread-safe for real-time audio processing.
 */
class SideAAllocator {
public:
    SideAAllocator();
    ~SideAAllocator();

    // Non-copyable, non-movable (singleton pattern)
    SideAAllocator(const SideAAllocator&) = delete;
    SideAAllocator& operator=(const SideAAllocator&) = delete;
    SideAAllocator(SideAAllocator&&) = delete;
    SideAAllocator& operator=(SideAAllocator&&) = delete;

    /**
     * Allocate memory from Side A pool.
     * @param bytes Number of bytes to allocate
     * @param alignment Memory alignment (default: alignof(max_align_t))
     * @return Pointer to allocated memory, or nullptr if pool exhausted
     * 
     * NOTE: This memory is NEVER freed until shutdown.
     */
    void* allocate(size_t bytes, size_t alignment = alignof(std::max_align_t));

    /**
     * Get the polymorphic memory resource for STL containers.
     * Use this with std::pmr:: containers for automatic allocation.
     */
    std::pmr::memory_resource* getResource() noexcept;

    /**
     * Get current memory usage statistics.
     */
    size_t getBytesUsed() const noexcept;
    size_t getBytesRemaining() const noexcept;
    float getUsagePercent() const noexcept;

    /**
     * Check if allocation would succeed without blocking.
     * Essential for real-time safety checks.
     */
    bool canAllocate(size_t bytes) const noexcept;

private:
    std::unique_ptr<std::byte[]> m_buffer;
    std::unique_ptr<std::pmr::monotonic_buffer_resource> m_resource;
    std::atomic<size_t> m_bytesUsed{0};
};

/**
 * Side B Allocator - Dream State (AI Generation)
 * 
 * Uses synchronized_pool_resource for dynamic allocation.
 * Supports allocation AND deallocation.
 * Thread-safe but may block - NEVER use from audio thread.
 */
class SideBAllocator {
public:
    SideBAllocator();
    ~SideBAllocator();

    // Non-copyable, non-movable
    SideBAllocator(const SideBAllocator&) = delete;
    SideBAllocator& operator=(const SideBAllocator&) = delete;
    SideBAllocator(SideBAllocator&&) = delete;
    SideBAllocator& operator=(SideBAllocator&&) = delete;

    /**
     * Allocate memory from Side B pool.
     * @param bytes Number of bytes to allocate
     * @param alignment Memory alignment
     * @return Pointer to allocated memory
     * @throws std::bad_alloc if allocation fails
     * 
     * WARNING: May block. Never call from real-time audio thread.
     */
    void* allocate(size_t bytes, size_t alignment = alignof(std::max_align_t));

    /**
     * Deallocate memory back to Side B pool.
     * @param ptr Pointer previously returned by allocate()
     * @param bytes Size of the allocation
     * @param alignment Alignment of the allocation
     */
    void deallocate(void* ptr, size_t bytes, size_t alignment = alignof(std::max_align_t));

    /**
     * Get the polymorphic memory resource for STL containers.
     */
    std::pmr::memory_resource* getResource() noexcept;

    /**
     * Get memory usage statistics.
     */
    size_t getApproximateBytesUsed() const noexcept;

private:
    std::unique_ptr<std::pmr::synchronized_pool_resource> m_resource;
    std::atomic<size_t> m_bytesAllocated{0};
    mutable std::mutex m_statsMutex;
};

/**
 * Lock-free Ring Buffer for Side A <-> Side B communication
 * 
 * Used to pass MIDI data from Python (Side B) to Audio Engine (Side A)
 * without blocking the audio thread.
 */
template<typename T, size_t Capacity>
class LockFreeRingBuffer {
public:
    LockFreeRingBuffer() : m_head(0), m_tail(0) {}

    /**
     * Try to push an item (Producer - Side B)
     * @return true if successful, false if buffer full
     */
    bool tryPush(const T& item) {
        size_t head = m_head.load(std::memory_order_relaxed);
        size_t next = (head + 1) % Capacity;
        
        if (next == m_tail.load(std::memory_order_acquire)) {
            return false;  // Buffer full
        }
        
        m_buffer[head] = item;
        m_head.store(next, std::memory_order_release);
        return true;
    }

    /**
     * Try to pop an item (Consumer - Side A Audio Thread)
     * @return true if successful, false if buffer empty
     */
    bool tryPop(T& item) {
        size_t tail = m_tail.load(std::memory_order_relaxed);
        
        if (tail == m_head.load(std::memory_order_acquire)) {
            return false;  // Buffer empty
        }
        
        item = m_buffer[tail];
        m_tail.store((tail + 1) % Capacity, std::memory_order_release);
        return true;
    }

    /**
     * Check if buffer is empty (approximate, for diagnostics)
     */
    bool isEmpty() const noexcept {
        return m_head.load(std::memory_order_relaxed) == 
               m_tail.load(std::memory_order_relaxed);
    }

    /**
     * Get approximate size (for diagnostics only)
     */
    size_t approximateSize() const noexcept {
        size_t head = m_head.load(std::memory_order_relaxed);
        size_t tail = m_tail.load(std::memory_order_relaxed);
        return (head >= tail) ? (head - tail) : (Capacity - tail + head);
    }

private:
    std::array<T, Capacity> m_buffer;
    std::atomic<size_t> m_head;
    std::atomic<size_t> m_tail;
};

/**
 * MIDI Event structure for Ring Buffer transfer
 */
struct MidiEvent {
    uint8_t status;      // MIDI status byte
    uint8_t data1;       // First data byte (note/CC number)
    uint8_t data2;       // Second data byte (velocity/value)
    uint32_t timestamp;  // Sample offset within buffer
};

/**
 * MemoryManager - Central coordinator for Dual Heap architecture
 * 
 * Singleton that provides access to both memory pools and the
 * lock-free ring buffer for Side A <-> Side B communication.
 */
class MemoryManager {
public:
    /**
     * Get the singleton instance.
     */
    static MemoryManager& getInstance();

    // Delete copy/move
    MemoryManager(const MemoryManager&) = delete;
    MemoryManager& operator=(const MemoryManager&) = delete;

    /**
     * Get Side A allocator (Work State - Real-time safe)
     */
    SideAAllocator& getSideA() noexcept { return m_sideA; }

    /**
     * Get Side B allocator (Dream State - AI/UI)
     */
    SideBAllocator& getSideB() noexcept { return m_sideB; }

    /**
     * Get the MIDI ring buffer for Side B -> Side A transfer
     */
    LockFreeRingBuffer<MidiEvent, 4096>& getMidiBuffer() noexcept { 
        return m_midiBuffer; 
    }

    /**
     * Check which "side" the current thread is on.
     * Returns true for Side A (audio thread), false for Side B.
     */
    bool isAudioThread() const noexcept;

    /**
     * Register the current thread as the audio thread.
     * Call once from the audio thread initialization.
     */
    void registerAudioThread();

    /**
     * Safety check: Assert we're not on the audio thread.
     * Use before any blocking operation.
     */
    void assertNotAudioThread() const;

private:
    MemoryManager();
    ~MemoryManager();

    SideAAllocator m_sideA;
    SideBAllocator m_sideB;
    LockFreeRingBuffer<MidiEvent, 4096> m_midiBuffer;
    std::atomic<std::thread::id> m_audioThreadId;
};

/**
 * RAII helper for Side B allocations
 * Automatically deallocates when going out of scope
 */
template<typename T>
class SideBPtr {
public:
    SideBPtr() : m_ptr(nullptr), m_size(0) {}
    
    explicit SideBPtr(size_t count) 
        : m_size(count * sizeof(T)) 
    {
        void* raw = MemoryManager::getInstance().getSideB().allocate(m_size, alignof(T));
        m_ptr = static_cast<T*>(raw);
        // Default construct elements
        for (size_t i = 0; i < count; ++i) {
            new (&m_ptr[i]) T();
        }
        m_count = count;
    }
    
    ~SideBPtr() {
        if (m_ptr) {
            // Destruct elements
            for (size_t i = 0; i < m_count; ++i) {
                m_ptr[i].~T();
            }
            MemoryManager::getInstance().getSideB().deallocate(m_ptr, m_size, alignof(T));
        }
    }
    
    // Move only
    SideBPtr(SideBPtr&& other) noexcept 
        : m_ptr(other.m_ptr), m_size(other.m_size), m_count(other.m_count) {
        other.m_ptr = nullptr;
        other.m_size = 0;
        other.m_count = 0;
    }
    
    SideBPtr& operator=(SideBPtr&& other) noexcept {
        if (this != &other) {
            std::swap(m_ptr, other.m_ptr);
            std::swap(m_size, other.m_size);
            std::swap(m_count, other.m_count);
        }
        return *this;
    }
    
    T* get() noexcept { return m_ptr; }
    const T* get() const noexcept { return m_ptr; }
    T& operator[](size_t i) { return m_ptr[i]; }
    const T& operator[](size_t i) const { return m_ptr[i]; }
    
private:
    T* m_ptr;
    size_t m_size;
    size_t m_count;
};

} // namespace iDAW
