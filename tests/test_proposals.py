"""
Tests for the proposals module.

Run with: pytest tests/test_proposals.py -v
"""

import pytest
from music_brain.session.proposals import (
    ProposalGenerator,
    Proposal,
    ProposalCategory,
    propose_for_emotion,
    quick_propose,
)


# =============================================================================
# ProposalGenerator Tests
# =============================================================================

@pytest.fixture
def generator():
    return ProposalGenerator()


def test_generator_initialization(generator):
    """Generator should initialize with proposal data."""
    assert generator is not None
    assert len(generator.all_proposals) > 0


def test_list_supported_emotions(generator):
    """Generator should list supported emotions."""
    emotions = generator.list_supported_emotions()
    assert len(emotions) > 0
    assert "grief" in emotions
    assert "rage" in emotions


# =============================================================================
# Emotion-based Proposal Tests
# =============================================================================

@pytest.mark.parametrize("emotion", ["grief", "rage", "nostalgia", "anxiety", "tenderness"])
def test_get_proposals_for_emotion(generator, emotion):
    """Should return proposals for known emotions."""
    proposals = generator.get_proposals_for_emotion(emotion)
    assert len(proposals) > 0
    for proposal in proposals:
        assert isinstance(proposal, Proposal)


def test_get_proposals_for_unknown_emotion(generator):
    """Unknown emotions should return empty list."""
    proposals = generator.get_proposals_for_emotion("foobar")
    assert proposals == []


def test_get_proposals_case_insensitive(generator):
    """Emotion matching should be case-insensitive."""
    proposals_lower = generator.get_proposals_for_emotion("grief")
    proposals_upper = generator.get_proposals_for_emotion("GRIEF")
    assert len(proposals_lower) == len(proposals_upper)


def test_get_proposals_with_category_filter(generator):
    """Should filter proposals by category."""
    proposals = generator.get_proposals_for_emotion(
        "grief",
        categories=[ProposalCategory.HARMONY]
    )
    for proposal in proposals:
        assert proposal.category == ProposalCategory.HARMONY


# =============================================================================
# Quick Proposal Tests
# =============================================================================

def test_quick_proposal_returns_single(generator):
    """Quick proposal should return a single proposal."""
    proposal = generator.get_quick_proposal("grief")
    assert proposal is None or isinstance(proposal, Proposal)


def test_quick_proposal_unknown_emotion(generator):
    """Unknown emotion should return None."""
    proposal = generator.get_quick_proposal("xyzzy")
    assert proposal is None


def test_quick_proposal_with_category(generator):
    """Quick proposal can be filtered by category."""
    proposal = generator.get_quick_proposal("grief", category=ProposalCategory.HARMONY)
    if proposal is not None:
        assert proposal.category == ProposalCategory.HARMONY


# =============================================================================
# Full Proposal Set Tests
# =============================================================================

def test_full_proposal_set(generator):
    """Full proposal set should be organized by category."""
    result = generator.get_full_proposal_set("grief")
    assert isinstance(result, dict)
    for category_name, proposals in result.items():
        assert isinstance(proposals, list)
        for proposal in proposals:
            assert proposal.category.value == category_name


# =============================================================================
# Proposal Object Tests
# =============================================================================

def test_proposal_structure():
    """Proposal should have all required fields."""
    proposal = Proposal(
        category=ProposalCategory.HARMONY,
        title="Test Title",
        description="Test description",
        emotional_justification="Test justification",
        implementation_hint="Test hint",
    )

    assert proposal.category == ProposalCategory.HARMONY
    assert proposal.title == "Test Title"
    assert proposal.description == "Test description"
    assert proposal.emotional_justification == "Test justification"
    assert proposal.implementation_hint == "Test hint"
    assert proposal.confidence == 0.7  # default
    assert proposal.alternatives == []  # default


def test_proposal_to_dict():
    """Proposal should serialize to dictionary."""
    proposal = Proposal(
        category=ProposalCategory.RHYTHM,
        title="Test",
        description="Desc",
        emotional_justification="Why",
        implementation_hint="How",
        confidence=0.8,
        alternatives=["Alt 1", "Alt 2"],
    )

    data = proposal.to_dict()

    assert data["category"] == "rhythm"
    assert data["title"] == "Test"
    assert data["confidence"] == 0.8
    assert len(data["alternatives"]) == 2


def test_proposal_from_dict():
    """Proposal should deserialize from dictionary."""
    data = {
        "category": "production",
        "title": "Test",
        "description": "Desc",
        "emotional_justification": "Why",
        "implementation_hint": "How",
        "confidence": 0.9,
        "alternatives": [],
    }

    proposal = Proposal.from_dict(data)

    assert proposal.category == ProposalCategory.PRODUCTION
    assert proposal.title == "Test"
    assert proposal.confidence == 0.9


def test_proposal_roundtrip():
    """to_dict and from_dict should roundtrip correctly."""
    original = Proposal(
        category=ProposalCategory.ARRANGEMENT,
        title="Roundtrip Test",
        description="Testing serialization",
        emotional_justification="For testing",
        implementation_hint="Run the test",
        confidence=0.85,
        alternatives=["Option A"],
    )

    data = original.to_dict()
    restored = Proposal.from_dict(data)

    assert restored.category == original.category
    assert restored.title == original.title
    assert restored.confidence == original.confidence
    assert restored.alternatives == original.alternatives


# =============================================================================
# CLI Function Tests
# =============================================================================

def test_propose_for_emotion_output():
    """CLI function should return formatted string."""
    output = propose_for_emotion("grief")
    assert "GRIEF" in output
    assert "HARMONY" in output or "RHYTHM" in output


def test_propose_for_emotion_unknown():
    """Unknown emotion should return helpful message."""
    output = propose_for_emotion("unknown_emotion")
    assert "No proposals" in output
    assert "Supported" in output


def test_quick_propose_output():
    """Quick propose should return formatted single proposal."""
    output = quick_propose("grief")
    assert "Proposal" in output or "No proposals" in output


# =============================================================================
# ProposalCategory Tests
# =============================================================================

def test_proposal_category_values():
    """All category values should be strings."""
    for category in ProposalCategory:
        assert isinstance(category.value, str)


def test_proposal_category_count():
    """Should have expected number of categories."""
    assert len(ProposalCategory) >= 4  # At least harmony, rhythm, production, arrangement
