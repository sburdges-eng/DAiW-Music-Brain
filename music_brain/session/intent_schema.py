"""
Song Intent Schema - Structured deep interrogation for songwriting.

Implements the three-phase interrogation model:
- Phase 0: Core Wound/Desire (deep interrogation)
- Phase 1: Emotional & Intent (validation)
- Phase 2: Technical Constraints (implementation)

Plus comprehensive rule-breaking enums for intentional creative choices.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# =================================================================
# ENUMS: Rule Breaking Categories
# =================================================================

class HarmonyRuleBreak(Enum):
    """Harmony rules to intentionally break."""
    AVOID_TONIC_RESOLUTION = "HARMONY_AvoidTonicResolution"
    PARALLEL_MOTION = "HARMONY_ParallelMotion"
    MODAL_INTERCHANGE = "HARMONY_ModalInterchange"
    TRITONE_SUBSTITUTION = "HARMONY_TritoneSubstitution"
    POLYTONALITY = "HARMONY_Polytonality"
    UNRESOLVED_DISSONANCE = "HARMONY_UnresolvedDissonance"


class RhythmRuleBreak(Enum):
    """Rhythm rules to intentionally break."""
    CONSTANT_DISPLACEMENT = "RHYTHM_ConstantDisplacement"
    TEMPO_FLUCTUATION = "RHYTHM_TempoFluctuation"
    METRIC_MODULATION = "RHYTHM_MetricModulation"
    POLYRHYTHMIC_LAYERS = "RHYTHM_PolyrhythmicLayers"
    DROPPED_BEATS = "RHYTHM_DroppedBeats"


class ArrangementRuleBreak(Enum):
    """Arrangement rules to intentionally break."""
    UNBALANCED_DYNAMICS = "ARRANGEMENT_UnbalancedDynamics"
    STRUCTURAL_MISMATCH = "ARRANGEMENT_StructuralMismatch"
    BURIED_VOCALS = "ARRANGEMENT_BuriedVocals"
    EXTREME_DYNAMIC_RANGE = "ARRANGEMENT_ExtremeDynamicRange"
    PREMATURE_CLIMAX = "ARRANGEMENT_PrematureClimax"


class ProductionRuleBreak(Enum):
    """Production rules to intentionally break."""
    EXCESSIVE_MUD = "PRODUCTION_ExcessiveMud"
    PITCH_IMPERFECTION = "PRODUCTION_PitchImperfection"
    ROOM_NOISE = "PRODUCTION_RoomNoise"
    DISTORTION = "PRODUCTION_Distortion"
    MONO_COLLAPSE = "PRODUCTION_MonoCollapse"
    LO_FI_DEGRADATION = "PRODUCTION_LoFiDegradation"
    SILENCE_AS_INSTRUMENT = "PRODUCTION_SilenceAsInstrument"
    CLIPPING_PEAKS = "PRODUCTION_ClippingPeaks"


class MelodyRuleBreak(Enum):
    """Melody rules to intentionally break."""
    AVOID_RESOLUTION = "MELODY_AvoidResolution"
    EXCESSIVE_REPETITION = "MELODY_ExcessiveRepetition"
    ANGULAR_INTERVALS = "MELODY_AngularIntervals"
    ANTI_CLIMAX = "MELODY_AntiClimax"
    MONOTONE_DRONE = "MELODY_MonotoneDrone"
    FRAGMENTED_PHRASES = "MELODY_FragmentedPhrases"


class TextureRuleBreak(Enum):
    """Texture rules to intentionally break."""
    FREQUENCY_MASKING = "TEXTURE_FrequencyMasking"
    SPARSE_EMPTINESS = "TEXTURE_SparseEmptiness"
    DENSE_WALL = "TEXTURE_DenseWall"
    CONFLICTING_TIMBRES = "TEXTURE_ConflictingTimbres"
    SINGLE_ELEMENT_FOCUS = "TEXTURE_SingleElementFocus"
    TIMBRAL_DRIFT = "TEXTURE_TimbralDrift"


class TemporalRuleBreak(Enum):
    """Temporal/time rules to intentionally break."""
    EXTENDED_INTRO = "TEMPORAL_ExtendedIntro"
    ABRUPT_ENDING = "TEMPORAL_AbruptEnding"
    TIME_STRETCH = "TEMPORAL_TimeStretch"
    LOOP_HYPNOSIS = "TEMPORAL_LoopHypnosis"
    BREATH_PAUSES = "TEMPORAL_BreathPauses"
    ACCELERANDO_DECAY = "TEMPORAL_AccelerandoDecay"


# =================================================================
# ENUMS: Musical Concept Mappings
# =================================================================

class AffectState(Enum):
    """Emotional states with musical parameter mappings."""
    GRIEF = "grief"
    LONGING = "longing"
    DEFIANCE = "defiance"
    HOPE = "hope"
    RAGE = "rage"
    TENDERNESS = "tenderness"
    ANXIETY = "anxiety"
    EUPHORIA = "euphoria"
    MELANCHOLY = "melancholy"
    NOSTALGIA = "nostalgia"
    CATHARSIS = "catharsis"
    DISSOCIATION = "dissociation"
    DETERMINATION = "determination"
    SURRENDER = "surrender"


class TextureType(Enum):
    """Sonic texture categories."""
    ETHEREAL = "Ethereal"           # Airy, spacious, reverberant
    INTIMATE = "Intimate"           # Close, dry, personal
    MASSIVE = "Massive"             # Full, layered, powerful
    SKELETAL = "Skeletal"           # Minimal, exposed, fragile
    LUSH = "Lush"                   # Rich, warm, enveloping
    HARSH = "Harsh"                 # Aggressive, abrasive, cutting
    MURKY = "Murky"                 # Dark, unclear, submerged
    CRYSTALLINE = "Crystalline"     # Clear, precise, bright


class TensionProfile(Enum):
    """How tension evolves over the song."""
    CONSTANT_HIGH = "Constant High"         # Relentless intensity
    CONSTANT_LOW = "Constant Low"           # Meditative calm
    BUILD_RELEASE = "Build and Release"     # Classic arc
    SAWTOOTH = "Sawtooth"                   # Repeated build-drops
    INVERSE = "Inverse"                     # Start high, end low
    PLATEAU = "Plateau"                     # Build to sustained level
    CHAOTIC = "Chaotic"                     # Unpredictable shifts
    SLOW_BURN = "Slow Burn"                 # Gradual accumulation


class DensityLevel(Enum):
    """Arrangement density."""
    SOLO = "Solo"               # Single voice/instrument
    DUO = "Duo"                 # Two elements in conversation
    SPARSE = "Sparse"           # Few elements, lots of space
    MODERATE = "Moderate"       # Balanced arrangement
    FULL = "Full"               # Complete band/ensemble
    DENSE = "Dense"             # Layered, complex
    OVERWHELMING = "Overwhelming"  # Intentionally too much


class ModalColor(Enum):
    """Mode with emotional associations."""
    IONIAN = "Ionian"           # Bright, happy, resolved
    DORIAN = "Dorian"           # Minor but hopeful, jazzy
    PHRYGIAN = "Phrygian"       # Dark, Spanish, exotic
    LYDIAN = "Lydian"           # Dreamy, floating, ethereal
    MIXOLYDIAN = "Mixolydian"   # Bluesy, earthy, unresolved
    AEOLIAN = "Aeolian"         # Natural minor, sad, serious
    LOCRIAN = "Locrian"         # Unstable, tense, rare


class VulnerabilityScale(Enum):
    """Vulnerability level for emotional exposure."""
    LOW = "Low"       # Guarded, protective
    MEDIUM = "Medium" # Honest but controlled
    HIGH = "High"     # Raw, exposed


class NarrativeArc(Enum):
    """Structural emotional arc."""
    CLIMB_TO_CLIMAX = "Climb-to-Climax"
    SLOW_REVEAL = "Slow Reveal"
    REPETITIVE_DESPAIR = "Repetitive Despair"
    STATIC_REFLECTION = "Static Reflection"
    SUDDEN_SHIFT = "Sudden Shift"
    DESCENT = "Descent"
    RISE_AND_FALL = "Rise and Fall"
    SPIRAL = "Spiral"


class CoreStakes(Enum):
    """What's at stake in the song."""
    PERSONAL = "Personal"         # Individual identity
    RELATIONAL = "Relational"     # Connections
    EXISTENTIAL = "Existential"   # Meaning/purpose
    SURVIVAL = "Survival"         # Life/safety
    CREATIVE = "Creative"         # Expression
    MORAL = "Moral"               # Right/wrong


