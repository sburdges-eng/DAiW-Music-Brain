"""
MCP Repos - Data Models

Defines repository connections, status, and cross-repo tasks.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import uuid


class RepoStatus(str, Enum):
    """Status of a repository connection."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    SYNCING = "syncing"
    ERROR = "error"


class SyncStatus(str, Enum):
    """Status of repository sync."""
    UP_TO_DATE = "up_to_date"
    AHEAD = "ahead"
    BEHIND = "behind"
    DIVERGED = "diverged"
    UNKNOWN = "unknown"


@dataclass
class Repository:
    """A GitHub repository in the sburdges-eng organization."""
    name: str
    full_name: str
    description: str = ""
    url: str = ""
    default_branch: str = "main"
    topics: List[str] = field(default_factory=list)
    status: RepoStatus = RepoStatus.DISCONNECTED
    sync_status: SyncStatus = SyncStatus.UNKNOWN
    local_path: Optional[str] = None
    last_synced: Optional[str] = None
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.url:
            self.url = f"https://github.com/{self.full_name}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "full_name": self.full_name,
            "description": self.description,
            "url": self.url,
            "default_branch": self.default_branch,
            "topics": self.topics,
            "status": self.status.value,
            "sync_status": self.sync_status.value,
            "local_path": self.local_path,
            "last_synced": self.last_synced,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Repository":
        return cls(
            name=data.get("name", ""),
            full_name=data.get("full_name", ""),
            description=data.get("description", ""),
            url=data.get("url", ""),
            default_branch=data.get("default_branch", "main"),
            topics=data.get("topics", []),
            status=RepoStatus(data["status"]) if data.get("status") else RepoStatus.DISCONNECTED,
            sync_status=SyncStatus(data["sync_status"]) if data.get("sync_status") else SyncStatus.UNKNOWN,
            local_path=data.get("local_path"),
            last_synced=data.get("last_synced"),
            created_at=data.get("created_at", ""),
        )


@dataclass
class RepoConnection:
    """Active connection to a repository."""
    id: str
    repository: Repository
    connected_at: str = ""
    current_branch: str = ""
    uncommitted_changes: int = 0
    ahead_by: int = 0
    behind_by: int = 0

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.connected_at:
            self.connected_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "repository": self.repository.to_dict(),
            "connected_at": self.connected_at,
            "current_branch": self.current_branch,
            "uncommitted_changes": self.uncommitted_changes,
            "ahead_by": self.ahead_by,
            "behind_by": self.behind_by,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepoConnection":
        return cls(
            id=data.get("id", ""),
            repository=Repository.from_dict(data["repository"]) if data.get("repository") else Repository("", ""),
            connected_at=data.get("connected_at", ""),
            current_branch=data.get("current_branch", ""),
            uncommitted_changes=data.get("uncommitted_changes", 0),
            ahead_by=data.get("ahead_by", 0),
            behind_by=data.get("behind_by", 0),
        )


@dataclass
class CrossRepoTask:
    """A task that spans multiple repositories."""
    id: str
    title: str
    description: str
    repos: List[str]  # Repository names involved
    status: str = "pending"
    priority: int = 5
    assigned_to: Optional[str] = None  # AI agent or human
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
            "title": self.title,
            "description": self.description,
            "repos": self.repos,
            "status": self.status,
            "priority": self.priority,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrossRepoTask":
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            repos=data.get("repos", []),
            status=data.get("status", "pending"),
            priority=data.get("priority", 5),
            assigned_to=data.get("assigned_to"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )


@dataclass
class RepoManagerState:
    """Complete state for the repository manager."""
    repositories: Dict[str, Repository] = field(default_factory=dict)
    connections: Dict[str, RepoConnection] = field(default_factory=dict)
    cross_repo_tasks: List[CrossRepoTask] = field(default_factory=list)
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
            "repositories": {k: v.to_dict() for k, v in self.repositories.items()},
            "connections": {k: v.to_dict() for k, v in self.connections.items()},
            "cross_repo_tasks": [t.to_dict() for t in self.cross_repo_tasks],
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepoManagerState":
        return cls(
            repositories={k: Repository.from_dict(v) for k, v in data.get("repositories", {}).items()},
            connections={k: RepoConnection.from_dict(v) for k, v in data.get("connections", {}).items()},
            cross_repo_tasks=[CrossRepoTask.from_dict(t) for t in data.get("cross_repo_tasks", [])],
            session_id=data.get("session_id", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    def save(self, path: str):
        """Save state to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "RepoManagerState":
        """Load state from JSON file."""
        with open(path, 'r') as f:
            return cls.from_dict(json.load(f))
