"""
Groove Engine V2
================
Applies Gaussian jitter + velocity shaping to make MIDI feel human.

Now supports:
- Per-note 'complexity' overrides (for tension curves / sections)
- Optional RNG seed for reproducible renders
- 'accent' flag for notes that should lean louder
"""

from __future__ import annotations

import random
from typing import List, Dict, Optional

SAFE_DRIFT_LIMIT = 40  # max ticks timing drift
VELOCITY_MIN = 20
VELOCITY_MAX = 120


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def apply_groove(
    notes: List[Dict],
    complexity: float,
    vulnerability: float,
    seed: Optional[int] = None,
) -> List[Dict]:
    """
    Applies 'Humanization' via Gaussian jitter and probability masks.

    Args:
        notes: List of dicts:
            {
                'pitch': int,
                'velocity': int,
                'start_tick': int,
                'duration_ticks': int,
                # optional: 'complexity': float, 'accent': bool, 'bar_index': int
            }
        complexity (0.0 - 1.0): Base chaos level (timing & dropout).
        vulnerability (0.0 - 1.0): Dynamic sensitivity / "shyness".
        seed: If provided, deterministic randomization for testing / reproducibility.
    """
    base_complexity = _clamp(float(complexity), 0.0, 1.0)
    vulnerability = _clamp(float(vulnerability), 0.0, 1.0)

    rng = random.Random(seed) if seed is not None else random

    processed_events: List[Dict] = []

    # Base velocity anchor: vulnerable → quieter
    base_velocity = 90.0 - (vulnerability * 30.0)  # 90 → 60

    # Base velocity variability: vulnerable → more erratic
    base_vel_sigma = 5.0 + (vulnerability * 15.0)

    for note in notes:
        # Per-note complexity override (hook from tension curve)
        local_complexity = note.get("complexity", base_complexity)
        local_complexity = _clamp(float(local_complexity), 0.0, 1.0)

        # Jitter sigma scaled by local complexity
        timing_sigma = local_complexity * 20.0

        # Dropout probability max 20% at full chaos
        dropout_prob = 0.2 * local_complexity

        # 1. Possible dropout
        if local_complexity > 0.0 and rng.random() < dropout_prob:
            continue

        # 2. Timing jitter
        if timing_sigma > 0:
            jitter = int(rng.gauss(0.0, timing_sigma))
            jitter = max(-SAFE_DRIFT_LIMIT, min(SAFE_DRIFT_LIMIT, jitter))
        else:
            jitter = 0

        new_start = max(0, int(note["start_tick"]) + jitter)

        # 3. Velocity humanization
        current_vel = note.get("velocity", base_velocity)
        target_vel = (float(current_vel) + base_velocity) / 2.0

        # Accents: push target a bit higher
        if note.get("accent"):
            target_vel += 10.0

        vel_sigma = base_vel_sigma
        new_vel = int(rng.gauss(target_vel, vel_sigma))
        new_vel = int(_clamp(new_vel, VELOCITY_MIN, VELOCITY_MAX))

        new_note = dict(note)
        new_note["start_tick"] = new_start
        new_note["velocity"] = new_vel
        processed_events.append(new_note)

    return processed_events
