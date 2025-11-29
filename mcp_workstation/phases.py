"""
MCP Workstation - Phase Management

Manages the 3 phases of the iDAW project:
1. Core Systems (Python foundation)
2. Expansion & Integration (MCP, audio analysis)
3. Advanced Features (C++ DAW plugin)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

from .models import Phase, PhaseTask, PhaseStatus, AIAgent
from .debug import get_debug, DebugCategory, trace


# =============================================================================
# iDAW Project Phases Definition
# =============================================================================

IDAW_PHASES = [
    Phase(
        id=1,
        name="Core Systems",
        description="Complete Python foundation with CLI, groove system, intent schema, and local AI agents.",
        status=PhaseStatus.IN_PROGRESS,
        progress=0.92,
        milestones=[
            "CLI completion (daiw command)",
            "Groove extraction/application",
            "Intent schema processing",
            "Local AI agents (Ollama)",
            "Voice profiles system",
            "MCP TODO server",
        ],
        deliverables=[
            "Working daiw CLI",
            "Groove templates for 10+ genres",
            "Complete intent processing pipeline",
            "6 AI agent roles",
            "Voice customization system",
            "Multi-AI task synchronization",
        ],
        tasks=[
            PhaseTask(
                id="p1_cli",
                name="CLI Completion",
                description="Finish all CLI commands and options",
                status=PhaseStatus.COMPLETED,
                progress=1.0,
            ),
            PhaseTask(
                id="p1_groove",
                name="Groove System",
                description="Extract and apply groove templates",
                status=PhaseStatus.COMPLETED,
                progress=1.0,
            ),
            PhaseTask(
                id="p1_intent",
                name="Intent Schema",
                description="Three-phase intent processing",
                status=PhaseStatus.COMPLETED,
                progress=1.0,
            ),
            PhaseTask(
                id="p1_agents",
                name="AI Agents",
                description="Local Ollama-based AI agents",
                status=PhaseStatus.COMPLETED,
                progress=1.0,
            ),
            PhaseTask(
                id="p1_voice",
                name="Voice Profiles",
                description="Voice customization with accents and patterns",
                status=PhaseStatus.COMPLETED,
                progress=1.0,
            ),
            PhaseTask(
                id="p1_mcp",
                name="MCP Integration",
                description="MCP TODO server for multi-AI",
                status=PhaseStatus.COMPLETED,
                progress=1.0,
            ),
            PhaseTask(
                id="p1_workstation",
                name="MCP Workstation",
                description="Multi-AI orchestration system",
                status=PhaseStatus.IN_PROGRESS,
                progress=0.5,
            ),
        ],
    ),
    Phase(
        id=2,
        name="Expansion & Integration",
        description="Expand capabilities with advanced MCP tools, audio analysis, DAW integration, and testing.",
        status=PhaseStatus.NOT_STARTED,
        progress=0.0,
        milestones=[
            "Full MCP tool set for all 4 AIs",
            "Audio feature extraction",
            "Ableton Live integration",
            "VST3 host preparation",
            "Comprehensive test suite",
        ],
        deliverables=[
            "MCP tools for groove, chord, intent",
            "Audio analysis (librosa integration)",
            "OSC/MIDI DAW control",
            "VST3 hosting foundation",
            "90%+ test coverage",
        ],
        tasks=[
            PhaseTask(
                id="p2_mcp_tools",
                name="MCP Tool Expansion",
                description="Create MCP tools for all core features",
                status=PhaseStatus.NOT_STARTED,
            ),
            PhaseTask(
                id="p2_audio",
                name="Audio Analysis",
                description="Integrate librosa for audio feature extraction",
                status=PhaseStatus.NOT_STARTED,
            ),
            PhaseTask(
                id="p2_ableton",
                name="Ableton Integration",
                description="Complete Ableton Live OSC/MIDI bridge",
                status=PhaseStatus.NOT_STARTED,
            ),
            PhaseTask(
                id="p2_vst_prep",
                name="VST3 Preparation",
                description="Setup VST3 hosting infrastructure",
                status=PhaseStatus.NOT_STARTED,
            ),
            PhaseTask(
                id="p2_testing",
                name="Test Suite",
                description="Comprehensive testing with >90% coverage",
                status=PhaseStatus.NOT_STARTED,
            ),
            PhaseTask(
                id="p2_docs",
                name="Documentation",
                description="Complete API and user documentation",
                status=PhaseStatus.NOT_STARTED,
            ),
        ],
    ),
    Phase(
        id=3,
        name="Advanced Features & C++ Transition",
        description="Transition core components to C++ for professional DAW plugin development.",
        status=PhaseStatus.NOT_STARTED,
        progress=0.0,
        milestones=[
            "C++ DSP core library",
            "VST3/AU/AAX plugin framework",
            "Real-time audio processing",
            "GUI framework (JUCE)",
            "Professional DAW release",
        ],
        deliverables=[
            "libdaiw-core (C++ library)",
            "DAiW plugin (VST3/AU/AAX)",
            "Real-time groove application",
            "Professional GUI",
            "Cross-platform builds",
        ],
        tasks=[
            PhaseTask(
                id="p3_cpp_core",
                name="C++ Core Library",
                description="Port core algorithms to C++",
                status=PhaseStatus.NOT_STARTED,
            ),
            PhaseTask(
                id="p3_dsp",
                name="DSP Module",
                description="Real-time DSP processing in C++",
                status=PhaseStatus.NOT_STARTED,
            ),
            PhaseTask(
                id="p3_midi",
                name="MIDI Engine",
                description="High-performance MIDI processing",
                status=PhaseStatus.NOT_STARTED,
            ),
            PhaseTask(
                id="p3_vst",
                name="VST3 Plugin",
                description="VST3 plugin wrapper",
                status=PhaseStatus.NOT_STARTED,
            ),
            PhaseTask(
                id="p3_au",
                name="Audio Unit Plugin",
                description="macOS Audio Unit wrapper",
                status=PhaseStatus.NOT_STARTED,
            ),
            PhaseTask(
                id="p3_gui",
                name="Plugin GUI",
                description="JUCE-based professional GUI",
                status=PhaseStatus.NOT_STARTED,
            ),
            PhaseTask(
                id="p3_build",
                name="Build System",
                description="CMake cross-platform builds",
                status=PhaseStatus.NOT_STARTED,
            ),
            PhaseTask(
                id="p3_python_bridge",
                name="Python Bridge",
                description="pybind11 bridge for Python access to C++ core",
                status=PhaseStatus.NOT_STARTED,
            ),
        ],
    ),
]


# =============================================================================
# Phase Manager
# =============================================================================

class PhaseManager:
    """
    Manages iDAW project phases.

    Tracks progress, assigns tasks, and coordinates phase transitions.
    """

    def __init__(self, phases: Optional[List[Phase]] = None):
        self.phases = phases or [Phase.from_dict(p.to_dict()) for p in IDAW_PHASES]
        self.current_phase_id = 1
        self._debug = get_debug()

        # Find current phase based on status
        for phase in self.phases:
            if phase.status == PhaseStatus.IN_PROGRESS:
                self.current_phase_id = phase.id
                break

    @trace(DebugCategory.PHASE)
    def get_current_phase(self) -> Phase:
        """Get the current active phase."""
        for phase in self.phases:
            if phase.id == self.current_phase_id:
                return phase
        return self.phases[0]

    @trace(DebugCategory.PHASE)
    def get_phase(self, phase_id: int) -> Optional[Phase]:
        """Get a specific phase by ID."""
        for phase in self.phases:
            if phase.id == phase_id:
                return phase
        return None

    @trace(DebugCategory.PHASE)
    def update_task_status(
        self,
        phase_id: int,
        task_id: str,
        status: PhaseStatus,
        progress: float = None,
        notes: str = None,
    ):
        """Update a task's status."""
        phase = self.get_phase(phase_id)
        if not phase:
            self._debug.warning(
                DebugCategory.PHASE,
                f"Phase {phase_id} not found"
            )
            return

        for task in phase.tasks:
            if task.id == task_id:
                task.status = status
                if progress is not None:
                    task.progress = progress
                if notes:
                    task.notes = notes

                if status == PhaseStatus.COMPLETED:
                    task.completed_at = datetime.now().isoformat()
                    task.progress = 1.0

                self._debug.info(
                    DebugCategory.TASK,
                    f"Updated task {task_id} to {status.value}",
                    data={"phase": phase_id, "task": task_id, "status": status.value}
                )

                # Update phase progress
                phase.update_progress()
                break

    @trace(DebugCategory.PHASE)
    def assign_task(
        self,
        phase_id: int,
        task_id: str,
        agent: AIAgent,
    ):
        """Assign a task to an AI agent."""
        phase = self.get_phase(phase_id)
        if not phase:
            return

        for task in phase.tasks:
            if task.id == task_id:
                task.assigned_to = agent
                if task.status == PhaseStatus.NOT_STARTED:
                    task.status = PhaseStatus.IN_PROGRESS

                self._debug.info(
                    DebugCategory.TASK,
                    f"Assigned task {task_id} to {agent.value}",
                    agent=agent.value,
                )
                break

    @trace(DebugCategory.PHASE)
    def advance_phase(self) -> bool:
        """Advance to the next phase if current is complete."""
        current = self.get_current_phase()

        if current.progress < 1.0:
            self._debug.warning(
                DebugCategory.PHASE,
                f"Cannot advance: Phase {current.id} is {current.progress:.0%} complete"
            )
            return False

        # Find next phase
        next_phase_id = current.id + 1
        next_phase = self.get_phase(next_phase_id)

        if not next_phase:
            self._debug.info(
                DebugCategory.PHASE,
                "All phases completed!"
            )
            return False

        # Mark current as verified, next as in progress
        current.status = PhaseStatus.VERIFIED
        next_phase.status = PhaseStatus.IN_PROGRESS
        next_phase.start_date = datetime.now().isoformat()
        self.current_phase_id = next_phase_id

        self._debug.info(
            DebugCategory.PHASE,
            f"Advanced to Phase {next_phase_id}: {next_phase.name}"
        )
        return True

    def get_incomplete_tasks(self, phase_id: Optional[int] = None) -> List[PhaseTask]:
        """Get all incomplete tasks, optionally filtered by phase."""
        tasks = []
        phases_to_check = [self.get_phase(phase_id)] if phase_id else self.phases

        for phase in phases_to_check:
            if phase:
                for task in phase.tasks:
                    if task.status not in (PhaseStatus.COMPLETED, PhaseStatus.VERIFIED):
                        tasks.append(task)
        return tasks

    def get_blocked_tasks(self) -> List[PhaseTask]:
        """Get all blocked tasks."""
        blocked = []
        for phase in self.phases:
            for task in phase.tasks:
                if task.status == PhaseStatus.BLOCKED or task.blockers:
                    blocked.append(task)
        return blocked

    def get_phase_summary(self, phase_id: Optional[int] = None) -> Dict:
        """Get a summary of phase progress."""
        if phase_id:
            phases = [self.get_phase(phase_id)]
        else:
            phases = self.phases

        summaries = []
        for phase in phases:
            if not phase:
                continue

            completed = sum(1 for t in phase.tasks if t.status == PhaseStatus.COMPLETED)
            in_progress = sum(1 for t in phase.tasks if t.status == PhaseStatus.IN_PROGRESS)
            blocked = sum(1 for t in phase.tasks if t.status == PhaseStatus.BLOCKED)

            summaries.append({
                "phase_id": phase.id,
                "name": phase.name,
                "status": phase.status.value,
                "progress": phase.progress,
                "tasks_total": len(phase.tasks),
                "tasks_completed": completed,
                "tasks_in_progress": in_progress,
                "tasks_blocked": blocked,
                "milestones": phase.milestones,
                "deliverables": phase.deliverables,
            })

        return {
            "current_phase": self.current_phase_id,
            "phases": summaries,
            "overall_progress": sum(p.progress for p in self.phases) / len(self.phases),
        }

    def to_dict(self) -> Dict:
        """Serialize manager state."""
        return {
            "phases": [p.to_dict() for p in self.phases],
            "current_phase_id": self.current_phase_id,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "PhaseManager":
        """Deserialize manager state."""
        phases = [Phase.from_dict(p) for p in data.get("phases", [])]
        manager = cls(phases=phases)
        manager.current_phase_id = data.get("current_phase_id", 1)
        return manager


# =============================================================================
# Phase Progress Visualization
# =============================================================================

def format_phase_progress(manager: PhaseManager) -> str:
    """Format phase progress for display."""
    lines = [
        "=" * 60,
        "iDAW PROJECT PROGRESS",
        "=" * 60,
        "",
    ]

    for phase in manager.phases:
        # Phase header
        status_icon = {
            PhaseStatus.NOT_STARTED: "○",
            PhaseStatus.IN_PROGRESS: "◐",
            PhaseStatus.BLOCKED: "✗",
            PhaseStatus.COMPLETED: "●",
            PhaseStatus.VERIFIED: "✓",
        }.get(phase.status, "?")

        progress_bar = "█" * int(phase.progress * 20) + "░" * (20 - int(phase.progress * 20))

        lines.append(f"{status_icon} Phase {phase.id}: {phase.name}")
        lines.append(f"  [{progress_bar}] {phase.progress:.0%}")
        lines.append(f"  {phase.description[:60]}...")
        lines.append("")

        # Tasks
        for task in phase.tasks:
            task_icon = {
                PhaseStatus.NOT_STARTED: "  ○",
                PhaseStatus.IN_PROGRESS: "  ◐",
                PhaseStatus.BLOCKED: "  ✗",
                PhaseStatus.COMPLETED: "  ●",
                PhaseStatus.VERIFIED: "  ✓",
            }.get(task.status, "  ?")

            assigned = f" [{task.assigned_to.value}]" if task.assigned_to else ""
            lines.append(f"  {task_icon} {task.name}{assigned}")

        lines.append("")

    summary = manager.get_phase_summary()
    lines.append(f"Overall Progress: {summary['overall_progress']:.0%}")

    return "\n".join(lines)


def get_next_actions(manager: PhaseManager) -> List[str]:
    """Get recommended next actions."""
    actions = []
    current = manager.get_current_phase()

    # Check for blocked tasks
    blocked = manager.get_blocked_tasks()
    if blocked:
        for task in blocked:
            actions.append(f"UNBLOCK: {task.name} - {', '.join(task.blockers)}")

    # Get in-progress tasks
    in_progress = [t for t in current.tasks if t.status == PhaseStatus.IN_PROGRESS]
    for task in in_progress:
        if task.progress < 1.0:
            actions.append(f"CONTINUE: {task.name} ({task.progress:.0%} complete)")

    # Get not-started tasks
    not_started = [t for t in current.tasks if t.status == PhaseStatus.NOT_STARTED]
    for task in not_started[:3]:  # Top 3
        actions.append(f"START: {task.name}")

    # Check phase completion
    if current.progress >= 1.0:
        actions.insert(0, f"READY: Advance to Phase {current.id + 1}")

    return actions
