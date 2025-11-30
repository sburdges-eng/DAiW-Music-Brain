"""
Proposal Generator Module
========================

Generates creative proposals for harmony, rhythm, production, and arrangement
based on emotional intent and musical context.

Part of the "Interrogate Before Generate" philosophy - suggestions are
emotionally-driven and come with justifications.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import random


class ProposalCategory(Enum):
    """Categories for musical proposals."""
    HARMONY = "harmony"
    RHYTHM = "rhythm"
    PRODUCTION = "production"
    ARRANGEMENT = "arrangement"
    MELODY = "melody"
    TEXTURE = "texture"


@dataclass
class Proposal:
    """A musical suggestion with emotional context."""
    category: ProposalCategory
    title: str
    description: str
    emotional_justification: str
    implementation_hint: str
    confidence: float = 0.7  # 0.0 to 1.0
    alternatives: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "category": self.category.value,
            "title": self.title,
            "description": self.description,
            "emotional_justification": self.emotional_justification,
            "implementation_hint": self.implementation_hint,
            "confidence": self.confidence,
            "alternatives": self.alternatives,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Proposal":
        """Deserialize from dictionary."""
        return cls(
            category=ProposalCategory(data["category"]),
            title=data["title"],
            description=data["description"],
            emotional_justification=data["emotional_justification"],
            implementation_hint=data["implementation_hint"],
            confidence=data.get("confidence", 0.7),
            alternatives=data.get("alternatives", []),
        )


class ProposalGenerator:
    """
    Generates creative proposals based on emotional intent.

    Philosophy: Every suggestion must have an emotional "why".
    """

    # Emotional -> Harmony mappings
    HARMONY_PROPOSALS = {
        "grief": [
            Proposal(
                category=ProposalCategory.HARMONY,
                title="Modal Interchange to Minor",
                description="Borrow chords from the parallel minor to add weight",
                emotional_justification="Minor borrowed chords carry the 'borrowed sadness' that mirrors unprocessed grief",
                implementation_hint="Try bVII or iv in a major context (e.g., Bb or Fm in C major)",
                alternatives=["Plagal cadence for resignation", "Deceptive cadence for unfulfilled longing"],
            ),
            Proposal(
                category=ProposalCategory.HARMONY,
                title="Avoid Tonic Resolution",
                description="End phrases on IV or vi instead of I",
                emotional_justification="Unresolved harmonic tension mirrors the unresolved nature of grief",
                implementation_hint="Substitute V-I with V-vi or IV-ii progressions",
            ),
        ],
        "rage": [
            Proposal(
                category=ProposalCategory.HARMONY,
                title="Tritone Substitutions",
                description="Replace V chords with bII for aggressive color",
                emotional_justification="The tritone's inherent tension mirrors rage's explosive quality",
                implementation_hint="In C, use Db7 instead of G7",
                alternatives=["Power chord only textures", "Chromatically descending bass"],
            ),
            Proposal(
                category=ProposalCategory.HARMONY,
                title="Parallel Minor Mode",
                description="Use Phrygian or Locrian mode fragments",
                emotional_justification="The flat 2 of Phrygian creates aggressive, confrontational color",
                implementation_hint="Emphasize the bII-i motion (Db-Cm in C Phrygian)",
            ),
        ],
        "nostalgia": [
            Proposal(
                category=ProposalCategory.HARMONY,
                title="Mixolydian Color",
                description="Use bVII chords for warm, nostalgic quality",
                emotional_justification="The flat 7th creates a 'looking back' quality without darkness",
                implementation_hint="Try I-bVII-IV progressions",
                alternatives=["Secondary dominants for yearning", "Add9 chords for wistful shimmer"],
            ),
        ],
        "anxiety": [
            Proposal(
                category=ProposalCategory.HARMONY,
                title="Diminished Passing Chords",
                description="Insert diminished chords between diatonic harmonies",
                emotional_justification="Diminished chords' instability mirrors anxiety's uncertainty",
                implementation_hint="Use #iv dim7 between IV and V, or vii dim7 for chromatic bass",
            ),
        ],
        "tenderness": [
            Proposal(
                category=ProposalCategory.HARMONY,
                title="Add9 and Maj7 Extensions",
                description="Use lush extended chords with open voicings",
                emotional_justification="Extended harmonies create space for emotional vulnerability",
                implementation_hint="Voice Cmaj9 as C-E-B-D in the upper register",
                alternatives=["Suspended chords that gently resolve", "Pedal tones for stability"],
            ),
        ],
    }

    # Emotional -> Rhythm mappings
    RHYTHM_PROPOSALS = {
        "grief": [
            Proposal(
                category=ProposalCategory.RHYTHM,
                title="Behind-the-Beat Feel",
                description="Push instruments 10-30ms late for laid-back feel",
                emotional_justification="The 'drag' in timing mirrors the weight of grief",
                implementation_hint="Apply -10 to -30ms humanization to snare and keys",
            ),
        ],
        "rage": [
            Proposal(
                category=ProposalCategory.RHYTHM,
                title="Ahead-of-Beat Urgency",
                description="Push hits 10-20ms early for aggressive feel",
                emotional_justification="Rushing creates urgency and impatience that mirrors anger",
                implementation_hint="Apply +10 to +20ms to kick and guitar attacks",
            ),
        ],
        "anxiety": [
            Proposal(
                category=ProposalCategory.RHYTHM,
                title="Metric Displacement",
                description="Shift accents off the beat periodically",
                emotional_justification="Displaced accents create the 'off-balance' feeling of anxiety",
                implementation_hint="Try 3+3+2 groupings over 4/4 time",
            ),
        ],
        "nostalgia": [
            Proposal(
                category=ProposalCategory.RHYTHM,
                title="Gentle Swing Feel",
                description="Apply light swing (55-58%) for warmth",
                emotional_justification="Swing evokes vintage recordings and simpler times",
                implementation_hint="Set swing to 56% on hi-hats and keys",
            ),
        ],
    }

    # Emotional -> Production mappings
    PRODUCTION_PROPOSALS = {
        "grief": [
            Proposal(
                category=ProposalCategory.PRODUCTION,
                title="Lo-Fi Warmth",
                description="Add subtle saturation and tape-style degradation",
                emotional_justification="Imperfection signals authenticity and vulnerability",
                implementation_hint="Use tape emulation with -3dB high shelf and light flutter",
            ),
        ],
        "rage": [
            Proposal(
                category=ProposalCategory.PRODUCTION,
                title="Aggressive Distortion",
                description="Use parallel distortion on melodic elements",
                emotional_justification="Clipping and distortion mirror the 'breaking point' of anger",
                implementation_hint="Blend 20-30% distorted signal with clean for aggression without mud",
            ),
        ],
        "dissociation": [
            Proposal(
                category=ProposalCategory.PRODUCTION,
                title="Buried Vocals",
                description="Push vocals behind the instrumental mix",
                emotional_justification="Distance in the mix mirrors emotional distance/detachment",
                implementation_hint="Lower vocal by 3-6dB and add heavy reverb",
            ),
        ],
    }

    # Emotional -> Arrangement mappings
    ARRANGEMENT_PROPOSALS = {
        "grief": [
            Proposal(
                category=ProposalCategory.ARRANGEMENT,
                title="Sparse Instrumentation",
                description="Strip arrangement to essential elements only",
                emotional_justification="Empty space gives room for the listener's emotions",
                implementation_hint="Remove all but piano/guitar, bass, and minimal percussion",
            ),
        ],
        "rage": [
            Proposal(
                category=ProposalCategory.ARRANGEMENT,
                title="Wall of Sound",
                description="Layer multiple distorted elements",
                emotional_justification="Overwhelming texture matches overwhelming emotion",
                implementation_hint="Stack 3+ guitar/synth layers with different EQ profiles",
            ),
        ],
        "anxiety": [
            Proposal(
                category=ProposalCategory.ARRANGEMENT,
                title="Gradual Build",
                description="Slowly add elements to increase tension",
                emotional_justification="The build mirrors escalating anxiety",
                implementation_hint="Add one new element every 8 bars, each slightly louder",
            ),
        ],
    }

    def __init__(self):
        self.all_proposals = {
            "harmony": self.HARMONY_PROPOSALS,
            "rhythm": self.RHYTHM_PROPOSALS,
            "production": self.PRODUCTION_PROPOSALS,
            "arrangement": self.ARRANGEMENT_PROPOSALS,
        }

    def get_proposals_for_emotion(
        self,
        emotion: str,
        categories: Optional[List[ProposalCategory]] = None,
    ) -> List[Proposal]:
        """
        Get all proposals matching an emotion.

        Args:
            emotion: Primary emotion (e.g., "grief", "rage")
            categories: Optional list of categories to filter by

        Returns:
            List of relevant Proposals
        """
        emotion = emotion.lower()
        results: List[Proposal] = []

        for category_name, emotion_map in self.all_proposals.items():
            if categories:
                # Check if this category is in the filter
                cat_enum = ProposalCategory(category_name)
                if cat_enum not in categories:
                    continue

            if emotion in emotion_map:
                results.extend(emotion_map[emotion])

        return results

    def get_quick_proposal(
        self,
        emotion: str,
        category: Optional[ProposalCategory] = None,
    ) -> Optional[Proposal]:
        """
        Get a single random proposal for quick inspiration.

        Args:
            emotion: Primary emotion
            category: Optional specific category

        Returns:
            A single Proposal or None
        """
        proposals = self.get_proposals_for_emotion(
            emotion,
            categories=[category] if category else None,
        )

        if not proposals:
            return None

        return random.choice(proposals)

    def get_full_proposal_set(self, emotion: str) -> Dict[str, List[Proposal]]:
        """
        Get proposals organized by category.

        Args:
            emotion: Primary emotion

        Returns:
            Dict mapping category names to lists of proposals
        """
        result: Dict[str, List[Proposal]] = {}

        for category in ProposalCategory:
            proposals = self.get_proposals_for_emotion(
                emotion,
                categories=[category],
            )
            if proposals:
                result[category.value] = proposals

        return result

    def list_supported_emotions(self) -> List[str]:
        """Return list of emotions with proposal support."""
        emotions = set()
        for emotion_map in self.all_proposals.values():
            emotions.update(emotion_map.keys())
        return sorted(emotions)


# =============================================================================
# CLI Integration Functions
# =============================================================================


def propose_for_emotion(emotion: str) -> str:
    """CLI-friendly proposal output for an emotion."""
    generator = ProposalGenerator()
    proposals = generator.get_proposals_for_emotion(emotion)

    if not proposals:
        supported = generator.list_supported_emotions()
        return f"No proposals for '{emotion}'. Supported: {', '.join(supported)}"

    lines = [
        f"\n=== Proposals for '{emotion.upper()}' ===\n",
    ]

    for p in proposals:
        lines.extend([
            f"[{p.category.value.upper()}] {p.title}",
            f"  Description: {p.description}",
            f"  Why: {p.emotional_justification}",
            f"  How: {p.implementation_hint}",
            "",
        ])

    return "\n".join(lines)


def quick_propose(emotion: str) -> str:
    """Get a single quick proposal for the CLI."""
    generator = ProposalGenerator()
    proposal = generator.get_quick_proposal(emotion)

    if not proposal:
        return f"No proposals for '{emotion}'."

    return (
        f"\n💡 Quick Proposal: {proposal.title}\n"
        f"Category: {proposal.category.value}\n"
        f"Description: {proposal.description}\n"
        f"Why: {proposal.emotional_justification}\n"
        f"How: {proposal.implementation_hint}\n"
    )
