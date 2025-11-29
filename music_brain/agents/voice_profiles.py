#!/usr/bin/env python3
"""
Voice Profiles - Customizable Voice Characteristics

LOCAL SYSTEM - All profiles stored locally, learns from user input.

Features:
- Voice pitch customization (base pitch, range, contour)
- Accent support (phoneme mappings for regional accents)
- Speech impediment simulation/compensation
- Learning from user examples
- Profile persistence (~/.daiw/voice_profiles/)

Supported Accents:
- American (General, Southern, Boston, New York)
- British (RP, Cockney, Scottish, Irish)
- Australian
- South African
- Indian English
- Caribbean

Speech Patterns:
- Stutter/Stammering
- Lisp (frontal, lateral)
- Rhotacism (R difficulty)
- Cluttering (fast/irregular)
- Dysarthria (muscle weakness)

Usage:
    from music_brain.agents.voice_profiles import VoiceProfileManager

    manager = VoiceProfileManager()

    # Create custom profile
    profile = manager.create_profile(
        name="my_voice",
        base_pitch=180,  # Hz
        accent="southern_us",
        speech_patterns=["mild_stutter"]
    )

    # Apply to text
    modified_text, params = manager.apply_profile("Hello world", "my_voice")
"""

import os
import json
import re
import random
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
import copy


# =============================================================================
# Enums and Constants
# =============================================================================

class Gender(str, Enum):
    """Voice gender for pitch defaults."""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"
    CHILD = "child"


class AccentRegion(str, Enum):
    """Supported accent regions."""
    # American
    AMERICAN_GENERAL = "american_general"
    AMERICAN_SOUTHERN = "southern_us"
    AMERICAN_BOSTON = "boston"
    AMERICAN_NYC = "new_york"
    AMERICAN_MIDWEST = "midwest"
    AMERICAN_CALIFORNIA = "california"

    # British
    BRITISH_RP = "british_rp"
    BRITISH_COCKNEY = "cockney"
    BRITISH_SCOTTISH = "scottish"
    BRITISH_IRISH = "irish"
    BRITISH_WELSH = "welsh"
    BRITISH_NORTHERN = "northern_uk"

    # Other English
    AUSTRALIAN = "australian"
    NEW_ZEALAND = "new_zealand"
    SOUTH_AFRICAN = "south_african"
    INDIAN = "indian_english"
    CARIBBEAN = "caribbean"
    CANADIAN = "canadian"

    # Non-native patterns
    SPANISH_ACCENT = "spanish_accent"
    FRENCH_ACCENT = "french_accent"
    GERMAN_ACCENT = "german_accent"
    ASIAN_ACCENT = "asian_accent"
    RUSSIAN_ACCENT = "russian_accent"


class SpeechPattern(str, Enum):
    """Speech patterns and impediments."""
    NONE = "none"

    # Fluency
    MILD_STUTTER = "mild_stutter"
    MODERATE_STUTTER = "moderate_stutter"
    SEVERE_STUTTER = "severe_stutter"
    CLUTTERING = "cluttering"

    # Articulation
    FRONTAL_LISP = "frontal_lisp"      # S/Z → TH
    LATERAL_LISP = "lateral_lisp"       # Slushy S
    RHOTACISM = "rhotacism"             # R → W
    LAMBDACISM = "lambdacism"           # L difficulty

    # Voice
    HOARSE = "hoarse"
    BREATHY = "breathy"
    NASAL = "nasal"
    DENASALIZED = "denasalized"         # Blocked nose sound

    # Rate
    FAST_SPEECH = "fast_speech"
    SLOW_SPEECH = "slow_speech"

    # Other
    MONOTONE = "monotone"
    SING_SONG = "sing_song"             # Exaggerated prosody


# Default pitch ranges by gender (Hz)
PITCH_DEFAULTS = {
    Gender.MALE: {"base": 120, "min": 80, "max": 180},
    Gender.FEMALE: {"base": 220, "min": 165, "max": 300},
    Gender.NEUTRAL: {"base": 170, "min": 120, "max": 240},
    Gender.CHILD: {"base": 300, "min": 250, "max": 400},
}


# =============================================================================
# Accent Phoneme Mappings
# =============================================================================

