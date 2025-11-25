# music_brain/audio_vault/refinery.py
"""
Audio Refinery - Sample normalization and augmentation.

Takes raw samples from AudioVault/raw and produces
normalized, tagged samples in AudioVault/refined.

Future: audiomentations integration for generating variants.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from music_brain.audio_vault.config import RAW_DIR, REFINED_DIR, MANIFESTS_DIR

# Try to import audio processing libs (optional)
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

try:
    import soundfile as sf
    import numpy as np
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False


# Target normalization settings
TARGET_SAMPLE_RATE = 44100
TARGET_CHANNELS = 1  # Mono
TARGET_BIT_DEPTH = 16
TARGET_LUFS = -14.0  # Loudness target (approximate via peak normalization)


def normalize_sample(
    input_path: Path,
    output_path: Path,
    target_db: float = -3.0,
) -> bool:
    """
    Normalize a single audio sample.

    Args:
        input_path: Path to raw sample
        output_path: Path to write normalized sample
        target_db: Target peak level in dB

    Returns:
        True if successful, False otherwise.
    """
    if not PYDUB_AVAILABLE:
        print("[WARN] pydub not installed, copying file as-is")
        import shutil
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(input_path, output_path)
        return True

    try:
        # Load audio
        audio = AudioSegment.from_file(str(input_path))

        # Convert to mono if stereo
        if audio.channels > 1:
            audio = audio.set_channels(1)

        # Resample if needed
        if audio.frame_rate != TARGET_SAMPLE_RATE:
            audio = audio.set_frame_rate(TARGET_SAMPLE_RATE)

        # Normalize to target dB
        change_in_db = target_db - audio.max_dBFS
        audio = audio.apply_gain(change_in_db)

        # Export
        output_path.parent.mkdir(parents=True, exist_ok=True)
        audio.export(str(output_path), format="wav")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to normalize {input_path}: {e}")
        return False


def refine_pack(
    pack_name: str,
    source_subdir: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Refine all samples in a raw pack.

    Args:
        pack_name: Name of the pack (subdirectory in raw/)
        source_subdir: Optional subdirectory within the pack
        tags: Tags to apply to all samples in manifest

    Returns:
        Manifest dict with processed sample info.
    """
    if source_subdir:
        source_dir = RAW_DIR / pack_name / source_subdir
    else:
        source_dir = RAW_DIR / pack_name

    if not source_dir.exists():
        print(f"[ERROR] Source directory not found: {source_dir}")
        return {"error": "source_not_found", "path": str(source_dir)}

    output_dir = REFINED_DIR / pack_name
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "pack_name": pack_name,
        "source_dir": str(source_dir),
        "output_dir": str(output_dir),
        "processed_at": datetime.now().isoformat(),
        "tags": tags or [],
        "samples": [],
    }

    # Find all audio files
    audio_extensions = {".wav", ".mp3", ".flac", ".ogg", ".aif", ".aiff"}
    audio_files = [
        f for f in source_dir.rglob("*")
        if f.suffix.lower() in audio_extensions
    ]

    print(f"[INFO] Found {len(audio_files)} audio files in {source_dir}")

    for audio_file in audio_files:
        # Generate output filename (clean, lowercase, underscores)
        clean_name = audio_file.stem.lower().replace(" ", "_").replace("-", "_")
        clean_name = "".join(c for c in clean_name if c.isalnum() or c == "_")
        output_name = f"{clean_name}.wav"
        output_path = output_dir / output_name

        # Skip if already processed (by hash)
        file_hash = _hash_file(audio_file)

        success = normalize_sample(audio_file, output_path)

        if success:
            manifest["samples"].append({
                "original_name": audio_file.name,
                "refined_name": output_name,
                "refined_path": str(output_path.relative_to(REFINED_DIR)),
                "source_hash": file_hash,
                "tags": tags or [],
            })

    # Save manifest
    manifest_path = MANIFESTS_DIR / "packs" / f"{pack_name}.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"[INFO] Refined {len(manifest['samples'])} samples -> {output_dir}")
    print(f"[INFO] Manifest saved -> {manifest_path}")

    return manifest


def _hash_file(path: Path, chunk_size: int = 8192) -> str:
    """Generate MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()[:12]


# =============================================================================
# FUTURE: Augmentation pipeline (audiomentations)
# =============================================================================

def augment_sample(
    input_path: Path,
    output_dir: Path,
    num_variants: int = 4,
    complexity: float = 0.5,
) -> List[Path]:
    """
    Generate augmented variants of a sample.

    Requires: pip install audiomentations

    Args:
        input_path: Path to source sample
        output_dir: Directory to write variants
        num_variants: Number of variants to generate
        complexity: 0.0-1.0 controls how extreme augmentations are

    Returns:
        List of paths to generated variants.
    """
    try:
        from audiomentations import Compose, AddGaussianNoise, TimeStretch, PitchShift, HighPassFilter
    except ImportError:
        print("[WARN] audiomentations not installed, skipping augmentation")
        return []

    if not SOUNDFILE_AVAILABLE:
        print("[WARN] soundfile not installed, skipping augmentation")
        return []

    # Build augmentation pipeline based on complexity
    transforms = [
        AddGaussianNoise(
            min_amplitude=0.001 * complexity,
            max_amplitude=0.015 * complexity,
            p=0.8
        ),
        TimeStretch(
            min_rate=1.0 - (0.1 * complexity),
            max_rate=1.0 + (0.1 * complexity),
            p=0.7
        ),
        PitchShift(
            min_semitones=-2 * complexity,
            max_semitones=2 * complexity,
            p=0.7
        ),
    ]

    if complexity > 0.5:
        transforms.append(
            HighPassFilter(
                min_cutoff_freq=300.0,
                max_cutoff_freq=3000.0 * complexity,
                p=0.5
            )
        )

    augmenter = Compose(transforms)

    # Load source
    samples, sample_rate = sf.read(str(input_path))
    if samples.ndim > 1:
        samples = samples.mean(axis=1)  # Convert to mono
    samples = samples.astype(np.float32)

    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = input_path.stem

    generated = []
    for i in range(num_variants):
        augmented = augmenter(samples, sample_rate=sample_rate)
        out_path = output_dir / f"{base_name}_var{i+1}.wav"
        sf.write(str(out_path), augmented, sample_rate)
        generated.append(out_path)

    return generated
