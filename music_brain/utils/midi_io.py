"""
MIDI I/O Utilities - Load, save, and inspect MIDI files.
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False


@dataclass
class MidiInfo:
    """Basic info about a MIDI file."""
    filename: str
    format_type: int  # 0, 1, or 2
    num_tracks: int
    ppq: int  # Ticks per quarter note
    tempo_bpm: float
    time_signature: Tuple[int, int]
    duration_ticks: int
    duration_seconds: float
    note_count: int
    track_names: List[str]


def load_midi(path: str) -> "mido.MidiFile":
    """
    Load a MIDI file.
    
    Args:
        path: Path to MIDI file
    
    Returns:
        mido.MidiFile object
    """
    if not MIDO_AVAILABLE:
        raise ImportError("mido package required. Install with: pip install mido")
    
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"MIDI file not found: {path}")
    
    return mido.MidiFile(str(path))


def save_midi(midi_file: "mido.MidiFile", path: str):
    """
    Save a MIDI file.
    
    Args:
        midi_file: mido.MidiFile object
        path: Output path
    """
    if not MIDO_AVAILABLE:
        raise ImportError("mido package required")
    
    midi_file.save(str(path))


def get_midi_info(path: str) -> MidiInfo:
    """
    Get basic information about a MIDI file.
    
    Args:
        path: Path to MIDI file
    
    Returns:
        MidiInfo with file statistics
    """
    if not MIDO_AVAILABLE:
        raise ImportError("mido package required")
    
    path = Path(path)
    mid = mido.MidiFile(str(path))
    
    # Extract metadata
    ppq = mid.ticks_per_beat
    tempo_bpm = 120.0  # Default
    time_sig = (4, 4)
    track_names = []
    
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo_bpm = mido.tempo2bpm(msg.tempo)
            elif msg.type == 'time_signature':
                time_sig = (msg.numerator, msg.denominator)
            elif msg.type == 'track_name':
                track_names.append(msg.name)
    
    # Calculate duration and note count
    total_ticks = 0
    note_count = 0
    
    for track in mid.tracks:
        track_ticks = 0
        for msg in track:
            track_ticks += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                note_count += 1
        total_ticks = max(total_ticks, track_ticks)
    
    # Convert ticks to seconds
    seconds_per_tick = 60.0 / (tempo_bpm * ppq)
    duration_seconds = total_ticks * seconds_per_tick
    
    return MidiInfo(
        filename=str(path),
        format_type=mid.type,
        num_tracks=len(mid.tracks),
        ppq=ppq,
        tempo_bpm=tempo_bpm,
        time_signature=time_sig,
        duration_ticks=total_ticks,
        duration_seconds=duration_seconds,
        note_count=note_count,
        track_names=track_names,
    )


def merge_tracks(midi_file: "mido.MidiFile") -> "mido.MidiTrack":
    """
    Merge all tracks into a single track.
    
    Args:
        midi_file: MIDI file with multiple tracks
    
    Returns:
        Single merged track
    """
    if not MIDO_AVAILABLE:
        raise ImportError("mido package required")
    
    merged = mido.merge_tracks(midi_file.tracks)
    return merged


def split_by_channel(midi_file: "mido.MidiFile") -> Dict[int, List]:
    """
    Split MIDI file by channel.
    
    Args:
        midi_file: MIDI file
    
    Returns:
        Dict mapping channel number to list of messages
    """
    channels = {}
    
    for track in midi_file.tracks:
        current_tick = 0
        for msg in track:
            current_tick += msg.time
            if hasattr(msg, 'channel'):
                if msg.channel not in channels:
                    channels[msg.channel] = []
                channels[msg.channel].append((current_tick, msg))
    
    return channels


def extract_notes(midi_file: "mido.MidiFile") -> List[Dict]:
    """
    Extract all notes from MIDI file as list of dicts.
    
    Returns:
        List of note dicts with pitch, velocity, start, duration, channel
    """
    notes = []
    
    for track_idx, track in enumerate(midi_file.tracks):
        current_tick = 0
        active_notes = {}  # (channel, pitch) -> (start_tick, velocity)
        
        for msg in track:
            current_tick += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                key = (msg.channel, msg.note)
                active_notes[key] = (current_tick, msg.velocity)
            
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                key = (msg.channel, msg.note)
                if key in active_notes:
                    start_tick, velocity = active_notes.pop(key)
                    notes.append({
                        'pitch': msg.note,
                        'velocity': velocity,
                        'start_tick': start_tick,
                        'duration_ticks': current_tick - start_tick,
                        'channel': msg.channel,
                        'track': track_idx,
                    })
    
    # Sort by start time
    notes.sort(key=lambda n: n['start_tick'])
    return notes
