/**
 * PythonBridge.cpp - C++/Python Integration implementation
 *
 * Phase 1: The Foundation
 */

#include "PythonBridge.h"

namespace daiw {
namespace bridge {

// =============================================================================
// PythonBridge Implementation
// =============================================================================

PythonBridge::PythonBridge() {
    // Ensure MemoryManager is initialized
    memory::MemoryManager::getInstance();
}

PythonBridge::~PythonBridge() {
    // Clean up any remaining buffers
    m_buffers.clear();
}

PythonBridge& PythonBridge::getInstance() {
    static PythonBridge instance;
    return instance;
}

std::map<std::string, size_t> PythonBridge::getMemoryStats() const {
    auto stats = memory::MemoryManager::getInstance().getStats();

    return {
        {"iron_heap_used", stats.iron_heap_used},
        {"iron_heap_capacity", stats.iron_heap_capacity},
        {"playground_used", stats.playground_used},
        {"playground_peak", stats.playground_peak},
        {"allocation_count", stats.allocation_count},
        {"deallocation_count", stats.deallocation_count}
    };
}

size_t PythonBridge::getIronHeapRemaining() const {
    return memory::MemoryManager::getInstance().getIronHeapRemaining();
}

size_t PythonBridge::getPlaygroundUsed() const {
    return memory::MemoryManager::getInstance().getStats().playground_used;
}

int PythonBridge::allocateBuffer(size_t size, const std::string& side) {
    memory::SideID sideId = memory::SideID::IronHeap;

    if (side == "playground" || side == "Playground" || side == "B") {
        sideId = memory::SideID::Playground;
    }

    auto buffer = std::make_unique<memory::AudioBuffer>(size, sideId);
    int handleId = m_nextHandleId++;

    m_buffers[handleId] = std::move(buffer);

    return handleId;
}

void PythonBridge::deallocateBuffer(int handleId) {
    auto it = m_buffers.find(handleId);
    if (it != m_buffers.end()) {
        m_buffers.erase(it);
    }
}

bool PythonBridge::bufferExists(int handleId) const {
    return m_buffers.find(handleId) != m_buffers.end();
}

std::string PythonBridge::getVersion() {
    return "1.0.0";
}

// =============================================================================
// Free Functions Implementation
// =============================================================================

std::map<std::string, size_t> get_memory_stats() {
    return PythonBridge::getInstance().getMemoryStats();
}

int allocate_buffer(size_t size, const std::string& side) {
    return PythonBridge::getInstance().allocateBuffer(size, side);
}

void deallocate_buffer(int handle_id) {
    PythonBridge::getInstance().deallocateBuffer(handle_id);
}

size_t get_iron_heap_remaining() {
    return PythonBridge::getInstance().getIronHeapRemaining();
}

std::string get_version() {
    return PythonBridge::getVersion();
}

bool is_dream_state() {
    return PythonBridge::getInstance().isDreamState();
}

void set_dream_state(bool dream) {
    PythonBridge::getInstance().setDreamState(dream);
}

} // namespace bridge
} // namespace daiw
