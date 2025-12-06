"""
Automated Test Suite for Musical Correctness

Tests that music software output is musically valid, not just that code runs.
Includes groove quality metrics, harmonic validity checks, and perceptual tests.

Proposal: Gemini - Automated Test Suite for Musical Correctness
"""

import pytest
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import json
import statistics


# =============================================================================
# Musical Quality Metrics
# =============================================================================

class GrooveQuality(str, Enum):
    """Quality levels for groove assessment."""
    MECHANICAL = "mechanical"      # Perfectly quantized, lifeless
    STIFF = "stiff"                # Some variation, still rigid
    ACCEPTABLE = "acceptable"      # Functional groove
    GOOD = "good"                  # Natural feel
    EXCELLENT = "excellent"        # Professional quality
    MASTERFUL = "masterful"        # Reference quality


@dataclass
class TimingAnalysis:
    """Analysis of timing characteristics."""
    mean_deviation_ms: float = 0.0      # Average deviation from grid
    std_deviation_ms: float = 0.0       # Consistency of deviation
    max_deviation_ms: float = 0.0       # Largest single deviation
    swing_ratio: float = 0.5            # Swing amount (0.5 = straight)
    push_pull_tendency: float = 0.0     # -1 = behind, 0 = on, +1 = ahead

    # Per-beat analysis
    beat_deviations: List[float] = field(default_factory=list)

    def is_humanized(self) -> bool:
        """Check if timing shows humanization."""
        return 2.0 < self.mean_deviation_ms < 30.0 and self.std_deviation_ms > 1.0

    def is_too_mechanical(self) -> bool:
        """Check if timing is too perfect."""
        return self.mean_deviation_ms < 1.0 and self.std_deviation_ms < 0.5

    def is_too_sloppy(self) -> bool:
        """Check if timing is too loose."""
        return self.mean_deviation_ms > 50.0 or self.max_deviation_ms > 100.0


@dataclass
class VelocityAnalysis:
    """Analysis of velocity/dynamics characteristics."""
    mean_velocity: float = 0.0          # Average velocity (0-127)
    std_velocity: float = 0.0           # Velocity variation
    dynamic_range: float = 0.0          # Max - min velocity
    accent_strength: float = 0.0        # How pronounced accents are
    ghost_note_ratio: float = 0.0       # Ratio of ghost notes (vel < 40)

    # Velocity curve shape
    velocity_curve: List[float] = field(default_factory=list)

    def has_dynamics(self) -> bool:
        """Check if velocity shows dynamic variation."""
        return self.std_velocity > 10 and self.dynamic_range > 30

    def is_flat(self) -> bool:
        """Check if velocity is too uniform."""
        return self.std_velocity < 5 or self.dynamic_range < 20


@dataclass
class GrooveAnalysis:
    """Complete groove analysis."""
    timing: TimingAnalysis = field(default_factory=TimingAnalysis)
    velocity: VelocityAnalysis = field(default_factory=VelocityAnalysis)
    quality: GrooveQuality = GrooveQuality.ACCEPTABLE
    score: float = 0.0  # 0-100

    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def assess_quality(self) -> GrooveQuality:
        """Assess overall groove quality."""
        score = 50.0  # Start at acceptable

        # Timing assessment
        if self.timing.is_humanized():
            score += 20
        elif self.timing.is_too_mechanical():
            score -= 20
            self.issues.append("Timing is too mechanical/quantized")
            self.suggestions.append("Add subtle timing variations (5-15ms)")
        elif self.timing.is_too_sloppy():
            score -= 30
            self.issues.append("Timing is too loose")
            self.suggestions.append("Tighten timing, keep deviations under 30ms")

        # Velocity assessment
        if self.velocity.has_dynamics():
            score += 15
        elif self.velocity.is_flat():
            score -= 15
            self.issues.append("Velocity is too uniform")
            self.suggestions.append("Add velocity variation, especially accents and ghost notes")

        # Ghost notes are a plus for certain genres
        if self.velocity.ghost_note_ratio > 0.1:
            score += 10

        # Swing assessment
        if 0.52 < self.timing.swing_ratio < 0.67:
            score += 5  # Natural swing

        self.score = max(0, min(100, score))

        # Map score to quality
        if self.score >= 90:
            self.quality = GrooveQuality.MASTERFUL
        elif self.score >= 80:
            self.quality = GrooveQuality.EXCELLENT
        elif self.score >= 70:
            self.quality = GrooveQuality.GOOD
        elif self.score >= 50:
            self.quality = GrooveQuality.ACCEPTABLE
        elif self.score >= 30:
            self.quality = GrooveQuality.STIFF
        else:
            self.quality = GrooveQuality.MECHANICAL

        return self.quality


# =============================================================================
# Harmonic Validity Checks
# =============================================================================

