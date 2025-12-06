"""
Tests for MCP proposal auto-approval and user voting system.

These tests verify:
1. MCP Coordinator proposals are auto-approved
2. User (sburdges-eng) has ultimate voting power
3. User specialties affect voting weights
4. Vote serialization includes weights
5. Proposal dependencies
6. Notification hooks
"""

import pytest
from mcp_workstation import (
    AIAgent,
    ProposalManager,
    ProposalCategory,
    ProposalStatus,
    UserVotingConfig,
    UserSpecialty,
    ProposalEvent,
    ProposalEventType,
    NotificationHook,
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


class TestProposalDependencies:
    """Test proposal dependency system."""

    def test_submit_proposal_with_dependencies(self):
        """Proposals can be submitted with dependencies."""
        pm = ProposalManager()

        # Create first proposal (no dependencies)
        proposal1 = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Base Feature",
            description="This is the base",
            category=ProposalCategory.ARCHITECTURE,
        )

        # Create second proposal that depends on first
        proposal2 = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Dependent Feature",
            description="Depends on base",
            category=ProposalCategory.FEATURE_NEW,
            dependencies=[proposal1.id],
        )

        assert proposal2 is not None
        assert proposal1.id in proposal2.dependencies

    def test_invalid_dependency_rejected(self):
        """Proposals with invalid dependencies are rejected."""
        pm = ProposalManager()

        proposal = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Bad Dependency",
            description="Has invalid dep",
            category=ProposalCategory.FEATURE_NEW,
            dependencies=["nonexistent_id"],
        )

        assert proposal is None

    def test_dependencies_not_met(self):
        """are_dependencies_met returns False when deps not approved."""
        pm = ProposalManager()

        proposal1 = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Base",
            description="Base",
            category=ProposalCategory.ARCHITECTURE,
        )

        proposal2 = pm.submit_proposal(
            agent=AIAgent.CHATGPT,
            title="Dependent",
            description="Depends on base",
            category=ProposalCategory.FEATURE_NEW,
            dependencies=[proposal1.id],
        )

        # Base is not approved yet
        assert pm.are_dependencies_met(proposal2.id) is False

    def test_dependencies_met_after_approval(self):
        """are_dependencies_met returns True after deps approved."""
        pm = ProposalManager()

        proposal1 = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Base",
            description="Base",
            category=ProposalCategory.ARCHITECTURE,
        )

        proposal2 = pm.submit_proposal(
            agent=AIAgent.CHATGPT,
            title="Dependent",
            description="Depends on base",
            category=ProposalCategory.FEATURE_NEW,
            dependencies=[proposal1.id],
        )

        # Approve base proposal via user
        pm.vote_on_proposal(agent=AIAgent.USER, proposal_id=proposal1.id, vote=1)

        assert pm.are_dependencies_met(proposal2.id) is True

    def test_get_ready_proposals(self):
        """get_ready_proposals only returns approved proposals with met deps."""
        pm = ProposalManager()

        # Create base and dependent proposals
        base = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Base",
            description="Base",
            category=ProposalCategory.ARCHITECTURE,
        )

        dependent = pm.submit_proposal(
            agent=AIAgent.CHATGPT,
            title="Dependent",
            description="Depends on base",
            category=ProposalCategory.FEATURE_NEW,
            dependencies=[base.id],
        )

        # Approve both
        pm.vote_on_proposal(agent=AIAgent.USER, proposal_id=base.id, vote=1)
        pm.vote_on_proposal(agent=AIAgent.USER, proposal_id=dependent.id, vote=1)

        ready = pm.get_ready_proposals()
        assert base in ready
        assert dependent in ready  # Both deps met

    def test_add_dependency(self):
        """Dependencies can be added after creation."""
        pm = ProposalManager()

        proposal1 = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="First",
            description="First",
            category=ProposalCategory.ARCHITECTURE,
        )

        proposal2 = pm.submit_proposal(
            agent=AIAgent.CHATGPT,
            title="Second",
            description="Second",
            category=ProposalCategory.FEATURE_NEW,
        )

        assert proposal1.id not in proposal2.dependencies

        result = pm.add_dependency(proposal2.id, proposal1.id)
        assert result is True
        assert proposal1.id in proposal2.dependencies

    def test_remove_dependency(self):
        """Dependencies can be removed."""
        pm = ProposalManager()

        proposal1 = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Base",
            description="Base",
            category=ProposalCategory.ARCHITECTURE,
        )

        proposal2 = pm.submit_proposal(
            agent=AIAgent.CHATGPT,
            title="Dependent",
            description="Depends on base",
            category=ProposalCategory.FEATURE_NEW,
            dependencies=[proposal1.id],
        )

        assert proposal1.id in proposal2.dependencies

        result = pm.remove_dependency(proposal2.id, proposal1.id)
        assert result is True
        assert proposal1.id not in proposal2.dependencies


