"""
Music Brain - Intelligent Music Analysis Toolkit

A Python package for music production analysis:
- Groove humanization (Drunken Drummer engine)
- Chord progression analysis
- Therapy-to-music pipeline (Comprehensive Engine)
"""

__version__ = "0.3.0"
__author__ = "Sean Burdges"

# Groove humanization
from music_brain.groove import (
    humanize_drums,
    GrooveSettings,
    apply_groove,
)

# Structure / Harmony
from music_brain.structure import (
    analyze_chords,
    ChordProgression,
    diagnose_progression,
    parse_progression_string,
)

# Comprehensive engine
from music_brain.structure.comprehensive_engine import (
    AffectAnalyzer,
    TherapySession,
    HarmonyPlan,
    render_plan_to_midi,
)

__all__ = [
    # Groove
    "humanize_drums",
    "GrooveSettings",
    "apply_groove",
    # Structure
    "analyze_chords",
    "ChordProgression",
    "diagnose_progression",
    "parse_progression_string",
    # Comprehensive Engine
    "AffectAnalyzer",
    "TherapySession",
    "HarmonyPlan",
    "render_plan_to_midi",
]
