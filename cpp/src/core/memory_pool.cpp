/**
 * DAiW Memory Pool Implementation
 *
 * Lock-free memory pool for real-time safe allocations.
 */

#include "daiw/memory_pool.hpp"
#include "daiw/core.hpp"

namespace daiw {

// Template instantiations for common types
// This ensures the templates are compiled into the library

// Forward declare common types we'll use
struct MidiEvent;
struct GroovePoint;
struct AudioFrame;

// The actual template implementations are header-only for performance,
// but we can add any non-template helper functions here.

namespace memory {

// Memory statistics tracking (optional, for debugging)
static std::atomic<size_t> g_total_allocations{0};
static std::atomic<size_t> g_total_deallocations{0};
static std::atomic<size_t> g_peak_usage{0};

void reset_stats() {
    g_total_allocations.store(0, std::memory_order_relaxed);
    g_total_deallocations.store(0, std::memory_order_relaxed);
    g_peak_usage.store(0, std::memory_order_relaxed);
}

size_t get_total_allocations() {
    return g_total_allocations.load(std::memory_order_relaxed);
}

size_t get_total_deallocations() {
    return g_total_deallocations.load(std::memory_order_relaxed);
}

size_t get_peak_usage() {
    return g_peak_usage.load(std::memory_order_relaxed);
}

void record_allocation() {
    g_total_allocations.fetch_add(1, std::memory_order_relaxed);

    size_t current = g_total_allocations.load(std::memory_order_relaxed) -
                     g_total_deallocations.load(std::memory_order_relaxed);

    size_t peak = g_peak_usage.load(std::memory_order_relaxed);
    while (current > peak) {
        if (g_peak_usage.compare_exchange_weak(peak, current, std::memory_order_relaxed)) {
            break;
        }
    }
}

void record_deallocation() {
    g_total_deallocations.fetch_add(1, std::memory_order_relaxed);
}

} // namespace memory
} // namespace daiw