class TestNotificationHooks:
    """Test notification hook system."""

    def test_register_hook(self):
        """Hooks can be registered."""
        pm = ProposalManager()

        hook = NotificationHook(
            id="test_register_hook",
            name="Test Hook",
            url="https://example.com/webhook",
        )

        hook_id = pm.register_hook(hook)
        assert hook_id == "test_register_hook"
        assert hook_id in [h.id for h in pm.get_hooks()]

    def test_unregister_hook(self):
        """Hooks can be unregistered."""
        pm = ProposalManager()

        hook = NotificationHook(
            id="test_hook",
            name="Test Hook",
            url="https://example.com/webhook",
        )

        pm.register_hook(hook)
        assert "test_hook" in [h.id for h in pm.get_hooks()]

        result = pm.unregister_hook("test_hook")
        assert result is True
        assert "test_hook" not in [h.id for h in pm.get_hooks()]

    def test_events_emitted_on_submit(self):
        """Events are emitted when proposals are submitted."""
        pm = ProposalManager()

        proposal = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Test",
            description="Test",
            category=ProposalCategory.FEATURE_NEW,
        )

        events = pm.get_events(proposal_id=proposal.id)
        assert len(events) >= 1

        submit_events = [e for e in events if e.event_type == ProposalEventType.SUBMITTED]
        assert len(submit_events) == 1

    def test_events_emitted_on_vote(self):
        """Events are emitted when votes are cast."""
        pm = ProposalManager()

        proposal = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Test",
            description="Test",
            category=ProposalCategory.FEATURE_NEW,
        )

        pm.vote_on_proposal(agent=AIAgent.USER, proposal_id=proposal.id, vote=1)

        events = pm.get_events(proposal_id=proposal.id)
        vote_events = [e for e in events if e.event_type == ProposalEventType.VOTE_CAST]
        assert len(vote_events) == 1

    def test_events_emitted_on_approval(self):
        """Approved events are emitted when proposals are approved."""
        pm = ProposalManager()

        proposal = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Test",
            description="Test",
            category=ProposalCategory.FEATURE_NEW,
        )

        pm.vote_on_proposal(agent=AIAgent.USER, proposal_id=proposal.id, vote=1)

        events = pm.get_events(proposal_id=proposal.id)
        approve_events = [e for e in events if e.event_type == ProposalEventType.APPROVED]
        assert len(approve_events) == 1

    def test_mcp_auto_approval_emits_events(self):
        """MCP auto-approved proposals emit both SUBMITTED and APPROVED events."""
        pm = ProposalManager()

        proposal = pm.submit_proposal(
            agent=AIAgent.MCP_COORDINATOR,
            title="MCP Test",
            description="Test",
            category=ProposalCategory.ARCHITECTURE,
        )

        events = pm.get_events(proposal_id=proposal.id)
        assert len(events) >= 2

        event_types = [e.event_type for e in events]
        assert ProposalEventType.SUBMITTED in event_types
        assert ProposalEventType.APPROVED in event_types

    def test_callback_triggered_on_event(self):
        """Registered callbacks are triggered on events."""
        pm = ProposalManager()
        received_events = []

        def callback(event, proposal):
            received_events.append(event)

        pm.register_callback(callback)

        proposal = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Test",
            description="Test",
            category=ProposalCategory.FEATURE_NEW,
        )

        assert len(received_events) >= 1
        assert received_events[0].proposal_id == proposal.id

    def test_hook_filtering_by_event_type(self):
        """Hooks can filter by event type."""
        hook = NotificationHook(
            id="test",
            name="Test",
            url="https://example.com",
            event_types=[ProposalEventType.APPROVED],
        )

        submitted_event = ProposalEvent(
            event_type=ProposalEventType.SUBMITTED,
            proposal_id="test_id",
        )

        approved_event = ProposalEvent(
            event_type=ProposalEventType.APPROVED,
            proposal_id="test_id",
        )

        assert hook.matches_event(submitted_event) is False
        assert hook.matches_event(approved_event) is True

    def test_hook_filtering_by_category(self):
        """Hooks can filter by proposal category."""
        hook = NotificationHook(
            id="test",
            name="Test",
            url="https://example.com",
            categories=[ProposalCategory.DSP_ALGORITHM],
        )

        event = ProposalEvent(
            event_type=ProposalEventType.SUBMITTED,
            proposal_id="test_id",
        )

        # With matching category
        assert hook.matches_event(event, ProposalCategory.DSP_ALGORITHM) is True

        # With non-matching category
        assert hook.matches_event(event, ProposalCategory.ARCHITECTURE) is False

        # With None category - hook with category filter should NOT match
        assert hook.matches_event(event, None) is False

    def test_hook_without_category_filter_matches_all(self):
        """Hooks without category filter match events regardless of category."""
        hook = NotificationHook(
            id="test",
            name="Test",
            url="https://example.com",
            categories=[],  # No category filter
        )

        event = ProposalEvent(
            event_type=ProposalEventType.SUBMITTED,
            proposal_id="test_id",
        )

        # Should match any category
        assert hook.matches_event(event, ProposalCategory.DSP_ALGORITHM) is True
        assert hook.matches_event(event, ProposalCategory.ARCHITECTURE) is True
        assert hook.matches_event(event, None) is True

    def test_serialization_includes_hooks_and_events(self):
        """Serialization includes hooks and events."""
        pm = ProposalManager()

        hook = NotificationHook(
            id="test_hook",
            name="Test Hook",
            url="https://example.com",
        )
        pm.register_hook(hook)

        proposal = pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Test",
            description="Test",
            category=ProposalCategory.FEATURE_NEW,
        )

        data = pm.to_dict()

        assert "hooks" in data
        assert "test_hook" in data["hooks"]

        assert "events" in data
        assert len(data["events"]) >= 1

    def test_deserialization_restores_hooks_and_events(self):
        """Deserialization restores hooks and events."""
        pm = ProposalManager()

        hook = NotificationHook(
            id="test_hook",
            name="Test Hook",
            url="https://example.com",
        )
        pm.register_hook(hook)

        pm.submit_proposal(
            agent=AIAgent.CLAUDE,
            title="Test",
            description="Test",
            category=ProposalCategory.FEATURE_NEW,
        )

        data = pm.to_dict()
        restored_pm = ProposalManager.from_dict(data)

        assert len(restored_pm.get_hooks()) == 1
        assert restored_pm.get_hooks()[0].id == "test_hook"
        assert len(restored_pm.events) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
