"""
Integration tests for the MIDI rendering bridge.

Tests render_plan_to_midi integration with mocks of underlying components.

Run with: pytest tests/test_bridge_integration.py -v
"""

import pytest
from unittest.mock import MagicMock, patch

from music_brain.structure.comprehensive_engine import (
    render_plan_to_midi,
    HarmonyPlan,
)


@pytest.fixture
def mock_plan():
    """Create a basic HarmonyPlan for testing."""
    return HarmonyPlan(
        root_note="C",
        mode="minor",
        tempo_bpm=120,
        time_signature="4/4",
        length_bars=4,
        chord_symbols=["Cm", "Fm", "Cm", "Gm"],
        harmonic_rhythm="1_chord_per_bar",
        mood_profile="grief",
        complexity=0.5,
        vulnerability=0.5,
    )


@pytest.fixture
def mock_plan_major():
    """Create a major key HarmonyPlan."""
    return HarmonyPlan(
        root_note="G",
        mode="ionian",
        tempo_bpm=100,
        time_signature="4/4",
        length_bars=8,
        chord_symbols=["G", "C", "D", "G"],
        mood_profile="tenderness",
        complexity=0.3,
        vulnerability=0.7,
    )


# ==============================================================================
# RENDER BRIDGE TESTS (with mocks)
# ==============================================================================

@patch("music_brain.structure.comprehensive_engine.MIDO_AVAILABLE", True)
@patch("music_brain.daw.logic.LogicProject")
@patch("music_brain.structure.progression.parse_progression_string")
def test_render_bridge_success(mock_parse, MockLogicProject, mock_plan):
    """Bridge should orchestrate LogicProject + progression correctly."""
    # Setup mocks
    mock_project_instance = MockLogicProject.return_value
    mock_project_instance.export_midi.return_value = "path/to/output.mid"
    mock_project_instance.ppq = 480

    # Mock parsed chord
    mock_chord = MagicMock()
    mock_chord.root_num = 0   # C
    mock_chord.quality = "min"
    mock_parse.return_value = [mock_chord, mock_chord, mock_chord, mock_chord]

    output = render_plan_to_midi(mock_plan, "output.mid")

    assert output == "path/to/output.mid"

    # Verify LogicProject was created with correct params
    MockLogicProject.assert_called_once_with(
        name="DAiW_Session",
        tempo_bpm=120,
        time_signature=(4, 4),
    )

    # Verify add_track was called
    mock_project_instance.add_track.assert_called()

    # Check that notes were added
    calls = mock_project_instance.add_track.call_args_list
    assert len(calls) >= 1  # At least harmony track

    # First track should be Harmony
    first_call_kwargs = calls[0][1]
    assert first_call_kwargs.get("name") == "Harmony"
    assert "notes" in first_call_kwargs
    assert len(first_call_kwargs["notes"]) > 0


@patch("music_brain.structure.comprehensive_engine.MIDO_AVAILABLE", True)
@patch("music_brain.daw.logic.LogicProject")
@patch("music_brain.structure.progression.parse_progression_string")
def test_render_bridge_creates_guide_tones(mock_parse, MockLogicProject, mock_plan):
    """Bridge should create guide tones track when requested."""
    mock_project_instance = MockLogicProject.return_value
    mock_project_instance.export_midi.return_value = "output.mid"
    mock_project_instance.ppq = 480

    mock_chord = MagicMock()
    mock_chord.root_num = 0
    mock_chord.quality = "min7"  # 4-note chord for guide tones
    mock_parse.return_value = [mock_chord, mock_chord]

    render_plan_to_midi(mock_plan, "output.mid", include_guide_tones=True)

    calls = mock_project_instance.add_track.call_args_list
    track_names = [call[1].get("name") for call in calls]

    assert "Harmony" in track_names
    assert "Guide Tones" in track_names


