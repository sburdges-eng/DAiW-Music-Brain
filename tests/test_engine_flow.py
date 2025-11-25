# tests/test_engine_flow.py
"""
Tests for the full engine flow - TherapySession → HarmonyPlan → MIDI.

Covers: affect analysis, plan generation, MIDI rendering integration.

Run with: pytest tests/test_engine_flow.py -v
"""

import os
import tempfile

import pytest

from music_brain.structure.comprehensive_engine import (
    TherapySession,
    HarmonyPlan,
    AffectResult,
    render_plan_to_midi,
    AFFECT_TO_MODE,
    MOTIVATION_TO_LENGTH,
)


class TestTherapySessionBasics:
    """Basic TherapySession functionality tests."""

    def test_session_init(self):
        """TherapySession should initialize cleanly."""
        session = TherapySession()
        assert session is not None
        assert session.state is not None

    def test_process_core_input(self):
        """Should process emotional text and return affect."""
        session = TherapySession()
        affect = session.process_core_input("I feel lost and abandoned")
        assert isinstance(affect, str)
        assert len(affect) > 0

    def test_set_scales(self):
        """Should accept motivation and complexity scales."""
        session = TherapySession()
        session.set_scales(motivation=7, complexity=0.5)
        assert session.state.motivation == 7
        assert session.state.complexity == 0.5


class TestAffectAnalysis:
    """Tests for emotional affect analysis."""

    @pytest.mark.parametrize("text,expected_affects", [
        ("I am so angry at the world", ["rage", "anger", "defiance"]),
        ("Everything feels hopeless and sad", ["grief", "sadness", "despair"]),
        ("I feel nothing, completely numb", ["dissociation", "numbness", "void"]),
        ("This is beautiful and overwhelming", ["awe", "wonder", "transcendence"]),
    ])
    def test_affect_keywords(self, text, expected_affects):
        """Text with affect keywords should detect that affect."""
        session = TherapySession()
        affect = session.process_core_input(text)
        # Should detect at least one of the expected affects
        assert any(exp in affect.lower() for exp in expected_affects) or affect in AFFECT_TO_MODE


class TestHarmonyPlanGeneration:
    """Tests for HarmonyPlan generation."""

    def test_generate_plan_returns_harmony_plan(self):
        """Should return a HarmonyPlan object."""
        session = TherapySession()
        session.process_core_input("I feel disconnected from reality")
        session.set_scales(motivation=5, complexity=0.3)
        plan = session.generate_plan()
        assert isinstance(plan, HarmonyPlan)

    def test_plan_has_required_fields(self):
        """HarmonyPlan should have all required fields."""
        session = TherapySession()
        session.process_core_input("Deep sadness and regret")
        session.set_scales(motivation=8, complexity=0.6)
        plan = session.generate_plan()

        assert hasattr(plan, 'root_note')
        assert hasattr(plan, 'mode')
        assert hasattr(plan, 'tempo_bpm')
        assert hasattr(plan, 'length_bars')
        assert hasattr(plan, 'chord_symbols')
        assert hasattr(plan, 'complexity')

    def test_plan_mode_from_affect(self):
        """Mode should be derived from detected affect."""
        session = TherapySession()
        session.process_core_input("Pure rage and fury")
        session.set_scales(motivation=5, complexity=0.5)
        plan = session.generate_plan()
        # Rage often maps to phrygian or similar dark modes
        assert plan.mode in ["phrygian", "locrian", "aeolian", "dorian"]

    def test_plan_length_from_motivation(self):
        """Length should scale with motivation."""
        # Low motivation = short
        session1 = TherapySession()
        session1.process_core_input("test")
        session1.set_scales(motivation=2, complexity=0.5)
        plan1 = session1.generate_plan()

        # High motivation = long
        session2 = TherapySession()
        session2.process_core_input("test")
        session2.set_scales(motivation=9, complexity=0.5)
        plan2 = session2.generate_plan()

        assert plan1.length_bars <= plan2.length_bars


class TestMIDIRendering:
    """Tests for MIDI file rendering."""

    @pytest.fixture
    def sample_plan(self):
        """Return a sample HarmonyPlan for testing."""
        return HarmonyPlan(
            root_note="D",
            mode="dorian",
            tempo_bpm=90,
            length_bars=16,
            chord_symbols=["Dm7", "G7", "Cmaj7", "Fmaj7"],
            complexity=0.4,
            structure_type="standard",
        )

    def test_render_creates_file(self, sample_plan):
        """Should create a MIDI file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.mid")
            result = render_plan_to_midi(sample_plan, path)
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0

    def test_render_returns_path(self, sample_plan):
        """Should return the output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.mid")
            result = render_plan_to_midi(sample_plan, path)
            assert result == path

    def test_render_valid_midi(self, sample_plan):
        """Output should be valid MIDI file."""
        import mido

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.mid")
            render_plan_to_midi(sample_plan, path)

            # Should parse without error
            mid = mido.MidiFile(path)
            assert len(mid.tracks) > 0
            assert mid.ticks_per_beat > 0


class TestFullPipeline:
    """End-to-end pipeline tests."""

    def test_full_therapy_to_midi_flow(self):
        """Complete flow: text → session → plan → MIDI."""
        session = TherapySession()

        # Phase 1: Process emotional input
        affect = session.process_core_input(
            "I chose safety over passion and now I feel dead inside"
        )
        assert affect is not None

        # Phase 2: Set scales
        session.set_scales(motivation=7, complexity=0.5)

        # Phase 3: Generate plan
        plan = session.generate_plan()
        assert plan.length_bars > 0
        assert len(plan.chord_symbols) > 0

        # Phase 4: Render MIDI
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "therapy_session.mid")
            result = render_plan_to_midi(plan, path)
            assert os.path.exists(result)

    def test_multiple_sessions_independent(self):
        """Multiple sessions should be independent."""
        session1 = TherapySession()
        session1.process_core_input("anger")
        session1.set_scales(5, 0.5)

        session2 = TherapySession()
        session2.process_core_input("sadness")
        session2.set_scales(8, 0.2)

        plan1 = session1.generate_plan()
        plan2 = session2.generate_plan()

        # Should have different characteristics
        assert plan1.mode != plan2.mode or plan1.length_bars != plan2.length_bars


class TestAffectMappings:
    """Tests for affect → mode mappings."""

    def test_all_affects_have_modes(self):
        """All affects in mapping should have valid modes."""
        for affect, mode in AFFECT_TO_MODE.items():
            assert isinstance(affect, str)
            assert isinstance(mode, str)
            assert mode in [
                "ionian", "dorian", "phrygian", "lydian",
                "mixolydian", "aeolian", "locrian"
            ]

    def test_motivation_to_length_mapping(self):
        """Motivation levels should map to bar lengths."""
        for key, value in MOTIVATION_TO_LENGTH.items():
            assert isinstance(value, int)
            assert value > 0
