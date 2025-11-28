"""
Feel-to-Template Matching

The intelligence layer that connects:
- Audio feel analysis → template selection
- Per-instrument velocity patterns
- Section-aware groove mapping
- Automatic best-match scoring

This is what makes it an assistant, not a randomizer.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import math

from ..utils.ppq import STANDARD_PPQ
from .genre_templates import GENRE_TEMPLATES, POCKET_OFFSETS


class EnergyLevel(Enum):
    """Quantized energy levels."""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


class SwingFeel(Enum):
    """Swing feel categories."""
    STRAIGHT = "straight"      # 0.50
    SUBTLE = "subtle"          # 0.52-0.55
    LIGHT = "light"            # 0.56-0.60
    MEDIUM = "medium"          # 0.61-0.64
    TRIPLET = "triplet"        # 0.65-0.68
    HEAVY = "heavy"            # 0.69+


@dataclass
class FeelProfile:
    """
    Quantified feel characteristics from audio or MIDI.
    
    This is the bridge between analysis and template selection.
    """
    # Tempo
    tempo_bpm: float
    tempo_stability: float = 1.0  # 0-1, how consistent
    
    # Energy
    energy_level: EnergyLevel = EnergyLevel.MEDIUM
    dynamic_range: float = 0.5   # 0-1, compressed to dynamic
    
    # Swing/groove
    swing_feel: SwingFeel = SwingFeel.STRAIGHT
    swing_ratio: float = 0.50
    
    # Density
    note_density: float = 0.5    # 0-1, sparse to dense
    ghost_density: float = 0.1   # Proportion of ghost notes
    
    # Timbre
    brightness: float = 0.5      # 0-1, dark to bright
    
    # Rhythm characteristics
    backbeat_strength: float = 0.5   # How strong 2 and 4 are
    syncopation: float = 0.3         # Off-beat emphasis
    
    # Optional: detected genre hints
    genre_hints: List[str] = field(default_factory=list)
    
    # Source info
    source_file: Optional[str] = None
    source_type: str = "unknown"  # "audio" or "midi"


@dataclass
class InstrumentVelocityPattern:
    """Per-instrument velocity pattern."""
    instrument: str
    
    # 16-position velocity curve (16th notes in a bar)
    velocity_curve: List[int]  # 0-127
    
    # Variation parameters
    velocity_std: List[float]   # Standard deviation per position
    accent_positions: List[int]  # Which positions get accents
    ghost_positions: List[int]   # Which positions are ghost notes
    
    # Dynamics
    base_velocity: int = 80
    accent_boost: int = 20
    ghost_reduction: int = 40


@dataclass
class SectionGrooveMap:
    """Groove parameters for a specific section."""
    section_name: str
    
    # Timing
    swing_ratio: float
    timing_offset: List[float]  # Per-position offset in ticks
    
    # Per-instrument velocities
    instrument_velocities: Dict[str, InstrumentVelocityPattern]
    
    # Per-instrument timing (pocket)
    instrument_pocket: Dict[str, int]  # Offset in ticks
    
    # Section-specific modifiers
    energy_modifier: float = 1.0   # Multiply velocities
    tightness_modifier: float = 1.0  # Reduce timing variation
    
    # Fill behavior
    fill_probability: float = 0.0  # Chance of fill at section end
    fill_intensity: float = 0.5


@dataclass
class TemplateScore:
    """Score for how well a template matches a feel profile."""
    genre: str
    total_score: float  # 0-100
    
    # Component scores
    tempo_score: float
    energy_score: float
    swing_score: float
    density_score: float
    brightness_score: float
    
    # Explanation
    match_reasons: List[str]
    mismatch_reasons: List[str]


# === Per-Instrument Velocity Patterns ===

INSTRUMENT_VELOCITY_PATTERNS: Dict[str, Dict[str, InstrumentVelocityPattern]] = {
    "hiphop": {
        "kick": InstrumentVelocityPattern(
            instrument="kick",
            velocity_curve=[100, 0, 0, 0, 85, 0, 0, 0, 100, 0, 0, 0, 88, 0, 0, 0],
            velocity_std=[5, 0, 0, 0, 8, 0, 0, 0, 5, 0, 0, 0, 8, 0, 0, 0],
            accent_positions=[0, 8],
            ghost_positions=[],
            base_velocity=95,
            accent_boost=10,
        ),
        "snare": InstrumentVelocityPattern(
            instrument="snare",
            velocity_curve=[0, 0, 0, 0, 100, 0, 0, 0, 0, 0, 0, 0, 100, 0, 0, 0],
            velocity_std=[0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0],
            accent_positions=[4, 12],
            ghost_positions=[],
            base_velocity=100,
        ),
        "hihat": InstrumentVelocityPattern(
            instrument="hihat",
            velocity_curve=[75, 55, 65, 50, 78, 58, 68, 52, 75, 55, 65, 50, 78, 58, 68, 52],
            velocity_std=[8, 10, 8, 12, 8, 10, 8, 12, 8, 10, 8, 12, 8, 10, 8, 12],
            accent_positions=[0, 4, 8, 12],
            ghost_positions=[3, 7, 11, 15],
            base_velocity=65,
            accent_boost=15,
            ghost_reduction=25,
        ),
    },
    
    "funk": {
        "kick": InstrumentVelocityPattern(
            instrument="kick",
            velocity_curve=[105, 0, 75, 0, 0, 0, 85, 0, 100, 0, 0, 80, 0, 0, 90, 0],
            velocity_std=[5, 0, 10, 0, 0, 0, 8, 0, 5, 0, 0, 10, 0, 0, 8, 0],
            accent_positions=[0, 8],
            ghost_positions=[],
            base_velocity=90,
            accent_boost=15,
        ),
        "snare": InstrumentVelocityPattern(
            instrument="snare",
            velocity_curve=[0, 0, 45, 0, 105, 0, 50, 0, 0, 0, 48, 0, 105, 0, 52, 0],
            velocity_std=[0, 0, 12, 0, 5, 0, 12, 0, 0, 0, 12, 0, 5, 0, 12, 0],
            accent_positions=[4, 12],
            ghost_positions=[2, 6, 10, 14],
            base_velocity=100,
            ghost_reduction=55,
        ),
        "hihat": InstrumentVelocityPattern(
            instrument="hihat",
            velocity_curve=[85, 60, 75, 58, 88, 62, 78, 60, 85, 60, 75, 58, 88, 62, 78, 60],
            velocity_std=[5, 8, 6, 10, 5, 8, 6, 10, 5, 8, 6, 10, 5, 8, 6, 10],
            accent_positions=[0, 2, 4, 6, 8, 10, 12, 14],
            ghost_positions=[1, 3, 5, 7, 9, 11, 13, 15],
            base_velocity=72,
            accent_boost=15,
            ghost_reduction=18,
        ),
    },
    
    "jazz": {
        "kick": InstrumentVelocityPattern(
            instrument="kick",
            velocity_curve=[70, 0, 0, 55, 0, 0, 65, 0, 72, 0, 0, 58, 0, 0, 68, 0],
            velocity_std=[12, 0, 0, 15, 0, 0, 12, 0, 12, 0, 0, 15, 0, 0, 12, 0],
            accent_positions=[0, 8],
            ghost_positions=[3, 7, 11, 15],
            base_velocity=65,
            accent_boost=10,
            ghost_reduction=15,
        ),
        "snare": InstrumentVelocityPattern(
            instrument="snare",
            velocity_curve=[0, 35, 0, 40, 75, 38, 0, 42, 0, 35, 0, 40, 78, 38, 0, 45],
            velocity_std=[0, 15, 0, 15, 10, 15, 0, 15, 0, 15, 0, 15, 10, 15, 0, 15],
            accent_positions=[4, 12],
            ghost_positions=[1, 3, 5, 7, 9, 11, 13, 15],
            base_velocity=75,
            ghost_reduction=40,
        ),
        "ride": InstrumentVelocityPattern(
            instrument="ride",
            velocity_curve=[80, 50, 70, 48, 78, 52, 72, 50, 80, 50, 70, 48, 78, 52, 72, 50],
            velocity_std=[8, 12, 10, 15, 8, 12, 10, 15, 8, 12, 10, 15, 8, 12, 10, 15],
            accent_positions=[0, 2, 4, 6, 8, 10, 12, 14],
            ghost_positions=[],
            base_velocity=68,
            accent_boost=12,
        ),
    },
    
    "rock": {
        "kick": InstrumentVelocityPattern(
            instrument="kick",
            velocity_curve=[110, 0, 0, 0, 0, 0, 0, 0, 108, 0, 0, 0, 0, 0, 105, 0],
            velocity_std=[5, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 8, 0],
            accent_positions=[0, 8],
            ghost_positions=[],
            base_velocity=108,
            accent_boost=5,
        ),
        "snare": InstrumentVelocityPattern(
            instrument="snare",
            velocity_curve=[0, 0, 0, 0, 115, 0, 0, 0, 0, 0, 0, 0, 115, 0, 0, 0],
            velocity_std=[0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0],
            accent_positions=[4, 12],
            ghost_positions=[],
            base_velocity=115,
        ),
        "hihat": InstrumentVelocityPattern(
            instrument="hihat",
            velocity_curve=[90, 70, 85, 68, 92, 72, 88, 70, 90, 70, 85, 68, 92, 72, 88, 70],
            velocity_std=[5, 8, 5, 8, 5, 8, 5, 8, 5, 8, 5, 8, 5, 8, 5, 8],
            accent_positions=[0, 4, 8, 12],
            ghost_positions=[],
            base_velocity=80,
            accent_boost=12,
        ),
    },
    
    "edm": {
        "kick": InstrumentVelocityPattern(
            instrument="kick",
            velocity_curve=[120, 0, 0, 0, 120, 0, 0, 0, 120, 0, 0, 0, 120, 0, 0, 0],
            velocity_std=[2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0],
            accent_positions=[0, 4, 8, 12],
            ghost_positions=[],
            base_velocity=120,
        ),
        "snare": InstrumentVelocityPattern(
            instrument="snare",
            velocity_curve=[0, 0, 0, 0, 115, 0, 0, 0, 0, 0, 0, 0, 115, 0, 0, 0],
            velocity_std=[0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0],
            accent_positions=[4, 12],
            ghost_positions=[],
            base_velocity=115,
        ),
        "hihat": InstrumentVelocityPattern(
            instrument="hihat",
            velocity_curve=[95, 80, 90, 78, 95, 80, 90, 78, 95, 80, 90, 78, 95, 80, 90, 78],
            velocity_std=[3, 5, 3, 5, 3, 5, 3, 5, 3, 5, 3, 5, 3, 5, 3, 5],
            accent_positions=[0, 2, 4, 6, 8, 10, 12, 14],
            ghost_positions=[],
            base_velocity=85,
            accent_boost=10,
        ),
    },
}


# === Section-Aware Groove Maps ===

SECTION_MODIFIERS: Dict[str, Dict[str, float]] = {
    # Section name → modifiers
    "intro": {
        "energy": 0.7,
        "tightness": 0.9,
        "fill_probability": 0.1,
        "swing_adjust": 0.0,
    },
    "verse": {
        "energy": 0.85,
        "tightness": 1.0,
        "fill_probability": 0.15,
        "swing_adjust": 0.0,
    },
    "pre_chorus": {
        "energy": 0.95,
        "tightness": 0.95,
        "fill_probability": 0.4,
        "swing_adjust": -0.01,  # Slightly tighter
    },
    "chorus": {
        "energy": 1.15,
        "tightness": 0.9,
        "fill_probability": 0.2,
        "swing_adjust": 0.0,
    },
    "bridge": {
        "energy": 0.8,
        "tightness": 1.1,
        "fill_probability": 0.3,
        "swing_adjust": 0.02,  # Slightly looser
    },
    "breakdown": {
        "energy": 0.6,
        "tightness": 1.2,
        "fill_probability": 0.05,
        "swing_adjust": 0.0,
    },
    "drop": {
        "energy": 1.3,
        "tightness": 0.85,
        "fill_probability": 0.1,
        "swing_adjust": -0.02,
    },
    "outro": {
        "energy": 0.75,
        "tightness": 1.0,
        "fill_probability": 0.2,
        "swing_adjust": 0.01,
    },
}


class TemplateMatcher:
    """
    Intelligent template matching based on feel profiles.
    
    Scores templates against audio/MIDI feel and returns
    ranked recommendations with explanations.
    """
    
    def __init__(self):
        self.templates = GENRE_TEMPLATES
        self.velocity_patterns = INSTRUMENT_VELOCITY_PATTERNS
        self.section_modifiers = SECTION_MODIFIERS
    
    def profile_from_audio_feel(self, audio_feel: Dict[str, Any]) -> FeelProfile:
        """
        Convert audio analysis results to a FeelProfile.
        
        Args:
            audio_feel: Dict from audio analyzer (or AudioFeel dataclass)
        
        Returns:
            FeelProfile for template matching
        """
        # Handle both dict and dataclass
        if hasattr(audio_feel, '__dataclass_fields__'):
            af = audio_feel
            tempo = af.rhythm.tempo_bpm
            tempo_stability = af.rhythm.beat_regularity
            dyn_range = af.dynamics.dynamic_range_db / 20  # Normalize
            brightness = af.spectral.centroid_mean / 5000  # Normalize
            density = af.onsets.onset_density / 10  # Normalize
        else:
            tempo = audio_feel.get('tempo_bpm', 120)
            tempo_stability = audio_feel.get('beat_regularity', 0.8)
            dyn_range = audio_feel.get('dynamic_range_db', 12) / 20
            brightness = audio_feel.get('brightness_hz', 2500) / 5000
            density = audio_feel.get('onset_density', 5) / 10
        
        # Quantize energy
        energy_score = density * 0.5 + (1 - dyn_range) * 0.3 + brightness * 0.2
        if energy_score < 0.2:
            energy = EnergyLevel.VERY_LOW
        elif energy_score < 0.4:
            energy = EnergyLevel.LOW
        elif energy_score < 0.6:
            energy = EnergyLevel.MEDIUM
        elif energy_score < 0.8:
            energy = EnergyLevel.HIGH
        else:
            energy = EnergyLevel.VERY_HIGH
        
        # Estimate swing from tempo stability (looser = more swing typically)
        swing_estimate = 0.50 + (1 - tempo_stability) * 0.15
        swing_feel = self._classify_swing(swing_estimate)
        
        return FeelProfile(
            tempo_bpm=tempo,
            tempo_stability=tempo_stability,
            energy_level=energy,
            dynamic_range=min(1.0, dyn_range),
            swing_feel=swing_feel,
            swing_ratio=swing_estimate,
            note_density=min(1.0, density),
            brightness=min(1.0, brightness),
            source_type="audio"
        )
    
    def profile_from_midi(self, midi_data, groove_template: Dict = None) -> FeelProfile:
        """
        Create FeelProfile from MIDI data and optional extracted groove.
        """
        # Basic MIDI stats
        tempo = midi_data.bpm if hasattr(midi_data, 'bpm') else 120
        notes = midi_data.all_notes if hasattr(midi_data, 'all_notes') else []
        
        # Calculate density
        if notes and hasattr(midi_data, 'ticks_per_bar'):
            total_bars = max(1, max(n.onset_ticks for n in notes) / midi_data.ticks_per_bar)
            density = len(notes) / (total_bars * 16)  # Notes per 16th
        else:
            density = 0.5
        
        # Calculate velocity stats for energy
        if notes:
            vels = [n.velocity for n in notes]
            avg_vel = sum(vels) / len(vels)
            vel_range = max(vels) - min(vels)
            energy_score = avg_vel / 127 * 0.6 + density * 0.4
        else:
            energy_score = 0.5
            vel_range = 50
        
        # Quantize energy
        if energy_score < 0.3:
            energy = EnergyLevel.LOW
        elif energy_score < 0.5:
            energy = EnergyLevel.MEDIUM
        elif energy_score < 0.7:
            energy = EnergyLevel.HIGH
        else:
            energy = EnergyLevel.VERY_HIGH
        
        # Use groove template swing if available
        if groove_template and 'swing' in groove_template:
            swing_ratio = groove_template['swing']
        elif groove_template and 'swing_ratio' in groove_template:
            swing_ratio = groove_template['swing_ratio']
        else:
            swing_ratio = 0.50
        
        swing_feel = self._classify_swing(swing_ratio)
        
        # Ghost note density
        ghost_count = sum(1 for n in notes if n.velocity < 40) if notes else 0
        ghost_density = ghost_count / len(notes) if notes else 0
        
        return FeelProfile(
            tempo_bpm=tempo,
            energy_level=energy,
            dynamic_range=vel_range / 127,
            swing_feel=swing_feel,
            swing_ratio=swing_ratio,
            note_density=min(1.0, density),
            ghost_density=ghost_density,
            source_type="midi"
        )
    
    def _classify_swing(self, ratio: float) -> SwingFeel:
        """Classify swing ratio into feel category."""
        if ratio < 0.52:
            return SwingFeel.STRAIGHT
        elif ratio < 0.56:
            return SwingFeel.SUBTLE
        elif ratio < 0.61:
            return SwingFeel.LIGHT
        elif ratio < 0.65:
            return SwingFeel.MEDIUM
        elif ratio < 0.69:
            return SwingFeel.TRIPLET
        else:
            return SwingFeel.HEAVY
    
    def score_template(
        self,
        profile: FeelProfile,
        genre: str,
        template: Dict[str, Any]
    ) -> TemplateScore:
        """
        Score how well a template matches a feel profile.
        
        Returns score 0-100 with component breakdown.
        """
        match_reasons = []
        mismatch_reasons = []
        
        # 1. Tempo compatibility (20 points)
        # Templates don't have tempo, but genres have typical ranges
        tempo_ranges = {
            "hiphop": (70, 100), "funk": (95, 120), "jazz": (80, 180),
            "rock": (100, 140), "edm": (120, 150), "reggae": (65, 90),
            "gospel": (70, 130), "rnb": (65, 100), "latin": (90, 130),
            "country": (90, 140), "metal": (120, 200), "soul": (70, 110),
            "afrobeat": (95, 130),
        }
        
        low, high = tempo_ranges.get(genre.lower(), (80, 140))
        tempo = profile.tempo_bpm
        
        if low <= tempo <= high:
            tempo_score = 20
            match_reasons.append(f"Tempo {tempo:.0f} fits {genre} range ({low}-{high})")
        elif tempo < low:
            tempo_score = max(0, 20 - (low - tempo) / 2)
            mismatch_reasons.append(f"Tempo {tempo:.0f} below typical {genre} ({low}+)")
        else:
            tempo_score = max(0, 20 - (tempo - high) / 2)
            mismatch_reasons.append(f"Tempo {tempo:.0f} above typical {genre} ({high}-)")
        
        # 2. Energy match (25 points)
        template_energy = self._estimate_template_energy(template)
        profile_energy = profile.energy_level.value / 5  # Normalize to 0-1
        
        energy_diff = abs(template_energy - profile_energy)
        energy_score = max(0, 25 - energy_diff * 40)
        
        if energy_diff < 0.2:
            match_reasons.append(f"Energy levels align well")
        elif energy_diff > 0.4:
            mismatch_reasons.append(f"Energy mismatch (template {'higher' if template_energy > profile_energy else 'lower'})")
        
        # 3. Swing match (25 points)
        template_swing = template.get('swing_ratio', 0.50)
        profile_swing = profile.swing_ratio
        
        swing_diff = abs(template_swing - profile_swing)
        swing_score = max(0, 25 - swing_diff * 100)
        
        if swing_diff < 0.05:
            match_reasons.append(f"Swing feel matches ({self._classify_swing(template_swing).value})")
        elif swing_diff > 0.1:
            mismatch_reasons.append(f"Swing mismatch ({self._classify_swing(template_swing).value} vs {profile.swing_feel.value})")
        
        # 4. Density match (15 points)
        template_density = sum(template.get('timing_density', [0.5]*16)) / 16
        density_diff = abs(template_density - profile.note_density)
        density_score = max(0, 15 - density_diff * 30)
        
        if density_diff < 0.2:
            match_reasons.append(f"Note density matches")
        
        # 5. Ghost note compatibility (15 points)
        template_ghosts = template.get('ghost_density', 0.1)
        ghost_diff = abs(template_ghosts - profile.ghost_density)
        brightness_score = max(0, 15 - ghost_diff * 50)
        
        if profile.ghost_density > 0.15 and template_ghosts > 0.15:
            match_reasons.append(f"Both use ghost notes")
        
        total = tempo_score + energy_score + swing_score + density_score + brightness_score
        
        return TemplateScore(
            genre=genre,
            total_score=total,
            tempo_score=tempo_score,
            energy_score=energy_score,
            swing_score=swing_score,
            density_score=density_score,
            brightness_score=brightness_score,
            match_reasons=match_reasons,
            mismatch_reasons=mismatch_reasons
        )
    
    def _estimate_template_energy(self, template: Dict) -> float:
        """Estimate energy level from template (0-1)."""
        vel_curve = template.get('velocity_curve', [90]*16)
        avg_vel = sum(vel_curve) / len(vel_curve) / 127
        
        density = template.get('timing_density', [0.5]*16)
        avg_density = sum(density) / len(density)
        
        return avg_vel * 0.6 + avg_density * 0.4
    
    def rank_templates(
        self,
        profile: FeelProfile,
        top_n: int = 5
    ) -> List[TemplateScore]:
        """
        Rank all templates by match quality.
        
        Returns top N matches with scores.
        """
        scores = []
        
        for genre, template in self.templates.items():
            score = self.score_template(profile, genre, template)
            scores.append(score)
        
        # Sort by total score descending
        scores.sort(key=lambda s: s.total_score, reverse=True)
        
        return scores[:top_n]
    
    def get_best_match(self, profile: FeelProfile) -> Tuple[str, TemplateScore]:
        """Get single best matching template."""
        scores = self.rank_templates(profile, top_n=1)
        if scores:
            return scores[0].genre, scores[0]
        return "rock", TemplateScore("rock", 50, 10, 10, 10, 10, 10, [], ["No good match"])
    
    def get_section_groove_map(
        self,
        base_genre: str,
        section_name: str
    ) -> SectionGrooveMap:
        """
        Get groove map for a specific section.
        
        Applies section modifiers to base genre template.
        """
        template = self.templates.get(base_genre.lower(), self.templates["rock"])
        modifiers = self.section_modifiers.get(section_name.lower(), {})
        
        # Apply modifiers
        energy_mod = modifiers.get('energy', 1.0)
        tightness_mod = modifiers.get('tightness', 1.0)
        swing_adjust = modifiers.get('swing_adjust', 0.0)
        
        # Adjust swing
        base_swing = template.get('swing_ratio', 0.50)
        section_swing = max(0.50, min(0.75, base_swing + swing_adjust))
        
        # Adjust timing offsets based on tightness
        base_offsets = template.get('timing_offset', [0]*16)
        section_offsets = [o / tightness_mod for o in base_offsets]
        
        # Get per-instrument velocities
        inst_vels = self.velocity_patterns.get(base_genre.lower(), {})
        
        # Apply energy modifier to velocities
        modified_vels = {}
        for inst, pattern in inst_vels.items():
            modified_curve = [
                min(127, int(v * energy_mod))
                for v in pattern.velocity_curve
            ]
            modified_vels[inst] = InstrumentVelocityPattern(
                instrument=inst,
                velocity_curve=modified_curve,
                velocity_std=pattern.velocity_std,
                accent_positions=pattern.accent_positions,
                ghost_positions=pattern.ghost_positions,
                base_velocity=min(127, int(pattern.base_velocity * energy_mod)),
                accent_boost=pattern.accent_boost,
                ghost_reduction=pattern.ghost_reduction,
            )
        
        # Get pocket
        pocket = POCKET_OFFSETS.get(base_genre.lower(), {})
        
        return SectionGrooveMap(
            section_name=section_name,
            swing_ratio=section_swing,
            timing_offset=section_offsets,
            instrument_velocities=modified_vels,
            instrument_pocket=pocket,
            energy_modifier=energy_mod,
            tightness_modifier=tightness_mod,
            fill_probability=modifiers.get('fill_probability', 0.1),
            fill_intensity=0.5,
        )


# === Convenience Functions ===

def match_audio_to_template(audio_feel: Dict) -> Tuple[str, TemplateScore]:
    """Match audio analysis to best template."""
    matcher = TemplateMatcher()
    profile = matcher.profile_from_audio_feel(audio_feel)
    return matcher.get_best_match(profile)


def rank_templates_for_audio(audio_feel: Dict, top_n: int = 5) -> List[TemplateScore]:
    """Rank templates for audio feel."""
    matcher = TemplateMatcher()
    profile = matcher.profile_from_audio_feel(audio_feel)
    return matcher.rank_templates(profile, top_n)


def get_section_aware_grooves(
    genre: str,
    sections: List[str]
) -> Dict[str, SectionGrooveMap]:
    """Get groove maps for multiple sections."""
    matcher = TemplateMatcher()
    return {
        section: matcher.get_section_groove_map(genre, section)
        for section in sections
    }


def get_instrument_velocity_pattern(
    genre: str,
    instrument: str
) -> Optional[InstrumentVelocityPattern]:
    """Get velocity pattern for specific instrument."""
    genre_patterns = INSTRUMENT_VELOCITY_PATTERNS.get(genre.lower(), {})
    return genre_patterns.get(instrument.lower())
