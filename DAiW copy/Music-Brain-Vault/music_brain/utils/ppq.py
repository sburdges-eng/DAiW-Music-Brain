"""
PPQ (Pulses Per Quarter Note) Handling

Critical: MIDI timing is PPQ-dependent. Templates extracted at one PPQ
must be scaled when applied to files with different PPQ.

Common PPQ values:
- 480: Most DAWs default, Mido tutorials
- 960: Pro Tools, high-resolution DAWs
- 120: Old hardware, some drum machines
- 96: Legacy MIDI files
- 9600: Logic Pro internal resolution
- 480-1920: MPC, Maschine exports vary

Silent failure mode: Applying 480 PPQ offsets to 960 PPQ file
doubles all timing shifts. This breaks groove completely.
"""

from typing import Dict, Any, Union, List, Tuple

# Industry standard - we normalize TO this for storage
STANDARD_PPQ = 480

# Known PPQ values by source
KNOWN_PPQ = {
    'logic_pro': 960,
    'logic_internal': 9600,
    'pro_tools': 960,
    'ableton': 96,
    'fl_studio': 96,
    'cubase': 480,
    'reaper': 960,
    'mpc': 480,
    'maschine': 480,
    'garageband': 480,
    'mido_default': 480,
}


def normalize_ticks(ticks: int, source_ppq: int, target_ppq: int = STANDARD_PPQ) -> int:
    """
    Convert ticks from source PPQ to target PPQ.
    
    Example:
        # 960 PPQ file has note at tick 1920 (2 beats)
        # Convert to 480 PPQ: 1920 * 480/960 = 960 ticks (still 2 beats)
        normalize_ticks(1920, 960, 480) -> 960
    """
    if source_ppq == target_ppq:
        return ticks
    return int(round(ticks * target_ppq / source_ppq))


def scale_ticks(ticks: int, source_ppq: int, target_ppq: int) -> int:
    """Scale ticks between any two PPQ values."""
    return normalize_ticks(ticks, source_ppq, target_ppq)


def ticks_per_bar(ppq: int, time_sig_num: int = 4, time_sig_denom: int = 4) -> int:
    """
    Calculate ticks per bar for given PPQ and time signature.
    
    4/4 at 480 PPQ: 4 * 480 * (4/4) = 1920 ticks/bar
    6/8 at 480 PPQ: 6 * 480 * (4/8) = 1440 ticks/bar
    """
    beat_ticks = ppq * 4 // time_sig_denom
    return time_sig_num * beat_ticks


def ticks_to_beats(ticks: int, ppq: int) -> float:
    """Convert ticks to beat count."""
    return ticks / ppq


def beats_to_ticks(beats: float, ppq: int) -> int:
    """Convert beats to ticks."""
    return int(round(beats * ppq))


def ticks_to_bars(ticks: int, ppq: int, beats_per_bar: int = 4) -> float:
    """Convert ticks to bar position (0-indexed)."""
    ticks_bar = ppq * beats_per_bar
    return ticks / ticks_bar


def grid_position(ticks: int, ppq: int, subdivisions: int = 16) -> int:
    """
    Get position within bar as grid index (0 to subdivisions-1).
    """
    ticks_per_bar_val = ppq * 4  # Assuming 4/4
    position_in_bar = ticks % ticks_per_bar_val
    grid_size = ticks_per_bar_val // subdivisions
    return int(position_in_bar // grid_size) % subdivisions


def grid_position_in_beat(ticks: int, ppq: int, subdivisions: int = 4) -> int:
    """Get position within beat as grid index (0 to subdivisions-1)."""
    position_in_beat = ticks % ppq
    grid_size = ppq // subdivisions
    return int(position_in_beat // grid_size) % subdivisions


def quantize_to_grid(ticks: int, ppq: int, grid_size: int = 16) -> Tuple[int, int]:
    """
    Quantize tick position to grid.
    
    Returns:
        (quantized_ticks, offset_from_grid)
        Positive offset = behind grid, Negative = ahead
    """
    ticks_per_bar_val = ppq * 4
    grid_ticks = ticks_per_bar_val // grid_size
    grid_index = round(ticks / grid_ticks)
    quantized = grid_index * grid_ticks
    offset = ticks - quantized
    return quantized, offset


def scale_template(template: Dict[str, Any], source_ppq: int, target_ppq: int) -> Dict[str, Any]:
    """
    Scale all tick-based values in a groove template.
    
    CRITICAL: Must be called when applying templates to files
    with different PPQ than extraction source.
    """
    if source_ppq == target_ppq:
        return template.copy()
    
    scale = target_ppq / source_ppq
    scaled = {}
    
    for key, value in template.items():
        if key == 'ppq':
            scaled['ppq'] = target_ppq
        elif key == 'push_pull':
            # Scale timing offsets per instrument per position
            scaled['push_pull'] = {}
            for inst, positions in value.items():
                if isinstance(positions, dict):
                    scaled['push_pull'][inst] = {
                        pos: int(round(offset * scale))
                        for pos, offset in positions.items()
                    }
                else:
                    # Single offset per instrument
                    scaled['push_pull'][inst] = int(round(positions * scale))
        elif key == 'stagger':
            scaled['stagger'] = {
                pair: int(round(offset * scale))
                for pair, offset in value.items()
            }
        elif key == 'swing_offsets':
            scaled['swing_offsets'] = {
                pos: int(round(offset * scale))
                for pos, offset in value.items()
            }
        elif key == 'ghost_timing':
            if isinstance(value, dict):
                scaled['ghost_timing'] = {
                    k: int(round(v * scale)) if isinstance(v, (int, float)) else v
                    for k, v in value.items()
                }
            else:
                scaled[key] = value
        elif key in ('timing_map', 'velocity_map', 'histogram', 'swing', 
                     'swing_consistency', 'ghost_ratio', 'per_instrument_swing'):
            # Normalized values, no scaling needed
            scaled[key] = value
        else:
            scaled[key] = value
    
    return scaled


def scale_pocket_rules(pocket: Dict[str, Any], source_ppq: int, target_ppq: int) -> Dict[str, Any]:
    """
    Scale genre pocket rules to target PPQ.
    Pocket rules are defined at STANDARD_PPQ (480).
    """
    if source_ppq == target_ppq:
        return pocket.copy()
    
    scale = target_ppq / source_ppq
    scaled = {}
    
    for key, value in pocket.items():
        if key == 'push_pull':
            scaled['push_pull'] = {
                inst: int(round(offset * scale))
                for inst, offset in value.items()
            }
        elif key == 'stagger':
            scaled['stagger'] = {
                pair: int(round(offset * scale))
                for pair, offset in value.items()
            }
        else:
            scaled[key] = value
    
    return scaled


def ms_to_ticks(ms: float, ppq: int, bpm: float) -> int:
    """Convert milliseconds to ticks."""
    ticks_per_ms = ppq * bpm / 60000
    return int(round(ms * ticks_per_ms))


def ticks_to_ms(ticks: int, ppq: int, bpm: float) -> float:
    """Convert ticks to milliseconds."""
    ms_per_tick = 60000 / (ppq * bpm)
    return ticks * ms_per_tick
