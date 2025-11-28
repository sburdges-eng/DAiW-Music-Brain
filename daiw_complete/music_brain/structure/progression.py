"""
Chord Progression Parser
========================
Parses chord symbols like "Cm", "F#maj7", "Bbm7" into structured data.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

# Note name to semitone offset from C
NOTE_MAP = {
    "C": 0, "C#": 1, "Db": 1,
    "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "Fb": 4, "E#": 5,
    "F": 5, "F#": 6, "Gb": 6,
    "G": 7, "G#": 8, "Ab": 8,
    "A": 9, "A#": 10, "Bb": 10,
    "B": 11, "Cb": 11, "B#": 0,
}

# Chord quality patterns and their interval structures
CHORD_QUALITIES = {
    "maj": (0, 4, 7),
    "min": (0, 3, 7),
    "m": (0, 3, 7),
    "dim": (0, 3, 6),
    "aug": (0, 4, 8),
    "maj7": (0, 4, 7, 11),
    "min7": (0, 3, 7, 10),
    "m7": (0, 3, 7, 10),
    "7": (0, 4, 7, 10),
    "dim7": (0, 3, 6, 9),
    "hdim7": (0, 3, 6, 10),  # half-diminished
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
    "add9": (0, 4, 7, 14),
    "6": (0, 4, 7, 9),
    "m6": (0, 3, 7, 9),
    "9": (0, 4, 7, 10, 14),
    "maj9": (0, 4, 7, 11, 14),
    "m9": (0, 3, 7, 10, 14),
}


@dataclass
class ParsedChord:
    """Represents a parsed chord symbol."""
    original: str
    root: str
    root_num: int  # semitone offset from C
    quality: str
    bass_note: Optional[str] = None
    bass_num: Optional[int] = None


def _parse_note(note_str: str) -> tuple[str, int] | None:
    """Parse a note name and return (name, semitone)."""
    note_str = note_str.strip()
    if not note_str:
        return None
    
    # Try two-character notes first (with accidental)
    if len(note_str) >= 2 and note_str[:2] in NOTE_MAP:
        return note_str[:2], NOTE_MAP[note_str[:2]]
    
    # Single character note
    if note_str[0].upper() in NOTE_MAP:
        return note_str[0].upper(), NOTE_MAP[note_str[0].upper()]
    
    return None


def parse_chord(chord_str: str) -> Optional[ParsedChord]:
    """
    Parse a single chord symbol.
    
    Examples:
        "C" -> C major
        "Cm" -> C minor
        "F#m7" -> F# minor 7
        "Bb/D" -> Bb major over D bass
    """
    chord_str = chord_str.strip()
    if not chord_str:
        return None
    
    original = chord_str
    
    # Handle slash chords (bass note)
    bass_note = None
    bass_num = None
    if "/" in chord_str:
        parts = chord_str.split("/")
        chord_str = parts[0]
        if len(parts) > 1 and parts[1]:
            bass_parsed = _parse_note(parts[1])
            if bass_parsed:
                bass_note, bass_num = bass_parsed
    
    # Parse root note
    root_parsed = _parse_note(chord_str)
    if not root_parsed:
        return None
    
    root, root_num = root_parsed
    
    # Get remainder after root
    if len(chord_str) > len(root):
        remainder = chord_str[len(root):]
    else:
        remainder = ""
    
    # Determine quality
    quality = "maj"  # default
    
    # Check for quality indicators (order matters - check longer patterns first)
    quality_patterns = [
        ("maj7", "maj7"),
        ("Maj7", "maj7"),
        ("M7", "maj7"),
        ("min7", "min7"),
        ("m7", "m7"),
        ("dim7", "dim7"),
        ("hdim7", "hdim7"),
        ("maj9", "maj9"),
        ("m9", "m9"),
        ("min", "min"),
        ("m", "m"),
        ("dim", "dim"),
        ("aug", "aug"),
        ("sus2", "sus2"),
        ("sus4", "sus4"),
        ("add9", "add9"),
        ("7", "7"),
        ("9", "9"),
        ("6", "6"),
    ]
    
    for pattern, qual in quality_patterns:
        if remainder.startswith(pattern):
            quality = qual
            break
    
    return ParsedChord(
        original=original,
        root=root,
        root_num=root_num,
        quality=quality,
        bass_note=bass_note,
        bass_num=bass_num,
    )


def parse_progression_string(prog_str: str) -> List[ParsedChord]:
    """
    Parse a chord progression string.
    
    Accepts:
        "C-Am-F-G"
        "Cm | Db | Bbm | Cm"
        "F#m7 Bmaj7 E A"
    """
    if not prog_str:
        return []
    
    # Normalize separators
    prog_str = prog_str.replace("|", "-").replace(",", "-")
    prog_str = re.sub(r"\s+", " ", prog_str)
    
    # Split on dash or space
    if "-" in prog_str:
        parts = [p.strip() for p in prog_str.split("-")]
    else:
        parts = prog_str.split()
    
    chords = []
    for part in parts:
        if not part:
            continue
        parsed = parse_chord(part)
        if parsed:
            chords.append(parsed)
    
    return chords