class GrooveFeel(Enum):
    """Rhythmic feel."""
    STRAIGHT_DRIVING = "Straight/Driving"
    LAID_BACK = "Laid Back"
    SWUNG = "Swung"
    SYNCOPATED = "Syncopated"
    RUBATO_FREE = "Rubato/Free"
    MECHANICAL = "Mechanical"
    ORGANIC_BREATHING = "Organic/Breathing"
    PUSH_PULL = "Push-Pull"


# =================================================================
# RULE BREAKING DEFINITIONS
# =================================================================

RULE_BREAKING_EFFECTS = {
    # Harmony
    "HARMONY_AvoidTonicResolution": {
        "description": "Resolve to IV or VI instead of I",
        "effect": "Unresolved, yearning feeling",
        "use_when": "Song shouldn't feel 'finished' or 'answered'",
        "example_emotions": ["longing", "grief", "uncertainty"],
    },
    "HARMONY_ParallelMotion": {
        "description": "Use forbidden parallel 5ths/octaves",
        "effect": "Vintage, punk, or medieval sound",
        "use_when": "Defiance, raw power, or historical evocation",
        "example_emotions": ["defiance", "anger", "power"],
    },
    "HARMONY_ModalInterchange": {
        "description": "Borrow chord from unrelated key",
        "effect": "Unexpected color, emotional shift",
        "use_when": "Making emotions feel 'earned' or complex",
        "example_emotions": ["bittersweet", "nostalgia", "hope"],
    },
    "HARMONY_TritoneSubstitution": {
        "description": "Replace V7 with bII7",
        "effect": "Jazz sophistication, chromatic movement",
        "use_when": "Adding depth without cliché resolution",
        "example_emotions": ["sophistication", "complexity"],
    },
    "HARMONY_Polytonality": {
        "description": "Stack chords from different keys",
        "effect": "Tension, complexity, disorientation",
        "use_when": "Representing internal conflict or chaos",
        "example_emotions": ["confusion", "conflict", "chaos"],
    },
    "HARMONY_UnresolvedDissonance": {
        "description": "Leave 7ths, 9ths, tritones unresolved",
        "effect": "Lingering tension, incompleteness",
        "use_when": "Grief, longing, or open questions",
        "example_emotions": ["grief", "longing", "uncertainty"],
    },
    
    # Rhythm
    "RHYTHM_ConstantDisplacement": {
        "description": "Shift pattern one 16th note late/early",
        "effect": "Perpetually off-kilter, unsettling",
        "use_when": "Anxiety, instability, before a shift",
        "example_emotions": ["anxiety", "unease", "anticipation"],
    },
    "RHYTHM_TempoFluctuation": {
        "description": "Gradual ±5 BPM drift over phrase",
        "effect": "Organic breathing, tension/release",
        "use_when": "Human feel, emotional intensity",
        "example_emotions": ["intimacy", "vulnerability"],
    },
    "RHYTHM_MetricModulation": {
        "description": "Temporarily change implied time signature",
        "effect": "Disorientation, complexity",
        "use_when": "Representing mental state change",
        "example_emotions": ["confusion", "transformation"],
    },
    "RHYTHM_PolyrhythmicLayers": {
        "description": "Layer conflicting rhythmic patterns",
        "effect": "Complexity, tension, richness",
        "use_when": "Multiple emotions simultaneously",
        "example_emotions": ["complexity", "internal conflict"],
    },
    "RHYTHM_DroppedBeats": {
        "description": "Remove expected beats/hits",
        "effect": "Surprise, space, emphasis",
        "use_when": "Creating impact through absence",
        "example_emotions": ["shock", "emphasis", "breath"],
    },
    
    # Arrangement
    "ARRANGEMENT_UnbalancedDynamics": {
        "description": "Keep element too loud/quiet for standard",
        "effect": "Intentional imbalance, focus shift",
        "use_when": "Drawing attention or creating discomfort",
        "example_emotions": ["obsession", "imbalance"],
    },
    "ARRANGEMENT_StructuralMismatch": {
        "description": "Use unexpected structure for genre",
        "effect": "Subverted expectations, uniqueness",
        "use_when": "Story requires non-standard form",
        "example_emotions": ["defiance", "uniqueness"],
    },
    "ARRANGEMENT_BuriedVocals": {
        "description": "Place vocals below instruments",
        "effect": "Intimacy, dissociation, texture",
        "use_when": "Vulnerability, dream states",
        "example_emotions": ["dissociation", "intimacy", "dreams"],
    },
    "ARRANGEMENT_ExtremeDynamicRange": {
        "description": "Exceed normal dynamic limits",
        "effect": "Dramatic impact, contrast",
        "use_when": "Emotional crescendos, reveals",
        "example_emotions": ["catharsis", "revelation"],
    },
    "ARRANGEMENT_PrematureClimax": {
        "description": "Put peak earlier than expected",
        "effect": "Subversion, reflection time",
        "use_when": "Aftermath is the point",
        "example_emotions": ["aftermath", "reflection"],
    },
    
    # Production
    "PRODUCTION_ExcessiveMud": {
        "description": "Leave 200-400Hz buildup",
        "effect": "Weight, claustrophobia, heaviness",
        "use_when": "Trapped feelings, density",
        "example_emotions": ["trapped", "heavy", "suffocating"],
    },
    "PRODUCTION_PitchImperfection": {
        "description": "Leave natural pitch drift",
        "effect": "Emotional honesty, vulnerability",
        "use_when": "Raw emotional delivery",
        "example_emotions": ["vulnerability", "honesty", "rawness"],
    },
    "PRODUCTION_RoomNoise": {
        "description": "Keep ambient room sound",
        "effect": "Authenticity, intimacy, place",
        "use_when": "Lo-fi aesthetic, presence",
        "example_emotions": ["intimacy", "authenticity"],
    },
    "PRODUCTION_Distortion": {
        "description": "Allow clipping/saturation",
        "effect": "Aggression, urgency, damage",
        "use_when": "Anger, intensity, decay",
        "example_emotions": ["anger", "damage", "intensity"],
    },
    "PRODUCTION_MonoCollapse": {
        "description": "Intentionally narrow stereo field",
        "effect": "Claustrophobia, focus, intimacy",
        "use_when": "Internal monologue, pressure",
        "example_emotions": ["pressure", "focus", "isolation"],
    },
    "PRODUCTION_LoFiDegradation": {
        "description": "Add tape hiss, bit crush, sample rate reduction",
        "effect": "Nostalgia, memory, distance from reality",
        "use_when": "Representing the past, unreliable memory",
        "example_emotions": ["nostalgia", "memory", "dissociation"],
    },
    "PRODUCTION_SilenceAsInstrument": {
        "description": "Use dramatic silence/dropouts mid-phrase",
        "effect": "Shock, breath, emphasis through absence",
        "use_when": "Creating impact, letting words land",
        "example_emotions": ["shock", "contemplation", "weight"],
    },
    "PRODUCTION_ClippingPeaks": {
        "description": "Allow transients to clip intentionally",
        "effect": "Urgency, damage, rawness",
        "use_when": "Anger, desperation, breaking point",
        "example_emotions": ["rage", "desperation", "breaking"],
    },

    # Melody
    "MELODY_AvoidResolution": {
        "description": "End phrases on non-tonic tones",
        "effect": "Incompleteness, searching, yearning",
        "use_when": "Questions without answers",
        "example_emotions": ["longing", "uncertainty", "searching"],
    },
    "MELODY_ExcessiveRepetition": {
        "description": "Repeat melodic cell obsessively",
        "effect": "Hypnotic, obsessive, ritualistic",
        "use_when": "Spiral thoughts, inability to move on",
        "example_emotions": ["obsession", "anxiety", "ritual"],
    },
    "MELODY_AngularIntervals": {
        "description": "Use wide, awkward interval leaps",
        "effect": "Discomfort, unease, otherness",
        "use_when": "Alienation, confusion, discord",
        "example_emotions": ["alienation", "confusion", "discord"],
    },
    "MELODY_AntiClimax": {
        "description": "Build up then resolve downward/weakly",
        "effect": "Disappointment, deflation, anticlimax",
        "use_when": "Failed expectations, letting go",
        "example_emotions": ["disappointment", "resignation", "deflation"],
    },
    "MELODY_MonotoneDrone": {
        "description": "Minimal melodic movement, near-monotone",
        "effect": "Numbness, dissociation, meditation",
        "use_when": "Emotional shutdown, trance states",
        "example_emotions": ["numbness", "dissociation", "meditation"],
    },
    "MELODY_FragmentedPhrases": {
        "description": "Break melody into disconnected fragments",
        "effect": "Fractured thought, interrupted speech",
        "use_when": "Difficulty expressing, trauma",
        "example_emotions": ["trauma", "confusion", "fragmentation"],
    },

    # Texture
    "TEXTURE_FrequencyMasking": {
        "description": "Let elements fight for same frequencies",
        "effect": "Crowded, competitive, overwhelming",
        "use_when": "Internal voices, crowded thoughts",
        "example_emotions": ["overwhelm", "conflict", "noise"],
    },
    "TEXTURE_SparseEmptiness": {
        "description": "Extreme space between elements",
        "effect": "Isolation, exposure, vulnerability",
        "use_when": "Loneliness, nakedness",
        "example_emotions": ["isolation", "vulnerability", "exposure"],
    },
    "TEXTURE_DenseWall": {
        "description": "Stack elements into undifferentiated mass",
        "effect": "Overwhelming force, loss of self",
        "use_when": "Catharsis, surrender, being swept away",
        "example_emotions": ["catharsis", "surrender", "power"],
    },
    "TEXTURE_ConflictingTimbres": {
        "description": "Combine timbres that traditionally clash",
        "effect": "Dissonance, wrongness, tension",
        "use_when": "Things that don't belong together",
        "example_emotions": ["conflict", "dissonance", "wrongness"],
    },
    "TEXTURE_SingleElementFocus": {
        "description": "Strip away all but one element",
        "effect": "Stark truth, nowhere to hide",
        "use_when": "Confession, revelation",
        "example_emotions": ["honesty", "revelation", "nakedness"],
    },
    "TEXTURE_TimbralDrift": {
        "description": "Gradually morph timbre over time",
        "effect": "Transformation, unease, evolution",
        "use_when": "Change, metamorphosis",
        "example_emotions": ["transformation", "unease", "evolution"],
    },

    # Temporal
    "TEMPORAL_ExtendedIntro": {
        "description": "Unusually long intro before main content",
        "effect": "Anticipation, world-building, patience test",
        "use_when": "Setting scene, building dread",
        "example_emotions": ["anticipation", "dread", "patience"],
    },
    "TEMPORAL_AbruptEnding": {
        "description": "End suddenly without resolution",
        "effect": "Shock, incompleteness, cut-off",
        "use_when": "Sudden loss, unexpected ending",
        "example_emotions": ["shock", "loss", "abruptness"],
    },
    "TEMPORAL_TimeStretch": {
        "description": "Stretch or compress time perception",
        "effect": "Altered reality, time distortion",
        "use_when": "Dream states, altered consciousness",
        "example_emotions": ["dissociation", "dream", "unreality"],
    },
    "TEMPORAL_LoopHypnosis": {
        "description": "Loop beyond comfortable repetition",
        "effect": "Hypnotic, meditative, obsessive",
        "use_when": "Trance, circular thoughts",
        "example_emotions": ["trance", "obsession", "meditation"],
    },
    "TEMPORAL_BreathPauses": {
        "description": "Insert pauses like held breath",
        "effect": "Tension, anticipation, human feel",
        "use_when": "Before revelation, gathering courage",
        "example_emotions": ["anticipation", "courage", "hesitation"],
    },
    "TEMPORAL_AccelerandoDecay": {
        "description": "Speed up then decay/fall apart",
        "effect": "Panic, collapse, exhaustion",
        "use_when": "Overwhelm, breaking point, surrender",
        "example_emotions": ["panic", "exhaustion", "surrender"],
    },
}


