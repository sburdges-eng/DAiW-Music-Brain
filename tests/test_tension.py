"""
Tests for Tension Curve modules.

Covers both tension.py (numpy-based) and tension_curve.py (list-based).

Run with: pytest tests/test_tension.py -v
"""

import pytest
import numpy as np

from music_brain.structure.tension import generate_tension_curve
from music_brain.structure.tension_curve import (
    get_tension_curve,
    list_tension_curves,
    apply_tension_curve,
    apply_section_markers,
    generate_curve_for_bars,
    TENSION_CURVES,
)


# ==============================================================================
# NUMPY TENSION CURVE TESTS (tension.py)
# ==============================================================================

class TestGenerateTensionCurve:
    """Tests for the numpy-based generate_tension_curve function."""

    def test_returns_numpy_array(self):
        """Should return a numpy array."""
        result = generate_tension_curve(16)
        assert isinstance(result, np.ndarray)

    def test_correct_length(self):
        """Should return array of correct length."""
        for bars in [8, 16, 32, 64, 128]:
            result = generate_tension_curve(bars)
            assert len(result) == bars

    def test_zero_bars_returns_empty(self):
        """Zero bars should return empty array."""
        result = generate_tension_curve(0)
        assert len(result) == 0

    def test_negative_bars_returns_empty(self):
        """Negative bars should return empty array."""
        result = generate_tension_curve(-5)
        assert len(result) == 0

    def test_climb_structure(self):
        """Climb structure should increase monotonically."""
        result = generate_tension_curve(32, "climb")

        # First value should be around 0.6
        assert result[0] < 0.7

        # Last value should be around 1.4
        assert result[-1] > 1.3

        # Should be monotonically increasing
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1]

    def test_standard_structure_shape(self):
        """Standard structure should have verse/chorus shape."""
        result = generate_tension_curve(64, "standard")

        # Verse 1 (bars 0-15) should be lower
        verse1_avg = np.mean(result[0:16])
        assert verse1_avg < 0.8

        # Chorus 1 (bars 16-31) should be higher
        if len(result) > 16:
            chorus1_avg = np.mean(result[16:32])
            assert chorus1_avg > 1.0

        # Bridge (bars 48-59) should be highest
        if len(result) > 48:
            bridge_avg = np.mean(result[48:60])
            assert bridge_avg > 1.2

    def test_constant_structure(self):
        """Constant structure should be flat."""
        result = generate_tension_curve(32, "constant")

        # All values should be 1.0
        assert np.allclose(result, 1.0)

    def test_unknown_structure_defaults_to_flat(self):
        """Unknown structure type should default to flat."""
        result = generate_tension_curve(16, "unknown_type")
        assert np.allclose(result, 1.0)

    def test_values_in_range(self):
        """Values should be in reasonable range (0.3 to 1.6)."""
        for structure in ["climb", "standard", "constant"]:
            result = generate_tension_curve(64, structure)
            assert np.all(result >= 0.3)
            assert np.all(result <= 1.6)


# ==============================================================================
# LIST-BASED TENSION CURVE TESTS (tension_curve.py)
# ==============================================================================

class TestTensionCurvePresets:
    """Tests for tension curve presets."""

    def test_list_curves_returns_list(self):
        """Should return list of available curves."""
        curves = list_tension_curves()
        assert isinstance(curves, list)
        assert len(curves) > 0

    def test_all_preset_curves_exist(self):
        """All documented curves should be accessible."""
        expected = ["verse_chorus", "slow_build", "front_loaded", "wave",
                    "catharsis", "static", "descent", "spiral"]

        for name in expected:
            assert name in TENSION_CURVES

    def test_get_curve_returns_copy(self):
        """get_tension_curve should return a copy, not the original."""
        curve1 = get_tension_curve("verse_chorus")
        curve2 = get_tension_curve("verse_chorus")

        # Modify one
        curve1[0] = 999

        # Other should be unchanged
        assert curve2[0] != 999

    def test_get_curve_unknown_raises(self):
        """Unknown curve name should raise ValueError."""
        with pytest.raises(ValueError):
            get_tension_curve("nonexistent_curve")