# Maps standard phonemes to accent-specific variants
# Format: {accent: {standard: replacement}}

ACCENT_PHONEME_MAPS = {
    AccentRegion.AMERICAN_SOUTHERN: {
        # Vowel shifts
        "I": "ah-ee",      # "ride" → "rahd"
        "ow": "ah",        # "about" → "abaht"
        "ing": "in'",      # "walking" → "walkin'"
        # Consonants
        "r": "r",          # Strong R (rhotic)
    },

    AccentRegion.BRITISH_RP: {
        # Non-rhotic (drop R before consonants/end)
        "r_end": "",       # "car" → "cah"
        "r_cons": "",      # "card" → "cahd"
        # Vowels
        "a_bath": "ah",    # "bath" → "bahth"
        "o_lot": "o",      # Rounded O
    },

    AccentRegion.BRITISH_COCKNEY: {
        # TH-fronting
        "th_voice": "v",   # "brother" → "bruvver"
        "th_unvoice": "f", # "think" → "fink"
        # H-dropping
        "h_init": "",      # "hello" → "'ello"
        # Glottal stop
        "t_mid": "ʔ",      # "bottle" → "bo'le"
        # Diphthongs
        "ay": "ai",        # "face" → "faice"
        "ow": "ah",        # "mouth" → "mahf"
    },

    AccentRegion.BRITISH_SCOTTISH: {
        # Rhotic
        "r": "r",          # Trilled or tapped R
        # Vowels
        "oo": "u",         # "good" → shorter
        "ou": "oo",        # "house" → "hoose"
    },

    AccentRegion.BRITISH_IRISH: {
        # TH sounds
        "th_voice": "d",   # "the" → "de"
        "th_unvoice": "t", # "think" → "tink"
        # Soft T
        "t": "t̪",
    },

    AccentRegion.AUSTRALIAN: {
        # Vowel shifts
        "ay": "ai",        # "day" → "die" sound
        "ee": "i",         # Shorter
        "i": "oi",         # "fish" → "foish"
    },

    AccentRegion.INDIAN: {
        # Retroflex consonants
        "t": "ʈ",
        "d": "ɖ",
        # V/W merge
        "v": "w",          # "very" → "wery"
        "w": "v",          # "what" → "vhat"
        # Aspirated stops
        "p": "pʰ",
        "k": "kʰ",
    },

    AccentRegion.SPANISH_ACCENT: {
        # Vowel purity
        "short_i": "ee",   # "sit" → "seet"
        "short_u": "oo",   # "put" → "poot"
        # Consonants
        "v": "b",          # "very" → "bery"
        "j": "y",          # "job" → "yob"
        "h": "",           # Often silent
    },

    AccentRegion.FRENCH_ACCENT: {
        # TH → Z/S
        "th_voice": "z",   # "the" → "ze"
        "th_unvoice": "s", # "think" → "sink"
        # H silent
        "h_init": "",      # "hello" → "ello"
        # R uvular
        "r": "ʁ",
    },
}

# Word-level accent modifications
ACCENT_WORD_MAPS = {
    AccentRegion.AMERICAN_SOUTHERN: {
        "going to": "gonna",
        "want to": "wanna",
        "you all": "y'all",
        "fixing to": "fixin' to",
        "might could": "might could",
    },

    AccentRegion.BRITISH_COCKNEY: {
        "hello": "'ello",
        "isn't it": "innit",
        "something": "somefink",
        "nothing": "nuffink",
        "think": "fink",
        "brother": "bruvver",
        "mother": "muvver",
    },

    AccentRegion.AUSTRALIAN: {
        "afternoon": "arvo",
        "breakfast": "brekkie",
        "definitely": "defo",
        "thank you": "ta",
    },
}


# =============================================================================
# Speech Pattern Modifications
# =============================================================================

