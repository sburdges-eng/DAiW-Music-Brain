"""
Track-Safe MIDI I/O

Critical: Most AI implementations flatten MIDI to single timeline.
This breaks:
- Kontakt multi-output kits
- V-Drums multi-lane recordings
- Orchestral templates with per-section tracks
- Any file with controller curves, pitch bends, meta events

This implementation:
- Preserves per-track event order
- Isolates tempo map (track 0 meta events)
- Maintains controller curves and pitch bends per track
- Properly pairs note-on/note-off
- Rebuilds delta time correctly on save
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable, Any
from collections import defaultdict

try:
    import mido
    HAS_MIDO = True
except ImportError:
    HAS_MIDO = False

from .ppq import STANDARD_PPQ, normalize_ticks, scale_ticks


@dataclass
class MidiNote:
    """A single MIDI note with full context."""
    pitch: int
    velocity: int
    onset_ticks: int          # Absolute time in ticks
    duration_ticks: int
    channel: int
    track_index: int
    # Computed on load
    onset_beats: float = 0.0
    onset_bars: float = 0.0
    grid_position: int = 0    # 0-15 for 16th notes


@dataclass
class MidiEvent:
    """Any MIDI event (note, CC, pitch bend, meta)."""
    abs_time: int             # Absolute time in ticks
    message: Any              # mido Message object
    track_index: int
    is_note: bool = False     # True for note_on/note_off


@dataclass
class TrackData:
    """Data for a single track."""
    index: int
    name: str
    events: List[MidiEvent] = field(default_factory=list)
    notes: List[MidiNote] = field(default_factory=list)
    
    # Track-level metadata
    channel: Optional[int] = None  # Primary channel if consistent
    is_drum: bool = False
    instrument_program: Optional[int] = None


@dataclass
class MidiData:
    """Complete MIDI file data with track separation."""
    ppq: int
    tracks: List[TrackData]
    tempo: int = 500000       # Microseconds per beat (default 120 BPM)
    time_signature: Tuple[int, int] = (4, 4)
    key_signature: Optional[str] = None
    
    # Tempo map for files with tempo changes
    tempo_map: List[Tuple[int, int]] = field(default_factory=list)  # [(tick, tempo), ...]
    
    @property
    def bpm(self) -> float:
        return mido.tempo2bpm(self.tempo) if HAS_MIDO else 60000000 / self.tempo
    
    @property
    def all_notes(self) -> List[MidiNote]:
        """All notes from all tracks, sorted by onset."""
        notes = []
        for track in self.tracks:
            notes.extend(track.notes)
        return sorted(notes, key=lambda n: n.onset_ticks)
    
    @property
    def ticks_per_bar(self) -> int:
        """Ticks per bar based on time signature."""
        num, denom = self.time_signature
        beat_ticks = self.ppq * 4 // denom
        return num * beat_ticks


def load_midi(filepath: str, normalize_ppq: bool = True) -> MidiData:
    """
    Load MIDI file preserving track structure.
    
    Args:
        filepath: Path to MIDI file
        normalize_ppq: If True, normalize to STANDARD_PPQ (480)
    
    Returns:
        MidiData with full track separation
    """
    if not HAS_MIDO:
        raise ImportError("mido required for MIDI loading")
    
    mid = mido.MidiFile(filepath)
    source_ppq = mid.ticks_per_beat
    target_ppq = STANDARD_PPQ if normalize_ppq else source_ppq
    
    tracks = []
    tempo = 500000  # Default 120 BPM
    time_sig = (4, 4)
    key_sig = None
    tempo_map = []
    
    for track_idx, track in enumerate(mid.tracks):
        track_data = TrackData(
            index=track_idx,
            name=track.name or f"Track {track_idx}"
        )
        
        abs_time = 0
        active_notes = {}  # (channel, pitch) -> (onset_time, velocity)
        track_channels = set()
        
        for msg in track:
            # Convert delta to absolute time
            abs_time += msg.time
            
            # Scale time if normalizing PPQ
            scaled_time = normalize_ticks(abs_time, source_ppq, target_ppq) if normalize_ppq else abs_time
            
            # Handle meta messages
            if msg.is_meta:
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                    tempo_map.append((scaled_time, msg.tempo))
                elif msg.type == 'time_signature':
                    time_sig = (msg.numerator, msg.denominator)
                elif msg.type == 'key_signature':
                    key_sig = msg.key
                elif msg.type == 'track_name':
                    track_data.name = msg.name
            
            # Store all events (for reconstruction)
            event = MidiEvent(
                abs_time=scaled_time,
                message=msg,
                track_index=track_idx,
                is_note=msg.type in ('note_on', 'note_off')
            )
            track_data.events.append(event)
            
            # Track note on/off for duration calculation
            if msg.type == 'note_on' and msg.velocity > 0:
                key = (msg.channel, msg.note)
                active_notes[key] = (scaled_time, msg.velocity)
                track_channels.add(msg.channel)
                
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                key = (msg.channel, msg.note)
                if key in active_notes:
                    onset_time, velocity = active_notes.pop(key)
                    duration = scaled_time - onset_time
                    
                    # Calculate beat/bar position
                    beats_per_bar = time_sig[0]
                    ticks_per_bar = target_ppq * beats_per_bar * 4 // time_sig[1]
                    onset_beats = onset_time / target_ppq
                    onset_bars = onset_time / ticks_per_bar
                    grid_pos = (onset_time % ticks_per_bar) // (ticks_per_bar // 16)
                    
                    note = MidiNote(
                        pitch=msg.note,
                        velocity=velocity,
                        onset_ticks=onset_time,
                        duration_ticks=max(1, duration),
                        channel=msg.channel,
                        track_index=track_idx,
                        onset_beats=onset_beats,
                        onset_bars=onset_bars,
                        grid_position=int(grid_pos) % 16
                    )
                    track_data.notes.append(note)
        
        # Handle any notes left on (no note_off received)
        for (channel, pitch), (onset_time, velocity) in active_notes.items():
            ticks_per_bar = target_ppq * time_sig[0] * 4 // time_sig[1]
            note = MidiNote(
                pitch=pitch,
                velocity=velocity,
                onset_ticks=onset_time,
                duration_ticks=target_ppq,  # Default quarter note duration
                channel=channel,
                track_index=track_idx,
                onset_beats=onset_time / target_ppq,
                onset_bars=onset_time / ticks_per_bar,
                grid_position=int((onset_time % ticks_per_bar) // (ticks_per_bar // 16)) % 16
            )
            track_data.notes.append(note)
        
        # Determine track channel and drum status
        if track_channels:
            track_data.channel = min(track_channels)  # Primary channel
            track_data.is_drum = (9 in track_channels)  # Channel 10 (0-indexed as 9)
        
        tracks.append(track_data)
    
    return MidiData(
        ppq=target_ppq,
        tracks=tracks,
        tempo=tempo,
        time_signature=time_sig,
        key_signature=key_sig,
        tempo_map=tempo_map if tempo_map else [(0, tempo)]
    )


def save_midi(data: MidiData, filepath: str, target_ppq: Optional[int] = None) -> None:
    """
    Save MidiData to file preserving track structure.
    
    Args:
        data: MidiData to save
        filepath: Output path
        target_ppq: Target PPQ (None = use data.ppq)
    """
    if not HAS_MIDO:
        raise ImportError("mido required for MIDI saving")
    
    target_ppq = target_ppq or data.ppq
    source_ppq = data.ppq
    
    mid = mido.MidiFile(ticks_per_beat=target_ppq)
    
    for track_data in data.tracks:
        track = mido.MidiTrack()
        mid.tracks.append(track)
        
        # Collect all events, scaling time if needed
        events = []
        for event in track_data.events:
            scaled_time = scale_ticks(event.abs_time, source_ppq, target_ppq)
            events.append((scaled_time, event.message))
        
        # Sort by absolute time
        events.sort(key=lambda x: x[0])
        
        # Convert back to delta time
        prev_time = 0
        for abs_time, msg in events:
            delta = abs_time - prev_time
            
            # Clone message with new time
            if msg.is_meta:
                new_msg = msg.copy(time=delta)
            else:
                new_msg = msg.copy(time=delta)
            
            track.append(new_msg)
            prev_time = abs_time
    
    mid.save(filepath)


def modify_notes_safe(
    data: MidiData,
    modifier_fn: Callable[[MidiNote], MidiNote]
) -> MidiData:
    """
    Safely modify notes while preserving all non-note events.
    
    CRITICAL: This maintains track structure, controller curves,
    pitch bends, and meta events exactly as they were.
    
    Args:
        data: Source MidiData
        modifier_fn: Function that takes MidiNote and returns modified MidiNote
    
    Returns:
        New MidiData with modified notes
    """
    new_tracks = []
    
    for track in data.tracks:
        new_track = TrackData(
            index=track.index,
            name=track.name,
            channel=track.channel,
            is_drum=track.is_drum,
            instrument_program=track.instrument_program
        )
        
        # Build map of note events by their original time
        # Key: (abs_time, channel, pitch, 'on'|'off')
        note_on_map = {}  # (channel, pitch) -> (abs_time, velocity)
        note_events = {}  # original_abs_time -> new_abs_time for note events
        
        # First pass: collect note modifications
        original_notes = {
            (n.onset_ticks, n.channel, n.pitch): n
            for n in track.notes
        }
        
        modified_notes = []
        for note in track.notes:
            new_note = modifier_fn(note)
            modified_notes.append(new_note)
            
            # Map original note_on time to new time
            key = (note.onset_ticks, note.channel, note.pitch, 'on')
            note_events[key] = new_note.onset_ticks
            
            # Map original note_off time to new time
            original_off = note.onset_ticks + note.duration_ticks
            new_off = new_note.onset_ticks + new_note.duration_ticks
            key_off = (original_off, note.channel, note.pitch, 'off')
            note_events[key_off] = new_off
        
        new_track.notes = modified_notes
        
        # Second pass: rebuild events list
        for event in track.events:
            if event.is_note:
                msg = event.message
                if msg.type == 'note_on' and msg.velocity > 0:
                    key = (event.abs_time, msg.channel, msg.note, 'on')
                    if key in note_events:
                        new_time = note_events[key]
                        # Find the modified note for new velocity
                        for mn in modified_notes:
                            if mn.channel == msg.channel and mn.pitch == msg.note:
                                if abs(mn.onset_ticks - new_time) < 10:
                                    new_event = MidiEvent(
                                        abs_time=new_time,
                                        message=msg.copy(velocity=mn.velocity),
                                        track_index=event.track_index,
                                        is_note=True
                                    )
                                    new_track.events.append(new_event)
                                    break
                        else:
                            # Fallback: just update time
                            new_event = MidiEvent(
                                abs_time=new_time,
                                message=msg,
                                track_index=event.track_index,
                                is_note=True
                            )
                            new_track.events.append(new_event)
                    else:
                        new_track.events.append(event)
                        
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    key = (event.abs_time, msg.channel, msg.note, 'off')
                    if key in note_events:
                        new_time = note_events[key]
                        new_event = MidiEvent(
                            abs_time=new_time,
                            message=msg,
                            track_index=event.track_index,
                            is_note=True
                        )
                        new_track.events.append(new_event)
                    else:
                        new_track.events.append(event)
                else:
                    new_track.events.append(event)
            else:
                # Non-note events: preserve exactly
                new_track.events.append(event)
        
        # Sort events by time
        new_track.events.sort(key=lambda e: e.abs_time)
        
        new_tracks.append(new_track)
    
    return MidiData(
        ppq=data.ppq,
        tracks=new_tracks,
        tempo=data.tempo,
        time_signature=data.time_signature,
        key_signature=data.key_signature,
        tempo_map=data.tempo_map
    )


def get_notes_by_instrument(data: MidiData, instrument_type: str) -> List[MidiNote]:
    """
    Filter notes by instrument classification.
    """
    from .instruments import classify_note, get_drum_category, is_drum_channel
    
    result = []
    for note in data.all_notes:
        if is_drum_channel(note.channel):
            inst = get_drum_category(note.pitch)
        else:
            inst = classify_note(note.channel, note.pitch)
        
        if inst == instrument_type:
            result.append(note)
    
    return result


def get_notes_by_track(data: MidiData, track_index: int) -> List[MidiNote]:
    """Get all notes from a specific track."""
    if 0 <= track_index < len(data.tracks):
        return data.tracks[track_index].notes
    return []


def get_tempo_at_tick(data: MidiData, tick: int) -> int:
    """Get tempo at a specific tick position."""
    if not data.tempo_map:
        return data.tempo
    
    current_tempo = data.tempo_map[0][1]
    for map_tick, map_tempo in data.tempo_map:
        if map_tick <= tick:
            current_tempo = map_tempo
        else:
            break
    
    return current_tempo


def flatten_to_single_track(data: MidiData) -> MidiData:
    """
    Intentionally flatten to single track.
    
    WARNING: Only use this when you explicitly want to merge tracks.
    This loses track separation and should be avoided for complex MIDI.
    """
    all_events = []
    all_notes = []
    
    for track in data.tracks:
        all_events.extend(track.events)
        all_notes.extend(track.notes)
    
    # Sort by time
    all_events.sort(key=lambda e: e.abs_time)
    all_notes.sort(key=lambda n: n.onset_ticks)
    
    # Update track indices
    for event in all_events:
        event.track_index = 0
    for note in all_notes:
        note.track_index = 0
    
    merged_track = TrackData(
        index=0,
        name="Merged",
        events=all_events,
        notes=all_notes
    )
    
    return MidiData(
        ppq=data.ppq,
        tracks=[merged_track],
        tempo=data.tempo,
        time_signature=data.time_signature,
        key_signature=data.key_signature,
        tempo_map=data.tempo_map
    )
