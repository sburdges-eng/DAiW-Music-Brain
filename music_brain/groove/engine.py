# music_brain/groove/engine.py
"""
Groove Engine V2
================
Applies Gaussian jitter + velocity shaping to make MIDI feel human.
"""

import random
from typing import List, Dict

# Safety Constants (Logic Pro PPQ is usually 960, we run 480 here)
SAFE_DRIFT_LIMIT = 40  # max ticks timing drift
VELOCITY_MIN = 20
VELOCITY_MAX = 120


def apply_groove(
    notes: List[Dict],
    complexity: float,
    vulnerability: float,
) -> List[Dict]:
    """
    Applies 'Humanization' via Gaussian jitter and probability masks.

    Args:
        notes: List of dicts
            {
                'pitch': int,
                'velocity': int,
                'start_tick': int,
                'duration_ticks': int
            }
        complexity (0.0 - 1.0): Controls timing looseness and dropped notes (Chaos).
        vulnerability (0.0 - 1.0): Controls dynamic range and 'shyness' (Fragility).
    """
    complexity = max(0.0, min(1.0, float(complexity)))
    vulnerability = max(0.0, min(1.0, float(vulnerability)))

    processed_events: List[Dict] = []

    # Timing sigma: 0 → rigid, 1 → quite loose
    timing_sigma = complexity * 20.0

    # Base velocity: vulnerable → quieter
    base_velocity = 90.0 - (vulnerability * 30.0)  # 90 → 60

    # Velocity variability: vulnerable → more erratic
    vel_sigma = 5.0 + (vulnerability * 15.0)

    for note in notes:
        # Dropped notes at high chaos
        if complexity > 0.8 and random.random() > 0.8:
            continue

        # Timing jitter
        if timing_sigma > 0:
            jitter = int(random.gauss(0.0, timing_sigma))
            jitter = max(-SAFE_DRIFT_LIMIT, min(SAFE_DRIFT_LIMIT, jitter))
        else:
            jitter = 0
        new_start = max(0, int(note["start_tick"]) + jitter)

        # Velocity humanization
        current_vel = note.get("velocity", base_velocity)
        target_vel = (float(current_vel) + base_velocity) / 2.0
        new_vel = int(random.gauss(target_vel, vel_sigma))
        new_vel = max(VELOCITY_MIN, min(VELOCITY_MAX, new_vel))

        new_note = dict(note)
        new_note["start_tick"] = new_start
        new_note["velocity"] = new_vel
        processed_events.append(new_note)

    return processed_events
