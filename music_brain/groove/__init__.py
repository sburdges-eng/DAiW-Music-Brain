"""
Groove extraction and application module.

Extract timing/velocity patterns from MIDI files and apply them to other tracks.

Includes:
- GrooveTemplate extraction from existing MIDI
- Genre-based groove templates
- "Drunken Drummer" humanization engine for emotionally-driven processing
"""

from music_brain.groove.extractor import extract_groove, GrooveTemplate
from music_brain.groove.applicator import apply_groove, humanize
from music_brain.groove.templates import get_genre_template, GENRE_TEMPLATES
from music_brain.groove.groove_engine import (
    humanize_drums,
    humanize_midi_file,
    GrooveSettings,
    settings_from_intent,
    quick_humanize,
    load_presets,
    list_presets,
    get_preset,
    settings_from_preset,
)
# Re-export apply_groove from engine for consistency
from music_brain.groove.engine import apply_groove as groove_engine_apply

__all__ = [
    # Extraction
    "extract_groove",
    "GrooveTemplate",
    # Application
    "apply_groove",
    "humanize",
    # Genre templates
    "get_genre_template",
    "GENRE_TEMPLATES",
    # Drunken Drummer humanization
    "humanize_drums",
    "humanize_midi_file",
    "GrooveSettings",
    "settings_from_intent",
    "quick_humanize",
    # Preset management
    "load_presets",
    "list_presets",
    "get_preset",
    "settings_from_preset",
]
