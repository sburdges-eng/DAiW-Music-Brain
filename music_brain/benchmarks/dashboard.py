"""
Performance Benchmark Dashboard

Tracks performance metrics across versions and implementations.
"""

import time
import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum
import threading


class MetricType(str, Enum):
    """Types of metrics tracked."""
    LATENCY = "latency"
    MEMORY = "memory"
    CPU = "cpu"
    THROUGHPUT = "throughput"


@dataclass
class LatencyMetrics:
    """Latency measurements."""
    mean_ms: float = 0.0
    median_ms: float = 0.0
    p95_ms: float = 0.0           # 95th percentile
    p99_ms: float = 0.0           # 99th percentile
    min_ms: float = 0.0
    max_ms: float = 0.0
    std_ms: float = 0.0
    jitter_ms: float = 0.0        # Variation between consecutive measurements

    samples: List[float] = field(default_factory=list)

    @classmethod
    def from_samples(cls, samples: List[float]) -> "LatencyMetrics":
        """Calculate metrics from samples."""
        if not samples:
            return cls()

        sorted_samples = sorted(samples)
        n = len(sorted_samples)

        # Calculate jitter (variation between consecutive samples)
        jitter = 0.0
        if n > 1:
            diffs = [abs(samples[i] - samples[i-1]) for i in range(1, n)]
            jitter = statistics.mean(diffs)

        return cls(
            mean_ms=statistics.mean(samples),
            median_ms=statistics.median(samples),
            p95_ms=sorted_samples[int(n * 0.95)] if n > 20 else max(samples),
            p99_ms=sorted_samples[int(n * 0.99)] if n > 100 else max(samples),
            min_ms=min(samples),
            max_ms=max(samples),
            std_ms=statistics.stdev(samples) if n > 1 else 0,
            jitter_ms=jitter,
            samples=samples,
        )

    def to_dict(self) -> Dict[str, float]:
        return {
            "mean_ms": self.mean_ms,
            "median_ms": self.median_ms,
            "p95_ms": self.p95_ms,
            "p99_ms": self.p99_ms,
            "min_ms": self.min_ms,
            "max_ms": self.max_ms,
            "std_ms": self.std_ms,
            "jitter_ms": self.jitter_ms,
            "sample_count": len(self.samples),
        }


@dataclass
class MemoryMetrics:
    """Memory usage measurements."""
    peak_mb: float = 0.0
    mean_mb: float = 0.0
    min_mb: float = 0.0

    allocations_count: int = 0
    deallocations_count: int = 0

    # Real-time specific
    rt_allocations: int = 0       # Allocations in RT context (should be 0)
    pool_utilization: float = 0.0  # Memory pool usage percentage

    samples: List[float] = field(default_factory=list)

    @classmethod
    def from_samples(cls, samples: List[float]) -> "MemoryMetrics":
        if not samples:
            return cls()

        return cls(
            peak_mb=max(samples),
            mean_mb=statistics.mean(samples),
            min_mb=min(samples),
            samples=samples,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "peak_mb": self.peak_mb,
            "mean_mb": self.mean_mb,
            "min_mb": self.min_mb,
            "allocations_count": self.allocations_count,
            "rt_allocations": self.rt_allocations,
            "pool_utilization": self.pool_utilization,
        }


@dataclass
class CPUMetrics:
    """CPU usage measurements."""
    mean_percent: float = 0.0
    peak_percent: float = 0.0

    # Per-core breakdown
    per_core: List[float] = field(default_factory=list)

    # SIMD utilization
    simd_utilization: float = 0.0  # Percentage of vectorized operations

    # Multi-core scaling
    scaling_efficiency: float = 0.0  # 1.0 = perfect linear scaling

    samples: List[float] = field(default_factory=list)

    @classmethod
    def from_samples(cls, samples: List[float]) -> "CPUMetrics":
        if not samples:
            return cls()

        return cls(
            mean_percent=statistics.mean(samples),
            peak_percent=max(samples),
            samples=samples,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mean_percent": self.mean_percent,
            "peak_percent": self.peak_percent,
            "simd_utilization": self.simd_utilization,
            "scaling_efficiency": self.scaling_efficiency,
        }


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    name: str
    category: str
    implementation: str  # "python" or "cpp"
    version: str

    latency: LatencyMetrics = field(default_factory=LatencyMetrics)
    memory: MemoryMetrics = field(default_factory=MemoryMetrics)
    cpu: CPUMetrics = field(default_factory=CPUMetrics)

    throughput: float = 0.0       # Operations per second
    timestamp: str = ""
    duration_seconds: float = 0.0

    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "implementation": self.implementation,
            "version": self.version,
            "latency": self.latency.to_dict(),
            "memory": self.memory.to_dict(),
            "cpu": self.cpu.to_dict(),
            "throughput": self.throughput,
            "timestamp": self.timestamp,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BenchmarkResult":
        result = cls(
            name=data["name"],
            category=data.get("category", ""),
            implementation=data.get("implementation", "python"),
            version=data.get("version", ""),
            throughput=data.get("throughput", 0),
            timestamp=data.get("timestamp", ""),
            duration_seconds=data.get("duration_seconds", 0),
            metadata=data.get("metadata", {}),
        )

        if "latency" in data:
            result.latency = LatencyMetrics(**{
                k: v for k, v in data["latency"].items()
                if k != "sample_count"
            })

        return result


