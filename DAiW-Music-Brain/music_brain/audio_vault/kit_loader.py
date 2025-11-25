# music_brain/audio_vault/kit_loader.py
"""
Kit loader for AudioVault.

Kits are JSON files that map MIDI notes to sample paths.
They follow General MIDI drum mappings by default.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any

from music_brain.audio_vault.config import MANIFESTS_DIR, REFINED_DIR

# General MIDI Drum Map (standard note assignments)
GM_DRUM_MAP = {
    35: "kick_acoustic",
    36: "kick",
    37: "sidestick",
    38: "snare",
    39: "clap",
    40: "snare_electric",
    41: "tom_low_floor",
    42: "hihat_closed",
    43: "tom_high_floor",
    44: "hihat_pedal",
    45: "tom_low",
    46: "hihat_open",
    47: "tom_low_mid",
    48: "tom_hi_mid",
    49: "crash",
    50: "tom_high",
    51: "ride",
    52: "china",
    53: "ride_bell",
    54: "tambourine",
    55: "splash",
    56: "cowbell",
    57: "crash_2",
    58: "vibraslap",
    59: "ride_2",
}

# Default kit structure (minimal working kit)
DEFAULT_KIT = {
    "name": "DAiW_Default",
    "description": "Default industrial/glitch kit",
    "gm_map": {
        36: "kick/kick_01.wav",
        38: "snare/snare_01.wav",
        42: "hihat/hh_closed_01.wav",
        46: "hihat/hh_open_01.wav",
        49: "crash/crash_01.wav",
        51: "ride/ride_01.wav",
    },
    "tags": ["industrial", "glitch", "default"],
    "chaos_tier": "all",  # "low", "mid", "high", or "all"
}


def load_kit(kit_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Load a kit from the manifests directory.

    Args:
        kit_name: Name of the kit (without .json extension).
                  If None, returns the default kit.

    Returns:
        Kit dictionary with 'gm_map' and metadata.
    """
    if kit_name is None:
        return DEFAULT_KIT.copy()

    kit_path = MANIFESTS_DIR / "kits" / f"{kit_name}.json"

    if not kit_path.exists():
        print(f"[WARN] Kit '{kit_name}' not found at {kit_path}, using default")
        return DEFAULT_KIT.copy()

    try:
        with open(kit_path, "r") as f:
            kit = json.load(f)
        return kit
    except (json.JSONDecodeError, OSError) as e:
        print(f"[ERROR] Failed to load kit '{kit_name}': {e}")
        return DEFAULT_KIT.copy()


def get_gm_map() -> Dict[int, str]:
    """Return the standard General MIDI drum map."""
    return GM_DRUM_MAP.copy()


def resolve_sample_path(kit: Dict[str, Any], note: int) -> Optional[Path]:
    """
    Resolve the full path to a sample for a given MIDI note.

    Args:
        kit: Kit dictionary with 'gm_map'
        note: MIDI note number

    Returns:
        Path to the sample file, or None if not mapped.
    """
    gm_map = kit.get("gm_map", {})
    relative_path = gm_map.get(note) or gm_map.get(str(note))

    if relative_path is None:
        return None

    full_path = REFINED_DIR / relative_path

    if not full_path.exists():
        # Try without subdirectory (flat structure)
        flat_path = REFINED_DIR / Path(relative_path).name
        if flat_path.exists():
            return flat_path
        return None

    return full_path


def list_available_kits() -> list:
    """List all available kit names in the manifests directory."""
    kits_dir = MANIFESTS_DIR / "kits"
    if not kits_dir.exists():
        return []

    return [f.stem for f in kits_dir.glob("*.json")]


def save_kit(kit: Dict[str, Any], kit_name: str) -> Path:
    """
    Save a kit to the manifests directory.

    Args:
        kit: Kit dictionary
        kit_name: Name for the kit file

    Returns:
        Path to the saved kit file.
    """
    kits_dir = MANIFESTS_DIR / "kits"
    kits_dir.mkdir(parents=True, exist_ok=True)

    kit_path = kits_dir / f"{kit_name}.json"

    with open(kit_path, "w") as f:
        json.dump(kit, f, indent=2)

    return kit_path
