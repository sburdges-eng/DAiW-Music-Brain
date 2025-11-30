"""
DAiW Central Configuration
==========================

Single source of truth for all configurable constants.
Import from here to ensure consistent behavior across modules.

Environment Variables:
    DAIW_AUDIO_VAULT_PATH - Path to audio vault directory
    DAIW_SEED - Random seed for reproducible output (optional)
"""

import os
from pathlib import Path
from typing import Optional


# =============================================================================
# PATHS
# =============================================================================

def get_audio_vault_path() -> Path:
    """
    Get the audio vault path from environment or default locations.

    Checks in order:
    1. DAIW_AUDIO_VAULT_PATH environment variable
    2. ~/Music/AudioVault
    3. ./audio_vault (relative to cwd)

    Returns:
        Path to the audio vault directory
    """
    # Check environment variable first
    env_path = os.environ.get("DAIW_AUDIO_VAULT_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()

    # Default locations
    home_vault = Path.home() / "Music" / "AudioVault"
    if home_vault.exists():
        return home_vault

    # Fallback to relative path
    return Path.cwd() / "audio_vault"


def get_data_path() -> Path:
    """Get path to the music_brain/data directory."""
    return Path(__file__).parent / "data"


# =============================================================================
# GROOVE ENGINE CONSTANTS
# =============================================================================

class GrooveConfig:
    """Configuration for the groove/humanization engine."""

    # Timing drift limits (in ticks at 480 PPQ)
    SAFE_DRIFT_LIMIT: int = 20      # Max timing offset for "safe" mode
    MAX_DRIFT_LIMIT: int = 60       # Absolute maximum timing offset

    # Velocity bounds
    VELOCITY_MIN: int = 1           # Minimum MIDI velocity
    VELOCITY_MAX: int = 127         # Maximum MIDI velocity
    VELOCITY_DEFAULT: int = 80      # Default velocity when not specified

    # Ghost note settings
    GHOST_NOTE_VELOCITY_RATIO: float = 0.4   # Ghost notes are 40% of main velocity
    GHOST_NOTE_PROBABILITY: float = 0.15     # 15% chance of ghost note insertion

    # Swing settings
    SWING_AMOUNT_DEFAULT: float = 0.0        # No swing by default
    SWING_AMOUNT_MAX: float = 0.5            # Maximum swing (50% of beat)


# =============================================================================
# TENSION CURVE CONSTANTS
# =============================================================================

class TensionConfig:
    """Configuration for tension curve generation."""

    # Velocity multiplier bounds
    TENSION_MIN: float = 0.3        # Minimum tension multiplier
    TENSION_MAX: float = 1.5        # Maximum tension multiplier

    # Default structure type by mood
    MOOD_TO_STRUCTURE: dict = {
        "grief": "climb",
        "dissociation": "climb",
        "rage": "standard",
        "defiance": "standard",
        "fear": "standard",
        "awe": "constant",
        "nostalgia": "constant",
        "tenderness": "constant",
        "confusion": "climb",
        "neutral": "constant",
    }

    # Structure type parameters
    CLIMB_START: float = 0.6
    CLIMB_END: float = 1.4
    STANDARD_VERSE_RANGE: tuple = (0.6, 0.7)
    STANDARD_CHORUS: float = 1.1
    STANDARD_BRIDGE_RANGE: tuple = (1.2, 1.5)
    STANDARD_OUTRO: float = 0.5


# =============================================================================
# THERAPY ENGINE CONSTANTS
# =============================================================================

class TherapyConfig:
    """Configuration for the therapy/affect engine."""

    # Tempo ranges by affect
    TEMPO_BASE: int = 100
    TEMPO_HIGH_ENERGY: int = 130    # rage, fear, defiance
    TEMPO_LOW_ENERGY: int = 70      # grief, dissociation
    TEMPO_MEDIUM_ENERGY: int = 90   # awe

    # Length (bars) by motivation scale
    LENGTH_LOW_MOTIVATION: int = 16     # motivation 1-3
    LENGTH_MID_MOTIVATION: int = 32     # motivation 4-7
    LENGTH_HIGH_MOTIVATION: int = 64    # motivation 8-10

    # Complexity adjustments
    HIGH_MOTIVATION_COMPLEXITY_BOOST: float = 0.1


# =============================================================================
# MIDI CONSTANTS
# =============================================================================

class MidiConfig:
    """Configuration for MIDI generation."""

    # Default PPQ (pulses per quarter note)
    DEFAULT_PPQ: int = 480

    # Default time signature
    DEFAULT_TIME_SIGNATURE: tuple = (4, 4)

    # Base octave for chord voicings (MIDI note number for C)
    CHORD_BASE_OCTAVE: int = 48     # C3


# =============================================================================
# REPRODUCIBILITY
# =============================================================================

def get_seed() -> Optional[int]:
    """
    Get random seed from environment if set.

    Set DAIW_SEED environment variable for reproducible output.

    Returns:
        Integer seed if set, None otherwise
    """
    seed_str = os.environ.get("DAIW_SEED")
    if seed_str:
        try:
            return int(seed_str)
        except ValueError:
            return None
    return None


def set_seeds(seed: Optional[int] = None) -> None:
    """
    Set random seeds for reproducibility.

    Args:
        seed: Integer seed. If None, uses DAIW_SEED env var or does nothing.
    """
    if seed is None:
        seed = get_seed()

    if seed is not None:
        import random
        random.seed(seed)

        try:
            import numpy as np
            np.random.seed(seed)
        except ImportError:
            pass


# =============================================================================
# VERSION
# =============================================================================

VERSION = "0.2.0"
