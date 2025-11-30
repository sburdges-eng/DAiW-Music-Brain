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
)


# ==============================================================================
# AFFECT ANALYZER TESTS
# ==============================================================================

@pytest.fixture
def analyzer():
    return AffectAnalyzer()


@pytest.mark.parametrize("keyword, expected_affect", [
    # Grief keywords (actual: loss, gone, miss, dead, died, funeral, mourning, never again, empty)
    ("dead", "grief"),
    ("mourning", "grief"),
    ("loss", "grief"),
    ("miss", "grief"),
    # Rage keywords (actual: angry, furious, hate, betrayed, unfair, revenge, burn, fight, destroy)
    ("furious", "rage"),
    ("burn", "rage"),
    ("revenge", "rage"),
    ("angry", "rage"),
    # Awe keywords (actual: wonder, beautiful, infinite, god, universe, transcend, light, vast)
    ("god", "awe"),
    ("infinite", "awe"),
    ("beautiful", "awe"),  # Fixed: "divine" is not in awe keywords
    # Nostalgia keywords (actual: remember, used to, childhood, back when, old days, memory, home)
    ("remember", "nostalgia"),
    ("childhood", "nostalgia"),
    ("memory", "nostalgia"),
    # Fear keywords (actual: scared, terrified, panic, can't breathe, trapped, anxious, dread)
    ("panic", "fear"),
    ("trapped", "fear"),
    ("terrified", "fear"),
    # Dissociation keywords (actual: numb, nothing, floating, unreal, detached, fog, grey, wall)
    ("numb", "dissociation"),
    ("nothing", "dissociation"),
    ("floating", "dissociation"),  # Fixed: "empty" is in grief keywords
    # Defiance keywords (actual: won't, refuse, stand, strong, break, free, my own, no more)
    ("refuse", "defiance"),
    ("strong", "defiance"),
    ("stand", "defiance"),  # Fixed: "fight" is in rage keywords
    # Tenderness keywords (actual: soft, gentle, hold, love, kind, care, fragile, warm)
    ("gentle", "tenderness"),
    ("care", "tenderness"),
    ("soft", "tenderness"),
    # Confusion keywords (actual: why, lost, don't know, spinning, chaos, strange, question)
    ("chaos", "confusion"),
    ("why", "confusion"),
    ("spinning", "confusion"),  # Fixed: "confused" is not in confusion keywords
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


def test_affect_analyzer_whitespace_only(analyzer):
    """Whitespace-only input should be treated as empty."""
    result = analyzer.analyze("   \n\t  ")
    assert result.primary == "neutral"
    assert result.intensity == 0.0


def test_affect_analyzer_mixed_emotions(analyzer):
    """Multiple affects should be detected with primary and secondary."""
    result = analyzer.analyze("I am furious that he is dead")
    assert result.scores.get("rage", 0) > 0
    assert result.scores.get("grief", 0) > 0
    assert result.secondary is not None


def test_affect_analyzer_case_insensitive(analyzer):
    """Keyword matching should be case-insensitive."""
    result = analyzer.analyze("DEAD FURIOUS NUMB")
    assert len(result.scores) >= 3


# ==============================================================================
# THERAPY SESSION LOGIC TESTS
# ==============================================================================

@pytest.fixture
def session():
    return TherapySession()


@pytest.mark.parametrize("input_text, expected_mode", [
    ("I am furious", "phrygian"),      # Rage
    ("So beautiful and divine", "lydian"),  # Awe
    ("I feel numb", "locrian"),        # Dissociation
    ("I miss him terribly", "aeolian"), # Grief
    ("I refuse to give up", "mixolydian"),  # Defiance
    ("Soft gentle touch", "ionian"),   # Tenderness
])
def test_process_core_input_mode_mapping(session, input_text, expected_mode):
    """Phase 0 -> Phase 1: text to mode inference."""
    session.process_core_input(input_text)
    assert session.state.suggested_mode == expected_mode


def test_process_core_input_empty(session):
    """Empty input should result in neutral/ionian."""
    session.process_core_input("   ")
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


def test_generate_plan_length_from_motivation(session):
    """Lower motivation should mean shorter song length."""
    session.process_core_input("test")

    session.set_scales(1, 0.5)  # Low motivation
    low_mot_plan = session.generate_plan()

    session.set_scales(10, 0.5)  # High motivation
    high_mot_plan = session.generate_plan()

    # Low motivation = shorter song (16 bars vs 64 bars)
    assert low_mot_plan.length_bars < high_mot_plan.length_bars


# ==============================================================================
# HARMONY PLAN TESTS
# ==============================================================================

def test_harmony_plan_creation():
    """HarmonyPlan should be creatable with required fields."""
    plan = HarmonyPlan(
        root_note="C",
        mode="minor",
        tempo_bpm=120,
        time_signature="4/4",
        length_bars=16,
        chord_symbols=["Cm", "Fm", "Gm", "Cm"],
        harmonic_rhythm="1_chord_per_bar",
        mood_profile="grief",
        complexity=0.5,
    )
    assert plan.root_note == "C"
    assert plan.mode == "minor"
    assert plan.tempo_bpm == 120
    assert plan.length_bars == 16
    assert len(plan.chord_symbols) > 0


def test_harmony_plan_stores_chord_symbols():
    """Chord symbols should be stored correctly."""
    chords = ["Am", "Dm", "Em", "Am"]
    plan = HarmonyPlan(
        root_note="A",
        mode="aeolian",
        tempo_bpm=100,
        time_signature="4/4",
        length_bars=8,
        chord_symbols=chords,
        harmonic_rhythm="1_chord_per_bar",
        mood_profile="grief",
        complexity=0.3,
    )
    assert plan.chord_symbols == chords
    assert any("m" in chord for chord in plan.chord_symbols)


# ==============================================================================
# THERAPY STATE TESTS
# ==============================================================================

def test_therapy_state_defaults():
    """TherapyState should initialize with defaults."""
    state = TherapyState()
    assert state.core_wound_name == ""  # Fixed: was core_wound_text
    assert state.motivation_scale == 5  # Fixed: was motivation
    assert state.chaos_tolerance == 0.3  # Default is 0.3, not 0.5
    assert state.suggested_mode == "ionian"
    # Note: phase attribute doesn't exist in current implementation


# ==============================================================================
# AFFECT RESULT TESTS
# ==============================================================================

def test_affect_result_repr():
    """AffectResult should have a readable repr."""
    result = AffectResult("grief", "fear", {"grief": 3.0, "fear": 1.0}, 0.75)
    repr_str = repr(result)
    assert "grief" in repr_str
    assert "0.75" in repr_str