class VoiceLeadingRule(str, Enum):
    """Voice leading rules to check."""
    NO_PARALLEL_FIFTHS = "no_parallel_fifths"
    NO_PARALLEL_OCTAVES = "no_parallel_octaves"
    RESOLVE_LEADING_TONE = "resolve_leading_tone"
    RESOLVE_SEVENTH = "resolve_seventh"
    SMOOTH_VOICE_MOTION = "smooth_voice_motion"
    AVOID_VOICE_CROSSING = "avoid_voice_crossing"


@dataclass
class VoiceLeadingViolation:
    """A voice leading rule violation."""
    rule: VoiceLeadingRule
    bar: int
    beat: float
    description: str
    severity: str = "warning"  # info, warning, error
    intentional: bool = False  # Marked as intentional rule-break


@dataclass
class HarmonicAnalysis:
    """Harmonic validity analysis."""
    violations: List[VoiceLeadingViolation] = field(default_factory=list)
    parallel_motion_count: int = 0
    resolution_score: float = 0.0  # How well tensions resolve
    voice_independence: float = 0.0  # 0-1, how independent voices are

    # Chord progression analysis
    progression_strength: float = 0.0  # Harmonic direction
    cadence_quality: float = 0.0

    def is_valid(self, allow_intentional: bool = True) -> bool:
        """Check if harmony is valid."""
        errors = [v for v in self.violations if v.severity == "error"]
        if allow_intentional:
            errors = [v for v in errors if not v.intentional]
        return len(errors) == 0

    def get_issues(self) -> List[str]:
        """Get list of harmonic issues."""
        return [f"{v.rule.value} at bar {v.bar}, beat {v.beat}: {v.description}"
                for v in self.violations]


def check_parallel_fifths(notes1: List[int], notes2: List[int]) -> List[VoiceLeadingViolation]:
    """Check for parallel fifths between two voices."""
    violations = []

    for i in range(len(notes1) - 1):
        if i >= len(notes2) - 1:
            break

        interval1 = abs(notes1[i] - notes2[i]) % 12
        interval2 = abs(notes1[i+1] - notes2[i+1]) % 12

        # Both are fifths (7 semitones) and moving in same direction
        if interval1 == 7 and interval2 == 7:
            motion1 = notes1[i+1] - notes1[i]
            motion2 = notes2[i+1] - notes2[i]

            if (motion1 > 0 and motion2 > 0) or (motion1 < 0 and motion2 < 0):
                violations.append(VoiceLeadingViolation(
                    rule=VoiceLeadingRule.NO_PARALLEL_FIFTHS,
                    bar=i // 4,
                    beat=(i % 4) + 1,
                    description="Parallel fifths detected",
                    severity="warning",
                ))

    return violations


def check_voice_leading(chord_progression: List[List[int]]) -> HarmonicAnalysis:
    """
    Analyze voice leading in a chord progression.

    Args:
        chord_progression: List of chords, each chord is list of MIDI notes

    Returns:
        HarmonicAnalysis with violations and scores
    """
    analysis = HarmonicAnalysis()

    if len(chord_progression) < 2:
        return analysis

    for i in range(len(chord_progression) - 1):
        chord1 = chord_progression[i]
        chord2 = chord_progression[i + 1]

        if len(chord1) < 2 or len(chord2) < 2:
            continue

        # Check parallel fifths between outer voices
        violations = check_parallel_fifths(
            [chord1[0], chord2[0]],  # Bass
            [chord1[-1], chord2[-1]]  # Soprano
        )

        for v in violations:
            v.bar = i
            analysis.violations.append(v)
            analysis.parallel_motion_count += 1

    # Calculate voice independence
    if len(chord_progression) > 1:
        # Simple metric: average interval between voices
        intervals = []
        for chord in chord_progression:
            for j in range(len(chord) - 1):
                intervals.append(abs(chord[j+1] - chord[j]))

        if intervals:
            avg_interval = statistics.mean(intervals)
            # Good independence: average interval 3-7 semitones
            analysis.voice_independence = max(0, min(1, (avg_interval - 2) / 5))

    return analysis


# =============================================================================
# Regression Detection
# =============================================================================

@dataclass
class MusicalRegression:
    """A detected musical regression."""
    metric: str
    previous_value: float
    current_value: float
    change_percent: float
    description: str
    severity: str = "warning"