@patch("music_brain.structure.comprehensive_engine.MIDO_AVAILABLE", True)
@patch("music_brain.daw.logic.LogicProject")
@patch("music_brain.structure.progression.parse_progression_string")
def test_render_bridge_no_guide_tones_when_disabled(mock_parse, MockLogicProject, mock_plan):
    """Bridge should skip guide tones track when disabled."""
    mock_project_instance = MockLogicProject.return_value
    mock_project_instance.export_midi.return_value = "output.mid"
    mock_project_instance.ppq = 480

    mock_chord = MagicMock()
    mock_chord.root_num = 0
    mock_chord.quality = "min"
    mock_parse.return_value = [mock_chord]

    render_plan_to_midi(mock_plan, "output.mid", include_guide_tones=False)

    calls = mock_project_instance.add_track.call_args_list
    track_names = [call[1].get("name") for call in calls]

    assert "Harmony" in track_names
    assert "Guide Tones" not in track_names


def test_render_bridge_handles_import_error(mock_plan):
    """If imports fail, function should return path without crashing."""
    # Test by providing a plan and checking it returns gracefully
    # The actual render function handles ImportError internally
    output = render_plan_to_midi(mock_plan, "output.mid")
    # Just verify it returns a path string
    assert isinstance(output, str)


@patch("music_brain.structure.progression.parse_progression_string")
@patch("music_brain.daw.logic.LogicProject")
def test_render_bridge_handles_empty_progression(MockLogicProject, mock_parse, mock_plan):
    """Empty progression should be handled gracefully."""
    mock_parse.return_value = []  # No chords parsed

    output = render_plan_to_midi(mock_plan, "output.mid")

    # Should return path without crashing
    assert output == "output.mid"


# ==============================================================================
# HARMONY PLAN INTEGRATION TESTS
# ==============================================================================

def test_harmony_plan_time_signature_parsing():
    """Time signature string should be parsed correctly."""
    plan = HarmonyPlan(time_signature="3/4")
    assert plan.time_signature == "3/4"

    plan6 = HarmonyPlan(time_signature="6/8")
    assert plan6.time_signature == "6/8"


def test_harmony_plan_chord_symbols_default():
    """Chord symbols should be generated from mode if not provided."""
    plan = HarmonyPlan(root_note="D", mode="minor")
    assert len(plan.chord_symbols) > 0

    # Should contain root chord
    assert any("D" in chord for chord in plan.chord_symbols)


def test_harmony_plan_major_progression():
    """Major mode should generate appropriate chords."""
    plan = HarmonyPlan(root_note="G", mode="ionian")
    assert len(plan.chord_symbols) > 0

    # Major chords shouldn't all have 'm'
    has_major = any("m" not in chord for chord in plan.chord_symbols)
    assert has_major


# ==============================================================================
# END-TO-END FLOW TESTS
# ==============================================================================

def test_full_therapy_to_plan_flow():
    """Test complete flow from therapy session to plan generation."""
    from music_brain.structure.comprehensive_engine import TherapySession

    session = TherapySession()

    # Phase 0: Core input
    session.process_core_input("I miss my grandmother who passed away")

    # Should detect grief
    assert session.state.affect_result.primary == "grief"
    assert session.state.suggested_mode == "aeolian"

    # Set scales
    session.set_scales(motivation=7, chaos_tolerance=0.3)

    # Generate plan
    plan = session.generate_plan()

    assert plan.mood_profile == "grief"
    assert plan.mode == "aeolian"
    assert plan.length_bars == 32  # motivation 7 = 32 bars
    assert len(plan.chord_symbols) > 0


def test_therapy_to_plan_rage():
    """Test flow for rage affect."""
    from music_brain.structure.comprehensive_engine import TherapySession

    session = TherapySession()
    session.process_core_input("I am furious and want revenge")
    session.set_scales(motivation=9, chaos_tolerance=0.8)

    plan = session.generate_plan()

    assert plan.mood_profile == "rage"
    assert plan.mode == "phrygian"
    assert plan.tempo_bpm > 140  # Rage base + chaos
    assert plan.length_bars == 64  # High motivation


def test_therapy_to_plan_tenderness():
    """Test flow for tenderness affect."""
    from music_brain.structure.comprehensive_engine import TherapySession

    session = TherapySession()
    session.process_core_input("I want to hold you gently and care for you")
    session.set_scales(motivation=4, chaos_tolerance=0.2)

    plan = session.generate_plan()

    assert plan.mood_profile == "tenderness"
    assert plan.mode == "ionian"
    assert plan.tempo_bpm < 100  # Tenderness is slower
