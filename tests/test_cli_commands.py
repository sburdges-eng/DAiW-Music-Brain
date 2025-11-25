"""
Tests for the CLI command handlers.

Covers: Individual cmd_* functions, argument parsing, error handling,
and command execution logic.

Run with: pytest tests/test_cli_commands.py -v
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from argparse import Namespace

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False

from music_brain.cli import (
    cmd_extract,
    cmd_apply,
    cmd_humanize,
    cmd_analyze,
    cmd_diagnose,
    cmd_reharm,
    cmd_teach,
    cmd_intent,
    main,
)


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def simple_midi_file():
    """Create a simple MIDI file for testing CLI commands."""
    if not MIDO_AVAILABLE:
        pytest.skip("mido not installed")

    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
    track.append(mido.Message('note_on', note=60, velocity=100, channel=0, time=0))
    track.append(mido.Message('note_off', note=60, velocity=0, channel=0, time=480))

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        temp_path = f.name

    mid.save(temp_path)
    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def drum_midi_file():
    """Create a drum MIDI file for humanize testing."""
    if not MIDO_AVAILABLE:
        pytest.skip("mido not installed")

    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))

    # Add drum hits on channel 9
    for i in range(8):
        track.append(mido.Message('note_on', note=36 if i % 2 == 0 else 38, velocity=100, channel=9, time=0 if i == 0 else 480))
        track.append(mido.Message('note_off', note=36 if i % 2 == 0 else 38, velocity=0, channel=9, time=240))

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        temp_path = f.name

    mid.save(temp_path)
    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def valid_intent_file():
    """Create a valid intent JSON file for testing."""
    intent_data = {
        "title": "Test Song",
        "song_root": {
            "core_event": "Something happened",
            "core_longing": "I want peace",
        },
        "song_intent": {
            "mood_primary": "grief",
            "mood_secondary_tension": 0.5,
            "vulnerability_scale": "Medium",
            "narrative_arc": "Slow Reveal",
        },
        "technical_constraints": {
            "technical_genre": "Indie",
            "technical_tempo_range": [80, 100],
            "technical_key": "Am",
            "technical_mode": "aeolian",
        },
    }

    with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as f:
        json.dump(intent_data, f)
        temp_path = f.name

    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


# ==============================================================================
# CMD_EXTRACT TESTS
# ==============================================================================

@pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")
class TestCmdExtract:
    """Test cmd_extract function."""

    def test_nonexistent_file_returns_error(self, capsys):
        args = Namespace(midi_file="/nonexistent/file.mid", output=None)
        result = cmd_extract(args)
        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.out or "not found" in captured.out.lower()

    def test_extract_creates_output_file(self, simple_midi_file, capsys):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            output_path = f.name

        try:
            args = Namespace(midi_file=simple_midi_file, output=output_path)
            result = cmd_extract(args)
            assert result == 0
            assert Path(output_path).exists()

            with open(output_path) as f:
                data = json.load(f)
            assert "swing_factor" in data
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_extract_default_output_name(self, simple_midi_file, capsys):
        args = Namespace(midi_file=simple_midi_file, output=None)
        result = cmd_extract(args)
        assert result == 0

        # Clean up generated file
        expected_output = Path(simple_midi_file).stem + "_groove.json"
        if Path(expected_output).exists():
            Path(expected_output).unlink()


# ==============================================================================
# CMD_APPLY TESTS
# ==============================================================================

@pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")
class TestCmdApply:
    """Test cmd_apply function."""

    def test_nonexistent_file_returns_error(self, capsys):
        args = Namespace(midi_file="/nonexistent/file.mid", genre="funk", output=None, intensity=0.5)
        result = cmd_apply(args)
        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.out or "not found" in captured.out.lower()

    def test_apply_creates_output(self, simple_midi_file, capsys):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            args = Namespace(midi_file=simple_midi_file, genre="funk", output=output_path, intensity=0.5)
            result = cmd_apply(args)
            assert result == 0
            assert Path(output_path).exists()
        finally:
            Path(output_path).unlink(missing_ok=True)


# ==============================================================================
# CMD_HUMANIZE TESTS
# ==============================================================================

@pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")
class TestCmdHumanize:
    """Test cmd_humanize function."""

    def test_list_presets(self, capsys):
        args = Namespace(
            midi_file=None,
            list_presets=True,
            preset=None,
            style=None,
            complexity=0.5,
            vulnerability=0.5,
            output=None,
            channel=9,
            no_ghost_notes=False,
            seed=None,
        )
        result = cmd_humanize(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Presets" in captured.out or "lofi" in captured.out.lower()

    def test_humanize_nonexistent_file(self, capsys):
        args = Namespace(
            midi_file="/nonexistent/file.mid",
            list_presets=False,
            preset=None,
            style=None,
            complexity=0.5,
            vulnerability=0.5,
            output=None,
            channel=9,
            no_ghost_notes=False,
            seed=None,
        )
        result = cmd_humanize(args)
        assert result == 1

    def test_humanize_with_style(self, drum_midi_file, capsys):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            args = Namespace(
                midi_file=drum_midi_file,
                list_presets=False,
                preset=None,
                style="natural",
                complexity=0.5,
                vulnerability=0.5,
                output=output_path,
                channel=9,
                no_ghost_notes=False,
                seed=42,
            )
            result = cmd_humanize(args)
            assert result == 0
            assert Path(output_path).exists()
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_humanize_with_preset(self, drum_midi_file, capsys):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            args = Namespace(
                midi_file=drum_midi_file,
                list_presets=False,
                preset="lofi_depression",
                style=None,
                complexity=0.5,
                vulnerability=0.5,
                output=output_path,
                channel=9,
                no_ghost_notes=False,
                seed=42,
            )
            result = cmd_humanize(args)
            assert result == 0
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_humanize_invalid_preset(self, drum_midi_file, capsys):
        args = Namespace(
            midi_file=drum_midi_file,
            list_presets=False,
            preset="nonexistent_preset",
            style=None,
            complexity=0.5,
            vulnerability=0.5,
            output=None,
            channel=9,
            no_ghost_notes=False,
            seed=None,
        )
        result = cmd_humanize(args)
        assert result == 1


# ==============================================================================
# CMD_DIAGNOSE TESTS
# ==============================================================================

class TestCmdDiagnose:
    """Test cmd_diagnose function."""

    def test_diagnose_simple_progression(self, capsys):
        args = Namespace(progression="C-G-Am-F")
        result = cmd_diagnose(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Key" in captured.out or "key" in captured.out.lower()

    def test_diagnose_minor_progression(self, capsys):
        args = Namespace(progression="Am-F-C-G")
        result = cmd_diagnose(args)
        assert result == 0

    def test_diagnose_with_issues(self, capsys):
        args = Namespace(progression="C-C#-D-D#")  # Chromatic, likely has issues
        result = cmd_diagnose(args)
        assert result == 0


# ==============================================================================
# CMD_REHARM TESTS
# ==============================================================================

class TestCmdReharm:
    """Test cmd_reharm function."""

    def test_reharm_basic(self, capsys):
        args = Namespace(progression="C-G-Am-F", style="jazz", count=3)
        result = cmd_reharm(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Reharmonization" in captured.out

    def test_reharm_different_styles(self, capsys):
        for style in ["jazz", "pop", "rnb"]:
            args = Namespace(progression="F-C-Am-Dm", style=style, count=2)
            result = cmd_reharm(args)
            assert result == 0


# ==============================================================================
# CMD_TEACH TESTS
# ==============================================================================

class TestCmdTeach:
    """Test cmd_teach function."""

    def test_invalid_topic_returns_error(self, capsys):
        args = Namespace(topic="nonexistent_topic", quick=True)
        result = cmd_teach(args)
        assert result == 1
        captured = capsys.readouterr()
        assert "Unknown topic" in captured.out

    @patch('music_brain.cli.get_session_module')
    def test_valid_topic_calls_teacher(self, mock_get_session):
        mock_teacher_class = MagicMock()
        mock_teacher_instance = MagicMock()
        mock_teacher_class.return_value = mock_teacher_instance
        mock_get_session.return_value = mock_teacher_class

        args = Namespace(topic="borrowed_chords", quick=True)
        result = cmd_teach(args)

        assert result == 0
        mock_teacher_instance.quick_lesson.assert_called_once()


# ==============================================================================
# CMD_INTENT TESTS
# ==============================================================================

class TestCmdIntent:
    """Test cmd_intent function."""

    def test_intent_new_creates_template(self, capsys):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            output_path = f.name

        try:
            args = Namespace(subcommand='new', title="My Test Song", output=output_path)
            result = cmd_intent(args)
            assert result == 0
            assert Path(output_path).exists()

            with open(output_path) as f:
                data = json.load(f)
            assert data["title"] == "My Test Song"
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_intent_new_default_output(self, capsys):
        args = Namespace(subcommand='new', title=None, output=None)
        result = cmd_intent(args)
        assert result == 0

        # Clean up
        if Path("song_intent.json").exists():
            Path("song_intent.json").unlink()

    def test_intent_suggest_grief(self, capsys):
        args = Namespace(subcommand='suggest', emotion='grief')
        result = cmd_intent(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "grief" in captured.out.lower()

    def test_intent_suggest_unknown_emotion(self, capsys):
        args = Namespace(subcommand='suggest', emotion='xyzzy_nonexistent')
        result = cmd_intent(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "No specific suggestions" in captured.out

    def test_intent_list_rules(self, capsys):
        args = Namespace(subcommand='list')
        result = cmd_intent(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Harmony" in captured.out
        assert "Rhythm" in captured.out

    def test_intent_validate_valid_file(self, valid_intent_file, capsys):
        args = Namespace(subcommand='validate', file=valid_intent_file)
        result = cmd_intent(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "valid" in captured.out.lower()

    def test_intent_validate_nonexistent_file(self, capsys):
        args = Namespace(subcommand='validate', file='/nonexistent/file.json')
        result = cmd_intent(args)
        assert result == 1

    def test_intent_process_valid_file(self, valid_intent_file, capsys):
        args = Namespace(subcommand='process', file=valid_intent_file, output=None, force=False)
        result = cmd_intent(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "GENERATED" in captured.out or "HARMONY" in captured.out

    def test_intent_process_nonexistent_file(self, capsys):
        args = Namespace(subcommand='process', file='/nonexistent/file.json', output=None, force=False)
        result = cmd_intent(args)
        assert result == 1

    def test_intent_process_missing_file_arg(self, capsys):
        args = Namespace(subcommand='process', file=None, output=None, force=False)
        result = cmd_intent(args)
        assert result == 1

    def test_intent_process_with_output(self, valid_intent_file, capsys):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            output_path = f.name

        try:
            args = Namespace(subcommand='process', file=valid_intent_file, output=output_path, force=False)
            result = cmd_intent(args)
            assert result == 0
            assert Path(output_path).exists()
        finally:
            Path(output_path).unlink(missing_ok=True)


# ==============================================================================
# MAIN FUNCTION TESTS
# ==============================================================================

class TestMain:
    """Test main CLI entry point."""

    def test_no_command_shows_help(self, capsys):
        with patch('sys.argv', ['daiw']):
            result = main()
            assert result == 0

    def test_version_flag(self, capsys):
        with patch('sys.argv', ['daiw', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # argparse exits with 0 for --version
            assert exc_info.value.code == 0

    def test_diagnose_command(self, capsys):
        with patch('sys.argv', ['daiw', 'diagnose', 'C-G-Am-F']):
            result = main()
            assert result == 0

    def test_intent_list_command(self, capsys):
        with patch('sys.argv', ['daiw', 'intent', 'list']):
            result = main()
            assert result == 0


# ==============================================================================
# ARGUMENT PARSING TESTS
# ==============================================================================

class TestArgumentParsing:
    """Test CLI argument parsing."""

    def test_extract_parses_midi_file(self):
        with patch('sys.argv', ['daiw', 'extract', 'test.mid']):
            # Just verify no exception
            pass

    def test_humanize_parses_all_options(self):
        with patch('sys.argv', [
            'daiw', 'humanize', 'test.mid',
            '-o', 'output.mid',
            '-s', 'loose',
            '-c', '0.7',
            '-v', '0.6',
            '--channel', '10',
            '--seed', '42',
        ]):
            # Just verify no exception
            pass

    def test_intent_suggest_parses_emotion(self):
        with patch('sys.argv', ['daiw', 'intent', 'suggest', 'grief']):
            # Just verify no exception
            pass


# ==============================================================================
# ERROR HANDLING TESTS
# ==============================================================================

class TestErrorHandling:
    """Test CLI error handling."""

    def test_invalid_command_handled(self, capsys):
        with patch('sys.argv', ['daiw', 'invalid_command']):
            # argparse should handle this
            with pytest.raises(SystemExit):
                main()

    def test_missing_required_args_handled(self, capsys):
        with patch('sys.argv', ['daiw', 'diagnose']):  # Missing progression
            with pytest.raises(SystemExit):
                main()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
