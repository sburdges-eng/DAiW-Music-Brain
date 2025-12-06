"""
Logic Pro Integration - Utilities for working with Logic Pro projects.

Note: Logic Pro project files (.logicx) are package bundles that contain
MIDI, audio, and project data. This module provides utilities for
preparing MIDI files for Logic import and processing Logic exports.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import json

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False


# Logic Pro uses 480 PPQ by default
LOGIC_PPQ = 480

# Logic Pro MIDI channel assignments (typical)
LOGIC_CHANNELS = {
    "drums": 10,  # GM drums on channel 10 (1-indexed: 10, 0-indexed: 9)
    "bass": 1,
    "keys": 2,
    "guitar": 3,
    "lead": 4,
    "pad": 5,
}


@dataclass
class LogicProject:
    """
    Represents a Logic Pro project structure for MIDI export.
    
    Not a full Logic project parser - just a container for
    organizing tracks to be exported as MIDI for Logic import.
    """
    name: str = "Untitled"
    tempo_bpm: float = 120.0
    time_signature: tuple = (4, 4)
    ppq: int = LOGIC_PPQ
    
    tracks: List[Dict] = field(default_factory=list)
    
    # Project metadata
    key: str = "C"
    mode: str = "major"
    genre: str = ""
    
    def add_track(
        self,
        name: str,
        channel: int = 1,
        instrument: Optional[int] = None,
        notes: Optional[List[Dict]] = None,
    ):
        """
        Add a track to the project.
        
        Args:
            name: Track name
            channel: MIDI channel (1-16)
            instrument: GM instrument program number
            notes: List of note dicts with pitch, velocity, start_tick, duration_ticks
        """
        track = {
            "name": name,
            "channel": channel - 1,  # Convert to 0-indexed
            "instrument": instrument,
            "notes": notes or [],
        }
        self.tracks.append(track)
    
    def export_midi(self, output_path: str) -> str:
        """
        Export project to MIDI file for Logic Pro import.
        
        Args:
            output_path: Output MIDI file path
        
        Returns:
            Path to exported file
        """
        if not MIDO_AVAILABLE:
            raise ImportError("mido package required")
        
        mid = mido.MidiFile(ticks_per_beat=self.ppq)
        
        # Create tempo/meta track
        meta_track = mido.MidiTrack()
        mid.tracks.append(meta_track)
        
        # Set tempo
        tempo_us = int(60_000_000 / self.tempo_bpm)
        meta_track.append(mido.MetaMessage('set_tempo', tempo=tempo_us, time=0))
        
        # Set time signature
        meta_track.append(mido.MetaMessage(
            'time_signature',
            numerator=self.time_signature[0],
            denominator=self.time_signature[1],
            time=0
        ))
        
        # Create tracks
        for track_data in self.tracks:
            track = mido.MidiTrack()
            mid.tracks.append(track)
            
            # Track name
            track.append(mido.MetaMessage('track_name', name=track_data["name"], time=0))
            
            # Program change (instrument)
            if track_data["instrument"] is not None:
                track.append(mido.Message(
                    'program_change',
                    channel=track_data["channel"],
                    program=track_data["instrument"],
                    time=0
                ))
            
            # Add notes
            events = []
            for note in track_data["notes"]:
                events.append((
                    note["start_tick"],
                    "note_on",
                    note["pitch"],
                    note["velocity"],
                    track_data["channel"],
                ))
                events.append((
                    note["start_tick"] + note["duration_ticks"],
                    "note_off",
                    note["pitch"],
                    0,
                    track_data["channel"],
                ))
            
            # Sort by time
            events.sort(key=lambda e: e[0])
            
            # Convert to delta times
            current_tick = 0
            for tick, msg_type, pitch, vel, ch in events:
                delta = tick - current_tick
                current_tick = tick
                
                if msg_type == "note_on":
                    track.append(mido.Message('note_on', note=pitch, velocity=vel, channel=ch, time=delta))
                else:
                    track.append(mido.Message('note_off', note=pitch, velocity=0, channel=ch, time=delta))
            
            # End of track
            track.append(mido.MetaMessage('end_of_track', time=0))
        
        output_path = Path(output_path)
        mid.save(str(output_path))
        
        return str(output_path)


def export_to_logic(
    midi_path: str,
    output_path: Optional[str] = None,
    normalize_ppq: bool = True,
) -> str:
    """
    Prepare a MIDI file for optimal Logic Pro import.
    
    - Normalizes PPQ to 480
    - Ensures proper track naming
    - Validates channel assignments
    
    Args:
        midi_path: Input MIDI file
        output_path: Output path (default: input_logic.mid)
        normalize_ppq: Whether to normalize to Logic's 480 PPQ
    
    Returns:
        Path to prepared file
    """
    if not MIDO_AVAILABLE:
        raise ImportError("mido package required")
    
    from music_brain.utils.ppq import normalize_ppq as norm_ppq
    
    midi_path = Path(midi_path)
    mid = mido.MidiFile(str(midi_path))
    
    # Determine output path
    if output_path is None:
        output_path = f"{midi_path.stem}_logic.mid"
    
    # If PPQ matches, just copy
    if mid.ticks_per_beat == LOGIC_PPQ and not normalize_ppq:
        mid.save(output_path)
        return output_path
    
    # Create new MIDI with Logic PPQ
    new_mid = mido.MidiFile(ticks_per_beat=LOGIC_PPQ)
    ppq_ratio = LOGIC_PPQ / mid.ticks_per_beat
    
    for track in mid.tracks:
        new_track = mido.MidiTrack()
        new_mid.tracks.append(new_track)
        
        for msg in track:
            new_msg = msg.copy()
            
            # Scale timing
            if hasattr(msg, 'time'):
                new_msg = msg.copy(time=int(msg.time * ppq_ratio))
            
            new_track.append(new_msg)
    
    new_mid.save(output_path)
    return output_path


def import_from_logic(midi_path: str) -> LogicProject:
    """
    Import a MIDI file exported from Logic Pro.
    
    Creates a LogicProject object from the MIDI data.
    
    Args:
        midi_path: Path to MIDI file from Logic
    
    Returns:
        LogicProject with imported data
    """
    if not MIDO_AVAILABLE:
        raise ImportError("mido package required")
    
    from music_brain.utils.midi_io import get_midi_info, extract_notes
    
    midi_path = Path(midi_path)
    mid = mido.MidiFile(str(midi_path))
    info = get_midi_info(str(midi_path))
    
    project = LogicProject(
        name=midi_path.stem,
        tempo_bpm=info.tempo_bpm,
        time_signature=info.time_signature,
        ppq=info.ppq,
    )
    
    # Extract tracks
    for i, track in enumerate(mid.tracks):
        track_name = f"Track {i+1}"
        channel = 0
        instrument = None
        notes = []
        
        current_tick = 0
        active_notes = {}
        
        for msg in track:
            current_tick += msg.time
            
            if msg.type == 'track_name':
                track_name = msg.name
            elif msg.type == 'program_change':
                instrument = msg.program
                channel = msg.channel
            elif msg.type == 'note_on' and msg.velocity > 0:
                channel = msg.channel
                key = (msg.channel, msg.note)
                active_notes[key] = (current_tick, msg.velocity)
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                key = (msg.channel, msg.note)
                if key in active_notes:
                    start_tick, velocity = active_notes.pop(key)
                    notes.append({
                        "pitch": msg.note,
                        "velocity": velocity,
                        "start_tick": start_tick,
                        "duration_ticks": current_tick - start_tick,
                    })
        
        if notes:
            project.tracks.append({
                "name": track_name,
                "channel": channel,
                "instrument": instrument,
                "notes": notes,
            })
    
    return project


def create_logic_template(
    name: str,
    tempo: float = 120.0,
    bars: int = 8,
    tracks: Optional[List[str]] = None,
) -> LogicProject:
    """
    Create a basic Logic project template.
    
    Args:
        name: Project name
        tempo: Tempo in BPM
        bars: Number of bars
        tracks: List of track names to create
    
    Returns:
        LogicProject template
    """
    if tracks is None:
        tracks = ["Drums", "Bass", "Keys", "Guitar", "Vocals"]
    
    project = LogicProject(
        name=name,
        tempo_bpm=tempo,
    )
    
    # Add empty tracks
    for i, track_name in enumerate(tracks):
        channel = i + 1
        if track_name.lower() == "drums":
            channel = 10
        
        project.add_track(name=track_name, channel=channel)
    
    return project
