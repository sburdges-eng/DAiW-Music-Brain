#!/usr/bin/env python3
"""
MCP TODO - Main entry point

When run as a module, starts the MCP server.
Use 'python -m mcp_todo' to start the server.
Use 'python -m mcp_todo.cli' for CLI commands.
"""

from .server import main

if __name__ == "__main__":
    main()