class SpeechPatternProcessor:
    """Processes text for speech patterns and impediments."""

    @staticmethod
    def apply_stutter(text: str, severity: str = "mild") -> str:
        """
        Apply stuttering pattern to text.

        Stuttering typically occurs on:
        - Initial consonants of words
        - Stressed syllables
        - After pauses
        """
        words = text.split()
        result = []

        # Probability of stutter per word
        prob = {"mild": 0.1, "moderate": 0.25, "severe": 0.4}.get(severity, 0.1)

        stutter_consonants = "bcdfghjklmnpqrstvwxyz"

        for i, word in enumerate(words):
            if not word:
                continue

            # Check if should stutter this word
            should_stutter = random.random() < prob

            # More likely on stressed/important words
            if word[0].isupper() or i == 0:
                should_stutter = should_stutter or random.random() < prob

            if should_stutter and word[0].lower() in stutter_consonants:
                # Repeat initial consonant(s)
                initial = ""
                for char in word:
                    if char.lower() in stutter_consonants:
                        initial += char
                    else:
                        break

                if initial:
                    if severity == "severe":
                        # Block then release
                        result.append(f"{initial}-{initial}-{word}")
                    elif severity == "moderate":
                        result.append(f"{initial}-{word}")
                    else:
                        # Mild repetition
                        result.append(f"{initial[0]}-{word}")
                else:
                    result.append(word)
            else:
                result.append(word)

        return " ".join(result)

    @staticmethod
    def apply_lisp(text: str, lisp_type: str = "frontal") -> str:
        """
        Apply lisp to text.

        Frontal lisp: S/Z sounds become TH
        Lateral lisp: S sounds are "slushy" (marked with *)
        """
        if lisp_type == "frontal":
            # S → TH (unvoiced)
            text = re.sub(r'\bs', 'th', text)
            text = re.sub(r's\b', 'th', text)
            text = re.sub(r'ss', 'th', text)
            text = re.sub(r'S', 'Th', text)

            # Z → TH (voiced, written as "th" but voiced)
            text = re.sub(r'\bz', 'th', text)
            text = re.sub(r'z\b', 'th', text)
            text = re.sub(r'Z', 'Th', text)

        elif lisp_type == "lateral":
            # Mark S sounds as slushy (for TTS interpretation)
            text = re.sub(r's', 'ṣ', text)
            text = re.sub(r'S', 'Ṣ', text)

        return text

    @staticmethod
    def apply_rhotacism(text: str) -> str:
        """
        Apply rhotacism (R → W substitution).

        Common in children and some adults.
        "rabbit" → "wabbit", "red" → "wed"
        """
        # R at start of words or syllables
        text = re.sub(r'\br', 'w', text)
        text = re.sub(r'\bR', 'W', text)

        # R after consonants
        text = re.sub(r'([bcdfghjklmnpqstvxz])r', r'\1w', text)

        return text

    @staticmethod
    def apply_cluttering(text: str) -> str:
        """
        Apply cluttering pattern.

        Cluttering involves:
        - Collapsed syllables
        - Word telescoping
        - Irregular rate markers
        """
        words = text.split()
        result = []

        for word in words:
            if len(word) > 6 and random.random() < 0.3:
                # Telescope long words
                mid = len(word) // 2
                word = word[:mid-1] + word[mid+1:]

            result.append(word)

            # Occasional run-on (remove space)
            if random.random() < 0.15:
                result[-1] = result[-1] + "-"

        return " ".join(result).replace("- ", "")

    @staticmethod
    def apply_pattern(text: str, pattern: SpeechPattern) -> str:
        """Apply a speech pattern to text."""
        if pattern == SpeechPattern.NONE:
            return text

        # Stuttering
        if pattern == SpeechPattern.MILD_STUTTER:
            return SpeechPatternProcessor.apply_stutter(text, "mild")
        elif pattern == SpeechPattern.MODERATE_STUTTER:
            return SpeechPatternProcessor.apply_stutter(text, "moderate")
        elif pattern == SpeechPattern.SEVERE_STUTTER:
            return SpeechPatternProcessor.apply_stutter(text, "severe")

        # Articulation
        elif pattern == SpeechPattern.FRONTAL_LISP:
            return SpeechPatternProcessor.apply_lisp(text, "frontal")
        elif pattern == SpeechPattern.LATERAL_LISP:
            return SpeechPatternProcessor.apply_lisp(text, "lateral")
        elif pattern == SpeechPattern.RHOTACISM:
            return SpeechPatternProcessor.apply_rhotacism(text)

        # Rate
        elif pattern == SpeechPattern.CLUTTERING:
            return SpeechPatternProcessor.apply_cluttering(text)

        return text


# =============================================================================
# Voice Profile
# =============================================================================

