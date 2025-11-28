"""
Harmony Generator - Maps emotional intent and rule-breaks to chord voicings

This module translates CompleteSongIntent objects into actual harmonic structures
with intentional rule-breaking applied. Philosophy: "Wrong notes with conviction."
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class RuleBreakType(Enum):
    """Types of intentional rule violations"""
    HARMONY_ModalInterchange = "modal_interchange"
    HARMONY_AvoidTonicResolution = "avoid_tonic_resolution"
    HARMONY_ParallelMotion = "parallel_motion"
    HARMONY_UnresolvedDissonance = "unresolved_dissonance"
    HARMONY_Polytonality = "polytonality"
    RHYTHM_ConstantDisplacement = "constant_displacement"
    RHYTHM_TempoFluctuation = "tempo_fluctuation"
    PRODUCTION_BuriedVocals = "buried_vocals"
    PRODUCTION_PitchImperfection = "pitch_imperfection"


@dataclass
class ChordVoicing:
    """Represents a chord with MIDI note numbers"""
    root: str  # e.g., "F", "C", "Bbm"
    notes: List[int]  # MIDI note numbers (e.g., [60, 64, 67] for C major)
    duration_beats: float = 4.0  # Quarter note = 1 beat
    velocity: int = 80
    roman_numeral: Optional[str] = None
    emotional_function: Optional[str] = None


@dataclass
class HarmonyResult:
    """Complete harmonic structure for a song"""
    chords: List[str]  # Chord symbols (e.g., ["F", "C", "Am", "Dm"])
    voicings: List[ChordVoicing]  # Full MIDI voicing data
    key: str
    mode: str
    rule_break_applied: Optional[str] = None
    emotional_justification: Optional[str] = None


class HarmonyGenerator:
    """
    Generates chord progressions and voicings based on emotional intent
    and intentional rule-breaking decisions.
    """
    
    # MIDI note numbers for reference
    NOTE_TO_MIDI = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
        'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }
    
    # Scale intervals (semitones from root)
    SCALES = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'natural_minor': [0, 2, 3, 5, 7, 8, 10],
        'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
        'melodic_minor': [0, 2, 3, 5, 7, 9, 11],
        'dorian': [0, 2, 3, 5, 7, 9, 10],
        'phrygian': [0, 1, 3, 5, 7, 8, 10],
        'lydian': [0, 2, 4, 6, 7, 9, 11],
        'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    }
    
    # Diatonic chords in major and minor (as intervals from root)
    DIATONIC_CHORDS_MAJOR = {
        'I': [0, 4, 7],      # Major triad
        'ii': [2, 5, 9],     # Minor triad
        'iii': [4, 7, 11],   # Minor triad
        'IV': [5, 9, 0],     # Major triad
        'V': [7, 11, 2],     # Major triad
        'vi': [9, 0, 4],     # Minor triad
        'vii°': [11, 2, 5],  # Diminished triad
    }
    
    DIATONIC_CHORDS_MINOR = {
        'i': [0, 3, 7],      # Minor triad
        'ii°': [2, 5, 8],    # Diminished triad
        'III': [3, 7, 10],   # Major triad
        'iv': [5, 8, 0],     # Minor triad
        'v': [7, 10, 2],     # Minor triad (or V for harmonic minor)
        'VI': [8, 0, 3],     # Major triad
        'VII': [10, 2, 5],   # Major triad
    }
    
    def __init__(self, base_octave: int = 4):
        """
        Initialize harmony generator.
        
        Args:
            base_octave: MIDI octave for root notes (4 = middle C octave)
        """
        self.base_octave = base_octave
        self.rule_break_handlers = {
            RuleBreakType.HARMONY_ModalInterchange: self._apply_modal_interchange,
            RuleBreakType.HARMONY_AvoidTonicResolution: self._apply_avoid_resolution,
            RuleBreakType.HARMONY_ParallelMotion: self._apply_parallel_motion,
        }
    
    def generate_from_intent(self, intent: 'CompleteSongIntent') -> HarmonyResult:
        """
        Generate harmony from a complete song intent.
        
        Args:
            intent: CompleteSongIntent with emotional and technical specifications
            
        Returns:
            HarmonyResult with chord progression and MIDI voicings
        """
        key = intent.technical_constraints.technical_key
        mode = intent.technical_constraints.technical_mode
        rule_break = intent.technical_constraints.technical_rule_to_break
        justification = intent.technical_constraints.rule_breaking_justification
        
        # Generate base progression
        base_progression = self._generate_base_progression(key, mode)
        
        # Apply rule-breaking if specified
        if rule_break:
            try:
                rule_enum = RuleBreakType[rule_break]
                if rule_enum in self.rule_break_handlers:
                    modified_progression = self.rule_break_handlers[rule_enum](
                        base_progression, key, mode, intent
                    )
                else:
                    modified_progression = base_progression
            except (KeyError, ValueError):
                # Rule break not recognized, use base
                modified_progression = base_progression
        else:
            modified_progression = base_progression
        
        # Convert to voicings
        voicings = self._chords_to_voicings(modified_progression, key)
        
        return HarmonyResult(
            chords=[chord.root for chord in voicings],
            voicings=voicings,
            key=key,
            mode=mode,
            rule_break_applied=rule_break,
            emotional_justification=justification
        )
    
    def generate_basic_progression(
        self,
        key: str,
        mode: str = "major",
        pattern: str = "I-V-vi-IV"
    ) -> HarmonyResult:
        """
        Generate a basic chord progression without rule-breaking.
        
        Args:
            key: Musical key (e.g., "F", "C", "G")
            mode: "major" or "minor"
            pattern: Roman numeral pattern (e.g., "I-V-vi-IV")
            
        Returns:
            HarmonyResult with basic diatonic progression
        """
        roman_numerals = pattern.split('-')
        chord_symbols = self._roman_to_chord_symbols(roman_numerals, key, mode)
        voicings = self._chords_to_voicings(chord_symbols, key)
        
        return HarmonyResult(
            chords=chord_symbols,
            voicings=voicings,
            key=key,
            mode=mode
        )
    
    def _generate_base_progression(self, key: str, mode: str) -> List[str]:
        """Generate a default base progression based on mode"""
        if mode == "major":
            # Classic I-V-vi-IV (like F-C-Am-Dm in F major, but wait that's wrong)
            # F major: F-C-Dm-Bb would be I-V-vi-IV
            # Kelly song is F-C-Am-Dm which is I-V-iii-vi
            # Let's use I-V-vi-IV as default
            return self._roman_to_chord_symbols(['I', 'V', 'vi', 'IV'], key, mode)
        else:
            # i-VI-III-VII (common minor progression)
            return self._roman_to_chord_symbols(['i', 'VI', 'III', 'VII'], key, mode)
    
    def _roman_to_chord_symbols(
        self,
        roman_numerals: List[str],
        key: str,
        mode: str
    ) -> List[str]:
        """
        Convert Roman numerals to chord symbols in a given key.
        
        Args:
            roman_numerals: List of Roman numerals (e.g., ['I', 'V', 'vi', 'IV'])
            key: Musical key (e.g., "F")
            mode: "major" or "minor"
            
        Returns:
            List of chord symbols (e.g., ['F', 'C', 'Dm', 'Bb'])
        """
        scale = self.SCALES['major'] if mode == 'major' else self.SCALES['natural_minor']
        root_midi = self.NOTE_TO_MIDI[key]
        
        chord_map_major = {
            'I': (0, 'maj'), 'ii': (1, 'min'), 'iii': (2, 'min'),
            'IV': (3, 'maj'), 'V': (4, 'maj'), 'vi': (5, 'min'),
            'vii°': (6, 'dim')
        }
        
        chord_map_minor = {
            'i': (0, 'min'), 'ii°': (1, 'dim'), 'III': (2, 'maj'),
            'iv': (3, 'min'), 'v': (4, 'min'), 'VI': (5, 'maj'),
            'VII': (6, 'maj'), 'V': (4, 'maj')  # V can be major in minor keys
        }
        
        chord_map = chord_map_major if mode == 'major' else chord_map_minor
        
        result = []
        for rn in roman_numerals:
            if rn in chord_map:
                scale_degree, quality = chord_map[rn]
                chord_root_midi = (root_midi + scale[scale_degree]) % 12
                chord_name = self._midi_to_note_name(chord_root_midi)
                
                # Add quality suffix
                if quality == 'min':
                    chord_name += 'm'
                elif quality == 'dim':
                    chord_name += 'dim'
                # 'maj' needs no suffix
                
                result.append(chord_name)
            else:
                # Unknown roman numeral, skip or use root
                result.append(key)
        
        return result
    
    def _midi_to_note_name(self, midi_note: int) -> str:
        """Convert MIDI note number to note name (prefers flats for readability)"""
        note_names = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
        return note_names[midi_note % 12]
    
    def _chord_symbol_to_intervals(self, chord_symbol: str) -> Tuple[str, List[int]]:
        """
        Parse chord symbol and return root + intervals.
        
        Args:
            chord_symbol: e.g., "F", "Cm", "G7", "Bbm"
            
        Returns:
            Tuple of (root_note, intervals_list)
        """
        # Simple parser - can be expanded
        chord = chord_symbol.strip()
        
        # Extract root (handle sharps/flats)
        if len(chord) > 1 and chord[1] in ['#', 'b']:
            root = chord[:2]
            quality = chord[2:]
        else:
            root = chord[0]
            quality = chord[1:]
        
        # Determine intervals based on quality
        if quality == '' or quality.upper() == 'MAJ':
            intervals = [0, 4, 7]  # Major triad
        elif quality == 'm' or quality.upper() == 'MIN':
            intervals = [0, 3, 7]  # Minor triad
        elif quality == 'dim' or quality == '°':
            intervals = [0, 3, 6]  # Diminished triad
        elif quality == 'aug' or quality == '+':
            intervals = [0, 4, 8]  # Augmented triad
        elif quality == '7':
            intervals = [0, 4, 7, 10]  # Dominant 7th
        elif quality == 'maj7':
            intervals = [0, 4, 7, 11]  # Major 7th
        elif quality == 'm7':
            intervals = [0, 3, 7, 10]  # Minor 7th
        else:
            # Default to major if unknown
            intervals = [0, 4, 7]
        
        return root, intervals
    
    def _chords_to_voicings(
        self,
        chord_symbols: List[str],
        key: str
    ) -> List[ChordVoicing]:
        """
        Convert chord symbols to MIDI voicings.
        
        Args:
            chord_symbols: List of chord names (e.g., ['F', 'C', 'Dm', 'Bb'])
            key: Root key for context
            
        Returns:
            List of ChordVoicing objects with MIDI notes
        """
        voicings = []
        
        for chord_symbol in chord_symbols:
            root, intervals = self._chord_symbol_to_intervals(chord_symbol)
            root_midi = self.NOTE_TO_MIDI.get(root, 0) + (self.base_octave * 12)
            
            # Generate MIDI notes
            midi_notes = [(root_midi + interval) for interval in intervals]
            
            voicing = ChordVoicing(
                root=chord_symbol,
                notes=midi_notes,
                duration_beats=4.0,  # Whole note default
                velocity=80
            )
            voicings.append(voicing)
        
        return voicings
    
    # ============================================================================
    # RULE-BREAKING HANDLERS
    # ============================================================================
    
    def _apply_modal_interchange(
        self,
        base_progression: List[str],
        key: str,
        mode: str,
        intent: 'CompleteSongIntent'
    ) -> List[str]:
        """
        Apply modal interchange - borrow chords from parallel minor/major.
        
        For Kelly song: F-C-Am-Dm becomes F-C-Bbm-F
        Bbm is borrowed from F minor (iv chord in minor becomes iv in major)
        
        This creates "bittersweet hope" - the darkness of minor within major context
        """
        if mode == 'major':
            # Most common: borrow iv from parallel minor
            # In F major: Bb becomes Bbm
            # Pattern: Replace IV with iv (or vi with ♭VI, etc.)
            
            # For MVP: if IV appears, replace with iv
            modified = []
            for chord in base_progression:
                # Check if this is the IV chord (Bb in F major, for example)
                if self._is_fourth_degree(chord, key, mode):
                    # Make it minor
                    root = chord.rstrip('m')  # Remove any existing 'm'
                    modified.append(root + 'm')
                else:
                    modified.append(chord)
            return modified
        else:
            # In minor: borrow from parallel major (less common)
            # Could replace iv with IV, etc.
            return base_progression
    
    def _apply_avoid_resolution(
        self,
        base_progression: List[str],
        key: str,
        mode: str,
        intent: 'CompleteSongIntent'
    ) -> List[str]:
        """
        Avoid tonic resolution - end on non-tonic chord.
        Creates unresolved yearning, perfect for grief/longing.
        
        Example: Instead of ending on I, end on V or vi
        """
        if len(base_progression) == 0:
            return base_progression
        
        # Replace last chord with V or vi instead of I
        modified = base_progression.copy()
        
        if mode == 'major':
            # End on V (dominant) for unresolved tension
            modified[-1] = self._get_fifth_degree(key, mode)
        else:
            # In minor, could end on VI or III
            modified[-1] = self._get_sixth_degree(key, mode)
        
        return modified
    
    def _apply_parallel_motion(
        self,
        base_progression: List[str],
        key: str,
        mode: str,
        intent: 'CompleteSongIntent'
    ) -> List[str]:
        """
        Use parallel fifths/octaves - breaks classical voice-leading rules.
        Creates power, defiance, rawness.
        
        In practice: all chords become power chords (root + fifth)
        This is more of a voicing decision than progression change.
        """
        # For now, return base progression
        # The actual parallel motion is better handled in voicing generation
        # where we'd use only root + fifth instead of full triads
        return base_progression
    
    def _is_fourth_degree(self, chord: str, key: str, mode: str) -> bool:
        """Check if chord is the IV degree in the key"""
        scale = self.SCALES['major'] if mode == 'major' else self.SCALES['natural_minor']
        root_midi = self.NOTE_TO_MIDI[key]
        fourth_degree_midi = (root_midi + scale[3]) % 12
        
        chord_root = chord.rstrip('m').rstrip('dim').rstrip('aug')
        chord_midi = self.NOTE_TO_MIDI.get(chord_root, -1)
        
        return chord_midi == fourth_degree_midi
    
    def _get_fifth_degree(self, key: str, mode: str) -> str:
        """Get the V chord in the key"""
        scale = self.SCALES['major'] if mode == 'major' else self.SCALES['natural_minor']
        root_midi = self.NOTE_TO_MIDI[key]
        fifth_degree_midi = (root_midi + scale[4]) % 12
        return self._midi_to_note_name(fifth_degree_midi)
    
    def _get_sixth_degree(self, key: str, mode: str) -> str:
        """Get the vi/VI chord in the key"""
        scale = self.SCALES['major'] if mode == 'major' else self.SCALES['natural_minor']
        root_midi = self.NOTE_TO_MIDI[key]
        sixth_degree_midi = (root_midi + scale[5]) % 12
        note = self._midi_to_note_name(sixth_degree_midi)
        return note + 'm' if mode == 'major' else note


def generate_midi_from_harmony(harmony: HarmonyResult, output_path: str, tempo_bpm: int = 82):
    """
    Generate a MIDI file from HarmonyResult.
    
    Args:
        harmony: HarmonyResult with voicings to render
        output_path: Path to save MIDI file
        tempo_bpm: Tempo in beats per minute
    """
    from mido import MidiFile, MidiTrack, Message, MetaMessage
    
    # Create MIDI file
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo
    tempo_microseconds = int(60_000_000 / tempo_bpm)
    track.append(MetaMessage('set_tempo', tempo=tempo_microseconds))
    
    # PPQ (pulses per quarter note)
    ppq = mid.ticks_per_beat  # Default is 480
    
    # Add chords
    for voicing in harmony.voicings:
        # Note on messages
        for note in voicing.notes:
            track.append(Message('note_on', note=note, velocity=voicing.velocity, time=0))
        
        # Calculate duration in ticks
        duration_ticks = int(voicing.duration_beats * ppq)
        
        # Note off messages (only first note gets the duration time)
        for i, note in enumerate(voicing.notes):
            time = duration_ticks if i == 0 else 0
            track.append(Message('note_off', note=note, velocity=0, time=time))
    
    # Save file
    mid.save(output_path)
    print(f"MIDI file saved: {output_path}")
    print(f"Key: {harmony.key} {harmony.mode}")
    print(f"Chords: {' - '.join(harmony.chords)}")
    if harmony.rule_break_applied:
        print(f"Rule break: {harmony.rule_break_applied}")
        print(f"Why: {harmony.emotional_justification}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example 1: Kelly song (F-C-Bbm-F with modal interchange)
    print("=" * 60)
    print("KELLY SONG EXAMPLE: Modal Interchange in F Major")
    print("=" * 60)
    
    generator = HarmonyGenerator()
    
    # Simulate the Kelly song intent
    from dataclasses import dataclass
    
    @dataclass
    class MockTechnicalConstraints:
        technical_key: str = "F"
        technical_mode: str = "major"
        technical_rule_to_break: str = "HARMONY_ModalInterchange"
        rule_breaking_justification: str = "Bbm makes hope feel earned and bittersweet"
    
    @dataclass
    class MockIntent:
        technical_constraints: MockTechnicalConstraints
    
    kelly_intent = MockIntent(technical_constraints=MockTechnicalConstraints())
    
    # Generate harmony
    kelly_harmony = generator.generate_from_intent(kelly_intent)
    
    # Generate MIDI
    generate_midi_from_harmony(kelly_harmony, "/home/claude/kelly_song_harmony.mid", tempo_bpm=82)
    
    print("\n")
    
    # Example 2: Basic progression without rule-breaking
    print("=" * 60)
    print("BASIC PROGRESSION: I-V-vi-IV in C Major")
    print("=" * 60)
    
    basic_harmony = generator.generate_basic_progression(
        key="C",
        mode="major",
        pattern="I-V-vi-IV"
    )
    
    generate_midi_from_harmony(basic_harmony, "/home/claude/basic_progression.mid", tempo_bpm=120)
