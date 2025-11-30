"""
AI Agent Definitions
====================

Defines the specialized AI agents for the DAiW orchestrator.
Each agent has specific capabilities and roles in the music production pipeline.

Agents:
- Eraser: Clean up, remove unwanted elements
- Pencil: Draft initial ideas, sketch outlines
- Press: Polish and finalize production
- Smudge: Blend and smooth transitions
- Trace: Analyze and learn from references
- Palette: Color/tonal decisions
- Parrot: Style mimicry and transfer
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any
from enum import Enum


class AgentCapability(Enum):
    """Capabilities that agents can have."""
    HARMONY = "harmony"
    RHYTHM = "rhythm"
    MELODY = "melody"
    ARRANGEMENT = "arrangement"
    PRODUCTION = "production"
    MIXING = "mixing"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    STYLE_TRANSFER = "style_transfer"
    CLEANUP = "cleanup"
    REFINEMENT = "refinement"


@dataclass
class AIAgent:
    """Represents a specialized AI agent."""
    name: str
    role: str
    capabilities: Set[AgentCapability]
    description: str
    priority: int = 5  # 1-10, higher = more important
    enabled: bool = True

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        return f"{self.name} ({self.role})"

    def can_handle(self, capability: AgentCapability) -> bool:
        """Check if agent can handle a specific capability."""
        return capability in self.capabilities

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "role": self.role,
            "capabilities": [c.value for c in self.capabilities],
            "description": self.description,
            "priority": self.priority,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIAgent":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            role=data["role"],
            capabilities={AgentCapability(c) for c in data["capabilities"]},
            description=data["description"],
            priority=data.get("priority", 5),
            enabled=data.get("enabled", True),
        )


# =============================================================================
# Default Agent Definitions
# =============================================================================

# The 7 core agents
ERASER = AIAgent(
    name="Eraser",
    role="Cleanup Specialist",
    capabilities={AgentCapability.CLEANUP, AgentCapability.MIXING, AgentCapability.REFINEMENT},
    description="Removes unwanted elements, cleans up recordings, reduces noise",
    priority=3,
)

PENCIL = AIAgent(
    name="Pencil",
    role="Initial Drafter",
    capabilities={AgentCapability.GENERATION, AgentCapability.MELODY, AgentCapability.HARMONY},
    description="Sketches initial ideas, creates rough drafts and outlines",
    priority=7,
)

PRESS = AIAgent(
    name="Press",
    role="Finisher",
    capabilities={AgentCapability.PRODUCTION, AgentCapability.MIXING, AgentCapability.REFINEMENT},
    description="Polishes and finalizes productions, applies final touches",
    priority=5,
)

SMUDGE = AIAgent(
    name="Smudge",
    role="Blender",
    capabilities={AgentCapability.ARRANGEMENT, AgentCapability.MIXING, AgentCapability.REFINEMENT},
    description="Blends elements together, creates smooth transitions",
    priority=4,
)

TRACE = AIAgent(
    name="Trace",
    role="Analyzer",
    capabilities={AgentCapability.ANALYSIS, AgentCapability.STYLE_TRANSFER},
    description="Analyzes reference tracks, extracts patterns and DNA",
    priority=6,
)

PALETTE = AIAgent(
    name="Palette",
    role="Tonal Designer",
    capabilities={AgentCapability.HARMONY, AgentCapability.PRODUCTION},
    description="Makes tonal and color decisions, designs sound palette",
    priority=6,
)

PARROT = AIAgent(
    name="Parrot",
    role="Style Mimic",
    capabilities={AgentCapability.STYLE_TRANSFER, AgentCapability.GENERATION, AgentCapability.MELODY},
    description="Mimics styles, transfers characteristics between pieces",
    priority=4,
)


class AgentRegistry:
    """
    Registry for managing AI agents.

    Provides lookup, filtering, and task routing capabilities.
    """

    def __init__(self):
        self.agents: Dict[str, AIAgent] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Register the default 7 agents."""
        for agent in [ERASER, PENCIL, PRESS, SMUDGE, TRACE, PALETTE, PARROT]:
            self.register(agent)

    def register(self, agent: AIAgent) -> None:
        """Register an agent."""
        self.agents[agent.name.lower()] = agent

    def get(self, name: str) -> Optional[AIAgent]:
        """Get an agent by name."""
        return self.agents.get(name.lower())

    def list_all(self) -> List[AIAgent]:
        """Get all registered agents."""
        return list(self.agents.values())

    def list_enabled(self) -> List[AIAgent]:
        """Get all enabled agents."""
        return [a for a in self.agents.values() if a.enabled]

    def find_by_capability(self, capability: AgentCapability) -> List[AIAgent]:
        """Find agents that have a specific capability."""
        return [
            a for a in self.agents.values()
            if a.enabled and a.can_handle(capability)
        ]

    def get_best_for_task(self, capability: AgentCapability) -> Optional[AIAgent]:
        """Get the highest priority agent for a capability."""
        candidates = self.find_by_capability(capability)
        if not candidates:
            return None
        return max(candidates, key=lambda a: a.priority)


# Global registry instance
_registry = AgentRegistry()


def get_agent_for_task(capability: AgentCapability) -> Optional[AIAgent]:
    """Get the best agent for a specific task capability."""
    return _registry.get_best_for_task(capability)


def list_agents() -> List[AIAgent]:
    """List all registered agents."""
    return _registry.list_all()


def get_agent(name: str) -> Optional[AIAgent]:
    """Get a specific agent by name."""
    return _registry.get(name)
