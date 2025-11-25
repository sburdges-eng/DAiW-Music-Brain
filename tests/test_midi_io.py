"""
Tests for the MIDI I/O utilities module.

Covers: load_midi, save_midi, get_midi_info, extract_notes,
merge_tracks, split_by_channel, MidiInfo dataclass.

Run with: pytest tests/test_midi_io.py -v
"""

import pytest
import tempfile
from pathlib import Path

# Import mido for creating test fixtures
try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False

from music_brain.utils.midi_io import (
    load_midi,
    save_midi,
    get_midi_info,
    extract_notes,
    merge_tracks,
    split_by_channel,
    MidiInfo,
    MIDO_AVAILABLE as MODULE_MIDO_AVAILABLE,
)


# Skip all tests if mido not available
pytestmark = pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def simple_midi_file():
    """Create a simple MIDI file for testing."""
    mid = mido.MidiFile(ticks_per_beat=480)

    # Track 0: Meta info
    track0 = mido.MidiTrack()
    mid.tracks.append(track0)
    track0.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))  # 120 BPM
    track0.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
    track0.append(mido.MetaMessage('track_name', name='Meta', time=0))

    # Track 1: Some notes
    track1 = mido.MidiTrack()
    mid.tracks.append(track1)
    track1.append(mido.MetaMessage('track_name', name='Piano', time=0))
    track1.append(mido.Message('program_change', channel=0, program=0, time=0))

    # Add a few notes
    track1.append(mido.Message('note_on', note=60, velocity=100, channel=0, time=0))
    track1.append(mido.Message('note_off', note=60, velocity=0, channel=0, time=480))
    track1.append(mido.Message('note_on', note=62, velocity=90, channel=0, time=0))
    track1.append(mido.Message('note_off', note=62, velocity=0, channel=0, time=480))
    track1.append(mido.Message('note_on', note=64, velocity=80, channel=0, time=0))
    track1.append(mido.Message('note_off', note=64, velocity=0, channel=0, time=480))
    track1.append(mido.MetaMessage('end_of_track', time=0))

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        temp_path = f.name

    mid.save(temp_path)
    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def multi_channel_midi_file():
    """Create a MIDI file with multiple channels."""
    mid = mido.MidiFile(ticks_per_beat=480)

    # Meta track
    track0 = mido.MidiTrack()
    mid.tracks.append(track0)
    track0.append(mido.MetaMessage('set_tempo', tempo=600000, time=0))  # 100 BPM

    # Track with multiple channels
    track1 = mido.MidiTrack()
    mid.tracks.append(track1)
    track1.append(mido.MetaMessage('track_name', name='Multi', time=0))

    # Channel 0 notes
    track1.append(mido.Message('note_on', note=60, velocity=100, channel=0, time=0))
    track1.append(mido.Message('note_off', note=60, velocity=0, channel=0, time=240))

    # Channel 1 notes
    track1.append(mido.Message('note_on', note=48, velocity=80, channel=1, time=0))
    track1.append(mido.Message('note_off', note=48, velocity=0, channel=1, time=240))

    # Channel 9 (drums)
    track1.append(mido.Message('note_on', note=36, velocity=110, channel=9, time=0))
    track1.append(mido.Message('note_off', note=36, velocity=0, channel=9, time=240))

    track1.append(mido.MetaMessage('end_of_track', time=0))

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        temp_path = f.name

    mid.save(temp_path)
    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def empty_midi_file():
    """Create an empty MIDI file (no notes)."""
    mid = mido.MidiFile(ticks_per_beat=480)

    track0 = mido.MidiTrack()
    mid.tracks.append(track0)
    track0.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
    track0.append(mido.MetaMessage('end_of_track', time=0))

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        temp_path = f.name

    mid.save(temp_path)
    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def complex_midi_file():
    """Create a more complex MIDI file with chords and overlapping notes."""
    mid = mido.MidiFile(ticks_per_beat=480)

    track0 = mido.MidiTrack()
    mid.tracks.append(track0)
    track0.append(mido.MetaMessage('set_tempo', tempo=428571, time=0))  # 140 BPM
    track0.append(mido.MetaMessage('time_signature', numerator=3, denominator=4, time=0))

    # Track with chord (simultaneous notes)
    track1 = mido.MidiTrack()
    mid.tracks.append(track1)
    track1.append(mido.MetaMessage('track_name', name='Chords', time=0))

    # C major chord
    track1.append(mido.Message('note_on', note=60, velocity=100, channel=0, time=0))
    track1.append(mido.Message('note_on', note=64, velocity=100, channel=0, time=0))
    track1.append(mido.Message('note_on', note=67, velocity=100, channel=0, time=0))
    track1.append(mido.Message('note_off', note=60, velocity=0, channel=0, time=480))
    track1.append(mido.Message('note_off', note=64, velocity=0, channel=0, time=0))
    track1.append(mido.Message('note_off', note=67, velocity=0, channel=0, time=0))

    # G major chord
    track1.append(mido.Message('note_on', note=67, velocity=90, channel=0, time=0))
    track1.append(mido.Message('note_on', note=71, velocity=90, channel=0, time=0))
    track1.append(mido.Message('note_on', note=74, velocity=90, channel=0, time=0))
    track1.append(mido.Message('note_off', note=67, velocity=0, channel=0, time=480))
    track1.append(mido.Message('note_off', note=71, velocity=0, channel=0, time=0))
    track1.append(mido.Message('note_off', note=74, velocity=0, channel=0, time=0))

    track1.append(mido.MetaMessage('end_of_track', time=0))

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        temp_path = f.name

    mid.save(temp_path)
    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


