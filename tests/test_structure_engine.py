"""
Tests for the Structure Engine - Song form generation.

Covers: StructuralArchitect, section generation, form archetypes.

Run with: pytest tests/test_structure_engine.py -v
"""

import pytest
from music_brain.structure.structure_engine import (
    StructuralArchitect,
    Section,
    generate_structure_for_plan,
)


@pytest.fixture
def architect():
    """Create a StructuralArchitect with default BPM."""
    return StructuralArchitect(bpm=120)


# ==============================================================================
# SECTION DATACLASS TESTS
# ==============================================================================

def test_section_creation():
    """Section dataclass should hold form data."""
    section = Section(
        name="verse",
        bars=8,
        energy=0.6,
        entropy=0.3,
        harmonic_load=0.5,
    )

    assert section.name == "verse"
    assert section.bars == 8
    assert section.energy == 0.6
    assert section.entropy == 0.3
    assert section.harmonic_load == 0.5


# ==============================================================================
# STRUCTURAL ARCHITECT TESTS
# ==============================================================================

def test_architect_creation():
    """StructuralArchitect should initialize with BPM."""
    arch = StructuralArchitect(bpm=140)
    assert arch.bpm == 140


def test_architect_default_creation():
    """StructuralArchitect should have default BPM."""
    arch = StructuralArchitect()
    assert arch.bpm == 100


def test_architect_available_forms():
    """Should have predefined form archetypes."""
    arch = StructuralArchitect()
    forms = list(arch.FORMS.keys())

    assert "pop_standard" in forms
    assert "electronic_build" in forms
    assert "punk_assault" in forms
    assert "ballad" in forms


def test_generate_map_pop_standard(architect):
    """Should generate valid pop_standard structure."""
    structure = architect.generate_map("pop_standard")

    assert len(structure) > 0

    # Each entry should have required fields
    for entry in structure:
        assert "bar_index" in entry
        assert "velocity_target" in entry
        assert "section" in entry


def test_generate_map_with_total_bars(architect):
    """Should respect total_bars parameter."""
    structure = architect.generate_map("pop_standard", total_bars=32)

    # Should have exactly 32 entries
    assert len(structure) == 32

    # Bar indices should be sequential
    for i, entry in enumerate(structure):
        assert entry["bar_index"] == i


def test_generate_map_electronic_build(architect):
    """Should generate electronic_build structure."""
    structure = architect.generate_map("electronic_build", total_bars=64)

    assert len(structure) == 64

    # Should have drop section with high velocity
    drop_entries = [e for e in structure if e["section"] == "Drop"]
    if drop_entries:
        avg_velocity = sum(e["velocity_target"] for e in drop_entries) / len(drop_entries)
        assert avg_velocity >= 100  # Drops should be energetic


def test_generate_map_punk_assault(architect):
    """Should generate punk_assault structure."""
    structure = architect.generate_map("punk_assault", total_bars=32)

    assert len(structure) == 32

    # Punk should have generally high energy
    avg_velocity = sum(e["velocity_target"] for e in structure) / len(structure)
    assert avg_velocity >= 60  # Punk is energetic


def test_generate_map_ballad(architect):
    """Should generate ballad structure."""
    structure = architect.generate_map("ballad", total_bars=48)

    assert len(structure) == 48

    # Ballad should have some variation
    velocities = [e["velocity_target"] for e in structure]
    assert max(velocities) != min(velocities)


def test_generate_map_unknown_form(architect):
    """Unknown form should return default (pop_standard)."""
    structure = architect.generate_map("unknown_form", total_bars=16)

    assert len(structure) == 16


def test_get_section_boundaries(architect):
    """Should identify section transitions."""
    structure = architect.generate_map("pop_standard", total_bars=64)
    boundaries = architect.get_section_boundaries(structure)

    assert len(boundaries) > 0

    for boundary in boundaries:
        assert "start_bar" in boundary
        assert "end_bar" in boundary
        assert "name" in boundary


def test_get_form_for_mood(architect):
    """Should map moods to appropriate forms."""
    # Test various moods
    assert architect.get_form_for_mood("rage") == "punk_assault"
    assert architect.get_form_for_mood("grief") == "ballad"
    assert architect.get_form_for_mood("neutral") == "pop_standard"


def test_get_form_for_unknown_mood(architect):
    """Unknown mood should return default form."""
    form = architect.get_form_for_mood("unknown_mood")
    assert form == "pop_standard"


# ==============================================================================
# GENERATE STRUCTURE FOR PLAN TESTS
# ==============================================================================

def test_generate_structure_for_plan_basic():
    """Should generate structure from mood and length."""
    structure = generate_structure_for_plan(
        mood="hope",
        length_bars=32,
        bpm=120
    )

    assert structure is not None
    assert len(structure) == 32


def test_generate_structure_for_plan_with_mood():
    """Should use mood to influence form selection."""
    grief_structure = generate_structure_for_plan("grief", 48)
    rage_structure = generate_structure_for_plan("rage", 48)

    # Both should have valid structure
    assert len(grief_structure) == 48
    assert len(rage_structure) == 48


# ==============================================================================
# EDGE CASES
# ==============================================================================

def test_generate_map_zero_bars(architect):
    """Zero bars should return empty structure."""
    structure = architect.generate_map("pop_standard", total_bars=0)

    assert structure == []


def test_generate_map_very_long(architect):
    """Should handle very long songs."""
    structure = architect.generate_map("pop_standard", total_bars=256)

    assert len(structure) == 256
    assert all(e["bar_index"] < 256 for e in structure)


def test_architect_with_extreme_bpm():
    """Should handle extreme tempos."""
    slow = StructuralArchitect(bpm=40)
    fast = StructuralArchitect(bpm=200)

    slow_structure = slow.generate_map("ballad", total_bars=16)
    fast_structure = fast.generate_map("punk_assault", total_bars=16)

    assert len(slow_structure) == 16
    assert len(fast_structure) == 16


def test_section_velocity_range(architect):
    """Velocity targets should be in valid range."""
    structure = architect.generate_map("pop_standard", total_bars=64)

    for entry in structure:
        assert 20 <= entry["velocity_target"] <= 120


def test_section_jitter_range(architect):
    """Jitter sigma should be in 0-1 range."""
    structure = architect.generate_map("pop_standard", total_bars=64)

    for entry in structure:
        assert 0.0 <= entry["jitter_sigma"] <= 1.0


def test_section_harmonic_density_range(architect):
    """Harmonic density should be in 0-1 range."""
    structure = architect.generate_map("pop_standard", total_bars=64)

    for entry in structure:
        assert 0.0 <= entry["harmonic_density"] <= 1.0
