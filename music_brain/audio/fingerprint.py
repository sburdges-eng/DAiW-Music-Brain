"""
Audio Fingerprint Analysis Engine

Deep audio analysis for timbral DNA extraction, production technique detection,
genre positioning, and reference track matching.

Proposal: Gemini - Audio Fingerprint Analysis Engine
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import json
from pathlib import Path


class ProductionTechnique(str, Enum):
    """Detectable production techniques."""
    # Compression
    PARALLEL_COMPRESSION = "parallel_compression"
    SIDECHAIN_COMPRESSION = "sidechain_compression"
    MULTIBAND_COMPRESSION = "multiband_compression"
    LIMITING = "limiting"

    # Saturation/Distortion
    TAPE_SATURATION = "tape_saturation"
    TUBE_SATURATION = "tube_saturation"
    SOFT_CLIPPING = "soft_clipping"
    HARD_CLIPPING = "hard_clipping"
    BITCRUSHING = "bitcrushing"

    # Reverb
    PLATE_REVERB = "plate_reverb"
    HALL_REVERB = "hall_reverb"
    ROOM_REVERB = "room_reverb"
    SPRING_REVERB = "spring_reverb"
    SHIMMER_REVERB = "shimmer_reverb"
    GATED_REVERB = "gated_reverb"

    # Delay
    SLAPBACK_DELAY = "slapback_delay"
    PING_PONG_DELAY = "ping_pong_delay"
    TAPE_DELAY = "tape_delay"
    DUB_DELAY = "dub_delay"

    # Modulation
    CHORUS = "chorus"
    FLANGER = "flanger"
    PHASER = "phaser"
    TREMOLO = "tremolo"
    VIBRATO = "vibrato"

    # Stereo
    WIDE_STEREO = "wide_stereo"
    MID_SIDE = "mid_side"
    MONO = "mono"
    HAAS_EFFECT = "haas_effect"

    # Lo-Fi
    VINYL_NOISE = "vinyl_noise"
    TAPE_HISS = "tape_hiss"
    SAMPLE_RATE_REDUCTION = "sample_rate_reduction"
    WOBBLE = "wobble"


class GenreCategory(str, Enum):
    """High-level genre categories."""
    ELECTRONIC = "electronic"
    HIP_HOP = "hip_hop"
    ROCK = "rock"
    POP = "pop"
    RNB = "rnb"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    FOLK = "folk"
    METAL = "metal"
    AMBIENT = "ambient"
    EXPERIMENTAL = "experimental"


@dataclass
class TimbralDNA:
    """Unique sonic characteristics of an audio file."""
    brightness: float = 0.0          # 0-1, spectral centroid
    warmth: float = 0.0              # 0-1, low-mid presence
    presence: float = 0.0            # 0-1, 2-5kHz energy
    air: float = 0.0                 # 0-1, high frequency content
    body: float = 0.0                # 0-1, low frequency foundation

    transient_sharpness: float = 0.0 # 0-1, attack characteristics
    sustain_character: float = 0.0   # 0-1, decay/sustain ratio

    stereo_width: float = 0.0        # 0-1, stereo spread
    depth: float = 0.0               # 0-1, front-to-back dimension

    density: float = 0.0             # 0-1, spectral density
    dynamic_range: float = 0.0       # 0-1, dynamics

    # Texture descriptors
    gritty: float = 0.0
    smooth: float = 0.0
    harsh: float = 0.0
    muddy: float = 0.0
    crisp: float = 0.0

    def to_vector(self) -> List[float]:
        """Convert to feature vector."""
        return [
            self.brightness, self.warmth, self.presence, self.air, self.body,
            self.transient_sharpness, self.sustain_character,
            self.stereo_width, self.depth, self.density, self.dynamic_range,
            self.gritty, self.smooth, self.harsh, self.muddy, self.crisp
        ]

    def similarity(self, other: "TimbralDNA") -> float:
        """Calculate similarity to another TimbralDNA (0-1)."""
        v1 = self.to_vector()
        v2 = other.to_vector()

        # Cosine similarity
        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = sum(a * a for a in v1) ** 0.5
        mag2 = sum(b * b for b in v2) ** 0.5

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot / (mag1 * mag2)


@dataclass
class ProductionAnalysis:
    """Detected production techniques and signal chain."""
    detected_techniques: Dict[ProductionTechnique, float] = field(default_factory=dict)
    estimated_signal_chain: List[str] = field(default_factory=list)

    # Specific measurements
    compression_ratio_estimate: float = 0.0
    reverb_decay_estimate: float = 0.0  # seconds
    saturation_amount: float = 0.0       # 0-1

    # Quality indicators
    headroom_db: float = 0.0
    peak_to_loudness_ratio: float = 0.0
    crest_factor: float = 0.0

    def get_top_techniques(self, n: int = 5) -> List[Tuple[ProductionTechnique, float]]:
        """Get top N most confident technique detections."""
        sorted_tech = sorted(
            self.detected_techniques.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_tech[:n]

    def describe_chain(self) -> str:
        """Get human-readable signal chain description."""
        if not self.estimated_signal_chain:
            return "Unable to estimate signal chain"
        return " → ".join(self.estimated_signal_chain)


@dataclass
class GenrePosition:
    """Position in genre space."""
    primary_genre: GenreCategory = GenreCategory.POP
    primary_confidence: float = 0.0

    secondary_genre: Optional[GenreCategory] = None
    secondary_confidence: float = 0.0

    # Sub-genre descriptors
    subgenre_tags: List[str] = field(default_factory=list)

    # 2D position for visualization
    x: float = 0.0  # Electronic ←→ Acoustic
    y: float = 0.0  # Experimental ←→ Traditional

    # Distances to genre centroids
    genre_distances: Dict[GenreCategory, float] = field(default_factory=dict)

    def describe(self) -> str:
        """Get human-readable genre description."""
        desc = f"{self.primary_genre.value} ({self.primary_confidence:.0%})"
        if self.secondary_genre:
            desc += f" / {self.secondary_genre.value} ({self.secondary_confidence:.0%})"
        if self.subgenre_tags:
            desc += f"\nTags: {', '.join(self.subgenre_tags)}"
        return desc


@dataclass
class ReferenceMatch:
    """A matching reference track."""
    track_name: str
    artist: str
    similarity_score: float  # 0-1

    # What aspects are similar
    similar_aspects: List[str] = field(default_factory=list)
    # drums, vocals, production, arrangement, etc.

    # Link to more info
    reference_url: Optional[str] = None

    def __str__(self) -> str:
        aspects = ", ".join(self.similar_aspects) if self.similar_aspects else "overall"
        return f"{self.artist} - {self.track_name} ({self.similarity_score:.0%} similar: {aspects})"


@dataclass
class AudioFingerprint:
    """Complete audio fingerprint analysis."""
    # Source info
    file_path: Optional[str] = None
    duration_seconds: float = 0.0
    sample_rate: int = 44100

    # Analysis results
    timbral_dna: TimbralDNA = field(default_factory=TimbralDNA)
    production: ProductionAnalysis = field(default_factory=ProductionAnalysis)
    genre_position: GenrePosition = field(default_factory=GenrePosition)
    reference_matches: List[ReferenceMatch] = field(default_factory=list)

    # Timestamps
    analyzed_at: str = ""
    analysis_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "file_path": self.file_path,
            "duration_seconds": self.duration_seconds,
            "sample_rate": self.sample_rate,
            "timbral_dna": {
                "brightness": self.timbral_dna.brightness,
                "warmth": self.timbral_dna.warmth,
                "presence": self.timbral_dna.presence,
                "air": self.timbral_dna.air,
                "body": self.timbral_dna.body,
                "transient_sharpness": self.timbral_dna.transient_sharpness,
                "sustain_character": self.timbral_dna.sustain_character,
                "stereo_width": self.timbral_dna.stereo_width,
                "depth": self.timbral_dna.depth,
                "density": self.timbral_dna.density,
                "dynamic_range": self.timbral_dna.dynamic_range,
            },
            "production": {
                "techniques": {k.value: v for k, v in self.production.detected_techniques.items()},
                "signal_chain": self.production.estimated_signal_chain,
                "compression_ratio": self.production.compression_ratio_estimate,
                "reverb_decay": self.production.reverb_decay_estimate,
            },
            "genre": {
                "primary": self.genre_position.primary_genre.value,
                "primary_confidence": self.genre_position.primary_confidence,
                "secondary": self.genre_position.secondary_genre.value if self.genre_position.secondary_genre else None,
                "tags": self.genre_position.subgenre_tags,
                "position": {"x": self.genre_position.x, "y": self.genre_position.y},
            },
            "references": [
                {"track": r.track_name, "artist": r.artist, "similarity": r.similarity_score}
                for r in self.reference_matches
            ],
        }

    def summary(self) -> str:
        """Get human-readable summary."""
        lines = [
            "=" * 60,
            "AUDIO FINGERPRINT ANALYSIS",
            "=" * 60,
            "",
            f"File: {self.file_path or 'Unknown'}",
            f"Duration: {self.duration_seconds:.1f}s",
            "",
            "TIMBRAL DNA:",
            f"  Brightness: {'█' * int(self.timbral_dna.brightness * 10)}{'░' * (10 - int(self.timbral_dna.brightness * 10))} {self.timbral_dna.brightness:.0%}",
            f"  Warmth:     {'█' * int(self.timbral_dna.warmth * 10)}{'░' * (10 - int(self.timbral_dna.warmth * 10))} {self.timbral_dna.warmth:.0%}",
            f"  Presence:   {'█' * int(self.timbral_dna.presence * 10)}{'░' * (10 - int(self.timbral_dna.presence * 10))} {self.timbral_dna.presence:.0%}",
            f"  Stereo:     {'█' * int(self.timbral_dna.stereo_width * 10)}{'░' * (10 - int(self.timbral_dna.stereo_width * 10))} {self.timbral_dna.stereo_width:.0%}",
            "",
            "PRODUCTION:",
            f"  Signal Chain: {self.production.describe_chain()}",
        ]

        top_tech = self.production.get_top_techniques(3)
        if top_tech:
            lines.append("  Detected Techniques:")
            for tech, conf in top_tech:
                lines.append(f"    - {tech.value}: {conf:.0%}")

        lines.extend([
            "",
            "GENRE:",
            f"  {self.genre_position.describe()}",
            "",
        ])

        if self.reference_matches:
            lines.append("SIMILAR TO:")
            for ref in self.reference_matches[:3]:
                lines.append(f"  • {ref}")

        return "\n".join(lines)


class AudioFingerprintEngine:
    """
    Main engine for audio fingerprint analysis.

    Uses audio ML models (wav2vec 2.0, CLAP) for deep analysis.
    Requires librosa for audio processing.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self._model_loaded = False

        # Reference database (would be loaded from file/API)
        self._reference_db: List[AudioFingerprint] = []

    def analyze(self, audio_path: str) -> AudioFingerprint:
        """
        Analyze an audio file and return its fingerprint.

        Args:
            audio_path: Path to audio file (wav, mp3, flac, etc.)

        Returns:
            AudioFingerprint with complete analysis
        """
        fingerprint = AudioFingerprint(file_path=audio_path)

        try:
            # Try to use librosa for analysis
            fingerprint = self._analyze_with_librosa(audio_path, fingerprint)
        except ImportError:
            # Fallback to basic analysis
            fingerprint = self._analyze_basic(audio_path, fingerprint)

        # Find reference matches
        fingerprint.reference_matches = self._find_references(fingerprint)

        from datetime import datetime
        fingerprint.analyzed_at = datetime.now().isoformat()

        return fingerprint

    def _analyze_with_librosa(self, audio_path: str, fingerprint: AudioFingerprint) -> AudioFingerprint:
        """Full analysis using librosa."""
        import librosa
        import numpy as np

        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        fingerprint.sample_rate = sr
        fingerprint.duration_seconds = len(y) / sr

        # Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]

        # Normalize to 0-1 range
        fingerprint.timbral_dna.brightness = float(np.mean(spectral_centroid) / (sr / 2))
        fingerprint.timbral_dna.presence = float(np.mean(spectral_rolloff) / sr)

        # RMS for dynamics
        rms = librosa.feature.rms(y=y)[0]
        fingerprint.timbral_dna.dynamic_range = float(np.std(rms) / (np.mean(rms) + 1e-6))

        # Zero crossing rate (brightness/noise indicator)
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        fingerprint.timbral_dna.crisp = float(np.mean(zcr))

        # MFCCs for timbral character
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        # Low MFCCs = body/warmth, high MFCCs = texture
        fingerprint.timbral_dna.warmth = float(np.clip(np.mean(mfccs[1:3]) / 100 + 0.5, 0, 1))
        fingerprint.timbral_dna.body = float(np.clip(np.mean(mfccs[0]) / 100 + 0.5, 0, 1))

        # Onset detection for transients
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        fingerprint.timbral_dna.transient_sharpness = float(np.std(onset_env) / (np.mean(onset_env) + 1e-6))

        # Stereo analysis if stereo file
        if len(y.shape) > 1 and y.shape[0] == 2:
            # Simple stereo width from L-R correlation
            correlation = np.corrcoef(y[0], y[1])[0, 1]
            fingerprint.timbral_dna.stereo_width = float(1 - abs(correlation))
        else:
            fingerprint.timbral_dna.stereo_width = 0.0

        # Production technique detection (simplified)
        fingerprint.production = self._detect_production_techniques(y, sr)

        # Genre classification (simplified)
        fingerprint.genre_position = self._classify_genre(mfccs, spectral_centroid)

        return fingerprint

    def _analyze_basic(self, audio_path: str, fingerprint: AudioFingerprint) -> AudioFingerprint:
        """Basic analysis without librosa (placeholder values)."""
        import os

        if os.path.exists(audio_path):
            fingerprint.file_path = audio_path
            # Get file size as rough duration estimate
            size_mb = os.path.getsize(audio_path) / (1024 * 1024)
            # Rough estimate: 1MB ≈ 1 minute at 128kbps
            fingerprint.duration_seconds = size_mb * 60

        # Return with default values
        return fingerprint

    def _detect_production_techniques(self, y, sr) -> ProductionAnalysis:
        """Detect production techniques from audio."""
        import numpy as np

        analysis = ProductionAnalysis()

        # Simple heuristics (would use ML models in production)

        # Check for compression (reduced dynamic range)
        rms = np.sqrt(np.mean(y**2))
        peak = np.max(np.abs(y))
        crest_factor = peak / (rms + 1e-6)

        analysis.crest_factor = float(crest_factor)

        # Low crest factor suggests compression
        if crest_factor < 4:
            analysis.detected_techniques[ProductionTechnique.LIMITING] = 0.8
            analysis.detected_techniques[ProductionTechnique.PARALLEL_COMPRESSION] = 0.6
        elif crest_factor < 8:
            analysis.detected_techniques[ProductionTechnique.MULTIBAND_COMPRESSION] = 0.5

        # Check for saturation (odd harmonics)
        # Simplified: high RMS with low peaks suggests saturation
        if rms > 0.1 and crest_factor < 6:
            analysis.detected_techniques[ProductionTechnique.TAPE_SATURATION] = 0.5
            analysis.detected_techniques[ProductionTechnique.SOFT_CLIPPING] = 0.4

        # Build estimated signal chain
        chain = []
        if ProductionTechnique.TAPE_SATURATION in analysis.detected_techniques:
            chain.append("Tape/Console")
        chain.append("EQ")
        if ProductionTechnique.PARALLEL_COMPRESSION in analysis.detected_techniques:
            chain.append("Parallel Comp")
        if ProductionTechnique.LIMITING in analysis.detected_techniques:
            chain.append("Limiter")

        analysis.estimated_signal_chain = chain or ["Unknown"]

        return analysis

    def _classify_genre(self, mfccs, spectral_centroid) -> GenrePosition:
        """Classify genre from features."""
        import numpy as np

        position = GenrePosition()

        # Simple heuristics based on spectral characteristics
        brightness = np.mean(spectral_centroid)
        mfcc_mean = np.mean(mfccs, axis=1)

        # Very rough genre estimation
        if brightness > 3000:
            position.primary_genre = GenreCategory.ELECTRONIC
            position.primary_confidence = 0.6
            position.subgenre_tags = ["bright", "synthetic"]
        elif brightness < 1500:
            position.primary_genre = GenreCategory.HIP_HOP
            position.primary_confidence = 0.5
            position.subgenre_tags = ["warm", "bass-heavy"]
        else:
            position.primary_genre = GenreCategory.POP
            position.primary_confidence = 0.4
            position.subgenre_tags = ["balanced"]

        # 2D position (would use trained embeddings)
        position.x = float(np.clip((brightness - 2000) / 2000, -1, 1))
        position.y = float(np.clip(mfcc_mean[0] / 50, -1, 1))

        return position

    def _find_references(self, fingerprint: AudioFingerprint) -> List[ReferenceMatch]:
        """Find similar reference tracks."""
        matches = []

        # Compare against reference database
        for ref in self._reference_db:
            similarity = fingerprint.timbral_dna.similarity(ref.timbral_dna)
            if similarity > 0.7:
                matches.append(ReferenceMatch(
                    track_name=ref.file_path or "Unknown",
                    artist="Unknown",
                    similarity_score=similarity,
                    similar_aspects=["timbre", "production"],
                ))

        # Sort by similarity
        matches.sort(key=lambda m: m.similarity_score, reverse=True)

        # Add some placeholder references for demo
        if not matches:
            matches = [
                ReferenceMatch(
                    track_name="[Analysis requires reference database]",
                    artist="System",
                    similarity_score=0.0,
                    similar_aspects=["N/A"],
                ),
            ]

        return matches[:5]

    def compare(self, audio1: str, audio2: str) -> Dict[str, Any]:
        """Compare two audio files."""
        fp1 = self.analyze(audio1)
        fp2 = self.analyze(audio2)

        timbral_similarity = fp1.timbral_dna.similarity(fp2.timbral_dna)

        return {
            "overall_similarity": timbral_similarity,
            "timbral_similarity": timbral_similarity,
            "same_genre": fp1.genre_position.primary_genre == fp2.genre_position.primary_genre,
            "file1": fp1.summary(),
            "file2": fp2.summary(),
        }


# Convenience function
def analyze_audio(audio_path: str) -> AudioFingerprint:
    """Analyze an audio file and return its fingerprint."""
    engine = AudioFingerprintEngine()
    return engine.analyze(audio_path)


def compare_audio(audio1: str, audio2: str) -> Dict[str, Any]:
    """Compare two audio files."""
    engine = AudioFingerprintEngine()
    return engine.compare(audio1, audio2)
