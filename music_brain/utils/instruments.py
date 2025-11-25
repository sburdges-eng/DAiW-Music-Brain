"""
Instrument Mappings - General MIDI drum and instrument mappings.

Standard GM (General MIDI) program numbers and drum note mappings
for consistent instrument identification across DAWs.
"""

# General MIDI Drum Map (Channel 10, notes 35-81)
GM_DRUMS = {
    35: "Acoustic Bass Drum",
    36: "Bass Drum 1",
    37: "Side Stick",
    38: "Acoustic Snare",
    39: "Hand Clap",
    40: "Electric Snare",
    41: "Low Floor Tom",
    42: "Closed Hi-Hat",
    43: "High Floor Tom",
    44: "Pedal Hi-Hat",
    45: "Low Tom",
    46: "Open Hi-Hat",
    47: "Low-Mid Tom",
    48: "Hi-Mid Tom",
    49: "Crash Cymbal 1",
    50: "High Tom",
    51: "Ride Cymbal 1",
    52: "Chinese Cymbal",
    53: "Ride Bell",
    54: "Tambourine",
    55: "Splash Cymbal",
    56: "Cowbell",
    57: "Crash Cymbal 2",
    58: "Vibraslap",
    59: "Ride Cymbal 2",
    60: "Hi Bongo",
    61: "Low Bongo",
    62: "Mute Hi Conga",
    63: "Open Hi Conga",
    64: "Low Conga",
    65: "High Timbale",
    66: "Low Timbale",
    67: "High Agogo",
    68: "Low Agogo",
    69: "Cabasa",
    70: "Maracas",
    71: "Short Whistle",
    72: "Long Whistle",
    73: "Short Guiro",
    74: "Long Guiro",
    75: "Claves",
    76: "Hi Wood Block",
    77: "Low Wood Block",
    78: "Mute Cuica",
    79: "Open Cuica",
    80: "Mute Triangle",
    81: "Open Triangle",
}

# Simplified drum categories for analysis
DRUM_CATEGORIES = {
    "kick": [35, 36],
    "snare": [38, 40],
    "hihat_closed": [42],
    "hihat_open": [46],
    "hihat_pedal": [44],
    "tom_low": [41, 43, 45],
    "tom_mid": [47, 48],
    "tom_high": [50],
    "crash": [49, 57],
    "ride": [51, 59],
    "ride_bell": [53],
    "percussion": list(range(54, 82)),
}

# General MIDI Instrument Programs (0-127)
GM_INSTRUMENTS = {
    # Piano (0-7)
    0: "Acoustic Grand Piano",
    1: "Bright Acoustic Piano",
    2: "Electric Grand Piano",
    3: "Honky-tonk Piano",
    4: "Electric Piano 1",
    5: "Electric Piano 2",
    6: "Harpsichord",
    7: "Clavinet",
    
    # Chromatic Percussion (8-15)
    8: "Celesta",
    9: "Glockenspiel",
    10: "Music Box",
    11: "Vibraphone",
    12: "Marimba",
    13: "Xylophone",
    14: "Tubular Bells",
    15: "Dulcimer",
    
    # Organ (16-23)
    16: "Drawbar Organ",
    17: "Percussive Organ",
    18: "Rock Organ",
    19: "Church Organ",
    20: "Reed Organ",
    21: "Accordion",
    22: "Harmonica",
    23: "Tango Accordion",
    
    # Guitar (24-31)
    24: "Acoustic Guitar (nylon)",
    25: "Acoustic Guitar (steel)",
    26: "Electric Guitar (jazz)",
    27: "Electric Guitar (clean)",
    28: "Electric Guitar (muted)",
    29: "Overdriven Guitar",
    30: "Distortion Guitar",
    31: "Guitar Harmonics",
    
    # Bass (32-39)
    32: "Acoustic Bass",
    33: "Electric Bass (finger)",
    34: "Electric Bass (pick)",
    35: "Fretless Bass",
    36: "Slap Bass 1",
    37: "Slap Bass 2",
    38: "Synth Bass 1",
    39: "Synth Bass 2",
    
    # Strings (40-47)
    40: "Violin",
    41: "Viola",
    42: "Cello",
    43: "Contrabass",
    44: "Tremolo Strings",
    45: "Pizzicato Strings",
    46: "Orchestral Harp",
    47: "Timpani",
    
    # Ensemble (48-55)
    48: "String Ensemble 1",
    49: "String Ensemble 2",
    50: "Synth Strings 1",
    51: "Synth Strings 2",
    52: "Choir Aahs",
    53: "Voice Oohs",
    54: "Synth Voice",
    55: "Orchestra Hit",
    
    # Brass (56-63)
    56: "Trumpet",
    57: "Trombone",
    58: "Tuba",
    59: "Muted Trumpet",
    60: "French Horn",
    61: "Brass Section",
    62: "Synth Brass 1",
    63: "Synth Brass 2",
    
    # Reed (64-71)
    64: "Soprano Sax",
    65: "Alto Sax",
    66: "Tenor Sax",
    67: "Baritone Sax",
    68: "Oboe",
    69: "English Horn",
    70: "Bassoon",
    71: "Clarinet",
    
    # Pipe (72-79)
    72: "Piccolo",
    73: "Flute",
    74: "Recorder",
    75: "Pan Flute",
    76: "Blown Bottle",
    77: "Shakuhachi",
    78: "Whistle",
    79: "Ocarina",
    
    # Synth Lead (80-87)
    80: "Lead 1 (square)",
    81: "Lead 2 (sawtooth)",
    82: "Lead 3 (calliope)",
    83: "Lead 4 (chiff)",
    84: "Lead 5 (charang)",
    85: "Lead 6 (voice)",
    86: "Lead 7 (fifths)",
    87: "Lead 8 (bass + lead)",
    
    # Synth Pad (88-95)
    88: "Pad 1 (new age)",
    89: "Pad 2 (warm)",
    90: "Pad 3 (polysynth)",
    91: "Pad 4 (choir)",
    92: "Pad 5 (bowed)",
    93: "Pad 6 (metallic)",
    94: "Pad 7 (halo)",
    95: "Pad 8 (sweep)",
    
    # Synth Effects (96-103)
    96: "FX 1 (rain)",
    97: "FX 2 (soundtrack)",
    98: "FX 3 (crystal)",
    99: "FX 4 (atmosphere)",
    100: "FX 5 (brightness)",
    101: "FX 6 (goblins)",
    102: "FX 7 (echoes)",
    103: "FX 8 (sci-fi)",
    
    # Ethnic (104-111)
    104: "Sitar",
    105: "Banjo",
    106: "Shamisen",
    107: "Koto",
    108: "Kalimba",
    109: "Bagpipe",
    110: "Fiddle",
    111: "Shanai",
    
    # Percussive (112-119)
    112: "Tinkle Bell",
    113: "Agogo",
    114: "Steel Drums",
    115: "Woodblock",
    116: "Taiko Drum",
    117: "Melodic Tom",
    118: "Synth Drum",
    119: "Reverse Cymbal",
    
    # Sound Effects (120-127)
    120: "Guitar Fret Noise",
    121: "Breath Noise",
    122: "Seashore",
    123: "Bird Tweet",
    124: "Telephone Ring",
    125: "Helicopter",
    126: "Applause",
    127: "Gunshot",
}

