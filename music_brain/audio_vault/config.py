# music_brain/audio_vault/config.py
"""
AudioVault configuration and paths.

The vault can live anywhere on disk. By default, it's a sibling
to the repo root, but can be overridden via environment variable.
"""

import os
from pathlib import Path

# Allow override via environment variable
_vault_env = os.environ.get("DAIW_VAULT_ROOT")

if _vault_env:
    VAULT_ROOT = Path(_vault_env)
else:
    # Default: AudioVault as sibling to the repo
    # e.g., if repo is ~/Projects/DAiW-Music-Brain, vault is ~/Projects/AudioVault
    _repo_root = Path(__file__).parent.parent.parent
    VAULT_ROOT = _repo_root.parent / "AudioVault"

# Subdirectories
RAW_DIR = VAULT_ROOT / "raw"
REFINED_DIR = VAULT_ROOT / "refined"
OUTPUT_DIR = VAULT_ROOT / "output"
MANIFESTS_DIR = VAULT_ROOT / "manifests"

# Ensure output directory exists (others are created by refinery)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_vault_info() -> dict:
    """Return vault configuration as a dict (useful for debugging)."""
    return {
        "vault_root": str(VAULT_ROOT),
        "raw_dir": str(RAW_DIR),
        "refined_dir": str(REFINED_DIR),
        "output_dir": str(OUTPUT_DIR),
        "manifests_dir": str(MANIFESTS_DIR),
        "vault_exists": VAULT_ROOT.exists(),
        "output_exists": OUTPUT_DIR.exists(),
    }