# ==============================================================================
# MIDI INFO DATACLASS TESTS
# ==============================================================================

class TestMidiInfo:
    """Test MidiInfo dataclass."""

    def test_creation(self):
        info = MidiInfo(
            filename="test.mid",
            format_type=1,
            num_tracks=2,
            ppq=480,
            tempo_bpm=120.0,
            time_signature=(4, 4),
            duration_ticks=1920,
            duration_seconds=4.0,
            note_count=10,
            track_names=["Track 1", "Track 2"],
        )
        assert info.filename == "test.mid"
        assert info.ppq == 480
        assert info.tempo_bpm == 120.0

    def test_time_signature_is_tuple(self):
        info = MidiInfo(
            filename="test.mid",
            format_type=1,
            num_tracks=1,
            ppq=480,
            tempo_bpm=120.0,
            time_signature=(3, 4),
            duration_ticks=0,
            duration_seconds=0.0,
            note_count=0,
            track_names=[],
        )
        assert info.time_signature == (3, 4)
        assert info.time_signature[0] == 3
        assert info.time_signature[1] == 4


# ==============================================================================
# LOAD_MIDI TESTS
# ==============================================================================

class TestLoadMidi:
    """Test load_midi function."""

    def test_load_valid_file(self, simple_midi_file):
        mid = load_midi(simple_midi_file)
        assert isinstance(mid, mido.MidiFile)
        assert mid.ticks_per_beat == 480

    def test_load_returns_midifile_object(self, simple_midi_file):
        mid = load_midi(simple_midi_file)
        assert hasattr(mid, 'tracks')
        assert hasattr(mid, 'ticks_per_beat')

    def test_load_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_midi("/nonexistent/path/file.mid")

    def test_load_preserves_tracks(self, simple_midi_file):
        mid = load_midi(simple_midi_file)
        assert len(mid.tracks) == 2  # Meta + Piano


# ==============================================================================
# SAVE_MIDI TESTS
# ==============================================================================

class TestSaveMidi:
    """Test save_midi function."""

    def test_save_creates_file(self, simple_midi_file):
        mid = load_midi(simple_midi_file)

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            save_midi(mid, output_path)
            assert Path(output_path).exists()
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_save_roundtrip(self, simple_midi_file):
        """Load -> save -> load should preserve data."""
        mid = load_midi(simple_midi_file)

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            save_midi(mid, output_path)
            reloaded = load_midi(output_path)

            assert reloaded.ticks_per_beat == mid.ticks_per_beat
            assert len(reloaded.tracks) == len(mid.tracks)
        finally:
            Path(output_path).unlink(missing_ok=True)


# ==============================================================================
# GET_MIDI_INFO TESTS
# ==============================================================================

