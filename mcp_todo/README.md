# MCP TODO - Multi-AI Task Management

A Model Context Protocol (MCP) server for managing TODOs across multiple AI assistants. Tasks created in one AI are instantly available in all others.

## Supported AI Assistants

| AI Assistant | Protocol | Status |
|-------------|----------|--------|
| **Claude** (Desktop & Code) | MCP (stdio) | Full Support |
| **Cursor** | MCP (stdio) | Full Support |
| **VSCode + Copilot** | MCP (stdio) | Full Support |
| **ChatGPT** | HTTP/OpenAPI | Full Support |
| **Gemini** | Function Calling | Full Support |
| **OpenAI API** | OpenAPI/Plugin | Full Support |

## Features

- **Cross-AI Sync**: Tasks created in Claude appear in ChatGPT, Cursor, Gemini, etc.
- **Rich Task Model**: Priority, tags, projects, due dates, notes, subtasks
- **File-based Storage**: JSON storage at `~/.mcp_todo/todos.json`
- **CLI Tool**: Manage tasks from the command line
- **HTTP API**: REST API for HTTP-based integrations

## Quick Start

### 1. Install

```bash
# From the DAiW-Music-Brain directory
pip install -e .

# Or install just the MCP TODO module
cd mcp_todo
pip install -e .
```

### 2. Test CLI

```bash
# Add a task
python -m mcp_todo.cli add "Review pull request" --priority high --tags "code,urgent"

# List tasks
python -m mcp_todo.cli list

# Complete a task
python -m mcp_todo.cli complete abc123
```

### 3. Configure Your AI Assistant

See setup instructions below for each AI.

---

## Setup Instructions

### Claude Desktop

Add to `~/.config/claude/claude_desktop_config.json` (Linux) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "mcp-todo": {
      "command": "python",
      "args": ["-m", "mcp_todo.server"],
      "cwd": "/path/to/DAiW-Music-Brain"
    }
  }
}
```

Restart Claude Desktop. You can now say things like:
- "Add a task to fix the login bug"
- "Show me my high priority tasks"
- "Mark task abc123 as complete"

### Claude Code

Add to your project's `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "mcp-todo": {
      "command": "python",
      "args": ["-m", "mcp_todo.server"]
    }
  }
}
```

### Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mcp-todo": {
      "command": "python",
      "args": ["-m", "mcp_todo.server"],
      "cwd": "/path/to/DAiW-Music-Brain"
    }
  }
}
```

Restart Cursor. The TODO tools will appear in Cursor's AI chat.

### VSCode with GitHub Copilot

If using Copilot Chat with MCP support, add to `.vscode/settings.json`:

```json
{
  "github.copilot.chat.mcp.enabled": true,
  "github.copilot.chat.mcp.servers": {
    "mcp-todo": {
      "command": "python",
      "args": ["-m", "mcp_todo.server"]
    }
  }
}
```

### ChatGPT (OpenAI Plugin)

1. Start the HTTP server:
   ```bash
   python -m mcp_todo.http_server --port 8080
   ```

2. For ChatGPT Plugins (requires ChatGPT Plus):
   - Go to ChatGPT Plugin Store
   - Choose "Develop your own plugin"
   - Enter `http://localhost:8080` as the plugin URL
   - The plugin manifest is served at `/.well-known/ai-plugin.json`

3. For OpenAI API function calling, use the OpenAPI spec at:
   ```
   http://localhost:8080/openapi.yaml
   ```

### Gemini (Google AI)

See `configs/gemini_instructions.md` for detailed integration:

**Option A: Function Declarations**
```python
import google.generativeai as genai
from mcp_todo.storage import TodoStorage

# Define tools and handle function calls
# See configs/gemini_instructions.md for full example
```

**Option B: HTTP API**
```bash
python -m mcp_todo.http_server --port 8080
```
Then configure Gemini to call `http://localhost:8080/todos`.

---

## Available Tools

When connected to an AI assistant, these tools become available:

| Tool | Description |
|------|-------------|
| `todo_add` | Create a new task |
| `todo_list` | List tasks with filters |
| `todo_get` | Get task details by ID |
| `todo_complete` | Mark task as done |
| `todo_start` | Mark task as in progress |
| `todo_update` | Update task properties |
| `todo_delete` | Delete a task |
| `todo_search` | Search by text |
| `todo_summary` | Get statistics |
| `todo_add_subtask` | Add a subtask |
| `todo_add_note` | Add a note to a task |
| `todo_clear_completed` | Remove completed tasks |
| `todo_export` | Export as Markdown |

