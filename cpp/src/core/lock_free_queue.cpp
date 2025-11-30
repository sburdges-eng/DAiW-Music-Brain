/**
 * DAiW Lock-Free Queue Implementation
 *
 * SPSC and MPSC queue implementations for real-time audio.
 */

#include "daiw/lock_free_queue.hpp"
#include "daiw/core.hpp"

namespace daiw {

// Template implementations are header-only for performance.
// This file provides any non-template utilities.

namespace queue {

// Queue statistics for debugging
static std::atomic<size_t> g_total_pushes{0};
static std::atomic<size_t> g_total_pops{0};
static std::atomic<size_t> g_failed_pushes{0};
static std::atomic<size_t> g_failed_pops{0};

void reset_stats() {
    g_total_pushes.store(0, std::memory_order_relaxed);
    g_total_pops.store(0, std::memory_order_relaxed);
    g_failed_pushes.store(0, std::memory_order_relaxed);
    g_failed_pops.store(0, std::memory_order_relaxed);
}

void record_push(bool success) {
    if (success) {
        g_total_pushes.fetch_add(1, std::memory_order_relaxed);
    } else {
        g_failed_pushes.fetch_add(1, std::memory_order_relaxed);
    }
}

void record_pop(bool success) {
    if (success) {
        g_total_pops.fetch_add(1, std::memory_order_relaxed);
    } else {
        g_failed_pops.fetch_add(1, std::memory_order_relaxed);
    }
}

size_t get_total_pushes() {
    return g_total_pushes.load(std::memory_order_relaxed);
}

size_t get_total_pops() {
    return g_total_pops.load(std::memory_order_relaxed);
}

size_t get_failed_pushes() {
    return g_failed_pushes.load(std::memory_order_relaxed);
}

size_t get_failed_pops() {
    return g_failed_pops.load(std::memory_order_relaxed);
}

} // namespace queue
} // namespace daiw
