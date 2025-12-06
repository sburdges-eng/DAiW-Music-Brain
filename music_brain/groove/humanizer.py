"""
Neural Groove Humanization Engine

Uses machine learning to humanize MIDI patterns by learning from real performances.
Analyzes timing micro-variations, velocity curves, and articulation patterns
to make programmed beats feel more human.

This is LOCAL-FIRST - uses lightweight models that run on CPU without cloud APIs.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any, Callable
from enum import Enum
import random
import math
import json
from pathlib import Path


class HumanizationStyle(Enum):
    """Different styles of humanization based on real performance analysis."""
    TIGHT_POCKET = "tight_pocket"      # Minimal variation, studio precision
    LAID_BACK = "laid_back"            # Behind the beat, relaxed feel
    PUSHED = "pushed"                   # Ahead of the beat, energetic
    DRUNK = "drunk"                     # Loose, imprecise, lo-fi
    JAZZ_SWING = "jazz_swing"          # Classic swing feel with accents
    HIP_HOP_BOUNCE = "hip_hop_bounce"  # Head-nod groove
    ROCK_DRIVE = "rock_drive"          # Driving, slightly ahead
    LATIN_CLAVE = "latin_clave"        # Clave-based micro-timing
    GOSPEL_PUSH = "gospel_push"        # Slightly ahead on 2 and 4
    DETROIT_TECHNO = "detroit_techno"  # Quantized but with velocity swing


class InstrumentRole(Enum):
    """Role of instrument in the groove - affects humanization differently."""
    KICK = "kick"
    SNARE = "snare"
    HIHAT = "hihat"
    RIDE = "ride"
    TOM = "tom"
    BASS = "bass"
    KEYS = "keys"
    GUITAR = "guitar"
    LEAD = "lead"
    PAD = "pad"


@dataclass
class TimingProfile:
    """Timing characteristics learned from real performances."""
    mean_offset_ticks: float = 0.0        # Average offset from grid
    std_deviation_ticks: float = 2.0      # Variation amount
    beat_position_weights: Dict[int, float] = field(default_factory=dict)  # Position-specific offsets
    tempo_sensitivity: float = 0.0         # How much timing loosens at different tempos
    intensity_correlation: float = 0.0     # Correlation between velocity and timing


@dataclass
class VelocityProfile:
    """Velocity characteristics learned from real performances."""
    base_velocity: int = 100
    accent_boost: int = 20                 # Extra velocity on accents
    ghost_reduction: int = 40              # Reduction for ghost notes
    position_weights: Dict[int, float] = field(default_factory=dict)  # Beat position affects velocity
    variation_range: int = 8               # Random variation range
    decay_per_bar: float = 0.0            # Velocity decay over time (fatigue)


@dataclass
class ArticulationProfile:
    """Articulation characteristics - note length and attack."""
    length_multiplier: float = 0.9         # Multiply original length
    length_variation: float = 0.1          # Random length variation
    attack_sharpness: float = 0.8          # 0=soft attack, 1=hard attack
    release_curve: str = "linear"          # linear, exponential, sudden
    overlap_tendency: float = 0.0          # Tendency to overlap notes (legato)


@dataclass
class HumanizationParams:
    """Complete humanization parameters for an instrument."""
    timing: TimingProfile = field(default_factory=TimingProfile)
    velocity: VelocityProfile = field(default_factory=VelocityProfile)
    articulation: ArticulationProfile = field(default_factory=ArticulationProfile)

    # Context-aware adjustments
    fill_intensity: float = 1.2            # Intensity multiplier during fills
    transition_looseness: float = 1.5      # Timing looseness during transitions
    buildup_tightness: float = 0.7         # Tighter timing during buildups


@dataclass
class MidiNote:
    """Represents a MIDI note for humanization."""
    pitch: int
    velocity: int
    start_tick: int
    duration_ticks: int
    channel: int = 0

    def copy(self) -> 'MidiNote':
        return MidiNote(
            pitch=self.pitch,
            velocity=self.velocity,
            start_tick=self.start_tick,
            duration_ticks=self.duration_ticks,
            channel=self.channel
        )


@dataclass
class GrooveContext:
    """Context information for humanization decisions."""
    ppq: int = 480                         # Ticks per quarter note
    tempo_bpm: float = 120.0
    time_signature: Tuple[int, int] = (4, 4)
    bar_number: int = 0
    beat_in_bar: int = 0
    is_fill: bool = False
    is_transition: bool = False
    is_buildup: bool = False
    intensity_curve: float = 1.0           # 0.0-2.0, where 1.0 is normal


class PerformanceAnalyzer:
    """Analyzes real performances to learn humanization patterns."""

    def __init__(self):
        self.learned_profiles: Dict[str, HumanizationParams] = {}
        self.style_templates = self._init_style_templates()

    def _init_style_templates(self) -> Dict[HumanizationStyle, HumanizationParams]:
        """Initialize built-in style templates based on analysis of real performances."""
        templates = {}

        # Tight pocket - minimal variation, studio precision
        templates[HumanizationStyle.TIGHT_POCKET] = HumanizationParams(
            timing=TimingProfile(
                mean_offset_ticks=0,
                std_deviation_ticks=1.5,
                beat_position_weights={0: 0, 1: 0, 2: 0, 3: 0},
                tempo_sensitivity=0.1
            ),
            velocity=VelocityProfile(
                base_velocity=100,
                accent_boost=15,
                ghost_reduction=35,
                variation_range=5
            ),
            articulation=ArticulationProfile(
                length_multiplier=0.95,
                length_variation=0.05,
                attack_sharpness=0.85
            )
        )

        # Laid back - behind the beat
        templates[HumanizationStyle.LAID_BACK] = HumanizationParams(
            timing=TimingProfile(
                mean_offset_ticks=8,  # Behind the beat
                std_deviation_ticks=4,
                beat_position_weights={0: 5, 1: 10, 2: 5, 3: 12},  # More laid back on 2 and 4
                tempo_sensitivity=0.3
            ),
            velocity=VelocityProfile(
                base_velocity=90,
                accent_boost=20,
                ghost_reduction=40,
                variation_range=10
            ),
            articulation=ArticulationProfile(
                length_multiplier=1.05,  # Slightly longer notes
                length_variation=0.15,
                attack_sharpness=0.6
            )
        )

        # Pushed - ahead of the beat
        templates[HumanizationStyle.PUSHED] = HumanizationParams(
            timing=TimingProfile(
                mean_offset_ticks=-6,  # Ahead of the beat
                std_deviation_ticks=3,
                beat_position_weights={0: -8, 1: -4, 2: -8, 3: -4},
                tempo_sensitivity=0.2
            ),
            velocity=VelocityProfile(
                base_velocity=105,
                accent_boost=25,
                ghost_reduction=30,
                variation_range=8
            ),
            articulation=ArticulationProfile(
                length_multiplier=0.85,
                length_variation=0.08,
                attack_sharpness=0.95
            )
        )

        # Drunk - loose and imprecise
        templates[HumanizationStyle.DRUNK] = HumanizationParams(
            timing=TimingProfile(
                mean_offset_ticks=0,
                std_deviation_ticks=15,  # High variation
                beat_position_weights={0: 0, 1: 5, 2: -3, 3: 8},
                tempo_sensitivity=0.5
            ),
            velocity=VelocityProfile(
                base_velocity=85,
                accent_boost=30,
                ghost_reduction=45,
                variation_range=20
            ),
            articulation=ArticulationProfile(
                length_multiplier=1.1,
                length_variation=0.25,
                attack_sharpness=0.5
            )
        )

        # Jazz swing
        templates[HumanizationStyle.JAZZ_SWING] = HumanizationParams(
            timing=TimingProfile(
                mean_offset_ticks=2,
                std_deviation_ticks=5,
                # Swing the offbeats
                beat_position_weights={0: 0, 1: 20, 2: 0, 3: 20},
                tempo_sensitivity=0.4
            ),
            velocity=VelocityProfile(
                base_velocity=95,
                accent_boost=25,
                ghost_reduction=50,
                position_weights={0: 1.0, 1: 0.7, 2: 1.1, 3: 0.7},
                variation_range=12
            ),
            articulation=ArticulationProfile(
                length_multiplier=0.8,
                length_variation=0.2,
                attack_sharpness=0.7,
                overlap_tendency=0.1
            )
        )

        # Hip-hop bounce
        templates[HumanizationStyle.HIP_HOP_BOUNCE] = HumanizationParams(
            timing=TimingProfile(
                mean_offset_ticks=5,
                std_deviation_ticks=6,
                beat_position_weights={0: 0, 1: 8, 2: -2, 3: 10},
                tempo_sensitivity=0.25
            ),
            velocity=VelocityProfile(
                base_velocity=100,
                accent_boost=20,
                ghost_reduction=45,
                position_weights={0: 1.0, 1: 0.85, 2: 1.05, 3: 0.8},
                variation_range=10
            ),
            articulation=ArticulationProfile(
                length_multiplier=0.75,
                length_variation=0.1,
                attack_sharpness=0.9
            )
        )

        # Rock drive
        templates[HumanizationStyle.ROCK_DRIVE] = HumanizationParams(
            timing=TimingProfile(
                mean_offset_ticks=-3,
                std_deviation_ticks=4,
                beat_position_weights={0: -5, 1: 0, 2: -5, 3: 0},
                tempo_sensitivity=0.15
            ),
            velocity=VelocityProfile(
                base_velocity=110,
                accent_boost=15,
                ghost_reduction=30,
                variation_range=6
            ),
            articulation=ArticulationProfile(
                length_multiplier=0.9,
                length_variation=0.08,
                attack_sharpness=0.95
            )
        )

        # Latin clave
        templates[HumanizationStyle.LATIN_CLAVE] = HumanizationParams(
            timing=TimingProfile(
                mean_offset_ticks=0,
                std_deviation_ticks=3,
                # Clave-aligned timing
                beat_position_weights={0: 0, 1: -5, 2: 3, 3: -3},
                tempo_sensitivity=0.2
            ),
            velocity=VelocityProfile(
                base_velocity=100,
                accent_boost=18,
                ghost_reduction=35,
                position_weights={0: 1.1, 1: 0.85, 2: 1.0, 3: 0.9},
                variation_range=8
            ),
            articulation=ArticulationProfile(
                length_multiplier=0.85,
                length_variation=0.1,
                attack_sharpness=0.8
            )
        )

        # Gospel push
        templates[HumanizationStyle.GOSPEL_PUSH] = HumanizationParams(
            timing=TimingProfile(
                mean_offset_ticks=-2,
                std_deviation_ticks=5,
                # Push on 2 and 4
                beat_position_weights={0: 0, 1: -10, 2: 0, 3: -10},
                tempo_sensitivity=0.3
            ),
            velocity=VelocityProfile(
                base_velocity=105,
                accent_boost=25,
                ghost_reduction=40,
                position_weights={0: 0.9, 1: 1.15, 2: 0.9, 3: 1.15},
                variation_range=10
            ),
            articulation=ArticulationProfile(
                length_multiplier=0.95,
                length_variation=0.12,
                attack_sharpness=0.85
            )
        )

        # Detroit techno - quantized but with velocity swing
        templates[HumanizationStyle.DETROIT_TECHNO] = HumanizationParams(
            timing=TimingProfile(
                mean_offset_ticks=0,
                std_deviation_ticks=1,  # Very tight
                beat_position_weights={0: 0, 1: 0, 2: 0, 3: 0},
                tempo_sensitivity=0.05
            ),
            velocity=VelocityProfile(
                base_velocity=100,
                accent_boost=10,
                ghost_reduction=25,
                # Velocity swing instead of timing swing
                position_weights={0: 1.1, 1: 0.75, 2: 1.0, 3: 0.8},
                variation_range=3
            ),
            articulation=ArticulationProfile(
                length_multiplier=0.9,
                length_variation=0.02,
                attack_sharpness=1.0
            )
        )

        return templates

    def analyze_performance(self, notes: List[MidiNote], ppq: int = 480,
                           grid_division: int = 4) -> HumanizationParams:
        """Analyze a real performance to extract humanization parameters."""
        if not notes:
            return HumanizationParams()

        # Calculate grid positions
        grid_size = ppq // grid_division  # e.g., 16th notes at division=4

        # Analyze timing offsets
        timing_offsets = []
        velocity_values = []
        beat_position_offsets: Dict[int, List[float]] = {i: [] for i in range(grid_division * 4)}

        for note in notes:
            # Find nearest grid position
            nearest_grid = round(note.start_tick / grid_size) * grid_size
            offset = note.start_tick - nearest_grid
            timing_offsets.append(offset)
            velocity_values.append(note.velocity)

            # Track by beat position (within a bar of 4 beats)
            bar_position = (note.start_tick // grid_size) % (grid_division * 4)
            beat_position_offsets[bar_position].append(offset)

        # Calculate statistics
        mean_offset = sum(timing_offsets) / len(timing_offsets) if timing_offsets else 0
        variance = sum((x - mean_offset) ** 2 for x in timing_offsets) / len(timing_offsets) if timing_offsets else 0
        std_dev = math.sqrt(variance)

        # Calculate position-specific weights
        position_weights = {}
        for pos, offsets in beat_position_offsets.items():
            if offsets:
                position_weights[pos] = sum(offsets) / len(offsets)

        # Calculate velocity statistics
        mean_velocity = sum(velocity_values) / len(velocity_values) if velocity_values else 100
        vel_variance = sum((v - mean_velocity) ** 2 for v in velocity_values) / len(velocity_values) if velocity_values else 0

        # Build the profile
        return HumanizationParams(
            timing=TimingProfile(
                mean_offset_ticks=mean_offset,
                std_deviation_ticks=std_dev,
                beat_position_weights=position_weights
            ),
            velocity=VelocityProfile(
                base_velocity=int(mean_velocity),
                variation_range=int(math.sqrt(vel_variance))
            )
        )

    def save_profile(self, name: str, params: HumanizationParams, path: Path):
        """Save a learned profile to disk."""
        data = {
            'name': name,
            'timing': {
                'mean_offset_ticks': params.timing.mean_offset_ticks,
                'std_deviation_ticks': params.timing.std_deviation_ticks,
                'beat_position_weights': params.timing.beat_position_weights,
                'tempo_sensitivity': params.timing.tempo_sensitivity,
                'intensity_correlation': params.timing.intensity_correlation
            },
            'velocity': {
                'base_velocity': params.velocity.base_velocity,
                'accent_boost': params.velocity.accent_boost,
                'ghost_reduction': params.velocity.ghost_reduction,
                'position_weights': params.velocity.position_weights,
                'variation_range': params.velocity.variation_range,
                'decay_per_bar': params.velocity.decay_per_bar
            },
            'articulation': {
                'length_multiplier': params.articulation.length_multiplier,
                'length_variation': params.articulation.length_variation,
                'attack_sharpness': params.articulation.attack_sharpness,
                'release_curve': params.articulation.release_curve,
                'overlap_tendency': params.articulation.overlap_tendency
            }
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_profile(self, path: Path) -> HumanizationParams:
        """Load a learned profile from disk."""
        with open(path, 'r') as f:
            data = json.load(f)

        return HumanizationParams(
            timing=TimingProfile(
                mean_offset_ticks=data['timing']['mean_offset_ticks'],
                std_deviation_ticks=data['timing']['std_deviation_ticks'],
                beat_position_weights=data['timing'].get('beat_position_weights', {}),
                tempo_sensitivity=data['timing'].get('tempo_sensitivity', 0),
                intensity_correlation=data['timing'].get('intensity_correlation', 0)
            ),
            velocity=VelocityProfile(
                base_velocity=data['velocity']['base_velocity'],
                accent_boost=data['velocity'].get('accent_boost', 20),
                ghost_reduction=data['velocity'].get('ghost_reduction', 40),
                position_weights=data['velocity'].get('position_weights', {}),
                variation_range=data['velocity']['variation_range'],
                decay_per_bar=data['velocity'].get('decay_per_bar', 0)
            ),
            articulation=ArticulationProfile(
                length_multiplier=data['articulation']['length_multiplier'],
                length_variation=data['articulation']['length_variation'],
                attack_sharpness=data['articulation'].get('attack_sharpness', 0.8),
                release_curve=data['articulation'].get('release_curve', 'linear'),
                overlap_tendency=data['articulation'].get('overlap_tendency', 0)
            )
        )


class NeuralGrooveHumanizer:
    """
    Main humanization engine that applies learned patterns to MIDI.

    This uses a combination of statistical models and rule-based systems
    to humanize MIDI data. The "neural" aspect comes from learning from
    real performances - the actual processing is lightweight and CPU-friendly.
    """

    def __init__(self, seed: Optional[int] = None):
        self.analyzer = PerformanceAnalyzer()
        self.rng = random.Random(seed)

        # Instrument-specific adjustments
        self.instrument_adjustments: Dict[InstrumentRole, Dict[str, float]] = {
            InstrumentRole.KICK: {'timing_scale': 0.5, 'velocity_scale': 1.2},
            InstrumentRole.SNARE: {'timing_scale': 0.7, 'velocity_scale': 1.1},
            InstrumentRole.HIHAT: {'timing_scale': 1.5, 'velocity_scale': 0.9},
            InstrumentRole.RIDE: {'timing_scale': 1.2, 'velocity_scale': 0.85},
            InstrumentRole.TOM: {'timing_scale': 0.8, 'velocity_scale': 1.15},
            InstrumentRole.BASS: {'timing_scale': 0.6, 'velocity_scale': 1.0},
            InstrumentRole.KEYS: {'timing_scale': 1.0, 'velocity_scale': 0.95},
            InstrumentRole.GUITAR: {'timing_scale': 1.1, 'velocity_scale': 1.0},
            InstrumentRole.LEAD: {'timing_scale': 1.0, 'velocity_scale': 1.05},
            InstrumentRole.PAD: {'timing_scale': 0.3, 'velocity_scale': 0.8},
        }

    def humanize(self, notes: List[MidiNote],
                 style: HumanizationStyle = HumanizationStyle.TIGHT_POCKET,
                 intensity: float = 1.0,
                 instrument: Optional[InstrumentRole] = None,
                 context: Optional[GrooveContext] = None,
                 custom_params: Optional[HumanizationParams] = None) -> List[MidiNote]:
        """
        Humanize a list of MIDI notes.

        Args:
            notes: List of MidiNote objects to humanize
            style: Humanization style preset
            intensity: How much humanization to apply (0.0-2.0)
            instrument: Optional instrument role for context-aware adjustments
            context: Optional groove context (tempo, time signature, etc.)
            custom_params: Optional custom humanization parameters

        Returns:
            List of humanized MidiNote objects
        """
        if not notes:
            return []

        # Get humanization parameters
        params = custom_params or self.analyzer.style_templates.get(
            style, HumanizationParams()
        )

        # Apply intensity scaling
        params = self._scale_params(params, intensity)

        # Get instrument adjustments
        inst_adj = self.instrument_adjustments.get(
            instrument, {'timing_scale': 1.0, 'velocity_scale': 1.0}
        ) if instrument else {'timing_scale': 1.0, 'velocity_scale': 1.0}

        # Set up context
        ctx = context or GrooveContext()

        humanized = []
        for note in notes:
            humanized_note = self._humanize_note(note, params, inst_adj, ctx)
            humanized.append(humanized_note)

        return humanized

    def _scale_params(self, params: HumanizationParams, intensity: float) -> HumanizationParams:
        """Scale humanization parameters by intensity."""
        return HumanizationParams(
            timing=TimingProfile(
                mean_offset_ticks=params.timing.mean_offset_ticks * intensity,
                std_deviation_ticks=params.timing.std_deviation_ticks * intensity,
                beat_position_weights={
                    k: v * intensity for k, v in params.timing.beat_position_weights.items()
                },
                tempo_sensitivity=params.timing.tempo_sensitivity,
                intensity_correlation=params.timing.intensity_correlation
            ),
            velocity=VelocityProfile(
                base_velocity=params.velocity.base_velocity,
                accent_boost=int(params.velocity.accent_boost * intensity),
                ghost_reduction=int(params.velocity.ghost_reduction * intensity),
                position_weights=params.velocity.position_weights,
                variation_range=int(params.velocity.variation_range * intensity),
                decay_per_bar=params.velocity.decay_per_bar * intensity
            ),
            articulation=ArticulationProfile(
                length_multiplier=1.0 + (params.articulation.length_multiplier - 1.0) * intensity,
                length_variation=params.articulation.length_variation * intensity,
                attack_sharpness=params.articulation.attack_sharpness,
                release_curve=params.articulation.release_curve,
                overlap_tendency=params.articulation.overlap_tendency * intensity
            ),
            fill_intensity=params.fill_intensity,
            transition_looseness=params.transition_looseness,
            buildup_tightness=params.buildup_tightness
        )

    def _humanize_note(self, note: MidiNote, params: HumanizationParams,
                       inst_adj: Dict[str, float], ctx: GrooveContext) -> MidiNote:
        """Humanize a single note."""
        humanized = note.copy()

        # Calculate beat position within bar
        ticks_per_beat = ctx.ppq
        ticks_per_bar = ticks_per_beat * ctx.time_signature[0]
        position_in_bar = (note.start_tick % ticks_per_bar) // (ticks_per_beat // 4)

        # --- TIMING HUMANIZATION ---

        # Base timing offset
        timing_offset = params.timing.mean_offset_ticks

        # Add position-specific offset
        if position_in_bar in params.timing.beat_position_weights:
            timing_offset += params.timing.beat_position_weights[position_in_bar]

        # Add random variation (Gaussian distribution)
        timing_variation = self.rng.gauss(0, params.timing.std_deviation_ticks)
        timing_offset += timing_variation

        # Scale by instrument
        timing_offset *= inst_adj['timing_scale']

        # Context adjustments
        if ctx.is_fill:
            timing_offset *= params.fill_intensity
        elif ctx.is_transition:
            timing_offset *= params.transition_looseness
        elif ctx.is_buildup:
            timing_offset *= params.buildup_tightness

        # Apply timing (ensure it doesn't go negative)
        humanized.start_tick = max(0, int(note.start_tick + timing_offset))

        # --- VELOCITY HUMANIZATION ---

        # Start with base velocity adjustment
        velocity = note.velocity

        # Apply position-based weighting
        if position_in_bar in params.velocity.position_weights:
            velocity = int(velocity * params.velocity.position_weights[position_in_bar])

        # Add random variation
        velocity_variation = self.rng.randint(
            -params.velocity.variation_range,
            params.velocity.variation_range
        )
        velocity += velocity_variation

        # Scale by instrument
        velocity = int(velocity * inst_adj['velocity_scale'])

        # Apply intensity curve from context
        velocity = int(velocity * ctx.intensity_curve)

        # Clamp to valid MIDI range
        humanized.velocity = max(1, min(127, velocity))

        # --- ARTICULATION HUMANIZATION ---

        # Adjust note length
        length_mult = params.articulation.length_multiplier
        length_var = self.rng.uniform(
            -params.articulation.length_variation,
            params.articulation.length_variation
        )
        new_duration = int(note.duration_ticks * (length_mult + length_var))
        humanized.duration_ticks = max(1, new_duration)

        return humanized

    def humanize_drums(self, kick: List[MidiNote], snare: List[MidiNote],
                       hihat: List[MidiNote], style: HumanizationStyle,
                       intensity: float = 1.0,
                       context: Optional[GrooveContext] = None) -> Dict[str, List[MidiNote]]:
        """
        Humanize a drum kit with correlated timing.

        Drums are humanized together to maintain groove coherence -
        when the drummer pushes, the whole kit pushes together.
        """
        ctx = context or GrooveContext()

        # Shared timing variation per beat (drummer plays ahead or behind together)
        beat_offsets: Dict[int, float] = {}
        ticks_per_beat = ctx.ppq

        # Pre-calculate shared offsets for each beat
        def get_beat_offset(tick: int) -> float:
            beat = tick // ticks_per_beat
            if beat not in beat_offsets:
                # All drums share this offset (with some variation)
                beat_offsets[beat] = self.rng.gauss(0, 3)
            return beat_offsets[beat]

        # Humanize each instrument with shared context
        result = {
            'kick': self.humanize(kick, style, intensity * 0.6, InstrumentRole.KICK, ctx),
            'snare': self.humanize(snare, style, intensity * 0.8, InstrumentRole.SNARE, ctx),
            'hihat': self.humanize(hihat, style, intensity, InstrumentRole.HIHAT, ctx),
        }

        # Apply shared beat offsets
        for instrument_notes in result.values():
            for note in instrument_notes:
                shared_offset = get_beat_offset(note.start_tick)
                note.start_tick = max(0, int(note.start_tick + shared_offset))

        return result

    def create_ghost_notes(self, main_notes: List[MidiNote],
                          density: float = 0.3,
                          velocity_range: Tuple[int, int] = (20, 50),
                          subdivisions: int = 4) -> List[MidiNote]:
        """
        Generate ghost notes between main hits.

        Args:
            main_notes: The main notes to add ghosts around
            density: Probability of ghost note at each grid position (0.0-1.0)
            velocity_range: Min and max velocity for ghosts
            subdivisions: Grid subdivision (4 = 16th notes, 6 = 16th triplets)

        Returns:
            List of ghost notes (doesn't include original notes)
        """
        if not main_notes:
            return []

        ghosts = []
        ppq = 480  # Assume standard PPQ
        grid_size = ppq // subdivisions

        # Get pitch from first note (assume all same instrument)
        pitch = main_notes[0].pitch
        channel = main_notes[0].channel

        # Find range of notes
        min_tick = min(n.start_tick for n in main_notes)
        max_tick = max(n.start_tick for n in main_notes)

        # Get positions of main notes for collision detection
        main_positions = {n.start_tick // grid_size for n in main_notes}

        # Generate potential ghost positions
        for pos in range(min_tick // grid_size, max_tick // grid_size + 1):
            if pos in main_positions:
                continue  # Don't put ghost on main note

            if self.rng.random() < density:
                velocity = self.rng.randint(velocity_range[0], velocity_range[1])
                ghost = MidiNote(
                    pitch=pitch,
                    velocity=velocity,
                    start_tick=pos * grid_size,
                    duration_ticks=grid_size // 2,
                    channel=channel
                )
                ghosts.append(ghost)

        return ghosts


# Convenience functions for common use cases

def humanize_midi(notes: List[MidiNote],
                  style: str = "tight_pocket",
                  intensity: float = 1.0) -> List[MidiNote]:
    """
    Simple humanization function.

    Args:
        notes: List of MidiNote objects
        style: Style name (tight_pocket, laid_back, pushed, drunk, jazz_swing,
               hip_hop_bounce, rock_drive, latin_clave, gospel_push, detroit_techno)
        intensity: How much humanization (0.0-2.0)

    Returns:
        Humanized notes
    """
    style_enum = HumanizationStyle(style)
    humanizer = NeuralGrooveHumanizer()
    return humanizer.humanize(notes, style_enum, intensity)


def learn_from_performance(notes: List[MidiNote], ppq: int = 480) -> HumanizationParams:
    """
    Analyze a real performance and extract humanization parameters.

    Args:
        notes: Notes from a real performance
        ppq: Ticks per quarter note

    Returns:
        HumanizationParams that can be used to humanize other patterns
    """
    analyzer = PerformanceAnalyzer()
    return analyzer.analyze_performance(notes, ppq)


# Export public API
__all__ = [
    'HumanizationStyle',
    'InstrumentRole',
    'TimingProfile',
    'VelocityProfile',
    'ArticulationProfile',
    'HumanizationParams',
    'MidiNote',
    'GrooveContext',
    'PerformanceAnalyzer',
    'NeuralGrooveHumanizer',
    'humanize_midi',
    'learn_from_performance',
]
