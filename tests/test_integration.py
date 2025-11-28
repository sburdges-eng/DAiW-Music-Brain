"""
Integration Tests for DAiW-Music-Brain.

These tests verify end-to-end workflows across multiple modules,
ensuring components work together correctly.

Run with: pytest tests/test_integration.py -v
"""

import pytest
import tempfile
import json
from pathlib import Path

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False

# ==============================================================================
# INTENT TO GENERATION WORKFLOW TESTS
# ==============================================================================

class TestIntentToGenerationWorkflow:
    """Test the complete intent-to-generation pipeline."""

    def test_create_and_validate_intent(self):
        """Test creating and validating a complete song intent."""
        from music_brain.session.intent_schema import (
            CompleteSongIntent,
            validate_intent,
        )

        # Create complete intent using the actual API
        complete_intent = CompleteSongIntent(title="For Grandma")
        complete_intent.song_intent.mood_primary = "grief"
        complete_intent.technical_constraints.technical_genre = "folk"
        complete_intent.technical_constraints.technical_key = "Am"
        complete_intent.technical_constraints.technical_mode = "aeolian"
        complete_intent.technical_constraints.technical_tempo_bpm = 72
        complete_intent.technical_constraints.technical_rule_to_break = "HARMONY_AvoidTonicResolution"
        complete_intent.technical_constraints.rule_breaking_justification = "The grief never fully resolves"

        # Validate
        errors = validate_intent(complete_intent)
        # Some validation may exist but check it runs without crashing
        assert isinstance(errors, list)

    def test_intent_serialization_roundtrip(self):
        """Test that intent can be saved and loaded."""
        from music_brain.session.intent_schema import CompleteSongIntent

        original = CompleteSongIntent(title="Test Song")
        original.song_intent.mood_primary = "defiance"
        original.technical_constraints.technical_genre = "rock"
        original.technical_constraints.technical_key = "E"

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            original.save(temp_path)
            loaded = CompleteSongIntent.load(temp_path)

            assert loaded.title == original.title
            assert loaded.song_intent.mood_primary == original.song_intent.mood_primary
            assert loaded.technical_constraints.technical_key == original.technical_constraints.technical_key
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_process_intent_generates_output(self):
        """Test that processing an intent generates musical elements."""
        from music_brain.session.intent_schema import CompleteSongIntent
        from music_brain.session.intent_processor import process_intent

        intent = CompleteSongIntent(title="Process Test")
        intent.song_intent.mood_primary = "rage"
        intent.technical_constraints.technical_genre = "metal"
        intent.technical_constraints.technical_key = "Dm"
        intent.technical_constraints.technical_mode = "phrygian"

        result = process_intent(intent)

        assert result is not None


# ==============================================================================
# COMPREHENSIVE ENGINE WORKFLOW TESTS
# ==============================================================================

class TestTherapySessionWorkflow:
    """Test the therapy session to harmony plan workflow."""

    def test_full_therapy_session_flow(self):
        """Test complete flow from text input to harmony plan."""
        from music_brain.structure.comprehensive_engine import (
            TherapySession,
            AffectAnalyzer,
        )

        session = TherapySession()

        # Phase 0: Input core wound
        session.process_core_input("I lost my job and feel worthless and angry")

        # Check affect was detected
        assert session.state.affect_result.primary in ['rage', 'grief', 'fear', 'defiance', 'neutral']

        # Set scales - using correct API (positional: motivation, chaos)
        session.set_scales(6, 0.4)

        # Generate plan
        plan = session.generate_plan()

        assert plan is not None
        assert plan.tempo_bpm > 0
        assert plan.length_bars in [16, 32, 64]
        assert plan.mode is not None

    def test_different_affects_produce_different_plans(self):
        """Different emotional inputs should produce different musical plans."""
        from music_brain.structure.comprehensive_engine import TherapySession

        # Rage input
        rage_session = TherapySession()
        rage_session.process_core_input("I am furious at the injustice")
        rage_session.set_scales(7, 0.6)
        rage_plan = rage_session.generate_plan()

        # Grief input
        grief_session = TherapySession()
        grief_session.process_core_input("I mourn the loss of innocence")
        grief_session.set_scales(7, 0.6)
        grief_plan = grief_session.generate_plan()

        # Plans should differ
        assert rage_plan.mode != grief_plan.mode or rage_plan.tempo_bpm != grief_plan.tempo_bpm


# ==============================================================================
# GROOVE WORKFLOW TESTS (Requires mido)
# ==============================================================================

@pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")
class TestGrooveWorkflow:
    """Test groove extraction and application workflow."""

    @pytest.fixture
    def source_midi(self):
        """Create a MIDI file with intentional groove."""
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))

        # Create notes with varied timing and velocity
        for i in range(16):
            velocity = 120 if i % 4 == 0 else (60 if i % 4 == 2 else 80)
            timing_offset = 10 if i % 2 == 1 else 0  # Slight swing
            track.append(mido.Message('note_on', note=36, velocity=velocity, channel=9, time=240 + timing_offset if i > 0 else 0))
            track.append(mido.Message('note_off', note=36, velocity=0, channel=9, time=120))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        mid.save(temp_path)
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def target_midi(self):
        """Create a quantized MIDI file to apply groove to."""
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))

        # Perfectly quantized notes
        for i in range(16):
            track.append(mido.Message('note_on', note=60, velocity=80, channel=0, time=240 if i > 0 else 0))
            track.append(mido.Message('note_off', note=60, velocity=0, channel=0, time=120))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        mid.save(temp_path)
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)

    def test_extract_then_apply_groove(self, source_midi, target_midi):
        """Test extracting groove from one file and applying to another."""
        from music_brain.groove.extractor import extract_groove
        from music_brain.groove.applicator import apply_groove

        # Extract groove
        groove = extract_groove(source_midi)
        assert groove is not None
        assert groove.ppq == 480

        # Apply groove
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            result = apply_groove(
                target_midi,
                groove=groove,
                output=output_path,
                intensity=0.8,
            )
            assert Path(result).exists()

            # Verify output is valid MIDI
            out_mid = mido.MidiFile(result)
            assert out_mid.ticks_per_beat == 480
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_genre_template_workflow(self, target_midi):
        """Test applying a genre template."""
        from music_brain.groove.applicator import apply_groove
        from music_brain.groove.templates import get_genre_template

        # Get a genre template
        funk_groove = get_genre_template("funk")
        assert funk_groove is not None

        # Apply it
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            result = apply_groove(
                target_midi,
                groove=funk_groove,
                output=output_path,
            )
            assert Path(result).exists()
        finally:
            Path(output_path).unlink(missing_ok=True)


# ==============================================================================
# DAW INTEGRATION WORKFLOW TESTS (Requires mido)
# ==============================================================================

@pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")
class TestDAWWorkflow:
    """Test DAW integration workflows."""

    def test_create_project_add_markers_export(self):
        """Test creating a project, adding markers, and exporting."""
        from music_brain.daw.logic import LogicProject, create_logic_template
        from music_brain.daw.markers import get_emotional_structure, merge_markers_with_midi

        # Create project
        project = create_logic_template(
            name="Workflow Test",
            tempo=100.0,
        )

        # Add some notes
        project.add_track(
            name="Lead",
            channel=1,
            notes=[
                {"pitch": 60, "velocity": 100, "start_tick": 0, "duration_ticks": 480},
                {"pitch": 64, "velocity": 90, "start_tick": 480, "duration_ticks": 480},
            ]
        )

        # Export to MIDI
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            midi_path = f.name

        try:
            project.export_midi(midi_path)
            assert Path(midi_path).exists()

            # Get emotional markers
            markers = get_emotional_structure(32, mood_profile="grief")
            assert len(markers) > 0

            # Merge markers with MIDI
            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
                output_path = f.name

            try:
                result = merge_markers_with_midi(markers, midi_path, output_path)
                assert Path(result).exists()

                # Verify markers are in file
                mid = mido.MidiFile(output_path)
                marker_count = sum(
                    1 for track in mid.tracks
                    for msg in track if msg.type == 'marker'
                )
                assert marker_count > 0
            finally:
                Path(output_path).unlink(missing_ok=True)
        finally:
            Path(midi_path).unlink(missing_ok=True)

    def test_import_analyze_export_roundtrip(self):
        """Test importing MIDI, analyzing, and exporting."""
        from music_brain.daw.logic import LogicProject, import_from_logic, export_to_logic
        from music_brain.structure.chord import analyze_chords

        # Create initial MIDI
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))

        # Add a chord progression (C-Am-F-G)
        chords = [
            [60, 64, 67],  # C
            [69, 72, 76],  # Am (one octave up)
            [65, 69, 72],  # F
            [67, 71, 74],  # G
        ]

        for chord in chords:
            for note in chord:
                track.append(mido.Message('note_on', note=note, velocity=80, channel=0, time=0))
            for note in chord:
                track.append(mido.Message('note_off', note=note, velocity=0, channel=0, time=480 if note == chord[-1] else 0))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            input_path = f.name

        mid.save(input_path)

        try:
            # Import
            project = import_from_logic(input_path)
            assert project is not None
            assert project.tempo_bpm == 120.0

            # Analyze chords
            progression = analyze_chords(input_path)
            assert len(progression.chords) > 0
            assert progression.key in ['C', 'G', 'Am', 'A']  # Should detect C major or A minor

            # Export back
            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
                output_path = f.name

            try:
                export_to_logic(input_path, output_path)
                assert Path(output_path).exists()

                # Verify PPQ is 480 (Logic standard)
                out_mid = mido.MidiFile(output_path)
                assert out_mid.ticks_per_beat == 480
            finally:
                Path(output_path).unlink(missing_ok=True)
        finally:
            Path(input_path).unlink(missing_ok=True)


# ==============================================================================
# TEXT GENERATION WORKFLOW TESTS
# ==============================================================================

