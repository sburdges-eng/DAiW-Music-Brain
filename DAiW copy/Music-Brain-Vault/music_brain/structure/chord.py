"""
Chord Analyzer
Detect chords from MIDI note data.
"""

from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass

from ..utils.midi_io import MidiNote


# Chord templates as intervals from root (semitones)
CHORD_TEMPLATES = {
    # Triads
    'maj': [0, 4, 7],
    'min': [0, 3, 7],
    'dim': [0, 3, 6],
    'aug': [0, 4, 8],
    'sus2': [0, 2, 7],
    'sus4': [0, 5, 7],
    
    # Seventh chords
    'maj7': [0, 4, 7, 11],
    'min7': [0, 3, 7, 10],
    '7': [0, 4, 7, 10],  # Dominant 7
    'dim7': [0, 3, 6, 9],
    'm7b5': [0, 3, 6, 10],  # Half-diminished
    'minmaj7': [0, 3, 7, 11],
    'aug7': [0, 4, 8, 10],
    
    # Extended
    'add9': [0, 4, 7, 14],
    '9': [0, 4, 7, 10, 14],
    'min9': [0, 3, 7, 10, 14],
    'maj9': [0, 4, 7, 11, 14],
    '11': [0, 4, 7, 10, 14, 17],
    '13': [0, 4, 7, 10, 14, 21],
    
    # Power chord
    '5': [0, 7],
}

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Chord family mappings
CHORD_FAMILIES = {
    'major': ['maj', 'maj7', 'maj9', 'add9'],
    'minor': ['min', 'min7', 'min9', 'minmaj7'],
    'dominant': ['7', '9', '11', '13', 'aug7'],
    'diminished': ['dim', 'dim7', 'm7b5'],
    'suspended': ['sus2', 'sus4'],
    'augmented': ['aug'],
    'power': ['5']
}


@dataclass
class Chord:
    """Detected chord."""
    root: int           # 0-11 (pitch class)
    root_name: str      # Note name (e.g., 'C', 'F#')
    chord_type: str     # e.g., 'maj7', 'min'
    family: str         # e.g., 'major', 'minor', 'dominant'
    confidence: float   # 0-1
    bar: int            # Bar number
    beat: float         # Beat position in bar
    duration_beats: float
    notes: List[int]    # Pitch classes in chord