@dataclass
class BenchmarkComparison:
    """Comparison between two benchmark results."""
    baseline: BenchmarkResult
    current: BenchmarkResult

    latency_change_percent: float = 0.0
    memory_change_percent: float = 0.0
    throughput_change_percent: float = 0.0

    is_regression: bool = False
    improvements: List[str] = field(default_factory=list)
    regressions: List[str] = field(default_factory=list)

    def analyze(self):
        """Analyze the comparison."""
        # Latency (lower is better)
        if self.baseline.latency.mean_ms > 0:
            self.latency_change_percent = (
                (self.current.latency.mean_ms - self.baseline.latency.mean_ms)
                / self.baseline.latency.mean_ms * 100
            )
            if self.latency_change_percent < -5:
                self.improvements.append(f"Latency improved by {-self.latency_change_percent:.1f}%")
            elif self.latency_change_percent > 10:
                self.regressions.append(f"Latency regressed by {self.latency_change_percent:.1f}%")
                self.is_regression = True

        # Memory (lower is better)
        if self.baseline.memory.peak_mb > 0:
            self.memory_change_percent = (
                (self.current.memory.peak_mb - self.baseline.memory.peak_mb)
                / self.baseline.memory.peak_mb * 100
            )
            if self.memory_change_percent < -5:
                self.improvements.append(f"Memory improved by {-self.memory_change_percent:.1f}%")
            elif self.memory_change_percent > 20:
                self.regressions.append(f"Memory regressed by {self.memory_change_percent:.1f}%")
                self.is_regression = True

        # Throughput (higher is better)
        if self.baseline.throughput > 0:
            self.throughput_change_percent = (
                (self.current.throughput - self.baseline.throughput)
                / self.baseline.throughput * 100
            )
            if self.throughput_change_percent > 5:
                self.improvements.append(f"Throughput improved by {self.throughput_change_percent:.1f}%")
            elif self.throughput_change_percent < -10:
                self.regressions.append(f"Throughput regressed by {-self.throughput_change_percent:.1f}%")
                self.is_regression = True


class BenchmarkSuite:
    """A collection of benchmarks to run."""

    def __init__(self, name: str):
        self.name = name
        self.benchmarks: Dict[str, Callable] = {}
        self.results: List[BenchmarkResult] = []

    def add(self, name: str, category: str = "general"):
        """Decorator to add a benchmark function."""
        def decorator(func: Callable):
            self.benchmarks[name] = {
                "func": func,
                "category": category,
            }
            return func
        return decorator

    def run(
        self,
        iterations: int = 100,
        warmup: int = 10,
        implementation: str = "python",
        version: str = "0.0.0",
    ) -> List[BenchmarkResult]:
        """Run all benchmarks in the suite."""
        self.results = []

        for name, benchmark in self.benchmarks.items():
            func = benchmark["func"]
            category = benchmark["category"]

            # Warmup
            for _ in range(warmup):
                func()

            # Measure
            latencies = []
            start_time = time.time()

            for _ in range(iterations):
                t0 = time.perf_counter()
                func()
                t1 = time.perf_counter()
                latencies.append((t1 - t0) * 1000)  # Convert to ms

            duration = time.time() - start_time

            result = BenchmarkResult(
                name=name,
                category=category,
                implementation=implementation,
                version=version,
                latency=LatencyMetrics.from_samples(latencies),
                throughput=iterations / duration,
                duration_seconds=duration,
                metadata={"iterations": iterations, "warmup": warmup},
            )

            self.results.append(result)

        return self.results


