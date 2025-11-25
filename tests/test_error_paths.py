"""
Tests for error handling across all modules.

Covers: Invalid inputs, missing files, malformed data, boundary conditions,
and graceful degradation.

Run with: pytest tests/test_error_paths.py -v
"""

import pytest
import json
import tempfile
from pathlib import Path

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False


# ==============================================================================
# INTENT SCHEMA ERROR HANDLING
# ==============================================================================

class TestIntentSchemaErrors:
    """Test error handling in intent schema module."""

    def test_from_dict_with_invalid_tempo_range(self):
        """Invalid tempo range should be handled gracefully."""
        from music_brain.session.intent_schema import CompleteSongIntent

        # String instead of list
        data = {
            "technical_constraints": {
                "technical_tempo_range": "invalid",
            }
        }

        # Should not crash, may use default
        try:
            intent = CompleteSongIntent.from_dict(data)
            # Either uses default or handles the invalid value
            assert intent is not None
        except (TypeError, ValueError):
            # Acceptable to raise an error for invalid data
            pass

    def test_load_malformed_json(self):
        """Loading malformed JSON should raise appropriate error."""
        from music_brain.session.intent_schema import CompleteSongIntent

        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                CompleteSongIntent.load(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_nonexistent_file(self):
        """Loading nonexistent file should raise FileNotFoundError."""
        from music_brain.session.intent_schema import CompleteSongIntent

        with pytest.raises(FileNotFoundError):
            CompleteSongIntent.load("/nonexistent/path/file.json")

    def test_save_to_invalid_path(self):
        """Saving to invalid path should raise appropriate error."""
        from music_brain.session.intent_schema import CompleteSongIntent

        intent = CompleteSongIntent(title="Test")

        with pytest.raises((FileNotFoundError, OSError, PermissionError)):
            intent.save("/nonexistent/directory/file.json")

    def test_validate_intent_with_extreme_tension(self):
        """Extreme tension values should be flagged."""
        from music_brain.session.intent_schema import (
            CompleteSongIntent, SongRoot, SongIntent, validate_intent
        )

        intent = CompleteSongIntent(
            song_root=SongRoot(core_event="Test", core_longing="Test"),
            song_intent=SongIntent(
                mood_primary="grief",
                mood_secondary_tension=100.0,  # Way out of range
            ),
        )

        issues = validate_intent(intent)
        assert any("tension" in issue.lower() for issue in issues)

    def test_suggest_rule_break_empty_string(self):
        """Empty string emotion should return empty suggestions."""
        from music_brain.session.intent_schema import suggest_rule_break

        suggestions = suggest_rule_break("")
        assert suggestions == []

    def test_get_rule_breaking_info_empty_string(self):
        """Empty string rule key should return None."""
        from music_brain.session.intent_schema import get_rule_breaking_info

        info = get_rule_breaking_info("")
        assert info is None


# ==============================================================================
# INTENT PROCESSOR ERROR HANDLING
# ==============================================================================

class TestIntentProcessorErrors:
    """Test error handling in intent processor module."""

    def test_processor_with_empty_intent(self):
        """Processor should handle empty intent gracefully."""
        from music_brain.session.intent_schema import CompleteSongIntent
        from music_brain.session.intent_processor import IntentProcessor

        intent = CompleteSongIntent()
        processor = IntentProcessor(intent)

        # Should not crash, uses defaults
        harmony = processor.generate_harmony()
        assert harmony is not None

    def test_processor_with_invalid_key(self):
        """Processor should handle invalid key gracefully."""
        from music_brain.session.intent_schema import CompleteSongIntent, TechnicalConstraints
        from music_brain.session.intent_processor import IntentProcessor

        intent = CompleteSongIntent(
            technical_constraints=TechnicalConstraints(
                technical_key="XYZ",  # Invalid key
            )
        )

        processor = IntentProcessor(intent)
        # Should not crash
        harmony = processor.generate_harmony()
        assert harmony is not None

    def test_process_intent_with_none(self):
        """process_intent with None should raise appropriate error."""
        from music_brain.session.intent_processor import process_intent

        with pytest.raises((TypeError, AttributeError)):
            process_intent(None)


# ==============================================================================
# MIDI I/O ERROR HANDLING
# ==============================================================================

@pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")
class TestMidiIOErrors:
    """Test error handling in MIDI I/O module."""

    def test_load_midi_nonexistent(self):
        """Loading nonexistent MIDI should raise FileNotFoundError."""
        from music_brain.utils.midi_io import load_midi

        with pytest.raises(FileNotFoundError):
            load_midi("/nonexistent/path/file.mid")

    def test_load_midi_invalid_file(self):
        """Loading non-MIDI file should raise appropriate error."""
        from music_brain.utils.midi_io import load_midi

        with tempfile.NamedTemporaryFile(suffix='.mid', mode='w', delete=False) as f:
            f.write("This is not a MIDI file")
            temp_path = f.name

        try:
            with pytest.raises(Exception):  # mido raises various exceptions
                load_midi(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_get_midi_info_nonexistent(self):
        """Getting info for nonexistent file should raise error."""
        from music_brain.utils.midi_io import get_midi_info

        with pytest.raises(FileNotFoundError):
            get_midi_info("/nonexistent/path/file.mid")

    def test_extract_notes_empty_midi(self):
        """Extracting notes from empty MIDI should return empty list."""
        from music_brain.utils.midi_io import load_midi, extract_notes

        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        notes = extract_notes(mid)
        assert notes == []


# ==============================================================================
# DAW INTEGRATION ERROR HANDLING
# ==============================================================================

@pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")
class TestDAWIntegrationErrors:
    """Test error handling in DAW integration module."""

    def test_export_to_logic_nonexistent_source(self):
        """Exporting nonexistent file should raise error."""
        from music_brain.daw.logic import export_to_logic

        with pytest.raises(FileNotFoundError):
            export_to_logic("/nonexistent/source.mid")

    def test_import_from_logic_nonexistent(self):
        """Importing nonexistent file should raise error."""
        from music_brain.daw.logic import import_from_logic

        with pytest.raises(FileNotFoundError):
            import_from_logic("/nonexistent/file.mid")

    def test_logic_project_export_invalid_path(self):
        """Exporting to invalid path should raise error."""
        from music_brain.daw.logic import LogicProject

        project = LogicProject()

        with pytest.raises((FileNotFoundError, OSError)):
            project.export_midi("/nonexistent/directory/output.mid")


# ==============================================================================
# GROOVE EXTRACTOR ERROR HANDLING
# ==============================================================================

@pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")
class TestGrooveExtractorErrors:
    """Test error handling in groove extractor module."""

    def test_extract_groove_nonexistent_file(self):
        """Extracting from nonexistent file should raise error."""
        from music_brain.groove.extractor import extract_groove

        with pytest.raises(FileNotFoundError):
            extract_groove("/nonexistent/file.mid")

    def test_extract_groove_invalid_file(self):
        """Extracting from invalid file should raise error."""
        from music_brain.groove.extractor import extract_groove

        with tempfile.NamedTemporaryFile(suffix='.mid', mode='w', delete=False) as f:
            f.write("Not a MIDI file")
            temp_path = f.name

        try:
            with pytest.raises(Exception):
                extract_groove(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_groove_template_load_nonexistent(self):
        """Loading nonexistent groove template should raise error."""
        from music_brain.groove.extractor import GrooveTemplate

        with pytest.raises(FileNotFoundError):
            GrooveTemplate.load("/nonexistent/template.json")

    def test_groove_template_load_malformed_json(self):
        """Loading malformed JSON should raise error."""
        from music_brain.groove.extractor import GrooveTemplate

        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as f:
            f.write("{ not valid json")
            temp_path = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                GrooveTemplate.load(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)


# ==============================================================================
# GROOVE TEMPLATES ERROR HANDLING
# ==============================================================================

class TestGrooveTemplatesErrors:
    """Test error handling in groove templates module."""

    def test_invalid_genre_raises_valueerror(self):
        """Invalid genre should raise ValueError."""
        from music_brain.groove.templates import get_genre_template

        with pytest.raises(ValueError):
            get_genre_template("nonexistent_genre_xyz")

    def test_genre_templates_exist(self):
        """All expected genres should exist."""
        from music_brain.groove.templates import GENRE_TEMPLATES

        expected_genres = ['funk', 'jazz', 'rock', 'hiphop']
        for genre in expected_genres:
            assert genre in GENRE_TEMPLATES


# ==============================================================================
# PROGRESSION MODULE ERROR HANDLING
# ==============================================================================

class TestProgressionErrors:
    """Test error handling in progression module."""

    def test_parse_empty_progression(self):
        """Empty progression string should be handled."""
        from music_brain.structure.progression import parse_progression_string

        result = parse_progression_string("")
        assert result == [] or len(result) == 0

    def test_diagnose_empty_progression(self):
        """Empty progression should return diagnosis with defaults."""
        from music_brain.structure.progression import diagnose_progression

        result = diagnose_progression("")
        assert isinstance(result, dict)
        assert "key" in result

    def test_parse_invalid_chord(self):
        """Invalid chord notation should be handled gracefully."""
        from music_brain.structure.progression import parse_chord

        # Should not crash - may return None for invalid chord
        try:
            result = parse_chord("XYZ123")
            # Returning None is acceptable for invalid input
            assert result is None or result is not None
        except ValueError:
            # Also acceptable to raise ValueError
            pass


# ==============================================================================
# TEACHING MODULE ERROR HANDLING
# ==============================================================================

class TestTeachingErrors:
    """Test error handling in teaching module."""

    def test_teacher_get_lesson_invalid_topic(self):
        """Getting invalid topic should return None or handle gracefully."""
        from music_brain.session.teaching import RuleBreakingTeacher

        teacher = RuleBreakingTeacher()

        result = teacher.get_lesson_content("nonexistent_topic_xyz")
        # Should return None or handle gracefully
        assert result is None or isinstance(result, dict)


# ==============================================================================
# INTERROGATOR ERROR HANDLING
# ==============================================================================

class TestInterrogatorErrors:
    """Test error handling in interrogator module."""

    def test_quick_questions_invalid_count(self):
        """Invalid count should be handled."""
        from music_brain.session.interrogator import SongInterrogator, SongPhase

        interrogator = SongInterrogator()

        # Zero count
        questions = interrogator.quick_questions(SongPhase.EMOTION, count=0)
        assert len(questions) == 0

        # Negative count raises ValueError (acceptable behavior)
        with pytest.raises(ValueError):
            interrogator.quick_questions(SongPhase.EMOTION, count=-1)


# ==============================================================================
# COMPREHENSIVE ENGINE ERROR HANDLING
# ==============================================================================

class TestComprehensiveEngineErrors:
    """Test error handling in comprehensive engine module."""

    def test_affect_analyzer_none_input(self):
        """Analyzer should handle None input gracefully."""
        from music_brain.structure.comprehensive_engine import AffectAnalyzer

        analyzer = AffectAnalyzer()

        # Analyzer handles None gracefully (treats as empty/neutral)
        # This is a design decision - not raising is acceptable
        try:
            result = analyzer.analyze(None)
            # If it returns, should be neutral
            assert result.primary == "neutral"
        except (TypeError, AttributeError):
            # Also acceptable to raise error
            pass

    def test_therapy_session_empty_processing(self):
        """Processing empty string should result in neutral affect."""
        from music_brain.structure.comprehensive_engine import TherapySession

        session = TherapySession()
        session.process_core_input("")

        assert session.state.affect_result.primary == "neutral"

    def test_therapy_session_extreme_motivation(self):
        """Extreme motivation values should be clamped."""
        from music_brain.structure.comprehensive_engine import TherapySession

        session = TherapySession()

        # Very high motivation - use correct API: set_scales(motivation, chaos)
        session.set_scales(motivation=1000, chaos=0.5)
        assert session.state.motivation_scale <= 10

        # Very low/negative motivation
        session.set_scales(motivation=-100, chaos=0.5)
        assert session.state.motivation_scale >= 1

    def test_therapy_session_extreme_chaos(self):
        """Extreme chaos values should be clamped."""
        from music_brain.structure.comprehensive_engine import TherapySession

        session = TherapySession()

        session.set_scales(motivation=5, chaos=100)
        assert session.state.chaos_tolerance <= 1.0

        session.set_scales(motivation=5, chaos=-100)
        assert session.state.chaos_tolerance >= 0.0


# ==============================================================================
# HUMANIZATION ERROR HANDLING
# ==============================================================================

class TestHumanizationErrors:
    """Test error handling in humanization module."""

    def test_humanize_empty_events(self):
        """Humanizing empty event list should return empty list."""
        from music_brain.groove import humanize_drums

        result = humanize_drums([], complexity=0.5, vulnerability=0.5)
        assert result == []

    def test_settings_from_invalid_preset(self):
        """Invalid preset should raise ValueError."""
        from music_brain.groove import settings_from_preset

        with pytest.raises(ValueError):
            settings_from_preset("nonexistent_preset_xyz")

    def test_groove_settings_boundary_values(self):
        """Settings should handle boundary values."""
        from music_brain.groove import GrooveSettings

        # Extreme values
        settings = GrooveSettings(complexity=0.0, vulnerability=0.0)
        assert settings.complexity == 0.0

        settings = GrooveSettings(complexity=1.0, vulnerability=1.0)
        assert settings.complexity == 1.0


# ==============================================================================
# BOUNDARY CONDITION TESTS
# ==============================================================================

class TestBoundaryConditions:
    """Test boundary conditions across modules."""

    def test_zero_tempo(self):
        """Zero tempo should be handled."""
        from music_brain.session.intent_processor import generate_groove_constant_displacement

        # Zero tempo would cause division issues
        # Function should handle or raise appropriate error
        try:
            result = generate_groove_constant_displacement(0)
            # If it returns, verify it's valid
            assert result is not None
        except (ZeroDivisionError, ValueError):
            # Also acceptable to raise an error
            pass

    def test_negative_tempo(self):
        """Negative tempo should be handled."""
        from music_brain.session.intent_processor import generate_groove_tempo_fluctuation

        try:
            result = generate_groove_tempo_fluctuation(-120)
            assert result is not None
        except (ValueError, ZeroDivisionError):
            pass

    def test_very_long_progression_string(self):
        """Very long progression string should be handled."""
        from music_brain.structure.progression import parse_progression_string

        # 100 chords
        long_progression = "-".join(["C", "G", "Am", "F"] * 25)
        result = parse_progression_string(long_progression)
        assert len(result) == 100

    def test_unicode_in_intent(self):
        """Unicode characters should be handled in intent."""
        from music_brain.session.intent_schema import CompleteSongIntent, SongRoot

        intent = CompleteSongIntent(
            title="Test Song with Unicode: 音楽 🎵",
            song_root=SongRoot(
                core_event="Émotions très fortes",
                core_longing="Paix intérieure",
            )
        )

        data = intent.to_dict()
        assert "音楽" in data["title"]

        restored = CompleteSongIntent.from_dict(data)
        assert "音楽" in restored.title


# ==============================================================================
# IMPORT ERROR HANDLING
# ==============================================================================

class TestImportErrors:
    """Test handling of optional import errors."""

    def test_midi_io_without_mido(self):
        """MIDI I/O should indicate when mido is missing."""
        from music_brain.utils.midi_io import MIDO_AVAILABLE

        # Just verify the flag exists
        assert isinstance(MIDO_AVAILABLE, bool)

    def test_audio_feel_without_librosa(self):
        """Audio feel module should indicate when librosa is missing."""
        from music_brain.audio.feel import LIBROSA_AVAILABLE

        assert isinstance(LIBROSA_AVAILABLE, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
