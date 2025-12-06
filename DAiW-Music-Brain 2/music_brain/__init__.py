"""
Music Brain - Intelligent Music Analysis Toolkit

A Python package for music production analysis:
- Groove extraction and application
- Chord progression analysis
- Section detection
- Feel/timing analysis
- DAW integration
"""

__version__ = "0.2.0"
__author__ = "Sean Burdges"

from music_brain.groove import extract_groove, apply_groove, GrooveTemplate
from music_brain.structure import analyze_chords, detect_sections, ChordProgression
from music_brain.audio import analyze_feel, AudioFeatures

__all__ = [
    # Groove
    "extract_groove",
    "apply_groove", 
    "GrooveTemplate",
    # Structure
    "analyze_chords",
    "detect_sections",
    "ChordProgression",
    # Audio
    "analyze_feel",
    "AudioFeatures",
]
