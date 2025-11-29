"""
Tests for MCP proposal auto-approval and user voting system.

These tests verify:
1. MCP Coordinator proposals are auto-approved
2. User (sburdges-eng) has ultimate voting power
3. User specialties affect voting weights
4. Vote serialization includes weights
"""

import pytest
from mcp_workstation import (
    AIAgent,
    ProposalManager,
    ProposalCategory,
    ProposalStatus,
    UserVotingConfig,
    UserSpecialty,
)


class TestMCPCoordinatorAutoApproval:
    """Test MCP Coordinator proposal auto-approval."""

    def test_mcp_coordinator_proposal_auto_approved(self):
        """MCP Coordinator proposals should be auto-approved by default."""
        user_config = UserVotingConfig(auto_approve_mcp=True)
        pm = ProposalManager(user_config=user_config)

        proposal = pm.submit_proposal(
            agent=AIAgent.MCP_COORDINATOR,
            title="Test MCP Proposal",
            description="This should be auto-approved",
            category=ProposalCategory.ARCHITECTURE,
        )

        assert proposal is not None
        assert proposal.status == ProposalStatus.APPROVED

    def test_mcp_coordinator_auto_approval_disabled(self):
        """When auto_approve_mcp is False, proposals should be submitted."""
        user_config = UserVotingConfig(auto_approve_mcp=False)
        pm = ProposalManager(user_config=user_config)

        proposal = pm.submit_proposal(
            agent=AIAgent.MCP_COORDINATOR,
            title="Test MCP Proposal",
            description="This should NOT be auto-approved",
            category=ProposalCategory.ARCHITECTURE,
        )

        assert proposal is not None
        assert proposal.status == ProposalStatus.SUBMITTED

    def test_mcp_coordinator_no_proposal_limit(self):
        """MCP Coordinator should have no proposal limit."""
        pm = ProposalManager()

        # Submit more than MAX_PROPOSALS_PER_AGENT (3) proposals
        for i in range(5):
            proposal = pm.submit_proposal(
                agent=AIAgent.MCP_COORDINATOR,
                title=f"MCP Proposal {i+1}",
                description="Testing no limit",
                category=ProposalCategory.TOOL_INTEGRATION,
            )
            assert proposal is not None


class TestUserUltimateVoting:
    """Test user ultimate voting powers."""

    def test_user_ultimate_approve(self):
        """User should be able to approve any proposal immediately."""
        pm = ProposalManager()

        proposal = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Test Proposal",
            description="To be approved by user",
            category=ProposalCategory.FEATURE_NEW,
        )

        result = pm.vote_on_proposal(
            agent=AIAgent.USER,
            proposal_id=proposal.id,
            vote=1,
            comment="User approves",
        )

        assert result is True
        assert proposal.status == ProposalStatus.APPROVED

    def test_user_ultimate_veto(self):
        """User should be able to veto any proposal immediately."""
        pm = ProposalManager()

        proposal = pm.submit_proposal(
            agent=AIAgent.CHATGPT,
            title="Test Proposal",
            description="To be vetoed by user",
            category=ProposalCategory.PERFORMANCE,
        )

        result = pm.vote_on_proposal(
            agent=AIAgent.USER,
            proposal_id=proposal.id,
            vote=-1,
            comment="User vetoes",
        )

        assert result is True
        assert proposal.status == ProposalStatus.REJECTED

    def test_user_neutral_vote(self):
        """User neutral vote should not immediately decide."""
        pm = ProposalManager()

        proposal = pm.submit_proposal(
            agent=AIAgent.GEMINI,
            title="Test Proposal",
            description="User neutral vote",
            category=ProposalCategory.TESTING,
        )

        result = pm.vote_on_proposal(
            agent=AIAgent.USER,
            proposal_id=proposal.id,
            vote=0,
            comment="User neutral",
        )

        assert result is True
        # Neutral vote doesn't immediately decide
        assert proposal.status in (ProposalStatus.SUBMITTED, ProposalStatus.UNDER_REVIEW)

    def test_user_no_proposal_limit(self):
        """User should have no proposal limit."""
        pm = ProposalManager()

        # Submit more than MAX_PROPOSALS_PER_AGENT (3) proposals
        for i in range(5):
            proposal = pm.submit_proposal(
                agent=AIAgent.USER,
                title=f"User Proposal {i+1}",
                description="Testing no limit",
                category=ProposalCategory.FEATURE_ENHANCEMENT,
            )
            assert proposal is not None


