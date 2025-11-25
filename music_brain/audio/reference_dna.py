"""
Reference DNA Analyzer - Learn from reference tracks.

Analyzes reference audio to extract tempo, key, and brightness,
allowing DAiW to align generated content with a target sound.

Philosophy: Reference tracks inform, not dictate. The emotional
intent always takes precedence.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict

try:
    import librosa
    import numpy as np
    LIBROSA_AVAILABLE = True
except ImportError:
    librosa = None
    np = None
    LIBROSA_AVAILABLE = False


# =================================================================
# DATA CLASSES
# =================================================================

@dataclass
class ReferenceProfile:
    """DNA profile extracted from a reference track."""
    tempo_bpm: float
    key_root: Optional[str]
    key_mode: Optional[str]  # major, minor
    brightness: float  # 0-1 normalized spectral centroid
    energy: float      # 0-1 normalized RMS energy
    warmth: float      # 0-1 low-frequency content

    def __repr__(self) -> str:
        key = f"{self.key_root} {self.key_mode}" if self.key_root else "unknown"
        return (
            f"ReferenceProfile(tempo={self.tempo_bpm:.1f}bpm, "
            f"key={key}, brightness={self.brightness:.2f})"
        )


# =================================================================
# KEY DETECTION
# =================================================================

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Krumhansl-Kessler key profiles
MAJOR_PROFILE = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
MINOR_PROFILE = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]


def _estimate_key(y, sr) -> tuple:
    """
    Estimate key from audio using chroma features and key profiles.

    Args:
        y: Audio time series
        sr: Sample rate

    Returns:
        Tuple of (root_note, mode) or (None, None) if detection fails
    """
    if not LIBROSA_AVAILABLE:
        return (None, None)

    try:
        # Compute chroma features
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        mean_chroma = np.mean(chroma, axis=1)

        # Normalize
        mean_chroma = mean_chroma / (np.sum(mean_chroma) + 1e-10)

        best_key = None
        best_mode = None
        best_corr = -1

        for root in range(12):
            # Rotate profiles to each root
            major_rotated = np.roll(MAJOR_PROFILE, root)
            minor_rotated = np.roll(MINOR_PROFILE, root)

            # Normalize profiles
            major_norm = major_rotated / np.sum(major_rotated)
            minor_norm = minor_rotated / np.sum(minor_rotated)

            # Correlation with mean chroma
            major_corr = np.corrcoef(mean_chroma, major_norm)[0, 1]
            minor_corr = np.corrcoef(mean_chroma, minor_norm)[0, 1]

            if major_corr > best_corr:
                best_corr = major_corr
                best_key = root
                best_mode = "major"

            if minor_corr > best_corr:
                best_corr = minor_corr
                best_key = root
                best_mode = "minor"

        if best_key is not None:
            return (NOTE_NAMES[best_key], best_mode)

        return (None, None)

    except Exception:
        return (None, None)


# =================================================================
# MAIN ANALYSIS
# =================================================================

def analyze_reference(path: Path) -> Optional[ReferenceProfile]:
    """
    Analyze a reference audio file and extract its DNA profile.

    Args:
        path: Path to audio file (wav, mp3, etc.)

    Returns:
        ReferenceProfile with extracted characteristics, or None if failed
    """
    if not LIBROSA_AVAILABLE:
        print("[REFERENCE DNA]: librosa not installed. Install with: pip install librosa")
        return None

    path = Path(path)
    if not path.exists():
        print(f"[REFERENCE DNA]: File not found: {path}")
        return None

    try:
        # Load audio (mono, original sample rate)
        y, sr = librosa.load(str(path), mono=True)

        # Tempo estimation
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        # Handle numpy array vs scalar
        if hasattr(tempo, '__len__'):
            tempo = float(tempo[0]) if len(tempo) > 0 else 120.0
        else:
            tempo = float(tempo)

        # Key estimation
        key_root, key_mode = _estimate_key(y, sr)

        # Brightness via spectral centroid
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        mean_centroid = float(np.mean(centroid))
        # Normalize roughly using Nyquist freq
        max_freq = sr / 2
        brightness = max(0.0, min(1.0, mean_centroid / max_freq))

        # Energy via RMS
        rms = librosa.feature.rms(y=y)
        mean_rms = float(np.mean(rms))
        # Normalize (typical RMS for music is 0.05-0.3)
        energy = max(0.0, min(1.0, mean_rms / 0.3))

        # Warmth via low-frequency energy ratio
        # Calculate spectral rolloff at low percentage
        rolloff_low = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.25)
        mean_rolloff = float(np.mean(rolloff_low))
        # Lower rolloff = more low-frequency content = warmer
        warmth = max(0.0, min(1.0, 1.0 - (mean_rolloff / (sr / 4))))

        return ReferenceProfile(
            tempo_bpm=tempo,
            key_root=key_root,
            key_mode=key_mode,
            brightness=brightness,
            energy=energy,
            warmth=warmth,
        )

    except Exception as e:
        print(f"[REFERENCE DNA]: Analysis failed: {e}")
        return None


def apply_reference_to_plan(plan, profile: ReferenceProfile) -> None:
    """
    Apply reference profile characteristics to a HarmonyPlan.

    Modifies the plan in-place based on reference DNA.

    Args:
        plan: HarmonyPlan to modify
        profile: ReferenceProfile to apply
    """
    if profile is None:
        return

    # Apply tempo (with some blending to preserve intent)
    if hasattr(plan, "tempo_bpm"):
        original_tempo = plan.tempo_bpm
        # Blend 70% reference, 30% original intent
        plan.tempo_bpm = int(profile.tempo_bpm * 0.7 + original_tempo * 0.3)

    # Apply key if detected
    if profile.key_root and hasattr(plan, "root_note"):
        plan.root_note = profile.key_root

    if profile.key_mode and hasattr(plan, "mode"):
        if profile.key_mode == "minor":
            plan.mode = "aeolian"
        elif profile.key_mode == "major":
            plan.mode = "ionian"

    # Adjust complexity based on brightness
    if hasattr(plan, "complexity"):
        # Brighter = potentially more complex/energetic
        brightness_mod = (profile.brightness - 0.5) * 0.2
        plan.complexity = max(0.0, min(1.0, plan.complexity + brightness_mod))

    # Adjust vulnerability based on warmth
    if hasattr(plan, "vulnerability"):
        # Warmer = more intimate = higher vulnerability
        warmth_mod = (profile.warmth - 0.5) * 0.2
        plan.vulnerability = max(0.0, min(1.0, plan.vulnerability + warmth_mod))


def compare_profiles(
    profile_a: ReferenceProfile,
    profile_b: ReferenceProfile,
) -> Dict[str, float]:
    """
    Compare two reference profiles and return similarity metrics.

    Args:
        profile_a: First profile
        profile_b: Second profile

    Returns:
        Dict with similarity scores for tempo, brightness, energy, warmth
    """
    results = {}

    # Tempo similarity (within 20 BPM = 1.0, linear falloff)
    tempo_diff = abs(profile_a.tempo_bpm - profile_b.tempo_bpm)
    results["tempo"] = max(0.0, 1.0 - tempo_diff / 40.0)

    # Key similarity
    if profile_a.key_root and profile_b.key_root:
        results["key"] = 1.0 if profile_a.key_root == profile_b.key_root else 0.0
    else:
        results["key"] = 0.5  # Unknown

    # Direct comparison of normalized values
    results["brightness"] = 1.0 - abs(profile_a.brightness - profile_b.brightness)
    results["energy"] = 1.0 - abs(profile_a.energy - profile_b.energy)
    results["warmth"] = 1.0 - abs(profile_a.warmth - profile_b.warmth)

    # Overall similarity
    weights = {"tempo": 0.3, "key": 0.2, "brightness": 0.2, "energy": 0.15, "warmth": 0.15}
    results["overall"] = sum(results[k] * v for k, v in weights.items())

    return results
