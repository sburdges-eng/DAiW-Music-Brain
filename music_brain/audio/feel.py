"""
Audio Feel Analysis - Extract feel and groove characteristics from audio.

Analyzes:
- Tempo and beat positions
- Energy curve
- Spectral characteristics
- Dynamic range
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# Optional imports for audio processing
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


@dataclass
class AudioFeatures:
    """
    Extracted audio features and feel characteristics.
    """
    # Basic info
    filename: str = ""
    duration_seconds: float = 0.0
    sample_rate: int = 44100
    
    # Tempo/rhythm
    tempo_bpm: float = 120.0
    tempo_confidence: float = 0.0
    beat_positions: List[float] = field(default_factory=list)  # In seconds
    
    # Energy
    energy_curve: List[float] = field(default_factory=list)  # Per-beat energy
    rms_mean: float = 0.0
    rms_std: float = 0.0
    dynamic_range_db: float = 0.0
    
    # Spectral
    spectral_centroid_mean: float = 0.0  # "Brightness"
    spectral_rolloff_mean: float = 0.0
    spectral_bandwidth_mean: float = 0.0
    
    # Feel characteristics
    swing_estimate: float = 0.0  # 0.0-1.0
    groove_regularity: float = 0.0  # How consistent timing is
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "filename": self.filename,
            "duration_seconds": self.duration_seconds,
            "sample_rate": self.sample_rate,
            "tempo_bpm": self.tempo_bpm,
            "tempo_confidence": self.tempo_confidence,
            "beat_count": len(self.beat_positions),
            "energy_stats": {
                "mean": sum(self.energy_curve) / len(self.energy_curve) if self.energy_curve else 0,
                "max": max(self.energy_curve) if self.energy_curve else 0,
            },
            "rms_mean": self.rms_mean,
            "dynamic_range_db": self.dynamic_range_db,
            "spectral_centroid": self.spectral_centroid_mean,
            "swing_estimate": self.swing_estimate,
            "groove_regularity": self.groove_regularity,
        }


def analyze_feel(
    audio_path: str,
    hop_length: int = 512,
) -> AudioFeatures:
    """
    Analyze feel and groove characteristics of an audio file.
    
    Args:
        audio_path: Path to audio file (wav, mp3, etc.)
        hop_length: Analysis hop length in samples
    
    Returns:
        AudioFeatures with extracted characteristics
    """
    if not LIBROSA_AVAILABLE:
        raise ImportError(
            "librosa package required for audio analysis. "
            "Install with: pip install librosa"
        )
    
    if not NUMPY_AVAILABLE:
        raise ImportError("numpy package required")
    
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Load audio
    y, sr = librosa.load(str(audio_path), sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    
    # Tempo and beat tracking
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop_length)
    
    # Tempo confidence (based on onset strength correlation)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    tempo_confidence = _estimate_tempo_confidence(onset_env, tempo, sr, hop_length)
    
    # Energy analysis (RMS)
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    
    # Per-beat energy
    energy_curve = []
    for i, beat_frame in enumerate(beat_frames[:-1]):
        next_beat_frame = beat_frames[i + 1]
        beat_rms = np.mean(rms[beat_frame:next_beat_frame])
        energy_curve.append(float(beat_rms))
    
    # Dynamic range
    rms_db = librosa.amplitude_to_db(rms)
    dynamic_range = float(np.max(rms_db) - np.min(rms_db[rms_db > -60]))  # Ignore silence
    
    # Spectral features
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=hop_length)[0]
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, hop_length=hop_length)[0]
    
    # Swing estimation (based on inter-onset intervals)
    swing_estimate = _estimate_swing(beat_times)
    
    # Groove regularity (how consistent beat intervals are)
    groove_regularity = _estimate_groove_regularity(beat_times)
    
    return AudioFeatures(
        filename=str(audio_path),
        duration_seconds=duration,
        sample_rate=sr,
        tempo_bpm=float(tempo),
        tempo_confidence=tempo_confidence,
        beat_positions=beat_times.tolist(),
        energy_curve=energy_curve,
        rms_mean=float(np.mean(rms)),
        rms_std=float(np.std(rms)),
        dynamic_range_db=dynamic_range,
        spectral_centroid_mean=float(np.mean(spectral_centroid)),
        spectral_rolloff_mean=float(np.mean(spectral_rolloff)),
        spectral_bandwidth_mean=float(np.mean(spectral_bandwidth)),
        swing_estimate=swing_estimate,
        groove_regularity=groove_regularity,
    )


def _estimate_tempo_confidence(
    onset_env: np.ndarray,
    tempo: float,
    sr: int,
    hop_length: int,
) -> float:
    """
    Estimate confidence in tempo detection.
    
    Based on autocorrelation peak strength.
    """
    # Calculate autocorrelation
    autocorr = np.correlate(onset_env, onset_env, mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    
    # Find lag corresponding to detected tempo
    frames_per_beat = (60.0 / tempo) * sr / hop_length
    tempo_lag = int(frames_per_beat)
    
    if tempo_lag >= len(autocorr):
        return 0.5
    
    # Confidence is ratio of tempo peak to first peak
    peak_value = autocorr[tempo_lag]
    max_value = np.max(autocorr[1:])  # Exclude lag 0
    
    confidence = min(1.0, peak_value / max_value) if max_value > 0 else 0.5
    return float(confidence)


def _estimate_swing(beat_times: np.ndarray) -> float:
    """
    Estimate swing amount from beat times.
    
    Swing manifests as alternating long/short beat intervals.
    Returns 0.0 (straight) to 1.0 (heavy swing).
    """
    if len(beat_times) < 4:
        return 0.0
    
    # Calculate inter-beat intervals
    intervals = np.diff(beat_times)
    
    if len(intervals) < 2:
        return 0.0
    
    # Look for alternating pattern
    even_intervals = intervals[0::2]
    odd_intervals = intervals[1::2]
    
    min_len = min(len(even_intervals), len(odd_intervals))
    if min_len < 2:
        return 0.0
    
    even_mean = np.mean(even_intervals[:min_len])
    odd_mean = np.mean(odd_intervals[:min_len])
    
    if even_mean == 0:
        return 0.0
    
    # Swing ratio
    ratio = odd_mean / even_mean
    
    # Convert to 0-1 scale
    # ratio = 1.0 -> no swing (0.0)
    # ratio = 0.67 (triplet) -> heavy swing (1.0)
    swing = max(0.0, min(1.0, (1.0 - ratio) * 3))
    
    return float(swing)


def _estimate_groove_regularity(beat_times: np.ndarray) -> float:
    """
    Estimate how regular/consistent the groove is.
    
    Returns 0.0 (very irregular) to 1.0 (perfectly regular).
    """
    if len(beat_times) < 3:
        return 1.0
    
    intervals = np.diff(beat_times)
    
    if len(intervals) < 2:
        return 1.0
    
    # Calculate coefficient of variation
    mean_interval = np.mean(intervals)
    std_interval = np.std(intervals)
    
    if mean_interval == 0:
        return 1.0
    
    cv = std_interval / mean_interval
    
    # Convert to regularity score (lower CV = more regular)
    # CV of 0 = perfect regularity (1.0)
    # CV of 0.2+ = very irregular (0.0)
    regularity = max(0.0, 1.0 - cv * 5)
    
    return float(regularity)


def compare_feel(audio_path1: str, audio_path2: str) -> Dict:
    """
    Compare feel characteristics of two audio files.
    
    Returns similarity metrics.
    """
    features1 = analyze_feel(audio_path1)
    features2 = analyze_feel(audio_path2)
    
    # Calculate similarities
    tempo_diff = abs(features1.tempo_bpm - features2.tempo_bpm)
    tempo_similarity = max(0, 1 - tempo_diff / 20)  # 20 BPM diff = 0 similarity
    
    swing_diff = abs(features1.swing_estimate - features2.swing_estimate)
    swing_similarity = 1 - swing_diff
    
    energy_similarity = 1 - abs(features1.rms_mean - features2.rms_mean) / max(features1.rms_mean, features2.rms_mean, 0.001)
    
    brightness_diff = abs(features1.spectral_centroid_mean - features2.spectral_centroid_mean)
    brightness_similarity = max(0, 1 - brightness_diff / 2000)
    
    overall = (tempo_similarity + swing_similarity + energy_similarity + brightness_similarity) / 4
    
    return {
        "overall_similarity": overall,
        "tempo_similarity": tempo_similarity,
        "swing_similarity": swing_similarity,
        "energy_similarity": energy_similarity,
        "brightness_similarity": brightness_similarity,
        "file1": features1.to_dict(),
        "file2": features2.to_dict(),
    }
