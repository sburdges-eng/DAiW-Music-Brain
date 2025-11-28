"""
Tests for the Tension Curve module (dynamic breathing over time).

Covers: tension curve presets, apply_tension_curve, apply_section_markers,
generate_curve_for_bars, and TensionProfile dataclass.

Run with: pytest tests/test_tension_curve.py -v
"""

import pytest
from music_brain.structure.tension_curve import (
    TENSION_CURVES,
    TensionProfile,
    get_tension_curve,
    list_tension_curves,
    apply_tension_curve,
    apply_section_markers,
    generate_curve_for_bars,
)


# ==============================================================================
# TENSION CURVES PRESETS TESTS
# ==============================================================================

class TestTensionCurvesPresets:
    """Test the preset tension curves dictionary."""

    def test_presets_exist(self):
        expected = ["verse_chorus", "slow_build", "front_loaded", "wave",
                    "catharsis", "static", "descent", "spiral"]
        for preset in expected:
            assert preset in TENSION_CURVES

    def test_all_presets_are_lists(self):
        for name, curve in TENSION_CURVES.items():
            assert isinstance(curve, list), f"{name} should be a list"

    def test_all_presets_have_values(self):
        for name, curve in TENSION_CURVES.items():
            assert len(curve) > 0, f"{name} should have values"

    def test_all_values_are_floats(self):
        for name, curve in TENSION_CURVES.items():
            for value in curve:
                assert isinstance(value, (int, float)), f"{name} has non-numeric value"

    def test_values_in_reasonable_range(self):
        """Tension multipliers should typically be between 0.0 and 2.0."""
        for name, curve in TENSION_CURVES.items():
            for value in curve:
                assert 0.0 <= value <= 2.0, f"{name} has out-of-range value {value}"


# ==============================================================================
# GET_TENSION_CURVE TESTS
# ==============================================================================

class TestGetTensionCurve:
    """Test get_tension_curve function."""

    def test_returns_list(self):
        result = get_tension_curve("verse_chorus")
        assert isinstance(result, list)

    def test_returns_copy(self):
        """Should return a copy, not the original."""
        result1 = get_tension_curve("verse_chorus")
        result2 = get_tension_curve("verse_chorus")

        result1[0] = 999  # Modify
        assert result2[0] != 999  # Original should be unchanged

    def test_all_presets_accessible(self):
        for name in TENSION_CURVES.keys():
            result = get_tension_curve(name)
            assert len(result) > 0

    def test_invalid_name_raises_valueerror(self):
        with pytest.raises(ValueError) as exc_info:
            get_tension_curve("nonexistent_curve")

        assert "Unknown tension curve" in str(exc_info.value)
        assert "Available:" in str(exc_info.value)


# ==============================================================================
# LIST_TENSION_CURVES TESTS
# ==============================================================================

class TestListTensionCurves:
    """Test list_tension_curves function."""

    def test_returns_list(self):
        result = list_tension_curves()
        assert isinstance(result, list)

    def test_contains_all_presets(self):
        result = list_tension_curves()
        for preset in TENSION_CURVES.keys():
            assert preset in result

    def test_length_matches_presets(self):
        result = list_tension_curves()
        assert len(result) == len(TENSION_CURVES)


# ==============================================================================
# TENSION PROFILE DATACLASS TESTS
# ==============================================================================

class TestTensionProfile:
    """Test TensionProfile dataclass."""

    def test_creation(self):
        profile = TensionProfile(
            name="Test Profile",
            multipliers=[0.5, 0.8, 1.0, 0.7],
        )
        assert profile.name == "Test Profile"
        assert profile.multipliers == [0.5, 0.8, 1.0, 0.7]

    def test_default_values(self):
        profile = TensionProfile(
            name="Test",
            multipliers=[1.0],
        )
        assert profile.affects_velocity is True
        assert profile.affects_timing is False
        assert profile.affects_density is False

    def test_custom_affects_flags(self):
        profile = TensionProfile(
            name="Custom",
            multipliers=[1.0],
            affects_velocity=False,
            affects_timing=True,
            affects_density=True,
        )
        assert profile.affects_velocity is False
        assert profile.affects_timing is True
        assert profile.affects_density is True


# ==============================================================================
# APPLY_TENSION_CURVE TESTS
# ==============================================================================

