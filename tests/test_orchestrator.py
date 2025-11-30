"""
Tests for the orchestrator module.

Run with: pytest tests/test_orchestrator.py -v
"""

import pytest
from music_brain.orchestrator.agents import (
    AIAgent,
    AgentCapability,
    AgentRegistry,
    get_agent_for_task,
    PENCIL,
    ERASER,
    TRACE,
)
from music_brain.orchestrator.coordinator import (
    MCPCoordinator,
    CoordinatorConfig,
    ApprovalStatus,
)
from music_brain.orchestrator.engine import (
    DualEngine,
    EngineMode,
    WorkState,
    DreamState,
)


# =============================================================================
# Agent Tests
# =============================================================================

class TestAIAgent:
    """Tests for AIAgent class."""

    def test_agent_creation(self):
        """Should create agent with required fields."""
        agent = AIAgent(
            name="Test",
            role="Tester",
            capabilities={AgentCapability.HARMONY},
            description="A test agent",
        )
        assert agent.name == "Test"
        assert agent.role == "Tester"
        assert AgentCapability.HARMONY in agent.capabilities

    def test_agent_display_name(self):
        """Display name should combine name and role."""
        agent = AIAgent(
            name="Pencil",
            role="Drafter",
            capabilities=set(),
            description="",
        )
        assert "Pencil" in agent.display_name
        assert "Drafter" in agent.display_name

    def test_agent_can_handle(self):
        """Can handle should check capabilities."""
        agent = AIAgent(
            name="Test",
            role="Test",
            capabilities={AgentCapability.HARMONY, AgentCapability.MELODY},
            description="",
        )
        assert agent.can_handle(AgentCapability.HARMONY)
        assert agent.can_handle(AgentCapability.MELODY)
        assert not agent.can_handle(AgentCapability.MIXING)

    def test_agent_serialization(self):
        """Should serialize to dict correctly."""
        agent = AIAgent(
            name="Test",
            role="Tester",
            capabilities={AgentCapability.RHYTHM},
            description="Test agent",
            priority=7,
            enabled=False,
        )
        data = agent.to_dict()
        assert data["name"] == "Test"
        assert data["priority"] == 7
        assert data["enabled"] is False
        assert "rhythm" in data["capabilities"]

    def test_agent_deserialization(self):
        """Should deserialize from dict correctly."""
        data = {
            "name": "Restored",
            "role": "Tester",
            "capabilities": ["harmony", "rhythm"],
            "description": "Restored agent",
            "priority": 8,
            "enabled": True,
        }
        agent = AIAgent.from_dict(data)
        assert agent.name == "Restored"
        assert agent.priority == 8
        assert AgentCapability.HARMONY in agent.capabilities


class TestAgentRegistry:
    """Tests for AgentRegistry class."""

    def test_registry_has_default_agents(self):
        """Registry should initialize with 7 default agents."""
        registry = AgentRegistry()
        assert len(registry.list_all()) == 7

    def test_registry_get_by_name(self):
        """Should get agent by name (case-insensitive)."""
        registry = AgentRegistry()
        agent = registry.get("pencil")
        assert agent is not None
        assert agent.name == "Pencil"

        agent_upper = registry.get("PENCIL")
        assert agent_upper is not None

    def test_registry_find_by_capability(self):
        """Should find agents with specific capability."""
        registry = AgentRegistry()
        harmony_agents = registry.find_by_capability(AgentCapability.HARMONY)
        assert len(harmony_agents) > 0

    def test_registry_get_best_for_task(self):
        """Should get highest priority agent for task."""
        registry = AgentRegistry()
        best = registry.get_best_for_task(AgentCapability.GENERATION)
        assert best is not None


class TestDefaultAgents:
    """Tests for default agent definitions."""

    def test_pencil_has_generation(self):
        """Pencil should have generation capability."""
        assert AgentCapability.GENERATION in PENCIL.capabilities

    def test_eraser_has_cleanup(self):
        """Eraser should have cleanup capability."""
        assert AgentCapability.CLEANUP in ERASER.capabilities

    def test_trace_has_analysis(self):
        """Trace should have analysis capability."""
        assert AgentCapability.ANALYSIS in TRACE.capabilities


# =============================================================================
# Coordinator Tests
# =============================================================================

