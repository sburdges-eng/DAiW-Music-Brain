"""
tension.py - Mood-Driven Tension Curve Generation
==================================================

Maps emotional states to structural tension curves, creating dynamic
arc over a song that matches the emotional intent.

Philosophy: Music should have emotional shape, not just static intensity.
The tension curve is how we make verses feel intimate and choruses explosive.
"""

from typing import List, Iterator


# =================================================================
# MOOD -> STRUCTURE TYPE MAPPING
# =================================================================

MOOD_TO_STRUCTURE = {
    # High energy / release seeking
    "rage": "spiral",
    "defiance": "catharsis",
    "fear": "spiral",

    # Low energy / introspective
    "grief": "descent",
    "dissociation": "static",

    # Transcendent / expansive
    "awe": "slow_build",
    "nostalgia": "wave",

    # Balanced / nurturing
    "tenderness": "slow_build",

    # Balanced / neutral
    "confusion": "wave",
    "neutral": "verse_chorus",
}


# =================================================================
# TENSION CURVE DEFINITIONS
# =================================================================

# Base tension curve templates (8-section blueprints)
STRUCTURE_CURVES = {
    # Verse-Chorus: Low, Low, High, High, Low, High, High, Outro
    "verse_chorus": [0.6, 0.6, 1.0, 1.0, 0.6, 1.0, 1.0, 0.8],
    "standard": [0.6, 0.6, 1.0, 1.0, 0.6, 1.0, 1.0, 0.8],  # Alias

    # Slow Build: Gradual increase to climax
    "slow_build": [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1],

    # Front-loaded: Big start, settle, return
    "front_loaded": [1.1, 1.0, 0.6, 0.6, 0.8, 0.8, 1.0, 1.0],

    # Wave: Ebb and flow
    "wave": [0.6, 0.9, 0.6, 1.0, 0.5, 1.1, 0.6, 0.8],

    # Catharsis: Build to massive release
    "catharsis": [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.2, 1.0],

    # Static: Hypnotic, minimal variation (for dissociation, trance)
    "static": [0.8, 0.8, 0.8, 0.85, 0.8, 0.85, 0.8, 0.8],

    # Descent: Falling energy (sadness, resignation)
    "descent": [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.35],

    # Spiral: Escalating chaos (anxiety, rage)
    "spiral": [0.5, 0.7, 0.6, 0.9, 0.7, 1.0, 0.9, 1.2],
}


def choose_structure_type_for_mood(mood: str) -> str:
    """
    Select the appropriate structure/tension curve type for a given mood.

    Maps emotional states to structural archetypes that enhance
    the emotional journey of the music.

    Args:
        mood: Primary emotional state (grief, rage, awe, etc.)

    Returns:
        Structure type name for use with generate_tension_curve()

    Examples:
        >>> choose_structure_type_for_mood("grief")
        'descent'
        >>> choose_structure_type_for_mood("rage")
        'spiral'
        >>> choose_structure_type_for_mood("neutral")
        'verse_chorus'
    """
    mood_lower = (mood or "neutral").lower().strip()
    return MOOD_TO_STRUCTURE.get(mood_lower, "verse_chorus")


def generate_tension_curve(
    total_bars: int,
    structure_type: str = "standard",
    repeat: bool = True,
    smooth: bool = True,
) -> Iterator[float]:
    """
    Generate a bar-by-bar tension curve for the specified length.

    The tension values scale velocity, complexity, and other parameters
    to create dynamic "breathing" over the course of a song.

    Args:
        total_bars: Total number of bars to generate
        structure_type: Curve template name (see STRUCTURE_CURVES)
        repeat: If True, tile the curve; if False, stretch to fit
        smooth: If True, interpolate for smoother transitions (when stretching)

    Yields:
        Tension multiplier for each bar (typically 0.3 to 1.2)

    Examples:
        >>> list(generate_tension_curve(16, "slow_build"))[:4]
        [0.4, 0.4, 0.5, 0.5]
    """
    # Get base curve, defaulting to standard if unknown
    base_curve = STRUCTURE_CURVES.get(structure_type, STRUCTURE_CURVES["standard"])
    curve_len = len(base_curve)

    if total_bars <= 0:
        return

    if repeat:
        # Tile the curve to fill all bars
        # Each section of the base curve represents multiple bars
        bars_per_section = max(1, total_bars // curve_len)

        for bar_idx in range(total_bars):
            section_idx = (bar_idx // bars_per_section) % curve_len
            yield base_curve[section_idx]
    else:
        # Stretch the curve to fit exactly
        for bar_idx in range(total_bars):
            # Map bar index to curve position
            curve_pos = (bar_idx / total_bars) * curve_len
            idx = int(curve_pos)
            frac = curve_pos - idx

            if idx >= curve_len - 1:
                yield base_curve[-1]
            elif smooth and frac > 0:
                # Linear interpolation for smoothness
                v1 = base_curve[idx]
                v2 = base_curve[idx + 1]
                yield v1 + (v2 - v1) * frac
            else:
                yield base_curve[idx]


def get_tension_at_bar(
    bar_index: int,
    total_bars: int,
    structure_type: str = "standard",
) -> float:
    """
    Get tension value at a specific bar without generating the full curve.

    Useful for real-time lookups during MIDI generation.

    Args:
        bar_index: Which bar (0-indexed)
        total_bars: Total bars in the song
        structure_type: Curve template name

    Returns:
        Tension multiplier for that bar
    """
    base_curve = STRUCTURE_CURVES.get(structure_type, STRUCTURE_CURVES["standard"])
    curve_len = len(base_curve)

    if total_bars <= 0 or bar_index < 0:
        return 1.0

    bars_per_section = max(1, total_bars // curve_len)
    section_idx = (bar_index // bars_per_section) % curve_len

    return base_curve[section_idx]


def list_structure_types() -> List[str]:
    """Return all available structure/curve types."""
    return list(STRUCTURE_CURVES.keys())


def get_structure_curve(name: str) -> List[float]:
    """
    Get raw structure curve by name.

    Args:
        name: Structure type name

    Returns:
        List of tension multipliers

    Raises:
        ValueError: If name not found
    """
    if name not in STRUCTURE_CURVES:
        available = ", ".join(STRUCTURE_CURVES.keys())
        raise ValueError(f"Unknown structure type: {name}. Available: {available}")

    return STRUCTURE_CURVES[name].copy()
