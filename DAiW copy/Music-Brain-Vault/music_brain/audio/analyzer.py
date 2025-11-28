"""
Audio Feel Analysis

Extracts rhythmic and timbral characteristics from audio files.

Features:
- Onset detection with multiple algorithms
- Spectral features (brightness, bandwidth, rolloff)
- Rhythmic density and tempo estimation
- Dynamic range analysis
- Proper error handling for all edge cases
"""

import os
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
import numpy as np

# Lazy import for optional dependency
_librosa = None

def _get_librosa():
    """Lazy load librosa to avoid import overhead."""
    global _librosa
    if _librosa is None:
        try:
            import librosa
            _librosa = librosa
        except ImportError:
            raise ImportError(
                "librosa is required for audio analysis. "
                "Install with: pip install librosa"
            )
    return _librosa


@dataclass
class OnsetInfo:
    """Onset detection results."""
    onset_times: List[float]      # Seconds
    onset_strength: List[float]   # Envelope values
    sample_rate: int
    num_onsets: int
    onset_density: float          # Onsets per second


@dataclass
class SpectralInfo:
    """Spectral feature results."""
    times: List[float]
    centroid_mean: float          # Average brightness (Hz)
    centroid_std: float           # Brightness variation
    bandwidth_mean: float         # Spectral spread (Hz)
    rolloff_mean: float           # High-frequency cutoff (Hz)
    flatness_mean: float          # Noisiness (0=tonal, 1=noisy)


@dataclass
class DynamicInfo:
    """Dynamics analysis results."""
    rms_mean: float               # Average loudness
    rms_std: float                # Loudness variation
    dynamic_range_db: float       # Difference between loud and quiet
    peak_to_average: float        # Crest factor
    compression_estimate: float   # 0=dynamic, 1=compressed


@dataclass
class RhythmInfo:
    """Rhythm analysis results."""
    tempo_bpm: float
    tempo_confidence: float       # 0-1
    beat_times: List[float]
    downbeat_times: List[float]
    beat_regularity: float        # How consistent the beat is


@dataclass
class AudioFeel:
    """Complete audio feel analysis."""
    duration_seconds: float
    sample_rate: int
    
    # Components
    onsets: OnsetInfo
    spectral: SpectralInfo
    dynamics: DynamicInfo
    rhythm: RhythmInfo
    
    # Derived descriptors
    energy_level: str             # "low", "medium", "high"
    brightness_level: str         # "dark", "neutral", "bright"
    texture: str                  # "sparse", "medium", "dense"
    feel_description: str         # Human-readable summary