class TestApplyTensionCurve:
    """Tests for applying tension curves to events."""

    @pytest.fixture
    def sample_events(self):
        """Create sample note events."""
        return [
            {"start_tick": 0, "velocity": 80},
            {"start_tick": 480, "velocity": 80},
            {"start_tick": 960, "velocity": 80},
            {"start_tick": 1440, "velocity": 80},
            {"start_tick": 1920, "velocity": 80},
        ]

    def test_empty_events_returns_empty(self):
        """Empty events list should return empty."""
        result = apply_tension_curve([], bar_ticks=1920, multipliers=[1.0])
        assert result == []

    def test_empty_multipliers_returns_copy(self, sample_events):
        """Empty multipliers should return unchanged copy."""
        result = apply_tension_curve(sample_events, bar_ticks=1920, multipliers=[])

        assert len(result) == len(sample_events)
        for orig, new in zip(sample_events, result):
            assert new["velocity"] == orig["velocity"]

    def test_applies_velocity_scaling(self, sample_events):
        """Should scale velocities by multiplier."""
        # All events in bar 0, multiplier is 0.5
        result = apply_tension_curve(
            sample_events,
            bar_ticks=10000,  # All events in first bar
            multipliers=[0.5],
        )

        for new in result:
            assert new["velocity"] == 40  # 80 * 0.5

    def test_respects_bar_boundaries(self):
        """Events in different bars should get different multipliers."""
        events = [
            {"start_tick": 0, "velocity": 100},      # Bar 0
            {"start_tick": 1920, "velocity": 100},   # Bar 1
        ]

        result = apply_tension_curve(
            events,
            bar_ticks=1920,
            multipliers=[0.5, 1.5],
        )

        assert result[0]["velocity"] == 50   # 100 * 0.5
        assert result[1]["velocity"] == 127  # 100 * 1.5, clamped to 127

    def test_clamps_velocity_range(self):
        """Velocity should be clamped to valid MIDI range."""
        events = [
            {"start_tick": 0, "velocity": 127},
            {"start_tick": 1920, "velocity": 10},
        ]

        result = apply_tension_curve(
            events,
            bar_ticks=1920,
            multipliers=[2.0, 0.01],  # Would push outside range
        )

        assert result[0]["velocity"] == 127  # Max
        assert result[1]["velocity"] == 1    # Min

    def test_original_not_modified(self, sample_events):
        """Original events should not be modified."""
        original_velocities = [e["velocity"] for e in sample_events]

        apply_tension_curve(sample_events, bar_ticks=1920, multipliers=[0.1])

        for orig_vel, event in zip(original_velocities, sample_events):
            assert event["velocity"] == orig_vel


class TestGenerateCurveForBars:
    """Tests for generating curves spanning specific bar counts."""

    def test_repeat_mode_tiles_curve(self):
        """Repeat mode should tile the base curve."""
        result = generate_curve_for_bars(20, "static", repeat=True)

        assert len(result) == 20

    def test_stretch_mode_interpolates(self):
        """Stretch mode should interpolate the curve."""
        result = generate_curve_for_bars(20, "slow_build", repeat=False)

        assert len(result) == 20

    def test_short_song_truncates(self):
        """Shorter than base curve should truncate."""
        base_len = len(TENSION_CURVES["verse_chorus"])
        result = generate_curve_for_bars(4, "verse_chorus", repeat=True)

        assert len(result) == 4


class TestApplySectionMarkers:
    """Tests for section-based tension application."""

    def test_applies_section_tensions(self):
        """Should apply different tensions to different sections."""
        events = [
            {"start_tick": 0, "velocity": 100},       # Intro
            {"start_tick": 3840, "velocity": 100},    # Verse (bar 2)
            {"start_tick": 15360, "velocity": 100},   # Chorus (bar 8)
        ]

        sections = [
            {"start_bar": 0, "end_bar": 2, "type": "intro"},
            {"start_bar": 2, "end_bar": 8, "type": "verse"},
            {"start_bar": 8, "end_bar": 16, "type": "chorus"},
        ]

        result = apply_section_markers(events, sections, ppq=480, beats_per_bar=4)

        # Different sections should have different velocities
        # Intro < Verse < Chorus typically
        assert len(result) == 3

    def test_empty_sections_returns_copy(self):
        """Empty sections should return unchanged copy."""
        events = [{"start_tick": 0, "velocity": 80}]

        result = apply_section_markers(events, [], ppq=480)

        assert len(result) == 1
        assert result[0]["velocity"] == 80
