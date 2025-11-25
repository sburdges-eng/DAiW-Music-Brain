"""
Tests for the DAW integration module (Logic Pro utilities).

Covers: LogicProject class, export_to_logic, import_from_logic,
create_logic_template, and MIDI export functionality.

Run with: pytest tests/test_daw_integration.py -v
"""

import pytest
import tempfile
from pathlib import Path

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False

from music_brain.daw.logic import (
    LogicProject,
    export_to_logic,
    import_from_logic,
    create_logic_template,
    LOGIC_PPQ,
    LOGIC_CHANNELS,
    MIDO_AVAILABLE as MODULE_MIDO_AVAILABLE,
)


# Skip all tests if mido not available
pytestmark = pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")


# ==============================================================================
# CONSTANTS TESTS
# ==============================================================================

class TestConstants:
    """Test module constants."""

    def test_logic_ppq(self):
        assert LOGIC_PPQ == 480

    def test_logic_channels(self):
        assert LOGIC_CHANNELS["drums"] == 10
        assert LOGIC_CHANNELS["bass"] == 1
        assert LOGIC_CHANNELS["keys"] == 2


# ==============================================================================
# LOGIC PROJECT CLASS TESTS
# ==============================================================================

class TestLogicProject:
    """Test LogicProject class."""

    def test_default_initialization(self):
        project = LogicProject()
        assert project.name == "Untitled"
        assert project.tempo_bpm == 120.0
        assert project.time_signature == (4, 4)
        assert project.ppq == 480
        assert project.tracks == []

    def test_custom_initialization(self):
        project = LogicProject(
            name="My Song",
            tempo_bpm=100.0,
            time_signature=(3, 4),
            key="Am",
            mode="aeolian",
            genre="Jazz",
        )
        assert project.name == "My Song"
        assert project.tempo_bpm == 100.0
        assert project.time_signature == (3, 4)
        assert project.key == "Am"
        assert project.mode == "aeolian"
        assert project.genre == "Jazz"

    def test_add_track_basic(self):
        project = LogicProject()
        project.add_track(name="Piano", channel=1)

        assert len(project.tracks) == 1
        assert project.tracks[0]["name"] == "Piano"
        assert project.tracks[0]["channel"] == 0  # Converted to 0-indexed

    def test_add_track_with_instrument(self):
        project = LogicProject()
        project.add_track(name="Strings", channel=3, instrument=48)

        assert project.tracks[0]["instrument"] == 48

    def test_add_track_with_notes(self):
        project = LogicProject()
        notes = [
            {"pitch": 60, "velocity": 100, "start_tick": 0, "duration_ticks": 480},
            {"pitch": 62, "velocity": 90, "start_tick": 480, "duration_ticks": 480},
        ]
        project.add_track(name="Melody", channel=1, notes=notes)

        assert len(project.tracks[0]["notes"]) == 2
        assert project.tracks[0]["notes"][0]["pitch"] == 60

    def test_add_multiple_tracks(self):
        project = LogicProject()
        project.add_track(name="Drums", channel=10)
        project.add_track(name="Bass", channel=1)
        project.add_track(name="Keys", channel=2)

        assert len(project.tracks) == 3

    def test_channel_conversion_to_zero_indexed(self):
        """MIDI channels are 1-16 in user input but 0-15 internally."""
        project = LogicProject()
        project.add_track(name="Test", channel=10)  # Drums channel

        assert project.tracks[0]["channel"] == 9  # 0-indexed


