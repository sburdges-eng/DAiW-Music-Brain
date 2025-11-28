"""
Tests for the Reference DNA Analyzer module.

Covers: ReferenceProfile dataclass, analyze_reference, apply_reference_to_plan,
compare_profiles, and key estimation.

Note: Most tests require librosa. Tests are skipped when unavailable.

Run with: pytest tests/test_reference_dna.py -v
"""

import pytest
from dataclasses import dataclass
from pathlib import Path

from music_brain.audio.reference_dna import (
    ReferenceProfile,
    NOTE_NAMES,
    MAJOR_PROFILE,
    MINOR_PROFILE,
    LIBROSA_AVAILABLE,
)

# Conditionally import functions that require librosa
if LIBROSA_AVAILABLE:
    from music_brain.audio.reference_dna import (
        analyze_reference,
        apply_reference_to_plan,
        compare_profiles,
        _estimate_key,
    )


# ==============================================================================
# REFERENCE PROFILE DATACLASS TESTS (No librosa required)
# ==============================================================================

class TestReferenceProfile:
    """Test ReferenceProfile dataclass."""

    def test_creation(self):
        profile = ReferenceProfile(
            tempo_bpm=120.0,
            key_root="C",
            key_mode="major",
            brightness=0.5,
            energy=0.6,
            warmth=0.4,
        )
        assert profile.tempo_bpm == 120.0
        assert profile.key_root == "C"
        assert profile.key_mode == "major"

    def test_none_key_values(self):
        profile = ReferenceProfile(
            tempo_bpm=100.0,
            key_root=None,
            key_mode=None,
            brightness=0.3,
            energy=0.5,
            warmth=0.7,
        )
        assert profile.key_root is None
        assert profile.key_mode is None

    def test_repr_with_key(self):
        profile = ReferenceProfile(
            tempo_bpm=95.0,
            key_root="Am",
            key_mode="minor",
            brightness=0.4,
            energy=0.5,
            warmth=0.6,
        )
        repr_str = repr(profile)

        assert "95.0" in repr_str
        assert "Am" in repr_str
        assert "0.4" in repr_str or "brightness" in repr_str

    def test_repr_without_key(self):
        profile = ReferenceProfile(
            tempo_bpm=100.0,
            key_root=None,
            key_mode=None,
            brightness=0.5,
            energy=0.5,
            warmth=0.5,
        )
        repr_str = repr(profile)

        assert "100.0" in repr_str
        assert "unknown" in repr_str

    def test_normalized_values_range(self):
        """brightness, energy, warmth should typically be 0-1."""
        profile = ReferenceProfile(
            tempo_bpm=120.0,
            key_root="G",
            key_mode="major",
            brightness=0.8,
            energy=0.7,
            warmth=0.3,
        )
        assert 0.0 <= profile.brightness <= 1.0
        assert 0.0 <= profile.energy <= 1.0
        assert 0.0 <= profile.warmth <= 1.0


# ==============================================================================
# CONSTANTS TESTS
# ==============================================================================

class TestConstants:
    """Test module constants."""

    def test_note_names(self):
        assert len(NOTE_NAMES) == 12
        assert NOTE_NAMES[0] == 'C'
        assert NOTE_NAMES[9] == 'A'
        assert 'C#' in NOTE_NAMES
        assert 'F#' in NOTE_NAMES

    def test_major_profile(self):
        assert len(MAJOR_PROFILE) == 12
        assert all(isinstance(v, (int, float)) for v in MAJOR_PROFILE)
        # Tonic (C) should be strong
        assert MAJOR_PROFILE[0] > MAJOR_PROFILE[1]

    def test_minor_profile(self):
        assert len(MINOR_PROFILE) == 12
        assert all(isinstance(v, (int, float)) for v in MINOR_PROFILE)
        # Tonic should be strong
        assert MINOR_PROFILE[0] > MINOR_PROFILE[1]


# ==============================================================================
# COMPARE PROFILES TESTS (Requires librosa for profile creation)
# ==============================================================================

