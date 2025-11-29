#!/usr/bin/env python3
"""
MCP TODO Server

Model Context Protocol server for cross-AI TODO management.
Compatible with Claude, ChatGPT, Gemini, and Cursor/VSCode with Copilot.

Run with:
    python -m mcp_todo.server
    # or
    mcp-todo-server
"""

import json
import sys
import asyncio
from typing import Any, Dict, List, Optional

from .storage import TodoStorage
from .models import Todo, TodoStatus, TodoPriority


class MCPTodoServer:
    """
    MCP-compliant TODO server.

    Implements the Model Context Protocol for tool-based interaction
    with AI assistants.
    """

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage = TodoStorage(storage_dir)
        self.server_info = {
            "name": "mcp-todo",
            "version": "1.0.0",
            "description": "Multi-AI compatible TODO management server",
        }

    def get_tools(self) -> List[Dict[str, Any]]:
        """Return the list of available MCP tools."""
        return [
            {
                "name": "todo_add",
                "description": "Add a new TODO task. Use this to create tasks with title, description, priority, tags, and project assignment.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The task title (required)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description of the task"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Task priority level"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags for organization"
                        },
                        "project": {
                            "type": "string",
                            "description": "Project name for grouping tasks"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in ISO format (YYYY-MM-DD)"
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context for AI assistants"
                        }
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "todo_list",
                "description": "List all TODO tasks with optional filters. Returns task IDs, titles, status, and priority.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "string",
                            "description": "Filter by project name"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed", "blocked", "cancelled"],
                            "description": "Filter by status"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Filter by priority"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by tags (any match)"
                        },
                        "include_completed": {
                            "type": "boolean",
                            "description": "Include completed tasks (default: true)"
                        }
                    }
                }
            },
            {
                "name": "todo_get",
                "description": "Get detailed information about a specific TODO by ID.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "The TODO ID"
                        },
                        "project": {
                            "type": "string",
                            "description": "Project name (optional)"
                        }
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "todo_complete",
                "description": "Mark a TODO as completed.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "The TODO ID to complete"
                        },
                        "project": {
                            "type": "string",
                            "description": "Project name (optional)"
                        }
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "todo_start",
                "description": "Mark a TODO as in progress (started working on it).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "The TODO ID to start"
                        },
                        "project": {
                            "type": "string",
                            "description": "Project name (optional)"
                        }
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "todo_update",
                "description": "Update a TODO's properties (title, description, priority, status, tags, etc.).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "The TODO ID to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New title"
                        },
                        "description": {
                            "type": "string",
                            "description": "New description"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "New priority"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed", "blocked", "cancelled"],
                            "description": "New status"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "New tags (replaces existing)"
                        },
                        "project": {
                            "type": "string",
                            "description": "Project name"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "New due date"
                        }
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "todo_delete",
                "description": "Delete a TODO by ID.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "The TODO ID to delete"
                        },
                        "project": {
                            "type": "string",
                            "description": "Project name (optional)"
                        }
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "todo_search",
                "description": "Search TODOs by text in title or description.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "project": {
                            "type": "string",
                            "description": "Project name (optional)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "todo_summary",
                "description": "Get a summary of TODO statistics (counts by status and priority).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "string",
                            "description": "Project name (optional)"
                        }
                    }
                }
            },
            {
                "name": "todo_add_subtask",
                "description": "Add a subtask to an existing TODO.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "parent_id": {
                            "type": "string",
                            "description": "ID of the parent TODO"
                        },
                        "title": {
                            "type": "string",
                            "description": "Subtask title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Subtask description"
                        },
                        "project": {
                            "type": "string",
                            "description": "Project name (optional)"
                        }
                    },
                    "required": ["parent_id", "title"]
                }
            },
            {
                "name": "todo_add_note",
                "description": "Add a note/comment to an existing TODO.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "The TODO ID"
                        },
                        "note": {
                            "type": "string",
                            "description": "The note to add"
                        },
                        "project": {
                            "type": "string",
                            "description": "Project name (optional)"
                        }
                    },
                    "required": ["id", "note"]
                }
            },
            {
                "name": "todo_clear_completed",
                "description": "Remove all completed TODOs from the list.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "string",
                            "description": "Project name (optional)"
                        }
                    }
                }
            },
            {
                "name": "todo_export",
                "description": "Export TODOs as Markdown.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "string",
                            "description": "Project name (optional)"
                        }
                    }
                }
            }
        ]

    def handle_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        ai_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle a tool call and return the result.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            ai_source: Which AI is making the call (claude, chatgpt, gemini, copilot)

        Returns:
            Tool result as a dictionary
        """
        try:
            if tool_name == "todo_add":
                todo = self.storage.add(
                    title=arguments["title"],
                    description=arguments.get("description", ""),
                    priority=arguments.get("priority", "medium"),
                    tags=arguments.get("tags", []),
                    project=arguments.get("project"),
                    due_date=arguments.get("due_date"),
                    context=arguments.get("context", ""),
                    ai_source=ai_source,
                )
                return {
                    "success": True,
                    "message": f"Created TODO: {todo.title}",
                    "todo": todo.to_dict()
                }

            elif tool_name == "todo_list":
                todos = self.storage.list_all(
                    project=arguments.get("project"),
                    status=arguments.get("status"),
                    priority=arguments.get("priority"),
                    tags=arguments.get("tags"),
                    include_completed=arguments.get("include_completed", True),
                )
                return {
                    "success": True,
                    "count": len(todos),
                    "todos": [
                        {
                            "id": t.id,
                            "title": t.title,
                            "status": t.status.value,
                            "priority": t.priority.value,
                            "tags": t.tags,
                            "project": t.project,
                        }
                        for t in todos
                    ]
                }

            elif tool_name == "todo_get":
                todo = self.storage.get(
                    arguments["id"],
                    project=arguments.get("project")
                )
                if todo:
                    return {
                        "success": True,
                        "todo": todo.to_dict()
                    }
                return {
                    "success": False,
                    "error": f"TODO not found: {arguments['id']}"
                }

            elif tool_name == "todo_complete":
                todo = self.storage.complete(
                    arguments["id"],
                    project=arguments.get("project"),
                    ai_source=ai_source,
                )
                if todo:
                    return {
                        "success": True,
                        "message": f"Completed: {todo.title}",
                        "todo": todo.to_dict()
                    }
                return {
                    "success": False,
                    "error": f"TODO not found: {arguments['id']}"
                }

            elif tool_name == "todo_start":
                todo = self.storage.start(
                    arguments["id"],
                    project=arguments.get("project"),
                    ai_source=ai_source,
                )
                if todo:
                    return {
                        "success": True,
                        "message": f"Started: {todo.title}",
                        "todo": todo.to_dict()
                    }
                return {
                    "success": False,
                    "error": f"TODO not found: {arguments['id']}"
                }

            elif tool_name == "todo_update":
                todo_id = arguments.pop("id")
                project = arguments.pop("project", None)
                todo = self.storage.update(
                    todo_id,
                    project=project,
                    ai_source=ai_source,
                    **arguments
                )
                if todo:
                    return {
                        "success": True,
                        "message": f"Updated: {todo.title}",
                        "todo": todo.to_dict()
                    }
                return {
                    "success": False,
                    "error": f"TODO not found: {todo_id}"
                }

            elif tool_name == "todo_delete":
                success = self.storage.delete(
                    arguments["id"],
                    project=arguments.get("project")
                )
                return {
                    "success": success,
                    "message": "TODO deleted" if success else "TODO not found"
                }

            elif tool_name == "todo_search":
                todos = self.storage.search(
                    arguments["query"],
                    project=arguments.get("project")
                )
                return {
                    "success": True,
                    "count": len(todos),
                    "todos": [
                        {
                            "id": t.id,
                            "title": t.title,
                            "status": t.status.value,
                            "priority": t.priority.value,
                        }
                        for t in todos
                    ]
                }

            elif tool_name == "todo_summary":
                summary = self.storage.get_summary(
                    project=arguments.get("project")
                )
                return {
                    "success": True,
                    "summary": summary
                }

            elif tool_name == "todo_add_subtask":
                todo = self.storage.add_subtask(
                    parent_id=arguments["parent_id"],
                    title=arguments["title"],
                    description=arguments.get("description", ""),
                    project=arguments.get("project"),
                    ai_source=ai_source,
                )
                if todo:
                    return {
                        "success": True,
                        "message": f"Created subtask: {todo.title}",
                        "todo": todo.to_dict()
                    }
                return {
                    "success": False,
                    "error": f"Parent TODO not found: {arguments['parent_id']}"
                }

            elif tool_name == "todo_add_note":
                todo = self.storage.get(
                    arguments["id"],
                    project=arguments.get("project")
                )
                if todo:
                    todo.add_note(arguments["note"], ai_source=ai_source)
                    self.storage.update(
                        todo.id,
                        project=arguments.get("project"),
                        notes=todo.notes
                    )
                    return {
                        "success": True,
                        "message": "Note added",
                        "todo": todo.to_dict()
                    }
                return {
                    "success": False,
                    "error": f"TODO not found: {arguments['id']}"
                }

            elif tool_name == "todo_clear_completed":
                count = self.storage.clear_completed(
                    project=arguments.get("project")
                )
                return {
                    "success": True,
                    "message": f"Cleared {count} completed TODOs"
                }

            elif tool_name == "todo_export":
                markdown = self.storage.export_markdown(
                    project=arguments.get("project")
                )
                return {
                    "success": True,
                    "format": "markdown",
                    "content": markdown
                }

            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP protocol message."""
        method = message.get("method", "")
        msg_id = message.get("id")
        params = message.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": self.server_info,
                    "capabilities": {
                        "tools": {"listChanged": False},
                    }
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": self.get_tools()
                }
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            ai_source = params.get("_meta", {}).get("ai_source")

            result = self.handle_tool_call(tool_name, arguments, ai_source)

            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }

        elif method == "notifications/initialized":
            # Client acknowledgment, no response needed
            return None

        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    async def run_stdio(self):
        """Run the server using stdio transport."""
        print(f"MCP TODO Server v{self.server_info['version']} starting...", file=sys.stderr)

        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                message = json.loads(line)
                response = await self.handle_message(message)

                if response:
                    print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)


def main():
    """Entry point for the MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description="MCP TODO Server")
    parser.add_argument(
        "--storage-dir",
        help="Directory for TODO storage",
        default=None
    )
    args = parser.parse_args()

    server = MCPTodoServer(storage_dir=args.storage_dir)
    asyncio.run(server.run_stdio())


if __name__ == "__main__":
    main()