class TestMCPCoordinator:
    """Tests for MCPCoordinator class."""

    def test_coordinator_creation(self):
        """Should create coordinator with default config."""
        coordinator = MCPCoordinator()
        assert coordinator is not None
        assert coordinator.config is not None

    def test_coordinator_with_custom_config(self):
        """Should accept custom configuration."""
        config = CoordinatorConfig(
            auto_approve_threshold=0.9,
            require_user_vote=False,
        )
        coordinator = MCPCoordinator(config)
        assert coordinator.config.auto_approve_threshold == 0.9
        assert coordinator.config.require_user_vote is False

    def test_submit_task(self):
        """Should submit task and return ID."""
        coordinator = MCPCoordinator()
        task_id = coordinator.submit_task(
            capability="harmony",
            description="Analyze chord progression",
        )
        assert task_id is not None
        assert task_id.startswith("task-")

    def test_get_task_status(self):
        """Should return task status."""
        coordinator = MCPCoordinator()
        task_id = coordinator.submit_task(
            capability="rhythm",
            description="Apply groove",
        )
        status = coordinator.get_task_status(task_id)
        assert status == ApprovalStatus.PENDING

    def test_vote_on_task(self):
        """Should record vote on task."""
        coordinator = MCPCoordinator()
        task_id = coordinator.submit_task(
            capability="test",
            description="Test task",
        )
        result = coordinator.vote(task_id, "user1", 1)
        assert result is True

    def test_vote_score_calculation(self):
        """Should calculate weighted vote score."""
        coordinator = MCPCoordinator()
        task_id = coordinator.submit_task(
            capability="test",
            description="Test",
        )
        coordinator.vote(task_id, "user1", 1)
        coordinator.vote(task_id, "user2", 1)
        score = coordinator.get_vote_score(task_id)
        assert score == 1.0

    def test_specialist_vote_weight(self):
        """Specialist votes should have higher weight."""
        coordinator = MCPCoordinator()
        task_id = coordinator.submit_task(
            capability="test",
            description="Test",
        )
        coordinator.vote(task_id, "user1", 1, is_specialist=True)
        coordinator.vote(task_id, "user2", -1, is_specialist=False)
        score = coordinator.get_vote_score(task_id)
        # Specialist weight is 1.5, so should be positive
        assert score > 0

    def test_get_pending_tasks(self):
        """Should return list of pending tasks."""
        coordinator = MCPCoordinator()
        coordinator.submit_task("test1", "Task 1")
        coordinator.submit_task("test2", "Task 2")
        pending = coordinator.get_pending_tasks()
        assert len(pending) == 2


# =============================================================================
# Dual Engine Tests
# =============================================================================

class TestDualEngine:
    """Tests for DualEngine class."""

    def test_engine_creation(self):
        """Should create engine with default mode."""
        engine = DualEngine()
        assert engine.current_mode == EngineMode.WORK

    def test_enter_work_mode(self):
        """Should enter work mode."""
        engine = DualEngine()
        state = engine.enter_work_mode()
        assert isinstance(state, WorkState)
        assert engine.in_work_mode

    def test_enter_dream_mode(self):
        """Should enter dream mode."""
        engine = DualEngine()
        state = engine.enter_dream_mode()
        assert isinstance(state, DreamState)
        assert engine.in_dream_mode

    def test_toggle_mode(self):
        """Should toggle between modes."""
        engine = DualEngine()
        engine.enter_work_mode()
        assert engine.in_work_mode

        engine.toggle_mode()
        assert engine.in_dream_mode

        engine.toggle_mode()
        assert engine.in_work_mode

    def test_work_state_tasks(self):
        """Work state should track tasks."""
        engine = DualEngine()
        state = engine.enter_work_mode()
        state.start_task("Task 1")
        assert state.current_task == "Task 1"

        state.complete_task()
        assert state.current_task is None
        assert "Task 1" in state.completed_tasks

    def test_dream_state_exploration(self):
        """Dream state should track exploration."""
        engine = DualEngine()
        state = engine.enter_dream_mode()
        assert state.exploration_depth == 0

        state.explore("New idea")
        assert state.exploration_depth == 1
        assert "New idea" in state.discovered_ideas

    def test_chaos_level_in_dream_state(self):
        """Dream state should accept chaos level."""
        engine = DualEngine()
        state = engine.enter_dream_mode(chaos_level=0.8)
        assert state.chaos_level == 0.8

    def test_mode_history(self):
        """Should track mode transition history."""
        engine = DualEngine()
        engine.enter_work_mode()
        engine.enter_dream_mode()
        engine.enter_work_mode()

        history = engine.get_history()
        assert len(history) == 2  # Two archived states

    def test_engine_stats(self):
        """Should provide engine statistics."""
        engine = DualEngine()
        engine.enter_work_mode()

        stats = engine.get_stats()
        assert "current_mode" in stats
        assert stats["current_mode"] == "work"
