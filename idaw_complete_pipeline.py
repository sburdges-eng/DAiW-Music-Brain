#!/usr/bin/env python3
"""
iDAW Complete Pipeline
======================
intelligent Digital Audio Workstation

Full emotional-to-audio pipeline:
USER PROMPT → Interrogation → EmotionalState → MusicalParameters
→ Structure Generator → Harmony Engine → Melody Engine
→ Groove Engine → MIDI Builder → Audio Tokenizer
→ Audio Generator → Post-Processing → Final Audio

Requirements:
    pip install music21 mido pydub librosa numpy scipy transformers torch

For AKAI MPK Mini integration:
    pip install python-rtmidi

Author: iDAW Project
License: MIT
"""

from __future__ import annotations
import os
import json
import random
import math
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Callable
from pathlib import Path
from datetime import datetime
import numpy as np

# ============================================================================
# 1. CORE DATA STRUCTURES
# ============================================================================

class TimingFeel(Enum):
    """Where notes sit relative to the beat."""
    BEHIND = "behind"      # Laid back, grief, nostalgia
    ON = "on"              # Precise, neutral
    AHEAD = "ahead"        # Pushing, anxious, urgent


class Mode(Enum):
    """Musical modes with emotional associations."""
    MAJOR = "major"           # Happy, resolved
    MINOR = "minor"           # Sad, introspective
    DORIAN = "dorian"         # Minor but hopeful
    PHRYGIAN = "phrygian"     # Dark, exotic, tense
    LYDIAN = "lydian"         # Bright, floating, magical
    MIXOLYDIAN = "mixolydian" # Major but melancholic
    AEOLIAN = "aeolian"       # Natural minor, resigned
    LOCRIAN = "locrian"       # Unstable, eerie


class RuleBreakCode(Enum):
    """Intentional theory violations for emotional effect."""
    HARMONY_ParallelMotion = auto()       # Power, defiance
    HARMONY_ModalInterchange = auto()     # Bittersweet, nostalgia
    HARMONY_UnresolvedDissonance = auto() # Tension, anxiety
    HARMONY_TritoneSubstitution = auto()  # Sophisticated, chromatic
    HARMONY_Polytonality = auto()         # Chaos, duality
    RHYTHM_MeterAmbiguity = auto()        # Floating, dreamlike
    RHYTHM_ConstantDisplacement = auto()  # Anxiety, unease
    RHYTHM_TempoFluctuation = auto()      # Intimacy, vulnerability
    STRUCTURE_NonResolution = auto()      # Grief, longing
    PRODUCTION_BuriedVocals = auto()      # Dissociation, dreams
    PRODUCTION_PitchImperfection = auto() # Vulnerability, rawness


class IntrusionType(Enum):
    """PTSD intrusion types that manifest musically."""
    REGISTER_SPIKE = auto()        # Sudden high note
    HARMONIC_RUSH = auto()         # Unexpected chord change
    UNRESOLVED_DISSONANCE = auto() # Tension that doesn't resolve
    DYNAMIC_SURGE = auto()         # Sudden volume spike
    RHYTHMIC_STUTTER = auto()      # Timing glitch


@dataclass
class EmotionalState:
    """
    Core emotional state from interrogation.
    Everything else derives from this.
    """
    # Primary emotion
    primary_emotion: str = "neutral"
    
    # Emotional complexity
    secondary_emotions: List[str] = field(default_factory=list)
    valence: float = 0.0          # -1.0 (negative) to 1.0 (positive)
    arousal: float = 0.5          # 0.0 (calm) to 1.0 (intense)
    
    # Trauma markers
    has_intrusions: bool = False
    intrusion_probability: float = 0.0
    intrusion_types: List[IntrusionType] = field(default_factory=list)
    
    # Misdirection (surface vs. undertow)
    surface_emotion: Optional[str] = None  # What it sounds like
    undertow_emotion: Optional[str] = None # What it really is
    misdirection_intensity: float = 0.0    # 0.0 to 1.0
    
    # Vulnerability and rawness
    vulnerability: float = 0.5    # 0.0 (guarded) to 1.0 (exposed)
    
    # Core wound (from Phase 0 interrogation)
    core_wound: Optional[str] = None
    core_longing: Optional[str] = None


@dataclass
class MusicalParameters:
    """
    Technical translation of EmotionalState.
    These drive all generation engines.
    """
    # Tempo
    tempo_min: int = 60
    tempo_max: int = 140
    tempo_suggested: int = 100
    tempo_variance: float = 0.0  # For rubato (0.0 = strict, 0.1 = human)
    
    # Mode and harmony
    mode_weights: Dict[Mode, float] = field(default_factory=dict)
    key_signature: str = "C"
    
    # Register (MIDI note numbers)
    register_low: int = 48    # C3
    register_high: int = 84   # C6
    register_center: int = 60 # C4
    
    # Harmonic rhythm (chords per bar)
    harmonic_rhythm_suggested: float = 1.0
    
    # Dissonance and tension
    dissonance: float = 0.3   # 0.0 (consonant) to 1.0 (harsh)
    
    # Groove
    timing_feel: TimingFeel = TimingFeel.ON
    timing_offset_ms: int = 0  # Negative = ahead, positive = behind
    swing: float = 0.5         # 0.5 = straight, 0.67 = triplet swing
    humanize: float = 0.1      # Timing variance
    
    # Density and space
    density_suggested: float = 1.0  # Notes per beat
    space_probability: float = 0.2  # Probability of rest
    
    # Dynamics
    dynamics_floor: int = 40       # Minimum velocity
    dynamics_ceiling: int = 100    # Maximum velocity
    dynamics_variance: float = 0.2 # How much velocity varies
    
    # Rule breaks
    rule_breaks: List[RuleBreakCode] = field(default_factory=list)
    rule_break_intensity: float = 0.5  # How pronounced
    
    # Imperfection aesthetic
    imperfection_level: float = 0.3  # 0.0 = perfect, 1.0 = very rough


# ============================================================================
# 2. EMOTIONAL PRESETS
# ============================================================================