class TestLogicProjectExport:
    """Test LogicProject export_midi method."""

    @pytest.fixture
    def project_with_notes(self):
        """Create a project with some notes for testing."""
        project = LogicProject(name="Test Song", tempo_bpm=120.0)
        notes = [
            {"pitch": 60, "velocity": 100, "start_tick": 0, "duration_ticks": 480},
            {"pitch": 64, "velocity": 90, "start_tick": 480, "duration_ticks": 480},
            {"pitch": 67, "velocity": 80, "start_tick": 960, "duration_ticks": 480},
        ]
        project.add_track(name="Melody", channel=1, instrument=0, notes=notes)
        return project

    def test_export_creates_file(self, project_with_notes):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            result = project_with_notes.export_midi(temp_path)
            assert Path(result).exists()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_export_returns_path(self, project_with_notes):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            result = project_with_notes.export_midi(temp_path)
            assert result == temp_path
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_exported_file_is_valid_midi(self, project_with_notes):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            project_with_notes.export_midi(temp_path)
            mid = mido.MidiFile(temp_path)
            assert mid.ticks_per_beat == 480
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_exported_has_tempo(self, project_with_notes):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            project_with_notes.export_midi(temp_path)
            mid = mido.MidiFile(temp_path)

            # Find tempo message
            tempo_found = False
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'set_tempo':
                        tempo_found = True
                        # 120 BPM = 500000 microseconds per beat
                        assert msg.tempo == 500000

            assert tempo_found
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_exported_has_time_signature(self, project_with_notes):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            project_with_notes.export_midi(temp_path)
            mid = mido.MidiFile(temp_path)

            # Find time signature message
            time_sig_found = False
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'time_signature':
                        time_sig_found = True
                        assert msg.numerator == 4
                        assert msg.denominator == 4

            assert time_sig_found
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_exported_has_notes(self, project_with_notes):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            project_with_notes.export_midi(temp_path)
            mid = mido.MidiFile(temp_path)

            # Count note_on messages
            note_on_count = 0
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'note_on' and msg.velocity > 0:
                        note_on_count += 1

            assert note_on_count == 3
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_exported_has_track_names(self, project_with_notes):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            project_with_notes.export_midi(temp_path)
            mid = mido.MidiFile(temp_path)

            # Find track name
            track_names = []
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'track_name':
                        track_names.append(msg.name)

            assert "Melody" in track_names
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_exported_has_program_change(self, project_with_notes):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            project_with_notes.export_midi(temp_path)
            mid = mido.MidiFile(temp_path)

            # Find program change
            program_found = False
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'program_change':
                        program_found = True
                        assert msg.program == 0  # Piano

            assert program_found
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_export_empty_project(self):
        """Empty project should still create valid MIDI."""
        project = LogicProject(name="Empty")

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            project.export_midi(temp_path)
            mid = mido.MidiFile(temp_path)
            assert mid.ticks_per_beat == 480
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_export_different_time_signature(self):
        project = LogicProject(name="Waltz", time_signature=(3, 4))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            project.export_midi(temp_path)
            mid = mido.MidiFile(temp_path)

            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'time_signature':
                        assert msg.numerator == 3
                        assert msg.denominator == 4
        finally:
            Path(temp_path).unlink(missing_ok=True)


# ==============================================================================
# EXPORT_TO_LOGIC TESTS
# ==============================================================================

class TestExportToLogic:
    """Test export_to_logic function."""

    @pytest.fixture
    def source_midi(self):
        """Create a source MIDI file with non-Logic PPQ."""
        mid = mido.MidiFile(ticks_per_beat=960)  # Not 480

        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
        track.append(mido.Message('note_on', note=60, velocity=100, channel=0, time=0))
        track.append(mido.Message('note_off', note=60, velocity=0, channel=0, time=960))
        track.append(mido.MetaMessage('end_of_track', time=0))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        mid.save(temp_path)
        yield temp_path

        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def logic_ppq_midi(self):
        """Create a MIDI file already at Logic's PPQ."""
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

    def test_normalizes_ppq_to_480(self, source_midi):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            result = export_to_logic(source_midi, output_path)
            mid = mido.MidiFile(result)
            assert mid.ticks_per_beat == 480
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_returns_output_path(self, source_midi):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            result = export_to_logic(source_midi, output_path)
            assert result == output_path
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_default_output_path(self, source_midi):
        """Without output_path, should create _logic.mid file."""
        try:
            result = export_to_logic(source_midi)
            expected_name = Path(source_midi).stem + "_logic.mid"
            assert expected_name in result
        finally:
            # Clean up generated file
            if Path(result).exists():
                Path(result).unlink()

    def test_already_480_ppq(self, logic_ppq_midi):
        """File already at 480 PPQ should still be processed."""
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            result = export_to_logic(logic_ppq_midi, output_path)
            mid = mido.MidiFile(result)
            assert mid.ticks_per_beat == 480
        finally:
            Path(output_path).unlink(missing_ok=True)


# ==============================================================================
# IMPORT_FROM_LOGIC TESTS
# ==============================================================================

