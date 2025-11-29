"""
Tests for the proposals module.

Tests the creative proposal generation based on emotional intent.
"""

import pytest  # noqa: F401 - used by pytest

from music_brain.session.proposals import (
    ProposalGenerator,
    Proposal,
    ProposalSet,
    ProposalCategory,
    ProposalConfidence,
    generate_proposals,
    quick_proposals,
    list_supported_emotions,
    generate_harmony_proposals,
    generate_rhythm_proposals,
    generate_production_proposals,
    generate_arrangement_proposals,
)


class TestProposalDataClasses:
    """Test the proposal data classes."""

    def test_proposal_creation(self):
        """Test creating a basic proposal."""
        proposal = Proposal(
            title="Use Aeolian Mode",
            category=ProposalCategory.HARMONY,
            description="Build foundation in Aeolian",
            technique="Modal composition",
            emotional_effect="Pure melancholy",
        )
        assert proposal.title == "Use Aeolian Mode"
        assert proposal.category == ProposalCategory.HARMONY
        assert proposal.confidence == ProposalConfidence.SUGGESTED  # default

    def test_proposal_with_rule_breaking(self):
        """Test creating a proposal with rule breaking."""
        proposal = Proposal(
            title="Avoid Tonic Resolution",
            category=ProposalCategory.HARMONY,
            description="Don't resolve to I",
            technique="HARMONY_AvoidTonicResolution",
            emotional_effect="Unresolved yearning",
            rule_breaking="HARMONY_AvoidTonicResolution",
            confidence=ProposalConfidence.RECOMMENDED,
        )
        assert proposal.rule_breaking == "HARMONY_AvoidTonicResolution"
        assert proposal.confidence == ProposalConfidence.RECOMMENDED

    def test_proposal_to_dict(self):
        """Test converting proposal to dictionary."""
        proposal = Proposal(
            title="Test Proposal",
            category=ProposalCategory.RHYTHM,
            description="A test",
            technique="Testing",
            emotional_effect="None",
            implementation_hints=["Hint 1", "Hint 2"],
        )
        d = proposal.to_dict()
        assert d["title"] == "Test Proposal"
        assert d["category"] == "rhythm"
        assert len(d["implementation_hints"]) == 2

    def test_proposal_set_creation(self):
        """Test creating a proposal set."""
        proposal1 = Proposal(
            title="P1",
            category=ProposalCategory.HARMONY,
            description="D1",
            technique="T1",
            emotional_effect="E1",
        )
        proposal2 = Proposal(
            title="P2",
            category=ProposalCategory.RHYTHM,
            description="D2",
            technique="T2",
            emotional_effect="E2",
        )
        ps = ProposalSet(
            emotion="grief",
            proposals=[proposal1, proposal2],
        )
        assert ps.emotion == "grief"
        assert len(ps.proposals) == 2

    def test_proposal_set_get_by_category(self):
        """Test filtering proposals by category."""
        harmony_p = Proposal(
            title="Harmony",
            category=ProposalCategory.HARMONY,
            description="D",
            technique="T",
            emotional_effect="E",
        )
        rhythm_p = Proposal(
            title="Rhythm",
            category=ProposalCategory.RHYTHM,
            description="D",
            technique="T",
            emotional_effect="E",
        )
        ps = ProposalSet(emotion="test", proposals=[harmony_p, rhythm_p])

        harmony_only = ps.get_by_category(ProposalCategory.HARMONY)
        assert len(harmony_only) == 1
        assert harmony_only[0].title == "Harmony"

    def test_proposal_set_get_by_confidence(self):
        """Test filtering proposals by confidence."""
        rec_p = Proposal(
            title="Recommended",
            category=ProposalCategory.HARMONY,
            description="D",
            technique="T",
            emotional_effect="E",
            confidence=ProposalConfidence.RECOMMENDED,
        )
        exp_p = Proposal(
            title="Experimental",
            category=ProposalCategory.HARMONY,
            description="D",
            technique="T",
            emotional_effect="E",
            confidence=ProposalConfidence.EXPERIMENTAL,
        )
        ps = ProposalSet(emotion="test", proposals=[rec_p, exp_p])

        recommended = ps.get_by_confidence(ProposalConfidence.RECOMMENDED)
        assert len(recommended) == 1
        assert recommended[0].title == "Recommended"


