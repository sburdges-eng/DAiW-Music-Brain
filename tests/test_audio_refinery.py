"""
Tests for the Audio Refinery module.

Covers: Sample/Kit classes, category detection, AudioVault operations.

Run with: pytest tests/test_audio_refinery.py -v
"""

import pytest
from pathlib import Path
import tempfile
import json

from music_brain.audio_refinery import (
    Sample,
    Kit,
    detect_category,
    extract_bpm_from_name,
    extract_key_from_name,
    scan_audio_vault,
    find_samples_by_category,
    build_kit_from_samples,
    build_basic_drum_kit,
    save_kit,
    load_kit,
    suggest_samples_for_mood,
    MOOD_PREFERENCES,
)


# ==============================================================================
# SAMPLE DATACLASS TESTS
# ==============================================================================

class TestSample:
    """Tests for the Sample dataclass."""

    def test_creation(self):
        """Should create a sample with required fields."""
        sample = Sample(
            path=Path("/audio/kick.wav"),
            name="kick",
        )

        assert sample.path == Path("/audio/kick.wav")
        assert sample.name == "kick"

    def test_defaults(self):
        """Should have sensible defaults."""
        sample = Sample(path=Path("/test.wav"), name="test")

        assert sample.category == "unknown"
        assert sample.bpm is None
        assert sample.key is None
        assert sample.tags == []

    def test_to_dict(self):
        """Should serialize to dictionary."""
        sample = Sample(
            path=Path("/audio/kick_120bpm.wav"),
            name="kick_120bpm",
            category="kick",
            bpm=120.0,
            key="Am",
            tags=["drums", "acoustic"],
        )

        data = sample.to_dict()

        assert data["path"] == "/audio/kick_120bpm.wav"
        assert data["name"] == "kick_120bpm"
        assert data["category"] == "kick"
        assert data["bpm"] == 120.0
        assert data["key"] == "Am"
        assert data["tags"] == ["drums", "acoustic"]

    def test_from_dict(self):
        """Should deserialize from dictionary."""
        data = {
            "path": "/audio/snare.wav",
            "name": "snare",
            "category": "snare",
            "bpm": 90.0,
            "key": "C",
            "tags": ["punchy"],
        }

        sample = Sample.from_dict(data)

        assert sample.path == Path("/audio/snare.wav")
        assert sample.name == "snare"
        assert sample.category == "snare"


# ==============================================================================
# KIT DATACLASS TESTS
# ==============================================================================

class TestKit:
    """Tests for the Kit dataclass."""

    def test_creation(self):
        """Should create a kit with name."""
        kit = Kit(name="Test Kit")

        assert kit.name == "Test Kit"
        assert kit.samples == []

    def test_with_samples(self):
        """Should hold samples."""
        samples = [
            Sample(path=Path("/kick.wav"), name="kick"),
            Sample(path=Path("/snare.wav"), name="snare"),
        ]

        kit = Kit(name="Drums", samples=samples)

        assert len(kit.samples) == 2

    def test_to_dict(self):
        """Should serialize to dictionary."""
        kit = Kit(
            name="Test Kit",
            samples=[Sample(path=Path("/test.wav"), name="test")],
            mood="grief",
            genre="ambient",
            description="Test description",
        )

        data = kit.to_dict()

        assert data["name"] == "Test Kit"
        assert len(data["samples"]) == 1
        assert data["mood"] == "grief"
        assert data["genre"] == "ambient"

    def test_from_dict(self):
        """Should deserialize from dictionary."""
        data = {
            "name": "Loaded Kit",
            "samples": [{"path": "/test.wav", "name": "test"}],
            "mood": "rage",
        }

        kit = Kit.from_dict(data)

        assert kit.name == "Loaded Kit"
        assert len(kit.samples) == 1


# ==============================================================================
# CATEGORY DETECTION TESTS
# ==============================================================================

class TestCategoryDetection:
    """Tests for automatic category detection."""

    @pytest.mark.parametrize("filename,expected", [
        ("kick_acoustic.wav", "kick"),
        ("bd_01.wav", "kick"),
        ("snare_tight.wav", "snare"),
        ("snr_02.wav", "snare"),
        ("hihat_closed.wav", "hihat"),
        ("hh_open.wav", "hihat"),
        ("tom_floor.wav", "tom"),
        ("crash_cymbal.wav", "cymbal"),
        ("ride_bell.wav", "cymbal"),
        ("shaker_01.wav", "perc"),
        ("tambourine.wav", "perc"),
        ("bass_synth.wav", "bass"),
        ("808_sub.wav", "bass"),
        ("lead_synth.wav", "synth"),
        ("pad_ambient.wav", "synth"),
        ("vocal_chop.wav", "vocal"),
        ("riser_fx.wav", "fx"),
        ("drum_loop_120bpm.wav", "loop"),
        ("random_sample.wav", "unknown"),
    ])
    def test_detects_category(self, filename, expected):
        """Should detect correct category from filename."""
        assert detect_category(filename) == expected

    def test_case_insensitive(self):
        """Should be case-insensitive."""
        assert detect_category("KICK_01.WAV") == "kick"
        assert detect_category("Snare_Hard.wav") == "snare"