EMOTIONAL_PRESETS: Dict[str, MusicalParameters] = {
    
    "grief": MusicalParameters(
        tempo_min=60,
        tempo_max=82,
        tempo_suggested=72,
        tempo_variance=0.08,  # Rubato - breathing
        mode_weights={
            Mode.MINOR: 0.4,
            Mode.DORIAN: 0.4,
            Mode.MAJOR: 0.2,  # For borrowed chords
        },
        register_low=48,
        register_high=72,
        register_center=58,
        harmonic_rhythm_suggested=1.0,
        dissonance=0.3,
        timing_feel=TimingFeel.BEHIND,
        timing_offset_ms=18,
        swing=0.5,
        humanize=0.25,
        density_suggested=0.5,
        space_probability=0.35,
        dynamics_floor=30,
        dynamics_ceiling=70,
        dynamics_variance=0.3,
        rule_breaks=[RuleBreakCode.STRUCTURE_NonResolution],
        imperfection_level=0.4,
    ),
    
    "anxiety": MusicalParameters(
        tempo_min=100,
        tempo_max=140,
        tempo_suggested=120,
        tempo_variance=0.02,  # Rigid
        mode_weights={
            Mode.MINOR: 0.3,
            Mode.PHRYGIAN: 0.3,
            Mode.LOCRIAN: 0.2,
            Mode.DORIAN: 0.2,
        },
        register_low=60,
        register_high=84,
        register_center=72,
        harmonic_rhythm_suggested=2.0,
        dissonance=0.6,
        timing_feel=TimingFeel.AHEAD,
        timing_offset_ms=-12,
        swing=0.5,
        humanize=0.08,
        density_suggested=2.0,
        space_probability=0.1,
        dynamics_floor=50,
        dynamics_ceiling=95,
        dynamics_variance=0.4,
        rule_breaks=[RuleBreakCode.RHYTHM_ConstantDisplacement],
        imperfection_level=0.15,
    ),
    
    "nostalgia": MusicalParameters(
        tempo_min=70,
        tempo_max=90,
        tempo_suggested=78,
        tempo_variance=0.05,
        mode_weights={
            Mode.MAJOR: 0.4,
            Mode.MIXOLYDIAN: 0.3,
            Mode.DORIAN: 0.2,
            Mode.MINOR: 0.1,
        },
        register_low=48,
        register_high=76,
        register_center=62,
        harmonic_rhythm_suggested=1.5,
        dissonance=0.25,
        timing_feel=TimingFeel.BEHIND,
        timing_offset_ms=15,
        swing=0.55,
        humanize=0.2,
        density_suggested=1.0,
        space_probability=0.2,
        dynamics_floor=35,
        dynamics_ceiling=75,
        dynamics_variance=0.25,
        rule_breaks=[RuleBreakCode.HARMONY_ModalInterchange],
        imperfection_level=0.35,
    ),
    
    "anger": MusicalParameters(
        tempo_min=120,
        tempo_max=160,
        tempo_suggested=138,
        tempo_variance=0.01,
        mode_weights={
            Mode.PHRYGIAN: 0.4,
            Mode.MINOR: 0.3,
            Mode.LOCRIAN: 0.2,
            Mode.DORIAN: 0.1,
        },
        register_low=36,
        register_high=72,
        register_center=54,
        harmonic_rhythm_suggested=0.5,
        dissonance=0.5,
        timing_feel=TimingFeel.AHEAD,
        timing_offset_ms=-15,
        swing=0.5,
        humanize=0.05,
        density_suggested=2.5,
        space_probability=0.05,
        dynamics_floor=70,
        dynamics_ceiling=127,
        dynamics_variance=0.15,
        rule_breaks=[RuleBreakCode.HARMONY_ParallelMotion],
        imperfection_level=0.1,
    ),
    
    "calm": MusicalParameters(
        tempo_min=60,
        tempo_max=80,
        tempo_suggested=68,
        tempo_variance=0.06,
        mode_weights={
            Mode.MAJOR: 0.5,
            Mode.LYDIAN: 0.3,
            Mode.MIXOLYDIAN: 0.2,
        },
        register_low=48,
        register_high=72,
        register_center=60,
        harmonic_rhythm_suggested=0.5,
        dissonance=0.1,
        timing_feel=TimingFeel.BEHIND,
        timing_offset_ms=10,
        swing=0.5,
        humanize=0.15,
        density_suggested=0.7,
        space_probability=0.3,
        dynamics_floor=25,
        dynamics_ceiling=60,
        dynamics_variance=0.15,
        rule_breaks=[],
        imperfection_level=0.2,
    ),
    
    "hope": MusicalParameters(
        tempo_min=80,
        tempo_max=110,
        tempo_suggested=92,
        tempo_variance=0.04,
        mode_weights={
            Mode.MAJOR: 0.4,
            Mode.LYDIAN: 0.3,
            Mode.DORIAN: 0.3,  # Minor but hopeful
        },
        register_low=55,
        register_high=80,
        register_center=67,
        harmonic_rhythm_suggested=1.0,
        dissonance=0.2,
        timing_feel=TimingFeel.ON,
        timing_offset_ms=0,
        swing=0.5,
        humanize=0.12,
        density_suggested=1.2,
        space_probability=0.15,
        dynamics_floor=45,
        dynamics_ceiling=85,
        dynamics_variance=0.2,
        rule_breaks=[],
        imperfection_level=0.15,
    ),
    
    "intimacy": MusicalParameters(
        tempo_min=55,
        tempo_max=75,
        tempo_suggested=64,
        tempo_variance=0.1,  # Lots of rubato
        mode_weights={
            Mode.MAJOR: 0.3,
            Mode.MINOR: 0.3,
            Mode.DORIAN: 0.4,
        },
        register_low=48,
        register_high=68,
        register_center=58,
        harmonic_rhythm_suggested=0.75,
        dissonance=0.2,
        timing_feel=TimingFeel.BEHIND,
        timing_offset_ms=20,
        swing=0.52,
        humanize=0.3,
        density_suggested=0.6,
        space_probability=0.4,
        dynamics_floor=20,
        dynamics_ceiling=55,
        dynamics_variance=0.35,
        rule_breaks=[RuleBreakCode.RHYTHM_TempoFluctuation, RuleBreakCode.PRODUCTION_PitchImperfection],
        imperfection_level=0.5,
    ),
    
    "defiance": MusicalParameters(
        tempo_min=100,
        tempo_max=130,
        tempo_suggested=115,
        tempo_variance=0.02,
        mode_weights={
            Mode.MINOR: 0.4,
            Mode.PHRYGIAN: 0.3,
            Mode.DORIAN: 0.3,
        },
        register_low=40,
        register_high=75,
        register_center=58,
        harmonic_rhythm_suggested=1.0,
        dissonance=0.4,
        timing_feel=TimingFeel.ON,
        timing_offset_ms=0,
        swing=0.5,
        humanize=0.08,
        density_suggested=1.8,
        space_probability=0.1,
        dynamics_floor=60,
        dynamics_ceiling=115,
        dynamics_variance=0.2,
        rule_breaks=[RuleBreakCode.HARMONY_ParallelMotion],
        imperfection_level=0.2,
    ),
}


# Emotion modifiers (applied on top of presets)
EMOTION_MODIFIERS: Dict[str, Dict[str, Any]] = {
    "ptsd_intrusion": {
        "intrusion_probability": 0.15,
        "intrusion_types": [
            IntrusionType.REGISTER_SPIKE,
            IntrusionType.HARMONIC_RUSH,
            IntrusionType.UNRESOLVED_DISSONANCE,
        ],
    },
    "misdirection": {
        "surface_differs_from_undertow": True,
        "reveal_point": 0.8,  # 80% through song
    },
    "dissociation": {
        "production_buried": True,
        "timing_drift": 0.15,
    },
    "suppressed": {
        "dynamics_ceiling_reduction": 20,
        "space_probability_increase": 0.15,
    },
}


# Interval emotional weights (semitones -> tension 0-1)
INTERVAL_EMOTIONS: Dict[int, Dict[str, float]] = {
    0:  {"tension": 0.0, "color": "unison"},        # Unison
    1:  {"tension": 0.9, "color": "harsh"},         # Minor 2nd
    2:  {"tension": 0.4, "color": "bright"},        # Major 2nd
    3:  {"tension": 0.3, "color": "sad"},           # Minor 3rd
    4:  {"tension": 0.2, "color": "happy"},         # Major 3rd
    5:  {"tension": 0.15, "color": "stable"},       # Perfect 4th
    6:  {"tension": 1.0, "color": "devil"},         # Tritone
    7:  {"tension": 0.1, "color": "powerful"},      # Perfect 5th
    8:  {"tension": 0.35, "color": "mysterious"},   # Minor 6th
    9:  {"tension": 0.25, "color": "warm"},         # Major 6th
    10: {"tension": 0.55, "color": "bluesy"},       # Minor 7th
    11: {"tension": 0.5, "color": "yearning"},      # Major 7th
    12: {"tension": 0.05, "color": "open"},         # Octave
}


# ============================================================================
# 3. INTERROGATION ENGINE
# ============================================================================

