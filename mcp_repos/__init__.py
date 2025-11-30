"""
MCP Repos - Multi-Repository Connection System

Connect to and manage all sburdges-eng repositories from a single workstation.
"""

from .models import Repository, RepoStatus, RepoConnection
from .manager import RepoManager, get_repo_manager
from .server import run_server

__version__ = "0.1.0"

__all__ = [
    "Repository",
    "RepoStatus",
    "RepoConnection",
    "RepoManager",
    "get_repo_manager",
    "run_server",
]

# sburdges-eng repositories
SBURDGES_REPOS = {
    "DAiW-Music-Brain": {
        "full_name": "sburdges-eng/DAiW-Music-Brain",
        "description": "Digital Audio intelligent Workstation - Music production intelligence toolkit",
        "topics": ["music", "daw", "midi", "audio", "python"],
    },
    "BEO-Master": {
        "full_name": "sburdges-eng/BEO-Master",
        "description": "Customized banquet event list management system",
        "topics": ["events", "banquet", "management"],
    },
    "lariat-bible": {
        "full_name": "sburdges-eng/lariat-bible",
        "description": "Inclusive Order of Operations reference",
        "topics": ["reference", "documentation", "operations"],
    },
}
