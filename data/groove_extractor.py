"""
Groove Extraction & Analysis - Extract timing and velocity patterns from MIDI

This module analyzes MIDI drum patterns to extract:
- Timing deviations (swing, push/pull, pocket)
- Velocity contours (accent patterns, dynamics)
- Genre-specific groove templates

Philosophy: "Feel isn't random - it's systematic deviation from the grid."
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import statistics
from collections import defaultdict


@dataclass
class MidiNote:
    """Single MIDI note with timing and velocity"""
    note: int  # MIDI note number (36 = kick, 38 = snare, etc.)
    time: int  # Time in ticks from start
    velocity: int  # 0-127
    duration: int  # Duration in ticks
    
    @property
    def note_name(self) -> str:
        """Get drum name from MIDI note number"""
        drum_map = {
            35: 'kick_acoustic', 36: 'kick', 37: 'rim', 38: 'snare',
            39: 'clap', 40: 'snare_electric', 41: 'tom_low',
            42: 'hihat_closed', 43: 'tom_low_mid', 44: 'hihat_pedal',
            45: 'tom_mid', 46: 'hihat_open', 47: 'tom_mid_high',
            48: 'tom_high', 49: 'crash', 50: 'tom_higher',
            51: 'ride', 52: 'crash_chinese', 53: 'ride_bell',
        }
        return drum_map.get(self.note, f'note_{self.note}')


@dataclass
class TimingDeviation:
    """Timing deviation from perfect grid"""
    beat_position: float  # Position in beats (0.0 = downbeat, 0.5 = offbeat, etc.)
    expected_time: int  # Where it "should" be (ticks)
    actual_time: int  # Where it actually is (ticks)
    deviation_ticks: int  # Difference (positive = late, negative = early)
    deviation_percent: float  # As percentage of beat subdivision
    note_type: str  # 'kick', 'snare', 'hihat', etc.


@dataclass
class VelocityPattern:
    """Velocity pattern over time"""
    beat_position: float
    velocity: int
    note_type: str
    is_accent: bool  # True if significantly louder than average


@dataclass
class GrooveProfile:
    """Complete groove analysis of a MIDI pattern"""
    name: str = ""
    tempo_bpm: float = 120.0
    ppq: int = 480  # Pulses per quarter note
    
    # Timing analysis
    timing_deviations: List[TimingDeviation] = field(default_factory=list)
    swing_percentage: float = 0.0  # 0-100% (50% = straight, 66% = triplet swing)
    average_push_pull: Dict[str, float] = field(default_factory=dict)  # ms per note type
    
    # Velocity analysis
    velocity_patterns: List[VelocityPattern] = field(default_factory=list)
    velocity_range: Tuple[int, int] = (0, 127)
    accent_threshold: int = 100
    
    # Genre classification
    genre_hints: List[str] = field(default_factory=list)
    pocket_description: str = ""


class GrooveExtractor:
    """
    Extract groove characteristics from MIDI drum patterns.
    
    Analyzes timing deviations, velocity patterns, and generates
    reusable groove templates for different genres.
    """
    
    # Standard drum MIDI note numbers (GM standard)
    KICK_NOTES = [35, 36]
    SNARE_NOTES = [38, 40]
    HIHAT_NOTES = [42, 44, 46]
    TOM_NOTES = [41, 43, 45, 47, 48, 50]
    CYMBAL_NOTES = [49, 51, 52, 53, 55, 57, 59]
    
    def __init__(self, ppq: int = 480):
        """
        Initialize groove extractor.
        
        Args:
            ppq: Pulses per quarter note (ticks per beat)
        """
        self.ppq = ppq
    
    def extract_from_midi_file(self, midi_path: str) -> GrooveProfile:
        """
        Extract groove from a MIDI file.
        
        Args:
            midi_path: Path to MIDI file
            
        Returns:
            GrooveProfile with timing and velocity analysis
        """
        import mido
        
        mid = mido.MidiFile(midi_path)
        
        # Get tempo
        tempo_bpm = 120.0
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    tempo_bpm = mido.tempo2bpm(msg.tempo)
                    break
        
        # Extract notes from drum track
        notes = self._extract_notes_from_midi(mid)
        
        if not notes:
            return GrooveProfile(name="empty", tempo_bpm=tempo_bpm, ppq=mid.ticks_per_beat)
        
        # Analyze timing
        timing_deviations = self._analyze_timing(notes, mid.ticks_per_beat)
        swing_pct = self._calculate_swing_percentage(timing_deviations)
        push_pull = self._calculate_push_pull(timing_deviations)
        
        # Analyze velocity
        velocity_patterns = self._analyze_velocity(notes, mid.ticks_per_beat)
        vel_range = self._calculate_velocity_range(notes)
        accent_thresh = self._calculate_accent_threshold(notes)
        
        # Genre classification
        genre_hints = self._classify_genre(timing_deviations, velocity_patterns, tempo_bpm)
        pocket_desc = self._describe_pocket(swing_pct, push_pull, genre_hints)
        
        return GrooveProfile(
            name=f"extracted_groove_{int(tempo_bpm)}bpm",
            tempo_bpm=tempo_bpm,
            ppq=mid.ticks_per_beat,
            timing_deviations=timing_deviations,
            swing_percentage=swing_pct,
            average_push_pull=push_pull,
            velocity_patterns=velocity_patterns,
            velocity_range=vel_range,
            accent_threshold=accent_thresh,
            genre_hints=genre_hints,
            pocket_description=pocket_desc
        )
    
    def _extract_notes_from_midi(self, mid) -> List[MidiNote]:
        """Extract all note events from MIDI file"""
        notes = []
        
        for track in mid.tracks:
            current_time = 0
            active_notes = {}  # note_number -> (start_time, velocity)
            
            for msg in track:
                current_time += msg.time
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes[msg.note] = (current_time, msg.velocity)
                
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in active_notes:
                        start_time, velocity = active_notes[msg.note]
                        duration = current_time - start_time
                        
                        notes.append(MidiNote(
                            note=msg.note,
                            time=start_time,
                            velocity=velocity,
                            duration=duration
                        ))
                        
                        del active_notes[msg.note]
        
        # Sort by time
        notes.sort(key=lambda n: n.time)
        return notes
    
    def _get_note_category(self, note_number: int) -> str:
        """Categorize drum note"""
        if note_number in self.KICK_NOTES:
            return 'kick'
        elif note_number in self.SNARE_NOTES:
            return 'snare'
        elif note_number in self.HIHAT_NOTES:
            return 'hihat'
        elif note_number in self.TOM_NOTES:
            return 'tom'
        elif note_number in self.CYMBAL_NOTES:
            return 'cymbal'
        else:
            return 'other'
    
    def _analyze_timing(self, notes: List[MidiNote], ppq: int) -> List[TimingDeviation]:
        """
        Analyze timing deviations from perfect grid.
        
        Quantizes to 16th notes and measures deviation.
        """
        deviations = []
        sixteenth_note = ppq // 4  # 16th note duration in ticks
        
        for note in notes:
            # Find nearest 16th note grid position
            beat_position = note.time / ppq
            nearest_sixteenth = round(note.time / sixteenth_note) * sixteenth_note
            
            deviation_ticks = note.time - nearest_sixteenth
            
            # Calculate as percentage of 16th note
            if sixteenth_note > 0:
                deviation_percent = (deviation_ticks / sixteenth_note) * 100
            else:
                deviation_percent = 0.0
            
            deviations.append(TimingDeviation(
                beat_position=beat_position,
                expected_time=nearest_sixteenth,
                actual_time=note.time,
                deviation_ticks=deviation_ticks,
                deviation_percent=deviation_percent,
                note_type=self._get_note_category(note.note)
            ))
        
        return deviations
    
    def _calculate_swing_percentage(self, deviations: List[TimingDeviation]) -> float:
        """
        Calculate swing percentage (50% = straight, 66% = triplet swing).
        
        Measures timing of offbeat hits relative to downbeats.
        """
        if not deviations:
            return 50.0
        
        # Find offbeat (2nd and 4th 16th notes) deviations
        offbeat_deviations = [
            d for d in deviations
            if 0.25 < (d.beat_position % 0.5) < 0.75  # Offbeats
        ]
        
        if not offbeat_deviations:
            return 50.0
        
        # Average deviation on offbeats
        avg_deviation = statistics.mean([d.deviation_percent for d in offbeat_deviations])
        
        # Convert to swing percentage
        # 0% deviation = 50% swing (straight)
        # +15% deviation = 66% swing (triplet)
        # -15% deviation = 33% swing (reverse swing, rare)
        swing_pct = 50.0 + (avg_deviation * 1.1)
        
        return max(33.0, min(75.0, swing_pct))  # Clamp to reasonable range
    
    def _calculate_push_pull(self, deviations: List[TimingDeviation]) -> Dict[str, float]:
        """
        Calculate average push/pull for each note type.
        
        Returns average deviation in milliseconds at 120 BPM.
        """
        push_pull = defaultdict(list)
        
        for dev in deviations:
            push_pull[dev.note_type].append(dev.deviation_ticks)
        
        # Calculate averages and convert to milliseconds
        result = {}
        for note_type, deviations_list in push_pull.items():
            avg_ticks = statistics.mean(deviations_list)
            # At 120 BPM, quarter note = 500ms
            # So one tick = (500 / ppq) ms
            avg_ms = (avg_ticks / self.ppq) * 500
            result[note_type] = round(avg_ms, 2)
        
        return result
    
    def _analyze_velocity(self, notes: List[MidiNote], ppq: int) -> List[VelocityPattern]:
        """Analyze velocity patterns over time"""
        patterns = []
        
        # Calculate average velocity for accent detection
        avg_velocity = statistics.mean([n.velocity for n in notes]) if notes else 80
        accent_threshold = avg_velocity * 1.25  # 25% above average = accent
        
        for note in notes:
            beat_position = note.time / ppq
            is_accent = note.velocity >= accent_threshold
            
            patterns.append(VelocityPattern(
                beat_position=beat_position,
                velocity=note.velocity,
                note_type=self._get_note_category(note.note),
                is_accent=is_accent
            ))
        
        return patterns
    
    def _calculate_velocity_range(self, notes: List[MidiNote]) -> Tuple[int, int]:
        """Calculate velocity range (min, max)"""
        if not notes:
            return (0, 127)
        
        velocities = [n.velocity for n in notes]
        return (min(velocities), max(velocities))
    
    def _calculate_accent_threshold(self, notes: List[MidiNote]) -> int:
        """Calculate velocity threshold for accents"""
        if not notes:
            return 100
        
        avg_velocity = statistics.mean([n.velocity for n in notes])
        return int(avg_velocity * 1.25)
    
    def _classify_genre(
        self,
        timing: List[TimingDeviation],
        velocity: List[VelocityPattern],
        tempo: float
    ) -> List[str]:
        """Attempt to classify groove into genre categories"""
        hints = []
        
        # Tempo-based hints
        if tempo < 90:
            hints.append("slow (hip-hop/downtempo)")
        elif 90 <= tempo < 110:
            hints.append("medium (boom-bap/soul)")
        elif 110 <= tempo < 140:
            hints.append("uptempo (funk/rock)")
        else:
            hints.append("fast (punk/metal/dnb)")
        
        # Swing-based hints
        if timing:
            avg_deviation = statistics.mean([abs(d.deviation_percent) for d in timing])
            
            if avg_deviation < 2:
                hints.append("quantized (electronic)")
            elif 2 <= avg_deviation < 8:
                hints.append("slight swing (funk/R&B)")
            elif avg_deviation >= 8:
                hints.append("heavy swing (jazz/blues)")
        
        # Velocity dynamics hints
        if velocity:
            velocities = [v.velocity for v in velocity]
            velocity_range = max(velocities) - min(velocities)
            
            if velocity_range < 20:
                hints.append("flat dynamics (electronic)")
            elif 20 <= velocity_range < 50:
                hints.append("moderate dynamics")
            else:
                hints.append("high dynamics (live/expressive)")
        
        return hints
    
    def _describe_pocket(
        self,
        swing_pct: float,
        push_pull: Dict[str, float],
        genre_hints: List[str]
    ) -> str:
        """Generate human-readable pocket description"""
        descriptions = []
        
        # Swing description
        if 48 <= swing_pct <= 52:
            descriptions.append("straight 16ths")
        elif 52 < swing_pct <= 60:
            descriptions.append("slight swing")
        elif 60 < swing_pct <= 68:
            descriptions.append("triplet swing")
        elif swing_pct > 68:
            descriptions.append("heavy shuffle")
        else:
            descriptions.append("reverse swing (rare)")
        
        # Push/pull description
        if 'kick' in push_pull:
            kick_ms = push_pull['kick']
            if kick_ms > 5:
                descriptions.append(f"kick pushes {kick_ms:.1f}ms")
            elif kick_ms < -5:
                descriptions.append(f"kick pulls {abs(kick_ms):.1f}ms")
        
        if 'snare' in push_pull:
            snare_ms = push_pull['snare']
            if snare_ms > 5:
                descriptions.append(f"snare lays back {snare_ms:.1f}ms")
            elif snare_ms < -5:
                descriptions.append(f"snare rushes {abs(snare_ms):.1f}ms")
        
        # Genre context
        if genre_hints:
            descriptions.append(f"({', '.join(genre_hints[:2])})")
        
        return " | ".join(descriptions)


def print_groove_analysis(profile: GrooveProfile):
    """Pretty-print groove analysis"""
    print("=" * 70)
    print(f"GROOVE ANALYSIS: {profile.name}")
    print("=" * 70)
    
    print(f"\nTempo: {profile.tempo_bpm} BPM")
    print(f"Swing: {profile.swing_percentage:.1f}% ", end="")
    if 48 <= profile.swing_percentage <= 52:
        print("(straight)")
    elif profile.swing_percentage > 60:
        print("(swung)")
    else:
        print("(slight swing)")
    
    print(f"\nPocket Description:")
    print(f"  {profile.pocket_description}")
    
    if profile.average_push_pull:
        print(f"\nTiming Characteristics (push/pull):")
        for note_type, ms in sorted(profile.average_push_pull.items()):
            direction = "pushes" if ms > 0 else "pulls"
            print(f"  {note_type:8} {direction:6} {abs(ms):5.2f}ms")
    
    if profile.velocity_patterns:
        velocities = [v.velocity for v in profile.velocity_patterns]
        avg_vel = statistics.mean(velocities)
        print(f"\nVelocity Characteristics:")
        print(f"  Range: {profile.velocity_range[0]} - {profile.velocity_range[1]}")
        print(f"  Average: {avg_vel:.1f}")
        print(f"  Accent threshold: {profile.accent_threshold}")
        
        # Count accents
        accents = sum(1 for v in profile.velocity_patterns if v.is_accent)
        accent_pct = (accents / len(profile.velocity_patterns)) * 100
        print(f"  Accents: {accents}/{len(profile.velocity_patterns)} ({accent_pct:.1f}%)")
    
    if profile.genre_hints:
        print(f"\nGenre Hints:")
        for hint in profile.genre_hints:
            print(f"  • {hint}")
    
    print("=" * 70)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("\nGroove Extractor - Example Usage\n")
    
    # Example 1: Create a simple test MIDI file with groove
    print("Creating test MIDI with funk groove...")
    
    import mido
    
    # Create a funky drum pattern with swing and dynamics
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo to 95 BPM (funk tempo)
    tempo = mido.bpm2tempo(95)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    
    ppq = mid.ticks_per_beat
    sixteenth = ppq // 4
    
    # Funky pattern with swing and ghost notes
    # Bar 1: K-h-K-H-s-h-K-h-K-h-K-H-s-h-K-h
    pattern = [
        # Beat 1
        (0, 36, 100),           # Kick (downbeat)
        (sixteenth, 42, 60),    # Hihat (ghost note)
        
        # Beat 1.5 (swung - push by 10 ticks)
        (sixteenth + 10, 36, 85),  # Kick (swung, slightly softer)
        (sixteenth, 42, 65),    # Hihat
        
        # Beat 2
        (sixteenth, 38, 110),   # Snare (accent)
        (sixteenth, 42, 60),    # Hihat (ghost)
        
        # Beat 2.5 (swung)
        (sixteenth + 10, 36, 80),  # Kick
        (sixteenth, 42, 65),    # Hihat
        
        # Beat 3
        (sixteenth, 36, 95),    # Kick
        (sixteenth, 42, 70),    # Hihat (slightly louder)
        
        # Beat 3.5 (swung)
        (sixteenth + 10, 36, 85),  # Kick
        (sixteenth, 42, 65),    # Hihat
        
        # Beat 4
        (sixteenth, 38, 115),   # Snare (strong accent)
        (sixteenth, 42, 60),    # Hihat
        
        # Beat 4.5 (swung)
        (sixteenth + 10, 36, 80),  # Kick
        (sixteenth, 42, 65),    # Hihat
    ]
    
    # Add notes to track
    current_time = 0
    for delta, note, velocity in pattern:
        track.append(mido.Message('note_on', note=note, velocity=velocity, time=delta))
        track.append(mido.Message('note_off', note=note, velocity=0, time=sixteenth//2))
        current_time += delta + sixteenth//2
    
    # Save test file
    test_file = "/home/claude/funk_groove_test.mid"
    mid.save(test_file)
    print(f"✓ Saved: {test_file}\n")
    
    # Extract groove
    extractor = GrooveExtractor()
    groove = extractor.extract_from_midi_file(test_file)
    
    # Print analysis
    print_groove_analysis(groove)
    
    # Save analysis to JSON
    import json
    
    analysis_data = {
        'name': groove.name,
        'tempo_bpm': groove.tempo_bpm,
        'swing_percentage': groove.swing_percentage,
        'pocket_description': groove.pocket_description,
        'average_push_pull': groove.average_push_pull,
        'velocity_range': groove.velocity_range,
        'accent_threshold': groove.accent_threshold,
        'genre_hints': groove.genre_hints
    }
    
    json_file = "/mnt/user-data/outputs/funk_groove_analysis.json"
    with open(json_file, 'w') as f:
        json.dump(analysis_data, f, indent=2)
    
    print(f"\n✓ Analysis saved: {json_file}")
