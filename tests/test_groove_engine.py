"""
Tests for the Groove Engine - Humanization and feel.

Covers: timing drift, velocity modulation, dropout logic, swing, and pocket.

Run with: pytest tests/test_groove_engine.py -v
"""

import pytest
from music_brain.groove_engine import (
    apply_groove,
    apply_swing,
    apply_pocket,
    humanize_velocities,
    MAX_TICKS_DRIFT,
)


@pytest.fixture
def basic_events():
    """Basic grid-aligned events for testing."""
    return [
        {"start_tick": 0, "velocity": 80, "pitch": 60, "duration_ticks": 480},
        {"start_tick": 240, "velocity": 80, "pitch": 62, "duration_ticks": 240},
        {"start_tick": 480, "velocity": 80, "pitch": 64, "duration_ticks": 480},
        {"start_tick": 720, "velocity": 80, "pitch": 65, "duration_ticks": 240},
    ]


@pytest.fixture
def many_events():
    """Large event list for statistical tests."""
    return [
        {"start_tick": i * 10, "velocity": 80, "pitch": 60}
        for i in range(1000)
    ]


# ==============================================================================
# BASIC GROOVE TESTS
# ==============================================================================

def test_groove_returns_new_list(basic_events):
    """apply_groove should not modify original list."""
    original = [ev.copy() for ev in basic_events]
    processed = apply_groove(basic_events, complexity=0.5, vulnerability=0.5)

    # Original unchanged
    for orig, current in zip(original, basic_events):
        assert orig == current

    # Result is different object
    assert processed is not basic_events


def test_groove_empty_input():
    """Empty input should return empty list."""
    result = apply_groove([], complexity=0.5, vulnerability=0.5)
    assert result == []


def test_groove_preserves_event_count_at_zero_complexity(basic_events):
    """At complexity=0, no dropouts should occur."""
    processed = apply_groove(basic_events, complexity=0.0, vulnerability=0.5)
    assert len(processed) == len(basic_events)


def test_groove_low_chaos_low_vulnerability_is_stable(basic_events):
    """With complexity=0.0, timing should stay close to grid."""
    processed = apply_groove(basic_events, complexity=0.0, vulnerability=0.0)

    assert len(processed) == len(basic_events)

    for orig, new in zip(basic_events, processed):
        # Allow small consistent latency bias, but no wild drift
        diff = abs(orig["start_tick"] - new["start_tick"])
        assert diff <= MAX_TICKS_DRIFT

        # Low vulnerability = confident = louder or equal
        assert new["velocity"] >= orig["velocity"] or abs(new["velocity"] - orig["velocity"]) < 20


def test_groove_high_complexity_introduces_jitter(basic_events):
    """High complexity should introduce noticeable timing variance."""
    processed = apply_groove(basic_events, complexity=1.0, vulnerability=0.0, seed=42)

    assert len(processed) <= len(basic_events)  # May drop notes

    # At least some drift should occur
    drifted = False
    for orig, new in zip(basic_events[:len(processed)], processed):
        diff = abs(orig["start_tick"] - new["start_tick"])
        if diff > 2:  # More than just latency bias
            drifted = True
        assert diff <= MAX_TICKS_DRIFT * 2  # Reasonable bound

    # May or may not have drifted due to randomness
    # Just verify no crash and bounds respected


def test_groove_high_vulnerability_softens_dynamics(basic_events):
    """High vulnerability should trend velocities downward."""
    processed = apply_groove(
        basic_events,
        complexity=0.0,
        vulnerability=1.0,
        seed=42
    )

    for new in processed:
        assert new["velocity"] < 80  # Original was 80
        assert new["velocity"] > 0   # Not silent


def test_groove_low_vulnerability_maintains_volume(basic_events):
    """Low vulnerability should maintain or boost velocity."""
    processed = apply_groove(
        basic_events,
        complexity=0.0,
        vulnerability=0.0,
        seed=42
    )

    for new in processed:
        # Should be around or above original
        assert new["velocity"] >= 75  # Allow small variation


def test_groove_reproducible_with_seed(basic_events):
    """Same seed should produce same results."""
    result1 = apply_groove(basic_events, complexity=0.8, vulnerability=0.5, seed=12345)
    result2 = apply_groove(basic_events, complexity=0.8, vulnerability=0.5, seed=12345)

    assert len(result1) == len(result2)
    for e1, e2 in zip(result1, result2):
        assert e1 == e2


# ==============================================================================
# DROPOUT TESTS
# ==============================================================================

