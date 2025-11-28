"""
Auto Song Generator
Generate complete song structures with MIDI output.

Features:
- Genre-aware chord progressions
- Section-based arrangement
- Humanized timing from genre pockets
- Drum, bass, and chord MIDI generation
"""

import random
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

try:
    import mido
    HAS_MIDO = True
except ImportError:
    HAS_MIDO = False

from ..groove.pocket_rules import GENRE_POCKETS, get_pocket, get_push_pull, get_swing
from ..structure.progression import COMMON_PROGRESSIONS, ProgressionMatcher
from ..utils.ppq import STANDARD_PPQ


@dataclass
class SongSection:
    """A section of the song."""
    name: str           # verse, chorus, bridge, etc.
    bars: int           # Length in bars
    progression: List[int]  # Chord degrees
    energy: float       # 0-1
    has_drums: bool = True
    has_bass: bool = True
    has_chords: bool = True


@dataclass
class SongStructure:
    """Complete song structure."""
    title: str
    genre: str
    key: int            # 0-11 (C=0)
    bpm: int
    time_sig: Tuple[int, int]
    sections: List[SongSection]
    total_bars: int = 0
    
    def __post_init__(self):
        self.total_bars = sum(s.bars for s in self.sections)


# Common song arrangements by genre
SONG_TEMPLATES = {
    'pop': [
        ('intro', 4, 0.3),
        ('verse', 8, 0.5),
        ('prechorus', 4, 0.6),
        ('chorus', 8, 0.9),
        ('verse', 8, 0.5),
        ('prechorus', 4, 0.6),
        ('chorus', 8, 0.9),
        ('bridge', 8, 0.4),
        ('chorus', 8, 1.0),
        ('outro', 4, 0.3),
    ],
    'rock': [
        ('intro', 4, 0.6),
        ('verse', 8, 0.6),
        ('chorus', 8, 0.9),
        ('verse', 8, 0.6),
        ('chorus', 8, 0.9),
        ('solo', 8, 0.8),
        ('chorus', 8, 1.0),
        ('outro', 4, 0.5),
    ],
    'hiphop': [
        ('intro', 4, 0.4),
        ('verse', 16, 0.6),
        ('hook', 8, 0.8),
        ('verse', 16, 0.6),
        ('hook', 8, 0.8),
        ('bridge', 8, 0.5),
        ('hook', 8, 0.9),
        ('outro', 4, 0.3),
    ],
    'jazz': [
        ('head', 8, 0.6),
        ('solo_a', 8, 0.7),
        ('solo_b', 8, 0.8),
        ('solo_c', 8, 0.7),
        ('head', 8, 0.6),
        ('outro', 4, 0.4),
    ],
    'electronic': [
        ('intro', 8, 0.3),
        ('buildup', 8, 0.5),
        ('drop', 8, 0.9),
        ('breakdown', 8, 0.4),
        ('buildup', 8, 0.6),
        ('drop', 8, 1.0),
        ('outro', 8, 0.3),
    ],
    'lofi': [
        ('intro', 4, 0.4),
        ('a', 8, 0.5),
        ('b', 8, 0.6),
        ('a', 8, 0.5),
        ('b', 8, 0.6),
        ('outro', 4, 0.3),
    ],
}

# Progressions by section type
SECTION_PROGRESSIONS = {
    'intro': ['I-IV', 'I-V', 'vi-IV'],
    'verse': ['I-V-vi-IV', 'I-vi-IV-V', 'I-IV-V-I', 'vi-IV-I-V'],
    'prechorus': ['IV-V', 'ii-V', 'vi-V'],
    'chorus': ['I-V-vi-IV', 'I-IV-vi-V', 'vi-IV-I-V'],
    'hook': ['I-V-vi-IV', 'vi-IV-I-V'],
    'bridge': ['IV-I-V-vi', 'ii-V-I', 'vi-ii-V-I'],
    'breakdown': ['vi-IV', 'I-V'],
    'buildup': ['vi-IV-I-V'],
    'drop': ['I-V-vi-IV', 'vi-IV-I-V'],
    'head': ['ii-V-I', 'I-vi-ii-V'],
    'solo_a': ['ii-V-I', 'I-vi-ii-V'],
    'solo_b': ['ii-V-I'],
    'solo_c': ['ii-V-I'],
    'solo': ['I-IV-V-I', 'I-V-vi-IV'],
    'outro': ['IV-I', 'V-I', 'I'],
    'a': ['I-V-vi-IV', 'ii-V-I'],
    'b': ['vi-IV-I-V', 'IV-V-I'],
}

