# music_brain/structure/structure_engine.py
"""
Structure Engine - Section-based song architecture.

Provides higher-level song structure beyond bar-level tension curves:
- Section definitions (verse, chorus, bridge, etc.)
- Section ordering and arrangement
- Per-section parameter overrides

This module is optional and builds on top of comprehensive_engine.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class SectionType(Enum):
    """Standard song section types."""
    INTRO = "intro"
    VERSE = "verse"
    PRE_CHORUS = "pre_chorus"
    CHORUS = "chorus"
    POST_CHORUS = "post_chorus"
    BRIDGE = "bridge"
    BREAKDOWN = "breakdown"
    BUILD = "build"
    DROP = "drop"
    OUTRO = "outro"


@dataclass
class Section:
    """A single section of a song."""
    section_type: SectionType
    length_bars: int = 8
    intensity: float = 1.0  # 0.0-1.5 multiplier for dynamics
    tempo_offset: int = 0   # BPM offset from base tempo
    chord_override: Optional[List[str]] = None  # Override progression
    label: str = ""  # Custom label (e.g., "Verse 1", "Final Chorus")

    def __post_init__(self):
        if not self.label:
            self.label = self.section_type.value.replace("_", " ").title()


@dataclass
class SongStructure:
    """Complete song structure with ordered sections."""
    sections: List[Section] = field(default_factory=list)
    base_tempo: int = 120
    key: str = "C"
    mode: str = "major"

    @property
    def total_bars(self) -> int:
        """Total bars across all sections."""
        return sum(s.length_bars for s in self.sections)

    @property
    def section_boundaries(self) -> List[Tuple[int, Section]]:
        """Return list of (start_bar, section) tuples."""
        boundaries = []
        current_bar = 0
        for section in self.sections:
            boundaries.append((current_bar, section))
            current_bar += section.length_bars
        return boundaries

    def get_section_at_bar(self, bar: int) -> Optional[Section]:
        """Get the section containing a specific bar."""
        current_bar = 0
        for section in self.sections:
            if current_bar <= bar < current_bar + section.length_bars:
                return section
            current_bar += section.length_bars
        return None


# =============================================================================
# PRESET STRUCTURES
# =============================================================================

def create_simple_structure() -> SongStructure:
    """Simple verse-chorus structure (32 bars)."""
    return SongStructure(
        sections=[
            Section(SectionType.INTRO, length_bars=4, intensity=0.6),
            Section(SectionType.VERSE, length_bars=8, intensity=0.8, label="Verse 1"),
            Section(SectionType.CHORUS, length_bars=8, intensity=1.2),
            Section(SectionType.VERSE, length_bars=8, intensity=0.85, label="Verse 2"),
            Section(SectionType.OUTRO, length_bars=4, intensity=0.5),
        ]
    )


def create_standard_structure() -> SongStructure:
    """Standard pop structure with bridge (48 bars)."""
    return SongStructure(
        sections=[
            Section(SectionType.INTRO, length_bars=4, intensity=0.5),
            Section(SectionType.VERSE, length_bars=8, intensity=0.7, label="Verse 1"),
            Section(SectionType.CHORUS, length_bars=8, intensity=1.0, label="Chorus 1"),
            Section(SectionType.VERSE, length_bars=8, intensity=0.75, label="Verse 2"),
            Section(SectionType.CHORUS, length_bars=8, intensity=1.1, label="Chorus 2"),
            Section(SectionType.BRIDGE, length_bars=8, intensity=0.9),
            Section(SectionType.CHORUS, length_bars=8, intensity=1.3, label="Final Chorus"),
            Section(SectionType.OUTRO, length_bars=4, intensity=0.4),
        ]
    )


def create_build_drop_structure() -> SongStructure:
    """EDM-style build and drop (32 bars)."""
    return SongStructure(
        sections=[
            Section(SectionType.INTRO, length_bars=8, intensity=0.4),
            Section(SectionType.BUILD, length_bars=8, intensity=0.8),
            Section(SectionType.DROP, length_bars=8, intensity=1.4),
            Section(SectionType.BREAKDOWN, length_bars=4, intensity=0.5),
            Section(SectionType.BUILD, length_bars=4, intensity=0.9, label="Build 2"),
            Section(SectionType.DROP, length_bars=8, intensity=1.5, label="Final Drop"),
        ]
    )


def create_minimal_structure() -> SongStructure:
    """Minimal structure for sketches (16 bars)."""
    return SongStructure(
        sections=[
            Section(SectionType.VERSE, length_bars=8, intensity=0.8),
            Section(SectionType.CHORUS, length_bars=8, intensity=1.1),
        ]
    )


def create_climactic_structure() -> SongStructure:
    """Single build to climax (24 bars)."""
    return SongStructure(
        sections=[
            Section(SectionType.INTRO, length_bars=4, intensity=0.3),
            Section(SectionType.VERSE, length_bars=8, intensity=0.5, label="Build"),
            Section(SectionType.BUILD, length_bars=4, intensity=0.8),
            Section(SectionType.CHORUS, length_bars=4, intensity=1.4, label="Climax"),
            Section(SectionType.OUTRO, length_bars=4, intensity=0.6, label="Resolution"),
        ]
    )


# =============================================================================
# STRUCTURE PRESETS MAP
# =============================================================================

STRUCTURE_PRESETS = {
    "simple": create_simple_structure,
    "standard": create_standard_structure,
    "build_drop": create_build_drop_structure,
    "minimal": create_minimal_structure,
    "climactic": create_climactic_structure,
}


def create_structure_from_preset(preset_name: str) -> SongStructure:
    """Create a song structure from a preset name."""
    if preset_name not in STRUCTURE_PRESETS:
        # Default to simple
        preset_name = "simple"
    return STRUCTURE_PRESETS[preset_name]()


def structure_to_tension_map(structure: SongStructure) -> Dict[int, float]:
    """
    Convert song structure to bar-level tension map.

    Returns a dict mapping bar number to intensity value.
    """
    tension_map = {}
    current_bar = 0

    for section in structure.sections:
        for bar_offset in range(section.length_bars):
            bar_num = current_bar + bar_offset
            tension_map[bar_num] = section.intensity
        current_bar += section.length_bars

    return tension_map


def get_section_labels(structure: SongStructure) -> List[Tuple[int, str]]:
    """
    Get section labels with their start bars.

    Useful for generating MIDI markers or display.
    """
    labels = []
    current_bar = 0

    for section in structure.sections:
        labels.append((current_bar, section.label))
        current_bar += section.length_bars

    return labels