class TestUserSpecialties:
    """Test user specialties and weighted voting."""

    def test_user_voting_weight(self):
        """User votes should have configurable weight."""
        user_config = UserVotingConfig(vote_weight=3.0)
        pm = ProposalManager(user_config=user_config)

        proposal = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Test Proposal",
            description="Test weighted vote",
            category=ProposalCategory.ARCHITECTURE,
        )

        pm.vote_on_proposal(
            agent=AIAgent.USER,
            proposal_id=proposal.id,
            vote=1,
        )

        # Check that the vote was recorded with the correct weight
        vote = [v for v in pm.votes if v.proposal_id == proposal.id][0]
        assert vote.weight == 3.0

    def test_user_specialty_weight(self):
        """User specialty should affect vote weight for matching categories."""
        specialty = UserSpecialty(
            name="Music Expert",
            categories=[ProposalCategory.DSP_ALGORITHM, ProposalCategory.AUDIO_PROCESSING],
            weight=1.5,
        )
        user_config = UserVotingConfig(
            vote_weight=2.0,
            specialties=[specialty],
        )
        pm = ProposalManager(user_config=user_config)

        # Submit proposal in specialty category
        proposal = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="DSP Proposal",
            description="In user specialty area",
            category=ProposalCategory.DSP_ALGORITHM,
        )

        pm.vote_on_proposal(
            agent=AIAgent.USER,
            proposal_id=proposal.id,
            vote=1,
        )

        # Weight should be vote_weight * specialty.weight = 2.0 * 1.5 = 3.0
        vote = [v for v in pm.votes if v.proposal_id == proposal.id][0]
        assert vote.weight == 3.0


class TestAIAgentProperties:
    """Test AIAgent enum properties."""

    def test_mcp_coordinator_is_mcp_coordinator(self):
        """MCP_COORDINATOR should return True for is_mcp_coordinator."""
        assert AIAgent.MCP_COORDINATOR.is_mcp_coordinator is True
        assert AIAgent.CLAUDE.is_mcp_coordinator is False
        assert AIAgent.USER.is_mcp_coordinator is False

    def test_user_is_user(self):
        """USER should return True for is_user."""
        assert AIAgent.USER.is_user is True
        assert AIAgent.CLAUDE.is_user is False
        assert AIAgent.MCP_COORDINATOR.is_user is False

    def test_display_names(self):
        """All agents should have display names."""
        assert AIAgent.MCP_COORDINATOR.display_name == "MCP Coordinator"
        assert AIAgent.USER.display_name == "User (sburdges-eng)"
        assert AIAgent.CLAUDE.display_name == "Claude (Anthropic)"


class TestUserVotingConfig:
    """Test UserVotingConfig model."""

    def test_default_config(self):
        """Default config should have expected values."""
        config = UserVotingConfig()
        assert config.username == "sburdges-eng"
        assert config.ultimate_veto is True
        assert config.ultimate_approve is True
        assert config.auto_approve_mcp is True
        assert config.vote_weight == 2.0

    def test_serialization(self):
        """Config should serialize and deserialize correctly."""
        specialty = UserSpecialty(
            name="Test",
            categories=[ProposalCategory.ARCHITECTURE],
            weight=1.5,
        )
        config = UserVotingConfig(
            username="test_user",
            specialties=[specialty],
            vote_weight=3.0,
        )

        data = config.to_dict()
        restored = UserVotingConfig.from_dict(data)

        assert restored.username == "test_user"
        assert restored.vote_weight == 3.0
        assert len(restored.specialties) == 1
        assert restored.specialties[0].name == "Test"


class TestProposalManagerSerialization:
    """Test ProposalManager serialization with new features."""

    def test_serialization_includes_user_config(self):
        """Serialized state should include user config."""
        user_config = UserVotingConfig(vote_weight=5.0)
        pm = ProposalManager(user_config=user_config)

        data = pm.to_dict()
        assert "user_config" in data
        assert data["user_config"]["vote_weight"] == 5.0

    def test_serialization_includes_vote_weights(self):
        """Serialized votes should include weights."""
        pm = ProposalManager()
        proposal = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Test",
            description="Test",
            category=ProposalCategory.FEATURE_NEW,
        )

        pm.vote_on_proposal(
            agent=AIAgent.USER,
            proposal_id=proposal.id,
            vote=1,
        )

        data = pm.to_dict()
        assert data["votes"][0]["weight"] == 2.0  # Default user vote weight

    def test_deserialization_restores_user_config(self):
        """Deserialized state should restore user config."""
        user_config = UserVotingConfig(vote_weight=4.0)
        pm = ProposalManager(user_config=user_config)
        proposal = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Test",
            description="Test",
            category=ProposalCategory.FEATURE_NEW,
        )

        pm.vote_on_proposal(
            agent=AIAgent.USER,
            proposal_id=proposal.id,
            vote=1,
        )

        data = pm.to_dict()
        restored_pm = ProposalManager.from_dict(data)

        assert restored_pm.user_config.vote_weight == 4.0
        assert len(restored_pm.votes) == 1
        assert restored_pm.votes[0].weight == 4.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