class ChordAnalyzer:
    """Detect chords from MIDI notes."""
    
    def __init__(self, ppq: int = 480, quantize_to_beat: float = 1.0):
        """
        Args:
            ppq: Ticks per quarter note
            quantize_to_beat: Grid size for chord detection (1.0 = quarter note)
        """
        self.ppq = ppq
        self.quantize_to_beat = quantize_to_beat
    
    def analyze(self, notes: List[MidiNote], exclude_drums: bool = True) -> List[Chord]:
        """
        Detect chords from notes.
        
        Args:
            notes: List of MidiNote objects
            exclude_drums: Skip drum channel (9)
        
        Returns:
            List of detected chords
        """
        if exclude_drums:
            notes = [n for n in notes if n.channel != 9]
        
        if not notes:
            return []
        
        # Group notes by time grid
        grid_ticks = int(self.ppq * self.quantize_to_beat)
        notes_by_grid = self._group_notes_by_grid(notes, grid_ticks)
        
        chords = []
        prev_grid = None
        prev_chord = None
        
        for grid_pos in sorted(notes_by_grid.keys()):
            grid_notes = notes_by_grid[grid_pos]
            
            # Get pitch classes (0-11)
            pitch_classes = set(n.pitch % 12 for n in grid_notes)
            
            # Include sustained notes from previous beat
            if prev_grid is not None and prev_grid in notes_by_grid:
                for n in notes_by_grid[prev_grid]:
                    if n.onset_ticks + n.duration_ticks > grid_pos * grid_ticks:
                        pitch_classes.add(n.pitch % 12)
            
            if len(pitch_classes) < 2:
                prev_grid = grid_pos
                continue
            
            # Detect chord
            chord = self._detect_chord(list(pitch_classes), grid_pos, grid_ticks)
            
            if chord and chord.confidence > 0.3:
                # Calculate duration (until next chord change)
                chord.duration_beats = self.quantize_to_beat
                chords.append(chord)
                prev_chord = chord
            
            prev_grid = grid_pos
        
        # Merge consecutive identical chords
        chords = self._merge_consecutive_chords(chords)
        
        return chords
    
    def _group_notes_by_grid(self, notes: List[MidiNote], grid_ticks: int) -> Dict[int, List[MidiNote]]:
        """Group notes by quantized time grid."""
        grouped = defaultdict(list)
        for note in notes:
            grid_pos = note.onset_ticks // grid_ticks
            grouped[grid_pos].append(note)
        return grouped
    
    def _detect_chord(self, pitch_classes: List[int], grid_pos: int, grid_ticks: int) -> Optional[Chord]:
        """
        Detect chord from pitch classes.
        Tries each pitch class as potential root and matches against templates.
        """
        best_match = None
        best_score = -1
        
        for potential_root in range(12):
            # Transpose pitch classes to root = 0
            transposed = sorted([(pc - potential_root) % 12 for pc in pitch_classes])
            
            for chord_type, template in CHORD_TEMPLATES.items():
                score = self._match_score(transposed, template, potential_root in pitch_classes)
                
                if score > best_score:
                    best_score = score
                    best_match = (potential_root, chord_type, score)
        
        if best_match is None or best_score < 0:
            return None
        
        root, chord_type, score = best_match
        
        # Calculate bar and beat
        ticks_per_bar = self.ppq * 4  # Assuming 4/4
        bar = (grid_pos * grid_ticks) // ticks_per_bar
        beat_in_bar = ((grid_pos * grid_ticks) % ticks_per_bar) / self.ppq
        
        # Find chord family
        family = 'other'
        for fam, types in CHORD_FAMILIES.items():
            if chord_type in types:
                family = fam
                break
        
        # Calculate confidence (normalize score)
        confidence = min(1.0, score / 5.0)
        
        return Chord(
            root=root,
            root_name=NOTE_NAMES[root],
            chord_type=chord_type,
            family=family,
            confidence=confidence,
            bar=bar,
            beat=beat_in_bar,
            duration_beats=self.quantize_to_beat,
            notes=pitch_classes
        )
    
    def _match_score(self, transposed: List[int], template: List[int], has_root: bool) -> float:
        """
        Score how well pitch classes match a chord template.
        Higher = better match.
        """
        transposed_set = set(transposed)
        template_set = set(template)
        
        # Count matches
        matches = len(transposed_set & template_set)
        
        # Penalize extra notes
        extras = len(transposed_set - template_set)
        
        # Penalize missing notes
        missing = len(template_set - transposed_set)
        
        score = matches - (extras * 0.5) - (missing * 0.3)
        
        # Bonus for exact match
        if transposed_set == template_set:
            score += 2
        
        # Bonus for having the root
        if has_root:
            score += 0.5
        
        return score
    
    def _merge_consecutive_chords(self, chords: List[Chord]) -> List[Chord]:
        """Merge consecutive identical chords."""
        if not chords:
            return []
        
        merged = [chords[0]]
        
        for chord in chords[1:]:
            prev = merged[-1]
            if (chord.root == prev.root and 
                chord.chord_type == prev.chord_type):
                # Extend duration
                prev.duration_beats += chord.duration_beats
            else:
                merged.append(chord)
        
        return merged
    
    def to_roman_numeral(self, chord: Chord, key_root: int = 0) -> str:
        """
        Convert chord to Roman numeral notation relative to key.
        
        Args:
            chord: Chord object
            key_root: Root of the key (0-11)
        
        Returns:
            Roman numeral string (e.g., 'I', 'iv', 'V7')
        """
        degree = (chord.root - key_root) % 12
        
        # Map semitones to scale degrees
        degree_map = {
            0: 'I', 1: 'bII', 2: 'II', 3: 'bIII', 4: 'III',
            5: 'IV', 6: 'bV', 7: 'V', 8: 'bVI', 9: 'VI',
            10: 'bVII', 11: 'VII'
        }
        
        numeral = degree_map.get(degree, '?')
        
        # Lowercase for minor chords
        if chord.family in ('minor', 'diminished'):
            numeral = numeral.lower()
        
        # Add chord type suffix
        suffix = ''
        if chord.chord_type in ('7', 'dom7'):
            suffix = '7'
        elif chord.chord_type == 'maj7':
            suffix = 'maj7'
        elif chord.chord_type == 'min7':
            suffix = '7'
        elif chord.chord_type == 'dim':
            suffix = '°'
        elif chord.chord_type == 'dim7':
            suffix = '°7'
        elif chord.chord_type == 'aug':
            suffix = '+'
        
        return numeral + suffix


def analyze_chords(notes: List[MidiNote], ppq: int = 480) -> List[Chord]:
    """Convenience function to analyze chords."""
    analyzer = ChordAnalyzer(ppq=ppq)
    return analyzer.analyze(notes)