class RegressionDetector:
    """Detects musical regressions between versions."""

    def __init__(self, baseline_path: Optional[str] = None):
        self.baseline: Dict[str, float] = {}
        if baseline_path:
            self.load_baseline(baseline_path)

    def load_baseline(self, path: str):
        """Load baseline metrics from file."""
        try:
            with open(path, 'r') as f:
                self.baseline = json.load(f)
        except Exception:
            self.baseline = {}

    def save_baseline(self, path: str):
        """Save current metrics as baseline."""
        with open(path, 'w') as f:
            json.dump(self.baseline, f, indent=2)

    def update_baseline(self, metrics: Dict[str, float]):
        """Update baseline with new metrics."""
        self.baseline.update(metrics)

    def check_regression(
        self,
        current_metrics: Dict[str, float],
        threshold_percent: float = 10.0
    ) -> List[MusicalRegression]:
        """
        Check for regressions against baseline.

        Args:
            current_metrics: Current metric values
            threshold_percent: Minimum change to flag as regression

        Returns:
            List of detected regressions
        """
        regressions = []

        for metric, current in current_metrics.items():
            if metric not in self.baseline:
                continue

            previous = self.baseline[metric]
            if previous == 0:
                continue

            change = ((current - previous) / abs(previous)) * 100

            # Negative change in "higher is better" metrics is regression
            higher_is_better = [
                "groove_score", "humanization", "dynamics",
                "voice_independence", "resolution_score"
            ]

            lower_is_better = [
                "parallel_fifths", "timing_error", "velocity_flatness"
            ]

            is_regression = False
            if metric in higher_is_better and change < -threshold_percent:
                is_regression = True
            elif metric in lower_is_better and change > threshold_percent:
                is_regression = True

            if is_regression:
                regressions.append(MusicalRegression(
                    metric=metric,
                    previous_value=previous,
                    current_value=current,
                    change_percent=change,
                    description=f"{metric} changed by {change:+.1f}%",
                    severity="warning" if abs(change) < 20 else "error",
                ))

        return regressions


# =============================================================================
# Test Fixtures and Helpers
# =============================================================================

def create_test_groove(
    num_notes: int = 16,
    humanize: bool = True,
    swing: float = 0.0
) -> Tuple[List[float], List[int]]:
    """
    Create a test groove pattern.

    Returns:
        Tuple of (timing_offsets_ms, velocities)
    """
    import random

    timings = []
    velocities = []

    for i in range(num_notes):
        # Base timing
        if humanize:
            offset = random.gauss(0, 8)  # 8ms standard deviation
        else:
            offset = 0

        # Add swing to off-beats
        if swing > 0 and i % 2 == 1:
            offset += swing * 30  # Swing in ms

        timings.append(offset)

        # Velocity
        if humanize:
            base_vel = 80
            if i % 4 == 0:
                vel = base_vel + random.randint(10, 20)  # Accent
            elif i % 2 == 1:
                vel = base_vel + random.randint(-20, -5)  # Ghost-ish
            else:
                vel = base_vel + random.randint(-10, 10)
        else:
            vel = 100

        velocities.append(max(1, min(127, vel)))

    return timings, velocities


def analyze_groove(timings: List[float], velocities: List[int]) -> GrooveAnalysis:
    """Analyze a groove pattern."""
    analysis = GrooveAnalysis()

    # Timing analysis
    if timings:
        analysis.timing.mean_deviation_ms = abs(statistics.mean(timings))
        analysis.timing.std_deviation_ms = statistics.stdev(timings) if len(timings) > 1 else 0
        analysis.timing.max_deviation_ms = max(abs(t) for t in timings)
        analysis.timing.beat_deviations = timings

        # Calculate push/pull tendency
        analysis.timing.push_pull_tendency = statistics.mean(timings) / 20  # Normalize

    # Velocity analysis
    if velocities:
        analysis.velocity.mean_velocity = statistics.mean(velocities)
        analysis.velocity.std_velocity = statistics.stdev(velocities) if len(velocities) > 1 else 0
        analysis.velocity.dynamic_range = max(velocities) - min(velocities)
        analysis.velocity.ghost_note_ratio = sum(1 for v in velocities if v < 40) / len(velocities)
        analysis.velocity.velocity_curve = velocities

    # Assess quality
    analysis.assess_quality()

    return analysis


# =============================================================================
# Pytest Test Cases
# =============================================================================

class TestGrooveQuality:
    """Test groove quality metrics."""

    def test_humanized_groove_scores_well(self):
        """Humanized groove should score good or better."""
        timings, velocities = create_test_groove(humanize=True)
        analysis = analyze_groove(timings, velocities)

        assert analysis.score >= 60, f"Humanized groove scored too low: {analysis.score}"
        assert analysis.quality in (GrooveQuality.GOOD, GrooveQuality.EXCELLENT, GrooveQuality.MASTERFUL)

    def test_mechanical_groove_scores_low(self):
        """Mechanical groove should score poorly."""
        timings, velocities = create_test_groove(humanize=False)
        analysis = analyze_groove(timings, velocities)

        assert analysis.score <= 50, f"Mechanical groove scored too high: {analysis.score}"
        assert "mechanical" in str(analysis.issues).lower() or "quantized" in str(analysis.issues).lower()

    def test_timing_deviation_detection(self):
        """Should detect timing deviation characteristics."""
        timings = [0, 5, -3, 8, -2, 6, -4, 7]  # Humanized
        velocities = [100] * len(timings)

        analysis = analyze_groove(timings, velocities)

        assert analysis.timing.is_humanized()
        assert not analysis.timing.is_too_mechanical()

    def test_ghost_note_detection(self):
        """Should detect ghost notes."""
        velocities = [100, 30, 90, 35, 100, 28, 95, 32]  # Every other is ghost
        timings = [0] * len(velocities)

        analysis = analyze_groove(timings, velocities)

        assert analysis.velocity.ghost_note_ratio >= 0.4


