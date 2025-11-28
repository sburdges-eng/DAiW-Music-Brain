"""
Vernacular Translation Engine for iDAW
=======================================

Translates casual music descriptions to technical parameters.
Enables understanding of "make it fat and laid back" or "needs more glue"
and converting to actionable iDAW generation parameters.

Usage:
    from vernacular import VernacularTranslator
    
    translator = VernacularTranslator()
    params = translator.translate("fat laid back swung")
    # Returns: {'eq.low_mid': '+3dB', 'saturation': 'light', 
    #           'groove.pocket': 'behind', 'groove.swing': 0.62, ...}
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import json
from pathlib import Path


# =============================================================================
# ENUMS
# =============================================================================

class VernacularCategory(Enum):
    """Categories of vernacular terms."""
    RHYTHMIC = "rhythmic_onomatopoeia"
    TIMBRE = "timbre_texture"
    GROOVE = "groove_feel"
    MIX = "mix_production"
    MEME_THEORY = "meme_theory"
    RULE_BREAK = "rule_breaking"


class RuleBreakCode(Enum):
    """Rule-breaking codes for intent schema."""
    HARMONY_ParallelMotion = "HARMONY_ParallelMotion"
    HARMONY_ModalInterchange = "HARMONY_ModalInterchange"
    HARMONY_UnresolvedDissonance = "HARMONY_UnresolvedDissonance"
    HARMONY_TritoneSubstitution = "HARMONY_TritoneSubstitution"
    HARMONY_Polytonality = "HARMONY_Polytonality"
    RHYTHM_MeterAmbiguity = "RHYTHM_MeterAmbiguity"
    RHYTHM_ConstantDisplacement = "RHYTHM_ConstantDisplacement"
    RHYTHM_TempoFluctuation = "RHYTHM_TempoFluctuation"
    STRUCTURE_NonResolution = "STRUCTURE_NonResolution"
    PRODUCTION_BuriedVocals = "PRODUCTION_BuriedVocals"
    PRODUCTION_PitchImperfection = "PRODUCTION_PitchImperfection"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class VernacularMatch:
    """Result of matching a vernacular term."""
    term: str
    category: VernacularCategory
    meaning: str
    idaw_params: Dict
    confidence: float = 1.0


@dataclass
class TranslationResult:
    """Complete result of translating vernacular input."""
    original_input: str
    matched_terms: List[VernacularMatch]
    combined_params: Dict
    unmatched_words: List[str]
    suggested_rule_breaks: List[str] = field(default_factory=list)


# =============================================================================
# VERNACULAR DATABASE (Inline for single-file deployment)
# =============================================================================

VERNACULAR_DB = {
    "rhythmic_onomatopoeia": {
        "boots and cats": {"meaning": "Basic 4/4 beat", "idaw_params": {"groove.pattern": "four_on_floor"}},
        "untz": {"meaning": "Techno/EDM kick pattern", "idaw_params": {"groove.pattern": "four_on_floor", "tempo_range": [120, 140]}},
        "boom bap": {"meaning": "Hip-hop groove", "idaw_params": {"groove.pattern": "boom_bap"}},
        "chugga": {"meaning": "Palm-muted power chords", "idaw_params": {"groove.feel": "chug", "muting": True}},
        "brr": {"meaning": "Trap hi-hat rolls", "idaw_params": {"hihat.subdivision": 32, "pattern": "trap_roll"}},
        "skrrt": {"meaning": "Record scratch effect", "idaw_params": {"fx.type": "scratch"}},
    },
    
    "timbre_texture": {
        "fat": {"meaning": "Full low-mid frequencies", "idaw_params": {"eq.low_mid": "+3dB", "saturation": "light"}},
        "phat": {"meaning": "Full low-mid frequencies", "idaw_params": {"eq.low_mid": "+3dB", "saturation": "light"}},
        "thin": {"meaning": "Lacking low frequencies", "idaw_params": {"eq.low": "-6dB"}},
        "muddy": {"meaning": "Cluttered low-mids", "idaw_params": {"eq.problem": "mud", "target": "200-500Hz"}},
        "crispy": {"meaning": "Pleasant high-frequency presence", "idaw_params": {"eq.presence": "+2dB", "dist": "light_saturation"}},
        "crunchy": {"meaning": "Pleasant high-frequency presence", "idaw_params": {"eq.presence": "+2dB", "dist": "light_saturation"}},
        "warm": {"meaning": "Analog-like, reduced harshness", "idaw_params": {"character": "analog", "warmth": 0.7}},
        "bright": {"meaning": "Emphasized high frequencies", "idaw_params": {"eq.high": "+3dB"}},
        "dark": {"meaning": "Subdued high frequencies", "idaw_params": {"eq.high": "-4dB", "character": "dark"}},
        "punchy": {"meaning": "Strong transient attack", "idaw_params": {"comp.attack": "fast", "punch": "high"}},
        "scooped": {"meaning": "Reduced midrange", "idaw_params": {"eq.mid": "-6dB"}},
        "honky": {"meaning": "Unpleasant nasal midrange", "idaw_params": {"eq.problem": "honk", "target": "800-1200Hz"}},
        "boxy": {"meaning": "Cardboard-like midrange", "idaw_params": {"eq.problem": "box", "target": "300-600Hz"}},
        "glassy": {"meaning": "Clear, crystalline highs", "idaw_params": {"eq.high_shelf": "+2dB", "dist": "none"}},
        "airy": {"meaning": "Sense of space in highs", "idaw_params": {"eq.air": "+3dB", "target": "12kHz+"}},
    },
    
    "groove_feel": {
        "laid back": {"meaning": "Behind the beat", "idaw_params": {"groove.pocket": "behind", "offset_ms": 15}},
        "on top": {"meaning": "Ahead of the beat", "idaw_params": {"groove.pocket": "ahead", "offset_ms": -10}},
        "pushing": {"meaning": "Ahead of the beat", "idaw_params": {"groove.pocket": "ahead", "offset_ms": -10}},
        "in the pocket": {"meaning": "Perfect groove lock", "idaw_params": {"groove.pocket": "locked"}},
        "swung": {"meaning": "Triplet-based timing", "idaw_params": {"groove.swing": 0.62}},
        "swing": {"meaning": "Triplet-based timing", "idaw_params": {"groove.swing": 0.62}},
        "straight": {"meaning": "Even note divisions", "idaw_params": {"groove.swing": 0.5}},
        "tight": {"meaning": "Precise timing", "idaw_params": {"groove.tightness": 0.95}},
        "loose": {"meaning": "Human timing variation", "idaw_params": {"groove.humanize": 0.4}},
        "driving": {"meaning": "Forward momentum", "idaw_params": {"groove.energy": "forward"}},
        "breathing": {"meaning": "Organic tempo variation", "idaw_params": {"tempo.rubato": True}},
    },
    
    "mix_production": {
        "glue": {"meaning": "Cohesive mix", "idaw_params": {"bus_comp": True, "shared_space": True}},
        "separation": {"meaning": "Each element distinct", "idaw_params": {"eq.carve": True, "stereo.spread": "wide"}},
        "in your face": {"meaning": "Aggressive, forward", "idaw_params": {"space": "dry", "aggression": 0.8}},
        "lush": {"meaning": "Rich, layered texture", "idaw_params": {"layers": "many", "fx": ["reverb", "chorus"]}},
        "lo-fi": {"meaning": "Degraded, vintage quality", "idaw_params": {"character": "lo-fi", "degradation": 0.6}},
        "lofi": {"meaning": "Degraded, vintage quality", "idaw_params": {"character": "lo-fi", "degradation": 0.6}},
        "wet": {"meaning": "Heavy effects", "idaw_params": {"fx.mix": 0.6}},
        "dry": {"meaning": "No/minimal effects", "idaw_params": {"fx.mix": 0.1}},
        "buried": {"meaning": "Too quiet in mix", "idaw_params": {"production.rule_break": "BURIED_ELEMENT"}},
    },
}

MEME_PROGRESSIONS = {
    "mario cadence": {
        "progression": "bVI-bVII-I",
        "formal_name": "Double Plagal Cadence",
        "emotions": ["triumphant", "heroic", "epic"],
        "idaw_params": {"progression.type": "mario_cadence"},
    },
    "creep progression": {
        "progression": "I-III-IV-iv",
        "formal_name": "Modal Interchange with III and iv",
        "emotions": ["yearning", "bittersweet"],
        "idaw_params": {"rule_break": "HARMONY_ModalInterchange"},
    },
    "axis": {
        "progression": "I-V-vi-IV",
        "formal_name": "Axis Progression",
        "emotions": ["universal", "pop", "accessible"],
        "idaw_params": {"progression.type": "axis"},
    },
    "andalusian": {
        "progression": "i-bVII-bVI-V",
        "formal_name": "Phrygian Descent",
        "emotions": ["spanish", "dramatic"],
        "idaw_params": {"progression.type": "andalusian"},
    },
}

EMOTION_TO_RULE_BREAK = {
    "bittersweet": [RuleBreakCode.HARMONY_ModalInterchange],
    "nostalgia": [RuleBreakCode.HARMONY_ModalInterchange],
    "longing": [RuleBreakCode.STRUCTURE_NonResolution, RuleBreakCode.HARMONY_ModalInterchange],
    "grief": [RuleBreakCode.STRUCTURE_NonResolution, RuleBreakCode.PRODUCTION_BuriedVocals],
    "power": [RuleBreakCode.HARMONY_ParallelMotion],
    "defiance": [RuleBreakCode.HARMONY_ParallelMotion],
    "anxiety": [RuleBreakCode.RHYTHM_ConstantDisplacement, RuleBreakCode.RHYTHM_MeterAmbiguity],
    "chaos": [RuleBreakCode.HARMONY_Polytonality, RuleBreakCode.RHYTHM_MeterAmbiguity],
    "vulnerability": [RuleBreakCode.PRODUCTION_PitchImperfection, RuleBreakCode.RHYTHM_TempoFluctuation],
    "intimacy": [RuleBreakCode.RHYTHM_TempoFluctuation, RuleBreakCode.PRODUCTION_PitchImperfection],
    "dissociation": [RuleBreakCode.PRODUCTION_BuriedVocals],
    "unfinished": [RuleBreakCode.STRUCTURE_NonResolution],
    "tension": [RuleBreakCode.HARMONY_UnresolvedDissonance],
}


# =============================================================================
# TRANSLATOR CLASS
# =============================================================================

class VernacularTranslator:
    """
    Translates casual music descriptions to iDAW parameters.
    
    Philosophy: Musicians describe sound in vernacular, not technical terms.
    This class bridges that gap.
    """
    
    def __init__(self, custom_db: Optional[Dict] = None):
        """Initialize with optional custom database."""
        self.db = custom_db or VERNACULAR_DB
        self.meme_progressions = MEME_PROGRESSIONS
        self.emotion_rules = EMOTION_TO_RULE_BREAK
        
        # Build reverse lookup for fast matching
        self._build_lookup()
    
    def _build_lookup(self) -> None:
        """Build flat lookup dictionary for matching."""
        self._lookup: Dict[str, Tuple[VernacularCategory, Dict]] = {}
        
        for category_name, terms in self.db.items():
            category = VernacularCategory(category_name)
            for term, data in terms.items():
                self._lookup[term.lower()] = (category, data)
        
        # Add meme progressions
        for term, data in self.meme_progressions.items():
            self._lookup[term.lower()] = (VernacularCategory.MEME_THEORY, data)
    
    def translate(self, input_text: str) -> TranslationResult:
        """
        Translate vernacular description to iDAW parameters.
        
        Args:
            input_text: Natural language description like "fat laid back swung"
        
        Returns:
            TranslationResult with matched terms and combined parameters
        """
        input_lower = input_text.lower()
        matched: List[VernacularMatch] = []
        combined_params: Dict = {}
        matched_spans: Set[Tuple[int, int]] = set()
        
        # Try to match multi-word phrases first (longest match wins)
        for term, (category, data) in sorted(
            self._lookup.items(), 
            key=lambda x: -len(x[0])  # Sort by length descending
        ):
            if term in input_lower:
                # Check if this span overlaps with already matched
                start = input_lower.find(term)
                end = start + len(term)
                
                overlaps = any(
                    not (end <= s or start >= e) 
                    for s, e in matched_spans
                )
                
                if not overlaps:
                    matched_spans.add((start, end))
                    match = VernacularMatch(
                        term=term,
                        category=category,
                        meaning=data.get("meaning", ""),
                        idaw_params=data.get("idaw_params", {}),
                    )
                    matched.append(match)
                    
                    # Merge params
                    for key, value in match.idaw_params.items():
                        combined_params[key] = value
        
        # Find unmatched words
        words = input_lower.split()
        matched_words = set()
        for term in [m.term for m in matched]:
            matched_words.update(term.split())
        unmatched = [w for w in words if w not in matched_words]
        
        # Check for emotion keywords that suggest rule-breaking
        suggested_rules = []
        for word in words:
            if word in self.emotion_rules:
                for rule in self.emotion_rules[word]:
                    if rule.value not in suggested_rules:
                        suggested_rules.append(rule.value)
        
        return TranslationResult(
            original_input=input_text,
            matched_terms=matched,
            combined_params=combined_params,
            unmatched_words=unmatched,
            suggested_rule_breaks=suggested_rules,
        )
    
    def suggest_rule_break(self, emotion: str) -> List[RuleBreakCode]:
        """
        Suggest rule-breaking techniques for an emotion.
        
        Args:
            emotion: Primary emotion like "grief", "defiance", "longing"
        
        Returns:
            List of RuleBreakCode enums
        """
        return self.emotion_rules.get(emotion.lower(), [])
    
    def get_progression(self, meme_name: str) -> Optional[Dict]:
        """
        Get chord progression from meme name.
        
        Args:
            meme_name: Like "mario cadence" or "creep progression"
        
        Returns:
            Dict with progression details or None
        """
        return self.meme_progressions.get(meme_name.lower())
    
    def explain_term(self, term: str) -> Optional[str]:
        """
        Get explanation of a vernacular term.
        
        Args:
            term: Like "fat" or "laid back"
        
        Returns:
            Human-readable explanation or None
        """
        if term.lower() in self._lookup:
            category, data = self._lookup[term.lower()]
            meaning = data.get("meaning", "No definition available")
            params = data.get("idaw_params", {})
            return f"{term}: {meaning}\n  → Translates to: {params}"
        return None


# =============================================================================
# CLI INTEGRATION
# =============================================================================

def translate_command(input_text: str) -> None:
    """
    CLI command for vernacular translation.
    
    Usage: idaw translate "fat laid back swung"
    """
    translator = VernacularTranslator()
    result = translator.translate(input_text)
    
    print(f"\n🎵 Vernacular Translation")
    print(f"   Input: \"{result.original_input}\"")
    print()
    
    if result.matched_terms:
        print("📋 Matched Terms:")
        for match in result.matched_terms:
            print(f"   • {match.term} ({match.category.value})")
            print(f"     → {match.meaning}")
        print()
    
    if result.combined_params:
        print("⚙️  iDAW Parameters:")
        for key, value in result.combined_params.items():
            print(f"   {key}: {value}")
        print()
    
    if result.suggested_rule_breaks:
        print("🎸 Suggested Rule-Breaks:")
        for rule in result.suggested_rule_breaks:
            print(f"   • {rule}")
        print()
    
    if result.unmatched_words:
        print(f"❓ Unrecognized: {', '.join(result.unmatched_words)}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # Demo usage
    translator = VernacularTranslator()
    
    test_inputs = [
        "fat laid back swung",
        "crispy tight in the pocket",
        "dark muddy needs glue",
        "mario cadence triumphant",
        "lo-fi breathing warm vulnerability",
    ]
    
    for test in test_inputs:
        result = translator.translate(test)
        print(f"\n{'='*60}")
        print(f"Input: \"{test}\"")
        print(f"Params: {result.combined_params}")
        if result.suggested_rule_breaks:
            print(f"Suggested rule-breaks: {result.suggested_rule_breaks}")
        print(f"Unmatched: {result.unmatched_words}")