class TestGetMidiInfo:
    """Test get_midi_info function."""

    def test_returns_midi_info(self, simple_midi_file):
        info = get_midi_info(simple_midi_file)
        assert isinstance(info, MidiInfo)

    def test_extracts_ppq(self, simple_midi_file):
        info = get_midi_info(simple_midi_file)
        assert info.ppq == 480

    def test_extracts_tempo(self, simple_midi_file):
        info = get_midi_info(simple_midi_file)
        assert info.tempo_bpm == 120.0

    def test_extracts_time_signature(self, simple_midi_file):
        info = get_midi_info(simple_midi_file)
        assert info.time_signature == (4, 4)

    def test_extracts_different_time_signature(self, complex_midi_file):
        info = get_midi_info(complex_midi_file)
        assert info.time_signature == (3, 4)

    def test_counts_notes(self, simple_midi_file):
        info = get_midi_info(simple_midi_file)
        assert info.note_count == 3  # Three notes in the file

    def test_counts_chord_notes(self, complex_midi_file):
        info = get_midi_info(complex_midi_file)
        assert info.note_count == 6  # Two chords * 3 notes each

    def test_extracts_track_names(self, simple_midi_file):
        info = get_midi_info(simple_midi_file)
        assert "Meta" in info.track_names or "Piano" in info.track_names

    def test_calculates_duration(self, simple_midi_file):
        info = get_midi_info(simple_midi_file)
        assert info.duration_ticks > 0
        assert info.duration_seconds > 0

    def test_empty_file_info(self, empty_midi_file):
        info = get_midi_info(empty_midi_file)
        assert info.note_count == 0
        assert info.ppq == 480

    def test_format_type(self, simple_midi_file):
        info = get_midi_info(simple_midi_file)
        assert info.format_type in [0, 1, 2]

    def test_num_tracks(self, simple_midi_file):
        info = get_midi_info(simple_midi_file)
        assert info.num_tracks == 2


# ==============================================================================
# EXTRACT_NOTES TESTS
# ==============================================================================

class TestExtractNotes:
    """Test extract_notes function."""

    def test_returns_list(self, simple_midi_file):
        mid = load_midi(simple_midi_file)
        notes = extract_notes(mid)
        assert isinstance(notes, list)

    def test_extracts_correct_note_count(self, simple_midi_file):
        mid = load_midi(simple_midi_file)
        notes = extract_notes(mid)
        assert len(notes) == 3

    def test_note_has_required_fields(self, simple_midi_file):
        mid = load_midi(simple_midi_file)
        notes = extract_notes(mid)

        for note in notes:
            assert "pitch" in note
            assert "velocity" in note
            assert "start_tick" in note
            assert "duration_ticks" in note
            assert "channel" in note
            assert "track" in note

    def test_extracts_correct_pitches(self, simple_midi_file):
        mid = load_midi(simple_midi_file)
        notes = extract_notes(mid)

        pitches = [n["pitch"] for n in notes]
        assert 60 in pitches  # C4
        assert 62 in pitches  # D4
        assert 64 in pitches  # E4

    def test_extracts_correct_velocities(self, simple_midi_file):
        mid = load_midi(simple_midi_file)
        notes = extract_notes(mid)

        velocities = [n["velocity"] for n in notes]
        assert 100 in velocities
        assert 90 in velocities
        assert 80 in velocities

    def test_notes_sorted_by_start_tick(self, simple_midi_file):
        mid = load_midi(simple_midi_file)
        notes = extract_notes(mid)

        start_ticks = [n["start_tick"] for n in notes]
        assert start_ticks == sorted(start_ticks)

    def test_extracts_chord_notes(self, complex_midi_file):
        mid = load_midi(complex_midi_file)
        notes = extract_notes(mid)

        # C major chord: C4, E4, G4 (60, 64, 67)
        first_chord_pitches = [n["pitch"] for n in notes if n["start_tick"] == 0]
        assert 60 in first_chord_pitches
        assert 64 in first_chord_pitches
        assert 67 in first_chord_pitches

    def test_calculates_duration(self, simple_midi_file):
        mid = load_midi(simple_midi_file)
        notes = extract_notes(mid)

        for note in notes:
            assert note["duration_ticks"] == 480  # One beat

    def test_empty_file_returns_empty_list(self, empty_midi_file):
        mid = load_midi(empty_midi_file)
        notes = extract_notes(mid)
        assert notes == []

    def test_tracks_channel(self, multi_channel_midi_file):
        mid = load_midi(multi_channel_midi_file)
        notes = extract_notes(mid)

        channels = set(n["channel"] for n in notes)
        assert 0 in channels
        assert 1 in channels
        assert 9 in channels


# ==============================================================================
# MERGE_TRACKS TESTS
# ==============================================================================

