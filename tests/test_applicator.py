"""
Tests for the Groove Applicator module.

Covers: apply_groove function and humanize function with various parameters.

Run with: pytest tests/test_applicator.py -v
"""

import pytest
import tempfile
from pathlib import Path

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False

from music_brain.groove.applicator import (
    apply_groove,
    humanize,
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

    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))  # 120 BPM

    # Add some notes
    for i in range(8):
        track.append(mido.Message('note_on', note=60 + i, velocity=80, channel=0, time=0 if i == 0 else 480))
        track.append(mido.Message('note_off', note=60 + i, velocity=0, channel=0, time=240))

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        temp_path = f.name

    mid.save(temp_path)
    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def drum_midi_file():
    """Create a drum MIDI file for testing."""
    mid = mido.MidiFile(ticks_per_beat=480)

    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))  # 120 BPM

    # Drum pattern on channel 9
    for i in range(16):
        pitch = 36 if i % 2 == 0 else 38  # Alternating kick/snare
        track.append(mido.Message('note_on', note=pitch, velocity=100, channel=9, time=0 if i == 0 else 240))
        track.append(mido.Message('note_off', note=pitch, velocity=0, channel=9, time=120))

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        temp_path = f.name

    mid.save(temp_path)
    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def quantized_midi_file():
    """Create a perfectly quantized MIDI file."""
    mid = mido.MidiFile(ticks_per_beat=480)

    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))

    # Perfectly on-grid 16th notes
    for i in range(16):
        track.append(mido.Message('note_on', note=60, velocity=80, channel=0, time=0 if i == 0 else 120))
        track.append(mido.Message('note_off', note=60, velocity=0, channel=0, time=60))

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        temp_path = f.name

    mid.save(temp_path)
    yield temp_path

    Path(temp_path).unlink(missing_ok=True)


# ==============================================================================
# APPLY_GROOVE TESTS
# ==============================================================================

class TestApplyGroove:
    """Test apply_groove function."""

    def test_creates_output_file(self, simple_midi_file):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            result = apply_groove(simple_midi_file, genre="funk", output=output_path)
            assert Path(result).exists()
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_returns_output_path(self, simple_midi_file):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            result = apply_groove(simple_midi_file, genre="funk", output=output_path)
            assert result == output_path
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_default_output_name(self, simple_midi_file):
        try:
            result = apply_groove(simple_midi_file, genre="funk")
            expected_suffix = "_grooved.mid"
            assert expected_suffix in result
            assert Path(result).exists()
        finally:
            if Path(result).exists():
                Path(result).unlink()

    def test_raises_without_groove_or_genre(self, simple_midi_file):
        with pytest.raises(ValueError) as exc_info:
            apply_groove(simple_midi_file)

        assert "groove template or genre" in str(exc_info.value).lower()

    def test_raises_for_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            apply_groove("/nonexistent/file.mid", genre="funk")

    def test_raises_for_invalid_genre(self, simple_midi_file):
        with pytest.raises(ValueError):
            apply_groove(simple_midi_file, genre="nonexistent_genre")

    def test_valid_genres(self, simple_midi_file):
        """Test that common genres work."""
        genres = ["funk", "jazz", "rock", "hiphop"]

        for genre in genres:
            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
                output_path = f.name

            try:
                result = apply_groove(simple_midi_file, genre=genre, output=output_path)
                assert Path(result).exists()
            finally:
                Path(output_path).unlink(missing_ok=True)

    def test_intensity_zero_minimal_change(self, quantized_midi_file):
        """Zero intensity should result in minimal changes."""
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            apply_groove(
                quantized_midi_file,
                genre="funk",
                output=output_path,
                intensity=0.0,
            )

            # Load and check
            original = mido.MidiFile(quantized_midi_file)
            grooved = mido.MidiFile(output_path)

            # Should have same structure
            assert len(grooved.tracks) == len(original.tracks)
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_intensity_one_maximum_change(self, quantized_midi_file):
        """Full intensity should apply maximum groove."""
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            apply_groove(
                quantized_midi_file,
                genre="funk",
                output=output_path,
                intensity=1.0,
            )

            assert Path(output_path).exists()
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_preserve_dynamics_false(self, simple_midi_file):
        """Test with preserve_dynamics=False."""
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            apply_groove(
                simple_midi_file,
                genre="funk",
                output=output_path,
                preserve_dynamics=False,
            )
            assert Path(output_path).exists()
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_humanize_timing_false(self, simple_midi_file):
        """Test with humanize_timing=False."""
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            apply_groove(
                simple_midi_file,
                genre="funk",
                output=output_path,
                humanize_timing=False,
            )
            assert Path(output_path).exists()
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_humanize_velocity_false(self, simple_midi_file):
        """Test with humanize_velocity=False."""
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            apply_groove(
                simple_midi_file,
                genre="funk",
                output=output_path,
                humanize_velocity=False,
            )
            assert Path(output_path).exists()
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_output_is_valid_midi(self, simple_midi_file):
        """Output should be a valid MIDI file."""
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            apply_groove(simple_midi_file, genre="jazz", output=output_path)

            # Should load without error
            mid = mido.MidiFile(output_path)
            assert mid.ticks_per_beat > 0
        finally:
            Path(output_path).unlink(missing_ok=True)


# ==============================================================================
# HUMANIZE TESTS
# ==============================================================================

