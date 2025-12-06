"""
Dual Engine System
==================

Implements the dual-mode creative engine for DAiW:
- Work State (Side A): Focused, structured production
- Dream State (Side B): Experimental, free-form exploration

This mirrors the philosophy of having both analytical and intuitive
modes available during the creative process.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
import time


class EngineMode(Enum):
    """The two primary engine modes."""
    WORK = "work"     # Side A: Focused, structured
    DREAM = "dream"   # Side B: Experimental, exploratory


@dataclass
class EngineState:
    """Base state for engine modes."""
    mode: EngineMode
    active: bool = True
    start_time: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Time spent in this state."""
        return time.time() - self.start_time


@dataclass
class WorkState(EngineState):
    """
    Work State (Side A): Iron Heap

    Characteristics:
    - Focused, goal-oriented
    - Structured approach
    - Deterministic outputs
    - Memory-efficient (monotonic allocation)
    """
    mode: EngineMode = EngineMode.WORK
    current_task: Optional[str] = None
    completed_tasks: List[str] = field(default_factory=list)
    focus_level: float = 1.0  # 0.0 to 1.0

    def start_task(self, task: str) -> None:
        """Begin a new task."""
        self.current_task = task

    def complete_task(self) -> None:
        """Mark current task as complete."""
        if self.current_task:
            self.completed_tasks.append(self.current_task)
            self.current_task = None


@dataclass
class DreamState(EngineState):
    """
    Dream State (Side B): Playground

    Characteristics:
    - Exploratory, open-ended
    - Non-linear approach
    - Probabilistic outputs
    - Thread-safe for parallel exploration
    """
    mode: EngineMode = EngineMode.DREAM
    exploration_depth: int = 0
    discovered_ideas: List[str] = field(default_factory=list)
    chaos_level: float = 0.5  # 0.0 to 1.0

    def explore(self, idea: str) -> None:
        """Record a discovered idea."""
        self.discovered_ideas.append(idea)
        self.exploration_depth += 1


class DualEngine:
    """
    Dual Engine Controller

    Manages transitions between Work and Dream states,
    maintains context across mode switches, and provides
    the interface for the DAiW creative workflow.
    """

    def __init__(self):
        self._work_state: Optional[WorkState] = None
        self._dream_state: Optional[DreamState] = None
        self._active_mode: EngineMode = EngineMode.WORK
        self._mode_history: List[Dict[str, Any]] = []

    @property
    def current_mode(self) -> EngineMode:
        """Get the current engine mode."""
        return self._active_mode

    @property
    def in_work_mode(self) -> bool:
        """Check if in Work mode."""
        return self._active_mode == EngineMode.WORK

    @property
    def in_dream_mode(self) -> bool:
        """Check if in Dream mode."""
        return self._active_mode == EngineMode.DREAM

    def enter_work_mode(self, context: Optional[Dict[str, Any]] = None) -> WorkState:
        """
        Enter Work State (Side A).

        This is the focused, structured mode for production work.
        """
        if self._dream_state and self._dream_state.active:
            self._archive_state(self._dream_state)
            self._dream_state.active = False

        self._work_state = WorkState(context=context or {})
        self._active_mode = EngineMode.WORK

        return self._work_state

    def enter_dream_mode(
        self,
        context: Optional[Dict[str, Any]] = None,
        chaos_level: float = 0.5,
    ) -> DreamState:
        """
        Enter Dream State (Side B).

        This is the experimental, exploratory mode for creative discovery.
        """
        if self._work_state and self._work_state.active:
            self._archive_state(self._work_state)
            self._work_state.active = False

        self._dream_state = DreamState(
            context=context or {},
            chaos_level=chaos_level,
        )
        self._active_mode = EngineMode.DREAM

        return self._dream_state

    def toggle_mode(self) -> EngineState:
        """Toggle between Work and Dream modes."""
        if self._active_mode == EngineMode.WORK:
            return self.enter_dream_mode()
        else:
            return self.enter_work_mode()

    def get_work_state(self) -> Optional[WorkState]:
        """Get the current work state if in work mode."""
        return self._work_state if self.in_work_mode else None

    def get_dream_state(self) -> Optional[DreamState]:
        """Get the current dream state if in dream mode."""
        return self._dream_state if self.in_dream_mode else None

    def _archive_state(self, state: EngineState) -> None:
        """Archive a state for history."""
        self._mode_history.append({
            "mode": state.mode.value,
            "duration": state.duration,
            "context": state.context,
            "archived_at": time.time(),
        })

    def get_history(self) -> List[Dict[str, Any]]:
        """Get the mode transition history."""
        return self._mode_history.copy()

    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        work_time = sum(
            h["duration"] for h in self._mode_history
            if h["mode"] == EngineMode.WORK.value
        )
        dream_time = sum(
            h["duration"] for h in self._mode_history
            if h["mode"] == EngineMode.DREAM.value
        )

        return {
            "current_mode": self._active_mode.value,
            "total_work_time": work_time,
            "total_dream_time": dream_time,
            "mode_switches": len(self._mode_history),
            "work_tasks_completed": (
                len(self._work_state.completed_tasks)
                if self._work_state else 0
            ),
            "ideas_discovered": (
                len(self._dream_state.discovered_ideas)
                if self._dream_state else 0
            ),
        }
