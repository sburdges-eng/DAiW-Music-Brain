"""
Dynamic Tension Curves - Breathing Over Time

Applies bar-wise tension multipliers to create dynamic arc over a song.
This makes the track "breathe" with verse/chorus/bridge energy arcs.

Philosophy: Music should have emotional shape, not just static intensity.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


# =================================================================
# PRESET TENSION CURVES
# =================================================================

# Standard song structures
TENSION_CURVES = {
    # Verse-Chorus: Low, Low, High, High, Low, High, High, Outro
    "verse_chorus": [0.6, 0.6, 1.0, 1.0, 0.6, 1.0, 1.0, 0.8],

    # Slow Build: Gradual increase to climax
    "slow_build": [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2],

    # Intro-Heavy: Big start, settle, return
    "front_loaded": [1.2, 1.0, 0.6, 0.6, 0.8, 0.8, 1.0, 1.0],

    # Wave: Ebb and flow
    "wave": [0.6, 0.9, 0.6, 1.0, 0.5, 1.1, 0.6, 0.8],

    # Catharsis: Build to massive release
    "catharsis": [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.3, 1.0],

    # Static: Hypnotic, minimal variation
    "static": [0.8, 0.8, 0.8, 0.85, 0.8, 0.85, 0.8, 0.8],

    # Descent: Falling energy (sadness, resignation)
    "descent": [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3],

    # Spiral: Escalating chaos
    "spiral": [0.5, 0.7, 0.6, 0.9, 0.7, 1.1, 0.9, 1.3],
}


@dataclass
class TensionProfile:
    """Describes how tension changes over the song."""
    name: str
    multipliers: List[float]
    affects_velocity: bool = True
    affects_timing: bool = False
    affects_density: bool = False


def get_tension_curve(name: str) -> List[float]:
    """
    Get a preset tension curve by name.

    Args:
        name: Curve name (verse_chorus, slow_build, etc.)

    Returns:
        List of multiplier values

    Raises:
        ValueError: If curve name not found
    """
    if name not in TENSION_CURVES:
        available = ", ".join(TENSION_CURVES.keys())
        raise ValueError(f"Unknown tension curve: {name}. Available: {available}")

    return TENSION_CURVES[name].copy()


def list_tension_curves() -> List[str]:
    """List all available tension curve presets."""
    return list(TENSION_CURVES.keys())


# =================================================================
# TENSION APPLICATION
# =================================================================

def apply_tension_curve(
    events: List[Dict[str, Any]],
    bar_ticks: int,
    multipliers: List[float],
    affect_velocity: bool = True,
    affect_timing: bool = False,
    min_velocity: int = 1,
    max_velocity: int = 127,
) -> List[Dict[str, Any]]:
    """
    Scale velocities (and optionally timing) based on a bar-wise tension curve.

    This creates dynamic "breathing" over the course of a song, making
    verses feel intimate and choruses feel explosive.

    Args:
        events: List of note dicts with start_tick, velocity
        bar_ticks: Number of ticks per bar
        multipliers: List of tension factors per section/bar
            - Values < 1.0 = lower energy
            - Values > 1.0 = higher energy
        affect_velocity: Whether to scale velocities
        affect_timing: Whether to tighten/loosen timing based on tension
        min_velocity: Minimum allowed velocity
        max_velocity: Maximum allowed velocity

    Returns:
        New list of events with tension applied
    """
    if not events:
        return events

    if not multipliers:
        return [ev.copy() for ev in events]

    result = []

    for ev in events:
        new_ev = ev.copy()

        # Determine which bar this event is in
        start_tick = ev.get("start_tick", 0)
        bar_index = start_tick // bar_ticks

        # Get tension factor (clamp or wrap to curve length)
        if bar_index >= len(multipliers):
            # Option 1: Clamp to last value
            factor = multipliers[-1]
            # Option 2: Wrap around (uncomment if preferred)
            # factor = multipliers[bar_index % len(multipliers)]
        else:
            factor = multipliers[bar_index]

        # Apply to velocity
        if affect_velocity and "velocity" in new_ev:
            v = new_ev["velocity"]
            new_v = int(v * factor)

            # Clamp to valid range
            new_v = max(min_velocity, min(max_velocity, new_v))
            new_ev["velocity"] = new_v

        # Apply to timing (optional - tighter during high tension)
        if affect_timing and "start_tick" in new_ev:
            # Pull notes closer to grid during high-tension sections
            if factor > 1.0:
                grid_size = bar_ticks // 4  # Quarter note grid
                tick = new_ev["start_tick"]
                nearest_grid = round(tick / grid_size) * grid_size

                # Blend toward grid based on tension
                pull_factor = min(1.0, (factor - 1.0) * 2)
                new_tick = int(tick + (nearest_grid - tick) * pull_factor)
                new_ev["start_tick"] = max(0, new_tick)

        result.append(new_ev)

    return result


def apply_section_markers(
    events: List[Dict[str, Any]],
    sections: List[Dict[str, Any]],
    ppq: int = 480,
    beats_per_bar: int = 4,
) -> List[Dict[str, Any]]:
    """
    Apply tension based on named sections (verse, chorus, bridge, etc.)

    Args:
        events: List of note events
        sections: List of section dicts with:
            - start_bar: int
            - end_bar: int
            - type: str (verse, chorus, bridge, etc.)
            - tension: float (optional override)
        ppq: Pulses per quarter note
        beats_per_bar: Beats per bar

    Returns:
        Events with section-appropriate tension applied
    """
    if not events or not sections:
        return [ev.copy() for ev in events]

    # Default tension by section type
    section_tensions = {
        "intro": 0.6,
        "verse": 0.7,
        "pre_chorus": 0.85,
        "chorus": 1.0,
        "bridge": 0.75,
        "breakdown": 0.5,
        "build": 0.9,
        "drop": 1.2,
        "outro": 0.6,
    }

    bar_ticks = ppq * beats_per_bar

    # Build bar-to-tension mapping
    max_bar = max(s.get("end_bar", 0) for s in sections)
    bar_tensions = [0.8] * (max_bar + 1)  # Default

    for section in sections:
        start_bar = section.get("start_bar", 0)
        end_bar = section.get("end_bar", start_bar + 1)
        section_type = section.get("type", "verse").lower()

        # Get tension (explicit override or from type)
        tension = section.get("tension", section_tensions.get(section_type, 0.8))

        for bar in range(start_bar, min(end_bar, len(bar_tensions))):
            bar_tensions[bar] = tension

    return apply_tension_curve(events, bar_ticks, bar_tensions)


def generate_curve_for_bars(
    total_bars: int,
    curve_name: str = "verse_chorus",
    repeat: bool = True,
) -> List[float]:
    """
    Generate a tension curve that spans the specified number of bars.

    Args:
        total_bars: Total number of bars in the song
        curve_name: Name of the preset curve to use
        repeat: If True, tile the curve; if False, stretch it

    Returns:
        List of multipliers, one per bar
    """
    base_curve = get_tension_curve(curve_name)

    if repeat:
        # Tile the curve to fill all bars
        result = []
        while len(result) < total_bars:
            result.extend(base_curve)
        return result[:total_bars]
    else:
        # Stretch the curve to fill all bars
        if len(base_curve) >= total_bars:
            return base_curve[:total_bars]

        result = []
        for i in range(total_bars):
            # Map bar index to curve position
            curve_pos = (i / total_bars) * len(base_curve)
            idx = int(curve_pos)
            frac = curve_pos - idx

            if idx >= len(base_curve) - 1:
                result.append(base_curve[-1])
            else:
                # Linear interpolation
                v1 = base_curve[idx]
                v2 = base_curve[idx + 1]
                result.append(v1 + (v2 - v1) * frac)

        return result