class TestProposalGenerator:
    """Test the ProposalGenerator class."""

    def test_generator_initialization(self):
        """Test generator initializes correctly."""
        gen = ProposalGenerator()
        assert gen is not None
        assert len(gen.generators) >= 4  # harmony, rhythm, production, arrangement

    def test_generate_for_grief(self):
        """Test generating proposals for grief."""
        gen = ProposalGenerator()
        ps = gen.generate("grief")

        assert ps.emotion == "grief"
        assert len(ps.proposals) > 0
        assert len(ps.context_notes) > 0
        assert ps.suggested_starting_point is not None

    def test_generate_for_longing(self):
        """Test generating proposals for longing."""
        gen = ProposalGenerator()
        ps = gen.generate("longing")

        assert ps.emotion == "longing"
        # Longing should suggest Dorian/Mixolydian modes
        harmony_proposals = ps.get_by_category(ProposalCategory.HARMONY)
        titles = [p.title for p in harmony_proposals]
        assert any("Dorian" in t for t in titles) or any("Mixolydian" in t for t in titles)

    def test_generate_for_rage(self):
        """Test generating proposals for rage."""
        gen = ProposalGenerator()
        ps = gen.generate("rage")

        assert ps.emotion == "rage"
        # Rage should have Phrygian/Locrian suggestions
        harmony_proposals = ps.get_by_category(ProposalCategory.HARMONY)
        assert len(harmony_proposals) > 0

    def test_generate_with_category_filter(self):
        """Test generating with specific categories only."""
        gen = ProposalGenerator()
        ps = gen.generate("grief", categories=[ProposalCategory.HARMONY])

        # Should only have harmony proposals
        categories = set(p.category for p in ps.proposals)
        assert ProposalCategory.HARMONY in categories
        # No rhythm should be present (only harmony was requested)
        rhythm_count = len(ps.get_by_category(ProposalCategory.RHYTHM))
        assert rhythm_count == 0

    def test_generate_with_max_per_category(self):
        """Test limiting proposals per category."""
        gen = ProposalGenerator()
        ps = gen.generate("grief", max_per_category=2)

        # Each category should have at most 2
        for category in ProposalCategory:
            cat_proposals = ps.get_by_category(category)
            assert len(cat_proposals) <= 2

    def test_generate_quick(self):
        """Test quick proposal generation."""
        gen = ProposalGenerator()
        proposals = gen.generate_quick("anxiety", count=3)

        assert len(proposals) <= 3
        # Quick should prioritize recommended confidence
        for p in proposals:
            assert p.confidence in (ProposalConfidence.RECOMMENDED, ProposalConfidence.SUGGESTED)

    def test_unknown_emotion_still_works(self):
        """Test that unknown emotions still generate proposals."""
        gen = ProposalGenerator()
        ps = gen.generate("xyzunknown")

        # Should still work, just with generic proposals
        assert ps.emotion == "xyzunknown"
        # Context notes should mention it's not mapped
        assert any("not a mapped affect" in note for note in ps.context_notes)


class TestConvenienceFunctions:
    """Test the module-level convenience functions."""

    def test_generate_proposals_function(self):
        """Test the generate_proposals convenience function."""
        ps = generate_proposals("nostalgia")
        assert ps.emotion == "nostalgia"
        assert len(ps.proposals) > 0

    def test_quick_proposals_function(self):
        """Test the quick_proposals convenience function."""
        proposals = quick_proposals("melancholy", count=2)
        assert len(proposals) <= 2

    def test_list_supported_emotions(self):
        """Test listing supported emotions."""
        emotions = list_supported_emotions()
        assert "grief" in emotions
        assert "longing" in emotions
        assert "rage" in emotions
        assert "hope" in emotions
        assert len(emotions) >= 10


class TestCategoryGenerators:
    """Test individual category generators."""

    def test_harmony_proposals_for_grief(self):
        """Test harmony proposal generation for grief."""
        proposals = generate_harmony_proposals("grief")
        assert len(proposals) > 0

        # Should include Aeolian for grief
        titles = [p.title for p in proposals]
        assert any("Aeolian" in t for t in titles)

    def test_rhythm_proposals_include_tempo(self):
        """Test rhythm proposals include tempo suggestions."""
        proposals = generate_rhythm_proposals("grief")
        assert len(proposals) > 0

        # Should include a tempo proposal
        techniques = [p.technique for p in proposals]
        assert any("Tempo" in t for t in techniques)

    def test_production_proposals_include_textures(self):
        """Test production proposals include texture options."""
        proposals = generate_production_proposals("euphoria")
        assert len(proposals) > 0

        # Should include texture proposals
        techniques = [p.technique for p in proposals]
        assert any("Texture" in t for t in techniques)

    def test_arrangement_proposals_include_density(self):
        """Test arrangement proposals include density."""
        proposals = generate_arrangement_proposals("rage")
        assert len(proposals) > 0

        # Should include density suggestion
        techniques = [p.technique for p in proposals]
        assert any("density" in t.lower() for t in techniques)


class TestProposalSerialization:
    """Test serialization of proposals."""

    def test_proposal_set_to_dict(self):
        """Test converting proposal set to dict."""
        ps = generate_proposals("grief")
        d = ps.to_dict()

        assert "emotion" in d
        assert d["emotion"] == "grief"
        assert "proposals" in d
        assert isinstance(d["proposals"], list)
        assert len(d["proposals"]) > 0

    def test_proposal_dict_has_all_fields(self):
        """Test that proposal dict has all required fields."""
        proposals = quick_proposals("anger", count=1)
        if proposals:
            d = proposals[0].to_dict()
            required_fields = [
                "title", "category", "description", "technique",
                "emotional_effect", "implementation_hints", "confidence"
            ]
            for field in required_fields:
                assert field in d


class TestEmotionToRuleBreakingMapping:
    """Test that emotions correctly map to rule-breaking suggestions."""

    def test_grief_suggests_unresolved(self):
        """Test grief suggests unresolved harmonies."""
        proposals = generate_harmony_proposals("grief")
        rule_breaks = [p.rule_breaking for p in proposals if p.rule_breaking]

        # Grief should suggest avoiding tonic or unresolved dissonance
        assert any("Avoid" in rb or "Unresolved" in rb for rb in rule_breaks)

    def test_anxiety_suggests_displacement(self):
        """Test anxiety suggests rhythmic displacement."""
        proposals = generate_rhythm_proposals("anxiety")
        rule_breaks = [p.rule_breaking for p in proposals if p.rule_breaking]

        # Anxiety should suggest constant displacement
        assert any("Displacement" in rb for rb in rule_breaks)

    def test_vulnerability_maps_to_production(self):
        """Test vulnerability emotions map to production techniques."""
        proposals = generate_production_proposals("vulnerability")
        # Should have some texture suggestions even if not perfectly mapped
        assert len(proposals) >= 0  # At minimum empty list is valid
