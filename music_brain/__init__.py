"""
Music Brain - Intelligent Music Analysis Toolkit

A Python package for music production analysis:
- Groove extraction and application
- Chord progression analysis
- Section detection
- Feel/timing analysis
- DAW integration
- Therapy-to-music pipeline (Comprehensive Engine)
- Lyrical fragment generation (Lyric Mirror)
- Audio sample processing (Audio Refinery)
"""

__version__ = "0.3.0"
__author__ = "Sean Burdges"

from music_brain.groove import extract_groove, apply_groove, GrooveTemplate
from music_brain.structure import analyze_chords, detect_sections, ChordProgression
from music_brain.audio import analyze_feel, AudioFeatures

# Comprehensive engine exports
from music_brain.structure.comprehensive_engine import (
    AffectAnalyzer,
    TherapySession,
    HarmonyPlan,
    render_plan_to_midi,
)

# Groove engine (simple Drunken Drummer)
from music_brain.groove.engine import apply_groove as apply_groove_simple

# Lyric Mirror
from music_brain.lyrics.engine import LyricMirror, get_lyric_fragments

# Legacy text module (if exists)
try:
    from music_brain.text.lyrical_mirror import generate_lyrical_fragments
except ImportError:
    generate_lyrical_fragments = None

__all__ = [
    # Groove (file-based)
    "extract_groove",
    "apply_groove",
    "GrooveTemplate",
    # Groove (simple engine)
    "apply_groove_simple",
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
    # Lyric Mirror
    "LyricMirror",
    "get_lyric_fragments",
    # Legacy (may be None)
    "generate_lyrical_fragments",
]
