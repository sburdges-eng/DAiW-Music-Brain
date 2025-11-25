"""
Groove Extractor - Extract timing and velocity patterns from MIDI files.

Analyzes:
- Timing deviations from grid
- Velocity contours
- Swing factor
- Ghost notes
- Accent patterns
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


@dataclass
class NoteEvent:
    """Single note event with timing and velocity info."""
    pitch: int
    velocity: int
    start_tick: int
    duration_ticks: int
    channel: int = 0
    
    # Computed analysis fields
    deviation_ticks: float = 0.0  # Deviation from quantized grid
    is_ghost: bool = False  # Ghost note (low velocity)
    is_accent: bool = False  # Accent note (high velocity)


@dataclass 
class GrooveTemplate:
    """
    Extracted groove pattern that can be applied to other MIDI files.
    
    Contains timing deviations, velocity curves, and statistical measures
    that define the "feel" of the original performance.
    """
    name: str = "Untitled Groove"
    source_file: str = ""
    ppq: int = 480  # Pulses per quarter note
    tempo_bpm: float = 120.0
    time_signature: Tuple[int, int] = (4, 4)
    
    # Timing analysis
    timing_deviations: List[float] = field(default_factory=list)  # Per-beat deviations in ticks
    swing_factor: float = 0.0  # 0.0 = straight, 0.5 = triplet swing
    
    # Velocity analysis
    velocity_curve: List[int] = field(default_factory=list)  # Per-beat velocities
    velocity_stats: Dict = field(default_factory=dict)
    
    # Timing statistics
    timing_stats: Dict = field(default_factory=dict)
    
    # Note events (optional, for detailed analysis)
    events: List[NoteEvent] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary for JSON export."""
        return {
            "name": self.name,
            "source_file": self.source_file,
            "ppq": self.ppq,
            "tempo_bpm": self.tempo_bpm,
            "time_signature": list(self.time_signature),
            "timing_deviations": self.timing_deviations,
            "swing_factor": self.swing_factor,
            "velocity_curve": self.velocity_curve,
            "velocity_stats": self.velocity_stats,
            "timing_stats": self.timing_stats,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "GrooveTemplate":
        """Deserialize from dictionary."""
        return cls(
            name=data.get("name", "Untitled"),
            source_file=data.get("source_file", ""),
            ppq=data.get("ppq", 480),
            tempo_bpm=data.get("tempo_bpm", 120.0),
            time_signature=tuple(data.get("time_signature", [4, 4])),
            timing_deviations=data.get("timing_deviations", []),
            swing_factor=data.get("swing_factor", 0.0),
            velocity_curve=data.get("velocity_curve", []),
            velocity_stats=data.get("velocity_stats", {}),
            timing_stats=data.get("timing_stats", {}),
        )
    
    def save(self, path: str):
        """Save groove template to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> "GrooveTemplate":
        """Load groove template from JSON file."""
        with open(path, 'r') as f:
            return cls.from_dict(json.load(f))


def extract_groove(
    midi_path: str,
    quantize_resolution: int = 16,  # 16th notes
    ghost_threshold: int = 40,
    accent_threshold: int = 100,
) -> GrooveTemplate:
    """
    Extract groove pattern from a MIDI file.
    
    Args:
        midi_path: Path to MIDI file
        quantize_resolution: Grid resolution for deviation calculation (8=8th, 16=16th)
        ghost_threshold: Velocity below this = ghost note
        accent_threshold: Velocity above this = accent
    
    Returns:
        GrooveTemplate with extracted timing/velocity patterns
    """
    if not MIDO_AVAILABLE:
        raise ImportError("mido package required for MIDI processing. Install with: pip install mido")
    
    midi_path = Path(midi_path)
    if not midi_path.exists():
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")
    
    mid = mido.MidiFile(str(midi_path))
    
    # Extract metadata
    ppq = mid.ticks_per_beat
    tempo_bpm = 120.0  # Default
    time_sig = (4, 4)
    
    # Find tempo and time signature
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo_bpm = mido.tempo2bpm(msg.tempo)
            elif msg.type == 'time_signature':
                time_sig = (msg.numerator, msg.denominator)
    
    # Collect all note events
    events = []
    for track in mid.tracks:
        current_tick = 0
        active_notes = {}  # pitch -> (start_tick, velocity, channel)
        
        for msg in track:
            current_tick += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                active_notes[msg.note] = (current_tick, msg.velocity, msg.channel)
            
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in active_notes:
                    start_tick, velocity, channel = active_notes.pop(msg.note)
                    duration = current_tick - start_tick
                    
                    event = NoteEvent(
                        pitch=msg.note,
                        velocity=velocity,
                        start_tick=start_tick,
                        duration_ticks=duration,
                        channel=channel,
                        is_ghost=(velocity < ghost_threshold),
                        is_accent=(velocity > accent_threshold),
                    )
                    events.append(event)
    
    if not events:
        return GrooveTemplate(
            name=midi_path.stem,
            source_file=str(midi_path),
            ppq=ppq,
            tempo_bpm=tempo_bpm,
            time_signature=time_sig,
        )
    
    # Calculate grid resolution in ticks
    ticks_per_beat = ppq
    ticks_per_grid = ticks_per_beat * 4 // quantize_resolution
    
    # Calculate timing deviations
    timing_deviations = []
    for event in events:
        # Find nearest grid position
        nearest_grid = round(event.start_tick / ticks_per_grid) * ticks_per_grid
        deviation = event.start_tick - nearest_grid
        event.deviation_ticks = deviation
        timing_deviations.append(deviation)
    
    # Calculate swing factor (ratio of long to short 8th notes)
    swing_factor = _calculate_swing(events, ppq)
    
    # Velocity statistics
    velocities = [e.velocity for e in events]
    velocity_stats = {
        "min": min(velocities),
        "max": max(velocities),
        "mean": sum(velocities) / len(velocities),
        "ghost_count": sum(1 for e in events if e.is_ghost),
        "accent_count": sum(1 for e in events if e.is_accent),
    }
    
    # Timing statistics
    timing_ms = [d * (60000 / tempo_bpm / ppq) for d in timing_deviations]
    timing_stats = {
        "mean_deviation_ticks": sum(timing_deviations) / len(timing_deviations),
        "mean_deviation_ms": sum(timing_ms) / len(timing_ms),
        "max_deviation_ticks": max(abs(d) for d in timing_deviations),
        "max_deviation_ms": max(abs(d) for d in timing_ms),
    }
    
    if NUMPY_AVAILABLE:
        timing_stats["std_deviation_ticks"] = float(np.std(timing_deviations))
        timing_stats["std_deviation_ms"] = float(np.std(timing_ms))
        velocity_stats["std"] = float(np.std(velocities))
    
    # Build velocity curve (per beat)
    total_beats = max(e.start_tick for e in events) // ppq + 1
    velocity_curve = []
    for beat in range(total_beats):
        beat_start = beat * ppq
        beat_end = (beat + 1) * ppq
        beat_events = [e for e in events if beat_start <= e.start_tick < beat_end]
        if beat_events:
            avg_vel = sum(e.velocity for e in beat_events) // len(beat_events)
            velocity_curve.append(avg_vel)
        else:
            velocity_curve.append(0)
    
    return GrooveTemplate(
        name=midi_path.stem,
        source_file=str(midi_path),
        ppq=ppq,
        tempo_bpm=tempo_bpm,
        time_signature=time_sig,
        timing_deviations=timing_deviations,
        swing_factor=swing_factor,
        velocity_curve=velocity_curve,
        velocity_stats=velocity_stats,
        timing_stats=timing_stats,
        events=events,
    )


def _calculate_swing(events: List[NoteEvent], ppq: int) -> float:
    """
    Calculate swing factor from note events.
    
    Swing is the ratio of the first 8th note to the second in a pair.
    - 0.5 = straight (even 8ths)
    - 0.67 = triplet swing (2:1 ratio)
    
    Returns value between 0.0 (laid back) and 1.0 (pushed)
    """
    if len(events) < 4:
        return 0.0
    
    # Look at 8th note pairs
    eighth_note_ticks = ppq // 2
    
    # Find events near 8th note boundaries
    on_beat_events = []
    off_beat_events = []
    
    for event in events:
        position_in_beat = event.start_tick % ppq
        
        # On beat (within 10% of beat start)
        if position_in_beat < ppq * 0.1 or position_in_beat > ppq * 0.9:
            on_beat_events.append(event)
        # Off beat (near middle of beat)
        elif abs(position_in_beat - eighth_note_ticks) < ppq * 0.15:
            off_beat_events.append(event)
    
    if not off_beat_events:
        return 0.0
    
    # Calculate average offset of off-beat notes
    offsets = []
    for event in off_beat_events:
        position_in_beat = event.start_tick % ppq
        expected_position = ppq // 2
        offset = (position_in_beat - expected_position) / expected_position
        offsets.append(offset)
    
    avg_offset = sum(offsets) / len(offsets)
    
    # Normalize to 0.0-1.0 range
    # Positive offset = swing (off-beats pushed late)
    swing_factor = max(0.0, min(1.0, avg_offset + 0.5))
    
    return round(swing_factor, 3)


def load_groove(path: str) -> GrooveTemplate:
    """Load a groove template from JSON file."""
    return GrooveTemplate.load(path)
