"""
Proposals - Creative proposal generation for emotionally-driven music composition.

This module generates creative proposals (suggestions) for music based on:
- Emotional states and affects
- Rule-breaking opportunities
- Harmonic and rhythmic ideas
- Production techniques

Philosophy: "The tool shouldn't finish art for people. It should make them braver."
Proposals are meant to inspire and educate, not dictate.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

from music_brain.session.intent_schema import (
    RULE_BREAKING_EFFECTS,
    AFFECT_MODE_MAP,
    HarmonyRuleBreak,
    RhythmRuleBreak,
    ArrangementRuleBreak,
    ProductionRuleBreak,
    suggest_full_palette,
)


class ProposalCategory(Enum):
    """Categories of creative proposals."""
    HARMONY = "harmony"
    RHYTHM = "rhythm"
    ARRANGEMENT = "arrangement"
    PRODUCTION = "production"
    MELODY = "melody"
    TEXTURE = "texture"
    EMOTIONAL = "emotional"
    FULL_CONCEPT = "full_concept"


class ProposalConfidence(Enum):
    """Confidence level of a proposal."""
    EXPERIMENTAL = "experimental"  # Try at your own risk
    SUGGESTED = "suggested"        # Likely to work
    RECOMMENDED = "recommended"    # Strongly aligned with intent


@dataclass
class Proposal:
    """A single creative proposal/suggestion."""
    title: str
    category: ProposalCategory
    description: str
    technique: str
    emotional_effect: str
    implementation_hints: List[str] = field(default_factory=list)
    confidence: ProposalConfidence = ProposalConfidence.SUGGESTED
    rule_breaking: Optional[str] = None
    examples: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "title": self.title,
            "category": self.category.value,
            "description": self.description,
            "technique": self.technique,
            "emotional_effect": self.emotional_effect,
            "implementation_hints": self.implementation_hints,
            "confidence": self.confidence.value,
            "rule_breaking": self.rule_breaking,
            "examples": self.examples,
        }


@dataclass
class ProposalSet:
    """A collection of proposals for a creative session."""
    emotion: str
    proposals: List[Proposal] = field(default_factory=list)
    context_notes: List[str] = field(default_factory=list)
    suggested_starting_point: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "emotion": self.emotion,
            "proposals": [p.to_dict() for p in self.proposals],
            "context_notes": self.context_notes,
            "suggested_starting_point": self.suggested_starting_point,
        }

    def get_by_category(self, category: ProposalCategory) -> List[Proposal]:
        """Get proposals filtered by category."""
        return [p for p in self.proposals if p.category == category]

    def get_by_confidence(self, confidence: ProposalConfidence) -> List[Proposal]:
        """Get proposals filtered by confidence level."""
        return [p for p in self.proposals if p.confidence == confidence]


# =================================================================
# PROPOSAL GENERATORS BY CATEGORY
# =================================================================

def generate_harmony_proposals(emotion: str) -> List[Proposal]:
    """Generate harmony-related proposals for an emotion."""
    proposals = []

    # Get affect mapping for the emotion
    affect_data = AFFECT_MODE_MAP.get(emotion.lower(), {})
    modes = affect_data.get("modes", ["Aeolian"])

    # Modal suggestions
    for mode in modes:
        proposals.append(Proposal(
            title=f"Use {mode} Mode",
            category=ProposalCategory.HARMONY,
            description=f"Build your harmonic foundation in {mode} mode",
            technique="Modal composition",
            emotional_effect=_get_mode_emotional_effect(mode),
            implementation_hints=[
                f"Start with a {mode.lower()} scale",
                "Emphasize the characteristic interval",
                "Let the mode color drive chord choices",
            ],
            confidence=ProposalConfidence.RECOMMENDED,
        ))

    # Rule-breaking proposals based on emotion
    harmony_rules = [
        HarmonyRuleBreak.AVOID_TONIC_RESOLUTION,
        HarmonyRuleBreak.MODAL_INTERCHANGE,
        HarmonyRuleBreak.PARALLEL_MOTION,
        HarmonyRuleBreak.UNRESOLVED_DISSONANCE,
    ]

    for rule in harmony_rules:
        rule_data = RULE_BREAKING_EFFECTS.get(rule.value, {})
        example_emotions = rule_data.get("example_emotions", [])

        if emotion.lower() in example_emotions:
            proposals.append(Proposal(
                title=rule_data.get("description", rule.value),
                category=ProposalCategory.HARMONY,
                description=rule_data.get("use_when", ""),
                technique=rule.value,
                emotional_effect=rule_data.get("effect", ""),
                implementation_hints=[
                    f"This technique aligns with {emotion}",
                    "Requires emotional justification",
                ],
                confidence=ProposalConfidence.RECOMMENDED,
                rule_breaking=rule.value,
                examples=example_emotions,
            ))

    return proposals


def generate_rhythm_proposals(emotion: str) -> List[Proposal]:
    """Generate rhythm-related proposals for an emotion."""
    proposals = []

    affect_data = AFFECT_MODE_MAP.get(emotion.lower(), {})
    tempo_range = affect_data.get("tempo_range", (80, 120))

    # Tempo proposal
    proposals.append(Proposal(
        title=f"Tempo Range: {tempo_range[0]}-{tempo_range[1]} BPM",
        category=ProposalCategory.RHYTHM,
        description=f"This tempo range supports {emotion} effectively",
        technique="Tempo selection",
        emotional_effect=_get_tempo_emotional_effect(tempo_range),
        implementation_hints=[
            f"Start around {sum(tempo_range) // 2} BPM",
            "Allow for feel-based adjustments",
        ],
        confidence=ProposalConfidence.RECOMMENDED,
    ))

    # Rhythm rule-breaking proposals
    rhythm_rules = [
        RhythmRuleBreak.CONSTANT_DISPLACEMENT,
        RhythmRuleBreak.TEMPO_FLUCTUATION,
        RhythmRuleBreak.DROPPED_BEATS,
    ]

    for rule in rhythm_rules:
        rule_data = RULE_BREAKING_EFFECTS.get(rule.value, {})
        example_emotions = rule_data.get("example_emotions", [])

        if emotion.lower() in example_emotions or _emotion_matches_rhythm(emotion, rule):
            proposals.append(Proposal(
                title=rule_data.get("description", rule.value),
                category=ProposalCategory.RHYTHM,
                description=rule_data.get("use_when", ""),
                technique=rule.value,
                emotional_effect=rule_data.get("effect", ""),
                implementation_hints=[
                    "Apply gradually, don't overdo it",
                    "Listen for the emotional shift",
                ],
                confidence=ProposalConfidence.SUGGESTED,
                rule_breaking=rule.value,
            ))

    return proposals


def generate_production_proposals(emotion: str) -> List[Proposal]:
    """Generate production-related proposals for an emotion."""
    proposals = []

    # Get full palette for texture recommendations
    palette = suggest_full_palette(emotion)
    texture_options = palette.get("texture_options", [])

    for tex_opt in texture_options:
        texture_name = tex_opt.get("texture", "")
        production = tex_opt.get("production", {})

        hints = []
        if production.get("reverb"):
            hints.append(f"Reverb: {production['reverb']}")
        if production.get("stereo_width"):
            hints.append(f"Stereo: {production['stereo_width']}")
        if production.get("compression"):
            hints.append(f"Compression: {production['compression']}")

        proposals.append(Proposal(
            title=f"{texture_name} Texture",
            category=ProposalCategory.PRODUCTION,
            description=f"Create a {texture_name.lower()} sonic texture",
            technique="Texture design",
            emotional_effect=_get_texture_emotional_effect(texture_name),
            implementation_hints=hints,
            confidence=ProposalConfidence.SUGGESTED,
        ))

    # Production rule-breaking proposals
    production_rules = [
        ProductionRuleBreak.PITCH_IMPERFECTION,
        ProductionRuleBreak.ROOM_NOISE,
        ProductionRuleBreak.EXCESSIVE_MUD,
        ProductionRuleBreak.LO_FI_DEGRADATION,
    ]

    for rule in production_rules:
        rule_data = RULE_BREAKING_EFFECTS.get(rule.value, {})
        example_emotions = rule_data.get("example_emotions", [])

        if emotion.lower() in example_emotions:
            proposals.append(Proposal(
                title=rule_data.get("description", rule.value),
                category=ProposalCategory.PRODUCTION,
                description=rule_data.get("use_when", ""),
                technique=rule.value,
                emotional_effect=rule_data.get("effect", ""),
                implementation_hints=[
                    "This is intentional imperfection",
                    "Know why you're breaking this rule",
                ],
                confidence=ProposalConfidence.EXPERIMENTAL,
                rule_breaking=rule.value,
            ))

    return proposals


def generate_arrangement_proposals(emotion: str) -> List[Proposal]:
    """Generate arrangement-related proposals for an emotion."""
    proposals = []

    # Density recommendation
    affect_data = AFFECT_MODE_MAP.get(emotion.lower(), {})
    density = affect_data.get("density", "Moderate")

    proposals.append(Proposal(
        title=f"{density} Arrangement Density",
        category=ProposalCategory.ARRANGEMENT,
        description=f"A {density.lower()} density supports {emotion}",
        technique="Arrangement density",
        emotional_effect=_get_density_emotional_effect(density),
        implementation_hints=[
            f"Aim for {density.lower()} instrumentation",
            "Leave space for the emotion to breathe",
        ],
        confidence=ProposalConfidence.RECOMMENDED,
    ))

    # Arrangement rule-breaking
    arrangement_rules = [
        ArrangementRuleBreak.BURIED_VOCALS,
        ArrangementRuleBreak.EXTREME_DYNAMIC_RANGE,
        ArrangementRuleBreak.STRUCTURAL_MISMATCH,
    ]

    for rule in arrangement_rules:
        rule_data = RULE_BREAKING_EFFECTS.get(rule.value, {})
        example_emotions = rule_data.get("example_emotions", [])

        if emotion.lower() in example_emotions:
            proposals.append(Proposal(
                title=rule_data.get("description", rule.value),
                category=ProposalCategory.ARRANGEMENT,
                description=rule_data.get("use_when", ""),
                technique=rule.value,
                emotional_effect=rule_data.get("effect", ""),
                implementation_hints=[
                    "Structure serves emotion, not convention",
                ],
                confidence=ProposalConfidence.SUGGESTED,
                rule_breaking=rule.value,
            ))

    return proposals


# =================================================================
# MAIN PROPOSAL GENERATOR
# =================================================================

class ProposalGenerator:
    """
    Generates creative proposals for music composition based on emotional intent.

    Usage:
        generator = ProposalGenerator()
        proposals = generator.generate(emotion="grief")
        for p in proposals.proposals:
            print(f"{p.title}: {p.emotional_effect}")
    """

    def __init__(self):
        """Initialize the proposal generator."""
        self.generators = {
            ProposalCategory.HARMONY: generate_harmony_proposals,
            ProposalCategory.RHYTHM: generate_rhythm_proposals,
            ProposalCategory.PRODUCTION: generate_production_proposals,
            ProposalCategory.ARRANGEMENT: generate_arrangement_proposals,
        }

    def generate(
        self,
        emotion: str,
        categories: Optional[List[ProposalCategory]] = None,
        max_per_category: int = 5,
    ) -> ProposalSet:
        """
        Generate a set of proposals for the given emotion.

        Args:
            emotion: Target emotion (grief, anger, nostalgia, etc.)
            categories: Specific categories to generate (None = all)
            max_per_category: Maximum proposals per category

        Returns:
            ProposalSet with all generated proposals
        """
        proposals = []
        categories = categories or list(self.generators.keys())

        for category in categories:
            if category in self.generators:
                category_proposals = self.generators[category](emotion)
                # Limit per category
                proposals.extend(category_proposals[:max_per_category])

        # Build context notes
        context_notes = self._build_context_notes(emotion)

        # Determine starting point
        starting_point = self._suggest_starting_point(emotion, proposals)

        return ProposalSet(
            emotion=emotion,
            proposals=proposals,
            context_notes=context_notes,
            suggested_starting_point=starting_point,
        )

    def generate_quick(self, emotion: str, count: int = 3) -> List[Proposal]:
        """
        Generate a quick list of the most relevant proposals.

        Args:
            emotion: Target emotion
            count: Number of proposals to return

        Returns:
            List of top proposals
        """
        proposal_set = self.generate(emotion)
        # Prioritize recommended confidence
        recommended = proposal_set.get_by_confidence(ProposalConfidence.RECOMMENDED)
        if len(recommended) >= count:
            return recommended[:count]
        # Fill with suggested
        suggested = proposal_set.get_by_confidence(ProposalConfidence.SUGGESTED)
        return (recommended + suggested)[:count]

    def _build_context_notes(self, emotion: str) -> List[str]:
        """Build contextual notes for the emotion."""
        notes = []
        affect_data = AFFECT_MODE_MAP.get(emotion.lower(), {})

        if affect_data:
            modes = affect_data.get("modes", [])
            tempo_range = affect_data.get("tempo_range", (80, 120))
            density = affect_data.get("density", "Moderate")

            notes.append(f"For '{emotion}', consider modes: {', '.join(modes)}")
            notes.append(f"Effective tempo range: {tempo_range[0]}-{tempo_range[1]} BPM")
            notes.append(f"Arrangement density: {density}")
        else:
            notes.append(f"'{emotion}' is not a mapped affect - proposals are general")
            notes.append("Consider adding specific emotional mapping for better results")

        notes.append("Remember: Rules are broken INTENTIONALLY with emotional justification")

        return notes

    def _suggest_starting_point(
        self, emotion: str, proposals: List[Proposal]
    ) -> Optional[str]:
        """Suggest where to start based on emotion and proposals."""
        # Find the highest-confidence harmony proposal
        harmony_props = [p for p in proposals if p.category == ProposalCategory.HARMONY]
        recommended = [p for p in harmony_props if p.confidence == ProposalConfidence.RECOMMENDED]

        if recommended:
            return f"Start with: {recommended[0].title}"

        if harmony_props:
            return f"Consider starting with: {harmony_props[0].title}"

        return "Begin by clarifying your emotional intent (Phase 0)"


# =================================================================
# HELPER FUNCTIONS
# =================================================================

def _get_mode_emotional_effect(mode: str) -> str:
    """Get the emotional effect description for a mode."""
    mode_effects = {
        "Ionian": "Bright, happy, resolved - the sound of certainty",
        "Dorian": "Minor but hopeful, sophisticated - grief with grace",
        "Phrygian": "Dark, exotic, tense - unresolved darkness",
        "Lydian": "Dreamy, floating, ethereal - escape from gravity",
        "Mixolydian": "Bluesy, earthy, unresolved - comfortable imperfection",
        "Aeolian": "Natural minor, sad, serious - pure melancholy",
        "Locrian": "Unstable, tense, rare - existential unease",
    }
    return mode_effects.get(mode, "Complex emotional coloring")


def _get_tempo_emotional_effect(tempo_range: Tuple[int, int]) -> str:
    """Get the emotional effect of a tempo range."""
    mid = sum(tempo_range) // 2
    if mid < 70:
        return "Contemplative, heavy, meditative"
    elif mid < 90:
        return "Reflective, intimate, breathing space"
    elif mid < 110:
        return "Balanced energy, conversational pace"
    elif mid < 130:
        return "Energetic, forward motion, urgency"
    else:
        return "Intense, driving, overwhelming force"


def _get_texture_emotional_effect(texture: str) -> str:
    """Get the emotional effect of a texture type."""
    texture_effects = {
        "Ethereal": "Creates distance and dreamlike quality",
        "Intimate": "Personal, close, vulnerable",
        "Massive": "Overwhelming, powerful, cathartic",
        "Skeletal": "Exposed, fragile, nowhere to hide",
        "Lush": "Comforting, enveloping, warm",
        "Harsh": "Confrontational, aggressive, jarring",
        "Murky": "Confused, heavy, submerged",
        "Crystalline": "Clear, precise, sharp",
    }
    return texture_effects.get(texture, "Creates specific sonic character")


def _get_density_emotional_effect(density: str) -> str:
    """Get the emotional effect of arrangement density."""
    density_effects = {
        "Solo": "Complete vulnerability, nakedness",
        "Duo": "Intimate conversation, interplay",
        "Sparse": "Room to breathe, emphasis through absence",
        "Moderate": "Balanced presence, focused attention",
        "Full": "Complete expression, ensemble support",
        "Dense": "Overwhelming presence, wall of sound",
        "Overwhelming": "Intentional excess, loss of self",
    }
    return density_effects.get(density, "Shapes the emotional density")


def _emotion_matches_rhythm(emotion: str, rule: RhythmRuleBreak) -> bool:
    """
    Check if an emotion generally matches a rhythm rule.

    This mapping supplements the rule_breaking_effects by providing
    additional emotion-to-rhythm-rule associations based on the
    emotions defined in AFFECT_MODE_MAP.
    """
    # Map rhythm rules to emotions (using emotions from AFFECT_MODE_MAP)
    rhythm_emotion_map = {
        RhythmRuleBreak.CONSTANT_DISPLACEMENT: [
            "anxiety",
            "dissociation",
        ],
        RhythmRuleBreak.TEMPO_FLUCTUATION: [
            "tenderness",
            "longing",
            "nostalgia",
        ],
        RhythmRuleBreak.DROPPED_BEATS: [
            "grief",
            "catharsis",
            "surrender",
        ],
        RhythmRuleBreak.METRIC_MODULATION: [
            "dissociation",
        ],
        RhythmRuleBreak.POLYRHYTHMIC_LAYERS: [
            "anxiety",
            "rage",
        ],
    }
    emotions = rhythm_emotion_map.get(rule, [])
    return emotion.lower() in emotions


# =================================================================
# CONVENIENCE FUNCTIONS
# =================================================================

def generate_proposals(emotion: str, **kwargs) -> ProposalSet:
    """
    Convenience function to generate proposals for an emotion.

    Args:
        emotion: Target emotion
        **kwargs: Additional arguments for ProposalGenerator.generate()

    Returns:
        ProposalSet with proposals
    """
    generator = ProposalGenerator()
    return generator.generate(emotion, **kwargs)


def quick_proposals(emotion: str, count: int = 3) -> List[Proposal]:
    """
    Get a quick list of top proposals for an emotion.

    Args:
        emotion: Target emotion
        count: Number of proposals

    Returns:
        List of Proposal objects
    """
    generator = ProposalGenerator()
    return generator.generate_quick(emotion, count)


def list_supported_emotions() -> List[str]:
    """List all emotions with defined affect mappings."""
    return list(AFFECT_MODE_MAP.keys())
