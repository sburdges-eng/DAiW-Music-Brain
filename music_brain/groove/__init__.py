"""
Groove module - Drunken Drummer humanization engine.

Provides emotionally-driven MIDI humanization.
"""

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
    apply_groove,
)
from music_brain.groove.templates import get_genre_template, GENRE_TEMPLATES

__all__ = [
    # Drunken Drummer humanization
    "humanize_drums",
    "humanize_midi_file",
    "GrooveSettings",
    "settings_from_intent",
    "quick_humanize",
    "apply_groove",
    # Preset management
    "load_presets",
    "list_presets",
    "get_preset",
    "settings_from_preset",
    # Genre templates
    "get_genre_template",
    "GENRE_TEMPLATES",
]
