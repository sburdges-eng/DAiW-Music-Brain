"""
MCP Repos - Repository Manager

Central manager for connecting to and managing sburdges-eng repositories.
"""

import json
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from .models import (
    Repository, RepoStatus, SyncStatus, RepoConnection,
    CrossRepoTask, RepoManagerState,
)


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_STORAGE_PATH = Path.home() / ".mcp_repos"
STATE_FILE = "repos_state.json"

# sburdges-eng repositories
SBURDGES_REPOS = {
    "DAiW-Music-Brain": {
        "full_name": "sburdges-eng/DAiW-Music-Brain",
        "description": "Digital Audio intelligent Workstation - Music production intelligence toolkit",
        "topics": ["music", "daw", "midi", "audio", "python"],
        "default_branch": "main",
    },
    "BEO-Master": {
        "full_name": "sburdges-eng/BEO-Master",
        "description": "Customized banquet event list management system",
        "topics": ["events", "banquet", "management"],
        "default_branch": "main",
    },
    "lariat-bible": {
        "full_name": "sburdges-eng/lariat-bible",
        "description": "Inclusive Order of Operations reference",
        "topics": ["reference", "documentation", "operations"],
        "default_branch": "main",
    },
}


# =============================================================================
# Repository Manager
# =============================================================================

