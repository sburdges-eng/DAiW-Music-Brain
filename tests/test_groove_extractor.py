"""
Tests for the Groove Extractor module.

Covers: extract_groove, GrooveTemplate serialization, NoteEvent,
swing calculation, and timing deviation analysis.

Run with: pytest tests/test_groove_extractor.py -v
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

from music_brain.groove.extractor import (
    extract_groove,
    load_groove,
    GrooveTemplate,
    NoteEvent,
    _calculate_swing,
    MIDO_AVAILABLE as MODULE_MIDO_AVAILABLE,
)


# Skip all tests if mido not available
pytestmark = pytest.mark.skipif(not MIDO_AVAILABLE, reason="mido not installed")


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def straight_drum_midi():
    """Create a MIDI file with perfectly quantized drums (no swing)."""
    mid = mido.MidiFile(ticks_per_beat=480)

    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))  # 120 BPM

    # Straight 8th notes on hi-hat (pitch 42)
    for i in range(16):  # 2 bars
        track.append(mido.Message('note_on', note=42, velocity=80, channel=9, time=0 if i == 0 else 240))
        track.append(mido.Message('note_off', note=42, velocity=0, channel=9, time=120))

    # Add kick on 1 and 3
    track.append(mido.Message('note_on', note=36, velocity=100, channel=9, time=0))
    track.append(mido.Message('note_off', note=36, velocity=0, channel=9, time=240))

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        temp_path = f.name

    mid.save(temp_path)
    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def swung_drum_midi():
    """Create a MIDI file with swung drums."""
    mid = mido.MidiFile(ticks_per_beat=480)

    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))  # 120 BPM

    # Swung 8ths: long-short pattern (triplet feel: 2:1 ratio)
    # On beat = 0, Off beat = 320 ticks (instead of 240)
    ppq = 480
    for i in range(8):  # 2 bars of 8ths
        if i % 2 == 0:
            # On beat
            track.append(mido.Message('note_on', note=42, velocity=80, channel=9, time=0 if i == 0 else 160))
        else:
            # Off beat - pushed late
            track.append(mido.Message('note_on', note=42, velocity=70, channel=9, time=320))
        track.append(mido.Message('note_off', note=42, velocity=0, channel=9, time=100))

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        temp_path = f.name

    mid.save(temp_path)
    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def humanized_drum_midi():
    """Create a MIDI file with humanized timing (slight deviations)."""
    mid = mido.MidiFile(ticks_per_beat=480)

    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))

    # Notes with slight timing variations
    deviations = [0, 5, -3, 8, -5, 10, -8, 3]
    base_interval = 240  # 8th notes

    cumulative_time = 0
    for i, dev in enumerate(deviations):
        delta = base_interval + dev if i > 0 else 0
        track.append(mido.Message('note_on', note=42, velocity=80, channel=9, time=delta))
        track.append(mido.Message('note_off', note=42, velocity=0, channel=9, time=100))

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        temp_path = f.name

    mid.save(temp_path)
    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def velocity_varied_midi():
    """Create a MIDI file with varied velocities including ghost notes."""
    mid = mido.MidiFile(ticks_per_beat=480)

    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))

    # Velocities: accent, normal, ghost, normal, accent, ghost, normal, normal
    velocities = [120, 80, 30, 80, 110, 25, 85, 90]

    for i, vel in enumerate(velocities):
        track.append(mido.Message('note_on', note=38, velocity=vel, channel=9, time=0 if i == 0 else 240))
        track.append(mido.Message('note_off', note=38, velocity=0, channel=9, time=120))

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        temp_path = f.name

    mid.save(temp_path)
    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def empty_midi():
    """Create an empty MIDI file (no notes)."""
    mid = mido.MidiFile(ticks_per_beat=480)

    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
    track.append(mido.MetaMessage('end_of_track', time=0))

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        temp_path = f.name

    mid.save(temp_path)
    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


# ==============================================================================
# NOTE EVENT TESTS
# ==============================================================================

class TestNoteEvent:
    """Test NoteEvent dataclass."""

    def test_creation(self):
        event = NoteEvent(
            pitch=60,
            velocity=100,
            start_tick=0,
            duration_ticks=480,
            channel=0,
        )
        assert event.pitch == 60
        assert event.velocity == 100
        assert event.start_tick == 0
        assert event.duration_ticks == 480

    def test_default_values(self):
        event = NoteEvent(pitch=60, velocity=80, start_tick=0, duration_ticks=240)
        assert event.channel == 0
        assert event.deviation_ticks == 0.0
        assert event.is_ghost is False
        assert event.is_accent is False

    def test_ghost_flag(self):
        event = NoteEvent(
            pitch=60, velocity=30, start_tick=0, duration_ticks=240,
            is_ghost=True,
        )
        assert event.is_ghost is True

    def test_accent_flag(self):
        event = NoteEvent(
            pitch=60, velocity=120, start_tick=0, duration_ticks=240,
            is_accent=True,
        )
        assert event.is_accent is True


# ==============================================================================
# GROOVE TEMPLATE TESTS
# ==============================================================================

class TestGrooveTemplate:
    """Test GrooveTemplate dataclass and serialization."""

    def test_default_creation(self):
        template = GrooveTemplate()
        assert template.name == "Untitled Groove"
        assert template.ppq == 480
        assert template.tempo_bpm == 120.0
        assert template.swing_factor == 0.0

    def test_custom_creation(self):
        template = GrooveTemplate(
            name="Funky Groove",
            source_file="drums.mid",
            ppq=480,
            tempo_bpm=100.0,
            time_signature=(4, 4),
            swing_factor=0.3,
            timing_deviations=[0, 5, -3, 8],
            velocity_curve=[100, 80, 90, 85],
        )
        assert template.name == "Funky Groove"
        assert template.swing_factor == 0.3
        assert len(template.timing_deviations) == 4

    def test_to_dict(self):
        template = GrooveTemplate(
            name="Test Groove",
            swing_factor=0.25,
            velocity_stats={"min": 30, "max": 120},
        )
        data = template.to_dict()

        assert isinstance(data, dict)
        assert data["name"] == "Test Groove"
        assert data["swing_factor"] == 0.25
        assert data["velocity_stats"]["min"] == 30

    def test_from_dict(self):
        data = {
            "name": "Loaded Groove",
            "source_file": "test.mid",
            "ppq": 480,
            "tempo_bpm": 110.0,
            "time_signature": [4, 4],
            "timing_deviations": [1, 2, 3],
            "swing_factor": 0.15,
            "velocity_curve": [80, 90, 85],
            "velocity_stats": {"min": 60, "max": 100},
            "timing_stats": {"mean_deviation_ms": 2.5},
        }
        template = GrooveTemplate.from_dict(data)

        assert template.name == "Loaded Groove"
        assert template.tempo_bpm == 110.0
        assert template.swing_factor == 0.15
        assert template.time_signature == (4, 4)

    def test_to_dict_from_dict_roundtrip(self):
        original = GrooveTemplate(
            name="Roundtrip Test",
            source_file="source.mid",
            ppq=480,
            tempo_bpm=95.0,
            time_signature=(3, 4),
            swing_factor=0.2,
            timing_deviations=[5, -3, 8, -2],
            velocity_curve=[100, 80, 90, 85],
            velocity_stats={"min": 40, "max": 110, "mean": 80},
            timing_stats={"mean_deviation_ms": 3.5},
        )

        data = original.to_dict()
        restored = GrooveTemplate.from_dict(data)

        assert restored.name == original.name
        assert restored.tempo_bpm == original.tempo_bpm
        assert restored.swing_factor == original.swing_factor
        assert restored.timing_deviations == original.timing_deviations

    def test_save_creates_file(self):
        template = GrooveTemplate(name="Save Test", swing_factor=0.3)

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            template.save(temp_path)
            assert Path(temp_path).exists()

            with open(temp_path) as f:
                data = json.load(f)
            assert data["name"] == "Save Test"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_reads_file(self):
        original = GrooveTemplate(name="Load Test", swing_factor=0.4)

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            original.save(temp_path)
            loaded = GrooveTemplate.load(temp_path)

            assert loaded.name == "Load Test"
            assert loaded.swing_factor == 0.4
        finally:
            Path(temp_path).unlink(missing_ok=True)


# ==============================================================================
# EXTRACT_GROOVE TESTS
# ==============================================================================

class TestExtractGroove:
    """Test extract_groove function."""

    def test_returns_groove_template(self, straight_drum_midi):
        result = extract_groove(straight_drum_midi)
        assert isinstance(result, GrooveTemplate)

    def test_extracts_ppq(self, straight_drum_midi):
        result = extract_groove(straight_drum_midi)
        assert result.ppq == 480

    def test_extracts_tempo(self, straight_drum_midi):
        result = extract_groove(straight_drum_midi)
        assert result.tempo_bpm == 120.0

    def test_extracts_source_file(self, straight_drum_midi):
        result = extract_groove(straight_drum_midi)
        assert result.source_file == straight_drum_midi

    def test_extracts_timing_deviations(self, humanized_drum_midi):
        result = extract_groove(humanized_drum_midi)
        assert len(result.timing_deviations) > 0

    def test_extracts_velocity_stats(self, velocity_varied_midi):
        result = extract_groove(velocity_varied_midi)
        assert "min" in result.velocity_stats
        assert "max" in result.velocity_stats
        assert "mean" in result.velocity_stats

    def test_detects_ghost_notes(self, velocity_varied_midi):
        result = extract_groove(velocity_varied_midi, ghost_threshold=40)
        assert result.velocity_stats["ghost_count"] >= 2

    def test_detects_accent_notes(self, velocity_varied_midi):
        result = extract_groove(velocity_varied_midi, accent_threshold=100)
        assert result.velocity_stats["accent_count"] >= 2

    def test_extracts_velocity_curve(self, straight_drum_midi):
        result = extract_groove(straight_drum_midi)
        assert len(result.velocity_curve) > 0

    def test_extracts_timing_stats(self, humanized_drum_midi):
        result = extract_groove(humanized_drum_midi)
        assert "mean_deviation_ticks" in result.timing_stats
        assert "mean_deviation_ms" in result.timing_stats

    def test_extracts_events(self, straight_drum_midi):
        result = extract_groove(straight_drum_midi)
        assert len(result.events) > 0
        assert all(isinstance(e, NoteEvent) for e in result.events)

    def test_empty_file_returns_basic_template(self, empty_midi):
        result = extract_groove(empty_midi)
        assert isinstance(result, GrooveTemplate)
        assert len(result.events) == 0

    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            extract_groove("/nonexistent/file.mid")

    def test_custom_quantize_resolution(self, humanized_drum_midi):
        result_16th = extract_groove(humanized_drum_midi, quantize_resolution=16)
        result_8th = extract_groove(humanized_drum_midi, quantize_resolution=8)

        # Both should work, deviations may differ based on grid
        assert len(result_16th.timing_deviations) > 0
        assert len(result_8th.timing_deviations) > 0


# ==============================================================================
# SWING CALCULATION TESTS
# ==============================================================================

class TestCalculateSwing:
    """Test _calculate_swing helper function."""

    def test_no_events_returns_zero(self):
        swing = _calculate_swing([], 480)
        assert swing == 0.0

    def test_few_events_returns_zero(self):
        events = [
            NoteEvent(pitch=42, velocity=80, start_tick=0, duration_ticks=120),
            NoteEvent(pitch=42, velocity=80, start_tick=240, duration_ticks=120),
        ]
        swing = _calculate_swing(events, 480)
        assert swing == 0.0

    def test_straight_events_low_swing(self):
        """Perfectly straight 8ths should have low swing factor."""
        ppq = 480
        events = []
        for i in range(16):
            events.append(NoteEvent(
                pitch=42,
                velocity=80,
                start_tick=i * (ppq // 2),
                duration_ticks=100,
            ))

        swing = _calculate_swing(events, ppq)
        # Straight should be close to 0.5 (no swing bias)
        assert swing < 0.6  # Allow some tolerance

    def test_swing_factor_in_valid_range(self, swung_drum_midi):
        """Swing factor should be between 0 and 1."""
        result = extract_groove(swung_drum_midi)
        assert 0.0 <= result.swing_factor <= 1.0


# ==============================================================================
# LOAD_GROOVE TESTS
# ==============================================================================

class TestLoadGroove:
    """Test load_groove convenience function."""

    def test_loads_groove_template(self):
        template = GrooveTemplate(name="Convenience Test", swing_factor=0.35)

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            template.save(temp_path)
            loaded = load_groove(temp_path)

            assert isinstance(loaded, GrooveTemplate)
            assert loaded.name == "Convenience Test"
            assert loaded.swing_factor == 0.35
        finally:
            Path(temp_path).unlink(missing_ok=True)


# ==============================================================================
# EDGE CASES
# ==============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_short_file(self):
        """File with just one note."""
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
        track.append(mido.Message('note_on', note=60, velocity=100, channel=0, time=0))
        track.append(mido.Message('note_off', note=60, velocity=0, channel=0, time=480))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            mid.save(temp_path)
            result = extract_groove(temp_path)
            assert len(result.events) == 1
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_all_ghost_notes(self):
        """File with only low velocity notes."""
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))

        for i in range(8):
            track.append(mido.Message('note_on', note=42, velocity=25, channel=9, time=0 if i == 0 else 240))
            track.append(mido.Message('note_off', note=42, velocity=0, channel=9, time=100))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            mid.save(temp_path)
            result = extract_groove(temp_path, ghost_threshold=40)
            assert result.velocity_stats["ghost_count"] == 8
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_all_accent_notes(self):
        """File with only high velocity notes."""
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))

        for i in range(8):
            track.append(mido.Message('note_on', note=38, velocity=120, channel=9, time=0 if i == 0 else 240))
            track.append(mido.Message('note_off', note=38, velocity=0, channel=9, time=100))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            mid.save(temp_path)
            result = extract_groove(temp_path, accent_threshold=100)
            assert result.velocity_stats["accent_count"] == 8
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_uses_filename_as_name(self, straight_drum_midi):
        result = extract_groove(straight_drum_midi)
        expected_name = Path(straight_drum_midi).stem
        assert result.name == expected_name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