@pytest.mark.skipif(not LIBROSA_AVAILABLE, reason="librosa not installed")
class TestCompareProfiles:
    """Test compare_profiles function."""

    @pytest.fixture
    def profile_a(self):
        return ReferenceProfile(
            tempo_bpm=120.0,
            key_root="C",
            key_mode="major",
            brightness=0.5,
            energy=0.6,
            warmth=0.4,
        )

    @pytest.fixture
    def profile_b_similar(self):
        return ReferenceProfile(
            tempo_bpm=122.0,  # Close tempo
            key_root="C",    # Same key
            key_mode="major",
            brightness=0.52,  # Similar brightness
            energy=0.58,
            warmth=0.42,
        )

    @pytest.fixture
    def profile_c_different(self):
        return ReferenceProfile(
            tempo_bpm=80.0,   # Very different tempo
            key_root="F#",   # Different key
            key_mode="minor",
            brightness=0.9,   # Very different brightness
            energy=0.2,
            warmth=0.8,
        )

    def test_returns_dict(self, profile_a, profile_b_similar):
        result = compare_profiles(profile_a, profile_b_similar)
        assert isinstance(result, dict)

    def test_has_expected_keys(self, profile_a, profile_b_similar):
        result = compare_profiles(profile_a, profile_b_similar)

        expected_keys = ["tempo", "key", "brightness", "energy", "warmth", "overall"]
        for key in expected_keys:
            assert key in result

    def test_similar_profiles_high_similarity(self, profile_a, profile_b_similar):
        result = compare_profiles(profile_a, profile_b_similar)

        assert result["overall"] > 0.8
        assert result["tempo"] > 0.9  # Very close tempo
        assert result["key"] == 1.0   # Same key

    def test_different_profiles_low_similarity(self, profile_a, profile_c_different):
        result = compare_profiles(profile_a, profile_c_different)

        assert result["overall"] < 0.6
        assert result["key"] == 0.0   # Different key

    def test_identical_profiles_perfect_similarity(self, profile_a):
        result = compare_profiles(profile_a, profile_a)

        assert result["overall"] == 1.0
        assert result["tempo"] == 1.0
        assert result["brightness"] == 1.0

    def test_unknown_key_gets_half_similarity(self, profile_a):
        profile_unknown = ReferenceProfile(
            tempo_bpm=120.0,
            key_root=None,
            key_mode=None,
            brightness=0.5,
            energy=0.6,
            warmth=0.4,
        )
        result = compare_profiles(profile_a, profile_unknown)

        assert result["key"] == 0.5

    def test_similarity_values_in_range(self, profile_a, profile_c_different):
        result = compare_profiles(profile_a, profile_c_different)

        for key, value in result.items():
            assert 0.0 <= value <= 1.0


# ==============================================================================
# APPLY REFERENCE TO PLAN TESTS
# ==============================================================================

