"""
MCP Coordinator
===============

Manages AI agent coordination, approval workflows, and task routing.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
import time


class ApprovalStatus(Enum):
    """Status of a task/proposal approval."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"


@dataclass
class CoordinatorConfig:
    """Configuration for the MCP Coordinator."""
    auto_approve_threshold: float = 0.8  # Confidence threshold for auto-approval
    require_user_vote: bool = True
    enable_specialty_voting: bool = True
    specialty_vote_weight: float = 1.5  # Weight for votes from relevant specialists
    notification_hooks: List[Callable] = field(default_factory=list)


@dataclass
class TaskRequest:
    """A request for an AI agent task."""
    task_id: str
    capability: str
    description: str
    context: Dict[str, Any]
    priority: int = 5
    timestamp: float = field(default_factory=time.time)
    status: ApprovalStatus = ApprovalStatus.PENDING
    assigned_agent: Optional[str] = None


@dataclass
class VoteRecord:
    """Record of a vote on a task/proposal."""
    voter_id: str
    vote: int  # -1, 0, or 1
    weight: float = 1.0
    comment: str = ""
    timestamp: float = field(default_factory=time.time)


class MCPCoordinator:
    """
    Coordinates AI agents and manages approval workflows.

    Features:
    - Auto-approval based on confidence thresholds
    - User voting with weighted specialty-based votes
    - Notification hooks for webhooks and callbacks
    """

    def __init__(self, config: Optional[CoordinatorConfig] = None):
        self.config = config or CoordinatorConfig()
        self.tasks: Dict[str, TaskRequest] = {}
        self.votes: Dict[str, List[VoteRecord]] = {}
        self._task_counter = 0

    def submit_task(
        self,
        capability: str,
        description: str,
        context: Optional[Dict[str, Any]] = None,
        priority: int = 5,
    ) -> str:
        """
        Submit a new task request.

        Returns:
            Task ID for tracking
        """
        self._task_counter += 1
        task_id = f"task-{self._task_counter:04d}"

        task = TaskRequest(
            task_id=task_id,
            capability=capability,
            description=description,
            context=context or {},
            priority=priority,
        )

        self.tasks[task_id] = task
        self.votes[task_id] = []

        # Check for auto-approval
        self._check_auto_approval(task)

        # Notify hooks
        self._notify("task_submitted", task)

        return task_id

    def vote(
        self,
        task_id: str,
        voter_id: str,
        vote: int,
        is_specialist: bool = False,
        comment: str = "",
    ) -> bool:
        """
        Cast a vote on a task.

        Args:
            task_id: The task to vote on
            voter_id: ID of the voter
            vote: -1 (reject), 0 (neutral), or 1 (approve)
            is_specialist: Whether voter is a specialist for this task
            comment: Optional comment

        Returns:
            True if vote was recorded
        """
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        if task.status != ApprovalStatus.PENDING:
            return False

        weight = self.config.specialty_vote_weight if is_specialist else 1.0

        vote_record = VoteRecord(
            voter_id=voter_id,
            vote=vote,
            weight=weight,
            comment=comment,
        )

        self.votes[task_id].append(vote_record)

        # Check if we should finalize
        self._evaluate_votes(task)

        return True

    def get_task_status(self, task_id: str) -> Optional[ApprovalStatus]:
        """Get the status of a task."""
        task = self.tasks.get(task_id)
        return task.status if task else None

    def get_pending_tasks(self) -> List[TaskRequest]:
        """Get all pending tasks."""
        return [
            t for t in self.tasks.values()
            if t.status == ApprovalStatus.PENDING
        ]

    def get_vote_score(self, task_id: str) -> float:
        """Calculate the weighted vote score for a task."""
        votes = self.votes.get(task_id, [])
        if not votes:
            return 0.0

        total_weight = sum(v.weight for v in votes)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(v.vote * v.weight for v in votes)
        return weighted_sum / total_weight

    def _check_auto_approval(self, task: TaskRequest) -> None:
        """Check if task should be auto-approved."""
        # Auto-approval based on confidence in context
        confidence = task.context.get("confidence", 0.0)

        if confidence >= self.config.auto_approve_threshold:
            if not self.config.require_user_vote:
                task.status = ApprovalStatus.AUTO_APPROVED
                self._notify("task_auto_approved", task)

    def _evaluate_votes(self, task: TaskRequest) -> None:
        """Evaluate votes and potentially finalize the task."""
        score = self.get_vote_score(task.task_id)
        vote_count = len(self.votes[task.task_id])

        # Simple threshold-based decision (can be made more sophisticated)
        if vote_count >= 2:  # Minimum votes required
            if score >= 0.5:
                task.status = ApprovalStatus.APPROVED
                self._notify("task_approved", task)
            elif score <= -0.5:
                task.status = ApprovalStatus.REJECTED
                self._notify("task_rejected", task)

    def _notify(self, event_type: str, task: TaskRequest) -> None:
        """Send notifications to registered hooks."""
        for hook in self.config.notification_hooks:
            try:
                hook(event_type, task)
            except Exception:
                pass  # Don't let hook failures break the coordinator

    def to_dict(self) -> Dict[str, Any]:
        """Serialize coordinator state."""
        return {
            "tasks": {
                tid: {
                    "task_id": t.task_id,
                    "capability": t.capability,
                    "description": t.description,
                    "context": t.context,
                    "priority": t.priority,
                    "status": t.status.value,
                    "assigned_agent": t.assigned_agent,
                }
                for tid, t in self.tasks.items()
            },
            "votes": {
                tid: [
                    {
                        "voter_id": v.voter_id,
                        "vote": v.vote,
                        "weight": v.weight,
                        "comment": v.comment,
                    }
                    for v in votes
                ]
                for tid, votes in self.votes.items()
            },
        }
