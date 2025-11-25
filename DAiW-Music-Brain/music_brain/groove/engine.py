# music_brain/groove/engine.py
"""
V2 Groove Engine - Gaussian jitter + dropout + velocity shaping.

This is the "Drunken Drummer" implementation that sits between
raw note generation and MIDI export.

Usage:
    from music_brain.groove.engine import apply_groove

    humanized = apply_groove(notes, complexity=0.7, vulnerability=0.5)
"""
import random
from typing import List, Dict

# Safety constants (Logic PPQ usually 480-960; we jitter within a small window)
SAFE_DRIFT_LIMIT = 40
VELOCITY_MIN = 20
VELOCITY_MAX = 120


def apply_groove(
    notes: List[Dict],
    complexity: float,
    vulnerability: float
) -> List[Dict]:
    """
    Applies humanization via Gaussian jitter and probability masks.

    Args:
        notes: List of dicts with keys:
            - pitch: int
            - velocity: int
            - start_tick: int
            - duration_ticks: int
        complexity (0.0-1.0): Controls timing looseness and dropped notes (Chaos).
        vulnerability (0.0-1.0): Controls dynamic range (Fragility).

    Returns:
        New list of humanized note dicts.
    """
    processed_events = []

    # 1. Parameters from controls
    # Timing Sigma: 0.0 -> perfect, 1.0 -> very loose
    timing_sigma = complexity * 20

    # Base velocity: vulnerable = quieter, confident = louder
    base_velocity = 90 - (vulnerability * 30)  # 90 down to 60

    # Velocity variance: vulnerable = more erratic
    vel_sigma = 5 + (vulnerability * 15)

    for note in notes:
        # 2. CHAOS: Dropped notes
        # At max complexity (1.0), ~20% chance to drop a note.
        if complexity > 0.8 and random.random() > 0.8:
            continue  # dropout

        # 3. CHAOS: Timing jitter (Gaussian around 0)
        if timing_sigma > 0:
            jitter = int(random.gauss(0, timing_sigma))
            jitter = max(-SAFE_DRIFT_LIMIT, min(SAFE_DRIFT_LIMIT, jitter))
        else:
            jitter = 0

        new_start = max(0, note["start_tick"] + jitter)

        # 4. VULNERABILITY: Velocity humanization
        current_vel = note.get("velocity", base_velocity)
        target_vel = (current_vel + base_velocity) / 2

        new_vel = int(random.gauss(target_vel, vel_sigma))
        new_vel = max(VELOCITY_MIN, min(VELOCITY_MAX, new_vel))

        # Rebuild note
        new_note = note.copy()
        new_note["start_tick"] = new_start
        new_note["velocity"] = new_vel

        processed_events.append(new_note)

    return processed_events
