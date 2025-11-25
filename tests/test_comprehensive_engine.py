"""
Tests for the Comprehensive Engine - Therapy Session and Affect Analysis.

Covers: affect detection, mode mapping, motivation to length, chaos to tempo,
and basic plan integrity.

Run with: pytest tests/test_comprehensive_engine.py -v
"""

import pytest
from music_brain.structure.comprehensive_engine import (
    AffectAnalyzer,
    TherapySession,
    TherapyState,
    AffectResult,
    HarmonyPlan,
    NoteEvent,
    build_tension_curve,
    tension_multiplier,
    select_kit_for_mood,
)


# ==============================================================================
# AFFECT ANALYZER TESTS
# ==============================================================================

@pytest.fixture
def analyzer():
    return AffectAnalyzer()


@pytest.mark.parametrize("keyword, expected_affect", [
    # Grief keywords
    ("dead", "grief"),
    ("mourning", "grief"),
    ("loss", "grief"),
    ("miss", "grief"),
    # Rage keywords
    ("furious", "rage"),
    ("burn", "rage"),
    ("revenge", "rage"),
    ("angry", "rage"),
    # Awe keywords
    ("infinite", "awe"),
    ("transcend", "awe"),
    # Nostalgia keywords
    ("remember", "nostalgia"),
    ("childhood", "nostalgia"),
    ("memory", "nostalgia"),
    # Fear keywords
    ("panic", "fear"),
    ("trapped", "fear"),
    ("terrified", "fear"),
    # Dissociation keywords
    ("numb", "dissociation"),
    ("nothing", "dissociation"),
    ("floating", "dissociation"),
    # Defiance keywords
    ("refuse", "defiance"),
    ("strong", "defiance"),
    # Tenderness keywords
    ("gentle", "tenderness"),
    ("care", "tenderness"),
    ("soft", "tenderness"),
    # Confusion keywords
    ("chaos", "confusion"),
    ("why", "confusion"),
])
def test_affect_analyzer_keywords(analyzer, keyword, expected_affect):
    """Every emotion keyword should trigger its mapped affect."""
    result = analyzer.analyze(f"I feel {keyword} today")
    assert result.primary == expected_affect
    assert result.scores[expected_affect] >= 1.0


def test_affect_analyzer_empty_input(analyzer):
    """Empty input should return neutral affect with zero intensity."""
    result = analyzer.analyze("")
    assert result.primary == "neutral"
    assert result.intensity == 0.0
    assert result.scores == {}


def test_affect_analyzer_mixed_emotions(analyzer):
    """Multiple affects should be detected with primary and secondary."""
    result = analyzer.analyze("I am furious that he is dead")
    assert result.scores.get("rage", 0) > 0
    assert result.scores.get("grief", 0) > 0
    assert result.secondary is not None


def test_affect_analyzer_case_insensitive(analyzer):
    """Keyword matching should be case-insensitive."""
    result = analyzer.analyze("DEAD FURIOUS NUMB")
    # Should detect multiple affects
    assert result.scores.get("grief", 0) > 0
    assert result.scores.get("rage", 0) > 0
    assert result.scores.get("dissociation", 0) > 0


# ==============================================================================
# THERAPY SESSION LOGIC TESTS
# ==============================================================================

@pytest.fixture
def session():
    return TherapySession()


@pytest.mark.parametrize("input_text, expected_mode", [
    ("I am furious", "phrygian"),           # Rage
    ("So beautiful and infinite", "lydian"),  # Awe
    ("I feel numb", "locrian"),             # Dissociation
    ("I miss him terribly", "aeolian"),     # Grief
    ("I refuse to give up", "mixolydian"),  # Defiance
    ("Soft gentle touch", "ionian"),        # Tenderness
])
def test_process_core_input_mode_mapping(session, input_text, expected_mode):
    """Phase 0 -> Phase 1: text to mode inference."""
    session.process_core_input(input_text)
    assert session.state.suggested_mode == expected_mode


def test_process_core_input_empty(session):
    """Empty input should result in neutral/ionian."""
    result = session.process_core_input("   ")
    assert result == "silence"
    assert session.state.suggested_mode == "ionian"
    assert session.state.affect_result.primary == "neutral"


@pytest.mark.parametrize("motivation, expected_bars", [
    (1, 16),
    (2, 16),
    (3, 16),   # Low motivation -> short song
    (4, 32),
    (5, 32),
    (7, 32),   # Mid motivation -> medium song
    (8, 64),
    (10, 64),  # High motivation -> long song
])
def test_plan_generation_length(session, motivation, expected_bars):
    """Motivation scale should drive song length."""
    session.set_scales(motivation, 0.5)
    session.process_core_input("test input")  # neutral affect
    plan = session.generate_plan()
    assert plan.length_bars == expected_bars


