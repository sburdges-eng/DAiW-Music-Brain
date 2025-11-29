/**
 * PythonModule.cpp - pybind11 module definition
 *
 * DAiW Phase 1: The Foundation
 *
 * This file defines the Python module interface for daiw_logic.
 *
 * Usage in Python:
 *   import daiw_logic
 *
 *   # Memory operations
 *   stats = daiw_logic.get_memory_stats()
 *   print(f"Iron Heap: {stats['iron_heap_used']} / {stats['iron_heap_capacity']}")
 *
 *   # Buffer operations
 *   handle = daiw_logic.allocate_buffer(1024, "iron_heap")
 *   daiw_logic.deallocate_buffer(handle)
 *
 *   # State
 *   daiw_logic.set_dream_state(True)
 *   print(f"Dream state: {daiw_logic.is_dream_state()}")
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "PythonBridge.h"

namespace py = pybind11;

PYBIND11_MODULE(daiw_logic, m) {
    m.doc() = R"pbdoc(
        DAiW Logic Module - C++ Audio Processing Bridge
        ================================================

        This module provides access to DAiW's C++ audio processing
        infrastructure from Python. Used by AI-2 (Logic/Computation)
        for calculations without touching creative output.

        Memory Architecture:
        - Iron Heap (Side A): Monotonic allocator for audio processing
        - Playground (Side B): Thread-safe pool for creative features

        Functions:
        - get_memory_stats(): Get memory usage statistics
        - allocate_buffer(): Allocate audio buffer
        - deallocate_buffer(): Free a buffer
        - get_iron_heap_remaining(): Check Iron Heap capacity
        - is_dream_state(): Check current state
        - set_dream_state(): Toggle state
        - get_version(): Get DAiW Core version
    )pbdoc";

    // Memory statistics
    m.def("get_memory_stats",
          &daiw::bridge::get_memory_stats,
          R"pbdoc(
              Get current memory statistics.

              Returns:
                  dict: Memory statistics including:
                      - iron_heap_used: Bytes used in Iron Heap
                      - iron_heap_capacity: Total Iron Heap size
                      - playground_used: Bytes used in Playground
                      - playground_peak: Peak Playground usage
                      - allocation_count: Total allocations
                      - deallocation_count: Total deallocations
          )pbdoc");

    // Iron heap remaining
    m.def("get_iron_heap_remaining",
          &daiw::bridge::get_iron_heap_remaining,
          R"pbdoc(
              Get remaining capacity in Iron Heap.

              Returns:
                  int: Bytes remaining in Iron Heap
          )pbdoc");

    // Buffer allocation
    m.def("allocate_buffer",
          &daiw::bridge::allocate_buffer,
          py::arg("size"),
          py::arg("side") = "iron_heap",
          R"pbdoc(
              Allocate an audio buffer.

              Args:
                  size: Number of float samples
                  side: "iron_heap" or "playground"

              Returns:
                  int: Buffer handle ID

              Note:
                  Iron Heap buffers are NOT freed until session reset.
                  Playground buffers can be freed with deallocate_buffer().
          )pbdoc");

    // Buffer deallocation
    m.def("deallocate_buffer",
          &daiw::bridge::deallocate_buffer,
          py::arg("handle_id"),
          R"pbdoc(
              Deallocate a buffer.

              Args:
                  handle_id: Buffer handle from allocate_buffer()

              Note:
                  For Iron Heap buffers, this is a no-op.
          )pbdoc");

    // Dream state
    m.def("is_dream_state",
          &daiw::bridge::is_dream_state,
          R"pbdoc(
              Check if currently in Dream state.

              Returns:
                  bool: True if Dream state active
          )pbdoc");

    m.def("set_dream_state",
          &daiw::bridge::set_dream_state,
          py::arg("dream"),
          R"pbdoc(
              Set the Dream state.

              Args:
                  dream: True for Dream state, False for Work state
          )pbdoc");

    // Version
    m.def("get_version",
          &daiw::bridge::get_version,
          R"pbdoc(
              Get DAiW Core version.

              Returns:
                  str: Version string
          )pbdoc");

    // Module version
#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "1.0.0";
#endif
}
