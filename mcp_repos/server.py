"""
MCP Repos - MCP Server

Model Context Protocol server for multi-repository management.
Provides tools for connecting to and managing sburdges-eng repositories.
"""

import json
import sys
import asyncio
from typing import Any, Sequence

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from .manager import get_repo_manager, RepoManager
from .models import RepoStatus


# =============================================================================
# MCP Server Implementation
# =============================================================================

if MCP_AVAILABLE:
    # Create MCP server
    server = Server("mcp-repos")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools for repository management."""
        return [
            Tool(
                name="repo_connect",
                description="Connect to a sburdges-eng repository. Pass 'all' to connect to all repos.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_name": {
                            "type": "string",
                            "description": "Repository name (e.g., 'DAiW-Music-Brain', 'BEO-Master', 'lariat-bible', or 'all')",
                        },
                        "local_path": {
                            "type": "string",
                            "description": "Optional local path if already cloned",
                        },
                    },
                    "required": ["repo_name"],
                },
            ),
            Tool(
                name="repo_list",
                description="List all sburdges-eng repositories and their connection status",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="repo_status",
                description="Get detailed status for a specific repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_name": {
                            "type": "string",
                            "description": "Repository name",
                        },
                    },
                    "required": ["repo_name"],
                },
            ),
            Tool(
                name="repo_dashboard",
                description="Get a formatted dashboard of all sburdges-eng repositories",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="repo_disconnect",
                description="Disconnect from a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_name": {
                            "type": "string",
                            "description": "Repository name to disconnect",
                        },
                    },
                    "required": ["repo_name"],
                },
            ),
            Tool(
                name="cross_repo_task_create",
                description="Create a task that spans multiple repositories",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title",
                        },
                        "description": {
                            "type": "string",
                            "description": "Task description",
                        },
                        "repos": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of repository names involved",
                        },
                        "priority": {
                            "type": "integer",
                            "description": "Priority 1-10 (10 highest)",
                            "default": 5,
                        },
                    },
                    "required": ["title", "description", "repos"],
                },
            ),
            Tool(
                name="cross_repo_task_list",
                description="List cross-repository tasks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_name": {
                            "type": "string",
                            "description": "Optional: filter by repository name",
                        },
                    },
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
        """Handle tool calls."""
        manager = get_repo_manager()

        try:
            if name == "repo_connect":
                repo_name = arguments.get("repo_name", "")
                local_path = arguments.get("local_path")

                if repo_name.lower() == "all":
                    results = manager.connect_all()
                    connected = [n for n, c in results.items() if c.repository.status == RepoStatus.CONNECTED]
                    return [TextContent(
                        type="text",
                        text=f"Connected to {len(connected)} repositories:\n" +
                             "\n".join(f"  - {n}: {c.repository.status.value}" for n, c in results.items())
                    )]
                else:
                    conn = manager.connect_repo(repo_name, local_path)
                    if conn:
                        return [TextContent(
                            type="text",
                            text=f"Connected to {repo_name}:\n" +
                                 f"  Status: {conn.repository.status.value}\n" +
                                 f"  Branch: {conn.current_branch}\n" +
                                 f"  Sync: {conn.repository.sync_status.value}"
                        )]
                    else:
                        return [TextContent(type="text", text=f"Failed to connect to {repo_name}")]

            elif name == "repo_list":
                repos = manager.list_all()
                lines = ["sburdges-eng Repositories:", ""]
                for repo in repos:
                    status = "[OK]" if repo["status"] == "connected" else "[--]"
                    lines.append(f"{status} {repo['full_name']}")
                    lines.append(f"    {repo['description']}")
                    lines.append("")
                return [TextContent(type="text", text="\n".join(lines))]

            elif name == "repo_status":
                repo_name = arguments.get("repo_name", "")
                status = manager.get_repo_status(repo_name)
                if status:
                    return [TextContent(
                        type="text",
                        text=json.dumps(status, indent=2)
                    )]
                else:
                    return [TextContent(type="text", text=f"Repository not found: {repo_name}")]

            elif name == "repo_dashboard":
                dashboard = manager.get_dashboard()
                return [TextContent(type="text", text=dashboard)]

            elif name == "repo_disconnect":
                repo_name = arguments.get("repo_name", "")
                success = manager.disconnect_repo(repo_name)
                return [TextContent(
                    type="text",
                    text=f"Disconnected from {repo_name}" if success else f"Not connected to {repo_name}"
                )]

            elif name == "cross_repo_task_create":
                task = manager.create_cross_repo_task(
                    title=arguments.get("title", ""),
                    description=arguments.get("description", ""),
                    repos=arguments.get("repos", []),
                    priority=arguments.get("priority", 5),
                )
                return [TextContent(
                    type="text",
                    text=f"Created cross-repo task: {task.id}\n" +
                         f"  Title: {task.title}\n" +
                         f"  Repos: {', '.join(task.repos)}"
                )]

            elif name == "cross_repo_task_list":
                repo_name = arguments.get("repo_name")
                tasks = manager.get_cross_repo_tasks(repo_name)
                if tasks:
                    lines = ["Cross-Repository Tasks:", ""]
                    for task in tasks:
                        lines.append(f"[{task.status}] {task.title} (#{task.id})")
                        lines.append(f"    Repos: {', '.join(task.repos)}")
                        lines.append(f"    {task.description[:60]}...")
                        lines.append("")
                    return [TextContent(type="text", text="\n".join(lines))]
                else:
                    return [TextContent(type="text", text="No cross-repo tasks found")]

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]


# =============================================================================
# Server Entry Point
# =============================================================================

async def _run_server():
    """Run the MCP server."""
    if not MCP_AVAILABLE:
        print("MCP SDK not available. Install with: pip install mcp", file=sys.stderr)
        sys.exit(1)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def run_server():
    """Entry point for running the MCP server."""
    asyncio.run(_run_server())


if __name__ == "__main__":
    run_server()
