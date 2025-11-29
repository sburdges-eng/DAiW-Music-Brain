#pragma once
/**
 * PythonBridge.h - C++/Python Integration via pybind11
 *
 * DAiW Phase 1: The Foundation
 *
 * This module enables Python code to call into C++ DAiW functions
 * and vice versa. It's used by the AI agents (AI-2: Logic/Computation)
 * to perform calculations without touching creative output.
 *
 * Usage from Python:
 *   import daiw_logic
 *   stats = daiw_logic.get_memory_stats()
 *   buffer = daiw_logic.allocate_buffer(1024, "iron_heap")
 */

#include "../Memory/MemoryManager.h"
#include "../Memory/DAiW_Buffer.h"
#include <string>
#include <unordered_map>

namespace daiw {
namespace bridge {

/**
 * PythonBridge - Interface between Python and C++ DAiW Core
 *
 * Provides:
 * - Memory management access
 * - Buffer operations
 * - Parameter queries
 */
class PythonBridge {
public:
    PythonBridge();
    ~PythonBridge();

    // Singleton access (for pybind11)
    static PythonBridge& getInstance();

    // Memory operations
    [[nodiscard]] std::map<std::string, size_t> getMemoryStats() const;
    [[nodiscard]] size_t getIronHeapRemaining() const;
    [[nodiscard]] size_t getPlaygroundUsed() const;

    // Buffer operations (returns handle ID)
    [[nodiscard]] int allocateBuffer(size_t size, const std::string& side);
    void deallocateBuffer(int handleId);
    [[nodiscard]] bool bufferExists(int handleId) const;

    // View state
    [[nodiscard]] bool isDreamState() const { return m_isDreamState; }
    void setDreamState(bool dream) { m_isDreamState = dream; }

    // Version info
    [[nodiscard]] static std::string getVersion();

private:
    bool m_isDreamState{false};

    // Buffer handle management
    std::unordered_map<int, std::unique_ptr<memory::AudioBuffer>> m_buffers;
    int m_nextHandleId{1};
};

// =============================================================================
// Free functions for pybind11 module
// =============================================================================

/**
 * Get memory statistics from MemoryManager
 *
 * @return Dictionary with memory stats
 */
std::map<std::string, size_t> get_memory_stats();

/**
 * Allocate a buffer
 *
 * @param size Number of float samples
 * @param side "iron_heap" or "playground"
 * @return Buffer handle ID
 */
int allocate_buffer(size_t size, const std::string& side);

/**
 * Deallocate a buffer
 *
 * @param handle_id Buffer handle to deallocate
 */
void deallocate_buffer(int handle_id);

/**
 * Get remaining Iron Heap capacity
 */
size_t get_iron_heap_remaining();

/**
 * Get DAiW Core version
 */
std::string get_version();

/**
 * Check if in dream state
 */
bool is_dream_state();

/**
 * Set dream state
 */
void set_dream_state(bool dream);

} // namespace bridge
} // namespace daiw