class InterrogationEngine:
    """
    Phase 0 + Phase 1 interrogation.
    Extracts emotional intent from user input.
    """
    
    # Phase 0: Core Wound questions
    PHASE_0_QUESTIONS = [
        ("core_event", "What happened? (The event, not the feeling)"),
        ("core_resistance", "What's the hardest part to say out loud?"),
        ("core_longing", "What do you wish you could feel instead?"),
        ("core_stakes", "What's at risk if you don't say this?"),
        ("core_transformation", "How should you feel when this song is done?"),
    ]
    
    # Phase 1: Emotional Intent questions
    PHASE_1_QUESTIONS = [
        ("mood_primary", "One word: the dominant emotion"),
        ("mood_secondary", "What's the undertow? The thing underneath?"),
        ("imagery", "Close your eyes. What do you see/feel/smell?"),
        ("vulnerability", "Scale 1-10: how exposed should this feel?"),
        ("misdirection", "Should it sound like one thing but be another?"),
    ]
    
    def __init__(self):
        self.responses: Dict[str, Any] = {}
        self.emotional_state: Optional[EmotionalState] = None
        
    def parse_vernacular(self, user_input: str) -> Dict[str, Any]:
        """
        Parse casual/vernacular input into structured data.
        """
        parsed = {
            "raw_input": user_input,
            "detected_emotions": [],
            "detected_tempo": None,
            "detected_feel": None,
            "detected_style": None,
        }
        
        # Emotion keywords
        emotion_keywords = {
            "grief": ["grief", "loss", "mourning", "death", "gone", "miss"],
            "anxiety": ["anxiety", "anxious", "nervous", "worried", "panic", "stressed"],
            "nostalgia": ["nostalgia", "nostalgic", "remember", "memory", "past", "used to"],
            "anger": ["anger", "angry", "rage", "furious", "pissed", "mad"],
            "calm": ["calm", "peaceful", "serene", "relaxed", "chill"],
            "hope": ["hope", "hopeful", "bright", "future", "optimistic"],
            "intimacy": ["intimate", "close", "tender", "soft", "vulnerable"],
            "defiance": ["defiance", "defiant", "rebel", "fight", "against"],
        }
        
        lower_input = user_input.lower()
        for emotion, keywords in emotion_keywords.items():
            if any(kw in lower_input for kw in keywords):
                parsed["detected_emotions"].append(emotion)
        
        # Tempo/feel keywords
        if any(w in lower_input for w in ["slow", "crawl", "dragging"]):
            parsed["detected_tempo"] = "slow"
        elif any(w in lower_input for w in ["fast", "driving", "urgent"]):
            parsed["detected_tempo"] = "fast"
            
        if any(w in lower_input for w in ["laid back", "behind", "lazy"]):
            parsed["detected_feel"] = "behind"
        elif any(w in lower_input for w in ["pushing", "ahead", "rushing"]):
            parsed["detected_feel"] = "ahead"
            
        # Style keywords
        if any(w in lower_input for w in ["lo-fi", "lofi", "bedroom", "raw"]):
            parsed["detected_style"] = "lo-fi"
        elif any(w in lower_input for w in ["clean", "polished", "produced"]):
            parsed["detected_style"] = "polished"
            
        return parsed
    
    def quick_interrogate(self, user_input: str) -> EmotionalState:
        """
        Fast path: parse vernacular directly to EmotionalState.
        For when user gives rich description upfront.
        """
        parsed = self.parse_vernacular(user_input)
        
        primary = parsed["detected_emotions"][0] if parsed["detected_emotions"] else "neutral"
        secondary = parsed["detected_emotions"][1:] if len(parsed["detected_emotions"]) > 1 else []
        
        # Detect trauma markers
        has_intrusions = any(w in user_input.lower() for w in [
            "ptsd", "trauma", "flashback", "intrusive", "can't stop thinking"
        ])
        
        # Detect misdirection intent
        misdirection = any(w in user_input.lower() for w in [
            "sounds like", "but really", "underneath", "secretly", "misdirect"
        ])
        
        state = EmotionalState(
            primary_emotion=primary,
            secondary_emotions=secondary,
            valence=self._emotion_to_valence(primary),
            arousal=self._emotion_to_arousal(primary),
            has_intrusions=has_intrusions,
            intrusion_probability=0.15 if has_intrusions else 0.0,
            misdirection_intensity=0.7 if misdirection else 0.0,
            vulnerability=0.8 if "vulnerable" in user_input.lower() else 0.5,
        )
        
        self.emotional_state = state
        return state
    
    def _emotion_to_valence(self, emotion: str) -> float:
        """Map emotion to valence (-1 to 1)."""
        valence_map = {
            "grief": -0.7,
            "anxiety": -0.5,
            "anger": -0.6,
            "nostalgia": -0.2,
            "calm": 0.4,
            "hope": 0.6,
            "intimacy": 0.3,
            "defiance": -0.3,
            "neutral": 0.0,
        }
        return valence_map.get(emotion, 0.0)
    
    def _emotion_to_arousal(self, emotion: str) -> float:
        """Map emotion to arousal (0 to 1)."""
        arousal_map = {
            "grief": 0.3,
            "anxiety": 0.8,
            "anger": 0.9,
            "nostalgia": 0.3,
            "calm": 0.2,
            "hope": 0.5,
            "intimacy": 0.3,
            "defiance": 0.7,
            "neutral": 0.5,
        }
        return arousal_map.get(emotion, 0.5)


# ============================================================================
# 4. EMOTIONAL STATE → MUSICAL PARAMETERS
# ============================================================================

def get_parameters_for_state(state: EmotionalState) -> MusicalParameters:
    """
    Convert EmotionalState to MusicalParameters.
    This is the core translation layer.
    """
    # Start from preset
    if state.primary_emotion in EMOTIONAL_PRESETS:
        params = EMOTIONAL_PRESETS[state.primary_emotion]
        # Create a copy to modify
        import copy
        params = copy.deepcopy(params)
    else:
        params = MusicalParameters()
    
    # Apply PTSD intrusion modifier
    if state.has_intrusions:
        modifier = EMOTION_MODIFIERS.get("ptsd_intrusion", {})
        # Add intrusion types to parameters
        # (Would need to extend MusicalParameters)
        params.dissonance = min(1.0, params.dissonance + 0.15)
        params.dynamics_variance = min(0.5, params.dynamics_variance + 0.1)
    
    # Apply misdirection
    if state.misdirection_intensity > 0:
        # Surface emotion affects early parameters
        # Undertow emotion affects late parameters
        # (Complex - would need structure-aware parameter morphing)
        pass
    
    # Adjust for vulnerability
    if state.vulnerability > 0.7:
        params.imperfection_level = min(0.6, params.imperfection_level + 0.15)
        params.dynamics_ceiling = max(60, params.dynamics_ceiling - 15)
    
    # Blend secondary emotions
    for secondary in state.secondary_emotions:
        if secondary in EMOTIONAL_PRESETS:
            sec_params = EMOTIONAL_PRESETS[secondary]
            # Blend at 30% weight
            params.dissonance = params.dissonance * 0.7 + sec_params.dissonance * 0.3
            params.density_suggested = params.density_suggested * 0.7 + sec_params.density_suggested * 0.3
    
    return params


# ============================================================================
# 5. STRUCTURE GENERATOR
# ============================================================================

@dataclass
class SongSection:
    """A section of the song."""
    name: str              # intro, verse, chorus, bridge, outro
    bars: int              # Length in bars
    energy: float          # 0.0 to 1.0
    density: float         # Relative to base
    reveal_level: float    # For misdirection (0.0 = surface, 1.0 = undertow)


class StructureGenerator:
    """
    Generates song structure based on emotional arc.
    """
    
    STANDARD_STRUCTURES = {
        "verse_chorus": [
            SongSection("intro", 4, 0.3, 0.5, 0.0),
            SongSection("verse", 8, 0.5, 1.0, 0.2),
            SongSection("chorus", 8, 0.8, 1.2, 0.4),
            SongSection("verse", 8, 0.5, 1.0, 0.3),
            SongSection("chorus", 8, 0.8, 1.2, 0.5),
            SongSection("bridge", 4, 0.6, 0.8, 0.7),
            SongSection("chorus", 8, 0.9, 1.3, 0.9),
            SongSection("outro", 4, 0.4, 0.6, 1.0),
        ],
        "slow_reveal": [
            SongSection("intro", 8, 0.2, 0.4, 0.0),
            SongSection("verse", 16, 0.4, 0.8, 0.3),
            SongSection("build", 8, 0.6, 1.0, 0.5),
            SongSection("climax", 8, 1.0, 1.5, 1.0),
            SongSection("outro", 8, 0.3, 0.5, 1.0),
        ],
        "intimate": [
            SongSection("intro", 4, 0.2, 0.4, 0.0),
            SongSection("verse", 8, 0.4, 0.7, 0.3),
            SongSection("verse", 8, 0.5, 0.8, 0.5),
            SongSection("bridge", 4, 0.6, 0.9, 0.7),
            SongSection("verse", 8, 0.5, 0.8, 0.9),
            SongSection("outro", 4, 0.3, 0.5, 1.0),
        ],
    }
    
    def generate(self, params: MusicalParameters, 
                 state: EmotionalState) -> List[SongSection]:
        """Generate song structure."""
        
        # Choose base structure
        if state.vulnerability > 0.7:
            structure_type = "intimate"
        elif state.misdirection_intensity > 0.5:
            structure_type = "slow_reveal"
        else:
            structure_type = "verse_chorus"
            
        sections = self.STANDARD_STRUCTURES[structure_type].copy()
        
        # Adjust for emotional parameters
        for section in sections:
            # Scale energy by arousal
            section.energy *= (0.5 + state.arousal * 0.5)
            
            # Adjust density
            section.density *= params.density_suggested
            
        return sections