## CLI Commands

```bash
# Add tasks
python -m mcp_todo.cli add "Task title" --priority high --tags "tag1,tag2" --project myproject

# List tasks
python -m mcp_todo.cli list
python -m mcp_todo.cli list --status pending --priority high
python -m mcp_todo.cli list --hide-completed

# Manage tasks
python -m mcp_todo.cli start <id>      # Mark in progress
python -m mcp_todo.cli complete <id>   # Mark complete
python -m mcp_todo.cli delete <id>     # Delete

# Other commands
python -m mcp_todo.cli get <id>        # Get details
python -m mcp_todo.cli search "query"  # Search
python -m mcp_todo.cli summary         # Statistics
python -m mcp_todo.cli export          # Export markdown
python -m mcp_todo.cli clear-completed # Remove done tasks
```

## HTTP API Endpoints

When running `python -m mcp_todo.http_server`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/todos` | List all tasks |
| POST | `/todos` | Create task |
| GET | `/todos/{id}` | Get task |
| PATCH | `/todos/{id}` | Update task |
| DELETE | `/todos/{id}` | Delete task |
| POST | `/todos/{id}/complete` | Complete task |
| POST | `/todos/{id}/start` | Start task |
| GET | `/todos/search?q=query` | Search |
| GET | `/todos/summary` | Statistics |

## Task Properties

```json
{
  "id": "abc123",
  "title": "Fix login bug",
  "description": "Users can't log in with special characters",
  "status": "in_progress",
  "priority": "high",
  "tags": ["bug", "auth"],
  "project": "backend",
  "due_date": "2024-12-31",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T14:20:00",
  "completed_at": null,
  "notes": ["Affects 10% of users"],
  "ai_source": "claude",
  "context": "Related to issue #123"
}
```

### Priority Levels
- `low` - Can wait
- `medium` - Normal priority (default)
- `high` - Important
- `urgent` - Critical, do immediately

### Status Values
- `pending` - Not started
- `in_progress` - Currently working
- `completed` - Done
- `blocked` - Waiting on something
- `cancelled` - No longer needed

## Storage

Tasks are stored in `~/.mcp_todo/todos.json`. This file is shared across all AI assistants, enabling seamless task management regardless of which AI you're using.

To use a different storage location:

```bash
# CLI
python -m mcp_todo.cli --storage-dir /path/to/dir list

# Server
python -m mcp_todo.server --storage-dir /path/to/dir

# HTTP
python -m mcp_todo.http_server --storage-dir /path/to/dir
```

## Example Workflows

### Cross-AI Task Management

1. **In Claude**: "Add a task to implement user authentication with high priority"
2. **In Cursor**: "Show me my pending tasks" (sees the task from Claude)
3. **In ChatGPT**: "Mark the authentication task as in progress"
4. **In CLI**: `python -m mcp_todo.cli list` (sees updates from all AIs)

### Project-Based Organization

```bash
# CLI
python -m mcp_todo.cli add "Design API" --project backend
python -m mcp_todo.cli add "Create UI" --project frontend
python -m mcp_todo.cli list --project backend
```

Or in AI:
- "Add task 'Design API' to the backend project"
- "Show me all frontend tasks"

### Using Tags

```bash
python -m mcp_todo.cli add "Fix bug #123" --tags "bug,urgent,production"
python -m mcp_todo.cli list --tags "urgent"
```

## Troubleshooting

### Claude/Cursor don't see the tools

1. Check the MCP config file path is correct
2. Ensure Python is in your PATH
3. Verify the module path: `python -m mcp_todo.server` should start without errors
4. Restart the AI application

### HTTP server connection refused

1. Check the server is running: `python -m mcp_todo.http_server`
2. Verify the port isn't blocked: `curl http://localhost:8080/todos`
3. Check firewall settings

### Tasks not syncing

All AI assistants share `~/.mcp_todo/todos.json`. If tasks aren't syncing:
1. Check all are using the same storage directory
2. Ensure no `--storage-dir` override is set
3. Verify file permissions

## Development

```bash
# Run tests
pytest tests/

# Format code
black mcp_todo/

# Type check
mypy mcp_todo/
```

## License

MIT License - See LICENSE file for details.