class RepoManager:
    """
    Central manager for sburdges-eng repository connections.

    Features:
    - Connect to all sburdges-eng repositories
    - Track sync status across repos
    - Manage cross-repo tasks
    - Coordinate multi-repo operations
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

        # Initialize repositories
        self.repositories: Dict[str, Repository] = {}
        self.connections: Dict[str, RepoConnection] = {}
        self.cross_repo_tasks: List[CrossRepoTask] = []

        # Session info
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.created_at = datetime.now().isoformat()

        # Initialize with known repos
        self._init_known_repos()

        # Load existing state if available
        if auto_load:
            self._load_state()

    def _init_known_repos(self):
        """Initialize with known sburdges-eng repositories."""
        for name, info in SBURDGES_REPOS.items():
            if name not in self.repositories:
                self.repositories[name] = Repository(
                    name=name,
                    full_name=info["full_name"],
                    description=info["description"],
                    topics=info["topics"],
                    default_branch=info.get("default_branch", "main"),
                )

    # =========================================================================
    # Connection Operations
    # =========================================================================

    def connect_repo(self, repo_name: str, local_path: Optional[str] = None) -> Optional[RepoConnection]:
        """
        Connect to a repository.

        Args:
            repo_name: Name of the repository (e.g., 'DAiW-Music-Brain')
            local_path: Optional local path if already cloned

        Returns:
            RepoConnection if successful, None otherwise
        """
        if repo_name not in self.repositories:
            return None

        repo = self.repositories[repo_name]
        repo.status = RepoStatus.CONNECTING

        # Try to find or use local path
        if local_path:
            repo.local_path = local_path
        elif repo_name == "DAiW-Music-Brain":
            # Current repository
            repo.local_path = str(Path.cwd())

        # Create connection
        connection = RepoConnection(
            id=f"conn_{repo_name}_{self.session_id}",
            repository=repo,
            current_branch=self._get_current_branch(repo.local_path) if repo.local_path else "",
        )

        # Update status
        if repo.local_path and Path(repo.local_path).exists():
            repo.status = RepoStatus.CONNECTED
            repo.sync_status = self._check_sync_status(repo.local_path)
            repo.last_synced = datetime.now().isoformat()

            # Get additional info
            connection.uncommitted_changes = self._count_uncommitted(repo.local_path)
            connection.ahead_by, connection.behind_by = self._get_ahead_behind(repo.local_path)
        else:
            repo.status = RepoStatus.DISCONNECTED

        self.connections[repo_name] = connection
        self._save_state()

        return connection

    def connect_all(self) -> Dict[str, RepoConnection]:
        """Connect to all sburdges-eng repositories."""
        results = {}
        for repo_name in self.repositories:
            conn = self.connect_repo(repo_name)
            if conn:
                results[repo_name] = conn
        return results

    def disconnect_repo(self, repo_name: str) -> bool:
        """Disconnect from a repository."""
        if repo_name in self.connections:
            del self.connections[repo_name]
            if repo_name in self.repositories:
                self.repositories[repo_name].status = RepoStatus.DISCONNECTED
            self._save_state()
            return True
        return False

    # =========================================================================
    # Repository Status
    # =========================================================================

    def get_repo_status(self, repo_name: str) -> Optional[Dict]:
        """Get detailed status for a repository."""
        if repo_name not in self.repositories:
            return None

        repo = self.repositories[repo_name]
        conn = self.connections.get(repo_name)

        return {
            "repository": repo.to_dict(),
            "connection": conn.to_dict() if conn else None,
            "is_connected": repo.status == RepoStatus.CONNECTED,
        }

    def get_all_status(self) -> Dict[str, Dict]:
        """Get status for all repositories."""
        return {
            name: self.get_repo_status(name)
            for name in self.repositories
        }

    def list_connected(self) -> List[str]:
        """List all connected repositories."""
        return [
            name for name, repo in self.repositories.items()
            if repo.status == RepoStatus.CONNECTED
        ]

    def list_all(self) -> List[Dict]:
        """List all known repositories."""
        return [repo.to_dict() for repo in self.repositories.values()]

    # =========================================================================
    # Cross-Repo Tasks
    # =========================================================================

    def create_cross_repo_task(
        self,
        title: str,
        description: str,
        repos: List[str],
        priority: int = 5,
        assigned_to: Optional[str] = None,
    ) -> CrossRepoTask:
        """Create a task spanning multiple repositories."""
        task = CrossRepoTask(
            id="",
            title=title,
            description=description,
            repos=repos,
            priority=priority,
            assigned_to=assigned_to,
        )
        self.cross_repo_tasks.append(task)
        self._save_state()
        return task

    def get_cross_repo_tasks(self, repo_name: Optional[str] = None) -> List[CrossRepoTask]:
        """Get cross-repo tasks, optionally filtered by repository."""
        if repo_name:
            return [t for t in self.cross_repo_tasks if repo_name in t.repos]
        return self.cross_repo_tasks

    def update_task_status(self, task_id: str, status: str) -> bool:
        """Update status of a cross-repo task."""
        for task in self.cross_repo_tasks:
            if task.id == task_id:
                task.status = status
                task.updated_at = datetime.now().isoformat()
                self._save_state()
                return True
        return False

    # =========================================================================
    # Git Operations (Helpers)
    # =========================================================================

    def _get_current_branch(self, path: str) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=path, capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""

    def _check_sync_status(self, path: str) -> SyncStatus:
        """Check sync status with remote."""
        try:
            # Fetch to update remote refs
            subprocess.run(
                ["git", "fetch", "--quiet"],
                cwd=path, capture_output=True, timeout=30
            )

            # Check ahead/behind
            result = subprocess.run(
                ["git", "status", "-sb"],
                cwd=path, capture_output=True, text=True, timeout=10
            )
            output = result.stdout

            if "ahead" in output and "behind" in output:
                return SyncStatus.DIVERGED
            elif "ahead" in output:
                return SyncStatus.AHEAD
            elif "behind" in output:
                return SyncStatus.BEHIND
            else:
                return SyncStatus.UP_TO_DATE
        except Exception:
            return SyncStatus.UNKNOWN

    def _count_uncommitted(self, path: str) -> int:
        """Count uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=path, capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                lines = [l for l in result.stdout.strip().split('\n') if l]
                return len(lines)
            return 0
        except Exception:
            return 0

    def _get_ahead_behind(self, path: str) -> tuple:
        """Get ahead/behind counts."""
        try:
            result = subprocess.run(
                ["git", "rev-list", "--left-right", "--count", "HEAD...@{upstream}"],
                cwd=path, capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split()
                if len(parts) == 2:
                    return int(parts[0]), int(parts[1])
            return 0, 0
        except Exception:
            return 0, 0

    # =========================================================================
    # Dashboard
    # =========================================================================

    def get_dashboard(self) -> str:
        """Get formatted dashboard view."""
        lines = [
            "=" * 70,
            "MCP REPOS - sburdges-eng Repository Dashboard",
            "=" * 70,
            "",
            f"Session: {self.session_id}",
            f"Total Repositories: {len(self.repositories)}",
            f"Connected: {len(self.list_connected())}",
            "",
            "REPOSITORIES:",
        ]

        for name, repo in self.repositories.items():
            status_icon = {
                RepoStatus.CONNECTED: "[OK]",
                RepoStatus.DISCONNECTED: "[--]",
                RepoStatus.CONNECTING: "[..]",
                RepoStatus.SYNCING: "[~~]",
                RepoStatus.ERROR: "[!!]",
            }.get(repo.status, "[??]")

            sync_icon = {
                SyncStatus.UP_TO_DATE: "",
                SyncStatus.AHEAD: " (ahead)",
                SyncStatus.BEHIND: " (behind)",
                SyncStatus.DIVERGED: " (diverged)",
                SyncStatus.UNKNOWN: "",
            }.get(repo.sync_status, "")

            lines.append(f"  {status_icon} {repo.full_name}{sync_icon}")
            if repo.description:
                lines.append(f"      {repo.description[:50]}...")

        lines.append("")

        # Cross-repo tasks
        if self.cross_repo_tasks:
            lines.extend([
                "CROSS-REPO TASKS:",
                *[f"  - [{t.status}] {t.title} ({', '.join(t.repos)})"
                  for t in self.cross_repo_tasks[:5]],
            ])

        return "\n".join(lines)

    # =========================================================================
    # Persistence
    # =========================================================================

    def _save_state(self):
        """Save state to disk."""
        state = {
            "repositories": {k: v.to_dict() for k, v in self.repositories.items()},
            "connections": {k: v.to_dict() for k, v in self.connections.items()},
            "cross_repo_tasks": [t.to_dict() for t in self.cross_repo_tasks],
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": datetime.now().isoformat(),
        }

        state_file = self.storage_path / STATE_FILE
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _load_state(self):
        """Load state from disk."""
        state_file = self.storage_path / STATE_FILE

        if not state_file.exists():
            return

        try:
            with open(state_file, 'r') as f:
                state = json.load(f)

            # Restore repositories (merge with known repos)
            for name, data in state.get("repositories", {}).items():
                self.repositories[name] = Repository.from_dict(data)

            # Restore cross-repo tasks
            self.cross_repo_tasks = [
                CrossRepoTask.from_dict(t)
                for t in state.get("cross_repo_tasks", [])
            ]

        except Exception:
            pass  # Start fresh if load fails

    def reset(self):
        """Reset to initial state."""
        self.repositories = {}
        self.connections = {}
        self.cross_repo_tasks = []
        self._init_known_repos()
        self._save_state()


# =============================================================================
# Global Functions
# =============================================================================

_manager: Optional[RepoManager] = None


def get_repo_manager() -> RepoManager:
    """Get the global repository manager instance."""
    global _manager
    if _manager is None:
        _manager = RepoManager()
    return _manager


def shutdown_repo_manager():
    """Shutdown the repository manager."""
    global _manager
    if _manager:
        _manager._save_state()
        _manager = None