class TestBpmExtraction:
    """Tests for BPM extraction from filenames."""

    @pytest.mark.parametrize("filename,expected", [
        ("beat_120bpm.wav", 120.0),
        ("loop_90_bpm.wav", 90.0),
        ("groove_140-bpm.wav", 140.0),
        ("bpm120_track.wav", 120.0),
        ("bpm_85_loop.wav", 85.0),
        ("100_tempo_track.wav", 100.0),
        ("no_tempo_info.wav", None),
        ("random_file.wav", None),
    ])
    def test_extracts_bpm(self, filename, expected):
        """Should extract BPM from various filename patterns."""
        assert extract_bpm_from_name(filename) == expected


class TestKeyExtraction:
    """Tests for key extraction from filenames."""

    @pytest.mark.parametrize("filename,expected", [
        ("melody_Am.wav", "Am"),
        ("chord_Cmaj.wav", "C"),
        ("bass_Dm.wav", "Dm"),
        ("lead_F#m.wav", "F#m"),
        ("pad_Bbmajor.wav", "Bb"),
        ("synth_Gminor.wav", "Gm"),
        ("no_key_info.wav", None),
    ])
    def test_extracts_key(self, filename, expected):
        """Should extract musical key from filename."""
        assert extract_key_from_name(filename) == expected


# ==============================================================================
# KIT OPERATIONS TESTS
# ==============================================================================

class TestKitOperations:
    """Tests for kit save/load operations."""

    def test_save_and_load_kit(self):
        """Should save kit to JSON and load it back."""
        kit = Kit(
            name="Test Kit",
            samples=[
                Sample(path=Path("/kick.wav"), name="kick", category="kick"),
                Sample(path=Path("/snare.wav"), name="snare", category="snare"),
            ],
            mood="rage",
            description="Test kit for testing",
        )

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            output_path = Path(f.name)

        try:
            # Save
            save_kit(kit, output_path)

            # Load
            loaded = load_kit(output_path)

            assert loaded.name == "Test Kit"
            assert len(loaded.samples) == 2
            assert loaded.mood == "rage"
        finally:
            output_path.unlink()


class TestBuildKitFromSamples:
    """Tests for building kits from sample lists."""

    def test_builds_kit(self):
        """Should create kit from samples."""
        samples = [
            Sample(path=Path("/kick.wav"), name="kick"),
            Sample(path=Path("/snare.wav"), name="snare"),
        ]

        kit = build_kit_from_samples(
            name="My Kit",
            samples=samples,
            mood="grief",
            genre="ambient",
        )

        assert kit.name == "My Kit"
        assert len(kit.samples) == 2
        assert kit.mood == "grief"
        assert kit.genre == "ambient"


# ==============================================================================
# MOOD-BASED SUGGESTION TESTS
# ==============================================================================

class TestMoodPreferences:
    """Tests for mood-based sample suggestions."""

    def test_mood_preferences_exist(self):
        """Should have preferences for common moods."""
        expected_moods = ["grief", "rage", "nostalgia", "defiance", "hope", "anxiety", "peace"]

        for mood in expected_moods:
            assert mood in MOOD_PREFERENCES

    def test_preferences_have_categories(self):
        """Each mood should have preferred categories."""
        for mood, prefs in MOOD_PREFERENCES.items():
            assert "categories" in prefs
            assert isinstance(prefs["categories"], list)

    def test_preferences_have_bpm_range(self):
        """Each mood should have BPM range."""
        for mood, prefs in MOOD_PREFERENCES.items():
            assert "bpm_range" in prefs
            low, high = prefs["bpm_range"]
            assert low < high


# ==============================================================================
# EDGE CASES
# ==============================================================================

class TestEdgeCases:
    """Edge case tests."""

    def test_scan_nonexistent_vault(self):
        """Scanning non-existent path should return empty list."""
        result = scan_audio_vault(Path("/nonexistent/path/to/vault"))
        assert result == []

    def test_suggest_unknown_mood(self):
        """Unknown mood should still return samples."""
        # This will return all samples scored at 0, sorted arbitrarily
        # Just verify it doesn't crash
        result = suggest_samples_for_mood(
            "unknown_mood",
            vault_path=Path("/nonexistent"),
        )
        assert isinstance(result, list)

    def test_build_basic_drum_kit_empty_vault(self):
        """Building kit from empty vault should return empty kit."""
        kit = build_basic_drum_kit(vault_path=Path("/nonexistent"))
        assert kit.name == "Basic Drums"
        assert kit.samples == []
