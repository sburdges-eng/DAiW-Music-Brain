"""
MCP TODO Server - Multi-AI Compatible Task Management

A Model Context Protocol (MCP) server that provides TODO/task management
capabilities across multiple AI assistants:
- Claude (Anthropic)
- ChatGPT (OpenAI)
- Gemini (Google)
- Cursor/VSCode with Copilot (GitHub)

Usage:
    # Run as MCP server
    python -m mcp_todo.server

    # Or use the CLI
    python -m mcp_todo.cli list
"""

__version__ = "1.0.0"
__all__ = ["TodoStorage", "Todo", "TodoServer"]

from .models import Todo, TodoPriority, TodoStatus
from .storage import TodoStorage