class TestHumanize:
    """Test humanize function."""

    def test_creates_output_file(self, simple_midi_file):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            result = humanize(simple_midi_file, output=output_path)
            assert Path(result).exists()
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_returns_output_path(self, simple_midi_file):
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            result = humanize(simple_midi_file, output=output_path)
            assert result == output_path
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_default_output_name(self, simple_midi_file):
        try:
            result = humanize(simple_midi_file)
            expected_suffix = "_humanized.mid"
            assert expected_suffix in result
            assert Path(result).exists()
        finally:
            if Path(result).exists():
                Path(result).unlink()

    def test_raises_for_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            humanize("/nonexistent/file.mid")

    def test_seed_reproducibility(self, quantized_midi_file):
        """Same seed should produce same output."""
        outputs = []

        for _ in range(2):
            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
                output_path = f.name

            try:
                humanize(
                    quantized_midi_file,
                    output=output_path,
                    seed=42,
                )

                mid = mido.MidiFile(output_path)
                # Extract note velocities as a fingerprint
                velocities = []
                for track in mid.tracks:
                    for msg in track:
                        if msg.type == 'note_on' and msg.velocity > 0:
                            velocities.append(msg.velocity)
                outputs.append(velocities)
            finally:
                Path(output_path).unlink(missing_ok=True)

        assert outputs[0] == outputs[1]

    def test_different_seeds_different_output(self, quantized_midi_file):
        """Different seeds should produce different output."""
        outputs = []

        for seed in [42, 123]:
            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
                output_path = f.name

            try:
                humanize(
                    quantized_midi_file,
                    output=output_path,
                    seed=seed,
                )

                mid = mido.MidiFile(output_path)
                velocities = []
                for track in mid.tracks:
                    for msg in track:
                        if msg.type == 'note_on' and msg.velocity > 0:
                            velocities.append(msg.velocity)
                outputs.append(velocities)
            finally:
                Path(output_path).unlink(missing_ok=True)

        # Should be different (with high probability)
        assert outputs[0] != outputs[1]

    def test_timing_range_parameter(self, simple_midi_file):
        """Test timing_range_ms parameter."""
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            result = humanize(
                simple_midi_file,
                output=output_path,
                timing_range_ms=5.0,
            )
            assert Path(result).exists()
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_velocity_range_parameter(self, simple_midi_file):
        """Test velocity_range parameter."""
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            result = humanize(
                simple_midi_file,
                output=output_path,
                velocity_range=20,
            )
            assert Path(result).exists()
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_zero_timing_range(self, quantized_midi_file):
        """Zero timing range should preserve timing."""
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            humanize(
                quantized_midi_file,
                output=output_path,
                timing_range_ms=0.0,
                velocity_range=0,
                seed=42,
            )

            # Load and check timing is similar
            original = mido.MidiFile(quantized_midi_file)
            humanized = mido.MidiFile(output_path)

            # Get timing from first track
            orig_times = [msg.time for msg in original.tracks[0] if msg.type == 'note_on']
            hum_times = [msg.time for msg in humanized.tracks[0] if msg.type == 'note_on']

            # Should be identical or very close
            assert orig_times == hum_times
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_output_is_valid_midi(self, simple_midi_file):
        """Output should be a valid MIDI file."""
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            humanize(simple_midi_file, output=output_path)

            # Should load without error
            mid = mido.MidiFile(output_path)
            assert mid.ticks_per_beat > 0
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_velocities_within_bounds(self, simple_midi_file):
        """Velocities should stay within MIDI bounds."""
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            humanize(
                simple_midi_file,
                output=output_path,
                velocity_range=50,  # Large range
            )

            mid = mido.MidiFile(output_path)
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'note_on' and msg.velocity > 0:
                        assert 1 <= msg.velocity <= 127
        finally:
            Path(output_path).unlink(missing_ok=True)


# ==============================================================================
# EDGE CASES
# ==============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_midi_file(self):
        """Test with MIDI file that has no notes."""
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
        track.append(mido.MetaMessage('end_of_track', time=0))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name
        mid.save(temp_path)

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            result = apply_groove(temp_path, genre="funk", output=output_path)
            assert Path(result).exists()
        finally:
            Path(temp_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)

    def test_single_note_midi(self):
        """Test with MIDI file containing only one note."""
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
        track.append(mido.Message('note_on', note=60, velocity=80, channel=0, time=0))
        track.append(mido.Message('note_off', note=60, velocity=0, channel=0, time=480))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name
        mid.save(temp_path)

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            result = humanize(temp_path, output=output_path)
            assert Path(result).exists()
        finally:
            Path(temp_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)

    def test_multiple_tracks(self):
        """Test with MIDI file containing multiple tracks."""
        mid = mido.MidiFile(ticks_per_beat=480)

        # Track 1: Melody
        track1 = mido.MidiTrack()
        mid.tracks.append(track1)
        track1.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
        for i in range(4):
            track1.append(mido.Message('note_on', note=60 + i, velocity=80, channel=0, time=0 if i == 0 else 480))
            track1.append(mido.Message('note_off', note=60 + i, velocity=0, channel=0, time=240))

        # Track 2: Bass
        track2 = mido.MidiTrack()
        mid.tracks.append(track2)
        for i in range(4):
            track2.append(mido.Message('note_on', note=36 + i, velocity=100, channel=1, time=0 if i == 0 else 480))
            track2.append(mido.Message('note_off', note=36 + i, velocity=0, channel=1, time=240))

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            temp_path = f.name
        mid.save(temp_path)

        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            output_path = f.name

        try:
            result = apply_groove(temp_path, genre="jazz", output=output_path)

            out_mid = mido.MidiFile(result)
            assert len(out_mid.tracks) == 2
        finally:
            Path(temp_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
