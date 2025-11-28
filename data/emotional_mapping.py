#!/usr/bin/env python3
"""
Emotional → Musical Parameter Mapping

Maps emotional states (valence, arousal, intrusions) to musical parameters
(tempo, mode, dissonance, timing feel, etc.)

Philosophy: "Interrogate Before Generate"
- Preserve human imperfection
- Teach theory in context
- Match emotion to harmony

Reference: "When I Found You Sleeping" by Kelly
- D minor, 82 BPM, F-C-Am-Dm (misdirection technique)
- Behind-the-beat timing, ±30-50ms drift
- Lo-fi bedroom emo aesthetic
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class TimingFeel(Enum):
    """Timing feel relative to beat"""
    BEHIND = "behind"  # Laid back, reflective (lo-fi, bedroom emo)
    ON = "on"  # Precise, focused (pop, electronic)
    AHEAD = "ahead"  # Urgent, anxious (punk, thrash)


class Register(Enum):
    """Pitch register"""
    LOW = "low"  # Below middle C
    MID = "mid"  # Around middle C
    HIGH = "high"  # Above middle C


class HarmonicRhythm(Enum):
    """Rate of chord changes"""
    SLOW = "slow"  # 1-2 chords per bar
    MEDIUM = "medium"  # 2-4 chords per bar
    FAST = "fast"  # 4+ chords per bar


class Density(Enum):
    """Note density"""
    SPARSE = "sparse"  # Minimalist, lots of space
    MEDIUM = "medium"  # Balanced
    DENSE = "dense"  # Busy, complex


@dataclass
class EmotionalState:
    """
    Represents an emotional state for mapping to musical parameters.

    Attributes:
        valence: Negative (-1) to positive (+1) emotional tone
        arousal: Calm (0) to energetic (1) activation level
        primary_emotion: Main emotion (grief, anger, anxiety, etc.)
        secondary_emotions: Supporting emotions
        has_intrusions: PTSD/trauma intrusions present
        intrusion_probability: Likelihood of intrusion events (0-1)
    """
    valence: float  # -1 (negative) to +1 (positive)
    arousal: float  # 0 (calm) to 1 (energetic)
    primary_emotion: str
    secondary_emotions: List[str] = field(default_factory=list)
    has_intrusions: bool = False
    intrusion_probability: float = 0.0

    def __post_init__(self):
        """Validate ranges"""
        assert -1 <= self.valence <= 1, "Valence must be in [-1, 1]"
        assert 0 <= self.arousal <= 1, "Arousal must be in [0, 1]"
        assert 0 <= self.intrusion_probability <= 1, "Intrusion probability in [0, 1]"


@dataclass
class MusicalParameters:
    """
    Musical parameters derived from emotional state.

    Tempo, mode, register, dissonance, timing feel, etc.
    Used to guide composition and performance.
    """
    tempo_min: int
    tempo_max: int
    tempo_suggested: int
    mode_weights: Dict[str, float]  # {mode: probability}
    register: Register
    harmonic_rhythm: HarmonicRhythm
    dissonance: float  # 0-1 (0=consonant, 1=max dissonance)
    timing_feel: TimingFeel
    density: Density
    dynamics: str  # pp, p, mp, mf, f, ff
    space_probability: float  # 0-1 (silence percentage)

    def __post_init__(self):
        """Validate and normalize mode_weights"""
        assert 0 <= self.dissonance <= 1, "Dissonance must be in [0, 1]"
        assert 0 <= self.space_probability <= 1, "Space probability in [0, 1]"

        # Normalize mode weights to sum to 1.0
        total = sum(self.mode_weights.values())
        if total > 0:
            self.mode_weights = {
                mode: weight / total
                for mode, weight in self.mode_weights.items()
            }


# Emotional presets: Common emotional states → musical parameters
EMOTIONAL_PRESETS: Dict[str, MusicalParameters] = {
    "grief": MusicalParameters(
        tempo_min=60,
        tempo_max=82,
        tempo_suggested=72,
        mode_weights={
            "minor": 0.6,
            "dorian": 0.3,
            "phrygian": 0.1,
        },
        register=Register.MID,
        harmonic_rhythm=HarmonicRhythm.SLOW,
        dissonance=0.3,
        timing_feel=TimingFeel.BEHIND,
        density=Density.SPARSE,
        dynamics="p",
        space_probability=0.3,
    ),
    "anxiety": MusicalParameters(
        tempo_min=100,
        tempo_max=140,
        tempo_suggested=120,
        mode_weights={
            "phrygian": 0.5,
            "locrian": 0.3,
            "minor": 0.2,
        },
        register=Register.HIGH,
        harmonic_rhythm=HarmonicRhythm.FAST,
        dissonance=0.6,
        timing_feel=TimingFeel.AHEAD,
        density=Density.DENSE,
        dynamics="f",
        space_probability=0.1,
    ),
    "nostalgia": MusicalParameters(
        tempo_min=70,
        tempo_max=90,
        tempo_suggested=82,
        mode_weights={
            "mixolydian": 0.5,
            "major": 0.3,
            "dorian": 0.2,
        },
        register=Register.MID,
        harmonic_rhythm=HarmonicRhythm.MEDIUM,
        dissonance=0.25,
        timing_feel=TimingFeel.BEHIND,
        density=Density.MEDIUM,
        dynamics="mp",
        space_probability=0.2,
    ),
    "anger": MusicalParameters(
        tempo_min=120,
        tempo_max=160,
        tempo_suggested=140,
        mode_weights={
            "phrygian": 0.5,
            "locrian": 0.3,
            "minor": 0.2,
        },
        register=Register.LOW,
        harmonic_rhythm=HarmonicRhythm.MEDIUM,
        dissonance=0.5,
        timing_feel=TimingFeel.AHEAD,
        density=Density.DENSE,
        dynamics="ff",
        space_probability=0.05,
    ),
    "calm": MusicalParameters(
        tempo_min=60,
        tempo_max=80,
        tempo_suggested=70,
        mode_weights={
            "major": 0.5,
            "lydian": 0.3,
            "mixolydian": 0.2,
        },
        register=Register.MID,
        harmonic_rhythm=HarmonicRhythm.SLOW,
        dissonance=0.1,
        timing_feel=TimingFeel.BEHIND,
        density=Density.SPARSE,
        dynamics="pp",
        space_probability=0.4,
    ),
}


# Emotion modifiers: Special techniques for complex emotional states
EMOTION_MODIFIERS: Dict[str, Dict] = {
    "ptsd_intrusion": {
        "description": "Sudden, disruptive musical events (trauma flashbacks)",
        "intrusion_probability": 0.15,
        "types": [
            "register_spike",  # Sudden jump to high register
            "harmonic_rush",  # Rapid chord progression
            "unresolved_dissonance",  # Tension without release
            "silence_break",  # Abrupt silence
        ],
        "intensity_multiplier": 2.0,
        "duration_range": (0.5, 2.0),  # seconds
    },
    "misdirection": {
        "description": "Major → minor tonic (Kelly song technique)",
        "progression_pattern": ["major", "major", "minor_relative", "minor_tonic"],
        "emotional_impact": "Hope → reality check",
        "example": "F-C-Am-Dm (in D minor)",
    },
    "dissociation": {
        "description": "Emotional numbness, disconnection",
        "effects": {
            "dynamics": "reduce by 30%",
            "register": "narrow range",
            "space_probability": "increase by 0.2",
            "timing_drift": "increase by 50%",
        },
    },
    "suppressed": {
        "description": "Held-back emotion, tension without release",
        "effects": {
            "dissonance": "increase by 0.2",
            "unresolved_cadences": 0.7,  # 70% of phrases end unresolved
            "dynamics": "stay below mf",
        },
    },
}


# Interval emotions: Interval → tension/emotion mapping
# Values represent tension level (0=consonant, 1=max tension)
INTERVAL_EMOTIONS: Dict[str, float] = {
    "P1": 0.0,  # Perfect unison (no tension)
    "m2": 0.9,  # Minor 2nd (high tension, cluster)
    "M2": 0.2,  # Major 2nd (gentle tension)
    "m3": 0.4,  # Minor 3rd (sad but stable)
    "M3": 0.1,  # Major 3rd (bright, consonant)
    "P4": 0.15,  # Perfect 4th (stable suspension)
    "tritone": 1.0,  # Augmented 4th/diminished 5th (max tension)
    "P5": 0.1,  # Perfect 5th (very stable)
    "m6": 0.5,  # Minor 6th (yearning)
    "M6": 0.2,  # Major 6th (open, hopeful)
    "m7": 0.6,  # Minor 7th (bluesy tension)
    "M7": 0.85,  # Major 7th (sharp dissonance)
    "P8": 0.0,  # Perfect octave (no tension)
}


# Chord progression emotions (common progressions and their feelings)
CHORD_PROGRESSION_EMOTIONS: Dict[str, Dict] = {
    "i-VII-VI-VII": {
        "emotion": "dorian drift",
        "feeling": "Melancholic wandering (Scarborough Fair)",
        "mode": "dorian",
    },
    "I-V-vi-IV": {
        "emotion": "pop optimism",
        "feeling": "Hopeful, uplifting (Don't Stop Believin')",
        "mode": "major",
    },
    "vi-IV-I-V": {
        "emotion": "sensitive pop",
        "feeling": "Vulnerable openness (Sensitive by Adele)",
        "mode": "major (relative minor start)",
    },
    "i-VI-III-VII": {
        "emotion": "aeolian descent",
        "feeling": "Descending sorrow (Hit The Road Jack)",
        "mode": "aeolian (natural minor)",
    },
    "I-IV-I-V": {
        "emotion": "modal avoidance",
        "feeling": "Ambiguous, drifting (avoids V-I resolution)",
        "mode": "mixolydian",
    },
}


def get_parameters_for_state(state: EmotionalState) -> MusicalParameters:
    """
    Map emotional state to musical parameters.

    Args:
        state: EmotionalState with valence, arousal, emotions

    Returns:
        MusicalParameters for composition/performance

    Strategy:
        1. Start with preset for primary emotion
        2. Blend in secondary emotions
        3. Adjust for valence/arousal
        4. Apply modifiers if needed (intrusions, etc.)
    """
    # Get base preset
    if state.primary_emotion in EMOTIONAL_PRESETS:
        params = EMOTIONAL_PRESETS[state.primary_emotion]
    else:
        # Default: blend based on valence/arousal
        if state.arousal > 0.6:  # High energy
            if state.valence < 0:
                params = EMOTIONAL_PRESETS["anger"]
            else:
                params = EMOTIONAL_PRESETS["anxiety"]  # Excited
        else:  # Low energy
            if state.valence < 0:
                params = EMOTIONAL_PRESETS["grief"]
            else:
                params = EMOTIONAL_PRESETS["calm"]

    # Adjust for valence/arousal (fine-tuning)
    # More negative valence → more dissonance
    dissonance_adjust = -0.2 * state.valence  # -1 valence → +0.2 dissonance
    adjusted_dissonance = max(0, min(1, params.dissonance + dissonance_adjust))

    # Higher arousal → faster tempo
    tempo_range = params.tempo_max - params.tempo_min
    tempo_adjust = int(tempo_range * state.arousal)
    adjusted_tempo = params.tempo_min + tempo_adjust

    # Apply intrusion modifiers if present
    if state.has_intrusions:
        # PTSD intrusions increase dissonance and space
        adjusted_dissonance = min(1.0, adjusted_dissonance + 0.2)
        space_adjust = min(1.0, params.space_probability + 0.15)
    else:
        space_adjust = params.space_probability

    # Return adjusted parameters
    return MusicalParameters(
        tempo_min=params.tempo_min,
        tempo_max=params.tempo_max,
        tempo_suggested=adjusted_tempo,
        mode_weights=params.mode_weights.copy(),
        register=params.register,
        harmonic_rhythm=params.harmonic_rhythm,
        dissonance=adjusted_dissonance,
        timing_feel=params.timing_feel,
        density=params.density,
        dynamics=params.dynamics,
        space_probability=space_adjust,
    )


def get_interrogation_prompts(params: MusicalParameters) -> List[str]:
    """
    Generate questions to ask user based on musical parameters.

    "Interrogate Before Generate" — ask about mood, intent, imagery first.

    Args:
        params: MusicalParameters that will guide composition

    Returns:
        List of questions to ask user before generating music

    Examples:
        - "This feels slow and sparse—are we sitting in the quiet, or is there
          restlessness under the surface?"
        - "The harmony wants to pull toward minor—is this grief, or is it
          something unresolved?"
    """
    prompts = []

    # Tempo questions
    if params.tempo_suggested < 80:
        prompts.append(
            "This feels slow and reflective—are we sitting with the feeling, "
            "or is there restlessness beneath the surface?"
        )
    elif params.tempo_suggested > 120:
        prompts.append(
            "This energy feels urgent—is it excitement, anxiety, or anger? "
            "What's driving the momentum?"
        )

    # Mode questions
    dominant_mode = max(params.mode_weights, key=params.mode_weights.get)
    if dominant_mode in ["minor", "dorian", "phrygian"]:
        prompts.append(
            f"The harmony wants to pull toward {dominant_mode}—is this grief, "
            "longing, or something unresolved?"
        )
    elif dominant_mode in ["major", "lydian", "mixolydian"]:
        prompts.append(
            f"This could go to {dominant_mode} (brighter)—does that match the "
            "feeling, or is there darkness underneath?"
        )

    # Dissonance questions
    if params.dissonance > 0.5:
        prompts.append(
            "There's a lot of tension here—are we avoiding resolution "
            "intentionally, or should we let it release?"
        )
    elif params.dissonance < 0.2:
        prompts.append(
            "This feels consonant and stable—is that the true emotion, "
            "or are we smoothing over something rougher?"
        )

    # Space questions
    if params.space_probability > 0.3:
        prompts.append(
            "There's a lot of silence here—what lives in those gaps? "
            "Is it peace, emptiness, or something held back?"
        )

    # Timing feel questions
    if params.timing_feel == TimingFeel.BEHIND:
        prompts.append(
            "The timing wants to drag (behind the beat)—is this reflective, "
            "melancholic, or dissociated?"
        )
    elif params.timing_feel == TimingFeel.AHEAD:
        prompts.append(
            "The timing feels rushed (ahead of the beat)—is this urgency, "
            "anxiety, or anticipation?"
        )

    # Register questions
    if params.register == Register.LOW:
        prompts.append(
            "This sits low in register—is it grounded and heavy, or ominous?"
        )
    elif params.register == Register.HIGH:
        prompts.append(
            "This reaches high in register—is it yearning, fragile, or ecstatic?"
        )

    return prompts


def get_misdirection_technique(
    surface_emotion: str, true_emotion: str
) -> Optional[Dict]:
    """
    Create misdirection technique: Surface emotion → true emotion reveal.

    Example: Kelly's "When I Found You Sleeping"
        Surface: Hopeful (F-C-Am major progression)
        True: Grief (Dm minor tonic resolution)
        Impact: "Things were good... but they're not anymore"

    Args:
        surface_emotion: Initial emotional presentation
        true_emotion: Revealed true emotion

    Returns:
        Dict with progression, description, emotional impact
    """
    # Major → Minor misdirection (Kelly technique)
    if surface_emotion in ["nostalgia", "calm"] and true_emotion == "grief":
        return {
            "name": "Major → Minor Tonic Gut Punch",
            "surface_progression": ["IV", "I", "vi"],  # Major-leaning
            "reveal_chord": "i",  # Minor tonic
            "description": "Hopeful progression resolves to minor tonic",
            "emotional_impact": "Hope → reality check (Kelly technique)",
            "example": "F-C-Am-Dm (in D minor)",
            "timing_suggestion": "Delay reveal until chorus or bridge",
        }

    # Other misdirection possibilities
    misdirection_map = {
        ("calm", "anxiety"): {
            "name": "Calm Before Storm",
            "surface_progression": ["I", "V"],
            "reveal_chord": "viio7/V",  # Diminished 7th
            "description": "Peaceful opening, sudden tension spike",
        },
        ("nostalgia", "anger"): {
            "name": "Sweet to Bitter",
            "surface_progression": ["I", "IV", "vi"],
            "reveal_chord": "VII",  # Subtonic (modal mixture)
            "description": "Sweet memory turns harsh",
        },
    }

    return misdirection_map.get((surface_emotion, true_emotion))


# Preset emotional states for testing
EMOTIONAL_STATE_PRESETS: Dict[str, EmotionalState] = {
    "profound_grief": EmotionalState(
        valence=-0.8,
        arousal=0.3,
        primary_emotion="grief",
        secondary_emotions=["nostalgia", "loss"],
        has_intrusions=False,
        intrusion_probability=0.0,
    ),
    "ptsd_anxiety": EmotionalState(
        valence=-0.6,
        arousal=0.8,
        primary_emotion="anxiety",
        secondary_emotions=["fear", "hypervigilance"],
        has_intrusions=True,
        intrusion_probability=0.2,
    ),
    "bittersweet_nostalgia": EmotionalState(
        valence=0.2,  # Slightly positive
        arousal=0.4,
        primary_emotion="nostalgia",
        secondary_emotions=["grief", "gratitude"],
        has_intrusions=False,
        intrusion_probability=0.0,
    ),
    "suppressed_anger": EmotionalState(
        valence=-0.7,
        arousal=0.6,
        primary_emotion="anger",
        secondary_emotions=["frustration", "helplessness"],
        has_intrusions=False,
        intrusion_probability=0.0,
    ),
}


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("EMOTIONAL → MUSICAL MAPPING")
    print("=" * 60)

    # Test with profound grief
    state = EMOTIONAL_STATE_PRESETS["profound_grief"]
    print(f"\n🧠 Emotional State: {state.primary_emotion}")
    print(f"   Valence: {state.valence}, Arousal: {state.arousal}")

    params = get_parameters_for_state(state)
    print(f"\n🎵 Musical Parameters:")
    print(f"   Tempo: {params.tempo_suggested} BPM "
          f"({params.tempo_min}-{params.tempo_max})")
    print(f"   Mode: {max(params.mode_weights, key=params.mode_weights.get)}")
    print(f"   Dissonance: {params.dissonance:.1%}")
    print(f"   Timing: {params.timing_feel.value}")
    print(f"   Density: {params.density.value}")

    prompts = get_interrogation_prompts(params)
    print(f"\n💬 Interrogation Prompts:")
    for i, prompt in enumerate(prompts, 1):
        print(f"   {i}. {prompt}")

    # Test misdirection technique
    print(f"\n🎭 Misdirection Technique:")
    misdirection = get_misdirection_technique("nostalgia", "grief")
    if misdirection:
        print(f"   {misdirection['name']}")
        print(f"   {misdirection['description']}")
        print(f"   Example: {misdirection['example']}")
