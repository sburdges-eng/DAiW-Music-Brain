"""
Groove Engine - Humanize MIDI note events with feel and imperfection.

Applies timing drift, velocity variation, and occasional dropouts
to make programmed notes feel more human and emotionally expressive.

Philosophy: Human imperfection is valued. Lo-fi, pitch drift, room noise
are features, not bugs.
"""

import random
from typing import List, Dict, Any, Optional


# =================================================================
# CONSTANTS
# =================================================================

# Maximum timing drift in ticks (at 480 PPQ, this is ~15ms at 120 BPM)
MAX_TICKS_DRIFT = 12

# Human latency bias - even at complexity 0, slight consistent late push
HUMAN_LATENCY_BIAS = 2

# Maximum probability of dropping a note (at max complexity)
MAX_DROPOUT_PROB = 0.2

# Velocity range modifiers
VELOCITY_RANGE_LOW = 0.7   # Multiplier for soft dynamics
VELOCITY_RANGE_HIGH = 1.15  # Multiplier for loud dynamics


# =================================================================
# CORE GROOVE FUNCTION
# =================================================================

def apply_groove(
    events: List[Dict[str, Any]],
    complexity: float = 0.5,
    vulnerability: float = 0.5,
    ppq: int = 480,
    seed: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Apply humanizing groove to a list of note events.

    This function introduces intentional imperfections that make
    programmed music feel more human and emotionally expressive.

    Args:
        events: List of note dicts with keys:
            - start_tick: int
            - velocity: int
            - pitch: int (optional)
            - duration_ticks: int (optional)
        complexity: 0-1 scale controlling timing variation and dropouts
            - 0 = tight, quantized feel
            - 1 = loose, human feel with possible dropouts
        vulnerability: 0-1 scale controlling dynamics
            - 0 = confident, louder
            - 1 = exposed, softer, more dynamic range
        ppq: Pulses per quarter note (for scaling)
        seed: Random seed for reproducibility

    Returns:
        New list of processed note events (original list is not modified)
    """
    if seed is not None:
        random.seed(seed)

    if not events:
        return []

    result = []

    # Scale drift based on PPQ
    ppq_scale = ppq / 480.0
    max_drift = int(MAX_TICKS_DRIFT * ppq_scale * complexity)
    latency_bias = int(HUMAN_LATENCY_BIAS * ppq_scale)

    for event in events:
        # Dropout logic - only at higher complexity
        if complexity > 0:
            dropout_prob = complexity * MAX_DROPOUT_PROB
            if random.random() < dropout_prob:
                continue  # Drop this note

        new_event = event.copy()

        # Timing humanization
        if "start_tick" in new_event:
            if complexity > 0:
                # Random drift within bounds
                drift = random.randint(-max_drift, max_drift)
            else:
                drift = 0

            # Add consistent human latency bias
            new_tick = new_event["start_tick"] + drift + latency_bias

            # Don't go negative
            new_event["start_tick"] = max(0, new_tick)

        # Velocity humanization
        if "velocity" in new_event:
            original_vel = new_event["velocity"]

            # Base velocity adjustment from vulnerability
            if vulnerability > 0.5:
                # Higher vulnerability = softer, more exposed
                vel_factor = 1.0 - ((vulnerability - 0.5) * 0.4)
            else:
                # Lower vulnerability = more confident
                vel_factor = 1.0 + ((0.5 - vulnerability) * 0.2)

            # Add random variation based on complexity
            if complexity > 0:
                vel_range = int(complexity * 15)
                vel_variation = random.randint(-vel_range, vel_range)
            else:
                vel_variation = 0

            new_vel = int(original_vel * vel_factor) + vel_variation

            # Clamp to valid MIDI range
            new_vel = max(1, min(127, new_vel))
            new_event["velocity"] = new_vel

        result.append(new_event)

    return result


def apply_swing(
    events: List[Dict[str, Any]],
    swing_amount: float = 0.3,
    ppq: int = 480,
) -> List[Dict[str, Any]]:
    """
    Apply swing feel to note events.

    Delays every other 8th note to create shuffle/swing feel.

    Args:
        events: List of note dicts with start_tick
        swing_amount: 0-1 where 0=straight, 1=full triplet swing
        ppq: Pulses per quarter note

    Returns:
        New list with swing applied
    """
    if not events:
        return []

    eighth_note = ppq // 2
    swing_delay = int(eighth_note * swing_amount * 0.5)

    result = []
    for event in events:
        new_event = event.copy()

        if "start_tick" in new_event:
            tick = new_event["start_tick"]
            # Check if this is on an upbeat (odd eighth note)
            position_in_beat = tick % ppq
            eighth_position = position_in_beat // eighth_note

            if eighth_position == 1:  # Upbeat
                new_event["start_tick"] = tick + swing_delay

        result.append(new_event)

    return result


def apply_pocket(
    events: List[Dict[str, Any]],
    pocket_depth: float = 0.5,
    ppq: int = 480,
) -> List[Dict[str, Any]]:
    """
    Apply "in the pocket" feel - consistent slight push or pull.

    This creates the characteristic groove where notes sit slightly
    behind or ahead of the beat in a consistent way.

    Args:
        events: List of note dicts
        pocket_depth: -1 to 1 where:
            - negative = rushing/ahead
            - 0 = on the beat
            - positive = laid back/behind
        ppq: Pulses per quarter note

    Returns:
        New list with pocket applied
    """
    if not events:
        return []

    # Max pocket shift is about 1/32 note
    max_shift = ppq // 8
    shift = int(max_shift * pocket_depth)

    result = []
    for event in events:
        new_event = event.copy()

        if "start_tick" in new_event:
            new_tick = new_event["start_tick"] + shift
            new_event["start_tick"] = max(0, new_tick)

        result.append(new_event)

    return result


def humanize_velocities(
    events: List[Dict[str, Any]],
    variation: float = 0.2,
    accent_pattern: Optional[List[float]] = None,
    ppq: int = 480,
) -> List[Dict[str, Any]]:
    """
    Apply human-like velocity variations.

    Args:
        events: List of note dicts with velocity
        variation: 0-1 amount of random variation
        accent_pattern: Optional list of multipliers per beat position
        ppq: Pulses per quarter note

    Returns:
        New list with humanized velocities
    """
    if not events:
        return []

    result = []
    for event in events:
        new_event = event.copy()

        if "velocity" in new_event:
            vel = new_event["velocity"]

            # Apply accent pattern if provided
            if accent_pattern and "start_tick" in new_event:
                beat = (new_event["start_tick"] // ppq) % len(accent_pattern)
                vel = int(vel * accent_pattern[beat])

            # Add random variation
            var_range = int(vel * variation)
            vel += random.randint(-var_range, var_range)

            new_event["velocity"] = max(1, min(127, vel))

        result.append(new_event)

    return result
