"""
Tests for the Audio Feel Analysis module.

Covers: AudioFeatures dataclass, analyze_feel, compare_feel,
swing estimation, groove regularity, and tempo confidence.

Note: These tests require librosa. Tests are skipped when unavailable.

Run with: pytest tests/test_audio_feel.py -v
"""

import pytest
import tempfile
from pathlib import Path

from music_brain.audio.feel import (
    AudioFeatures,
    LIBROSA_AVAILABLE,
    NUMPY_AVAILABLE,
)

# Conditionally import functions that require librosa
if LIBROSA_AVAILABLE and NUMPY_AVAILABLE:
    from music_brain.audio.feel import (
        analyze_feel,
        compare_feel,
        _estimate_tempo_confidence,
        _estimate_swing,
        _estimate_groove_regularity,
    )
    import numpy as np


# ==============================================================================
# AUDIO FEATURES DATACLASS TESTS (No librosa required)
# ==============================================================================

class TestAudioFeatures:
    """Test AudioFeatures dataclass."""

    def test_default_values(self):
        features = AudioFeatures()
        assert features.filename == ""
        assert features.duration_seconds == 0.0
        assert features.sample_rate == 44100
        assert features.tempo_bpm == 120.0
        assert features.tempo_confidence == 0.0

    def test_custom_values(self):
        features = AudioFeatures(
            filename="test.wav",
            duration_seconds=180.0,
            sample_rate=48000,
            tempo_bpm=95.5,
            tempo_confidence=0.85,
            rms_mean=0.15,
            swing_estimate=0.3,
            groove_regularity=0.9,
        )
        assert features.filename == "test.wav"
        assert features.duration_seconds == 180.0
        assert features.tempo_bpm == 95.5
        assert features.swing_estimate == 0.3

    def test_beat_positions_default_empty(self):
        features = AudioFeatures()
        assert features.beat_positions == []

    def test_energy_curve_default_empty(self):
        features = AudioFeatures()
        assert features.energy_curve == []

    def test_to_dict_returns_dict(self):
        features = AudioFeatures(
            filename="test.wav",
            tempo_bpm=120.0,
            beat_positions=[0.5, 1.0, 1.5, 2.0],
            energy_curve=[0.1, 0.2, 0.3],
        )
        data = features.to_dict()

        assert isinstance(data, dict)
        assert data["filename"] == "test.wav"
        assert data["tempo_bpm"] == 120.0
        assert data["beat_count"] == 4

    def test_to_dict_energy_stats(self):
        features = AudioFeatures(
            energy_curve=[0.1, 0.2, 0.3, 0.4],
        )
        data = features.to_dict()

        assert "energy_stats" in data
        assert data["energy_stats"]["max"] == 0.4
        # Mean of [0.1, 0.2, 0.3, 0.4] = 0.25
        assert abs(data["energy_stats"]["mean"] - 0.25) < 0.01

    def test_to_dict_empty_energy_curve(self):
        features = AudioFeatures(energy_curve=[])
        data = features.to_dict()

        assert data["energy_stats"]["mean"] == 0
        assert data["energy_stats"]["max"] == 0


# ==============================================================================
# SWING ESTIMATION TESTS (Requires numpy only)
# ==============================================================================

@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not installed")
class TestEstimateSwing:
    """Test _estimate_swing helper function."""

    def test_empty_beat_times_returns_zero(self):
        beat_times = np.array([])
        result = _estimate_swing(beat_times)
        assert result == 0.0

    def test_few_beats_returns_zero(self):
        beat_times = np.array([0.0, 0.5])
        result = _estimate_swing(beat_times)
        assert result == 0.0

    def test_straight_timing_low_swing(self):
        """Perfectly even beat times should have low swing."""
        # 8 beats at exactly 0.5s intervals
        beat_times = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5])
        result = _estimate_swing(beat_times)

        # Should be close to 0 (no swing)
        assert result < 0.2

    def test_swing_in_valid_range(self):
        """Swing should always be between 0 and 1."""
        # Some arbitrary timing
        beat_times = np.array([0.0, 0.6, 1.0, 1.6, 2.0, 2.6, 3.0, 3.6])
        result = _estimate_swing(beat_times)

        assert 0.0 <= result <= 1.0


# ==============================================================================
# GROOVE REGULARITY TESTS (Requires numpy only)
# ==============================================================================

@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not installed")
class TestEstimateGrooveRegularity:
    """Test _estimate_groove_regularity helper function."""

    def test_few_beats_returns_one(self):
        beat_times = np.array([0.0, 0.5])
        result = _estimate_groove_regularity(beat_times)
        assert result == 1.0

    def test_perfect_regularity(self):
        """Perfectly regular beats should return 1.0."""
        beat_times = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5])
        result = _estimate_groove_regularity(beat_times)

        assert result > 0.95

    def test_irregular_timing_lower_regularity(self):
        """Irregular timing should have lower regularity score."""
        # Very irregular intervals
        beat_times = np.array([0.0, 0.3, 1.2, 1.5, 2.8, 3.0, 4.5, 5.0])
        result = _estimate_groove_regularity(beat_times)

        assert result < 0.8

    def test_regularity_in_valid_range(self):
        """Regularity should always be between 0 and 1."""
        beat_times = np.array([0.0, 0.4, 0.9, 1.5, 2.1, 2.6, 3.2, 3.8])
        result = _estimate_groove_regularity(beat_times)

        assert 0.0 <= result <= 1.0


# ==============================================================================
# ANALYZE FEEL TESTS (Requires librosa)
# ==============================================================================

@pytest.mark.skipif(not LIBROSA_AVAILABLE, reason="librosa not installed")
class TestAnalyzeFeel:
    """Test analyze_feel function."""

    def test_raises_for_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            analyze_feel("/nonexistent/audio/file.wav")

    def test_raises_for_invalid_path_type(self):
        # Just check it handles the error gracefully
        with pytest.raises((FileNotFoundError, TypeError)):
            analyze_feel(None)


# ==============================================================================
# COMPARE FEEL TESTS (Requires librosa)
# ==============================================================================

@pytest.mark.skipif(not LIBROSA_AVAILABLE, reason="librosa not installed")
class TestCompareFeel:
    """Test compare_feel function."""

    def test_raises_for_nonexistent_files(self):
        with pytest.raises(FileNotFoundError):
            compare_feel("/nonexistent/file1.wav", "/nonexistent/file2.wav")


# ==============================================================================
# IMPORT AVAILABILITY TESTS
# ==============================================================================

class TestImportAvailability:
    """Test that availability flags work correctly."""

    def test_librosa_available_is_bool(self):
        assert isinstance(LIBROSA_AVAILABLE, bool)

    def test_numpy_available_is_bool(self):
        assert isinstance(NUMPY_AVAILABLE, bool)

    def test_can_import_dataclass_without_librosa(self):
        """AudioFeatures should be importable even without librosa."""
        from music_brain.audio.feel import AudioFeatures
        features = AudioFeatures()
        assert features is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
