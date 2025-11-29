#pragma once

/**
 * DAiW Core Library
 *
 * Real-time safe foundations for audio processing.
 * NO allocations, NO locks, NO exceptions in RT context.
 */

#include "daiw/types.hpp"
#include "daiw/memory_pool.hpp"
#include "daiw/lock_free_queue.hpp"
#include "daiw/ring_buffer.hpp"

namespace daiw {

/// Library version
constexpr const char* VERSION = "1.0.0";

/// Check if we're in a real-time context
/// Set this to true in audio callbacks
inline thread_local bool g_realtime_context = false;

/// RAII guard for marking real-time context
struct RealtimeGuard {
    RealtimeGuard() { g_realtime_context = true; }
    ~RealtimeGuard() { g_realtime_context = false; }

    RealtimeGuard(const RealtimeGuard&) = delete;
    RealtimeGuard& operator=(const RealtimeGuard&) = delete;
};

/// Assert that we're NOT in real-time context (for functions that allocate)
inline void assert_not_realtime() {
#ifdef DAIW_DEBUG
    if (g_realtime_context) {
        // In debug mode, this would trigger a breakpoint
        // In release, it's a no-op for performance
        std::abort();
    }
#endif
}

} // namespace daiw
