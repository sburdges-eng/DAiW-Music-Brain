"""
Groove extraction and application module.

Extract timing/velocity patterns from MIDI files and apply them to other tracks.

Includes the V2 "Drunken Drummer" engine for humanization via
Gaussian jitter + dropout + velocity shaping.
"""

from music_brain.groove.extractor import extract_groove, GrooveTemplate
from music_brain.groove.applicator import apply_groove
from music_brain.groove.templates import get_genre_template, GENRE_TEMPLATES

# V2 Engine (Drunken Drummer humanization)
from music_brain.groove.engine import apply_groove as apply_groove_v2

__all__ = [
    "extract_groove",
    "apply_groove",
    "apply_groove_v2",
    "GrooveTemplate",
    "get_genre_template",
    "GENRE_TEMPLATES",
]