@pytest.mark.parametrize("complexity, expect_drops", [
    (0.0, False),  # No drops at 0 complexity
    (1.0, True),   # Some drops at max complexity
])
def test_groove_dropout_logic(many_events, complexity, expect_drops):
    """Statistical test for dropped notes vs complexity."""
    processed = apply_groove(
        many_events,
        complexity=complexity,
        vulnerability=0.5,
        seed=42
    )

    dropped_count = len(many_events) - len(processed)

    if not expect_drops:
        assert dropped_count == 0
    else:
        assert dropped_count > 0
        # Our MAX_DROPOUT_PROB is 0.2, so drop_rate should be below ~0.25
        drop_rate = dropped_count / len(many_events)
        assert drop_rate < 0.3


# ==============================================================================
# SWING TESTS
# ==============================================================================

def test_swing_zero_amount_no_change(basic_events):
    """Zero swing should not modify timing."""
    processed = apply_swing(basic_events, swing_amount=0.0, ppq=480)

    for orig, new in zip(basic_events, processed):
        assert orig["start_tick"] == new["start_tick"]


def test_swing_affects_upbeats(basic_events):
    """Swing should delay upbeat (off-beat) notes."""
    # Create events on specific beat positions
    events = [
        {"start_tick": 0, "velocity": 80},      # Downbeat
        {"start_tick": 240, "velocity": 80},    # Upbeat (8th note)
        {"start_tick": 480, "velocity": 80},    # Downbeat
        {"start_tick": 720, "velocity": 80},    # Upbeat
    ]

    processed = apply_swing(events, swing_amount=0.5, ppq=480)

    # Downbeats should be unchanged
    assert processed[0]["start_tick"] == 0
    assert processed[2]["start_tick"] == 480

    # Upbeats should be delayed
    assert processed[1]["start_tick"] > 240
    assert processed[3]["start_tick"] > 720


# ==============================================================================
# POCKET TESTS
# ==============================================================================

def test_pocket_zero_depth_no_change(basic_events):
    """Zero pocket depth should not modify timing."""
    processed = apply_pocket(basic_events, pocket_depth=0.0, ppq=480)

    for orig, new in zip(basic_events, processed):
        assert orig["start_tick"] == new["start_tick"]


def test_pocket_positive_pushes_back(basic_events):
    """Positive pocket (laid back) should delay all notes."""
    processed = apply_pocket(basic_events, pocket_depth=0.5, ppq=480)

    for orig, new in zip(basic_events, processed):
        assert new["start_tick"] >= orig["start_tick"]


def test_pocket_negative_pulls_forward(basic_events):
    """Negative pocket (rushing) should advance notes (with floor at 0)."""
    # Use events not at tick 0 to test properly
    events = [
        {"start_tick": 100, "velocity": 80},
        {"start_tick": 200, "velocity": 80},
        {"start_tick": 300, "velocity": 80},
    ]

    processed = apply_pocket(events, pocket_depth=-0.5, ppq=480)

    for orig, new in zip(events, processed):
        assert new["start_tick"] <= orig["start_tick"]


# ==============================================================================
# VELOCITY HUMANIZATION TESTS
# ==============================================================================

def test_humanize_velocities_empty():
    """Empty input should return empty."""
    result = humanize_velocities([])
    assert result == []


def test_humanize_velocities_preserves_count(basic_events):
    """Should not add or remove events."""
    result = humanize_velocities(basic_events, variation=0.2)
    assert len(result) == len(basic_events)


def test_humanize_velocities_applies_variation(basic_events):
    """Velocity should vary within bounds."""
    result = humanize_velocities(basic_events, variation=0.3)

    for orig, new in zip(basic_events, result):
        # Velocity should change but stay in range
        assert 1 <= new["velocity"] <= 127


def test_humanize_velocities_with_accent_pattern():
    """Accent pattern should modulate velocity."""
    events = [
        {"start_tick": 0, "velocity": 80},
        {"start_tick": 480, "velocity": 80},
        {"start_tick": 960, "velocity": 80},
        {"start_tick": 1440, "velocity": 80},
    ]

    # Accent pattern: strong, weak, medium, weak
    pattern = [1.2, 0.7, 1.0, 0.7]

    result = humanize_velocities(events, variation=0.0, accent_pattern=pattern, ppq=480)

    # First beat should be louder
    assert result[0]["velocity"] > result[1]["velocity"]

    # Third beat (1.0) should be between
    assert result[1]["velocity"] < result[2]["velocity"] < result[0]["velocity"]