# =================================================================
# AFFECT → MODE MAPPING
# =================================================================

AFFECT_MODE_MAP = {
    # Maps emotional states to suggested musical modes
    "grief": {"modes": ["Aeolian", "Phrygian"], "tempo_range": (50, 80), "density": "Sparse"},
    "longing": {"modes": ["Dorian", "Mixolydian"], "tempo_range": (60, 90), "density": "Sparse"},
    "defiance": {"modes": ["Phrygian", "Locrian"], "tempo_range": (100, 140), "density": "Full"},
    "hope": {"modes": ["Ionian", "Lydian"], "tempo_range": (90, 120), "density": "Moderate"},
    "rage": {"modes": ["Phrygian", "Locrian"], "tempo_range": (120, 180), "density": "Dense"},
    "tenderness": {"modes": ["Ionian", "Lydian"], "tempo_range": (60, 85), "density": "Sparse"},
    "anxiety": {"modes": ["Locrian", "Phrygian"], "tempo_range": (90, 130), "density": "Moderate"},
    "euphoria": {"modes": ["Ionian", "Lydian"], "tempo_range": (120, 150), "density": "Full"},
    "melancholy": {"modes": ["Aeolian", "Dorian"], "tempo_range": (60, 90), "density": "Sparse"},
    "nostalgia": {"modes": ["Mixolydian", "Dorian"], "tempo_range": (70, 100), "density": "Moderate"},
    "catharsis": {"modes": ["Aeolian", "Phrygian"], "tempo_range": (80, 130), "density": "Dense"},
    "dissociation": {"modes": ["Lydian", "Locrian"], "tempo_range": (60, 90), "density": "Sparse"},
    "determination": {"modes": ["Ionian", "Mixolydian"], "tempo_range": (100, 130), "density": "Full"},
    "surrender": {"modes": ["Aeolian", "Dorian"], "tempo_range": (50, 75), "density": "Sparse"},
}