# Instrument categories for analysis
INSTRUMENT_CATEGORIES = {
    "piano": list(range(0, 8)),
    "chromatic_percussion": list(range(8, 16)),
    "organ": list(range(16, 24)),
    "guitar": list(range(24, 32)),
    "bass": list(range(32, 40)),
    "strings": list(range(40, 48)),
    "ensemble": list(range(48, 56)),
    "brass": list(range(56, 64)),
    "reed": list(range(64, 72)),
    "pipe": list(range(72, 80)),
    "synth_lead": list(range(80, 88)),
    "synth_pad": list(range(88, 96)),
    "synth_fx": list(range(96, 104)),
    "ethnic": list(range(104, 112)),
    "percussive": list(range(112, 120)),
    "sfx": list(range(120, 128)),
}


def get_instrument_name(program: int) -> str:
    """Get instrument name from GM program number (0-127)."""
    return GM_INSTRUMENTS.get(program, f"Unknown ({program})")


def get_drum_name(note: int) -> str:
    """Get drum name from MIDI note number."""
    return GM_DRUMS.get(note, f"Unknown Drum ({note})")


def get_instrument_category(program: int) -> str:
    """Get category for instrument program number."""
    for category, programs in INSTRUMENT_CATEGORIES.items():
        if program in programs:
            return category
    return "unknown"


def get_drum_category(note: int) -> str:
    """Get category for drum note."""
    for category, notes in DRUM_CATEGORIES.items():
        if note in notes:
            return category
    return "other"


def is_drum_channel(channel: int) -> bool:
    """Check if channel is the GM drum channel (9, zero-indexed)."""
    return channel == 9


def midi_note_to_name(note: int, include_octave: bool = True) -> str:
    """Convert MIDI note number to note name (e.g., 60 -> 'C4')."""
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    name = note_names[note % 12]
    if include_octave:
        octave = (note // 12) - 1
        return f"{name}{octave}"
    return name


def note_name_to_midi(name: str) -> int:
    """Convert note name to MIDI note number (e.g., 'C4' -> 60)."""
    import re
    match = re.match(r'([A-Ga-g][#b]?)(-?\d+)', name)
    if not match:
        raise ValueError(f"Invalid note name: {name}")
    
    note_name = match.group(1).upper()
    octave = int(match.group(2))
    
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    flat_map = {'DB': 'C#', 'EB': 'D#', 'FB': 'E', 'GB': 'F#', 'AB': 'G#', 'BB': 'A#', 'CB': 'B'}
    
    if note_name in flat_map:
        note_name = flat_map[note_name]
    
    try:
        note_num = note_names.index(note_name)
    except ValueError:
        raise ValueError(f"Invalid note name: {name}")
    
    return (octave + 1) * 12 + note_num
