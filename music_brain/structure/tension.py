# music_brain/structure/tension.py
import numpy as np


def generate_tension_curve(total_bars: int, structure_type: str = "standard") -> np.ndarray:
    """
    Generates a 1D array of tension multipliers (~0.5 to ~1.5) for each bar.
    These act as automation lanes for velocity / complexity.

    structure_type:
        - "climb"    : slow linear build (post-rock, endless build)
        - "standard" : verse/chorus/bridge shape
        - "constant" : flat line, loop/techno
    """
    if total_bars <= 0:
        return np.array([], dtype=float)

    curve = np.ones(total_bars, dtype=float)

    if structure_type == "climb":
        # Simple build from 0.6 up to 1.4
        curve = np.linspace(0.6, 1.4, total_bars)

    elif structure_type == "standard":
        # Rough Verse/Chorus/Verse/Chorus/Bridge/Outro archetype
        # Defaults to 1.0, then we overwrite slices.
        curve[:] = 1.0

        # Verse 1: quiet, slight build (0–15)
        end_v1 = min(16, total_bars)
        curve[0:end_v1] = np.linspace(0.6, 0.7, end_v1)

        # Chorus 1: loud & steady (16–31)
        if total_bars > 16:
            end_c1 = min(32, total_bars)
            curve[16:end_c1] = 1.1

        # Verse 2: a bit higher than V1 (32–47)
        if total_bars > 32:
            end_v2 = min(48, total_bars)
            curve[32:end_v2] = np.linspace(0.7, 0.8, end_v2 - 32)

        # Bridge / Climax (48–59)
        if total_bars > 48:
            end_bridge = min(60, total_bars)
            curve[48:end_bridge] = np.linspace(1.2, 1.5, end_bridge - 48)

        # Outro: drop down (60+)
        if total_bars > 60:
            curve[60:] = 0.5

    elif structure_type == "constant":
        curve[:] = 1.0

    else:
        # Unknown structure type → flat line instead of chaos
        curve[:] = 1.0

    return curve
