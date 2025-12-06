"""
Music Brain - Intelligent Music Analysis Toolkit

A Python package for music production analysis:
- Groove extraction and application
- Chord progression analysis
- Section detection
- Feel/timing analysis
- DAW integration
- Therapy-to-music pipeline (Comprehensive Engine)
- Lyrical fragment generation
- Reference track DNA analysis
"""

__version__ = "1.0.0"
__author__ = "Sean Burdges"
__app_name__ = "iDAW"
__codename__ = "Dual Engine"

from music_brain.groove import extract_groove, apply_groove, GrooveTemplate
from music_brain.structure import analyze_chords, detect_sections, ChordProgression
from music_brain.audio import analyze_feel, AudioFeatures

# New comprehensive engine exports
from music_brain.structure.comprehensive_engine import (
    AffectAnalyzer,
    TherapySession,
    HarmonyPlan,
    render_plan_to_midi,
)
from music_brain.groove_engine import apply_groove as apply_groove_events
from music_brain.text.lyrical_mirror import generate_lyrical_fragments

__all__ = [
    # Groove (file-based)
    "extract_groove",
    "apply_groove",
    "GrooveTemplate",
    # Groove (event-based)
    "apply_groove_events",
    # Structure
    "analyze_chords",
    "detect_sections",
    "ChordProgression",
    # Audio
    "analyze_feel",
    "AudioFeatures",
    # Comprehensive Engine
    "AffectAnalyzer",
    "TherapySession",
    "HarmonyPlan",
    "render_plan_to_midi",
    # Text/Lyrical
    "generate_lyrical_fragments",
]