# ============================================================================
# 6. HARMONY ENGINE
# ============================================================================

class HarmonyEngine:
    """
    Generates chord progressions based on emotional parameters.
    """
    
    # Scale degrees for each mode (semitones from root)
    MODE_SCALES = {
        Mode.MAJOR: [0, 2, 4, 5, 7, 9, 11],
        Mode.MINOR: [0, 2, 3, 5, 7, 8, 10],
        Mode.DORIAN: [0, 2, 3, 5, 7, 9, 10],
        Mode.PHRYGIAN: [0, 1, 3, 5, 7, 8, 10],
        Mode.LYDIAN: [0, 2, 4, 6, 7, 9, 11],
        Mode.MIXOLYDIAN: [0, 2, 4, 5, 7, 9, 10],
        Mode.AEOLIAN: [0, 2, 3, 5, 7, 8, 10],
        Mode.LOCRIAN: [0, 1, 3, 5, 6, 8, 10],
    }
    
    # Common progressions by emotion
    EMOTIONAL_PROGRESSIONS = {
        "grief": [
            [1, 5, 6, 4],       # I-V-vi-IV
            [1, 4, 6, 5],       # I-IV-vi-V
            [6, 4, 1, 5],       # vi-IV-I-V (start minor)
        ],
        "anxiety": [
            [1, "b7", 4, 1],    # i-bVII-iv-i
            [1, "b2", 1, "b7"], # i-bII-i-bVII (phrygian)
        ],
        "nostalgia": [
            [1, 5, 6, 4],       # I-V-vi-IV
            [1, 4, "b7", 1],    # I-IV-bVII-I (mixolydian)
        ],
        "hope": [
            [1, 5, 4, 5],       # I-V-IV-V
            [4, 1, 5, 1],       # IV-I-V-I
        ],
    }
    
    def __init__(self, params: MusicalParameters):
        self.params = params
        self.key_root = self._parse_key(params.key_signature)
        self.mode = self._select_mode()
        self.scale = self.MODE_SCALES[self.mode]
        
    def _parse_key(self, key_sig: str) -> int:
        """Parse key signature to MIDI root note."""
        key_map = {
            "C": 60, "C#": 61, "Db": 61, "D": 62, "D#": 63, "Eb": 63,
            "E": 64, "F": 65, "F#": 66, "Gb": 66, "G": 67, "G#": 68,
            "Ab": 68, "A": 69, "A#": 70, "Bb": 70, "B": 71
        }
        return key_map.get(key_sig, 60)
    
    def _select_mode(self) -> Mode:
        """Select mode based on weights."""
        if not self.params.mode_weights:
            return Mode.MAJOR
        modes = list(self.params.mode_weights.keys())
        weights = list(self.params.mode_weights.values())
        return random.choices(modes, weights=weights)[0]
    
    def generate_progression(self, bars: int, emotion: str = "neutral") -> List[List[int]]:
        """
        Generate chord progression.
        Returns list of chords, each chord is list of MIDI notes.
        """
        # Get base progression
        progressions = self.EMOTIONAL_PROGRESSIONS.get(
            emotion, self.EMOTIONAL_PROGRESSIONS["hope"]
        )
        base_prog = random.choice(progressions)
        
        # Extend/repeat to fill bars
        chords_needed = int(bars * self.params.harmonic_rhythm_suggested)
        progression = []
        
        for i in range(chords_needed):
            degree = base_prog[i % len(base_prog)]
            chord = self._build_chord(degree)
            progression.append(chord)
            
        # Apply rule breaks
        if RuleBreakCode.HARMONY_ModalInterchange in self.params.rule_breaks:
            progression = self._apply_modal_interchange(progression)
            
        if RuleBreakCode.STRUCTURE_NonResolution in self.params.rule_breaks:
            progression = self._apply_non_resolution(progression)
            
        return progression
    
    def _build_chord(self, degree: Any) -> List[int]:
        """Build a chord from scale degree."""
        if isinstance(degree, str):
            # Handle borrowed chords like "b7"
            if degree.startswith("b"):
                semitones = int(degree[1:]) - 1
                root = self.key_root + semitones - 1  # Flatten
            else:
                root = self.key_root
        else:
            # Standard diatonic degree
            idx = (degree - 1) % 7
            root = self.key_root + self.scale[idx]
        
        # Build triad
        third = root + (3 if self._is_minor_chord(degree) else 4)
        fifth = root + 7
        
        return [root, third, fifth]
    
    def _is_minor_chord(self, degree: Any) -> bool:
        """Determine if chord should be minor."""
        if self.mode in [Mode.MAJOR, Mode.LYDIAN, Mode.MIXOLYDIAN]:
            return degree in [2, 3, 6]
        else:
            return degree in [1, 4, 5]
    
    def _apply_modal_interchange(self, progression: List[List[int]]) -> List[List[int]]:
        """Apply modal interchange (borrowed chords)."""
        # Randomly borrow from parallel minor/major
        for i, chord in enumerate(progression):
            if random.random() < 0.2:  # 20% chance
                root = chord[0]
                # Borrow iv chord (flatten the third)
                if chord[1] - root == 4:  # Major third
                    progression[i] = [root, root + 3, root + 7]
        return progression
    
    def _apply_non_resolution(self, progression: List[List[int]]) -> List[List[int]]:
        """End on non-tonic chord."""
        # Replace final chord with IV or vi
        if progression:
            root = self.key_root
            # End on IV
            progression[-1] = [root + 5, root + 9, root + 12]
        return progression


# ============================================================================
# 7. MELODY ENGINE
# ============================================================================