@dataclass
class VoiceProfile:
    """
    Complete voice profile with pitch, accent, and speech patterns.

    All settings are local and customizable.
    """
    # Identity
    name: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Pitch characteristics (Hz)
    gender: Gender = Gender.NEUTRAL
    base_pitch: float = 170.0          # Default pitch
    pitch_range: float = 50.0          # Variation range
    pitch_contour: str = "natural"     # natural, monotone, sing_song, questioning

    # Timing
    speech_rate: float = 1.0           # 1.0 = normal, 0.5 = slow, 2.0 = fast
    pause_frequency: float = 1.0       # Pause insertion frequency

    # Accent
    accent: AccentRegion = AccentRegion.AMERICAN_GENERAL
    accent_strength: float = 1.0       # 0.0 = none, 1.0 = full

    # Speech patterns
    speech_patterns: List[SpeechPattern] = field(default_factory=list)

    # Voice quality
    breathiness: float = 0.0           # 0.0 - 1.0
    hoarseness: float = 0.0            # 0.0 - 1.0
    nasality: float = 0.0              # 0.0 - 1.0
    creakiness: float = 0.0            # Vocal fry, 0.0 - 1.0

    # Formants (for formant synthesis)
    formant_shift: float = 0.0         # -1.0 to 1.0
    formant_scale: float = 1.0         # 0.8 - 1.2

    # Learned preferences (updated by learning system)
    learned_words: Dict[str, str] = field(default_factory=dict)  # Custom pronunciations
    learned_phrases: Dict[str, str] = field(default_factory=dict)

    # Metadata
    notes: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["gender"] = self.gender.value
        data["accent"] = self.accent.value
        data["speech_patterns"] = [p.value for p in self.speech_patterns]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VoiceProfile":
        """Create from dictionary."""
        data = copy.deepcopy(data)

        if "gender" in data and isinstance(data["gender"], str):
            data["gender"] = Gender(data["gender"])

        if "accent" in data and isinstance(data["accent"], str):
            data["accent"] = AccentRegion(data["accent"])

        if "speech_patterns" in data:
            data["speech_patterns"] = [
                SpeechPattern(p) if isinstance(p, str) else p
                for p in data["speech_patterns"]
            ]

        return cls(**data)


# =============================================================================
# Voice Profile Manager
# =============================================================================

