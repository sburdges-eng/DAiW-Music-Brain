"""
TODO Data Models

Defines the core data structures for task management.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
import uuid


class TodoPriority(str, Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TodoStatus(str, Enum):
    """Status states for tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass
class Todo:
    """
    A single TODO item with full metadata.

    Designed to be compatible across AI assistants with rich context.
    """
    title: str
    description: str = ""
    status: TodoStatus = TodoStatus.PENDING
    priority: TodoPriority = TodoPriority.MEDIUM

    # Unique identifier
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    due_date: Optional[str] = None

    # Organization
    tags: List[str] = field(default_factory=list)
    project: Optional[str] = None
    parent_id: Optional[str] = None  # For subtasks

    # Context for AI assistants
    context: str = ""  # Additional context about the task
    ai_source: Optional[str] = None  # Which AI created/modified this
    notes: List[str] = field(default_factory=list)

    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # IDs of blocking tasks
    blocks: List[str] = field(default_factory=list)  # IDs of tasks this blocks

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["status"] = self.status.value
        data["priority"] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Todo":
        """Create from dictionary."""
        # Handle enum conversion
        if isinstance(data.get("status"), str):
            data["status"] = TodoStatus(data["status"])
        if isinstance(data.get("priority"), str):
            data["priority"] = TodoPriority(data["priority"])
        return cls(**data)

    def mark_complete(self, ai_source: Optional[str] = None) -> None:
        """Mark the task as completed."""
        self.status = TodoStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        if ai_source:
            self.ai_source = ai_source
            self.notes.append(f"Completed by {ai_source} at {self.completed_at}")

    def mark_in_progress(self, ai_source: Optional[str] = None) -> None:
        """Mark the task as in progress."""
        self.status = TodoStatus.IN_PROGRESS
        self.updated_at = datetime.now().isoformat()
        if ai_source:
            self.ai_source = ai_source
            self.notes.append(f"Started by {ai_source} at {self.updated_at}")

    def add_note(self, note: str, ai_source: Optional[str] = None) -> None:
        """Add a note to the task."""
        timestamp = datetime.now().isoformat()
        prefix = f"[{ai_source}] " if ai_source else ""
        self.notes.append(f"{prefix}{timestamp}: {note}")
        self.updated_at = timestamp

    def __str__(self) -> str:
        status_icons = {
            TodoStatus.PENDING: "[ ]",
            TodoStatus.IN_PROGRESS: "[~]",
            TodoStatus.COMPLETED: "[x]",
            TodoStatus.BLOCKED: "[!]",
            TodoStatus.CANCELLED: "[-]",
        }
        priority_icons = {
            TodoPriority.LOW: "",
            TodoPriority.MEDIUM: "*",
            TodoPriority.HIGH: "**",
            TodoPriority.URGENT: "!!!",
        }
        icon = status_icons.get(self.status, "[ ]")
        pri = priority_icons.get(self.priority, "")
        return f"{icon} {pri}{self.title} ({self.id})"


@dataclass
class TodoList:
    """A collection of todos, optionally grouped by project."""
    name: str = "default"
    todos: List[Todo] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "todos": [t.to_dict() for t in self.todos],
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TodoList":
        todos = [Todo.from_dict(t) for t in data.get("todos", [])]
        return cls(
            name=data.get("name", "default"),
            todos=todos,
            created_at=data.get("created_at", datetime.now().isoformat()),
        )