class TestApplyTensionCurve:
    """Test apply_tension_curve function."""

    @pytest.fixture
    def sample_events(self):
        """Create sample MIDI-like events."""
        return [
            {"start_tick": 0, "velocity": 80},
            {"start_tick": 480, "velocity": 80},
            {"start_tick": 960, "velocity": 80},
            {"start_tick": 1440, "velocity": 80},
            {"start_tick": 1920, "velocity": 80},  # Bar 2
            {"start_tick": 2400, "velocity": 80},
            {"start_tick": 2880, "velocity": 80},
            {"start_tick": 3360, "velocity": 80},
        ]

    def test_returns_list(self, sample_events):
        result = apply_tension_curve(
            sample_events,
            bar_ticks=1920,
            multipliers=[0.8, 1.2],
        )
        assert isinstance(result, list)

    def test_preserves_event_count(self, sample_events):
        result = apply_tension_curve(
            sample_events,
            bar_ticks=1920,
            multipliers=[0.8, 1.2],
        )
        assert len(result) == len(sample_events)

    def test_empty_events_returns_empty(self):
        result = apply_tension_curve([], bar_ticks=1920, multipliers=[1.0])
        assert result == []

    def test_empty_multipliers_returns_copy(self, sample_events):
        result = apply_tension_curve(
            sample_events,
            bar_ticks=1920,
            multipliers=[],
        )
        assert len(result) == len(sample_events)
        # Should be copies
        assert result[0] is not sample_events[0]

    def test_velocity_scaled_down(self, sample_events):
        result = apply_tension_curve(
            sample_events,
            bar_ticks=1920,
            multipliers=[0.5],  # Half velocity
        )
        # First bar events should have reduced velocity
        assert result[0]["velocity"] == 40  # 80 * 0.5

    def test_velocity_scaled_up(self, sample_events):
        result = apply_tension_curve(
            sample_events,
            bar_ticks=1920,
            multipliers=[1.5],  # 150% velocity
        )
        assert result[0]["velocity"] == 120  # 80 * 1.5

    def test_velocity_clamped_to_max(self, sample_events):
        result = apply_tension_curve(
            sample_events,
            bar_ticks=1920,
            multipliers=[2.0],  # Would be 160
            max_velocity=127,
        )
        assert result[0]["velocity"] <= 127

    def test_velocity_clamped_to_min(self, sample_events):
        result = apply_tension_curve(
            sample_events,
            bar_ticks=1920,
            multipliers=[0.01],  # Would be ~0
            min_velocity=1,
        )
        assert result[0]["velocity"] >= 1

    def test_different_bars_get_different_multipliers(self, sample_events):
        result = apply_tension_curve(
            sample_events,
            bar_ticks=1920,
            multipliers=[0.5, 1.5],  # Bar 1 = 0.5, Bar 2 = 1.5
        )
        # Bar 1 events (ticks 0-1919) should be quieter
        bar1_velocity = result[0]["velocity"]  # tick 0
        # Bar 2 events (ticks 1920+) should be louder
        bar2_velocity = result[4]["velocity"]  # tick 1920

        assert bar1_velocity < bar2_velocity

    def test_clamps_to_last_multiplier(self, sample_events):
        """Events beyond curve length should use last multiplier."""
        result = apply_tension_curve(
            sample_events,
            bar_ticks=960,  # Half bar = 4 bars total
            multipliers=[0.5, 1.5],  # Only 2 multipliers
        )
        # Bar 3+ should use last multiplier (1.5)
        # Events at tick 1920+ are bar 3+
        assert result[4]["velocity"] == 120  # 80 * 1.5

    def test_affect_velocity_can_be_disabled(self, sample_events):
        result = apply_tension_curve(
            sample_events,
            bar_ticks=1920,
            multipliers=[0.5],
            affect_velocity=False,
        )
        # Velocities should be unchanged
        assert result[0]["velocity"] == 80

    def test_original_events_not_modified(self, sample_events):
        original_velocity = sample_events[0]["velocity"]
        apply_tension_curve(
            sample_events,
            bar_ticks=1920,
            multipliers=[0.5],
        )
        assert sample_events[0]["velocity"] == original_velocity


# ==============================================================================
# APPLY_SECTION_MARKERS TESTS
# ==============================================================================

