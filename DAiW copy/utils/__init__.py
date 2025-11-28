"""
Utility modules for MIDI processing.
"""

from .ppq import (
    STANDARD_PPQ, normalize_ticks, scale_ticks, scale_template,
    ticks_per_bar, ticks_to_beats, grid_position, quantize_to_grid,
    ticks_to_ms, ms_to_ticks
)
from .midi_io import (
    load_midi, save_midi, modify_notes_safe,
    MidiData, MidiNote, MidiEvent, TrackData,
    get_notes_by_instrument, get_notes_by_track
)
from .instruments import (
    classify_note, get_drum_category, is_drum_channel,
    get_groove_instruments, GM_DRUM_MAP, DRUM_CATEGORIES
)
from .orchestral import (
    OrchestralAnalyzer, validate_orchestral, is_orchestral_template,
    OrchestralValidation
)

__all__ = [
    # PPQ
    'STANDARD_PPQ', 'normalize_ticks', 'scale_ticks', 'scale_template',
    'ticks_per_bar', 'ticks_to_beats', 'grid_position', 'quantize_to_grid',
    'ticks_to_ms', 'ms_to_ticks',
    # MIDI I/O
    'load_midi', 'save_midi', 'modify_notes_safe',
    'MidiData', 'MidiNote', 'MidiEvent', 'TrackData',
    'get_notes_by_instrument', 'get_notes_by_track',
    # Instruments
    'classify_note', 'get_drum_category', 'is_drum_channel',
    'get_groove_instruments', 'GM_DRUM_MAP', 'DRUM_CATEGORIES',
    # Orchestral
    'OrchestralAnalyzer', 'validate_orchestral', 'is_orchestral_template',
    'OrchestralValidation',
]