class MelodyEngine:
    """
    Generates melodies based on emotional parameters and harmony.
    """
    
    def __init__(self, params: MusicalParameters, harmony: HarmonyEngine):
        self.params = params
        self.harmony = harmony
        
    def generate(self, progression: List[List[int]], bars: int) -> List[Dict]:
        """
        Generate melody notes.
        Returns list of {pitch, start, duration, velocity}
        """
        melody = []
        ticks_per_bar = 1920  # 4 beats * 480 ticks
        current_tick = 0
        
        notes_per_bar = int(4 * self.params.density_suggested)
        
        for bar in range(bars):
            chord_idx = bar % len(progression)
            chord = progression[chord_idx]
            
            for note_idx in range(notes_per_bar):
                # Decide if we play a note or rest
                if random.random() < self.params.space_probability:
                    continue
                    
                # Choose pitch
                pitch = self._choose_pitch(chord)
                
                # Duration
                base_duration = ticks_per_bar // notes_per_bar
                duration = int(base_duration * random.uniform(0.7, 1.0))
                
                # Velocity
                velocity = self._calculate_velocity(note_idx, notes_per_bar)
                
                # Position
                start = current_tick + (note_idx * base_duration)
                
                # Apply humanization
                start = self._humanize_timing(start)
                velocity = self._humanize_velocity(velocity)
                
                melody.append({
                    "pitch": pitch,
                    "start": start,
                    "duration": duration,
                    "velocity": velocity,
                })
                
            current_tick += ticks_per_bar
            
        return melody
    
    def _choose_pitch(self, chord: List[int]) -> int:
        """Choose a pitch, preferring chord tones."""
        # 70% chord tone, 30% scale tone
        if random.random() < 0.7:
            pitch = random.choice(chord)
        else:
            scale_pitches = [
                self.harmony.key_root + s 
                for s in self.harmony.scale
            ]
            pitch = random.choice(scale_pitches)
            
        # Apply register constraints
        while pitch < self.params.register_low:
            pitch += 12
        while pitch > self.params.register_high:
            pitch -= 12
            
        return pitch
    
    def _calculate_velocity(self, note_idx: int, total_notes: int) -> int:
        """Calculate velocity with dynamic shape."""
        base = (self.params.dynamics_floor + self.params.dynamics_ceiling) // 2
        
        # Create gentle arc
        position = note_idx / max(1, total_notes - 1)
        arc = math.sin(position * math.pi) * 20
        
        return int(base + arc)
    
    def _humanize_timing(self, tick: int) -> int:
        """Add human timing variation."""
        variance = int(self.params.humanize * 50)
        offset = random.gauss(0, variance)
        
        # Apply pocket feel
        if self.params.timing_feel == TimingFeel.BEHIND:
            offset += self.params.timing_offset_ms * 2  # Convert ms to ticks approx
        elif self.params.timing_feel == TimingFeel.AHEAD:
            offset -= abs(self.params.timing_offset_ms) * 2
            
        return max(0, int(tick + offset))
    
    def _humanize_velocity(self, velocity: int) -> int:
        """Add human velocity variation."""
        variance = int(self.params.dynamics_variance * 20)
        offset = int(random.gauss(0, variance))
        return max(1, min(127, velocity + offset))


# ============================================================================
# 8. GROOVE ENGINE
# ============================================================================