# =================================================================
# TEXTURE → PRODUCTION MAPPING
# =================================================================

TEXTURE_PRODUCTION_MAP = {
    # Maps texture types to suggested production characteristics
    "Ethereal": {
        "reverb": "long",
        "delay": "ambient",
        "eq_character": "air",
        "stereo_width": "wide",
        "compression": "light",
    },
    "Intimate": {
        "reverb": "none/room",
        "delay": "none/subtle",
        "eq_character": "presence",
        "stereo_width": "narrow",
        "compression": "moderate",
    },
    "Massive": {
        "reverb": "medium-large",
        "delay": "rhythmic",
        "eq_character": "full",
        "stereo_width": "wide",
        "compression": "heavy",
    },
    "Skeletal": {
        "reverb": "none/room",
        "delay": "none",
        "eq_character": "thin",
        "stereo_width": "mono/narrow",
        "compression": "none",
    },
    "Lush": {
        "reverb": "medium-long",
        "delay": "modulated",
        "eq_character": "warm",
        "stereo_width": "wide",
        "compression": "glue",
    },
    "Harsh": {
        "reverb": "short/none",
        "delay": "none",
        "eq_character": "bright/cutting",
        "stereo_width": "variable",
        "compression": "aggressive",
    },
    "Murky": {
        "reverb": "dark",
        "delay": "degraded",
        "eq_character": "muddy",
        "stereo_width": "mono",
        "compression": "squashed",
    },
    "Crystalline": {
        "reverb": "short/bright",
        "delay": "clean",
        "eq_character": "bright/clear",
        "stereo_width": "precise",
        "compression": "light",
    },
}


# =================================================================
# DATA CLASSES: Song Intent Structure
# =================================================================

@dataclass
class SongRoot:
    """
    Phase 0: The Core Wound/Desire
    
    Deep interrogation to find what the song NEEDS to express.
    """
    core_event: str = ""           # The inciting moment/realization
    core_resistance: str = ""      # What's holding you back
    core_longing: str = ""         # What you ultimately want to feel
    core_stakes: str = ""          # What's at risk
    core_transformation: str = ""  # How you want to feel when done


@dataclass
class SongIntent:
    """
    Phase 1: Emotional & Intent
    
    Validated by Phase 0, guides all technical decisions.
    """
    mood_primary: str = ""                  # Primary emotion
    mood_secondary_tension: float = 0.5     # Tension level 0.0-1.0
    imagery_texture: str = ""               # Visual/tactile quality
    vulnerability_scale: str = "Medium"     # Low/Medium/High
    narrative_arc: str = ""                 # Structural emotion


@dataclass
class TechnicalConstraints:
    """
    Phase 2: Technical Constraints
    
    Implementation of intent into concrete musical decisions.
    """
    technical_genre: str = ""
    technical_tempo_range: Tuple[int, int] = (80, 120)
    technical_key: str = ""
    technical_mode: str = ""
    technical_groove_feel: str = ""
    technical_rule_to_break: str = ""
    rule_breaking_justification: str = ""


@dataclass
class SystemDirective:
    """What DAiW should generate."""
    output_target: str = ""           # What to generate
    output_feedback_loop: str = ""    # Which modules to iterate


