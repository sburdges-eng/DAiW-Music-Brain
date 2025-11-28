"""
groove/engine.py - Alias module for groove_engine.py
====================================================

This module provides a cleaner import path for the groove engine.
All functionality is re-exported from groove_engine.py.

Usage:
    from music_brain.groove.engine import apply_groove, GrooveSettings
"""

# Re-export everything from groove_engine
from music_brain.groove.groove_engine import (
    # Constants
    GHOST_NOTE_PROBABILITY,
    ACCENT_THRESHOLD,
    MAX_TICKS_DRIFT,
    HUMAN_LATENCY_BIAS,
    VELOCITY_MIN,
    VELOCITY_MAX,
    MAX_DROPOUT_PROB,
    DRUM_NOTES,
    PROTECTION_LEVELS,
    # Data classes
    GrooveSettings,
    # Core functions
    apply_groove,
    humanize_drums,
    humanize_midi_file,
    # Intent integration
    settings_from_intent,
    # Convenience functions
    quick_humanize,
    # Preset functions
    load_presets,
    list_presets,
    get_preset,
    settings_from_preset,
)

__all__ = [
    # Constants
    "GHOST_NOTE_PROBABILITY",
    "ACCENT_THRESHOLD",
    "MAX_TICKS_DRIFT",
    "HUMAN_LATENCY_BIAS",
    "VELOCITY_MIN",
    "VELOCITY_MAX",
    "MAX_DROPOUT_PROB",
    "DRUM_NOTES",
    "PROTECTION_LEVELS",
    # Data classes
    "GrooveSettings",
    # Core functions
    "apply_groove",
    "humanize_drums",
    "humanize_midi_file",
    # Intent integration
    "settings_from_intent",
    # Convenience functions
    "quick_humanize",
    # Preset functions
    "load_presets",
    "list_presets",
    "get_preset",
    "settings_from_preset",
]