# Degree name to semitone mapping
DEGREE_TO_SEMITONE = {
    'I': 0, 'i': 0,
    'bII': 1, 'II': 2, 'ii': 2,
    'bIII': 3, 'III': 4, 'iii': 4,
    'IV': 5, 'iv': 5,
    'bV': 6, 'V': 7, 'v': 7,
    'bVI': 8, 'VI': 9, 'vi': 9,
    'bVII': 10, 'VII': 11, 'vii': 11,
}


class SongGenerator:
    """Generate song structures and MIDI."""
    
    def __init__(self, ppq: int = STANDARD_PPQ):
        self.ppq = ppq
        self.ticks_per_bar = ppq * 4  # Assuming 4/4
    
    def generate_structure(
        self,
        genre: str = 'pop',
        key: int = 0,
        bpm: Optional[int] = None,
        title: Optional[str] = None
    ) -> SongStructure:
        """
        Generate a song structure.
        
        Args:
            genre: Genre name
            key: Key root (0=C, 7=G, etc.)
            bpm: Tempo (or auto from genre)
            title: Song title (or auto-generated)
        
        Returns:
            SongStructure object
        """
        # Get genre pocket for BPM range
        pocket = get_pocket(genre) if genre in GENRE_POCKETS else GENRE_POCKETS.get('pop')
        
        # Auto BPM from genre range
        if bpm is None:
            bpm_range = pocket.get('bpm_range', (100, 120))
            bpm = random.randint(bpm_range[0], bpm_range[1])
        
        # Auto title
        if title is None:
            adjectives = ['Midnight', 'Golden', 'Electric', 'Velvet', 'Neon', 'Crystal', 'Shadow', 'Cosmic']
            nouns = ['Dreams', 'Waves', 'Echoes', 'Hearts', 'Lights', 'Streets', 'Skies', 'Memories']
            title = f"{random.choice(adjectives)} {random.choice(nouns)}"
        
        # Get song template
        template = SONG_TEMPLATES.get(genre, SONG_TEMPLATES['pop'])
        
        # Build sections
        sections = []
        for section_name, bars, energy in template:
            # Get progression for this section type
            prog_options = SECTION_PROGRESSIONS.get(section_name, ['I-IV-V-I'])
            prog_str = random.choice(prog_options)
            
            # Parse progression string to degrees
            degrees = self._parse_progression(prog_str)
            
            # Determine what plays in this section
            has_drums = energy > 0.2
            has_bass = energy > 0.3
            has_chords = True
            
            # Intro/outro might be sparse
            if section_name in ('intro', 'outro'):
                has_drums = random.random() < 0.5
            
            section = SongSection(
                name=section_name,
                bars=bars,
                progression=degrees,
                energy=energy,
                has_drums=has_drums,
                has_bass=has_bass,
                has_chords=has_chords
            )
            sections.append(section)
        
        return SongStructure(
            title=title,
            genre=genre,
            key=key,
            bpm=bpm,
            time_sig=(4, 4),
            sections=sections
        )
    
    def _parse_progression(self, prog_str: str) -> List[int]:
        """Parse progression string like 'I-V-vi-IV' to semitone list."""
        parts = prog_str.replace(' ', '').split('-')
        degrees = []
        
        for part in parts:
            # Strip any chord type suffix for now
            degree = part.rstrip('7').rstrip('maj').rstrip('min').rstrip('dim')
            if degree in DEGREE_TO_SEMITONE:
                degrees.append(DEGREE_TO_SEMITONE[degree])
            else:
                degrees.append(0)  # Default to I
        
        return degrees
    
    def generate_midi(
        self,
        structure: SongStructure,
        output_path: str,
        humanize: bool = True
    ) -> str:
        """
        Generate MIDI file from song structure.
        
        Args:
            structure: SongStructure object
            output_path: Path to save MIDI
            humanize: Apply genre-appropriate humanization
        
        Returns:
            Path to generated MIDI file
        """
        if not HAS_MIDO:
            raise ImportError("mido required for MIDI generation")
        
        mid = mido.MidiFile(ticks_per_beat=self.ppq)
        
        # Create tracks
        drum_track = mido.MidiTrack()
        bass_track = mido.MidiTrack()
        chord_track = mido.MidiTrack()
        
        drum_track.name = 'Drums'
        bass_track.name = 'Bass'
        chord_track.name = 'Chords'
        
        mid.tracks.append(drum_track)
        mid.tracks.append(bass_track)
        mid.tracks.append(chord_track)
        
        # Add tempo
        tempo = mido.bpm2tempo(structure.bpm)
        drum_track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
        
        # Get genre pocket for humanization
        pocket = get_pocket(structure.genre)
        swing = pocket.get('swing', 0.5) if humanize else 0.5
        push_pull = pocket.get('push_pull', {}) if humanize else {}
        
        # Generate each section
        current_tick = 0
        
        for section in structure.sections:
            current_tick = self._generate_section(
                section, structure,
                drum_track, bass_track, chord_track,
                current_tick, swing, push_pull, humanize
            )
        
        # Save
        output_path = Path(output_path)
        mid.save(str(output_path))
        
        return str(output_path)
    
    def _generate_section(
        self,
        section: SongSection,
        structure: SongStructure,
        drum_track: mido.MidiTrack,
        bass_track: mido.MidiTrack,
        chord_track: mido.MidiTrack,
        start_tick: int,
        swing: float,
        push_pull: dict,
        humanize: bool
    ) -> int:
        """Generate MIDI for one section. Returns end tick."""
        
        bars = section.bars
        progression = section.progression
        energy = section.energy
        key = structure.key
        
        # Velocity based on energy
        base_vel = int(60 + energy * 50)
        
        current_tick = start_tick
        
        for bar in range(bars):
            # Get chord for this bar (cycle through progression)
            chord_degree = progression[bar % len(progression)]
            chord_root = (key + chord_degree) % 12
            
            # Generate drums for this bar
            if section.has_drums:
                self._generate_drum_bar(
                    drum_track, current_tick, energy, swing, push_pull, humanize
                )
            
            # Generate bass for this bar
            if section.has_bass:
                self._generate_bass_bar(
                    bass_track, current_tick, chord_root, energy, push_pull, humanize
                )
            
            # Generate chords for this bar
            if section.has_chords:
                self._generate_chord_bar(
                    chord_track, current_tick, chord_root, energy, push_pull, humanize
                )
            
            current_tick += self.ticks_per_bar
        
        return current_tick
    
    def _generate_drum_bar(
        self,
        track: mido.MidiTrack,
        bar_start: int,
        energy: float,
        swing: float,
        push_pull: dict,
        humanize: bool
    ):
        """Generate one bar of drums."""
        ppq = self.ppq
        
        # Basic pattern: kick on 1 and 3, snare on 2 and 4
        # Hi-hat on 8ths or 16ths based on energy
        
        kick_times = [0, ppq * 2]  # Beats 1 and 3
        snare_times = [ppq, ppq * 3]  # Beats 2 and 4
        
        # Hi-hat pattern
        if energy > 0.7:
            # 16th notes
            hihat_times = [ppq * i // 4 for i in range(16)]
        else:
            # 8th notes
            hihat_times = [ppq * i // 2 for i in range(8)]
        
        # Apply swing to off-beat hi-hats
        if swing > 0.5:
            swing_amount = int((swing - 0.5) * ppq)
            hihat_times = [
                t + swing_amount if (i % 2 == 1) else t
                for i, t in enumerate(hihat_times)
            ]
        
        # Get push/pull offsets
        kick_offset = push_pull.get('kick', 0) if humanize else 0
        snare_offset = push_pull.get('snare', 0) if humanize else 0
        hihat_offset = push_pull.get('hihat', 0) if humanize else 0
        
        # Velocity
        base_vel = int(80 + energy * 30)
        
        # Collect all events with absolute times
        events = []
        
        # Kicks (note 36)
        for t in kick_times:
            abs_t = bar_start + t + kick_offset
            vel = base_vel + random.randint(-5, 5) if humanize else base_vel
            events.append((abs_t, 'note_on', 36, vel, 9))
            events.append((abs_t + ppq // 4, 'note_off', 36, 0, 9))
        
        # Snares (note 38)
        for t in snare_times:
            abs_t = bar_start + t + snare_offset
            vel = base_vel + random.randint(-5, 5) if humanize else base_vel
            events.append((abs_t, 'note_on', 38, vel, 9))
            events.append((abs_t + ppq // 4, 'note_off', 38, 0, 9))
        
        # Hi-hats (note 42)
        for i, t in enumerate(hihat_times):
            abs_t = bar_start + t + hihat_offset
            # Accent on downbeats
            accent = 15 if i % 4 == 0 else 0
            vel = int(base_vel * 0.7) + accent + (random.randint(-8, 8) if humanize else 0)
            vel = max(1, min(127, vel))
            events.append((abs_t, 'note_on', 42, vel, 9))
            events.append((abs_t + ppq // 8, 'note_off', 42, 0, 9))
        
        # Sort by time and add to track
        events.sort(key=lambda x: x[0])
        
        for abs_t, msg_type, note, vel, ch in events:
            if msg_type == 'note_on':
                track.append(mido.Message('note_on', note=note, velocity=vel, channel=ch, time=0))
            else:
                track.append(mido.Message('note_off', note=note, velocity=0, channel=ch, time=0))
    
    def _generate_bass_bar(
        self,
        track: mido.MidiTrack,
        bar_start: int,
        root: int,
        energy: float,
        push_pull: dict,
        humanize: bool
    ):
        """Generate one bar of bass."""
        ppq = self.ppq
        
        # Bass note (octave 2 = MIDI 36-47)
        bass_note = 36 + root
        
        # Simple pattern: root on 1 and 3, with variations
        if energy > 0.6:
            # More active pattern
            times = [0, ppq, ppq * 2, ppq * 3]
            notes = [bass_note, bass_note + 7, bass_note, bass_note + 5]  # Root, 5th, root, 4th
        else:
            # Simple pattern
            times = [0, ppq * 2]
            notes = [bass_note, bass_note]
        
        bass_offset = push_pull.get('bass', 0) if humanize else 0
        base_vel = int(70 + energy * 30)
        
        for t, note in zip(times, notes):
            abs_t = bar_start + t + bass_offset
            vel = base_vel + (random.randint(-5, 5) if humanize else 0)
            vel = max(1, min(127, vel))
            
            track.append(mido.Message('note_on', note=note, velocity=vel, channel=1, time=0))
            track.append(mido.Message('note_off', note=note, velocity=0, channel=1, time=0))
    
    def _generate_chord_bar(
        self,
        track: mido.MidiTrack,
        bar_start: int,
        root: int,
        energy: float,
        push_pull: dict,
        humanize: bool
    ):
        """Generate one bar of chords."""
        ppq = self.ppq
        
        # Chord notes (major triad in octave 4 = MIDI 60-71)
        chord_notes = [60 + root, 60 + root + 4, 60 + root + 7]  # Root, 3rd, 5th
        
        # Play chord on beat 1 (whole note or half notes)
        if energy > 0.5:
            times = [0, ppq * 2]  # Half notes
            duration = ppq * 2 - 10
        else:
            times = [0]  # Whole note
            duration = ppq * 4 - 10
        
        keys_offset = push_pull.get('keys', 0) if humanize else 0
        base_vel = int(50 + energy * 40)
        
        for t in times:
            abs_t = bar_start + t + keys_offset
            
            for note in chord_notes:
                vel = base_vel + (random.randint(-5, 5) if humanize else 0)
                vel = max(1, min(127, vel))
                
                track.append(mido.Message('note_on', note=note, velocity=vel, channel=0, time=0))
            
            # Note offs
            for note in chord_notes:
                track.append(mido.Message('note_off', note=note, velocity=0, channel=0, time=0))


def generate_song(
    genre: str = 'pop',
    output_path: Optional[str] = None,
    key: int = 0,
    bpm: Optional[int] = None,
    title: Optional[str] = None,
    humanize: bool = True
) -> Tuple[SongStructure, str]:
    """
    Convenience function to generate a complete song.
    
    Args:
        genre: Genre name
        output_path: Output MIDI path (auto-generated if None)
        key: Key root (0=C)
        bpm: Tempo (auto from genre if None)
        title: Song title (auto-generated if None)
        humanize: Apply genre humanization
    
    Returns:
        (SongStructure, midi_path)
    """
    generator = SongGenerator()
    
    structure = generator.generate_structure(
        genre=genre,
        key=key,
        bpm=bpm,
        title=title
    )
    
    if output_path is None:
        safe_title = structure.title.lower().replace(' ', '_')
        output_path = f"{safe_title}_{structure.genre}_{structure.bpm}bpm.mid"
    
    midi_path = generator.generate_midi(structure, output_path, humanize=humanize)
    
    return structure, midi_path