class BenchmarkDashboard:
    """
    Central dashboard for performance tracking.

    Features:
    - Historical tracking
    - Regression detection
    - Comparison views
    - Export for CI/CD
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else Path.home() / ".daiw_benchmarks"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.history: List[BenchmarkResult] = []
        self.baselines: Dict[str, BenchmarkResult] = {}

        self._load_history()

    def _load_history(self):
        """Load historical results."""
        history_file = self.storage_path / "history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    self.history = [BenchmarkResult.from_dict(r) for r in data.get("results", [])]
                    self.baselines = {
                        k: BenchmarkResult.from_dict(v)
                        for k, v in data.get("baselines", {}).items()
                    }
            except Exception:
                pass

    def _save_history(self):
        """Save historical results."""
        history_file = self.storage_path / "history.json"
        with open(history_file, 'w') as f:
            json.dump({
                "results": [r.to_dict() for r in self.history[-1000:]],  # Keep last 1000
                "baselines": {k: v.to_dict() for k, v in self.baselines.items()},
            }, f, indent=2)

    def record(self, result: BenchmarkResult):
        """Record a benchmark result."""
        self.history.append(result)
        self._save_history()

    def record_all(self, results: List[BenchmarkResult]):
        """Record multiple results."""
        self.history.extend(results)
        self._save_history()

    def set_baseline(self, name: str, result: BenchmarkResult):
        """Set a baseline for comparison."""
        self.baselines[name] = result
        self._save_history()

    def compare_to_baseline(self, result: BenchmarkResult) -> Optional[BenchmarkComparison]:
        """Compare a result to its baseline."""
        baseline = self.baselines.get(result.name)
        if not baseline:
            return None

        comparison = BenchmarkComparison(baseline=baseline, current=result)
        comparison.analyze()
        return comparison

    def get_history(
        self,
        name: Optional[str] = None,
        implementation: Optional[str] = None,
        limit: int = 100,
    ) -> List[BenchmarkResult]:
        """Get historical results with optional filters."""
        results = self.history

        if name:
            results = [r for r in results if r.name == name]
        if implementation:
            results = [r for r in results if r.implementation == implementation]

        return results[-limit:]

    def get_trend(self, name: str, metric: str = "latency") -> List[Tuple[str, float]]:
        """Get trend data for a benchmark."""
        history = self.get_history(name=name)

        trend = []
        for result in history:
            if metric == "latency":
                value = result.latency.mean_ms
            elif metric == "memory":
                value = result.memory.peak_mb
            elif metric == "throughput":
                value = result.throughput
            else:
                continue

            trend.append((result.timestamp, value))

        return trend

    def format_dashboard(self) -> str:
        """Format dashboard for display."""
        lines = [
            "=" * 70,
            "PERFORMANCE BENCHMARK DASHBOARD",
            "=" * 70,
            "",
        ]

        # Latest results by category
        latest_by_name: Dict[str, BenchmarkResult] = {}
        for result in reversed(self.history):
            if result.name not in latest_by_name:
                latest_by_name[result.name] = result

        if not latest_by_name:
            lines.append("No benchmark data available.")
            lines.append("Run benchmarks with: daiw benchmark run")
            return "\n".join(lines)

        # Group by category
        by_category: Dict[str, List[BenchmarkResult]] = {}
        for result in latest_by_name.values():
            cat = result.category or "general"
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(result)

        for category, results in sorted(by_category.items()):
            lines.append(f"[{category.upper()}]")
            lines.append("-" * 50)

            for result in results:
                impl_tag = f"[{result.implementation}]"
                lines.append(f"  {result.name} {impl_tag}")
                lines.append(f"    Latency: {result.latency.mean_ms:.2f}ms (p99: {result.latency.p99_ms:.2f}ms)")
                lines.append(f"    Throughput: {result.throughput:.0f} ops/sec")

                # Compare to baseline
                comparison = self.compare_to_baseline(result)
                if comparison:
                    if comparison.is_regression:
                        lines.append(f"    ⚠️  REGRESSION: {', '.join(comparison.regressions)}")
                    elif comparison.improvements:
                        lines.append(f"    ✓ Improved: {', '.join(comparison.improvements)}")

                lines.append("")

        # Python vs C++ comparison
        python_results = [r for r in latest_by_name.values() if r.implementation == "python"]
        cpp_results = [r for r in latest_by_name.values() if r.implementation == "cpp"]

        if python_results and cpp_results:
            lines.extend([
                "",
                "PYTHON vs C++ COMPARISON",
                "-" * 50,
            ])

            for py_result in python_results:
                cpp_result = next(
                    (r for r in cpp_results if r.name == py_result.name),
                    None
                )
                if cpp_result:
                    speedup = py_result.latency.mean_ms / cpp_result.latency.mean_ms
                    lines.append(f"  {py_result.name}: C++ is {speedup:.1f}x faster")

        return "\n".join(lines)

    def export_for_ci(self, output_path: str):
        """Export results in CI-friendly format."""
        latest_by_name = {}
        for result in reversed(self.history):
            if result.name not in latest_by_name:
                latest_by_name[result.name] = result

        ci_data = {
            "timestamp": datetime.now().isoformat(),
            "benchmarks": {},
            "regressions": [],
        }

        for name, result in latest_by_name.items():
            ci_data["benchmarks"][name] = {
                "latency_ms": result.latency.mean_ms,
                "throughput": result.throughput,
                "implementation": result.implementation,
            }

            comparison = self.compare_to_baseline(result)
            if comparison and comparison.is_regression:
                ci_data["regressions"].append({
                    "name": name,
                    "issues": comparison.regressions,
                })

        with open(output_path, 'w') as f:
            json.dump(ci_data, f, indent=2)


# =============================================================================
# Convenience Functions
# =============================================================================

_dashboard: Optional[BenchmarkDashboard] = None


def get_dashboard() -> BenchmarkDashboard:
    """Get the global benchmark dashboard."""
    global _dashboard
    if _dashboard is None:
        _dashboard = BenchmarkDashboard()
    return _dashboard


def run_benchmark(
    func: Callable,
    name: str,
    iterations: int = 100,
    category: str = "general",
    implementation: str = "python",
    version: str = "0.0.0",
) -> BenchmarkResult:
    """Run a single benchmark and record it."""
    # Warmup
    for _ in range(10):
        func()

    # Measure
    latencies = []
    start_time = time.time()

    for _ in range(iterations):
        t0 = time.perf_counter()
        func()
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)

    duration = time.time() - start_time

    result = BenchmarkResult(
        name=name,
        category=category,
        implementation=implementation,
        version=version,
        latency=LatencyMetrics.from_samples(latencies),
        throughput=iterations / duration,
        duration_seconds=duration,
    )

    # Record in dashboard
    get_dashboard().record(result)

    return result


def compare_versions(
    name: str,
    python_func: Callable,
    cpp_func: Optional[Callable] = None,
    iterations: int = 100,
) -> Dict[str, Any]:
    """Compare Python and C++ implementations."""
    results = {}

    # Python benchmark
    py_result = run_benchmark(
        python_func,
        name=name,
        iterations=iterations,
        implementation="python",
    )
    results["python"] = py_result

    # C++ benchmark (if available)
    if cpp_func:
        cpp_result = run_benchmark(
            cpp_func,
            name=name,
            iterations=iterations,
            implementation="cpp",
        )
        results["cpp"] = cpp_result

        # Calculate speedup
        speedup = py_result.latency.mean_ms / cpp_result.latency.mean_ms
        results["speedup"] = speedup

    return results


# =============================================================================
# Built-in Benchmarks
# =============================================================================

def create_daiw_benchmark_suite() -> BenchmarkSuite:
    """Create the standard DAiW benchmark suite."""
    suite = BenchmarkSuite("daiw")

    @suite.add("groove_extract", category="groove")
    def benchmark_groove_extract():
        """Benchmark groove extraction."""
        # Simulate groove extraction
        data = list(range(1000))
        result = [x * 1.1 for x in data]
        return result

    @suite.add("chord_parse", category="harmony")
    def benchmark_chord_parse():
        """Benchmark chord parsing."""
        chords = ["Cmaj7", "Dm7", "G7", "Cmaj7"]
        # Simulate parsing
        for chord in chords:
            parts = list(chord)
        return parts

    @suite.add("midi_process", category="midi")
    def benchmark_midi_process():
        """Benchmark MIDI processing."""
        # Simulate MIDI event processing
        events = [(i, 60 + (i % 12), 100) for i in range(100)]
        processed = [(t + 10, n, v * 0.9) for t, n, v in events]
        return processed

    return suite
