"""
Tests for the CLI flow - user interaction simulation.

Simulates CLI interactions without actually writing MIDI files.

Run with: pytest tests/test_cli_flow.py -v
"""

import pytest
from unittest.mock import patch, MagicMock


# ==============================================================================
# CLI FLOW TESTS
# ==============================================================================

@patch("builtins.input")
@patch("music_brain.structure.comprehensive_engine.render_plan_to_midi")
def test_cli_happy_path(mock_render, mock_input):
    """Simulate a full user session end-to-end."""
    from music_brain.structure.comprehensive_engine import run_cli

    # Simulate user inputs:
    # 1. Core wound text (contains 'miss' -> grief)
    # 2. Motivation (10)
    # 3. Chaos tolerance (5)
    mock_input.side_effect = ["I miss him terribly", "10", "5"]
    mock_render.return_value = "output.mid"

    run_cli()

    assert mock_render.called

    args, _ = mock_render.call_args
    plan = args[0]

    assert plan.mood_profile == "grief"
    assert plan.length_bars == 64  # motivation 10


@patch("builtins.input")
@patch("music_brain.structure.comprehensive_engine.render_plan_to_midi")
def test_cli_rage_path(mock_render, mock_input):
    """Test CLI with rage-inducing input."""
    from music_brain.structure.comprehensive_engine import run_cli

    mock_input.side_effect = ["I am furious and want revenge", "8", "7"]
    mock_render.return_value = "output.mid"

    run_cli()

    args, _ = mock_render.call_args
    plan = args[0]

    assert plan.mood_profile == "rage"
    assert plan.mode == "phrygian"


@patch("builtins.input")
@patch("music_brain.structure.comprehensive_engine.render_plan_to_midi")
def test_cli_low_motivation(mock_render, mock_input):
    """Test CLI with low motivation produces short song."""
    from music_brain.structure.comprehensive_engine import run_cli

    mock_input.side_effect = ["feeling gentle", "2", "3"]
    mock_render.return_value = "output.mid"

    run_cli()

    args, _ = mock_render.call_args
    plan = args[0]

    assert plan.length_bars == 16  # Low motivation


@patch("builtins.input")
@patch("music_brain.structure.comprehensive_engine.render_plan_to_midi")
def test_cli_retry_empty_input(mock_render, mock_input):
    """CLI should reject empty input until it gets real text."""
    from music_brain.structure.comprehensive_engine import run_cli

    # First two inputs are empty, third is valid
    mock_input.side_effect = ["", "   ", "Real emotional content", "5", "5"]
    mock_render.return_value = "output.mid"

    run_cli()

    assert mock_render.called


@patch("builtins.input")
@patch("music_brain.structure.comprehensive_engine.render_plan_to_midi")
def test_cli_invalid_motivation_retry(mock_render, mock_input):
    """CLI should retry on invalid motivation values."""
    from music_brain.structure.comprehensive_engine import run_cli

    # Invalid motivation inputs, then valid
    mock_input.side_effect = [
        "test content",
        "abc",      # Invalid
        "-5",       # Invalid
        "5",        # Valid
        "5"         # Chaos
    ]
    mock_render.return_value = "output.mid"

    run_cli()

    assert mock_render.called


@patch("builtins.input")
@patch("music_brain.structure.comprehensive_engine.render_plan_to_midi")
def test_cli_chaos_normalization(mock_render, mock_input):
    """Chaos tolerance 0-10 should be normalized to 0-1."""
    from music_brain.structure.comprehensive_engine import run_cli

    # Chaos input of 10 should become 1.0 internally
    mock_input.side_effect = ["test content", "5", "10"]
    mock_render.return_value = "output.mid"

    run_cli()

    args, _ = mock_render.call_args
    plan = args[0]

    assert plan.complexity == 1.0  # Chaos 10 -> complexity 1.0


@patch("builtins.input")
@patch("music_brain.structure.comprehensive_engine.render_plan_to_midi")
def test_cli_zero_chaos(mock_render, mock_input):
    """Zero chaos should result in zero complexity."""
    from music_brain.structure.comprehensive_engine import run_cli

    mock_input.side_effect = ["test content", "5", "0"]
    mock_render.return_value = "output.mid"

    run_cli()

    args, _ = mock_render.call_args
    plan = args[0]

    assert plan.complexity == 0.0


# ==============================================================================
# THERAPY SESSION DIRECT TESTS
# ==============================================================================

def test_therapy_session_scale_bounds():
    """Scale setting should clamp to valid ranges."""
    from music_brain.structure.comprehensive_engine import TherapySession

    session = TherapySession()

    # Out of bounds values should be clamped
    session.set_scales(motivation=-5, chaos_tolerance=2.0)

    assert session.state.motivation == 1.0  # Clamped to min
    assert session.state.chaos_tolerance == 1.0  # Clamped to max

    session.set_scales(motivation=100, chaos_tolerance=-1.0)

    assert session.state.motivation == 10.0  # Clamped to max
    assert session.state.chaos_tolerance == 0.0  # Clamped to min


def test_therapy_session_multiple_core_inputs():
    """Processing multiple core inputs should update state."""
    from music_brain.structure.comprehensive_engine import TherapySession

    session = TherapySession()

    # First input - grief
    session.process_core_input("I miss him")
    assert session.state.suggested_mode == "aeolian"

    # Second input - rage (should update state)
    session.process_core_input("I am furious")
    assert session.state.suggested_mode == "phrygian"


def test_therapy_session_neutral_on_no_keywords():
    """Unknown words should result in neutral affect."""
    from music_brain.structure.comprehensive_engine import TherapySession

    session = TherapySession()

    session.process_core_input("xyzzy foobar baz")

    assert session.state.affect_result.primary == "neutral"
    assert session.state.suggested_mode == "ionian"


# ==============================================================================
# EDGE CASES
# ==============================================================================

def test_affect_with_multiple_keywords():
    """Multiple keywords should contribute to scores."""
    from music_brain.structure.comprehensive_engine import AffectAnalyzer

    analyzer = AffectAnalyzer()

    result = analyzer.analyze("dead dead dead grief mourning loss")

    # Grief should have high score from multiple keywords
    assert result.scores.get("grief", 0) >= 5


def test_plan_generation_without_processing():
    """Plan generation without processing should use defaults."""
    from music_brain.structure.comprehensive_engine import TherapySession

    session = TherapySession()
    session.set_scales(5, 0.5)

    # Generate without processing core input
    plan = session.generate_plan()

    # Should still work with neutral defaults
    assert plan.mode == "ionian"
    assert plan.mood_profile == "neutral"


def test_harmony_plan_custom_chord_symbols():
    """Custom chord symbols should be preserved."""
    from music_brain.structure.comprehensive_engine import HarmonyPlan

    custom_chords = ["Am7", "Dm7", "G7", "Cmaj7"]
    plan = HarmonyPlan(chord_symbols=custom_chords)

    assert plan.chord_symbols == custom_chords


@patch("builtins.input")
@patch("music_brain.structure.comprehensive_engine.render_plan_to_midi")
def test_cli_dissociation_path(mock_render, mock_input):
    """Test CLI with dissociation-inducing input."""
    from music_brain.structure.comprehensive_engine import run_cli

    mock_input.side_effect = ["I feel numb and empty, nothing matters", "4", "6"]
    mock_render.return_value = "output.mid"

    run_cli()

    args, _ = mock_render.call_args
    plan = args[0]

    assert plan.mood_profile == "dissociation"
    assert plan.mode == "locrian"
