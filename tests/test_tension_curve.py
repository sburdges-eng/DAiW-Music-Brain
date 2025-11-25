# tests/test_tension_curve.py
"""
Tests for the Tension Curve Generator.

Covers: climb, standard, constant presets and edge cases.

Run with: pytest tests/test_tension_curve.py -v
"""

import pytest
import numpy as np

from music_brain.structure.tension import generate_tension_curve


class TestTensionCurveBasics:
    """Basic tension curve generation tests."""

    def test_empty_bars_returns_empty_array(self):
        """Zero bars should return empty array."""
        result = generate_tension_curve(0, "standard")
        assert len(result) == 0
        assert isinstance(result, np.ndarray)

    def test_negative_bars_returns_empty_array(self):
        """Negative bars should return empty array."""
        result = generate_tension_curve(-5, "climb")
        assert len(result) == 0

    def test_returns_correct_length(self):
        """Output array should match requested bar count."""
        for bars in [8, 16, 32, 64]:
            result = generate_tension_curve(bars, "standard")
            assert len(result) == bars

    def test_returns_numpy_array(self):
        """Should return numpy array of floats."""
        result = generate_tension_curve(16, "climb")
        assert isinstance(result, np.ndarray)
        assert result.dtype == float


class TestClimbPreset:
    """Tests for the 'climb' structure type."""

    def test_climb_starts_low(self):
        """Climb preset should start at lower tension."""
        result = generate_tension_curve(32, "climb")
        assert result[0] < result[-1]

    def test_climb_ends_high(self):
        """Climb preset should end at higher tension."""
        result = generate_tension_curve(32, "climb")
        assert result[-1] > 1.0

    def test_climb_is_monotonic(self):
        """Climb should be monotonically increasing."""
        result = generate_tension_curve(32, "climb")
        for i in range(1, len(result)):
            assert result[i] >= result[i - 1]

    def test_climb_range(self):
        """Climb should span from ~0.6 to ~1.4."""
        result = generate_tension_curve(32, "climb")
        assert 0.5 <= result[0] <= 0.7
        assert 1.3 <= result[-1] <= 1.5


class TestStandardPreset:
    """Tests for the 'standard' structure type (verse/chorus/bridge)."""

    def test_standard_has_variation(self):
        """Standard should not be flat."""
        result = generate_tension_curve(32, "standard")
        assert np.std(result) > 0.01

    def test_standard_within_bounds(self):
        """All values should be within reasonable range."""
        result = generate_tension_curve(32, "standard")
        assert np.all(result >= 0.5)
        assert np.all(result <= 1.5)


class TestConstantPreset:
    """Tests for the 'constant' structure type."""

    def test_constant_is_flat(self):
        """Constant should return all 1.0 values."""
        result = generate_tension_curve(16, "constant")
        assert np.allclose(result, 1.0)

    def test_constant_no_variation(self):
        """Constant should have zero variance."""
        result = generate_tension_curve(32, "constant")
        assert np.std(result) == 0.0


class TestUnknownPreset:
    """Tests for unknown structure types."""

    def test_unknown_defaults_to_constant(self):
        """Unknown type should default to constant (all 1.0)."""
        result = generate_tension_curve(16, "unknown_type")
        assert np.allclose(result, 1.0)

    def test_empty_string_defaults_to_constant(self):
        """Empty string should default to constant."""
        result = generate_tension_curve(16, "")
        assert np.allclose(result, 1.0)


class TestEdgeCases:
    """Edge case tests."""

    def test_single_bar(self):
        """Single bar should return single value array."""
        for preset in ["climb", "standard", "constant"]:
            result = generate_tension_curve(1, preset)
            assert len(result) == 1
            assert result[0] > 0

    def test_large_bar_count(self):
        """Should handle large bar counts."""
        result = generate_tension_curve(256, "climb")
        assert len(result) == 256
        assert result[0] < result[-1]