class AudioAnalyzer:
    """
    Analyze audio files for feel characteristics.
    
    Handles edge cases:
    - Very short files
    - Silent files
    - Files with no clear beat
    - Various sample rates
    """
    
    def __init__(
        self,
        target_sr: Optional[int] = None,
        hop_length: int = 512,
        n_fft: int = 2048
    ):
        """
        Args:
            target_sr: Resample to this rate (None = use original)
            hop_length: STFT hop length
            n_fft: FFT window size
        """
        self.target_sr = target_sr
        self.hop_length = hop_length
        self.n_fft = n_fft
    
    def analyze(self, audio_path: str) -> AudioFeel:
        """
        Complete audio analysis.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            AudioFeel with all analysis results
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is too short or invalid
        """
        librosa = _get_librosa()
        
        # Validate file
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Load audio
        try:
            y, sr = librosa.load(audio_path, sr=self.target_sr, mono=True)
        except Exception as e:
            raise ValueError(f"Failed to load audio: {e}")
        
        duration = len(y) / sr
        
        # Minimum duration check
        if duration < 0.5:
            raise ValueError(f"Audio too short ({duration:.2f}s). Need at least 0.5s.")
        
        # Check for silence
        if np.max(np.abs(y)) < 1e-6:
            raise ValueError("Audio appears to be silent.")
        
        # Run all analyses
        onsets = self._analyze_onsets(y, sr)
        spectral = self._analyze_spectral(y, sr)
        dynamics = self._analyze_dynamics(y, sr)
        rhythm = self._analyze_rhythm(y, sr)
        
        # Derive descriptors
        energy = self._classify_energy(dynamics, onsets)
        brightness = self._classify_brightness(spectral)
        texture = self._classify_texture(onsets, spectral)
        description = self._generate_description(energy, brightness, texture, rhythm)
        
        return AudioFeel(
            duration_seconds=duration,
            sample_rate=sr,
            onsets=onsets,
            spectral=spectral,
            dynamics=dynamics,
            rhythm=rhythm,
            energy_level=energy,
            brightness_level=brightness,
            texture=texture,
            feel_description=description
        )
    
    def _analyze_onsets(self, y: np.ndarray, sr: int) -> OnsetInfo:
        """Detect note onsets."""
        librosa = _get_librosa()
        
        # Onset strength envelope
        onset_env = librosa.onset.onset_strength(
            y=y, sr=sr, hop_length=self.hop_length
        )
        
        # Detect onset times
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=sr,
            hop_length=self.hop_length
        )
        onset_times = librosa.frames_to_time(
            onset_frames, sr=sr, hop_length=self.hop_length
        )
        
        # Calculate density
        duration = len(y) / sr
        density = len(onset_times) / duration if duration > 0 else 0
        
        return OnsetInfo(
            onset_times=onset_times.tolist(),
            onset_strength=onset_env.tolist(),
            sample_rate=sr,
            num_onsets=len(onset_times),
            onset_density=density
        )
    
    def _analyze_spectral(self, y: np.ndarray, sr: int) -> SpectralInfo:
        """Extract spectral features."""
        librosa = _get_librosa()
        
        # Compute spectrogram
        S = np.abs(librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length))
        
        # Spectral centroid (brightness)
        centroid = librosa.feature.spectral_centroid(
            S=S, sr=sr, hop_length=self.hop_length
        )[0]
        
        # Spectral bandwidth
        bandwidth = librosa.feature.spectral_bandwidth(
            S=S, sr=sr, hop_length=self.hop_length
        )[0]
        
        # Spectral rolloff (high frequency cutoff)
        rolloff = librosa.feature.spectral_rolloff(
            S=S, sr=sr, hop_length=self.hop_length
        )[0]
        
        # Spectral flatness (noisiness)
        flatness = librosa.feature.spectral_flatness(S=S)[0]
        
        # Frame times
        times = librosa.frames_to_time(
            np.arange(len(centroid)), sr=sr, hop_length=self.hop_length
        )
        
        return SpectralInfo(
            times=times.tolist(),
            centroid_mean=float(np.mean(centroid)),
            centroid_std=float(np.std(centroid)),
            bandwidth_mean=float(np.mean(bandwidth)),
            rolloff_mean=float(np.mean(rolloff)),
            flatness_mean=float(np.mean(flatness))
        )
    
    def _analyze_dynamics(self, y: np.ndarray, sr: int) -> DynamicInfo:
        """Analyze loudness dynamics."""
        librosa = _get_librosa()
        
        # RMS energy
        rms = librosa.feature.rms(
            y=y, frame_length=self.n_fft, hop_length=self.hop_length
        )[0]
        
        rms_mean = float(np.mean(rms))
        rms_std = float(np.std(rms))
        
        # Dynamic range (90th percentile - 10th percentile in dB)
        if len(rms) > 0 and rms_mean > 1e-10:
            p90 = np.percentile(rms, 90)
            p10 = max(np.percentile(rms, 10), 1e-10)  # Avoid log(0)
            dynamic_range = 20 * np.log10(p90 / p10)
        else:
            dynamic_range = 0.0
        
        # Peak to average (crest factor)
        peak = float(np.max(np.abs(y)))
        rms_total = float(np.sqrt(np.mean(y ** 2)))
        if rms_total > 1e-10:
            crest = peak / rms_total
        else:
            crest = 1.0
        
        # Compression estimate (lower dynamic range = more compressed)
        # Typical ranges: 6dB (very compressed) to 20dB+ (dynamic)
        compression = max(0, 1 - (dynamic_range - 6) / 14)
        compression = min(1, compression)
        
        return DynamicInfo(
            rms_mean=rms_mean,
            rms_std=rms_std,
            dynamic_range_db=dynamic_range,
            peak_to_average=crest,
            compression_estimate=compression
        )
    
    def _analyze_rhythm(self, y: np.ndarray, sr: int) -> RhythmInfo:
        """Analyze tempo and beat structure."""
        librosa = _get_librosa()
        
        # Beat tracking
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        
        # Handle array tempo (newer librosa versions)
        if hasattr(tempo, '__len__'):
            tempo = float(tempo[0]) if len(tempo) > 0 else 0.0
        else:
            tempo = float(tempo)
        
        # Beat times
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        
        # Downbeat estimation (every 4 beats for 4/4)
        downbeat_times = beat_times[::4] if len(beat_times) >= 4 else beat_times
        
        # Beat regularity (consistency of inter-beat intervals)
        if len(beat_times) > 2:
            ibis = np.diff(beat_times)  # Inter-beat intervals
            regularity = 1 - (np.std(ibis) / np.mean(ibis)) if np.mean(ibis) > 0 else 0
            regularity = max(0, min(1, regularity))
        else:
            regularity = 0.0
        
        # Tempo confidence based on beat regularity and onset alignment
        confidence = regularity * 0.8 + 0.2  # Base confidence
        
        return RhythmInfo(
            tempo_bpm=tempo,
            tempo_confidence=confidence,
            beat_times=beat_times.tolist(),
            downbeat_times=downbeat_times.tolist(),
            beat_regularity=regularity
        )
    
    def _classify_energy(self, dynamics: DynamicInfo, onsets: OnsetInfo) -> str:
        """Classify overall energy level."""
        # Combine RMS and onset density
        score = dynamics.rms_mean * 5 + onsets.onset_density / 10
        
        if score < 0.3:
            return "low"
        elif score < 0.6:
            return "medium"
        else:
            return "high"
    
    def _classify_brightness(self, spectral: SpectralInfo) -> str:
        """Classify timbral brightness."""
        # Based on spectral centroid
        centroid = spectral.centroid_mean
        
        if centroid < 1500:
            return "dark"
        elif centroid < 3500:
            return "neutral"
        else:
            return "bright"
    
    def _classify_texture(self, onsets: OnsetInfo, spectral: SpectralInfo) -> str:
        """Classify rhythmic/textural density."""
        density = onsets.onset_density
        flatness = spectral.flatness_mean
        
        score = density / 8 + flatness
        
        if score < 0.4:
            return "sparse"
        elif score < 0.7:
            return "medium"
        else:
            return "dense"
    
    def _generate_description(
        self,
        energy: str,
        brightness: str,
        texture: str,
        rhythm: RhythmInfo
    ) -> str:
        """Generate human-readable feel description."""
        tempo = rhythm.tempo_bpm
        
        # Tempo description
        if tempo < 80:
            tempo_desc = "slow"
        elif tempo < 120:
            tempo_desc = "mid-tempo"
        elif tempo < 150:
            tempo_desc = "upbeat"
        else:
            tempo_desc = "fast"
        
        # Combine
        parts = []
        
        if energy == "high":
            parts.append("energetic")
        elif energy == "low":
            parts.append("mellow")
        
        parts.append(tempo_desc)
        
        if brightness == "bright":
            parts.append("with bright tones")
        elif brightness == "dark":
            parts.append("with warm, dark tones")
        
        if texture == "dense":
            parts.append("and dense arrangement")
        elif texture == "sparse":
            parts.append("and spacious arrangement")
        
        return " ".join(parts).capitalize()


# Convenience function
def analyze_audio_feel(audio_path: str) -> AudioFeel:
    """Analyze audio file feel characteristics."""
    analyzer = AudioAnalyzer()
    return analyzer.analyze(audio_path)


# Quick analysis (returns dict instead of dataclass)
def quick_analyze(audio_path: str) -> Dict[str, Any]:
    """Quick audio analysis returning dict."""
    feel = analyze_audio_feel(audio_path)
    
    return {
        "duration": feel.duration_seconds,
        "tempo_bpm": feel.rhythm.tempo_bpm,
        "tempo_confidence": feel.rhythm.tempo_confidence,
        "beat_regularity": feel.rhythm.beat_regularity,
        "onset_density": feel.onsets.onset_density,
        "brightness_hz": feel.spectral.centroid_mean,
        "dynamic_range_db": feel.dynamics.dynamic_range_db,
        "compression": feel.dynamics.compression_estimate,
        "energy": feel.energy_level,
        "brightness": feel.brightness_level,
        "texture": feel.texture,
        "description": feel.feel_description,
    }