@dataclass
class CompleteSongIntent:
    """
    Complete song intent combining all phases.
    
    This is the full specification for a song that DAiW
    uses to generate meaningful, emotionally-aligned output.
    """
    # Phase 0
    song_root: SongRoot = field(default_factory=SongRoot)
    
    # Phase 1
    song_intent: SongIntent = field(default_factory=SongIntent)
    
    # Phase 2
    technical_constraints: TechnicalConstraints = field(default_factory=TechnicalConstraints)
    
    # System
    system_directive: SystemDirective = field(default_factory=SystemDirective)
    
    # Meta
    title: str = ""
    created: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "title": self.title,
            "created": self.created,
            "song_root": {
                "core_event": self.song_root.core_event,
                "core_resistance": self.song_root.core_resistance,
                "core_longing": self.song_root.core_longing,
                "core_stakes": self.song_root.core_stakes,
                "core_transformation": self.song_root.core_transformation,
            },
            "song_intent": {
                "mood_primary": self.song_intent.mood_primary,
                "mood_secondary_tension": self.song_intent.mood_secondary_tension,
                "imagery_texture": self.song_intent.imagery_texture,
                "vulnerability_scale": self.song_intent.vulnerability_scale,
                "narrative_arc": self.song_intent.narrative_arc,
            },
            "technical_constraints": {
                "technical_genre": self.technical_constraints.technical_genre,
                "technical_tempo_range": list(self.technical_constraints.technical_tempo_range),
                "technical_key": self.technical_constraints.technical_key,
                "technical_mode": self.technical_constraints.technical_mode,
                "technical_groove_feel": self.technical_constraints.technical_groove_feel,
                "technical_rule_to_break": self.technical_constraints.technical_rule_to_break,
                "rule_breaking_justification": self.technical_constraints.rule_breaking_justification,
            },
            "system_directive": {
                "output_target": self.system_directive.output_target,
                "output_feedback_loop": self.system_directive.output_feedback_loop,
            },
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CompleteSongIntent":
        """Create from dictionary."""
        intent = cls()
        intent.title = data.get("title", "")
        intent.created = data.get("created", "")
        
        if "song_root" in data:
            root = data["song_root"]
            intent.song_root = SongRoot(
                core_event=root.get("core_event", ""),
                core_resistance=root.get("core_resistance", ""),
                core_longing=root.get("core_longing", ""),
                core_stakes=root.get("core_stakes", ""),
                core_transformation=root.get("core_transformation", ""),
            )
        
        if "song_intent" in data:
            si = data["song_intent"]
            intent.song_intent = SongIntent(
                mood_primary=si.get("mood_primary", ""),
                mood_secondary_tension=si.get("mood_secondary_tension", 0.5),
                imagery_texture=si.get("imagery_texture", ""),
                vulnerability_scale=si.get("vulnerability_scale", "Medium"),
                narrative_arc=si.get("narrative_arc", ""),
            )
        
        if "technical_constraints" in data:
            tc = data["technical_constraints"]
            tempo = tc.get("technical_tempo_range", [80, 120])
            intent.technical_constraints = TechnicalConstraints(
                technical_genre=tc.get("technical_genre", ""),
                technical_tempo_range=tuple(tempo) if isinstance(tempo, list) else tempo,
                technical_key=tc.get("technical_key", ""),
                technical_mode=tc.get("technical_mode", ""),
                technical_groove_feel=tc.get("technical_groove_feel", ""),
                technical_rule_to_break=tc.get("technical_rule_to_break", ""),
                rule_breaking_justification=tc.get("rule_breaking_justification", ""),
            )
        
        if "system_directive" in data:
            sd = data["system_directive"]
            intent.system_directive = SystemDirective(
                output_target=sd.get("output_target", ""),
                output_feedback_loop=sd.get("output_feedback_loop", ""),
            )
        
        return intent
    
    def save(self, path: str):
        """Save to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> "CompleteSongIntent":
        """Load from JSON file."""
        with open(path, 'r') as f:
            return cls.from_dict(json.load(f))


# =================================================================
# HELPER FUNCTIONS
# =================================================================

def suggest_rule_break(emotion: str) -> List[Dict]:
    """
    Suggest appropriate rules to break based on target emotion.
    
    Args:
        emotion: Target emotion (grief, defiance, etc.)
    
    Returns:
        List of rule-breaking suggestions with justifications
    """
    emotion_lower = emotion.lower()
    suggestions = []
    
    for rule_key, rule_data in RULE_BREAKING_EFFECTS.items():
        if any(e in emotion_lower for e in rule_data.get("example_emotions", [])):
            suggestions.append({
                "rule": rule_key,
                "description": rule_data["description"],
                "effect": rule_data["effect"],
                "use_when": rule_data["use_when"],
            })
    
    return suggestions


def get_rule_breaking_info(rule_key: str) -> Optional[Dict]:
    """Get detailed info about a rule-breaking option."""
    return RULE_BREAKING_EFFECTS.get(rule_key)


def validate_intent(intent: CompleteSongIntent) -> List[str]:
    """
    Validate a song intent for completeness and consistency.
    
    Returns list of issues found (empty = valid).
    """
    issues = []
    
    # Phase 0 checks
    if not intent.song_root.core_event:
        issues.append("Phase 0: Missing core_event - what happened?")
    if not intent.song_root.core_longing:
        issues.append("Phase 0: Missing core_longing - what do you want to feel?")
    
    # Phase 1 checks (use enhanced validation)
    phase1_issues = validate_phase1(intent.song_intent)
    issues.extend(phase1_issues)
    
    # Phase 2 checks (use enhanced validation)
    phase2_issues = validate_phase2(intent.technical_constraints)
    issues.extend(phase2_issues)
    
    # Consistency checks
    if intent.song_intent.vulnerability_scale == "High":
        if intent.song_intent.mood_secondary_tension < 0.3:
            issues.append("Consistency: High vulnerability usually implies some tension (tension is very low)")
    
    return issues


def list_all_rules() -> Dict[str, List[str]]:
    """Get all available rule-breaking options by category."""
    return {
        "Harmony": [e.value for e in HarmonyRuleBreak],
        "Rhythm": [e.value for e in RhythmRuleBreak],
        "Arrangement": [e.value for e in ArrangementRuleBreak],
        "Production": [e.value for e in ProductionRuleBreak],
        "Melody": [e.value for e in MelodyRuleBreak],
        "Texture": [e.value for e in TextureRuleBreak],
        "Temporal": [e.value for e in TemporalRuleBreak],
    }


def get_affect_mapping(emotion: str) -> Optional[Dict]:
    """
    Get musical parameter suggestions for an emotional state.

    Args:
        emotion: The target emotion (grief, hope, etc.)

    Returns:
        Dict with modes, tempo_range, density suggestions or None if not found
    """
    return AFFECT_MODE_MAP.get(emotion.lower())


def get_texture_production(texture: str) -> Optional[Dict]:
    """
    Get production parameter suggestions for a texture type.

    Args:
        texture: The target texture (Ethereal, Intimate, etc.)

    Returns:
        Dict with reverb, delay, eq, stereo, compression suggestions or None
    """
    return TEXTURE_PRODUCTION_MAP.get(texture)


def suggest_full_palette(emotion: str) -> Dict:
    """
    Get a complete musical palette suggestion for an emotion.

    Combines affect mapping, rule suggestions, and texture recommendations.

    Args:
        emotion: Target emotion

    Returns:
        Dict with modes, tempo, density, suggested_rules, texture recommendations
    """
    result = {
        "emotion": emotion,
        "affect_mapping": get_affect_mapping(emotion),
        "suggested_rules": suggest_rule_break(emotion),
        "texture_options": [],
    }

    # Suggest textures based on emotion
    emotion_texture_map = {
        "grief": ["Murky", "Skeletal", "Ethereal"],
        "longing": ["Ethereal", "Intimate", "Lush"],
        "defiance": ["Harsh", "Massive", "Crystalline"],
        "hope": ["Ethereal", "Lush", "Crystalline"],
        "rage": ["Harsh", "Dense", "Massive"],
        "tenderness": ["Intimate", "Lush", "Ethereal"],
        "anxiety": ["Harsh", "Skeletal", "Murky"],
        "euphoria": ["Massive", "Lush", "Crystalline"],
        "melancholy": ["Murky", "Ethereal", "Intimate"],
        "nostalgia": ["Murky", "Intimate", "Lush"],
        "catharsis": ["Massive", "Dense", "Ethereal"],
        "dissociation": ["Ethereal", "Murky", "Skeletal"],
        "determination": ["Massive", "Crystalline", "Full"],
        "surrender": ["Ethereal", "Skeletal", "Intimate"],
    }

    textures = emotion_texture_map.get(emotion.lower(), [])
    for tex in textures:
        prod = get_texture_production(tex)
        if prod:
            result["texture_options"].append({
                "texture": tex,
                "production": prod,
            })

    return result


def load_schema_options() -> Dict[str, List[str]]:
    """
    Load enum options from song_intent_schema.yaml.
    
    Returns:
        Dict mapping option names to lists of valid values
    """
    schema_path = Path(__file__).parent.parent / "data" / "song_intent_schema.yaml"
    
    if not HAS_YAML:
        # Fallback to hardcoded values if PyYAML not available
        return _get_fallback_options()
    
    try:
        with open(schema_path, 'r') as f:
            data = yaml.safe_load(f)
        
        enums = data.get("enums", {})
        return {
            "mood_primary": enums.get("mood_primary_options", []),
            "imagery_texture": enums.get("imagery_texture_options", []),
            "vulnerability_scale": enums.get("vulnerability_scale_options", []),
            "narrative_arc": enums.get("narrative_arc_options", []),
            "core_stakes": enums.get("core_stakes_options", []),
            "genre": enums.get("genre_options", []),
            "groove_feel": enums.get("groove_feel_options", []),
        }
    except Exception as e:
        # Fallback to hardcoded values if YAML can't be loaded
        return _get_fallback_options()


def _get_fallback_options() -> Dict[str, List[str]]:
    """Fallback options if YAML can't be loaded."""
    return {
        "mood_primary": ["Grief", "Joy", "Defiance", "Longing", "Rage", "Nostalgia", "Melancholy", "Euphoria", "Desperation", "Serenity", "Confusion", "Determination", "Bittersweet", "Triumphant Hope", "Dissociation", "Acceptance", "Liberation", "Nervousness"],
        "imagery_texture": ["Sharp Edges", "Muffled", "Open/Vast", "Claustrophobic", "Hazy/Dreamy", "Crystalline", "Muddy/Thick", "Sparse/Empty", "Chaotic", "Flowing/Liquid", "Fractured", "Warm/Enveloping", "Cold/Distant", "Blinding Light", "Deep Shadow"],
        "vulnerability_scale": ["Low", "Medium", "High"],
        "narrative_arc": ["Climb-to-Climax", "Slow Reveal", "Repetitive Despair", "Static Reflection", "Sudden Shift", "Descent", "Rise and Fall", "Spiral"],
        "core_stakes": ["Personal", "Relational", "Existential", "Survival", "Creative", "Moral"],
        "genre": ["Cinematic Neo-Soul", "Lo-Fi Bedroom", "Industrial Pop", "Synthwave", "Confessional Acoustic", "Art Rock", "Indie Folk", "Post-Punk", "Chamber Pop", "Electronic", "Hip-Hop", "R&B", "Alternative", "Shoegaze", "Dream Pop"],
        "groove_feel": ["Straight/Driving", "Laid Back", "Swung", "Syncopated", "Rubato/Free", "Mechanical", "Organic/Breathing", "Push-Pull"],
    }


