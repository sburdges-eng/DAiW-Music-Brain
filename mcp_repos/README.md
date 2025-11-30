# MCP Repos - Multi-Repository Connection System

Connect to and manage all **sburdges-eng** repositories from a unified interface.

## Overview

MCP Repos provides a Model Context Protocol (MCP) server and CLI for managing connections to all sburdges-eng GitHub repositories. It enables cross-repository task management and coordination between AI assistants.

## sburdges-eng Repositories

| Repository | Description |
|------------|-------------|
| [DAiW-Music-Brain](https://github.com/sburdges-eng/DAiW-Music-Brain) | Digital Audio intelligent Workstation - Music production intelligence toolkit |
| [BEO-Master](https://github.com/sburdges-eng/BEO-Master) | Customized banquet event list management system |
| [lariat-bible](https://github.com/sburdges-eng/lariat-bible) | Inclusive Order of Operations reference |

## Installation

The module is part of DAiW-Music-Brain:

```bash
cd DAiW-Music-Brain
pip install -e .
```

## Usage

### CLI Mode

```bash
# List all repositories
python -m mcp_repos list

# Connect to all repositories
python -m mcp_repos connect --all

# Connect to specific repo
python -m mcp_repos connect DAiW-Music-Brain

# Show dashboard
python -m mcp_repos dashboard

# Get repository status
python -m mcp_repos status DAiW-Music-Brain

# Create cross-repo task
python -m mcp_repos task create \
    --title "Update CI/CD pipelines" \
    --repos "DAiW-Music-Brain,BEO-Master,lariat-bible" \
    --priority 7

# List cross-repo tasks
python -m mcp_repos task list
```

### MCP Server Mode

Run as an MCP server for AI assistant integration:

```bash
python -m mcp_repos --server
```

## MCP Tools

The MCP server provides these tools:

| Tool | Description |
|------|-------------|
| `repo_connect` | Connect to a repository (or all with 'all') |
| `repo_list` | List all sburdges-eng repositories |
| `repo_status` | Get detailed status for a repository |
| `repo_dashboard` | Get formatted dashboard view |
| `repo_disconnect` | Disconnect from a repository |
| `cross_repo_task_create` | Create a task spanning multiple repos |
| `cross_repo_task_list` | List cross-repository tasks |

## Configuration

### Claude Code

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "mcp-repos": {
      "command": "python",
      "args": ["-m", "mcp_repos", "--server"],
      "env": {
        "PYTHONPATH": "/path/to/DAiW-Music-Brain"
      }
    }
  }
}
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or equivalent:

```json
{
  "mcpServers": {
    "mcp-repos": {
      "command": "python",
      "args": ["-m", "mcp_repos", "--server"],
      "env": {
        "PYTHONPATH": "/path/to/DAiW-Music-Brain"
      }
    }
  }
}
```

### Cursor

Add to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "mcp-repos": {
      "command": "python",
      "args": ["-m", "mcp_repos", "--server"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

## Cross-Repository Tasks

Track tasks that span multiple repositories:

```python
from mcp_repos import get_repo_manager

manager = get_repo_manager()

# Create cross-repo task
task = manager.create_cross_repo_task(
    title="Unified CI/CD pipeline",
    description="Set up consistent GitHub Actions across all repos",
    repos=["DAiW-Music-Brain", "BEO-Master", "lariat-bible"],
    priority=8,
)

# List tasks
tasks = manager.get_cross_repo_tasks()
```

## Storage

State is stored in `~/.mcp_repos/repos_state.json` and persists between sessions.

## Integration with MCP Workstation

MCP Repos integrates with the existing MCP Workstation for multi-AI collaboration:

```
DAiW-Music-Brain/
├── mcp_repos/          # Repository connections (this module)
├── mcp_todo/           # Cross-AI task management
├── mcp_workstation/    # Multi-AI collaboration orchestrator
```

## API Reference

### RepoManager

```python
from mcp_repos import get_repo_manager

manager = get_repo_manager()

# Connect to repositories
manager.connect_all()                    # Connect to all
manager.connect_repo("DAiW-Music-Brain") # Connect to one

# Get status
manager.get_repo_status("DAiW-Music-Brain")
manager.get_all_status()
manager.list_connected()
manager.list_all()

# Dashboard
print(manager.get_dashboard())

# Cross-repo tasks
manager.create_cross_repo_task(title, description, repos)
manager.get_cross_repo_tasks()
manager.update_task_status(task_id, "completed")
```

## License

Part of DAiW-Music-Brain. See main repository for license information.
