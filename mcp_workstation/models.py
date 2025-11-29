"""
MCP Workstation - Data Models

Defines AI agents, proposals, phases, and workstation state.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import uuid


class AIAgent(str, Enum):
    """AI assistants participating in the workstation."""
    CLAUDE = "claude"
    CHATGPT = "chatgpt"
    GEMINI = "gemini"
    GITHUB_COPILOT = "github_copilot"
    MCP_COORDINATOR = "mcp_coordinator"  # Special agent for auto-approval
    USER = "user"  # Ultimate voter (sburdges-eng)

    @property
    def display_name(self) -> str:
        names = {
            "claude": "Claude (Anthropic)",
            "chatgpt": "ChatGPT (OpenAI)",
            "gemini": "Gemini (Google)",
            "github_copilot": "GitHub Copilot",
            "mcp_coordinator": "MCP Coordinator",
            "user": "User (sburdges-eng)",
        }
        return names.get(self.value, self.value)

    @property
    def is_mcp_coordinator(self) -> bool:
        """Check if this agent is the MCP coordinator."""
        return self == AIAgent.MCP_COORDINATOR

    @property
    def is_user(self) -> bool:
        """Check if this agent is the ultimate user voter."""
        return self == AIAgent.USER


class ProposalStatus(str, Enum):
    """Status of a proposal."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    DEFERRED = "deferred"


class ProposalCategory(str, Enum):
    """Category of improvement proposal."""
    # Core System
    ARCHITECTURE = "architecture"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"

    # Features
    FEATURE_NEW = "feature_new"
    FEATURE_ENHANCEMENT = "feature_enhancement"
    USER_EXPERIENCE = "user_experience"

    # Audio/Music Specific
    AUDIO_PROCESSING = "audio_processing"
    MIDI_HANDLING = "midi_handling"
    DSP_ALGORITHM = "dsp_algorithm"
    DAW_INTEGRATION = "daw_integration"

    # Development
    CODE_QUALITY = "code_quality"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    BUILD_SYSTEM = "build_system"

    # C++ Transition
    CPP_PORT = "cpp_port"
    CPP_OPTIMIZATION = "cpp_optimization"
    MEMORY_MANAGEMENT = "memory_management"

    # Multi-AI
    AI_COLLABORATION = "ai_collaboration"
    TOOL_INTEGRATION = "tool_integration"