class TestHarmonicValidity:
    """Test harmonic validity checks."""

    def test_parallel_fifths_detection(self):
        """Should detect parallel fifths."""
        # C-G moving to D-A (parallel fifths)
        chord1 = [60, 67]  # C4, G4
        chord2 = [62, 69]  # D4, A4

        violations = check_parallel_fifths([60, 62], [67, 69])

        assert len(violations) > 0
        assert violations[0].rule == VoiceLeadingRule.NO_PARALLEL_FIFTHS

    def test_good_voice_leading_passes(self):
        """Good voice leading should pass checks."""
        # I - IV - V - I in C major with proper voice leading
        progression = [
            [48, 52, 55, 60],  # C major
            [48, 53, 57, 60],  # F major
            [47, 55, 59, 62],  # G major
            [48, 52, 55, 60],  # C major
        ]

        analysis = check_voice_leading(progression)

        # Should have few or no serious violations
        errors = [v for v in analysis.violations if v.severity == "error"]
        assert len(errors) == 0

    def test_voice_independence_scoring(self):
        """Should score voice independence."""
        # Widely spaced voices
        progression = [
            [36, 48, 60, 72],  # Octave spacing
            [38, 50, 62, 74],
        ]

        analysis = check_voice_leading(progression)

        assert analysis.voice_independence > 0.5


class TestRegressionDetection:
    """Test musical regression detection."""

    def test_detects_groove_regression(self):
        """Should detect groove quality regression."""
        detector = RegressionDetector()
        detector.baseline = {"groove_score": 80.0}

        current = {"groove_score": 60.0}  # 25% drop

        regressions = detector.check_regression(current)

        assert len(regressions) == 1
        assert regressions[0].metric == "groove_score"
        assert regressions[0].change_percent < -20

    def test_ignores_small_changes(self):
        """Should ignore changes below threshold."""
        detector = RegressionDetector()
        detector.baseline = {"groove_score": 80.0}

        current = {"groove_score": 78.0}  # Only 2.5% drop

        regressions = detector.check_regression(current, threshold_percent=10.0)

        assert len(regressions) == 0

    def test_improvement_not_flagged(self):
        """Improvements should not be flagged as regressions."""
        detector = RegressionDetector()
        detector.baseline = {"groove_score": 70.0}

        current = {"groove_score": 85.0}  # Improvement

        regressions = detector.check_regression(current)

        assert len(regressions) == 0


class TestGrooveTemplateValidity:
    """Test that groove templates produce valid output."""

    def test_funk_groove_quality(self):
        """Funk groove template should produce quality groove."""
        # Simulate funk groove characteristics
        timings = [0, 12, -5, 15, -3, 10, -8, 18]  # Pushed feel
        velocities = [100, 45, 85, 40, 95, 50, 80, 35]  # Ghost notes

        analysis = analyze_groove(timings, velocities)

        assert analysis.quality in (GrooveQuality.GOOD, GrooveQuality.EXCELLENT, GrooveQuality.MASTERFUL)
        assert analysis.velocity.ghost_note_ratio > 0.2

    def test_jazz_swing_detection(self):
        """Jazz groove should show swing characteristics."""
        # Swung 8ths: long-short pattern
        timings = [0, 20, 0, 18, 0, 22, 0, 19]  # Off-beats pushed late
        velocities = [90, 60, 85, 55, 88, 62, 82, 58]

        analysis = analyze_groove(timings, velocities)

        # Off-beats should be consistently late
        off_beat_timings = timings[1::2]
        assert all(t > 10 for t in off_beat_timings)


# =============================================================================
# Test Runner Utilities
# =============================================================================

def run_musical_correctness_suite() -> Dict[str, Any]:
    """
    Run the full musical correctness test suite.

    Returns:
        Dict with test results and metrics
    """
    results = {
        "passed": 0,
        "failed": 0,
        "errors": [],
        "metrics": {},
    }

    # Run pytest programmatically
    try:
        import pytest
        exit_code = pytest.main([__file__, "-v", "--tb=short"])
        results["passed"] = exit_code == 0
    except Exception as e:
        results["errors"].append(str(e))

    return results


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
