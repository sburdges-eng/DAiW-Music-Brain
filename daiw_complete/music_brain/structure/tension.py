"""
Tension Curve Generator
=======================
Bar-level automation lanes for dynamics / intensity.
"""

from __future__ import annotations

import numpy as np


def generate_tension_curve(
    total_bars: int,
    structure_type: str = "standard",
) -> np.ndarray:
    """
    Generates a 1D array of tension multipliers (~0.5 to ~1.5) per bar.

    structure_type:
        - "climb"    : slow linear build (post-rock style)
        - "standard" : verse/chorus/bridge shaped arc
        - "constant" : flat line
    """
    if total_bars <= 0:
        return np.array([], dtype=float)

    curve = np.ones(total_bars, dtype=float)

    if structure_type == "climb":
        curve = np.linspace(0.6, 1.4, total_bars)

    elif structure_type == "standard":
        curve[:] = 1.0

        # Verse 1: quiet, small build (0-15)
        end_v1 = min(16, total_bars)
        curve[0:end_v1] = np.linspace(0.6, 0.7, end_v1)

        # Chorus 1: loud & steady (16-31)
        if total_bars > 16:
            end_c1 = min(32, total_bars)
            curve[16:end_c1] = 1.1

        # Verse 2: slightly higher floor (32-47)
        if total_bars > 32:
            end_v2 = min(48, total_bars)
            curve[32:end_v2] = np.linspace(0.7, 0.8, end_v2 - 32)

        # Bridge / Climax (48-59)
        if total_bars > 48:
            end_bridge = min(60, total_bars)
            curve[48:end_bridge] = np.linspace(1.2, 1.5, end_bridge - 48)

        # Outro (60+)
        if total_bars > 60:
            curve[60:] = 0.5

    elif structure_type == "constant":
        curve[:] = 1.0

    else:
        curve[:] = 1.0

    return curve


def choose_structure_type_for_mood(mood: str) -> str:
    """
    Convenience helper to map affect/mood into a macro structure type.
    """
    m = (mood or "").lower()
    if m in {"grief", "dissociation", "broken"}:
        return "climb"
    if m in {"rage", "defiance", "fear"}:
        return "standard"
    if m in {"awe", "nostalgia"}:
        return "standard"
    return "constant"