def collect_phase1_interactive(song_root: Optional[SongRoot] = None) -> SongIntent:
    """
    Interactively collect Phase 1 (Emotional Intent) data from user.
    
    Args:
        song_root: Optional Phase 0 data to inform questions
    
    Returns:
        SongIntent with collected data
    """
    options = load_schema_options()
    
    print("\n" + "=" * 60)
    print("PHASE 1: EMOTIONAL & INTENT")
    print("=" * 60)
    print("\nValidated by Phase 0, guides all technical decisions.\n")
    
    # Mood Primary
    print("1. PRIMARY EMOTION")
    print("   What's the dominant emotion?")
    if options["mood_primary"]:
        print(f"   Options: {', '.join(options['mood_primary'][:10])}...")
        print("   (You can type your own or choose from the list)")
    mood_primary = input("   > ").strip()
    if not mood_primary:
        mood_primary = "[Primary emotion]"
    
    # Secondary Tension
    print("\n2. SECONDARY TENSION (0.0 - 1.0)")
    print("   Internal conflict level:")
    print("   0.0 = calm, resolved")
    print("   0.5 = balanced tension")
    print("   1.0 = anxious, high tension")
    while True:
        try:
            tension_input = input("   > ").strip()
            if not tension_input:
                mood_secondary_tension = 0.5
                break
            mood_secondary_tension = float(tension_input)
            if 0.0 <= mood_secondary_tension <= 1.0:
                break
            else:
                print("   Please enter a value between 0.0 and 1.0")
        except ValueError:
            print("   Please enter a number between 0.0 and 1.0")
    
    # Imagery Texture
    print("\n3. IMAGERY TEXTURE")
    print("   Visual/tactile quality - how should this song FEEL?")
    if options["imagery_texture"]:
        print("   Options:")
        for i, opt in enumerate(options["imagery_texture"], 1):
            print(f"   {i}. {opt}")
        print("   (You can type your own or choose from the list)")
    imagery_texture = input("   > ").strip()
    if not imagery_texture:
        imagery_texture = "[Visual/tactile quality]"
    
    # Vulnerability Scale
    print("\n4. VULNERABILITY SCALE")
    print("   How exposed should this song be?")
    if options["vulnerability_scale"]:
        for i, opt in enumerate(options["vulnerability_scale"], 1):
            desc = {
                "Low": "Guarded, protective",
                "Medium": "Honest but controlled",
                "High": "Raw, exposed"
            }.get(opt, "")
            print(f"   {i}. {opt} - {desc}")
    while True:
        vuln_input = input("   > ").strip()
        if not vuln_input:
            vulnerability_scale = "Medium"
            break
        vuln_lower = vuln_input.lower()
        if vuln_lower in ["low", "medium", "high"]:
            vulnerability_scale = vuln_input.capitalize()
            break
        elif vuln_input in options["vulnerability_scale"]:
            vulnerability_scale = vuln_input
            break
        else:
            print("   Please enter: Low, Medium, or High")
    
    # Narrative Arc
    print("\n5. NARRATIVE ARC")
    print("   How should the emotion evolve structurally?")
    if options["narrative_arc"]:
        print("   Options:")
        for i, opt in enumerate(options["narrative_arc"], 1):
            print(f"   {i}. {opt}")
        print("   (You can type your own or choose from the list)")
    narrative_arc = input("   > ").strip()
    if not narrative_arc:
        narrative_arc = "Climb-to-Climax"
    
    print("\n" + "=" * 60)
    print("Phase 1 Complete!")
    print("=" * 60 + "\n")
    
    return SongIntent(
        mood_primary=mood_primary,
        mood_secondary_tension=mood_secondary_tension,
        imagery_texture=imagery_texture,
        vulnerability_scale=vulnerability_scale,
        narrative_arc=narrative_arc,
    )


def validate_phase1(song_intent: SongIntent) -> List[str]:
    """
    Validate Phase 1 fields against schema options.
    
    Returns list of validation issues (empty = valid).
    """
    issues = []
    options = load_schema_options()
    
    # Validate mood_primary
    if not song_intent.mood_primary or song_intent.mood_primary.startswith("["):
        issues.append("Phase 1: mood_primary is required")
    elif options["mood_primary"] and song_intent.mood_primary not in options["mood_primary"]:
        # Warn but don't fail - allow custom emotions
        pass
    
    # Validate mood_secondary_tension
    if not (0.0 <= song_intent.mood_secondary_tension <= 1.0):
        issues.append("Phase 1: mood_secondary_tension must be between 0.0 and 1.0")
    
    # Validate imagery_texture
    if not song_intent.imagery_texture or song_intent.imagery_texture.startswith("["):
        issues.append("Phase 1: imagery_texture is required")
    
    # Validate vulnerability_scale
    if song_intent.vulnerability_scale not in options["vulnerability_scale"]:
        issues.append(f"Phase 1: vulnerability_scale must be one of {options['vulnerability_scale']}")
    
    # Validate narrative_arc
    if not song_intent.narrative_arc or song_intent.narrative_arc.startswith("["):
        issues.append("Phase 1: narrative_arc is required")
    
    return issues


# =================================================================
# PHASE 2 HELPER FUNCTIONS
# =================================================================

# Note names for key validation
NOTE_NAMES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTE_NAMES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
ALL_NOTE_NAMES = set(NOTE_NAMES_SHARP + NOTE_NAMES_FLAT)

# Valid mode names
VALID_MODES = {
    'major', 'minor', 'ionian', 'dorian', 'phrygian', 
    'lydian', 'mixolydian', 'aeolian', 'locrian'
}


def suggest_phase2_from_phase1(song_intent: SongIntent) -> Dict:
    """
    Suggest Phase 2 technical constraints based on Phase 1 emotional intent.
    
    Uses Phase 1 data to suggest appropriate technical parameters.
    
    Args:
        song_intent: Phase 1 SongIntent data
    
    Returns:
        Dict with suggested values for Phase 2 fields
    """
    suggestions = {
        "technical_genre": "",
        "technical_tempo_range": (80, 120),
        "technical_key": "",
        "technical_mode": "",
        "technical_groove_feel": "",
        "technical_rule_to_break": "",
        "rule_breaking_justification": "",
    }
    
    # Get affect mapping from mood_primary
    if song_intent.mood_primary:
        affect = get_affect_mapping(song_intent.mood_primary.lower())
        if affect:
            # Suggest tempo range from affect mapping
            if "tempo_range" in affect:
                suggestions["technical_tempo_range"] = affect["tempo_range"]
            
            # Suggest mode from affect mapping
            if "modes" in affect and affect["modes"]:
                # Use first suggested mode
                mode_name = affect["modes"][0].lower()
                # Convert to common format
                if mode_name == "ionian":
                    suggestions["technical_mode"] = "major"
                elif mode_name == "aeolian":
                    suggestions["technical_mode"] = "minor"
                else:
                    suggestions["technical_mode"] = mode_name.capitalize()
    
    # Suggest rule to break from emotion
    if song_intent.mood_primary:
        rule_suggestions = suggest_rule_break(song_intent.mood_primary)
        if rule_suggestions:
            suggestions["technical_rule_to_break"] = rule_suggestions[0]["rule"]
    
    # Suggest genre/groove from imagery texture
    if song_intent.imagery_texture:
        # Map texture to genre suggestions
        texture_genre_map = {
            "Muffled": "Lo-Fi Bedroom",
            "Open/Vast": "Cinematic Neo-Soul",
            "Sharp Edges": "Industrial Pop",
            "Hazy/Dreamy": "Dream Pop",
            "Crystalline": "Shoegaze",
            "Muddy/Thick": "Post-Punk",
            "Sparse/Empty": "Confessional Acoustic",
            "Warm/Enveloping": "Chamber Pop",
            "Cold/Distant": "Synthwave",
        }
        for texture_key, genre in texture_genre_map.items():
            if texture_key.lower() in song_intent.imagery_texture.lower():
                suggestions["technical_genre"] = genre
                break
    
    # Suggest groove feel from narrative arc
    arc_groove_map = {
        "Climb-to-Climax": "Straight/Driving",
        "Slow Reveal": "Organic/Breathing",
        "Repetitive Despair": "Mechanical",
        "Static Reflection": "Rubato/Free",
        "Sudden Shift": "Push-Pull",
        "Descent": "Laid Back",
        "Rise and Fall": "Swung",
        "Spiral": "Syncopated",
    }
    if song_intent.narrative_arc:
        for arc_key, groove in arc_groove_map.items():
            if arc_key.lower() in song_intent.narrative_arc.lower():
                suggestions["technical_groove_feel"] = groove
                break
    
    return suggestions


