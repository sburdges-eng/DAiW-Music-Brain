"""
Performance Benchmark Dashboard

Comprehensive performance tracking for DAiW as it transitions to C++.
Tracks latency, memory, CPU, and provides comparison views.

Proposal: Gemini - Performance Benchmark Dashboard
"""

from .dashboard import (
    BenchmarkDashboard,
    BenchmarkResult,
    BenchmarkSuite,
    LatencyMetrics,
    MemoryMetrics,
    CPUMetrics,
    run_benchmark,
    compare_versions,
    get_dashboard,
)

__all__ = [
    "BenchmarkDashboard",
    "BenchmarkResult",
    "BenchmarkSuite",
    "LatencyMetrics",
    "MemoryMetrics",
    "CPUMetrics",
    "run_benchmark",
    "compare_versions",
    "get_dashboard",
]