@pytest.mark.skipif(not LIBROSA_AVAILABLE, reason="librosa not installed")
class TestApplyReferenceToPlan:
    """Test apply_reference_to_plan function."""

    @dataclass
    class MockPlan:
        """Mock plan object for testing."""
        tempo_bpm: int = 120
        root_note: str = "C"
        mode: str = "ionian"
        complexity: float = 0.5
        vulnerability: float = 0.5

    def test_none_profile_does_nothing(self):
        plan = self.MockPlan()
        original_tempo = plan.tempo_bpm

        apply_reference_to_plan(plan, None)

        assert plan.tempo_bpm == original_tempo

    def test_applies_tempo_blend(self):
        plan = self.MockPlan(tempo_bpm=100)
        profile = ReferenceProfile(
            tempo_bpm=140.0,
            key_root="G",
            key_mode="major",
            brightness=0.5,
            energy=0.5,
            warmth=0.5,
        )

        apply_reference_to_plan(plan, profile)

        # Should be blended: 70% reference + 30% original
        # 0.7 * 140 + 0.3 * 100 = 98 + 30 = 128
        assert plan.tempo_bpm == 128

    def test_applies_key_root(self):
        plan = self.MockPlan(root_note="C")
        profile = ReferenceProfile(
            tempo_bpm=120.0,
            key_root="Am",
            key_mode="minor",
            brightness=0.5,
            energy=0.5,
            warmth=0.5,
        )

        apply_reference_to_plan(plan, profile)

        assert plan.root_note == "Am"

    def test_applies_mode_from_key_mode_minor(self):
        plan = self.MockPlan(mode="ionian")
        profile = ReferenceProfile(
            tempo_bpm=120.0,
            key_root="A",
            key_mode="minor",
            brightness=0.5,
            energy=0.5,
            warmth=0.5,
        )

        apply_reference_to_plan(plan, profile)

        assert plan.mode == "aeolian"

    def test_applies_mode_from_key_mode_major(self):
        plan = self.MockPlan(mode="aeolian")
        profile = ReferenceProfile(
            tempo_bpm=120.0,
            key_root="C",
            key_mode="major",
            brightness=0.5,
            energy=0.5,
            warmth=0.5,
        )

        apply_reference_to_plan(plan, profile)

        assert plan.mode == "ionian"

    def test_brightness_affects_complexity(self):
        plan = self.MockPlan(complexity=0.5)
        profile = ReferenceProfile(
            tempo_bpm=120.0,
            key_root=None,
            key_mode=None,
            brightness=0.9,  # High brightness
            energy=0.5,
            warmth=0.5,
        )

        apply_reference_to_plan(plan, profile)

        # High brightness should increase complexity
        assert plan.complexity > 0.5

    def test_warmth_affects_vulnerability(self):
        plan = self.MockPlan(vulnerability=0.5)
        profile = ReferenceProfile(
            tempo_bpm=120.0,
            key_root=None,
            key_mode=None,
            brightness=0.5,
            energy=0.5,
            warmth=0.9,  # High warmth
        )

        apply_reference_to_plan(plan, profile)

        # High warmth should increase vulnerability
        assert plan.vulnerability > 0.5

    def test_complexity_clamped_to_range(self):
        plan = self.MockPlan(complexity=0.95)
        profile = ReferenceProfile(
            tempo_bpm=120.0,
            key_root=None,
            key_mode=None,
            brightness=1.0,  # Maximum brightness
            energy=0.5,
            warmth=0.5,
        )

        apply_reference_to_plan(plan, profile)

        assert plan.complexity <= 1.0

    def test_vulnerability_clamped_to_range(self):
        plan = self.MockPlan(vulnerability=0.05)
        profile = ReferenceProfile(
            tempo_bpm=120.0,
            key_root=None,
            key_mode=None,
            brightness=0.5,
            energy=0.5,
            warmth=0.0,  # Minimum warmth
        )

        apply_reference_to_plan(plan, profile)

        assert plan.vulnerability >= 0.0


# ==============================================================================
# ANALYZE REFERENCE TESTS (Requires librosa and actual audio)
# ==============================================================================

@pytest.mark.skipif(not LIBROSA_AVAILABLE, reason="librosa not installed")
class TestAnalyzeReference:
    """Test analyze_reference function."""

    def test_nonexistent_file_returns_none(self):
        result = analyze_reference(Path("/nonexistent/audio.wav"))
        assert result is None

    def test_accepts_path_object(self):
        # Should not crash with Path object
        result = analyze_reference(Path("/nonexistent/test.wav"))
        assert result is None

    def test_accepts_string_path(self):
        # Should not crash with string path
        result = analyze_reference("/nonexistent/test.wav")
        assert result is None


# ==============================================================================
# IMPORT AVAILABILITY TESTS
# ==============================================================================

class TestImportAvailability:
    """Test that availability flags work correctly."""

    def test_librosa_available_is_bool(self):
        assert isinstance(LIBROSA_AVAILABLE, bool)

    def test_can_import_dataclass_without_librosa(self):
        """ReferenceProfile should be importable even without librosa."""
        from music_brain.audio.reference_dna import ReferenceProfile
        profile = ReferenceProfile(
            tempo_bpm=120.0,
            key_root=None,
            key_mode=None,
            brightness=0.5,
            energy=0.5,
            warmth=0.5,
        )
        assert profile is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
