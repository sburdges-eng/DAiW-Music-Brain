"""
Audio Analysis - Analyze feel and characteristics of audio files.

Features:
- Feel/groove analysis
- Energy extraction
- Tempo detection
- Spectral analysis
- Reference track DNA analysis
"""

from music_brain.audio.feel import analyze_feel, AudioFeatures
from music_brain.audio.reference_dna import (
    analyze_reference,
    apply_reference_to_plan,
    ReferenceProfile,
)

__all__ = [
    "analyze_feel",
    "AudioFeatures",
    # Reference DNA
    "analyze_reference",
    "apply_reference_to_plan",
    "ReferenceProfile",
]
