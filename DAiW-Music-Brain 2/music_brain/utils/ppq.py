"""
PPQ Utilities - Handle different MIDI timing resolutions.

Different DAWs use different PPQ (Pulses Per Quarter note) values:
- Logic Pro: 480 or 960
- Ableton Live: 96
- Pro Tools: 960
- FL Studio: 96 or 384
- Cubase: 480

This module provides utilities for normalizing and converting
between different PPQ values.
"""

from typing import List, Tuple, Union


# Common DAW PPQ values
DAW_PPQ = {
    "logic_pro": 480,
    "logic_pro_hd": 960,
    "ableton_live": 96,
    "pro_tools": 960,
    "fl_studio": 96,
    "fl_studio_hd": 384,
    "cubase": 480,
    "reaper": 960,
    "standard": 480,  # Most common default
}


def normalize_ppq(
    ticks: Union[int, List[int]],
    source_ppq: int,
    target_ppq: int = 480,
) -> Union[int, List[int]]:
    """
    Normalize tick values from one PPQ to another.
    
    Args:
        ticks: Single tick value or list of tick values
        source_ppq: Source PPQ resolution
        target_ppq: Target PPQ resolution (default: 480)
    
    Returns:
        Normalized tick value(s)
    """
    if source_ppq == target_ppq:
        return ticks
    
    ratio = target_ppq / source_ppq
    
    if isinstance(ticks, list):
        return [int(t * ratio) for t in ticks]
    return int(ticks * ratio)


def scale_ticks(
    ticks: Union[int, List[int]],
    ratio: float,
) -> Union[int, List[int]]:
    """
    Scale tick values by a ratio.
    
    Args:
        ticks: Tick value(s) to scale
        ratio: Scaling ratio
    
    Returns:
        Scaled tick value(s)
    """
    if isinstance(ticks, list):
        return [int(t * ratio) for t in ticks]
    return int(ticks * ratio)


def ticks_to_beats(
    ticks: Union[int, float],
    ppq: int = 480,
) -> float:
    """
    Convert ticks to beats.
    
    Args:
        ticks: Tick value
        ppq: Pulses per quarter note
    
    Returns:
        Beat position
    """
    return ticks / ppq


def beats_to_ticks(
    beats: Union[int, float],
    ppq: int = 480,
) -> int:
    """
    Convert beats to ticks.
    
    Args:
        beats: Beat position
        ppq: Pulses per quarter note
    
    Returns:
        Tick position
    """
    return int(beats * ppq)


def ticks_to_bars(
    ticks: int,
    ppq: int = 480,
    time_signature: Tuple[int, int] = (4, 4),
) -> float:
    """
    Convert ticks to bar position.
    
    Args:
        ticks: Tick value
        ppq: Pulses per quarter note
        time_signature: (numerator, denominator)
    
    Returns:
        Bar position (float)
    """
    beats_per_bar = time_signature[0] * (4 / time_signature[1])
    beats = ticks / ppq
    return beats / beats_per_bar


def bars_to_ticks(
    bars: Union[int, float],
    ppq: int = 480,
    time_signature: Tuple[int, int] = (4, 4),
) -> int:
    """
    Convert bar position to ticks.
    
    Args:
        bars: Bar position
        ppq: Pulses per quarter note
        time_signature: (numerator, denominator)
    
    Returns:
        Tick position
    """
    beats_per_bar = time_signature[0] * (4 / time_signature[1])
    beats = bars * beats_per_bar
    return int(beats * ppq)


def ticks_to_seconds(
    ticks: int,
    ppq: int = 480,
    tempo_bpm: float = 120.0,
) -> float:
    """
    Convert ticks to seconds.
    
    Args:
        ticks: Tick value
        ppq: Pulses per quarter note
        tempo_bpm: Tempo in BPM
    
    Returns:
        Time in seconds
    """
    beats = ticks / ppq
    seconds_per_beat = 60.0 / tempo_bpm
    return beats * seconds_per_beat


def seconds_to_ticks(
    seconds: float,
    ppq: int = 480,
    tempo_bpm: float = 120.0,
) -> int:
    """
    Convert seconds to ticks.
    
    Args:
        seconds: Time in seconds
        ppq: Pulses per quarter note
        tempo_bpm: Tempo in BPM
    
    Returns:
        Tick position
    """
    seconds_per_beat = 60.0 / tempo_bpm
    beats = seconds / seconds_per_beat
    return int(beats * ppq)


def quantize_ticks(
    ticks: int,
    ppq: int = 480,
    resolution: int = 16,
) -> int:
    """
    Quantize tick value to nearest grid position.
    
    Args:
        ticks: Tick value
        ppq: Pulses per quarter note
        resolution: Grid resolution (4=quarter, 8=eighth, 16=sixteenth, etc.)
    
    Returns:
        Quantized tick position
    """
    grid_ticks = ppq * 4 // resolution
    return round(ticks / grid_ticks) * grid_ticks


def get_grid_positions(
    start_tick: int,
    end_tick: int,
    ppq: int = 480,
    resolution: int = 16,
) -> List[int]:
    """
    Get all grid positions between start and end.
    
    Args:
        start_tick: Start position
        end_tick: End position
        ppq: Pulses per quarter note
        resolution: Grid resolution
    
    Returns:
        List of grid tick positions
    """
    grid_ticks = ppq * 4 // resolution
    positions = []
    
    current = quantize_ticks(start_tick, ppq, resolution)
    while current <= end_tick:
        positions.append(current)
        current += grid_ticks
    
    return positions


def calculate_swing_offset(
    position_in_beat: float,
    swing_amount: float = 0.5,
    ppq: int = 480,
) -> int:
    """
    Calculate swing timing offset for a position.
    
    Swing delays the off-beat (2nd) 8th note in each pair.
    
    Args:
        position_in_beat: Position within the beat (0.0-1.0)
        swing_amount: Swing intensity (0.0=none, 0.5=moderate, 1.0=triplet)
        ppq: PPQ for tick calculation
    
    Returns:
        Timing offset in ticks
    """
    # Swing only affects the "e" of "1 e & a" pattern (position 0.25)
    # and the "a" (position 0.75)
    
    eighth_position = position_in_beat * 4  # 0, 1, 2, 3 in 8th notes
    
    # Check if this is an off-beat 8th note
    if abs(eighth_position - 1) < 0.1 or abs(eighth_position - 3) < 0.1:
        # This is an off-beat - apply swing delay
        max_delay = ppq // 6  # Max swing is triplet (1/3 of beat -> 1/6 delay)
        return int(max_delay * swing_amount)
    
    return 0


def get_ppq_for_daw(daw_name: str) -> int:
    """
    Get the default PPQ for a specific DAW.
    
    Args:
        daw_name: DAW name (e.g., "logic_pro", "ableton_live")
    
    Returns:
        PPQ value
    """
    daw_lower = daw_name.lower().replace(" ", "_").replace("-", "_")
    return DAW_PPQ.get(daw_lower, 480)