def validate_key(key: str) -> Tuple[bool, Optional[str]]:
    """
    Validate musical key format.
    
    Accepts formats like "C", "C#", "F minor", "E major", "Db", etc.
    
    Args:
        key: Key string to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not key or not key.strip():
        return (False, "Key cannot be empty")
    
    key = key.strip()
    
    # Check if it's in format "Note" or "Note mode"
    parts = key.split()
    
    if len(parts) == 1:
        # Just note name
        note_part = parts[0]
    elif len(parts) == 2:
        # Note and mode (e.g., "C minor", "F# major")
        note_part = parts[0]
        mode_part = parts[1].lower()
        if mode_part not in ["major", "minor"]:
            return (False, f"Mode '{mode_part}' not recognized. Use 'major' or 'minor'")
    else:
        return (False, "Key format should be 'Note' or 'Note mode' (e.g., 'C' or 'F minor')")
    
    # Validate note name
    if note_part not in ALL_NOTE_NAMES:
        return (False, f"Note '{note_part}' not recognized. Use standard note names like C, C#, Db, etc.")
    
    return (True, None)


def validate_mode(mode: str) -> Tuple[bool, Optional[str]]:
    """
    Validate mode format.
    
    Accepts: major, minor, and modal names (Dorian, Phrygian, Lydian, 
    Mixolydian, Aeolian, Locrian, Ionian). Case-insensitive.
    
    Args:
        mode: Mode string to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not mode or not mode.strip():
        return (False, "Mode cannot be empty")
    
    mode_lower = mode.strip().lower()
    
    if mode_lower not in VALID_MODES:
        return (False, f"Mode '{mode}' not recognized. Valid modes: {', '.join(sorted(VALID_MODES))}")
    
    return (True, None)


def suggest_key_from_mode(mode: str) -> List[str]:
    """
    Suggest common keys for a given mode.
    
    Args:
        mode: Mode name (major, minor, Dorian, etc.)
    
    Returns:
        List of suggested key names
    """
    mode_lower = mode.lower()
    
    # Common keys for different modes
    if mode_lower in ["major", "ionian", "lydian", "mixolydian"]:
        # Bright keys work well
        return ["C", "G", "D", "F", "A"]
    elif mode_lower in ["minor", "aeolian", "dorian", "phrygian"]:
        # Darker keys
        return ["A", "E", "D", "G", "C"]
    elif mode_lower == "locrian":
        # Locrian is rare, suggest less common keys
        return ["B", "F#", "C#"]
    else:
        # Default suggestions
        return ["C", "G", "D", "F", "A", "E"]