class TestImportFromLogic:
    """Test import_from_logic function."""

    @pytest.fixture
    def logic_export_file(self):
        """Create a MIDI file simulating Logic Pro export."""
        mid = mido.MidiFile(ticks_per_beat=480)

        # Meta track
        track0 = mido.MidiTrack()
        mid.tracks.append(track0)
        track0.append(mido.MetaMessage('set_tempo', tempo=600000, time=0))  # 100 BPM
        track0.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))

        # Melody track
        track1 = mido.MidiTrack()
        mid.tracks.append(track1)
        track1.append(mido.MetaMessage('track_name', name='Melody', time=0))
        track1.append(mido.Message('program_change', channel=0, program=40, time=0))
        track1.append(mido.Message('note_on', note=60, velocity=100, channel=0, time=0))
        track1.append(mido.Message('note_off', note=60, velocity=0, channel=0, time=480))
        track1.append(mido.Message('note_on', note=62, velocity=90, channel=0, time=0))
        track1.append(mido.Message('note_off', note=62, velocity=0, channel=0, time=480))

        # Bass track
        track2 = mido.MidiTrack()
        mid.tracks.append(track2)
        track2.append(mido.MetaMessage('track_name', name='Bass', time=0))
        track2.append(mido.Message('program_change', channel=1, program=33, time=0))
        track2.append(mido.Message('note_on', note=36, velocity=110, channel=1, time=0))
        track2.append(mido.Message('note_off', note=36, velocity=0, channel=1, time=960))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        mid.save(temp_path)
        yield temp_path

        Path(temp_path).unlink(missing_ok=True)

    def test_returns_logic_project(self, logic_export_file):
        project = import_from_logic(logic_export_file)
        assert isinstance(project, LogicProject)

    def test_extracts_tempo(self, logic_export_file):
        project = import_from_logic(logic_export_file)
        assert project.tempo_bpm == 100.0

    def test_extracts_time_signature(self, logic_export_file):
        project = import_from_logic(logic_export_file)
        assert project.time_signature == (4, 4)

    def test_extracts_ppq(self, logic_export_file):
        project = import_from_logic(logic_export_file)
        assert project.ppq == 480

    def test_extracts_tracks(self, logic_export_file):
        project = import_from_logic(logic_export_file)
        # Should have tracks with notes (meta track may be empty)
        tracks_with_notes = [t for t in project.tracks if t["notes"]]
        assert len(tracks_with_notes) >= 2

    def test_extracts_track_names(self, logic_export_file):
        project = import_from_logic(logic_export_file)
        track_names = [t["name"] for t in project.tracks]
        assert "Melody" in track_names or any("Melody" in n for n in track_names)

    def test_extracts_notes(self, logic_export_file):
        project = import_from_logic(logic_export_file)

        # Find melody track
        melody_track = None
        for track in project.tracks:
            if "Melody" in track["name"]:
                melody_track = track
                break

        if melody_track:
            assert len(melody_track["notes"]) == 2

    def test_uses_filename_as_name(self, logic_export_file):
        project = import_from_logic(logic_export_file)
        expected_name = Path(logic_export_file).stem
        assert project.name == expected_name


# ==============================================================================
# CREATE_LOGIC_TEMPLATE TESTS
# ==============================================================================

class TestCreateLogicTemplate:
    """Test create_logic_template function."""

    def test_returns_logic_project(self):
        project = create_logic_template("My Song")
        assert isinstance(project, LogicProject)

    def test_sets_name(self):
        project = create_logic_template("Test Project")
        assert project.name == "Test Project"

    def test_sets_tempo(self):
        project = create_logic_template("Test", tempo=140.0)
        assert project.tempo_bpm == 140.0

    def test_default_tracks(self):
        project = create_logic_template("Test")
        track_names = [t["name"] for t in project.tracks]

        # Should have default tracks
        assert "Drums" in track_names
        assert "Bass" in track_names
        assert "Keys" in track_names

    def test_custom_tracks(self):
        project = create_logic_template("Test", tracks=["Lead", "Pad", "FX"])
        track_names = [t["name"] for t in project.tracks]

        assert "Lead" in track_names
        assert "Pad" in track_names
        assert "FX" in track_names
        assert "Drums" not in track_names  # Custom tracks replace defaults

    def test_drums_on_channel_10(self):
        project = create_logic_template("Test")

        drums_track = None
        for track in project.tracks:
            if track["name"] == "Drums":
                drums_track = track
                break

        if drums_track:
            # Channel is 0-indexed internally, so 10 becomes 9
            assert drums_track["channel"] == 9

    def test_bars_parameter(self):
        """bars parameter doesn't affect the project directly but is accepted."""
        project = create_logic_template("Test", bars=16)
        assert project is not None


# ==============================================================================
# ROUNDTRIP TESTS
# ==============================================================================

class TestRoundtrip:
    """Test export -> import roundtrip."""

    def test_export_import_preserves_tempo(self):
        project = LogicProject(name="Roundtrip", tempo_bpm=95.0)
        project.add_track(
            name="Test",
            channel=1,
            notes=[{"pitch": 60, "velocity": 100, "start_tick": 0, "duration_ticks": 480}]
        )

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            project.export_midi(temp_path)
            imported = import_from_logic(temp_path)

            # Tempo might have slight floating point differences
            assert abs(imported.tempo_bpm - 95.0) < 1.0
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_export_import_preserves_notes(self):
        project = LogicProject(name="Roundtrip")
        original_notes = [
            {"pitch": 60, "velocity": 100, "start_tick": 0, "duration_ticks": 480},
            {"pitch": 64, "velocity": 90, "start_tick": 480, "duration_ticks": 240},
        ]
        project.add_track(name="Test", channel=1, notes=original_notes)

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            project.export_midi(temp_path)
            imported = import_from_logic(temp_path)

            # Find the track with notes
            imported_notes = None
            for track in imported.tracks:
                if track["notes"]:
                    imported_notes = track["notes"]
                    break

            assert imported_notes is not None
            assert len(imported_notes) == 2
        finally:
            Path(temp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