class TestTextGenerationWorkflow:
    """Test lyrical generation workflow."""

    def test_therapy_to_lyrics_workflow(self):
        """Test generating lyrics from therapy session input."""
        from music_brain.text.lyrical_mirror import mirror_session, save_fragments

        # Simulate therapy session answers
        fragments = mirror_session(
            core_wound="The day I realized my father would never change",
            core_resistance="Fear of disappointing him by speaking my truth",
            core_longing="Freedom to be myself without judgment",
            core_stakes="My sense of self-worth and identity",
            core_transformation="Self-acceptance and moving forward",
            max_lines=6,
        )

        assert isinstance(fragments, list)

        # Save if fragments were generated
        if fragments:
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                output_path = f.name

            try:
                result = save_fragments(fragments, output_path)
                assert Path(result).exists()

                content = Path(result).read_text()
                assert "Lyrical Fragments" in content
            finally:
                Path(output_path).unlink(missing_ok=True)


# ==============================================================================
# TENSION AND STRUCTURE WORKFLOW TESTS
# ==============================================================================

class TestTensionStructureWorkflow:
    """Test tension curve and structure workflow."""

    def test_generate_and_apply_tension(self):
        """Test generating tension curve and applying to events."""
        from music_brain.structure.tension_curve import (
            generate_curve_for_bars,
            apply_tension_curve,
        )

        # Create events
        ppq = 480
        bar_ticks = ppq * 4
        events = []
        for bar in range(8):
            for beat in range(4):
                events.append({
                    "start_tick": bar * bar_ticks + beat * ppq,
                    "velocity": 80,
                    "pitch": 60,
                })

        # Generate curve for 8 bars
        curve = generate_curve_for_bars(8, "catharsis")
        assert len(curve) == 8

        # Apply curve
        result = apply_tension_curve(events, bar_ticks, curve)
        assert len(result) == len(events)

        # Check that velocities were modified
        # Catharsis curve has low start and high end
        first_bar_vel = result[0]["velocity"]
        last_bar_vel = result[-1]["velocity"]
        assert last_bar_vel > first_bar_vel  # Should build tension

    def test_section_markers_with_tension(self):
        """Test applying section markers with tension."""
        from music_brain.structure.tension_curve import apply_section_markers
        from music_brain.daw.markers import get_emotional_structure

        # Create events
        ppq = 480
        bar_ticks = ppq * 4
        events = []
        for bar in range(32):
            for beat in range(4):
                events.append({
                    "start_tick": bar * bar_ticks + beat * ppq,
                    "velocity": 80,
                })

        # Create sections from emotional structure
        markers = get_emotional_structure(32, mood_profile="rage")
        sections = []
        for i, marker in enumerate(markers[:-1]):
            sections.append({
                "start_bar": marker.bar - 1,  # Convert to 0-indexed
                "end_bar": markers[i + 1].bar - 1,
                "type": "verse" if i % 2 == 0 else "chorus",
            })

        # Apply sections
        result = apply_section_markers(events, sections, ppq=ppq)
        assert len(result) == len(events)


# ==============================================================================
# TEACHING MODULE INTEGRATION TESTS
# ==============================================================================

class TestTeachingIntegration:
    """Test teaching module integration."""

    def test_rule_breaking_teacher_exists(self):
        """Test that teaching module is accessible."""
        from music_brain.session.teaching import RuleBreakingTeacher

        teacher = RuleBreakingTeacher()
        assert teacher is not None

    def test_teacher_has_wisdom(self):
        """Test that teacher can provide wisdom."""
        from music_brain.session.teaching import RuleBreakingTeacher

        teacher = RuleBreakingTeacher()
        # Check that get_wisdom method exists and works
        if hasattr(teacher, 'get_wisdom'):
            wisdom = teacher.get_wisdom()
            assert wisdom is not None


# ==============================================================================
# CROSS-MODULE DATA FLOW TESTS
# ==============================================================================

class TestCrossModuleDataFlow:
    """Test data flows correctly between modules."""

    def test_intent_to_therapy_to_plan(self):
        """Test that intent data flows to therapy session correctly."""
        from music_brain.session.intent_schema import CompleteSongIntent
        from music_brain.structure.comprehensive_engine import TherapySession

        # Create intent with Phase 0 data
        intent = CompleteSongIntent(title="Data Flow Test")
        intent.song_intent.mood_primary = "grief"

        # Use mood in therapy session - simulating the flow
        session = TherapySession()
        session.process_core_input("A moment of betrayal with grief and loss")

        # The affect should be detected from the text
        assert session.state.affect_result is not None

    @pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")
    def test_groove_to_daw_project(self):
        """Test groove template integrates with DAW project."""
        from music_brain.groove.templates import get_genre_template
        from music_brain.daw.logic import LogicProject

        # Get groove characteristics
        groove = get_genre_template("jazz")
        assert groove is not None

        # Create project with groove's tempo
        project = LogicProject(
            name="Jazz Project",
            tempo_bpm=groove.tempo_bpm,
        )

        # Project should have matching tempo
        assert project.tempo_bpm == groove.tempo_bpm


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
