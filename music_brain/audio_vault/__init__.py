# music_brain/audio_vault/__init__.py
"""
AudioVault - Sample library management for DAiW.

Structure:
    AudioVault/
    ├── raw/          # Unprocessed samples (Freesound, custom recordings)
    ├── refined/      # Normalized, tagged samples ready for use
    ├── output/       # Generated MIDI and rendered audio
    └── manifests/    # JSON metadata for packs and kits

Usage:
    from music_brain.audio_vault import OUTPUT_DIR, load_kit
    from music_brain.audio_vault.refinery import normalize_sample
"""

from music_brain.audio_vault.config import (
    VAULT_ROOT,
    RAW_DIR,
    REFINED_DIR,
    OUTPUT_DIR,
    MANIFESTS_DIR,
)
from music_brain.audio_vault.kit_loader import load_kit, get_gm_map

__all__ = [
    "VAULT_ROOT",
    "RAW_DIR",
    "REFINED_DIR",
    "OUTPUT_DIR",
    "MANIFESTS_DIR",
    "load_kit",
    "get_gm_map",
]
