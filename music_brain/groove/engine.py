# music_brain/groove/engine.py
import random
from typing import List, Dict

# Safety Constants (Logic Pro PPQ is usually 960; we use 480 baseline)
SAFE_DRIFT_LIMIT = 40
VELOCITY_MIN = 20
VELOCITY_MAX = 120


def apply_groove(notes: List[Dict], complexity: float, vulnerability: float) -> List[Dict]:
    """
    Applies 'Humanization' via Gaussian jitter and probability masks.

    Args:
        notes: List of dicts
            {
                "pitch": int,
                "velocity": int,
                "start_tick": int,
                "duration_ticks": int
            }
        complexity (0.0 - 1.0): Controls timing looseness and dropped notes (Chaos).
        vulnerability (0.0 - 1.0): Controls dynamic range (Fragility).
    """
    processed_events: List[Dict] = []

    # Timing Sigma: How 'drunk' is the drummer?
    timing_sigma = max(0.0, min(1.0, complexity)) * 20.0

    # Velocity Base: Vulnerable = quiet/shy; Confident = loud
    base_velocity = 90.0 - (max(0.0, min(1.0, vulnerability)) * 30.0)

    # Velocity Variance: Vulnerable = erratic; Confident = consistent
    vel_sigma = 5.0 + (vulnerability * 15.0)

    for note in notes:
        # 1. CHAOS: Dropped Notes (Probability)
        if complexity > 0.8 and random.random() > 0.8:
            # Drop ~20% of notes at max chaos
            continue

        # 2. Timing Jitter (Gaussian)
        if timing_sigma > 0:
            jitter = int(random.gauss(0, timing_sigma))
            jitter = max(-SAFE_DRIFT_LIMIT, min(SAFE_DRIFT_LIMIT, jitter))
        else:
            jitter = 0

        new_start = max(0, int(note.get("start_tick", 0)) + jitter)

        # 3. Velocity Humanization
        current_vel = note.get("velocity", int(base_velocity))
        target_vel = (current_vel + base_velocity) / 2.0

        new_vel = int(random.gauss(target_vel, vel_sigma))
        new_vel = max(VELOCITY_MIN, min(VELOCITY_MAX, new_vel))

        new_note = dict(note)
        new_note["start_tick"] = new_start
        new_note["velocity"] = new_vel
        processed_events.append(new_note)

    return processed_events