class PhaseStatus(str, Enum):
    """Status of a project phase."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    VERIFIED = "verified"


@dataclass
class Proposal:
    """An improvement proposal from an AI agent."""
    id: str
    agent: AIAgent
    title: str
    description: str
    category: ProposalCategory
    status: ProposalStatus = ProposalStatus.DRAFT
    priority: int = 5  # 1-10, 10 being highest
    estimated_effort: str = "medium"  # low, medium, high, very_high
    phase_target: int = 1  # Which iDAW phase this targets
    dependencies: List[str] = field(default_factory=list)  # Other proposal IDs
    implementation_notes: str = ""
    votes: Dict[str, int] = field(default_factory=dict)  # agent_id -> vote (-1, 0, 1)
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent": self.agent.value if isinstance(self.agent, AIAgent) else self.agent,
            "title": self.title,
            "description": self.description,
            "category": self.category.value if isinstance(self.category, ProposalCategory) else self.category,
            "status": self.status.value if isinstance(self.status, ProposalStatus) else self.status,
            "priority": self.priority,
            "estimated_effort": self.estimated_effort,
            "phase_target": self.phase_target,
            "dependencies": self.dependencies,
            "implementation_notes": self.implementation_notes,
            "votes": self.votes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Proposal":
        return cls(
            id=data.get("id", ""),
            agent=AIAgent(data["agent"]) if data.get("agent") else AIAgent.CLAUDE,
            title=data.get("title", ""),
            description=data.get("description", ""),
            category=ProposalCategory(data["category"]) if data.get("category") else ProposalCategory.FEATURE_NEW,
            status=ProposalStatus(data["status"]) if data.get("status") else ProposalStatus.DRAFT,
            priority=data.get("priority", 5),
            estimated_effort=data.get("estimated_effort", "medium"),
            phase_target=data.get("phase_target", 1),
            dependencies=data.get("dependencies", []),
            implementation_notes=data.get("implementation_notes", ""),
            votes=data.get("votes", {}),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    @property
    def vote_score(self) -> int:
        """Calculate total vote score."""
        return sum(self.votes.values())

    def add_vote(self, agent: AIAgent, vote: int):
        """Add or update a vote (-1, 0, or 1)."""
        vote = max(-1, min(1, vote))  # Clamp to [-1, 1]
        self.votes[agent.value] = vote
        self.updated_at = datetime.now().isoformat()


@dataclass
class PhaseTask:
    """A task within a project phase."""
    id: str
    name: str
    description: str
    status: PhaseStatus = PhaseStatus.NOT_STARTED
    assigned_to: Optional[AIAgent] = None
    progress: float = 0.0  # 0.0 to 1.0
    blockers: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: str = ""
    completed_at: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "assigned_to": self.assigned_to.value if self.assigned_to else None,
            "progress": self.progress,
            "blockers": self.blockers,
            "notes": self.notes,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PhaseTask":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            status=PhaseStatus(data["status"]) if data.get("status") else PhaseStatus.NOT_STARTED,
            assigned_to=AIAgent(data["assigned_to"]) if data.get("assigned_to") else None,
            progress=data.get("progress", 0.0),
            blockers=data.get("blockers", []),
            notes=data.get("notes", ""),
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at"),
        )


@dataclass
class Phase:
    """A major project phase."""
    id: int
    name: str
    description: str
    status: PhaseStatus = PhaseStatus.NOT_STARTED
    progress: float = 0.0
    tasks: List[PhaseTask] = field(default_factory=list)
    milestones: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    start_date: Optional[str] = None
    target_completion: Optional[str] = None
    actual_completion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "progress": self.progress,
            "tasks": [t.to_dict() for t in self.tasks],
            "milestones": self.milestones,
            "deliverables": self.deliverables,
            "start_date": self.start_date,
            "target_completion": self.target_completion,
            "actual_completion": self.actual_completion,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Phase":
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            description=data.get("description", ""),
            status=PhaseStatus(data["status"]) if data.get("status") else PhaseStatus.NOT_STARTED,
            progress=data.get("progress", 0.0),
            tasks=[PhaseTask.from_dict(t) for t in data.get("tasks", [])],
            milestones=data.get("milestones", []),
            deliverables=data.get("deliverables", []),
            start_date=data.get("start_date"),
            target_completion=data.get("target_completion"),
            actual_completion=data.get("actual_completion"),
        )

    def update_progress(self):
        """Update progress based on task completion."""
        if not self.tasks:
            return
        completed = sum(1 for t in self.tasks if t.status == PhaseStatus.COMPLETED)
        self.progress = completed / len(self.tasks)
        if self.progress >= 1.0:
            self.status = PhaseStatus.COMPLETED
            self.actual_completion = datetime.now().isoformat()
        elif self.progress > 0:
            self.status = PhaseStatus.IN_PROGRESS


@dataclass
class WorkstationState:
    """Complete workstation state for persistence."""
    proposals: List[Proposal] = field(default_factory=list)
    phases: List[Phase] = field(default_factory=list)
    active_agents: List[AIAgent] = field(default_factory=list)
    current_phase: int = 1
    session_id: str = ""
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposals": [p.to_dict() for p in self.proposals],
            "phases": [p.to_dict() for p in self.phases],
            "active_agents": [a.value for a in self.active_agents],
            "current_phase": self.current_phase,
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkstationState":
        return cls(
            proposals=[Proposal.from_dict(p) for p in data.get("proposals", [])],
            phases=[Phase.from_dict(p) for p in data.get("phases", [])],
            active_agents=[AIAgent(a) for a in data.get("active_agents", [])],
            current_phase=data.get("current_phase", 1),
            session_id=data.get("session_id", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    def save(self, path: str):
        """Save state to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "WorkstationState":
        """Load state from JSON file."""
        with open(path, 'r') as f:
            return cls.from_dict(json.load(f))


@dataclass
class UserSpecialty:
    """
    User-defined specialty/role for proposal voting and assignment.

    Users can define their expertise areas to influence how they vote
    and what tasks get assigned to them.
    """
    name: str
    categories: List[ProposalCategory] = field(default_factory=list)
    weight: float = 1.0  # 0.0-2.0, higher means more influence in that area
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "categories": [c.value for c in self.categories],
            "weight": self.weight,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserSpecialty":
        return cls(
            name=data.get("name", ""),
            categories=[ProposalCategory(c) for c in data.get("categories", [])],
            weight=data.get("weight", 1.0),
            description=data.get("description", ""),
        )


@dataclass
class UserVotingConfig:
    """
    Configuration for the ultimate user voter (sburdges-eng).

    This defines how the user's votes are weighted and what override
    capabilities they have.
    """
    username: str = "sburdges-eng"
    specialties: List[UserSpecialty] = field(default_factory=list)
    ultimate_veto: bool = True  # Can veto any proposal
    ultimate_approve: bool = True  # Can approve any proposal directly
    auto_approve_mcp: bool = True  # Auto-approve MCP coordinator proposals
    vote_weight: float = 2.0  # User's vote counts as this many votes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "specialties": [s.to_dict() for s in self.specialties],
            "ultimate_veto": self.ultimate_veto,
            "ultimate_approve": self.ultimate_approve,
            "auto_approve_mcp": self.auto_approve_mcp,
            "vote_weight": self.vote_weight,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserVotingConfig":
        return cls(
            username=data.get("username", "sburdges-eng"),
            specialties=[
                UserSpecialty.from_dict(s) for s in data.get("specialties", [])
            ],
            ultimate_veto=data.get("ultimate_veto", True),
            ultimate_approve=data.get("ultimate_approve", True),
            auto_approve_mcp=data.get("auto_approve_mcp", True),
            vote_weight=data.get("vote_weight", 2.0),
        )

    def get_category_weight(self, category: ProposalCategory) -> float:
        """Get the user's voting weight for a specific category."""
        for specialty in self.specialties:
            if category in specialty.categories:
                return self.vote_weight * specialty.weight
        return self.vote_weight