class VoiceProfileManager:
    """
    Manages voice profiles with learning capabilities.

    LOCAL SYSTEM - All data stored in ~/.daiw/voice_profiles/
    """

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = Path(
            storage_dir or os.path.expanduser("~/.daiw/voice_profiles")
        )
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self._profiles: Dict[str, VoiceProfile] = {}
        self._active_profile: Optional[str] = None
        self._pattern_processor = SpeechPatternProcessor()

        # Load existing profiles
        self._load_all_profiles()

    def _load_all_profiles(self):
        """Load all profiles from storage."""
        for filepath in self.storage_dir.glob("*.json"):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    profile = VoiceProfile.from_dict(data)
                    self._profiles[profile.name] = profile
            except Exception as e:
                print(f"Error loading profile {filepath}: {e}")

    def _save_profile(self, profile: VoiceProfile):
        """Save a profile to storage."""
        filepath = self.storage_dir / f"{profile.name}.json"
        with open(filepath, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)

    # =========================================================================
    # Profile Management
    # =========================================================================

    def create_profile(
        self,
        name: str,
        gender: Gender = Gender.NEUTRAL,
        base_pitch: Optional[float] = None,
        accent: AccentRegion = AccentRegion.AMERICAN_GENERAL,
        speech_patterns: Optional[List[SpeechPattern]] = None,
        **kwargs
    ) -> VoiceProfile:
        """
        Create a new voice profile.

        Args:
            name: Profile name
            gender: Voice gender (for pitch defaults)
            base_pitch: Base pitch in Hz (auto if None)
            accent: Accent region
            speech_patterns: List of speech patterns
            **kwargs: Additional VoiceProfile fields

        Returns:
            Created VoiceProfile
        """
        # Auto-set pitch from gender if not provided
        if base_pitch is None:
            base_pitch = PITCH_DEFAULTS[gender]["base"]

        profile = VoiceProfile(
            name=name,
            gender=gender,
            base_pitch=base_pitch,
            accent=accent,
            speech_patterns=speech_patterns or [],
            **kwargs
        )

        self._profiles[name] = profile
        self._save_profile(profile)

        return profile

    def get_profile(self, name: str) -> Optional[VoiceProfile]:
        """Get a profile by name."""
        return self._profiles.get(name)

    def list_profiles(self) -> List[str]:
        """List all profile names."""
        return list(self._profiles.keys())

    def delete_profile(self, name: str) -> bool:
        """Delete a profile."""
        if name in self._profiles:
            del self._profiles[name]
            filepath = self.storage_dir / f"{name}.json"
            if filepath.exists():
                filepath.unlink()
            return True
        return False

    def set_active_profile(self, name: str) -> bool:
        """Set the active profile."""
        if name in self._profiles:
            self._active_profile = name
            return True
        return False

    @property
    def active_profile(self) -> Optional[VoiceProfile]:
        """Get the active profile."""
        if self._active_profile:
            return self._profiles.get(self._active_profile)
        return None

    # =========================================================================
    # Profile Application
    # =========================================================================

    def apply_profile(
        self,
        text: str,
        profile_name: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Apply a voice profile to text.

        Returns:
            Tuple of (modified_text, voice_parameters)
        """
        profile = self._profiles.get(profile_name) if profile_name else self.active_profile

        if not profile:
            return text, {}

        modified_text = text

        # Apply learned words/phrases first
        for phrase, replacement in profile.learned_phrases.items():
            modified_text = modified_text.replace(phrase, replacement)

        for word, replacement in profile.learned_words.items():
            # Word boundary matching
            modified_text = re.sub(
                rf'\b{re.escape(word)}\b',
                replacement,
                modified_text,
                flags=re.IGNORECASE
            )

        # Apply accent
        if profile.accent_strength > 0:
            modified_text = self._apply_accent(
                modified_text,
                profile.accent,
                profile.accent_strength
            )

        # Apply speech patterns
        for pattern in profile.speech_patterns:
            modified_text = self._pattern_processor.apply_pattern(
                modified_text,
                pattern
            )

        # Build voice parameters for TTS
        params = {
            "pitch": profile.base_pitch,
            "pitch_range": profile.pitch_range,
            "rate": profile.speech_rate,
            "breathiness": profile.breathiness,
            "hoarseness": profile.hoarseness,
            "nasality": profile.nasality,
            "formant_shift": profile.formant_shift,
        }

        return modified_text, params

    def _apply_accent(
        self,
        text: str,
        accent: AccentRegion,
        strength: float
    ) -> str:
        """Apply accent modifications to text."""
        # Word-level replacements
        word_map = ACCENT_WORD_MAPS.get(accent, {})
        for standard, accented in word_map.items():
            if random.random() < strength:
                text = re.sub(
                    rf'\b{re.escape(standard)}\b',
                    accented,
                    text,
                    flags=re.IGNORECASE
                )

        return text

    # =========================================================================
    # Learning System
    # =========================================================================

    def learn_pronunciation(
        self,
        profile_name: str,
        word: str,
        pronunciation: str
    ):
        """
        Learn a custom pronunciation for a word.

        Args:
            profile_name: Profile to update
            word: Original word
            pronunciation: How to pronounce it
        """
        profile = self._profiles.get(profile_name)
        if profile:
            profile.learned_words[word.lower()] = pronunciation
            profile.updated_at = datetime.now().isoformat()
            self._save_profile(profile)

    def learn_phrase(
        self,
        profile_name: str,
        phrase: str,
        replacement: str
    ):
        """
        Learn a custom phrase replacement.

        Args:
            profile_name: Profile to update
            phrase: Original phrase
            replacement: How to say it
        """
        profile = self._profiles.get(profile_name)
        if profile:
            profile.learned_phrases[phrase.lower()] = replacement
            profile.updated_at = datetime.now().isoformat()
            self._save_profile(profile)

    def forget_pronunciation(self, profile_name: str, word: str):
        """Remove a learned pronunciation."""
        profile = self._profiles.get(profile_name)
        if profile and word.lower() in profile.learned_words:
            del profile.learned_words[word.lower()]
            self._save_profile(profile)

    # =========================================================================
    # Presets
    # =========================================================================

    def create_preset_profiles(self):
        """Create common preset profiles."""
        presets = [
            # Gender defaults
            {
                "name": "male_default",
                "gender": Gender.MALE,
                "accent": AccentRegion.AMERICAN_GENERAL,
            },
            {
                "name": "female_default",
                "gender": Gender.FEMALE,
                "accent": AccentRegion.AMERICAN_GENERAL,
            },
            {
                "name": "child_default",
                "gender": Gender.CHILD,
                "accent": AccentRegion.AMERICAN_GENERAL,
            },

            # Accent presets
            {
                "name": "british_gentleman",
                "gender": Gender.MALE,
                "base_pitch": 130,
                "accent": AccentRegion.BRITISH_RP,
                "speech_rate": 0.9,
            },
            {
                "name": "southern_belle",
                "gender": Gender.FEMALE,
                "base_pitch": 240,
                "accent": AccentRegion.AMERICAN_SOUTHERN,
                "speech_rate": 0.85,
            },
            {
                "name": "aussie_mate",
                "gender": Gender.MALE,
                "accent": AccentRegion.AUSTRALIAN,
                "speech_rate": 1.1,
            },
            {
                "name": "irish_storyteller",
                "gender": Gender.NEUTRAL,
                "accent": AccentRegion.BRITISH_IRISH,
                "pitch_contour": "sing_song",
            },

            # Character voices
            {
                "name": "robot",
                "gender": Gender.NEUTRAL,
                "base_pitch": 150,
                "speech_rate": 0.9,
                "pitch_contour": "monotone",
                "breathiness": 0.0,
            },
            {
                "name": "whisper",
                "gender": Gender.NEUTRAL,
                "breathiness": 0.9,
                "speech_rate": 0.8,
                "base_pitch": 160,
            },
            {
                "name": "old_sage",
                "gender": Gender.MALE,
                "base_pitch": 95,
                "speech_rate": 0.7,
                "hoarseness": 0.4,
                "creakiness": 0.3,
            },
        ]

        for preset in presets:
            if preset["name"] not in self._profiles:
                self.create_profile(**preset)


# =============================================================================
# Convenience Functions
# =============================================================================

_default_manager: Optional[VoiceProfileManager] = None


def get_voice_manager() -> VoiceProfileManager:
    """Get or create the default voice profile manager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = VoiceProfileManager()
        _default_manager.create_preset_profiles()
    return _default_manager


def apply_voice_profile(text: str, profile: str = None) -> Tuple[str, Dict]:
    """Apply a voice profile to text."""
    return get_voice_manager().apply_profile(text, profile)


def learn_word(profile: str, word: str, pronunciation: str):
    """Learn a custom pronunciation."""
    get_voice_manager().learn_pronunciation(profile, word, pronunciation)


def list_accents() -> List[str]:
    """List all available accents."""
    return [a.value for a in AccentRegion]


def list_speech_patterns() -> List[str]:
    """List all available speech patterns."""
    return [p.value for p in SpeechPattern]


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("Voice Profile System - LOCAL")
    print("=" * 50)

    manager = VoiceProfileManager()
    manager.create_preset_profiles()

    print(f"\nAvailable profiles: {manager.list_profiles()}")
    print(f"\nAvailable accents: {list_accents()}")
    print(f"\nSpeech patterns: {list_speech_patterns()}")

    # Create custom profile
    profile = manager.create_profile(
        name="test_voice",
        gender=Gender.MALE,
        accent=AccentRegion.AMERICAN_SOUTHERN,
        speech_patterns=[SpeechPattern.MILD_STUTTER],
        speech_rate=0.9
    )
    print(f"\nCreated profile: {profile.name}")

    # Test application
    test_text = "Hello, I'm going to think about something."
    modified, params = manager.apply_profile(test_text, "test_voice")
    print(f"\nOriginal: {test_text}")
    print(f"Modified: {modified}")
    print(f"Params: {params}")

    # Test learning
    manager.learn_pronunciation("test_voice", "hello", "howdy")
    modified2, _ = manager.apply_profile(test_text, "test_voice")
    print(f"\nAfter learning 'hello' → 'howdy':")
    print(f"Modified: {modified2}")
