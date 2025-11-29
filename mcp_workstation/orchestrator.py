"""
MCP Workstation - Orchestrator

Central coordinator for multi-AI collaboration on the iDAW project.
"""

import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from .models import (
    AIAgent, Proposal, ProposalStatus, ProposalCategory,
    Phase, PhaseStatus, WorkstationState,
)
from .proposals import ProposalManager, format_proposal_list
from .phases import PhaseManager, format_phase_progress, get_next_actions
from .cpp_planner import CppTransitionPlanner, format_cpp_plan
from .debug import (
    get_debug, DebugCategory, DebugProtocol, trace,
    log_info, log_error, log_warning,
)
from .ai_specializations import (
    get_capabilities, get_best_agent_for_task,
    suggest_task_assignment, TaskType, AI_CAPABILITIES,
)


# =============================================================================
# Workstation Configuration
# =============================================================================

DEFAULT_STORAGE_PATH = Path.home() / ".mcp_workstation"
STATE_FILE = "workstation_state.json"
DEBUG_LOG = "workstation_debug.log"


# =============================================================================
# Main Workstation Class
# =============================================================================

class Workstation:
    """
    Central orchestrator for multi-AI collaboration.

    Coordinates Claude, ChatGPT, Gemini, and GitHub Copilot to:
    1. Submit and vote on improvement proposals
    2. Track iDAW project phases
    3. Plan C++ transition
    4. Assign tasks based on AI strengths
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        auto_load: bool = True,
    ):
        if self._initialized:
            return

        self._initialized = True
        self.storage_path = Path(storage_path) if storage_path else DEFAULT_STORAGE_PATH
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize debug protocol
        self._debug = get_debug()
        self._debug.set_log_file(str(self.storage_path / DEBUG_LOG))

        # Initialize managers
        self.proposals = ProposalManager()
        self.phases = PhaseManager()
        self.cpp_planner = CppTransitionPlanner()

        # Active agents
        self.active_agents: Dict[AIAgent, datetime] = {}

        # Session info
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.created_at = datetime.now().isoformat()

        # Load existing state if available
        if auto_load:
            self._load_state()

        log_info(
            DebugCategory.ORCHESTRATION,
            f"Workstation initialized (session: {self.session_id})",
        )

    # =========================================================================
    # Agent Management
    # =========================================================================

    @trace(DebugCategory.ORCHESTRATION)
    def register_agent(self, agent: AIAgent) -> bool:
        """Register an AI agent as active."""
        self.active_agents[agent] = datetime.now()
        log_info(
            DebugCategory.AI_COMMUNICATION,
            f"Agent registered: {agent.display_name}",
            agent=agent.value,
        )
        self._save_state()
        return True

    @trace(DebugCategory.ORCHESTRATION)
    def unregister_agent(self, agent: AIAgent):
        """Unregister an AI agent."""
        if agent in self.active_agents:
            del self.active_agents[agent]
            log_info(
                DebugCategory.AI_COMMUNICATION,
                f"Agent unregistered: {agent.display_name}",
                agent=agent.value,
            )
            self._save_state()

    def get_active_agents(self) -> List[AIAgent]:
        """Get list of active agents."""
        return list(self.active_agents.keys())

    def get_agent_capabilities(self, agent: AIAgent) -> Dict:
        """Get capabilities summary for an agent."""
        caps = get_capabilities(agent)
        return {
            "name": caps.display_name,
            "description": caps.description,
            "best_languages": caps.best_languages,
            "special_abilities": caps.special_abilities,
            "recommended_for": caps.recommended_for,
            "limitations": caps.limitations,
            "proposal_categories": [c.value for c in caps.proposal_categories],
        }

    # =========================================================================
    # Proposal Operations
    # =========================================================================

    @trace(DebugCategory.PROPOSAL)
    def submit_proposal(
        self,
        agent: AIAgent,
        title: str,
        description: str,
        category: ProposalCategory,
        priority: int = 5,
        estimated_effort: str = "medium",
        phase_target: int = 1,
        implementation_notes: str = "",
    ) -> Optional[Dict]:
        """
        Submit an improvement proposal from an AI agent.

        Each agent can submit up to 3 proposals.
        """
        # Ensure agent is registered
        if agent not in self.active_agents:
            self.register_agent(agent)

        proposal = self.proposals.submit_proposal(
            agent=agent,
            title=title,
            description=description,
            category=category,
            priority=priority,
            estimated_effort=estimated_effort,
            phase_target=phase_target,
            implementation_notes=implementation_notes,
        )

        if proposal:
            self._save_state()
            return proposal.to_dict()
        return None

    @trace(DebugCategory.PROPOSAL)
    def vote_on_proposal(
        self,
        agent: AIAgent,
        proposal_id: str,
        vote: int,
        comment: str = "",
    ) -> bool:
        """
        Cast a vote on a proposal.

        vote: -1 (reject), 0 (neutral), 1 (approve)
        """
        result = self.proposals.vote_on_proposal(agent, proposal_id, vote, comment)
        if result:
            self._save_state()
        return result

    def get_proposals_for_agent(self, agent: AIAgent) -> Dict:
        """Get proposals relevant to an agent."""
        return {
            "submitted": [p.to_dict() for p in self.proposals.get_proposals_by_agent(agent)],
            "pending_votes": [p.to_dict() for p in self.proposals.get_pending_votes(agent)],
            "slots_remaining": self.proposals.get_agent_proposal_slots()[agent],
        }

    def get_all_proposals(self) -> Dict:
        """Get all proposals with summary."""
        return {
            "proposals": [p.to_dict() for p in self.proposals.get_all_proposals()],
            "summary": self.proposals.get_proposal_summary(),
            "implementation_queue": [
                p.to_dict() for p in self.proposals.get_implementation_queue()
            ],
        }

    # =========================================================================
    # Phase Operations
    # =========================================================================

    @trace(DebugCategory.PHASE)
    def get_current_phase(self) -> Dict:
        """Get current phase information."""
        phase = self.phases.get_current_phase()
        return {
            "phase": phase.to_dict(),
            "summary": self.phases.get_phase_summary(phase.id),
            "next_actions": get_next_actions(self.phases),
        }

    @trace(DebugCategory.PHASE)
    def update_task(
        self,
        phase_id: int,
        task_id: str,
        status: str,
        progress: float = None,
        notes: str = None,
    ):
        """Update a task's status."""
        self.phases.update_task_status(
            phase_id=phase_id,
            task_id=task_id,
            status=PhaseStatus(status),
            progress=progress,
            notes=notes,
        )
        self._save_state()

    @trace(DebugCategory.PHASE)
    def assign_task_to_agent(
        self,
        phase_id: int,
        task_id: str,
        agent: AIAgent,
    ):
        """Assign a task to an AI agent."""
        self.phases.assign_task(phase_id, task_id, agent)
        self._save_state()

    @trace(DebugCategory.PHASE)
    def advance_phase(self) -> bool:
        """Advance to next phase if current is complete."""
        result = self.phases.advance_phase()
        if result:
            self._save_state()
        return result

    def get_phase_progress(self) -> str:
        """Get formatted phase progress."""
        return format_phase_progress(self.phases)

    # =========================================================================
    # C++ Transition Operations
    # =========================================================================

    @trace(DebugCategory.PHASE)
    def get_cpp_plan(self) -> Dict:
        """Get C++ transition plan."""
        return {
            "summary": self.cpp_planner.get_progress_summary(),
            "modules": [m.to_dict() for m in self.cpp_planner.modules.values()],
            "ready_modules": [m.id for m in self.cpp_planner.get_ready_modules()],
            "dependency_order": self.cpp_planner.get_dependency_order(),
        }

    @trace(DebugCategory.PHASE)
    def start_cpp_module(self, module_id: str, agent: Optional[AIAgent] = None):
        """Start work on a C++ module."""
        self.cpp_planner.start_module(module_id, agent)
        self._save_state()

    @trace(DebugCategory.PHASE)
    def update_cpp_module(self, module_id: str, progress: float, status: str = None):
        """Update C++ module progress."""
        self.cpp_planner.update_module_progress(
            module_id,
            progress,
            PhaseStatus(status) if status else None,
        )
        self._save_state()

    def get_cpp_progress(self) -> str:
        """Get formatted C++ transition progress."""
        return format_cpp_plan(self.cpp_planner)

    def get_cmake_plan(self) -> str:
        """Get CMake build plan."""
        return self.cpp_planner.get_build_plan()

    # =========================================================================
    # Task Assignment
    # =========================================================================

    @trace(DebugCategory.ORCHESTRATION)
    def suggest_assignments(self, tasks: List[tuple]) -> Dict[str, str]:
        """
        Suggest optimal AI assignments for a list of tasks.

        tasks: List of (task_name, task_type) tuples
        Returns: Dict of {task_name: agent_value}
        """
        assignments = suggest_task_assignment(tasks)
        return {name: agent.value for name, agent in assignments.items()}

    def get_agent_workload(self) -> Dict[str, Dict]:
        """Get current workload for each agent."""
        workload = {agent.value: {"tasks": [], "proposals": 0} for agent in AIAgent}

        # Count proposals
        for proposal in self.proposals.get_all_proposals():
            if proposal.status == ProposalStatus.APPROVED:
                workload[proposal.agent.value]["proposals"] += 1

        # Count assigned tasks
        for phase in self.phases.phases:
            for task in phase.tasks:
                if task.assigned_to and task.status == PhaseStatus.IN_PROGRESS:
                    workload[task.assigned_to.value]["tasks"].append(task.name)

        # Count C++ tasks
        for task in self.cpp_planner.tasks.values():
            if task.assigned_to and task.status == PhaseStatus.IN_PROGRESS:
                workload[task.assigned_to.value]["tasks"].append(task.name)

        return workload

    # =========================================================================
    # Debug & Monitoring
    # =========================================================================

    def get_debug_summary(self) -> Dict:
        """Get debug and monitoring summary."""
        return {
            "recent_errors": [e.to_dict() for e in self._debug.get_errors(10)],
            "performance": self._debug.get_performance_report(),
            "agent_activity": {
                agent.value: [e.to_dict() for e in self._debug.get_ai_activity(agent.value, 5)]
                for agent in self.active_agents
            },
        }

    def export_debug_session(self, path: str):
        """Export debug session for analysis."""
        self._debug.export_session(path)

    # =========================================================================
    # Status & Summary
    # =========================================================================

    def get_status(self) -> Dict:
        """Get complete workstation status."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "active_agents": [a.value for a in self.active_agents],
            "proposals": self.proposals.get_proposal_summary(),
            "phases": self.phases.get_phase_summary(),
            "cpp_transition": self.cpp_planner.get_progress_summary(),
            "workload": self.get_agent_workload(),
        }

    def get_dashboard(self) -> str:
        """Get formatted dashboard view."""
        lines = [
            "=" * 70,
            "MCP WORKSTATION - Multi-AI Collaboration Dashboard",
            "=" * 70,
            "",
            f"Session: {self.session_id}",
            f"Active Agents: {', '.join(a.display_name for a in self.active_agents)}",
            "",
        ]

        # Proposals summary
        prop_summary = self.proposals.get_proposal_summary()
        lines.extend([
            "PROPOSALS:",
            f"  Total: {prop_summary['total']} | "
            f"Approved: {prop_summary['by_status'].get('approved', 0)} | "
            f"Pending: {prop_summary['by_status'].get('submitted', 0)}",
            "",
        ])

        # Phase summary
        phase_summary = self.phases.get_phase_summary()
        lines.extend([
            f"PROJECT PHASE: {phase_summary['current_phase']}",
            f"  Overall Progress: {phase_summary['overall_progress']:.0%}",
            "",
        ])

        for p in phase_summary['phases']:
            status_icon = "◐" if p["status"] == "in_progress" else ("●" if p["status"] == "completed" else "○")
            lines.append(f"  {status_icon} Phase {p['phase_id']}: {p['name']} ({p['progress']:.0%})")

        lines.append("")

        # C++ transition
        cpp_summary = self.cpp_planner.get_progress_summary()
        lines.extend([
            "C++ TRANSITION:",
            f"  Progress: {cpp_summary['overall_progress']:.0%}",
            f"  Modules: {cpp_summary['modules_completed']}/{cpp_summary['total_modules']}",
            f"  Ready to start: {', '.join(cpp_summary['ready_to_start'][:3])}...",
            "",
        ])

        # Next actions
        next_actions = get_next_actions(self.phases)
        if next_actions:
            lines.extend([
                "NEXT ACTIONS:",
                *[f"  • {action}" for action in next_actions[:5]],
            ])

        return "\n".join(lines)

    # =========================================================================
    # Persistence
    # =========================================================================

    def _save_state(self):
        """Save workstation state to disk."""
        state = {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "active_agents": [a.value for a in self.active_agents],
            "proposals": self.proposals.to_dict(),
            "phases": self.phases.to_dict(),
            "cpp_planner": self.cpp_planner.to_dict(),
            "updated_at": datetime.now().isoformat(),
        }

        state_file = self.storage_path / STATE_FILE
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

        log_info(
            DebugCategory.STORAGE,
            f"State saved to {state_file}",
        )

    def _load_state(self):
        """Load workstation state from disk."""
        state_file = self.storage_path / STATE_FILE

        if not state_file.exists():
            log_info(
                DebugCategory.STORAGE,
                "No existing state found, starting fresh",
            )
            return

        try:
            with open(state_file, 'r') as f:
                state = json.load(f)

            # Restore active agents
            self.active_agents = {
                AIAgent(a): datetime.now()
                for a in state.get("active_agents", [])
            }

            # Restore managers
            if "proposals" in state:
                self.proposals = ProposalManager.from_dict(state["proposals"])

            if "phases" in state:
                self.phases = PhaseManager.from_dict(state["phases"])

            if "cpp_planner" in state:
                self.cpp_planner = CppTransitionPlanner.from_dict(state["cpp_planner"])

            self.session_id = state.get("session_id", self.session_id)
            self.created_at = state.get("created_at", self.created_at)

            log_info(
                DebugCategory.STORAGE,
                f"State loaded from {state_file}",
            )

        except Exception as e:
            log_error(
                DebugCategory.STORAGE,
                f"Failed to load state: {e}",
            )

    def reset(self):
        """Reset workstation to initial state."""
        self.proposals = ProposalManager()
        self.phases = PhaseManager()
        self.cpp_planner = CppTransitionPlanner()
        self.active_agents = {}
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.created_at = datetime.now().isoformat()
        self._save_state()

        log_info(
            DebugCategory.ORCHESTRATION,
            "Workstation reset",
        )


# =============================================================================
# Global Functions
# =============================================================================

_workstation: Optional[Workstation] = None


def get_workstation() -> Workstation:
    """Get the global workstation instance."""
    global _workstation
    if _workstation is None:
        _workstation = Workstation()
    return _workstation


def shutdown_workstation():
    """Shutdown the workstation."""
    global _workstation
    if _workstation:
        _workstation._save_state()
        _workstation = None
        log_info(
            DebugCategory.ORCHESTRATION,
            "Workstation shutdown",
        )
