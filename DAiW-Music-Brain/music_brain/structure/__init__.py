"""
Structure Analysis - Chord, section, and progression analysis.

Analyze harmonic content, detect song sections, and work with
chord progressions for reharmonization and diagnosis.

Includes the Comprehensive Engine for therapy-based music generation.

TODO: Future integration planned for:
- Therapy-based music generation workflows
- Emotional mapping to harmonic structures
- Session-aware progression recommendations
"""

from music_brain.structure.chord import (
    analyze_chords,
    ChordProgression,
    Chord,
    detect_key,
)
from music_brain.structure.sections import (
    detect_sections,
    Section,
    SectionType,
)
from music_brain.structure.progression import (
    diagnose_progression,
    generate_reharmonizations,
    parse_progression_string,
)

__all__ = [
    # Chord analysis
    "analyze_chords",
    "ChordProgression", 
    "Chord",
    "detect_key",
    # Section detection
    "detect_sections",
    "Section",
    "SectionType",
    # Progression tools
    "diagnose_progression",
    "generate_reharmonizations",
    "parse_progression_string",
]
