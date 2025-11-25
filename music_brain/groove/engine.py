# music_brain/groove/engine.py
"""
Groove Engine - The "Drunken Drummer"

Applies humanization via Gaussian jitter and probability masks.
This is the core groove logic that makes MIDI feel more human.
"""
import random
from typing import List, Dict

# Logic Pro standard PPQ is 960
SAFE_DRIFT_LIMIT = 40
VELOCITY_MIN = 20
VELOCITY_MAX = 120


def apply_groove(notes: List[Dict], complexity: float, vulnerability: float) -> List[Dict]:
    """
    Applies 'Humanization' via Gaussian jitter and probability masks.

    Args:
        notes: List of note dicts with 'start_tick', 'velocity', etc.
        complexity: 0.0-1.0 - timing chaos (higher = more off-grid)
        vulnerability: 0.0-1.0 - dynamic fragility (higher = softer, more erratic)

    Returns:
        List of processed note events
    """
    processed_events = []

    # 1. Calculate Parameters
    # Timing Sigma: 0.0 -> 0 (perfect), 1.0 -> 20 (very loose)
    timing_sigma = complexity * 20

    # Velocity Base: Vulnerable = quiet; Confident = loud
    base_velocity = 90 - (vulnerability * 30)

    # Velocity Variance: Vulnerable = erratic; Confident = consistent
    vel_sigma = 5 + (vulnerability * 15)

    for note in notes:
        # 2. CHAOS: Dropped Notes (Probability)
        if complexity > 0.8 and random.random() > 0.8:
            continue  # Skip this note (Dropout)

        # 3. CHAOS: Timing Jitter (Gaussian)
        if timing_sigma > 0:
            jitter = int(random.gauss(0, timing_sigma))
            jitter = max(-SAFE_DRIFT_LIMIT, min(SAFE_DRIFT_LIMIT, jitter))
        else:
            jitter = 0

        new_start = max(0, note['start_tick'] + jitter)

        # 4. VULNERABILITY: Velocity Humanization
        current_vel = note.get('velocity', base_velocity)
        target_vel = (current_vel + base_velocity) / 2

        new_vel = int(random.gauss(target_vel, vel_sigma))
        new_vel = max(VELOCITY_MIN, min(VELOCITY_MAX, new_vel))

        # Reconstruct note
        new_note = note.copy()
        new_note['start_tick'] = int(new_start)
        new_note['velocity'] = int(new_vel)
        processed_events.append(new_note)

    return processed_events