class GrooveEngine:
    """
    Generates rhythmic patterns (drums, bass rhythm).
    Handles pocket, swing, and feel.
    """
    
    DRUM_PATTERNS = {
        "basic": {
            "kick":  [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            "snare": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            "hat":   [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        },
        "boom_bap": {
            "kick":  [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            "snare": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            "hat":   [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        },
        "sparse": {
            "kick":  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "snare": [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            "hat":   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "four_on_floor": {
            "kick":  [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            "snare": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            "hat":   [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
        },
    }
    
    # GM Drum Map
    DRUM_NOTES = {
        "kick": 36,
        "snare": 38,
        "hat": 42,
        "hat_open": 46,
        "tom_low": 45,
        "tom_mid": 47,
        "tom_high": 50,
        "crash": 49,
        "ride": 51,
    }
    
    def __init__(self, params: MusicalParameters):
        self.params = params
        
    def generate_drums(self, bars: int, style: str = "basic") -> List[Dict]:
        """Generate drum pattern."""
        pattern = self.DRUM_PATTERNS.get(style, self.DRUM_PATTERNS["basic"])
        events = []
        
        ticks_per_16th = 120  # 480 / 4
        
        for bar in range(bars):
            bar_start = bar * 16 * ticks_per_16th
            
            for drum, hits in pattern.items():
                note = self.DRUM_NOTES.get(drum, 36)
                
                for i, hit in enumerate(hits):
                    if hit:
                        tick = bar_start + i * ticks_per_16th
                        
                        # Apply swing to offbeats
                        if i % 2 == 1 and self.params.swing > 0.5:
                            swing_offset = int((self.params.swing - 0.5) * ticks_per_16th * 2)
                            tick += swing_offset
                        
                        # Humanize
                        tick = self._humanize_tick(tick)
                        velocity = self._calculate_drum_velocity(drum, i)
                        
                        events.append({
                            "pitch": note,
                            "start": tick,
                            "duration": ticks_per_16th // 2,
                            "velocity": velocity,
                            "channel": 9,  # GM drum channel
                        })
                        
        return events
    
    def _humanize_tick(self, tick: int) -> int:
        """Add timing variation."""
        variance = int(self.params.humanize * 30)
        offset = int(random.gauss(0, variance))
        
        # Apply pocket
        if self.params.timing_feel == TimingFeel.BEHIND:
            offset += int(self.params.timing_offset_ms * 0.48)  # ms to ticks
        elif self.params.timing_feel == TimingFeel.AHEAD:
            offset -= int(abs(self.params.timing_offset_ms) * 0.48)
            
        return max(0, tick + offset)
    
    def _calculate_drum_velocity(self, drum: str, position: int) -> int:
        """Calculate velocity for drums."""
        base = 80
        
        # Accent downbeats
        if position % 4 == 0:
            base += 15
        elif position % 2 == 0:
            base += 5
            
        # Apply dynamics variance
        variance = int(self.params.dynamics_variance * 15)
        offset = int(random.gauss(0, variance))
        
        return max(40, min(127, base + offset))


# ============================================================================
# 9. MIDI BUILDER
# ============================================================================

class MIDIBuilder:
    """
    Assembles all parts into MIDI file.
    Supports AKAI MPK Mini for live input.
    """
    
    def __init__(self, bpm: int = 120, ppq: int = 480):
        self.bpm = bpm
        self.ppq = ppq
        self.tracks: Dict[str, List[Dict]] = {}
        
    def add_track(self, name: str, events: List[Dict]):
        """Add a track of events."""
        self.tracks[name] = events
        
    def build(self) -> 'MidiFile':
        """Build MIDI file from all tracks."""
        from mido import MidiFile, MidiTrack, Message, MetaMessage
        
        mid = MidiFile(ticks_per_beat=self.ppq)
        
        # Tempo track
        tempo_track = MidiTrack()
        tempo_track.name = "Tempo"
        microseconds = int(60_000_000 / self.bpm)
        tempo_track.append(MetaMessage('set_tempo', tempo=microseconds, time=0))
        mid.tracks.append(tempo_track)
        
        # Add each track
        for name, events in self.tracks.items():
            track = MidiTrack()
            track.name = name
            
            # Sort events by start time
            events = sorted(events, key=lambda x: x["start"])
            
            current_time = 0
            for event in events:
                delta = event["start"] - current_time
                channel = event.get("channel", 0)
                
                track.append(Message(
                    'note_on',
                    note=event["pitch"],
                    velocity=event["velocity"],
                    time=max(0, delta),
                    channel=channel
                ))
                track.append(Message(
                    'note_off',
                    note=event["pitch"],
                    velocity=0,
                    time=event["duration"],
                    channel=channel
                ))
                
                current_time = event["start"] + event["duration"]
                
            mid.tracks.append(track)
            
        return mid
    
    def save(self, path: Path):
        """Save MIDI file."""
        mid = self.build()
        mid.save(str(path))
        return path


# ============================================================================
# 10. AKAI MPK MINI INTEGRATION
# ============================================================================

class MPKMiniController:
    """
    Integration with AKAI MPK Mini.
    Captures live input and maps controls to parameters.
    """
    
    # MPK Mini CC mappings (default)
    CC_MAPPINGS = {
        1: "mod_wheel",
        70: "knob_1",
        71: "knob_2",
        72: "knob_3",
        73: "knob_4",
        74: "knob_5",
        75: "knob_6",
        76: "knob_7",
        77: "knob_8",
    }
    
    # Map knobs to iDAW parameters
    PARAM_MAPPINGS = {
        "knob_1": "tempo",          # 60-180 BPM
        "knob_2": "humanize",       # 0.0-0.5
        "knob_3": "dissonance",     # 0.0-1.0
        "knob_4": "density",        # 0.3-2.0
        "knob_5": "dynamics_range", # 0.1-0.5
        "knob_6": "swing",          # 0.5-0.7
        "knob_7": "space",          # 0.0-0.5
        "knob_8": "imperfection",   # 0.0-0.6
    }
    
    def __init__(self):
        self.midi_in = None
        self.current_values: Dict[str, float] = {}
        self.recording: List[Dict] = []
        self.is_recording = False
        
    def connect(self, port_name: str = "MPK mini 3") -> bool:
        """Connect to MPK Mini."""
        try:
            import rtmidi
            self.midi_in = rtmidi.MidiIn()
            
            ports = self.midi_in.get_ports()
            for i, port in enumerate(ports):
                if port_name.lower() in port.lower():
                    self.midi_in.open_port(i)
                    self.midi_in.set_callback(self._midi_callback)
                    print(f"Connected to: {port}")
                    return True
                    
            print(f"MPK Mini not found. Available ports: {ports}")
            return False
            
        except ImportError:
            print("python-rtmidi not installed. Run: pip install python-rtmidi")
            return False
    
    def _midi_callback(self, message, data):
        """Handle incoming MIDI messages."""
        msg, delta = message
        
        if len(msg) == 3:
            status, data1, data2 = msg
            
            # Note on (0x90)
            if status & 0xF0 == 0x90 and data2 > 0:
                if self.is_recording:
                    self.recording.append({
                        "type": "note_on",
                        "pitch": data1,
                        "velocity": data2,
                        "time": delta,
                    })
                    
            # Control Change (0xB0)
            elif status & 0xF0 == 0xB0:
                cc_name = self.CC_MAPPINGS.get(data1)
                if cc_name:
                    param = self.PARAM_MAPPINGS.get(cc_name)
                    if param:
                        # Normalize 0-127 to parameter range
                        normalized = data2 / 127.0
                        self.current_values[param] = normalized
                        print(f"{param}: {normalized:.2f}")
    
    def start_recording(self):
        """Start recording MIDI input."""
        self.recording = []
        self.is_recording = True
        print("Recording started...")
        
    def stop_recording(self) -> List[Dict]:
        """Stop recording and return events."""
        self.is_recording = False
        print(f"Recording stopped. {len(self.recording)} events captured.")
        return self.recording
    
    def get_current_params(self) -> Dict[str, float]:
        """Get current knob values as parameters."""
        return self.current_values.copy()


# ============================================================================
# 11. AUDIO TOKENIZER
# ============================================================================

class AudioTokenizer:
    """
    Converts between audio and tokens for transformer processing.
    Uses EnCodec-style approach.
    """
    
    def __init__(self, sample_rate: int = 24000, 
                 codebook_size: int = 1024,
                 n_codebooks: int = 4):
        self.sample_rate = sample_rate
        self.codebook_size = codebook_size
        self.n_codebooks = n_codebooks
        self.encoder = None
        self.decoder = None
        
    def load_model(self):
        """Load EnCodec model."""
        try:
            from encodec import EncodecModel
            self.model = EncodecModel.encodec_model_24khz()
            self.model.set_target_bandwidth(6.0)  # kbps
            print("EnCodec model loaded")
        except ImportError:
            print("EnCodec not available. Install: pip install encodec")
            self.model = None
            
    def encode(self, audio: np.ndarray) -> np.ndarray:
        """
        Encode audio to tokens.
        Returns: [n_codebooks, seq_len] token indices
        """
        if self.model is None:
            # Fallback: simple quantization
            return self._simple_encode(audio)
            
        import torch
        
        # Reshape for model
        audio_tensor = torch.from_numpy(audio).float().unsqueeze(0).unsqueeze(0)
        
        with torch.no_grad():
            encoded = self.model.encode(audio_tensor)
            codes = encoded[0][0]  # [n_codebooks, seq_len]
            
        return codes.numpy()
    
    def decode(self, tokens: np.ndarray) -> np.ndarray:
        """
        Decode tokens back to audio.
        Input: [n_codebooks, seq_len] token indices
        """
        if self.model is None:
            return self._simple_decode(tokens)
            
        import torch
        
        codes = torch.from_numpy(tokens).unsqueeze(0)
        
        with torch.no_grad():
            audio = self.model.decode([(codes, None)])
            
        return audio[0, 0].numpy()
    
    def _simple_encode(self, audio: np.ndarray) -> np.ndarray:
        """Fallback: mu-law encoding."""
        # Normalize
        audio = audio / (np.abs(audio).max() + 1e-8)
        
        # Mu-law compression
        mu = self.codebook_size - 1
        compressed = np.sign(audio) * np.log1p(mu * np.abs(audio)) / np.log1p(mu)
        
        # Quantize to codebook indices
        tokens = ((compressed + 1) / 2 * (self.codebook_size - 1)).astype(np.int32)
        
        return tokens.reshape(1, -1)  # [1, seq_len]
    
    def _simple_decode(self, tokens: np.ndarray) -> np.ndarray:
        """Fallback: mu-law decoding."""
        # Dequantize
        mu = self.codebook_size - 1
        compressed = tokens.flatten() / (self.codebook_size - 1) * 2 - 1
        
        # Mu-law expansion
        audio = np.sign(compressed) * (np.exp(np.abs(compressed) * np.log1p(mu)) - 1) / mu
        
        return audio


# ============================================================================
# 12. AUDIO GENERATOR (Transformer)
# ============================================================================

class AudioGenerator:
    """
    Transformer-based audio generation from MIDI + emotional context.
    Can use local models or API.
    """
    
    def __init__(self, model_name: str = "facebook/musicgen-small"):
        self.model_name = model_name
        self.model = None
        self.processor = None
        
    def load_model(self):
        """Load MusicGen model."""
        try:
            from transformers import AutoProcessor, MusicgenForConditionalGeneration
            
            print(f"Loading {self.model_name}...")
            self.processor = AutoProcessor.from_pretrained(self.model_name)
            self.model = MusicgenForConditionalGeneration.from_pretrained(self.model_name)
            print("Model loaded")
            
        except ImportError:
            print("Transformers not available. Install: pip install transformers torch")
            
    def generate_from_prompt(self, 
                            prompt: str,
                            duration_seconds: float = 10.0,
                            guidance_scale: float = 3.0) -> np.ndarray:
        """
        Generate audio from text prompt.
        """
        if self.model is None:
            print("Model not loaded")
            return np.zeros(int(24000 * duration_seconds))
            
        import torch
        
        inputs = self.processor(
            text=[prompt],
            padding=True,
            return_tensors="pt"
        )
        
        # Calculate tokens needed
        tokens_per_second = 50  # Approximate for MusicGen
        max_new_tokens = int(duration_seconds * tokens_per_second)
        
        with torch.no_grad():
            audio_values = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                guidance_scale=guidance_scale,
                do_sample=True,
            )
            
        return audio_values[0, 0].numpy()
    
    def emotional_state_to_prompt(self, state: EmotionalState, 
                                  params: MusicalParameters) -> str:
        """
        Convert EmotionalState to text prompt for generation.
        """
        # Build prompt from emotional parameters
        parts = []
        
        # Emotion
        parts.append(f"{state.primary_emotion} emotional")
        
        # Tempo feel
        if params.tempo_suggested < 80:
            parts.append("slow")
        elif params.tempo_suggested > 120:
            parts.append("fast")
        else:
            parts.append("moderate tempo")
            
        # Mood/mode
        if Mode.MINOR in params.mode_weights:
            parts.append("minor key")
        elif Mode.LYDIAN in params.mode_weights:
            parts.append("bright floating")
        elif Mode.PHRYGIAN in params.mode_weights:
            parts.append("dark tense")
            
        # Style
        if params.imperfection_level > 0.3:
            parts.append("lo-fi bedroom recording")
        else:
            parts.append("clean production")
            
        # Instruments (generic)
        parts.append("acoustic guitar, soft drums, piano")
        
        return ", ".join(parts)


# ============================================================================
# 13. POST-PROCESSING
# ============================================================================

class PostProcessor:
    """
    Applies final processing to generated audio.
    Lo-fi effects, tape saturation, etc.
    """
    
    def __init__(self, sample_rate: int = 24000):
        self.sample_rate = sample_rate
        
    def apply_lofi(self, audio: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Apply lo-fi degradation."""
        # Bit reduction
        bits = int(16 - intensity * 8)  # 16 down to 8 bits
        factor = 2 ** bits
        audio = np.round(audio * factor) / factor
        
        # High-frequency rolloff
        audio = self._lowpass(audio, 8000 - intensity * 4000)
        
        # Add subtle noise
        noise = np.random.randn(len(audio)) * 0.005 * intensity
        audio = audio + noise
        
        return np.clip(audio, -1, 1)
    
    def apply_tape_saturation(self, audio: np.ndarray, 
                              drive: float = 0.3) -> np.ndarray:
        """Apply tape-style saturation."""
        # Soft clipping
        audio = np.tanh(audio * (1 + drive * 2))
        
        # Gentle compression
        threshold = 0.7
        ratio = 3.0
        above_threshold = np.abs(audio) > threshold
        audio[above_threshold] = (
            np.sign(audio[above_threshold]) * 
            (threshold + (np.abs(audio[above_threshold]) - threshold) / ratio)
        )
        
        return audio
    
    def apply_vinyl_crackle(self, audio: np.ndarray, 
                            amount: float = 0.1) -> np.ndarray:
        """Add vinyl crackle."""
        # Random pops
        n_pops = int(len(audio) / self.sample_rate * 20 * amount)
        pop_positions = np.random.randint(0, len(audio), n_pops)
        
        for pos in pop_positions:
            if pos < len(audio) - 100:
                # Short impulse
                audio[pos:pos+50] += np.random.randn(50) * 0.1 * amount
                
        # Constant noise floor
        noise = np.random.randn(len(audio)) * 0.003 * amount
        audio = audio + noise
        
        return np.clip(audio, -1, 1)
    
    def _lowpass(self, audio: np.ndarray, cutoff: float) -> np.ndarray:
        """Simple lowpass filter."""
        from scipy import signal
        
        nyquist = self.sample_rate / 2
        normalized_cutoff = cutoff / nyquist
        b, a = signal.butter(4, normalized_cutoff, btype='low')
        
        return signal.filtfilt(b, a, audio)
    
    def process_for_emotion(self, audio: np.ndarray, 
                           params: MusicalParameters) -> np.ndarray:
        """Apply processing based on emotional parameters."""
        # Lo-fi for high imperfection
        if params.imperfection_level > 0.2:
            audio = self.apply_lofi(audio, params.imperfection_level)
            
        # Tape saturation for warmth
        if params.imperfection_level > 0.3:
            audio = self.apply_tape_saturation(audio, params.imperfection_level * 0.5)
            
        # Vinyl for nostalgia
        if params.imperfection_level > 0.4:
            audio = self.apply_vinyl_crackle(audio, params.imperfection_level * 0.3)
            
        return audio


# ============================================================================
# 14. STREAMLIT UI LAYER
# ============================================================================

def create_streamlit_app():
    """
    Generate Streamlit UI code.
    Run with: streamlit run idaw_ui.py
    """
    
    ui_code = '''
import streamlit as st
import sys
sys.path.append(".")
from idaw_complete_pipeline import (
    InterrogationEngine, 
    get_parameters_for_state,
    StructureGenerator,
    HarmonyEngine,
    MelodyEngine,
    GrooveEngine,
    MIDIBuilder,
    EMOTIONAL_PRESETS
)
from pathlib import Path

st.set_page_config(page_title="iDAW", page_icon="🎵", layout="wide")

st.title("🎵 iDAW - intelligent Digital Audio Workspace")
st.markdown("*Interrogate Before Generate*")

# Sidebar - Presets
with st.sidebar:
    st.header("Quick Presets")
    preset = st.selectbox("Emotion Preset", list(EMOTIONAL_PRESETS.keys()))
    
    st.header("Manual Overrides")
    tempo = st.slider("Tempo", 40, 180, 90)
    humanize = st.slider("Humanize", 0.0, 0.5, 0.15)
    dissonance = st.slider("Dissonance", 0.0, 1.0, 0.3)

# Main area - Interrogation
st.header("1. Interrogation")

user_input = st.text_area(
    "Describe your song (emotions, feel, vibe):",
    placeholder="e.g., 'slow grief song, acoustic, laid back feel, lo-fi bedroom recording'",
    height=100
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Phase 0: Core Wound")
    core_event = st.text_input("What happened?")
    core_longing = st.text_input("What do you wish you could feel?")

with col2:
    st.subheader("Phase 1: Emotional Intent")
    vulnerability = st.slider("Vulnerability", 0, 10, 5)
    misdirection = st.checkbox("Use misdirection (sounds like X but really Y)")

# Generate button
if st.button("🎵 Generate", type="primary"):
    with st.spinner("Interrogating..."):
        engine = InterrogationEngine()
        state = engine.quick_interrogate(user_input or f"{preset} song")
        
        # Override with preset if selected
        if preset:
            state.primary_emotion = preset
            
        params = get_parameters_for_state(state)
        
        # Apply manual overrides
        params.tempo_suggested = tempo
        params.humanize = humanize
        params.dissonance = dissonance
        params.vulnerability = vulnerability / 10.0
        
    st.success("Emotional state captured!")
    
    # Display parameters
    st.header("2. Musical Parameters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tempo", f"{params.tempo_suggested} BPM")
        st.metric("Timing Feel", params.timing_feel.value)
    with col2:
        st.metric("Dissonance", f"{params.dissonance:.0%}")
        st.metric("Density", f"{params.density_suggested:.1f}x")
    with col3:
        st.metric("Humanize", f"{params.humanize:.0%}")
        st.metric("Imperfection", f"{params.imperfection_level:.0%}")
    
    # Generate structure
    st.header("3. Structure")
    struct_gen = StructureGenerator()
    structure = struct_gen.generate(params, state)
    
    structure_str = " → ".join([f"{s.name}({s.bars})" for s in structure])
    st.write(structure_str)
    
    # Generate music
    with st.spinner("Generating MIDI..."):
        params.key_signature = "F"  # Default to F for Kelly song
        
        harmony = HarmonyEngine(params)
        total_bars = sum(s.bars for s in structure)
        progression = harmony.generate_progression(total_bars, state.primary_emotion)
        
        melody_engine = MelodyEngine(params, harmony)
        melody = melody_engine.generate(progression, total_bars)
        
        groove = GrooveEngine(params)
        drums = groove.generate_drums(total_bars, "sparse" if params.density_suggested < 0.8 else "basic")
        
        # Build MIDI
        builder = MIDIBuilder(bpm=params.tempo_suggested)
        builder.add_track("melody", melody)
        builder.add_track("drums", drums)
        
        # Save
        output_dir = Path.home() / "Music" / "iDAW_Output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"{timestamp}_{state.primary_emotion}.mid"
        
        builder.save(output_path)
    
    st.success(f"✓ Saved to {output_path}")
    
    # Download button
    with open(output_path, "rb") as f:
        st.download_button(
            "📥 Download MIDI",
            f,
            file_name=output_path.name,
            mime="audio/midi"
        )

# Footer
st.markdown("---")
st.markdown("*iDAW: Making musicians braver since 2025*")
'''
    
    return ui_code


# ============================================================================
# 15. FOLDER LAYOUT
# ============================================================================

FOLDER_STRUCTURE = """
iDAW-Music-Brain/
├── .claude/
│   └── settings.json           # Claude Code config
├── .cursorrules                # Cursor IDE rules
├── CLAUDE.md                   # Project context for AI
│
├── music_brain/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── emotional_state.py      # EmotionalState dataclass
│   │   ├── musical_parameters.py   # MusicalParameters dataclass
│   │   └── presets.py              # EMOTIONAL_PRESETS dict
│   │
│   ├── interrogation/
│   │   ├── __init__.py
│   │   └── engine.py               # InterrogationEngine
│   │
│   ├── structure/
│   │   ├── __init__.py
│   │   └── generator.py            # StructureGenerator
│   │
│   ├── harmony/
│   │   ├── __init__.py
│   │   ├── engine.py               # HarmonyEngine
│   │   └── progressions.py         # Chord progression templates
│   │
│   ├── melody/
│   │   ├── __init__.py
│   │   └── engine.py               # MelodyEngine
│   │
│   ├── groove/
│   │   ├── __init__.py
│   │   ├── engine.py               # GrooveEngine
│   │   └── patterns.py             # Drum patterns
│   │
│   ├── midi/
│   │   ├── __init__.py
│   │   ├── builder.py              # MIDIBuilder
│   │   └── mpk_mini.py             # MPKMiniController
│   │
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── tokenizer.py            # AudioTokenizer
│   │   ├── generator.py            # AudioGenerator (transformer)
│   │   └── postprocess.py          # PostProcessor
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── quality_checker.py      # Quality scoring
│   │   ├── critic.py               # Interpretation critic
│   │   └── arbiter.py              # Final judgment
│   │
│   ├── learning/
│   │   ├── __init__.py
│   │   └── user_preferences.py     # Future: learn from feedback
│   │
│   └── data/
│       ├── presets.json            # Emotional presets
│       ├── progressions.json       # Chord progressions
│       ├── patterns.json           # Drum patterns
│       ├── rule_breaks.json        # Rule-breaking database
│       └── vernacular.json         # Vernacular translations
│
├── ui/
│   ├── __init__.py
│   └── streamlit_app.py            # Streamlit UI
│
├── cli/
│   ├── __init__.py
│   └── main.py                     # Typer CLI
│
├── tests/
│   ├── __init__.py
│   ├── test_core/
│   ├── test_interrogation/
│   ├── test_harmony/
│   ├── test_groove/
│   └── test_integration/
│
├── samples/                        # User's sample library (gitignored)
│   └── .gitkeep
│
├── output/                         # Generated files (gitignored)
│   └── .gitkeep
│
├── docs/
│   ├── philosophy.md               # "Interrogate Before Generate"
│   ├── api.md                      # API documentation
│   └── examples/
│
├── scripts/
│   ├── setup.sh                    # Environment setup
│   └── install_deps.py             # Dependency installer
│
├── pyproject.toml                  # Project config
├── requirements.txt                # Python deps
├── README.md
└── LICENSE
"""


# ============================================================================
# 16. MAIN PIPELINE
# ============================================================================

class iDAWPipeline:
    """
    Complete pipeline orchestrator.
    
    USER PROMPT → Interrogation → EmotionalState → MusicalParameters
    → Structure Generator → Harmony Engine → Melody Engine
    → Groove Engine → MIDI Builder → Audio Tokenizer
    → Audio Generator → Post-Processing → Final Audio
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path.home() / "Music" / "iDAW_Output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.interrogation = InterrogationEngine()
        self.structure_gen = StructureGenerator()
        self.post_processor = PostProcessor()
        
        # Optional components (load on demand)
        self.audio_tokenizer = None
        self.audio_generator = None
        self.mpk_controller = None
        
    def generate(self, user_input: str, 
                 output_audio: bool = False,
                 use_mpk: bool = False) -> Dict[str, Any]:
        """
        Full pipeline execution.
        
        Returns dict with:
            - emotional_state: EmotionalState
            - parameters: MusicalParameters  
            - structure: List[SongSection]
            - midi_path: Path
            - audio_path: Path (if output_audio=True)
        """
        results = {}
        
        # 1. INTERROGATION
        print("1. Interrogating...")
        state = self.interrogation.quick_interrogate(user_input)
        results["emotional_state"] = state
        print(f"   → Primary emotion: {state.primary_emotion}")
        
        # 2. EMOTIONAL STATE → MUSICAL PARAMETERS
        print("2. Translating to musical parameters...")
        params = get_parameters_for_state(state)
        results["parameters"] = params
        print(f"   → {params.tempo_suggested} BPM, {params.timing_feel.value} beat")
        
        # 3. STRUCTURE GENERATION
        print("3. Generating structure...")
        structure = self.structure_gen.generate(params, state)
        results["structure"] = structure
        total_bars = sum(s.bars for s in structure)
        print(f"   → {len(structure)} sections, {total_bars} bars")
        
        # 4. HARMONY ENGINE
        print("4. Generating harmony...")
        harmony = HarmonyEngine(params)
        progression = harmony.generate_progression(total_bars, state.primary_emotion)
        results["progression"] = progression
        print(f"   → {len(progression)} chords")
        
        # 5. MELODY ENGINE
        print("5. Generating melody...")
        melody_engine = MelodyEngine(params, harmony)
        melody = melody_engine.generate(progression, total_bars)
        results["melody"] = melody
        print(f"   → {len(melody)} notes")
        
        # 6. GROOVE ENGINE
        print("6. Generating groove...")
        groove = GrooveEngine(params)
        style = "sparse" if params.density_suggested < 0.8 else "basic"
        drums = groove.generate_drums(total_bars, style)
        results["drums"] = drums
        print(f"   → {len(drums)} drum hits, {style} style")
        
        # 7. MIDI BUILDER
        print("7. Building MIDI...")
        builder = MIDIBuilder(bpm=params.tempo_suggested)
        builder.add_track("melody", melody)
        builder.add_track("drums", drums)
        
        # Add MPK input if connected
        if use_mpk and self.mpk_controller:
            mpk_events = self.mpk_controller.recording
            if mpk_events:
                builder.add_track("mpk_live", mpk_events)
                
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        midi_path = self.output_dir / f"{timestamp}_{state.primary_emotion}.mid"
        builder.save(midi_path)
        results["midi_path"] = midi_path
        print(f"   → Saved: {midi_path}")
        
        # 8-10. AUDIO GENERATION (optional)
        if output_audio:
            print("8. Tokenizing for audio generation...")
            # Load models if needed
            if self.audio_generator is None:
                self.audio_generator = AudioGenerator()
                self.audio_generator.load_model()
                
            print("9. Generating audio...")
            prompt = self.audio_generator.emotional_state_to_prompt(state, params)
            audio = self.audio_generator.generate_from_prompt(prompt, duration_seconds=30)
            
            print("10. Post-processing...")
            audio = self.post_processor.process_for_emotion(audio, params)
            
            # Save audio
            audio_path = midi_path.with_suffix(".wav")
            from scipy.io import wavfile
            wavfile.write(str(audio_path), 24000, (audio * 32767).astype(np.int16))
            results["audio_path"] = audio_path
            print(f"    → Saved: {audio_path}")
            
        print("\n✓ Pipeline complete!")
        return results
    
    def connect_mpk(self) -> bool:
        """Connect to AKAI MPK Mini."""
        self.mpk_controller = MPKMiniController()
        return self.mpk_controller.connect()


# ============================================================================
# 17. CLI ENTRY POINT
# ============================================================================

def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="iDAW - intelligent Digital Audio Workspace")
    parser.add_argument("prompt", nargs="?", default=None, help="Song description")
    parser.add_argument("--audio", action="store_true", help="Generate audio (requires transformers)")
    parser.add_argument("--mpk", action="store_true", help="Connect to AKAI MPK Mini")
    parser.add_argument("--ui", action="store_true", help="Launch Streamlit UI")
    parser.add_argument("--folder-layout", action="store_true", help="Print recommended folder structure")
    
    args = parser.parse_args()
    
    if args.folder_layout:
        print(FOLDER_STRUCTURE)
        return
        
    if args.ui:
        # Generate and run Streamlit app
        ui_code = create_streamlit_app()
        ui_path = Path("idaw_ui.py")
        ui_path.write_text(ui_code)
        print(f"Streamlit UI saved to {ui_path}")
        print("Run with: streamlit run idaw_ui.py")
        return
        
    # Interactive mode if no prompt
    if args.prompt is None:
        print("iDAW - intelligent Digital Audio Workspace")
        print("=" * 40)
        args.prompt = input("Describe your song: ")
        
    # Run pipeline
    pipeline = iDAWPipeline()
    
    if args.mpk:
        pipeline.connect_mpk()
        
    results = pipeline.generate(
        args.prompt,
        output_audio=args.audio,
        use_mpk=args.mpk
    )
    
    print(f"\nMIDI: {results['midi_path']}")
    if "audio_path" in results:
        print(f"Audio: {results['audio_path']}")


if __name__ == "__main__":
    main()