class TestApplySectionMarkers:
    """Test apply_section_markers function."""

    @pytest.fixture
    def sample_events(self):
        """Events spanning multiple bars."""
        ppq = 480
        bar_ticks = ppq * 4
        events = []
        for bar in range(8):
            for beat in range(4):
                events.append({
                    "start_tick": bar * bar_ticks + beat * ppq,
                    "velocity": 80,
                })
        return events

    @pytest.fixture
    def sample_sections(self):
        return [
            {"start_bar": 0, "end_bar": 2, "type": "intro"},
            {"start_bar": 2, "end_bar": 4, "type": "verse"},
            {"start_bar": 4, "end_bar": 6, "type": "chorus"},
            {"start_bar": 6, "end_bar": 8, "type": "outro"},
        ]

    def test_returns_list(self, sample_events, sample_sections):
        result = apply_section_markers(sample_events, sample_sections)
        assert isinstance(result, list)

    def test_preserves_event_count(self, sample_events, sample_sections):
        result = apply_section_markers(sample_events, sample_sections)
        assert len(result) == len(sample_events)

    def test_empty_events_returns_empty(self, sample_sections):
        result = apply_section_markers([], sample_sections)
        assert result == []

    def test_empty_sections_returns_copy(self, sample_events):
        result = apply_section_markers(sample_events, [])
        assert len(result) == len(sample_events)

    def test_chorus_louder_than_intro(self, sample_events, sample_sections):
        result = apply_section_markers(sample_events, sample_sections, ppq=480)

        # Intro is bar 0-1, chorus is bar 4-5
        # Intro tension = 0.6, chorus tension = 1.0
        intro_event = result[0]  # First event in intro
        chorus_event = result[16]  # First event in chorus (bar 4)

        assert chorus_event["velocity"] > intro_event["velocity"]

    def test_custom_tension_override(self, sample_events):
        sections = [
            {"start_bar": 0, "end_bar": 4, "type": "verse", "tension": 0.3},
            {"start_bar": 4, "end_bar": 8, "type": "verse", "tension": 1.5},
        ]
        result = apply_section_markers(sample_events, sections, ppq=480)

        # First section should be quiet, second loud
        first_velocity = result[0]["velocity"]
        second_velocity = result[16]["velocity"]

        assert second_velocity > first_velocity

    def test_different_beats_per_bar(self, sample_events, sample_sections):
        # Waltz (3/4)
        result = apply_section_markers(
            sample_events, sample_sections, ppq=480, beats_per_bar=3
        )
        assert len(result) == len(sample_events)


# ==============================================================================
# GENERATE_CURVE_FOR_BARS TESTS
# ==============================================================================

class TestGenerateCurveForBars:
    """Test generate_curve_for_bars function."""

    def test_returns_list(self):
        result = generate_curve_for_bars(16, "verse_chorus")
        assert isinstance(result, list)

    def test_returns_correct_length(self):
        result = generate_curve_for_bars(32, "verse_chorus")
        assert len(result) == 32

    def test_invalid_curve_raises(self):
        with pytest.raises(ValueError):
            generate_curve_for_bars(16, "nonexistent")

    def test_repeat_mode_tiles(self):
        """Repeat mode should tile the curve."""
        base = get_tension_curve("verse_chorus")
        base_len = len(base)

        result = generate_curve_for_bars(base_len * 3, "verse_chorus", repeat=True)

        # Should be 3 copies of base
        assert len(result) == base_len * 3
        assert result[:base_len] == base
        assert result[base_len:base_len*2] == base

    def test_stretch_mode_interpolates(self):
        """Stretch mode should interpolate the curve."""
        result = generate_curve_for_bars(100, "verse_chorus", repeat=False)

        assert len(result) == 100
        # Values should be floats (interpolated)
        for value in result:
            assert isinstance(value, (int, float))

    def test_stretch_shorter_than_base(self):
        """Stretching to fewer bars than base should truncate."""
        result = generate_curve_for_bars(4, "verse_chorus", repeat=False)
        assert len(result) == 4

    def test_repeat_exact_multiple(self):
        base = get_tension_curve("static")
        exact_multiple = len(base) * 2

        result = generate_curve_for_bars(exact_multiple, "static", repeat=True)
        assert len(result) == exact_multiple

    def test_repeat_non_multiple(self):
        """Non-multiple lengths should truncate to exact bar count."""
        base = get_tension_curve("verse_chorus")
        non_multiple = len(base) + 3

        result = generate_curve_for_bars(non_multiple, "verse_chorus", repeat=True)
        assert len(result) == non_multiple


# ==============================================================================
# EDGE CASES
# ==============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_bar_curve(self):
        result = generate_curve_for_bars(1, "verse_chorus")
        assert len(result) == 1

    def test_zero_bars_curve(self):
        result = generate_curve_for_bars(0, "verse_chorus")
        assert len(result) == 0

    def test_very_long_curve(self):
        result = generate_curve_for_bars(1000, "verse_chorus", repeat=True)
        assert len(result) == 1000

    def test_apply_to_events_without_velocity(self):
        events = [
            {"start_tick": 0, "pitch": 60},
            {"start_tick": 480, "pitch": 62},
        ]
        result = apply_tension_curve(events, bar_ticks=1920, multipliers=[0.5])
        # Should not crash, events without velocity just pass through
        assert len(result) == 2

    def test_apply_to_events_without_start_tick(self):
        events = [
            {"velocity": 80},
            {"velocity": 90},
        ]
        result = apply_tension_curve(events, bar_ticks=1920, multipliers=[0.5])
        # Should use default start_tick of 0 (all in bar 0)
        assert len(result) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
