"""
Groove Applicator - Apply extracted grooves to MIDI files.

Takes a groove template (extracted or preset) and applies its
timing/velocity characteristics to a target MIDI file.
"""

from pathlib import Path
from typing import Optional, Union
import copy

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False

from music_brain.groove.extractor import GrooveTemplate
from music_brain.groove.templates import get_genre_template


def apply_groove(
    midi_path: str,
    groove: Optional[GrooveTemplate] = None,
    genre: Optional[str] = None,
    output: Optional[str] = None,
    intensity: float = 0.5,
    preserve_dynamics: bool = True,
    humanize_timing: bool = True,
    humanize_velocity: bool = True,
) -> str:
    """
    Apply groove template to a MIDI file.
    
    Args:
        midi_path: Path to input MIDI file
        groove: GrooveTemplate to apply (optional if genre specified)
        genre: Genre template name ('funk', 'jazz', 'rock', etc.)
        output: Output path (default: input_grooved.mid)
        intensity: How strongly to apply groove (0.0-1.0)
        preserve_dynamics: Keep original velocity range while applying groove shape
        humanize_timing: Apply timing deviations
        humanize_velocity: Apply velocity variations
    
    Returns:
        Path to output file
    """
    if not MIDO_AVAILABLE:
        raise ImportError("mido package required. Install with: pip install mido")
    
    # Get groove template
    if groove is None:
        if genre is None:
            raise ValueError("Must provide either groove template or genre name")
        groove = get_genre_template(genre)
    
    # Load input MIDI
    midi_path = Path(midi_path)
    if not midi_path.exists():
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")
    
    mid = mido.MidiFile(str(midi_path))
    
    # Create output MIDI
    output_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
    
    # Scale groove to match target PPQ
    ppq_ratio = mid.ticks_per_beat / groove.ppq
    
    for track in mid.tracks:
        new_track = mido.MidiTrack()
        output_mid.tracks.append(new_track)
        
        current_tick = 0
        note_index = 0
        
        for msg in track:
            new_msg = msg.copy()
            
            if msg.type in ['note_on', 'note_off']:
                current_tick += msg.time
                
                if humanize_timing and groove.timing_deviations:
                    # Get deviation for this note position
                    dev_index = note_index % len(groove.timing_deviations)
                    deviation = groove.timing_deviations[dev_index] * ppq_ratio
                    
                    # Apply with intensity
                    time_adjustment = int(deviation * intensity)
                    
                    # Adjust message time
                    new_time = max(0, msg.time + time_adjustment)
                    new_msg = msg.copy(time=new_time)
                
                if humanize_velocity and msg.type == 'note_on' and msg.velocity > 0:
                    # Get velocity curve value
                    if groove.velocity_curve:
                        beat = current_tick // mid.ticks_per_beat
                        vel_index = beat % len(groove.velocity_curve)
                        target_vel = groove.velocity_curve[vel_index]
                        
                        if preserve_dynamics:
                            # Blend original velocity with groove velocity
                            new_vel = int(msg.velocity * (1 - intensity) + target_vel * intensity)
                        else:
                            new_vel = target_vel
                        
                        new_vel = max(1, min(127, new_vel))
                        new_msg = new_msg.copy(velocity=new_vel)
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    note_index += 1
            
            new_track.append(new_msg)
    
    # Determine output path
    if output is None:
        output = str(midi_path.stem) + "_grooved.mid"
    
    output_path = Path(output)
    output_mid.save(str(output_path))
    
    return str(output_path)


def humanize(
    midi_path: str,
    output: Optional[str] = None,
    timing_range_ms: float = 10.0,
    velocity_range: int = 15,
    seed: Optional[int] = None,
) -> str:
    """
    Add random human-like variations to a MIDI file.
    
    Unlike apply_groove, this adds random variations rather than
    applying a specific groove pattern.
    
    Args:
        midi_path: Input MIDI file
        output: Output path
        timing_range_ms: Max timing deviation in milliseconds
        velocity_range: Max velocity deviation (+/-)
        seed: Random seed for reproducibility
    
    Returns:
        Path to output file
    """
    if not MIDO_AVAILABLE:
        raise ImportError("mido package required. Install with: pip install mido")
    
    import random
    if seed is not None:
        random.seed(seed)
    
    midi_path = Path(midi_path)
    mid = mido.MidiFile(str(midi_path))
    output_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
    
    # Calculate timing range in ticks (assume 120 BPM default)
    tempo_bpm = 120.0
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo_bpm = mido.tempo2bpm(msg.tempo)
                break
    
    ticks_per_ms = mid.ticks_per_beat * tempo_bpm / 60000
    timing_range_ticks = int(timing_range_ms * ticks_per_ms)
    
    for track in mid.tracks:
        new_track = mido.MidiTrack()
        output_mid.tracks.append(new_track)
        
        accumulated_offset = 0
        
        for msg in track:
            new_msg = msg.copy()
            
            if msg.type in ['note_on', 'note_off']:
                # Random timing deviation
                timing_offset = random.randint(-timing_range_ticks, timing_range_ticks)
                
                # Apply timing change
                new_time = max(0, msg.time + timing_offset - accumulated_offset)
                accumulated_offset = timing_offset
                new_msg = new_msg.copy(time=new_time)
                
                # Random velocity deviation for note_on
                if msg.type == 'note_on' and msg.velocity > 0:
                    vel_offset = random.randint(-velocity_range, velocity_range)
                    new_vel = max(1, min(127, msg.velocity + vel_offset))
                    new_msg = new_msg.copy(velocity=new_vel)
            
            new_track.append(new_msg)
    
    if output is None:
        output = str(midi_path.stem) + "_humanized.mid"
    
    output_path = Path(output)
    output_mid.save(str(output_path))
    
    return str(output_path)