def test_tempo_increases_with_chaos_for_same_affect(session):
    """Higher chaos_tolerance should yield higher tempo for same affect."""
    # Grief baseline
    session.state.affect_result = AffectResult("grief", None, {}, 1.0)
    session.state.suggested_mode = "aeolian"

    session.set_scales(5, 0.0)
    low_chaos_tempo = session.generate_plan().tempo_bpm

    session.set_scales(5, 1.0)
    high_chaos_tempo = session.generate_plan().tempo_bpm

    assert high_chaos_tempo > low_chaos_tempo


def test_tempo_varies_by_affect(session):
    """Different affects should have different base tempos."""
    # Rage should generally be faster than grief at same chaos
    session.set_scales(5, 0.5)

    session.state.affect_result = AffectResult("rage", None, {"rage": 1.0}, 1.0)
    session.state.suggested_mode = "phrygian"
    rage_tempo = session.generate_plan().tempo_bpm

    session.state.affect_result = AffectResult("grief", None, {"grief": 1.0}, 1.0)
    session.state.suggested_mode = "aeolian"
    grief_tempo = session.generate_plan().tempo_bpm

    assert rage_tempo > grief_tempo


def test_generate_plan_uses_suggested_mode(session):
    """Plan mode should be tied to suggested_mode."""
    session.process_core_input("I feel numb and detached")  # dissociation -> locrian
    session.set_scales(5, 0.5)
    plan = session.generate_plan()
    assert plan.mode == "locrian"
    assert plan.mood_profile == "dissociation"


def test_generate_plan_complexity_from_chaos(session):
    """Complexity should derive from chaos tolerance."""
    session.process_core_input("test")

    session.set_scales(5, 0.0)
    low_chaos_plan = session.generate_plan()

    session.set_scales(5, 1.0)
    high_chaos_plan = session.generate_plan()

    assert low_chaos_plan.complexity < high_chaos_plan.complexity


# ==============================================================================
# THERAPY STATE TESTS
# ==============================================================================

def test_therapy_state_defaults():
    """TherapyState should initialize with defaults."""
    state = TherapyState()
    assert state.core_wound_name == ""
    assert state.motivation_scale == 5
    assert state.chaos_tolerance == 0.3
    assert state.suggested_mode == "ionian"


# ==============================================================================
# AFFECT RESULT TESTS
# ==============================================================================

def test_affect_result_creation():
    """AffectResult should store all fields."""
    result = AffectResult("grief", "fear", {"grief": 3.0, "fear": 1.0}, 0.75)
    assert result.primary == "grief"
    assert result.secondary == "fear"
    assert result.intensity == 0.75
    assert result.scores["grief"] == 3.0


# ==============================================================================
# NOTE EVENT TESTS
# ==============================================================================

def test_note_event_creation():
    """NoteEvent should be created with all fields."""
    note = NoteEvent(pitch=60, velocity=80, start_tick=0, duration_ticks=480)
    assert note.pitch == 60
    assert note.velocity == 80
    assert note.start_tick == 0
    assert note.duration_ticks == 480


def test_note_event_to_dict():
    """NoteEvent.to_dict should return proper dict format."""
    note = NoteEvent(pitch=60, velocity=80, start_tick=0, duration_ticks=480)
    d = note.to_dict()
    assert d["pitch"] == 60
    assert d["velocity"] == 80
    assert d["start_tick"] == 0
    assert d["duration_ticks"] == 480


# ==============================================================================
# TENSION CURVE TESTS
# ==============================================================================

def test_build_tension_curve_length():
    """Tension curve should have correct length."""
    curve = build_tension_curve(32)
    assert len(curve) == 32

    curve = build_tension_curve(64)
    assert len(curve) == 64


def test_build_tension_curve_values_in_range():
    """Tension curve values should be reasonable multipliers."""
    curve = build_tension_curve(32)
    for val in curve:
        assert 0.3 <= val <= 1.5


def test_build_tension_curve_zero_length():
    """Zero length should return single default value."""
    curve = build_tension_curve(0)
    assert curve == [1.0]


def test_tension_multiplier_boundaries():
    """Tension multiplier should handle edge cases."""
    assert tension_multiplier(0.0) is not None
    assert tension_multiplier(1.0) is not None
    assert tension_multiplier(0.5) is not None


def test_tension_multiplier_with_curve():
    """Tension multiplier should use provided curve."""
    curve = [0.5, 0.7, 1.0, 1.2, 0.8]
    assert tension_multiplier(0.0, curve) == 0.5
    assert tension_multiplier(1.0, curve) == 0.8


# ==============================================================================
# KIT SELECTION TESTS
# ==============================================================================

def test_select_kit_for_grief():
    """Grief should map to LoFi kit."""
    assert select_kit_for_mood("grief") == "LoFi_Bedroom_Kit"


def test_select_kit_for_rage():
    """Rage should map to Industrial kit."""
    assert select_kit_for_mood("rage") == "Industrial_Glitch_Kit"


def test_select_kit_for_unknown():
    """Unknown mood should map to Standard kit."""
    assert select_kit_for_mood("unknown") == "Standard_Kit"
    assert select_kit_for_mood("") == "Standard_Kit"
    assert select_kit_for_mood(None) == "Standard_Kit"