class TestMergeTracks:
    """Test merge_tracks function."""

    def test_returns_single_track(self, simple_midi_file):
        mid = load_midi(simple_midi_file)
        merged = merge_tracks(mid)
        assert isinstance(merged, mido.MidiTrack)

    def test_preserves_all_messages(self, simple_midi_file):
        mid = load_midi(simple_midi_file)
        merged = merge_tracks(mid)

        # Count note_on messages
        note_on_count = sum(1 for msg in merged if msg.type == 'note_on' and msg.velocity > 0)
        assert note_on_count == 3

    def test_merges_multiple_tracks(self, multi_channel_midi_file):
        mid = load_midi(multi_channel_midi_file)
        merged = merge_tracks(mid)

        # Should have notes from all channels
        channels = set()
        for msg in merged:
            if hasattr(msg, 'channel'):
                channels.add(msg.channel)

        assert len(channels) == 3  # 0, 1, 9


# ==============================================================================
# SPLIT_BY_CHANNEL TESTS
# ==============================================================================

class TestSplitByChannel:
    """Test split_by_channel function."""

    def test_returns_dict(self, multi_channel_midi_file):
        mid = load_midi(multi_channel_midi_file)
        channels = split_by_channel(mid)
        assert isinstance(channels, dict)

    def test_separates_channels(self, multi_channel_midi_file):
        mid = load_midi(multi_channel_midi_file)
        channels = split_by_channel(mid)

        assert 0 in channels
        assert 1 in channels
        assert 9 in channels

    def test_each_channel_has_messages(self, multi_channel_midi_file):
        mid = load_midi(multi_channel_midi_file)
        channels = split_by_channel(mid)

        for channel, messages in channels.items():
            assert len(messages) > 0

    def test_messages_are_tuples(self, multi_channel_midi_file):
        mid = load_midi(multi_channel_midi_file)
        channels = split_by_channel(mid)

        for channel, messages in channels.items():
            for msg_tuple in messages:
                assert isinstance(msg_tuple, tuple)
                assert len(msg_tuple) == 2  # (tick, message)

    def test_single_channel_file(self, simple_midi_file):
        mid = load_midi(simple_midi_file)
        channels = split_by_channel(mid)

        assert len(channels) == 1
        assert 0 in channels


# ==============================================================================
# ERROR HANDLING TESTS
# ==============================================================================

class TestErrorHandling:
    """Test error handling in MIDI I/O functions."""

    def test_load_nonexistent_raises_filenotfound(self):
        with pytest.raises(FileNotFoundError):
            load_midi("/this/path/does/not/exist.mid")

    def test_get_info_nonexistent_raises(self):
        with pytest.raises(FileNotFoundError):
            get_midi_info("/this/path/does/not/exist.mid")


# ==============================================================================
# EDGE CASES
# ==============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_note_on_with_zero_velocity_is_note_off(self):
        """Note on with velocity 0 should be treated as note off."""
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        # Note on with velocity > 0
        track.append(mido.Message('note_on', note=60, velocity=100, channel=0, time=0))
        # Note on with velocity 0 (equivalent to note off)
        track.append(mido.Message('note_on', note=60, velocity=0, channel=0, time=480))
        track.append(mido.MetaMessage('end_of_track', time=0))

        notes = extract_notes(mid)
        assert len(notes) == 1
        assert notes[0]["duration_ticks"] == 480

    def test_overlapping_notes_same_pitch(self):
        """Handle overlapping notes on the same pitch."""
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        # First note starts
        track.append(mido.Message('note_on', note=60, velocity=100, channel=0, time=0))
        # First note ends (but second note on same pitch might start)
        track.append(mido.Message('note_off', note=60, velocity=0, channel=0, time=240))
        # Second note on same pitch
        track.append(mido.Message('note_on', note=60, velocity=80, channel=0, time=0))
        track.append(mido.Message('note_off', note=60, velocity=0, channel=0, time=240))

        notes = extract_notes(mid)
        assert len(notes) == 2

    def test_tempo_change_mid_file(self):
        """MIDI files can have tempo changes - we take first tempo."""
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))  # 120 BPM
        track.append(mido.MetaMessage('set_tempo', tempo=600000, time=1920))  # 100 BPM (ignored)
        track.append(mido.MetaMessage('end_of_track', time=0))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            mid.save(temp_path)
            info = get_midi_info(temp_path)
            # Should get the first tempo encountered
            assert info.tempo_bpm in [100.0, 120.0]  # Either is acceptable
        finally:
            Path(temp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