def collect_phase2_interactive(
    song_intent: Optional[SongIntent] = None, 
    song_root: Optional[SongRoot] = None
) -> TechnicalConstraints:
    """
    Interactively collect Phase 2 (Technical Constraints) data from user.
    
    Args:
        song_intent: Optional Phase 1 data to inform suggestions
        song_root: Optional Phase 0 data for context
    
    Returns:
        TechnicalConstraints with collected data
    """
    options = load_schema_options()
    
    print("\n" + "=" * 60)
    print("PHASE 2: TECHNICAL CONSTRAINTS")
    print("=" * 60)
    print("\nImplementation of intent into concrete musical decisions.\n")
    
    # Show suggestions from Phase 1 if available
    suggestions = {}
    if song_intent:
        suggestions = suggest_phase2_from_phase1(song_intent)
        print("💡 Suggestions based on Phase 1:")
        if suggestions.get("technical_tempo_range"):
            print(f"   Tempo: {suggestions['technical_tempo_range'][0]}-{suggestions['technical_tempo_range'][1]} BPM")
        if suggestions.get("technical_mode"):
            print(f"   Mode: {suggestions['technical_mode']}")
        if suggestions.get("technical_genre"):
            print(f"   Genre: {suggestions['technical_genre']}")
        if suggestions.get("technical_groove_feel"):
            print(f"   Groove: {suggestions['technical_groove_feel']}")
        if suggestions.get("technical_rule_to_break"):
            print(f"   Rule to break: {suggestions['technical_rule_to_break']}")
        print()
    
    # 1. Genre
    print("1. GENRE")
    print("   What genre/style should this song be?")
    if options["genre"]:
        print("   Options:")
        for i, genre in enumerate(options["genre"], 1):
            print(f"   {i}. {genre}")
        print("   (You can type your own or choose from the list)")
    genre_input = input("   > ").strip()
    if not genre_input:
        technical_genre = suggestions.get("technical_genre", "[Genre]")
    else:
        technical_genre = genre_input
    
    # 2. Tempo Range
    print("\n2. TEMPO RANGE (BPM)")
    print("   Enter minimum and maximum BPM (e.g., 80 120)")
    if suggestions.get("technical_tempo_range"):
        print(f"   Suggested: {suggestions['technical_tempo_range'][0]}-{suggestions['technical_tempo_range'][1]} BPM")
    while True:
        tempo_input = input("   > ").strip()
        if not tempo_input:
            if suggestions.get("technical_tempo_range"):
                technical_tempo_range = suggestions["technical_tempo_range"]
                break
            technical_tempo_range = (80, 120)
            break
        
        try:
            parts = tempo_input.split()
            if len(parts) == 2:
                low = int(parts[0])
                high = int(parts[1])
                if 40 <= low <= 240 and 40 <= high <= 240:
                    if low < high:
                        technical_tempo_range = (low, high)
                        break
                    else:
                        print("   Minimum must be less than maximum")
                else:
                    print("   BPM must be between 40 and 240")
            else:
                print("   Please enter two numbers: min max")
        except ValueError:
            print("   Please enter valid numbers")
    
    # 3. Mode
    print("\n3. MODE")
    print("   What mode? (major, minor, Dorian, Lydian, etc.)")
    print("   Valid modes: major, minor, Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian")
    if suggestions.get("technical_mode"):
        print(f"   Suggested: {suggestions['technical_mode']}")
    while True:
        mode_input = input("   > ").strip()
        if not mode_input:
            if suggestions.get("technical_mode"):
                technical_mode = suggestions["technical_mode"]
                break
            technical_mode = "major"
            break
        
        is_valid, error = validate_mode(mode_input)
        if is_valid:
            technical_mode = mode_input
            break
        else:
            print(f"   {error}")
    
    # 4. Key
    print("\n4. KEY")
    print("   What key? (e.g., C, F#, E minor, Db major)")
    key_suggestions = suggest_key_from_mode(technical_mode)
    if key_suggestions:
        print(f"   Suggested keys for {technical_mode}: {', '.join(key_suggestions[:5])}")
    while True:
        key_input = input("   > ").strip()
        if not key_input:
            technical_key = key_suggestions[0] if key_suggestions else "C"
            break
        
        is_valid, error = validate_key(key_input)
        if is_valid:
            technical_key = key_input
            break
        else:
            print(f"   {error}")
    
    # 5. Groove Feel
    print("\n5. GROOVE FEEL")
    print("   What rhythmic feel?")
    if options["groove_feel"]:
        print("   Options:")
        for i, opt in enumerate(options["groove_feel"], 1):
            marker = " ← suggested" if suggestions and suggestions.get("technical_groove_feel") == opt else ""
            print(f"   {i}. {opt}{marker}")
    groove_input = input("   > ").strip()
    if not groove_input:
        technical_groove_feel = suggestions.get("technical_groove_feel", "") if suggestions else ""
    elif groove_input.isdigit() and options["groove_feel"]:
        idx = int(groove_input) - 1
        if 0 <= idx < len(options["groove_feel"]):
            technical_groove_feel = options["groove_feel"][idx]
        else:
            technical_groove_feel = groove_input
    else:
        technical_groove_feel = groove_input
    
    # 6. Rule to Break
    print("\n6. RULE TO BREAK")
    print("   What musical rule should be intentionally broken? (Optional)")
    print("   Type 'list' to see all categories, or 'skip' to skip")
    if suggestions and suggestions.get("technical_rule_to_break"):
        rule_info = get_rule_breaking_info(suggestions['technical_rule_to_break'])
        if rule_info:
            print(f"   Suggested: {suggestions['technical_rule_to_break']}")
            print(f"      {rule_info.get('description', '')}")
            print(f"      Effect: {rule_info.get('effect', '')}")
    
    # Show suggestions from Phase 1
    if song_intent and song_intent.mood_primary:
        rule_suggestions = suggest_rule_break(song_intent.mood_primary)
        if rule_suggestions:
            print("   Suggested rules for your emotion:")
            for i, rule in enumerate(rule_suggestions[:3], 1):
                print(f"   {i}. {rule['rule']} - {rule['effect']}")
    
    print("   Type 'list' to see all available rules")
    rule_input = input("   > ").strip()
    
    if rule_input.lower() == "list":
        all_rules = list_all_rules()
        print("\n   Available rules to break:")
        for category, rules in all_rules.items():
            print(f"\n   {category}:")
            for rule in rules:
                rule_info = get_rule_breaking_info(rule)
                if rule_info:
                    print(f"     - {rule}: {rule_info['effect']}")
        print()
        rule_input = input("   Enter rule to break (or press Enter to skip): ").strip()
    
    technical_rule_to_break = rule_input if rule_input else ""
    
    # 7. Justification (required if rule selected)
    rule_breaking_justification = ""
    if technical_rule_to_break:
        print("\n7. RULE BREAKING JUSTIFICATION")
        print("   WHY break this rule? What emotional effect does it serve?")
        rule_info = get_rule_breaking_info(technical_rule_to_break)
        if rule_info:
            print(f"   Rule: {rule_info['description']}")
            print(f"   Effect: {rule_info['effect']}")
            print(f"   Use when: {rule_info['use_when']}")
        while True:
            justification_input = input("   > ").strip()
            if justification_input:
                rule_breaking_justification = justification_input
                break
            else:
                print("   Justification is required when a rule is selected. Please explain WHY.")
    
    print("\n" + "=" * 60)
    print("Phase 2 Complete!")
    print("=" * 60 + "\n")
    
    return TechnicalConstraints(
        technical_genre=technical_genre,
        technical_tempo_range=technical_tempo_range,
        technical_key=technical_key,
        technical_mode=technical_mode,
        technical_groove_feel=technical_groove_feel,
        technical_rule_to_break=technical_rule_to_break,
        rule_breaking_justification=rule_breaking_justification,
    )


def validate_phase2(technical_constraints: TechnicalConstraints) -> List[str]:
    """
    Validate Phase 2 fields against schema options and constraints.
    
    Returns list of validation issues (empty = valid).
    """
    issues = []
    options = load_schema_options()
    
    # Validate technical_genre (warn if custom but don't fail)
    if not technical_constraints.technical_genre or technical_constraints.technical_genre.startswith("["):
        issues.append("Phase 2: technical_genre is required")
    elif options["genre"] and technical_constraints.technical_genre not in options["genre"]:
        # Allow custom genres but could warn
        pass
    
    # Validate tempo_range
    tempo_range = technical_constraints.technical_tempo_range
    if not isinstance(tempo_range, tuple) or len(tempo_range) != 2:
        issues.append("Phase 2: technical_tempo_range must be a tuple of 2 integers")
    else:
        low, high = tempo_range
        if not isinstance(low, int) or not isinstance(high, int):
            issues.append("Phase 2: technical_tempo_range values must be integers")
        else:
            if low >= high:  # pyright: ignore[reportUndefinedVariable]
                issues.append("Phase 2: technical_tempo_range minimum must be less than maximum")
            if not (40 <= low <= 240):
                issues.append("Phase 2: technical_tempo_range minimum must be between 40 and 240 BPM")
            if not (40 <= high <= 240):
                issues.append("Phase 2: technical_tempo_range maximum must be between 40 and 240 BPM")
    
    # Validate technical_key
    if not technical_constraints.technical_key or technical_constraints.technical_key.startswith("["):
        issues.append("Phase 2: technical_key is required")
    else:
        is_valid, error = validate_key(technical_constraints.technical_key)
        if not is_valid:
            issues.append(f"Phase 2: technical_key - {error}")
    
    # Validate technical_mode
    if not technical_constraints.technical_mode or technical_constraints.technical_mode.startswith("["):
        issues.append("Phase 2: technical_mode is required")
    else:
        is_valid, error = validate_mode(technical_constraints.technical_mode)
        if not is_valid:
            issues.append(f"Phase 2: technical_mode - {error}")
    
    # Validate technical_groove_feel
    if not technical_constraints.technical_groove_feel or technical_constraints.technical_groove_feel.startswith("["):
        issues.append("Phase 2: technical_groove_feel is required")
    elif options["groove_feel"] and technical_constraints.technical_groove_feel not in options["groove_feel"]:
        # Allow custom groove feels but could warn
        pass
    
    # Validate technical_rule_to_break
        if technical_constraints.technical_rule_to_break:
            # Check if it's a valid rule enum value
            all_rules = list_all_rules()
            all_rule_values = []
            for category_rules in all_rules.values():
                all_rule_values.extend(category_rules)
        if technical_constraints.technical_rule_to_break not in all_rule_values:
            issues.append(f"Phase 2: technical_rule_to_break '{technical_constraints.technical_rule_to_break}' is not a valid rule")
        
        
        if not technical_constraints.rule_breaking_justification or technical_constraints.rule_breaking_justification.startswith("["):
            issues.append("Phase 2: rule_breaking_justification is required when technical_rule_to_break is set")
    
    return issues
