"""
Chord Progression Analysis

Features:
- Major AND minor key support
- Mode detection (Dorian, Mixolydian, etc.)
- Chromatic chord handling (bVII, #IV, etc.)
- Confidence-scored pattern matching
- Common progression database
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class Mode(Enum):
    """Musical modes."""
    MAJOR = "major"
    MINOR = "minor"
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"
    LYDIAN = "lydian"
    MIXOLYDIAN = "mixolydian"
    LOCRIAN = "locrian"
    HARMONIC_MINOR = "harmonic_minor"
    MELODIC_MINOR = "melodic_minor"


# Scale intervals from root (semitones)
SCALE_INTERVALS = {
    Mode.MAJOR:          [0, 2, 4, 5, 7, 9, 11],
    Mode.MINOR:          [0, 2, 3, 5, 7, 8, 10],  # Natural minor
    Mode.DORIAN:         [0, 2, 3, 5, 7, 9, 10],
    Mode.PHRYGIAN:       [0, 1, 3, 5, 7, 8, 10],
    Mode.LYDIAN:         [0, 2, 4, 6, 7, 9, 11],
    Mode.MIXOLYDIAN:     [0, 2, 4, 5, 7, 9, 10],
    Mode.LOCRIAN:        [0, 1, 3, 5, 6, 8, 10],
    Mode.HARMONIC_MINOR: [0, 2, 3, 5, 7, 8, 11],
    Mode.MELODIC_MINOR:  [0, 2, 3, 5, 7, 9, 11],
}


# Note name to pitch class
NOTE_TO_PC = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "Fb": 4, "E#": 5, "F": 5, "F#": 6, "Gb": 6,
    "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10,
    "B": 11, "Cb": 11, "B#": 0,
}

# Pitch class to note name (sharps)
PC_TO_NOTE_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
PC_TO_NOTE_FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]


@dataclass
class ChordDegree:
    """A chord analyzed in context of key."""
    degree: int           # 1-7 for diatonic, 0 for unknown
    quality: str          # "major", "minor", "dim", "aug", "dom7", etc.
    root_pc: int          # Pitch class of root
    is_chromatic: bool    # Not in key
    chromatic_name: str   # e.g., "bVII", "#IV" if chromatic
    confidence: float     # 0-1 how sure we are


@dataclass
class ProgressionMatch:
    """A matched progression pattern."""
    family: str           # Name of pattern family
    pattern: List[int]    # The pattern matched
    start_index: int      # Where in the sequence
    window: List[int]     # Actual degrees matched
    confidence: float     # Match quality (0-1)
    transposition: int    # Semitones from original if transposed


# Common progression patterns (Roman numeral degrees)
PROGRESSION_PATTERNS = {
    # Pop/Rock
    "axis": {
        "pattern": [1, 5, 6, 4],  # I-V-vi-IV
        "aliases": ["pop_1564", "sensitive_female_chord"],
        "genres": ["pop", "rock", "country"],
    },
    "50s_progression": {
        "pattern": [1, 6, 4, 5],  # I-vi-IV-V
        "aliases": ["doo_wop", "heart_and_soul"],
        "genres": ["oldies", "pop"],
    },
    "andalusian": {
        "pattern": [1, 7, 6, 5],  # i-VII-VI-V (in minor)
        "aliases": ["flamenco", "hit_the_road_jack"],
        "genres": ["flamenco", "rock"],
        "mode": Mode.MINOR,
    },
    
    # Blues
    "basic_blues": {
        "pattern": [1, 1, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5],  # 12-bar
        "aliases": ["12_bar_blues"],
        "genres": ["blues", "rock"],
    },
    "quick_change_blues": {
        "pattern": [1, 4, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5],
        "aliases": ["blues_quick_iv"],
        "genres": ["blues"],
    },
    
    # Jazz
    "ii_V_I": {
        "pattern": [2, 5, 1],
        "aliases": ["jazz_turnaround_short"],
        "genres": ["jazz", "bossa"],
    },
    "I_vi_ii_V": {
        "pattern": [1, 6, 2, 5],
        "aliases": ["rhythm_changes_a", "jazz_turnaround"],
        "genres": ["jazz", "standards"],
    },
    "iii_vi_ii_V": {
        "pattern": [3, 6, 2, 5],
        "aliases": ["long_approach"],
        "genres": ["jazz"],
    },
    "coltrane_changes": {
        "pattern": [1, 5, 1, 5, 1, 5],  # Simplified - moves by major 3rds
        "aliases": ["giant_steps"],
        "genres": ["jazz"],
        "chromatic": True,
    },
    
    # Classical
    "circle_of_fifths": {
        "pattern": [1, 4, 7, 3, 6, 2, 5, 1],
        "aliases": ["pachelbel", "canon"],
        "genres": ["classical", "pop"],
    },
    "authentic_cadence": {
        "pattern": [5, 1],
        "aliases": ["V_I", "perfect_cadence"],
        "genres": ["classical", "all"],
    },
    "plagal_cadence": {
        "pattern": [4, 1],
        "aliases": ["IV_I", "amen_cadence"],
        "genres": ["classical", "gospel"],
    },
    
    # EDM / Modern
    "four_chord_minor": {
        "pattern": [1, 6, 3, 7],  # i-VI-III-VII in minor
        "aliases": ["sad_edm"],
        "genres": ["edm", "pop"],
        "mode": Mode.MINOR,
    },
    "epic_trailer": {
        "pattern": [6, 4, 1, 5],  # vi-IV-I-V (deceptive start)
        "aliases": ["save_tonight"],
        "genres": ["pop", "rock"],
    },
    
    # Gospel / R&B
    "gospel_vamp": {
        "pattern": [4, 3, 6, 2, 5],
        "aliases": ["rb_turnaround"],
        "genres": ["gospel", "rnb"],
    },
    "mary_jane": {
        "pattern": [1, 7, 4, 1],  # I-bVII-IV-I
        "aliases": ["mixolydian_vamp"],
        "genres": ["rock", "funk"],
        "chromatic": True,
    },
}


class ProgressionAnalyzer:
    """
    Analyze chord progressions in context.
    """
    
    def __init__(self):
        self.patterns = PROGRESSION_PATTERNS
    
    def parse_key(self, key_name: str) -> Tuple[int, Mode]:
        """
        Parse key name to (root_pc, mode).
        
        Handles:
            "C major", "C", "Cm", "C minor", "C min",
            "C dorian", "Cmaj", "CM"
        """
        key_name = key_name.strip()
        
        # Split into note and mode parts
        parts = key_name.split()
        
        if len(parts) >= 2:
            note_part = parts[0]
            mode_part = " ".join(parts[1:]).lower()
        else:
            # Single word: "Cm", "Cmaj", "C"
            note_part = key_name.rstrip("mMaj").rstrip("in").rstrip("ajor")
            mode_part = key_name[len(note_part):].lower()
        
        # Get root pitch class
        if note_part not in NOTE_TO_PC:
            raise ValueError(f"Unknown note: {note_part}")
        root_pc = NOTE_TO_PC[note_part]
        
        # Determine mode
        mode_map = {
            "": Mode.MAJOR,
            "major": Mode.MAJOR,
            "maj": Mode.MAJOR,
            "m": Mode.MINOR,
            "minor": Mode.MINOR,
            "min": Mode.MINOR,
            "dorian": Mode.DORIAN,
            "dor": Mode.DORIAN,
            "phrygian": Mode.PHRYGIAN,
            "phryg": Mode.PHRYGIAN,
            "lydian": Mode.LYDIAN,
            "lyd": Mode.LYDIAN,
            "mixolydian": Mode.MIXOLYDIAN,
            "mixo": Mode.MIXOLYDIAN,
            "locrian": Mode.LOCRIAN,
            "loc": Mode.LOCRIAN,
        }
        
        mode = mode_map.get(mode_part, Mode.MAJOR)
        
        return root_pc, mode
    
    def get_scale_degrees(self, root_pc: int, mode: Mode) -> List[int]:
        """Get pitch classes for each scale degree."""
        intervals = SCALE_INTERVALS[mode]
        return [(root_pc + interval) % 12 for interval in intervals]
    
    def analyze_chord(
        self,
        chord_root_pc: int,
        key_root_pc: int,
        mode: Mode
    ) -> ChordDegree:
        """
        Analyze a single chord in context of key.
        """
        scale_pcs = self.get_scale_degrees(key_root_pc, mode)
        
        # Check if diatonic
        if chord_root_pc in scale_pcs:
            degree = scale_pcs.index(chord_root_pc) + 1
            return ChordDegree(
                degree=degree,
                quality=self._default_quality(degree, mode),
                root_pc=chord_root_pc,
                is_chromatic=False,
                chromatic_name="",
                confidence=1.0
            )
        
        # Chromatic chord - determine alteration
        chromatic_name = self._chromatic_name(chord_root_pc, key_root_pc, mode)
        
        return ChordDegree(
            degree=0,
            quality="unknown",
            root_pc=chord_root_pc,
            is_chromatic=True,
            chromatic_name=chromatic_name,
            confidence=0.8
        )
    
    def _default_quality(self, degree: int, mode: Mode) -> str:
        """Default chord quality for scale degree."""
        if mode in (Mode.MAJOR, Mode.LYDIAN):
            qualities = ["", "major", "minor", "minor", "major", "major", "minor", "dim"]
        elif mode in (Mode.MINOR, Mode.DORIAN, Mode.PHRYGIAN):
            qualities = ["", "minor", "dim", "major", "minor", "minor", "major", "major"]
        elif mode == Mode.MIXOLYDIAN:
            qualities = ["", "major", "minor", "dim", "major", "major", "minor", "major"]
        else:
            qualities = ["", "?"] * 4
        
        return qualities[degree] if degree < len(qualities) else "?"
    
    def _chromatic_name(self, chord_pc: int, key_pc: int, mode: Mode) -> str:
        """Get Roman numeral name for chromatic chord."""
        # Calculate semitones from tonic
        interval = (chord_pc - key_pc) % 12
        
        # Common chromatic chords
        chromatic_map = {
            1: "bII",    # Neapolitan
            3: "#II/bIII",
            6: "#IV/bV",  # Tritone
            8: "#V/bVI",
            10: "bVII",   # Subtonic
        }
        
        return chromatic_map.get(interval, f"?{interval}")
    
    def extract_degrees(
        self,
        chords: List[Tuple[int, List[int]]],  # (tick, [midi_notes])
        key_name: str
    ) -> List[ChordDegree]:
        """
        Extract chord degrees from chord list.
        
        Args:
            chords: List of (time, midi_notes)
            key_name: Key like "C major", "G minor"
        
        Returns:
            List of ChordDegree objects
        """
        try:
            key_pc, mode = self.parse_key(key_name)
        except ValueError:
            return []
        
        degrees = []
        for _, notes in chords:
            if not notes:
                continue
            
            # Assume lowest note is root (simple heuristic)
            root_pc = min(notes) % 12
            
            degree = self.analyze_chord(root_pc, key_pc, mode)
            degrees.append(degree)
        
        return degrees
    
    def match_patterns(
        self,
        degrees: List[ChordDegree],
        tolerance: float = 0.25
    ) -> List[ProgressionMatch]:
        """
        Match degree sequence against known patterns.
        
        Args:
            degrees: List of ChordDegree objects
            tolerance: Maximum mismatch ratio (0.25 = 25% can differ)
        
        Returns:
            List of ProgressionMatch sorted by confidence
        """
        if not degrees:
            return []
        
        # Extract numeric degrees (0 for chromatic)
        deg_nums = [d.degree for d in degrees]
        
        matches = []
        
        for name, info in self.patterns.items():
            pattern = info["pattern"]
            plen = len(pattern)
            
            if plen > len(deg_nums):
                continue
            
            # Slide window across sequence
            for i in range(len(deg_nums) - plen + 1):
                window = deg_nums[i:i + plen]
                
                # Count matches and mismatches
                match_count = 0
                mismatch_count = 0
                chromatic_count = 0
                
                for actual, expected in zip(window, pattern):
                    if actual == expected:
                        match_count += 1
                    elif actual == 0:
                        chromatic_count += 1  # Unknown, not a hard mismatch
                    else:
                        mismatch_count += 1
                
                # Calculate confidence
                mismatch_ratio = mismatch_count / plen
                if mismatch_ratio > tolerance:
                    continue
                
                # Confidence based on matches and penalties
                confidence = match_count / plen
                confidence -= chromatic_count * 0.1  # Small penalty for unknowns
                confidence = max(0, confidence)
                
                matches.append(ProgressionMatch(
                    family=name,
                    pattern=pattern,
                    start_index=i,
                    window=window,
                    confidence=confidence,
                    transposition=0
                ))
        
        # Sort by confidence
        matches.sort(key=lambda m: m.confidence, reverse=True)
        
        # Remove duplicates (same family at same position)
        seen = set()
        unique = []
        for m in matches:
            key = (m.family, m.start_index)
            if key not in seen:
                seen.add(key)
                unique.append(m)
        
        return unique
    
    def analyze(
        self,
        chords: List[Tuple[int, List[int]]],
        key_name: str
    ) -> Dict:
        """
        Complete progression analysis.
        
        Returns dict with:
            - key: Parsed key info
            - degrees: List of analyzed chords
            - matches: Pattern matches
            - summary: Human-readable summary
        """
        try:
            key_pc, mode = self.parse_key(key_name)
        except ValueError as e:
            return {"error": str(e)}
        
        degrees = self.extract_degrees(chords, key_name)
        matches = self.match_patterns(degrees)
        
        # Build summary
        deg_str = " ".join(
            d.chromatic_name if d.is_chromatic else str(d.degree)
            for d in degrees[:16]
        )
        
        top_matches = [
            f"{m.family} ({m.confidence:.0%})"
            for m in matches[:3]
        ]
        
        return {
            "key": {
                "root": PC_TO_NOTE_SHARP[key_pc],
                "mode": mode.value,
            },
            "degrees": degrees,
            "matches": matches,
            "summary": {
                "progression": deg_str,
                "top_matches": top_matches,
                "chromatic_count": sum(1 for d in degrees if d.is_chromatic),
            }
        }


# Convenience functions
def analyze_progression(
    chords: List[Tuple[int, List[int]]],
    key_name: str
) -> Dict:
    """Analyze chord progression."""
    analyzer = ProgressionAnalyzer()
    return analyzer.analyze(chords, key_name)


def match_progressions(degrees: List[int], tolerance: float = 0.25) -> List[ProgressionMatch]:
    """Match numeric degrees against patterns."""
    analyzer = ProgressionAnalyzer()
    # Convert to ChordDegree objects
    chord_degrees = [
        ChordDegree(d, "", 0, d == 0, "", 1.0)
        for d in degrees
    ]
    return analyzer.match_patterns(chord_degrees, tolerance)
