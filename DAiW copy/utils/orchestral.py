"""
Orchestral Template Handling

Handles complex orchestral MIDI with:
- Multiple articulation tracks per instrument
- Expression controller data (CC1, CC11, CC7)
- Keyswitch tracks
- Section divisi
- Tempo and time signature changes

This module validates and processes orchestral templates
that would break simpler MIDI handlers.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict

from .midi_io import MidiData, TrackData, MidiEvent


# Common orchestral CC numbers
CC_MODWHEEL = 1       # Modulation / dynamics / expression
CC_BREATH = 2         # Breath controller
CC_VOLUME = 7         # Channel volume
CC_PAN = 10           # Pan position
CC_EXPRESSION = 11    # Expression
CC_SUSTAIN = 64       # Sustain pedal


# Keyswitch ranges (common ranges for sample libraries)
KEYSWITCH_RANGES = {
    'low': (0, 23),       # C-2 to B-1 (common)
    'high': (108, 127),   # C7 to G9 (less common)
}

# Orchestral instrument families
ORCHESTRAL_FAMILIES = {
    'strings': ['violin', 'viola', 'cello', 'bass', 'contrabass'],
    'woodwinds': ['flute', 'oboe', 'clarinet', 'bassoon', 'piccolo', 'english horn'],
    'brass': ['trumpet', 'horn', 'trombone', 'tuba', 'french horn'],
    'percussion': ['timpani', 'snare', 'bass drum', 'cymbals', 'triangle', 'glockenspiel'],
    'keyboards': ['piano', 'harp', 'celesta'],
}


@dataclass
class ArticulationTrack:
    """Represents an articulation within an instrument."""
    instrument: str
    articulation: str        # legato, staccato, pizzicato, etc.
    track_index: int
    keyswitch_note: Optional[int] = None
    cc_controller: Optional[int] = None
    note_count: int = 0


@dataclass
class ExpressionData:
    """Expression controller data for a track."""
    track_index: int
    cc_number: int
    values: List[Tuple[int, int]] = field(default_factory=list)  # (tick, value)
    min_value: int = 127
    max_value: int = 0
    has_automation: bool = False


@dataclass
class OrchestralValidation:
    """Results of orchestral template validation."""
    is_valid: bool = True
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    # Detected features
    has_keyswitches: bool = False
    has_expression: bool = False
    has_tempo_changes: bool = False
    has_time_sig_changes: bool = False
    has_divisi: bool = False
    
    # Track analysis
    articulation_tracks: List[ArticulationTrack] = field(default_factory=list)
    expression_data: Dict[int, List[ExpressionData]] = field(default_factory=dict)
    
    # Complexity metrics
    total_tracks: int = 0
    total_cc_events: int = 0
    total_keyswitch_notes: int = 0
    unique_instruments: int = 0


class OrchestralAnalyzer:
    """
    Analyze and validate orchestral MIDI templates.
    
    Detects:
    - Keyswitch tracks
    - Expression automation
    - Articulation layers
    - Divisi sections
    - Tempo/time signature changes
    """
    
    def __init__(self):
        self.keyswitch_low = KEYSWITCH_RANGES['low']
        self.keyswitch_high = KEYSWITCH_RANGES['high']
    
    def validate(self, data: MidiData) -> OrchestralValidation:
        """
        Validate orchestral MIDI and detect features.
        
        Args:
            data: MidiData object
        
        Returns:
            OrchestralValidation with analysis results
        """
        result = OrchestralValidation()
        result.total_tracks = len(data.tracks)
        
        # Check tempo map
        if len(data.tempo_map) > 1:
            result.has_tempo_changes = True
            result.warnings.append(f"File has {len(data.tempo_map)} tempo changes")
        
        # Analyze each track
        instruments_seen = set()
        
        for track in data.tracks:
            track_analysis = self._analyze_track(track, data.ppq)
            
            # Check for keyswitches
            keyswitch_notes = self._detect_keyswitches(track)
            if keyswitch_notes:
                result.has_keyswitches = True
                result.total_keyswitch_notes += len(keyswitch_notes)
            
            # Check for expression data
            expr_data = self._extract_expression_data(track)
            if expr_data:
                result.has_expression = True
                result.expression_data[track.index] = expr_data
                for ed in expr_data:
                    result.total_cc_events += len(ed.values)
            
            # Detect instrument and articulation
            inst_name = self._guess_instrument(track.name)
            if inst_name:
                instruments_seen.add(inst_name)
                
                # Check for articulation in track name
                articulation = self._detect_articulation(track.name)
                if articulation:
                    result.articulation_tracks.append(ArticulationTrack(
                        instrument=inst_name,
                        articulation=articulation,
                        track_index=track.index,
                        keyswitch_note=keyswitch_notes[0] if keyswitch_notes else None,
                        note_count=len(track.notes)
                    ))
        
        result.unique_instruments = len(instruments_seen)
        
        # Check for divisi (multiple tracks of same instrument)
        inst_track_counts = defaultdict(int)
        for art in result.articulation_tracks:
            inst_track_counts[art.instrument] += 1
        
        for inst, count in inst_track_counts.items():
            if count > 1:
                result.has_divisi = True
                result.warnings.append(f"Possible divisi: {inst} has {count} tracks")
        
        # Validate for common issues
        self._check_common_issues(data, result)
        
        return result
    
    def _analyze_track(self, track: TrackData, ppq: int) -> Dict:
        """Analyze a single track."""
        analysis = {
            'note_count': len(track.notes),
            'cc_count': 0,
            'pitch_bend_count': 0,
            'has_keyswitches': False,
        }
        
        for event in track.events:
            msg = event.message
            if hasattr(msg, 'type'):
                if msg.type == 'control_change':
                    analysis['cc_count'] += 1
                elif msg.type == 'pitchwheel':
                    analysis['pitch_bend_count'] += 1
        
        return analysis
    
    def _detect_keyswitches(self, track: TrackData) -> List[int]:
        """Detect keyswitch notes in track."""
        keyswitch_notes = []
        
        for note in track.notes:
            # Check if in keyswitch range
            if (self.keyswitch_low[0] <= note.pitch <= self.keyswitch_low[1] or
                self.keyswitch_high[0] <= note.pitch <= self.keyswitch_high[1]):
                
                # Keyswitches typically have:
                # - Very short duration (just triggers)
                # - Often same velocity
                # - Isolated from melodic content
                if note.duration_ticks < 100:  # Very short
                    keyswitch_notes.append(note.pitch)
        
        return list(set(keyswitch_notes))
    
    def _extract_expression_data(self, track: TrackData) -> List[ExpressionData]:
        """Extract expression controller data from track."""
        cc_data = defaultdict(list)
        
        for event in track.events:
            msg = event.message
            if hasattr(msg, 'type') and msg.type == 'control_change':
                if msg.control in (CC_MODWHEEL, CC_EXPRESSION, CC_VOLUME, CC_BREATH):
                    cc_data[msg.control].append((event.abs_time, msg.value))
        
        result = []
        for cc_num, values in cc_data.items():
            if len(values) > 1:  # Only if there's actual automation
                ed = ExpressionData(
                    track_index=track.index,
                    cc_number=cc_num,
                    values=sorted(values),
                    min_value=min(v[1] for v in values),
                    max_value=max(v[1] for v in values),
                    has_automation=True
                )
                result.append(ed)
        
        return result
    
    def _guess_instrument(self, track_name: str) -> Optional[str]:
        """Guess instrument from track name."""
        name_lower = track_name.lower()
        
        for family, instruments in ORCHESTRAL_FAMILIES.items():
            for inst in instruments:
                if inst in name_lower:
                    return inst
        
        # Common abbreviations
        abbrevs = {
            'vln': 'violin', 'vla': 'viola', 'vcl': 'cello', 'vc': 'cello',
            'cb': 'contrabass', 'db': 'contrabass',
            'fl': 'flute', 'ob': 'oboe', 'cl': 'clarinet', 'bn': 'bassoon',
            'hn': 'horn', 'tp': 'trumpet', 'tb': 'trombone',
            'timp': 'timpani', 'perc': 'percussion',
        }
        
        for abbrev, inst in abbrevs.items():
            if abbrev in name_lower:
                return inst
        
        return None
    
    def _detect_articulation(self, track_name: str) -> Optional[str]:
        """Detect articulation from track name."""
        name_lower = track_name.lower()
        
        articulations = [
            'legato', 'staccato', 'pizzicato', 'tremolo', 'trills',
            'spiccato', 'marcato', 'tenuto', 'sustain', 'short',
            'long', 'con sord', 'muted', 'harmonics', 'col legno',
            'sul pont', 'sul tasto', 'arco', 'detache',
        ]
        
        for art in articulations:
            if art in name_lower:
                return art
        
        return None
    
    def _check_common_issues(self, data: MidiData, result: OrchestralValidation):
        """Check for common orchestral MIDI issues."""
        
        # Check for empty tracks
        empty_tracks = [t.index for t in data.tracks if not t.notes and not t.events]
        if empty_tracks:
            result.warnings.append(f"Empty tracks: {empty_tracks}")
        
        # Check for overlapping notes (common issue)
        for track in data.tracks:
            overlaps = self._check_overlapping_notes(track)
            if overlaps > 0:
                result.warnings.append(f"Track {track.index} ({track.name}): {overlaps} overlapping notes")
        
        # Check for extreme CC density (might cause playback issues)
        for track_idx, expr_list in result.expression_data.items():
            for expr in expr_list:
                if len(expr.values) > 1000:
                    result.warnings.append(
                        f"Track {track_idx}: High CC{expr.cc_number} density ({len(expr.values)} events)"
                    )
        
        # Check for potential channel conflicts
        channels_used = defaultdict(list)
        for track in data.tracks:
            if track.channel is not None:
                channels_used[track.channel].append(track.name)
        
        for channel, track_names in channels_used.items():
            if len(track_names) > 1:
                result.warnings.append(
                    f"Channel {channel + 1} shared by: {', '.join(track_names)}"
                )
    
    def _check_overlapping_notes(self, track: TrackData) -> int:
        """Count overlapping notes of same pitch."""
        overlaps = 0
        notes_by_pitch = defaultdict(list)
        
        for note in track.notes:
            notes_by_pitch[note.pitch].append(note)
        
        for pitch, notes in notes_by_pitch.items():
            notes = sorted(notes, key=lambda n: n.onset_ticks)
            for i in range(1, len(notes)):
                prev_end = notes[i-1].onset_ticks + notes[i-1].duration_ticks
                if notes[i].onset_ticks < prev_end:
                    overlaps += 1
        
        return overlaps


def validate_orchestral(data: MidiData) -> OrchestralValidation:
    """Convenience function for orchestral validation."""
    analyzer = OrchestralAnalyzer()
    return analyzer.validate(data)


def is_orchestral_template(data: MidiData) -> bool:
    """
    Quick check if a MIDI file appears to be an orchestral template.
    """
    # Multiple tracks
    if len(data.tracks) < 5:
        return False
    
    # Check for orchestral instrument names
    orchestral_keywords = [
        'violin', 'viola', 'cello', 'bass', 'flute', 'oboe', 'clarinet',
        'bassoon', 'horn', 'trumpet', 'trombone', 'tuba', 'timpani',
        'strings', 'brass', 'woodwind', 'orchestra', 'ensemble'
    ]
    
    matches = 0
    for track in data.tracks:
        name_lower = track.name.lower()
        if any(kw in name_lower for kw in orchestral_keywords):
            matches += 1
    
    return matches >= 3
