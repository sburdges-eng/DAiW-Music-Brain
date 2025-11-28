"""
Instrument Classification
Maps MIDI channels, program numbers, and note ranges to instrument types.
"""

from typing import Optional

# MIDI Channel 9 (10 in 1-indexed) is drums
DRUM_CHANNEL = 9

# GM Drum Map (channel 9 note numbers)
GM_DRUM_MAP = {
    # Kicks
    35: 'kick', 36: 'kick',
    # Snares
    38: 'snare', 40: 'snare',
    # Rimshot/Sidestick
    37: 'rimshot',
    # Hi-hats
    42: 'hihat_closed', 44: 'hihat_pedal', 46: 'hihat_open',
    # Toms
    41: 'tom_low', 43: 'tom_low', 45: 'tom_mid', 47: 'tom_mid', 48: 'tom_high', 50: 'tom_high',
    # Cymbals
    49: 'crash', 57: 'crash',
    51: 'ride', 59: 'ride',
    52: 'china', 55: 'splash',
    # Percussion
    39: 'clap', 54: 'tambourine', 56: 'cowbell',
    60: 'bongo_high', 61: 'bongo_low',
    62: 'conga_mute', 63: 'conga_open', 64: 'conga_low',
    65: 'timbale_high', 66: 'timbale_low',
    # Shaker/misc
    69: 'cabasa', 70: 'maracas', 75: 'clave', 76: 'woodblock_high', 77: 'woodblock_low'
}

# Simplified drum categories
DRUM_CATEGORIES = {
    'kick': ['kick'],
    'snare': ['snare', 'rimshot', 'clap'],
    'hihat': ['hihat_closed', 'hihat_pedal', 'hihat_open'],
    'tom': ['tom_low', 'tom_mid', 'tom_high'],
    'cymbal': ['crash', 'ride', 'china', 'splash'],
    'percussion': ['tambourine', 'cowbell', 'bongo_high', 'bongo_low', 
                   'conga_mute', 'conga_open', 'conga_low', 
                   'timbale_high', 'timbale_low', 'cabasa', 'maracas',
                   'clave', 'woodblock_high', 'woodblock_low']
}

# GM Program Number ranges
GM_PROGRAMS = {
    (0, 7): 'keys',       # Piano
    (8, 15): 'keys',      # Chromatic Percussion
    (16, 23): 'organ',    # Organ
    (24, 31): 'guitar',   # Guitar
    (32, 39): 'bass',     # Bass
    (40, 47): 'strings',  # Strings
    (48, 55): 'strings',  # Ensemble
    (56, 63): 'brass',    # Brass
    (64, 71): 'brass',    # Reed
    (72, 79): 'lead',     # Pipe
    (80, 87): 'lead',     # Synth Lead
    (88, 95): 'pad',      # Synth Pad
    (96, 103): 'fx',      # Synth Effects
    (104, 111): 'ethnic', # Ethnic
    (112, 119): 'percussion', # Percussive
    (120, 127): 'fx'      # Sound Effects
}


def classify_drum(note: int) -> str:
    """Classify a drum note to its instrument type."""
    return GM_DRUM_MAP.get(note, 'percussion')


def get_drum_category(note: int) -> str:
    """Get broad category for drum note."""
    specific = classify_drum(note)
    for category, instruments in DRUM_CATEGORIES.items():
        if specific in instruments:
            return category
    return 'percussion'


def classify_program(program: int) -> str:
    """Classify GM program number to instrument type."""
    for (low, high), instrument in GM_PROGRAMS.items():
        if low <= program <= high:
            return instrument
    return 'unknown'


def classify_note(channel: int, pitch: int, program: Optional[int] = None) -> str:
    """
    Classify a note to its instrument type.
    
    Args:
        channel: MIDI channel (0-15)
        pitch: Note number (0-127)
        program: Optional program number for melodic instruments
    
    Returns:
        Instrument type string
    """
    if channel == DRUM_CHANNEL:
        return get_drum_category(pitch)
    
    if program is not None:
        return classify_program(program)
    
    # Fallback based on pitch range if no program info
    if pitch < 40:
        return 'bass'
    elif pitch < 60:
        return 'mid'  # Could be keys, guitar, etc.
    else:
        return 'high'  # Could be lead, strings, etc.


def is_drum_channel(channel: int) -> bool:
    """Check if channel is the drum channel."""
    return channel == DRUM_CHANNEL


def get_instrument_priority() -> list:
    """
    Get instruments in order of rhythmic importance.
    Used for groove extraction priority.
    """
    return [
        'kick',
        'snare', 
        'hihat',
        'bass',
        'percussion',
        'tom',
        'cymbal',
        'keys',
        'guitar',
        'strings',
        'brass',
        'lead',
        'pad'
    ]


# Instrument timing characteristics (default pocket positions)
INSTRUMENT_TIMING_DEFAULTS = {
    'kick': 0,       # On the grid - the anchor
    'snare': 0,      # Default on grid, genre-dependent
    'hihat': 0,      # Default on grid, often ahead
    'bass': 0,       # Usually with kick
    'keys': 0,
    'guitar': 0,
    'strings': 0,
    'brass': 0,
    'lead': 0,
    'pad': 0,
    'tom': 0,
    'cymbal': 0,
    'percussion': 0
}


def get_groove_instruments() -> list:
    """Get instruments that define groove (timing-critical)."""
    return ['kick', 'snare', 'hihat', 'bass', 'percussion']


def get_harmonic_instruments() -> list:
    """Get instruments that define harmony."""
    return ['keys', 'guitar', 'strings', 'brass', 'pad']


def get_melodic_instruments() -> list:
    """Get instruments that carry melody."""
    return ['lead', 'keys', 'guitar', 'brass', 'strings']
