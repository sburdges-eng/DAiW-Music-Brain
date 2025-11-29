"""
TODO Storage Backend

JSON file-based storage for cross-AI task persistence.
Supports multiple projects and concurrent access patterns.
"""

import json
import os
import fcntl
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import Todo, TodoStatus, TodoPriority, TodoList


class TodoStorage:
    """
    File-based TODO storage with JSON persistence.

    Features:
    - Multi-project support
    - File locking for concurrent access
    - Automatic backup on write
    - Query/filter capabilities
    """

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize storage.

        Args:
            storage_dir: Directory for TODO files. Defaults to ~/.mcp_todo/
        """
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path.home() / ".mcp_todo"

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.default_file = self.storage_dir / "todos.json"

        # Initialize default file if needed
        if not self.default_file.exists():
            self._save_data({"lists": {"default": {"name": "default", "todos": []}}})

    def _get_file_path(self, project: Optional[str] = None) -> Path:
        """Get file path for a project."""
        if project and project != "default":
            return self.storage_dir / f"todos_{project}.json"
        return self.default_file

    def _load_data(self, project: Optional[str] = None) -> Dict[str, Any]:
        """Load data with file locking."""
        file_path = self._get_file_path(project)

        if not file_path.exists():
            return {"lists": {"default": {"name": "default", "todos": []}}}

        with open(file_path, "r") as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return data

    def _save_data(self, data: Dict[str, Any], project: Optional[str] = None) -> None:
        """Save data with file locking and backup."""
        file_path = self._get_file_path(project)

        # Create backup if file exists
        if file_path.exists():
            backup_path = file_path.with_suffix(".json.bak")
            with open(file_path, "r") as src:
                with open(backup_path, "w") as dst:
                    dst.write(src.read())

        # Write with lock
        with open(file_path, "w") as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                json.dump(data, f, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    # CRUD Operations

    def add(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        project: Optional[str] = None,
        due_date: Optional[str] = None,
        context: str = "",
        ai_source: Optional[str] = None,
    ) -> Todo:
        """
        Add a new TODO.

        Args:
            title: Task title
            description: Detailed description
            priority: low/medium/high/urgent
            tags: List of tags for organization
            project: Project name for grouping
            due_date: ISO format date string
            context: Additional context for AI assistants
            ai_source: Which AI created this task

        Returns:
            The created Todo object
        """
        todo = Todo(
            title=title,
            description=description,
            priority=TodoPriority(priority) if isinstance(priority, str) else priority,
            tags=tags or [],
            project=project or "default",
            due_date=due_date,
            context=context,
            ai_source=ai_source,
        )

        data = self._load_data(project)
        list_name = project or "default"

        if "lists" not in data:
            data["lists"] = {}
        if list_name not in data["lists"]:
            data["lists"][list_name] = {"name": list_name, "todos": []}

        data["lists"][list_name]["todos"].append(todo.to_dict())
        self._save_data(data, project)

        return todo

    def get(self, todo_id: str, project: Optional[str] = None) -> Optional[Todo]:
        """Get a TODO by ID."""
        todos = self.list_all(project=project)
        for todo in todos:
            if todo.id == todo_id:
                return todo
        return None

    def update(
        self,
        todo_id: str,
        project: Optional[str] = None,
        ai_source: Optional[str] = None,
        **updates
    ) -> Optional[Todo]:
        """
        Update a TODO.

        Args:
            todo_id: ID of the TODO to update
            project: Project name
            ai_source: Which AI is making the update
            **updates: Fields to update

        Returns:
            Updated Todo or None if not found
        """
        data = self._load_data(project)
        list_name = project or "default"

        if "lists" not in data or list_name not in data["lists"]:
            return None

        todos = data["lists"][list_name]["todos"]
        for i, todo_data in enumerate(todos):
            if todo_data["id"] == todo_id:
                # Apply updates
                for key, value in updates.items():
                    if key in todo_data:
                        if key == "status" and isinstance(value, str):
                            todo_data[key] = value
                        elif key == "priority" and isinstance(value, str):
                            todo_data[key] = value
                        else:
                            todo_data[key] = value

                todo_data["updated_at"] = datetime.now().isoformat()
                if ai_source:
                    todo_data["ai_source"] = ai_source

                # Handle completion
                if updates.get("status") == "completed":
                    todo_data["completed_at"] = datetime.now().isoformat()

                data["lists"][list_name]["todos"][i] = todo_data
                self._save_data(data, project)
                return Todo.from_dict(todo_data)

        return None

    def delete(self, todo_id: str, project: Optional[str] = None) -> bool:
        """Delete a TODO by ID."""
        data = self._load_data(project)
        list_name = project or "default"

        if "lists" not in data or list_name not in data["lists"]:
            return False

        todos = data["lists"][list_name]["todos"]
        original_len = len(todos)
        data["lists"][list_name]["todos"] = [t for t in todos if t["id"] != todo_id]

        if len(data["lists"][list_name]["todos"]) < original_len:
            self._save_data(data, project)
            return True
        return False

    def complete(self, todo_id: str, project: Optional[str] = None, ai_source: Optional[str] = None) -> Optional[Todo]:
        """Mark a TODO as completed."""
        return self.update(todo_id, project=project, status="completed", ai_source=ai_source)

    def start(self, todo_id: str, project: Optional[str] = None, ai_source: Optional[str] = None) -> Optional[Todo]:
        """Mark a TODO as in progress."""
        return self.update(todo_id, project=project, status="in_progress", ai_source=ai_source)

    # Query Operations

    def list_all(
        self,
        project: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        include_completed: bool = True,
    ) -> List[Todo]:
        """
        List TODOs with optional filters.

        Args:
            project: Filter by project
            status: Filter by status (pending/in_progress/completed/blocked/cancelled)
            priority: Filter by priority (low/medium/high/urgent)
            tags: Filter by tags (any match)
            include_completed: Whether to include completed tasks

        Returns:
            List of matching Todo objects
        """
        data = self._load_data(project)

        all_todos = []
        if "lists" in data:
            for list_name, list_data in data["lists"].items():
                if project and list_name != project:
                    continue
                for todo_data in list_data.get("todos", []):
                    all_todos.append(Todo.from_dict(todo_data))

        # Apply filters
        result = []
        for todo in all_todos:
            if status and todo.status.value != status:
                continue
            if priority and todo.priority.value != priority:
                continue
            if tags and not any(t in todo.tags for t in tags):
                continue
            if not include_completed and todo.status == TodoStatus.COMPLETED:
                continue
            result.append(todo)

        return result

    def search(self, query: str, project: Optional[str] = None) -> List[Todo]:
        """Search TODOs by title or description."""
        todos = self.list_all(project=project)
        query = query.lower()
        return [
            t for t in todos
            if query in t.title.lower() or query in t.description.lower()
        ]

    def get_by_tags(self, tags: List[str], project: Optional[str] = None) -> List[Todo]:
        """Get all TODOs with any of the specified tags."""
        return self.list_all(project=project, tags=tags)

    def get_pending(self, project: Optional[str] = None) -> List[Todo]:
        """Get all pending TODOs."""
        return self.list_all(project=project, status="pending")

    def get_in_progress(self, project: Optional[str] = None) -> List[Todo]:
        """Get all in-progress TODOs."""
        return self.list_all(project=project, status="in_progress")

    def get_summary(self, project: Optional[str] = None) -> Dict[str, Any]:
        """Get a summary of TODO statistics."""
        todos = self.list_all(project=project)

        by_status = {}
        by_priority = {}

        for todo in todos:
            status = todo.status.value
            priority = todo.priority.value

            by_status[status] = by_status.get(status, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1

        return {
            "total": len(todos),
            "by_status": by_status,
            "by_priority": by_priority,
            "pending": by_status.get("pending", 0),
            "in_progress": by_status.get("in_progress", 0),
            "completed": by_status.get("completed", 0),
        }

    # Bulk Operations

    def add_subtask(
        self,
        parent_id: str,
        title: str,
        project: Optional[str] = None,
        ai_source: Optional[str] = None,
        **kwargs
    ) -> Optional[Todo]:
        """Add a subtask to an existing TODO."""
        parent = self.get(parent_id, project)
        if not parent:
            return None

        subtask = self.add(
            title=title,
            project=project,
            ai_source=ai_source,
            **kwargs
        )
        subtask.parent_id = parent_id

        # Update the subtask with parent reference
        self.update(subtask.id, project=project, parent_id=parent_id)

        return subtask

    def clear_completed(self, project: Optional[str] = None) -> int:
        """Remove all completed TODOs. Returns count removed."""
        data = self._load_data(project)
        list_name = project or "default"

        if "lists" not in data or list_name not in data["lists"]:
            return 0

        original = data["lists"][list_name]["todos"]
        filtered = [t for t in original if t.get("status") != "completed"]

        removed = len(original) - len(filtered)
        if removed > 0:
            data["lists"][list_name]["todos"] = filtered
            self._save_data(data, project)

        return removed

    def export_markdown(self, project: Optional[str] = None) -> str:
        """Export TODOs as Markdown."""
        todos = self.list_all(project=project)

        lines = [f"# TODO List - {project or 'default'}\n"]
        lines.append(f"_Generated: {datetime.now().isoformat()}_\n")

        # Group by status
        by_status = {}
        for todo in todos:
            status = todo.status.value
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(todo)

        status_order = ["in_progress", "pending", "blocked", "completed", "cancelled"]
        status_headers = {
            "in_progress": "## In Progress",
            "pending": "## Pending",
            "blocked": "## Blocked",
            "completed": "## Completed",
            "cancelled": "## Cancelled",
        }

        for status in status_order:
            if status in by_status:
                lines.append(f"\n{status_headers[status]}\n")
                for todo in by_status[status]:
                    checkbox = "x" if status == "completed" else " "
                    pri_marker = "!" * ["low", "medium", "high", "urgent"].index(todo.priority.value)
                    lines.append(f"- [{checkbox}] {pri_marker} {todo.title} `{todo.id}`")
                    if todo.description:
                        lines.append(f"  - {todo.description}")
                    if todo.tags:
                        lines.append(f"  - Tags: {', '.join(todo.tags)}")

        return "\n".join(lines)
