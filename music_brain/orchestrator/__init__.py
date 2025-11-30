"""
AI Orchestrator Module
======================

Coordinates multiple AI agents for music production tasks.
Part of the DAiW v1.0.0 infrastructure.

Architecture:
- AI Agents (Eraser, Pencil, Press, Smudge, Trace, Palette, Parrot)
- Dual Engine system for different creative modes
- MCP Coordinator for approval workflows
"""

from music_brain.orchestrator.agents import (
    AIAgent,
    AgentCapability,
    AgentRegistry,
    get_agent_for_task,
)
from music_brain.orchestrator.coordinator import (
    MCPCoordinator,
    CoordinatorConfig,
)
from music_brain.orchestrator.engine import (
    DualEngine,
    EngineMode,
    WorkState,
    DreamState,
)

__all__ = [
    # Agents
    "AIAgent",
    "AgentCapability",
    "AgentRegistry",
    "get_agent_for_task",
    # Coordinator
    "MCPCoordinator",
    "CoordinatorConfig",
    # Engine
    "DualEngine",
    "EngineMode",
    "WorkState",
    "DreamState",
]
