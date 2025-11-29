#!/usr/bin/env python3
"""
MCP TODO CLI

Command-line interface for managing TODOs directly.
Useful for testing and manual management.

Usage:
    python -m mcp_todo.cli list
    python -m mcp_todo.cli add "My task" --priority high
    python -m mcp_todo.cli complete abc123
"""

import argparse
import json
import sys
from typing import Optional

from .storage import TodoStorage
from .models import TodoStatus, TodoPriority


def cmd_add(args, storage: TodoStorage):
    """Add a new TODO."""
    tags = args.tags.split(",") if args.tags else []

    todo = storage.add(
        title=args.title,
        description=args.description or "",
        priority=args.priority,
        tags=tags,
        project=args.project,
        due_date=args.due,
        context=args.context or "",
        ai_source="cli",
    )

    print(f"Created: {todo}")
    print(f"  ID: {todo.id}")


def cmd_list(args, storage: TodoStorage):
    """List TODOs."""
    tags = args.tags.split(",") if args.tags else None

    todos = storage.list_all(
        project=args.project,
        status=args.status,
        priority=args.priority,
        tags=tags,
        include_completed=not args.hide_completed,
    )

    if not todos:
        print("No TODOs found.")
        return

    # Group by status if not filtering
    if not args.status:
        by_status = {}
        for todo in todos:
            status = todo.status.value
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(todo)

        status_order = ["in_progress", "pending", "blocked", "completed", "cancelled"]
        for status in status_order:
            if status in by_status:
                print(f"\n{status.upper().replace('_', ' ')}:")
                for todo in by_status[status]:
                    print(f"  {todo}")
    else:
        for todo in todos:
            print(todo)

    print(f"\nTotal: {len(todos)} items")


def cmd_get(args, storage: TodoStorage):
    """Get TODO details."""
    todo = storage.get(args.id, project=args.project)

    if not todo:
        print(f"TODO not found: {args.id}")
        sys.exit(1)

    print(f"ID: {todo.id}")
    print(f"Title: {todo.title}")
    print(f"Status: {todo.status.value}")
    print(f"Priority: {todo.priority.value}")
    print(f"Project: {todo.project or 'default'}")
    print(f"Created: {todo.created_at}")
    print(f"Updated: {todo.updated_at}")

    if todo.description:
        print(f"Description: {todo.description}")
    if todo.tags:
        print(f"Tags: {', '.join(todo.tags)}")
    if todo.due_date:
        print(f"Due: {todo.due_date}")
    if todo.completed_at:
        print(f"Completed: {todo.completed_at}")
    if todo.notes:
        print("Notes:")
        for note in todo.notes:
            print(f"  - {note}")


def cmd_complete(args, storage: TodoStorage):
    """Mark TODO as complete."""
    todo = storage.complete(args.id, project=args.project, ai_source="cli")

    if todo:
        print(f"Completed: {todo}")
    else:
        print(f"TODO not found: {args.id}")
        sys.exit(1)


def cmd_start(args, storage: TodoStorage):
    """Mark TODO as in progress."""
    todo = storage.start(args.id, project=args.project, ai_source="cli")

    if todo:
        print(f"Started: {todo}")
    else:
        print(f"TODO not found: {args.id}")
        sys.exit(1)


def cmd_delete(args, storage: TodoStorage):
    """Delete a TODO."""
    success = storage.delete(args.id, project=args.project)

    if success:
        print(f"Deleted: {args.id}")
    else:
        print(f"TODO not found: {args.id}")
        sys.exit(1)


def cmd_search(args, storage: TodoStorage):
    """Search TODOs."""
    todos = storage.search(args.query, project=args.project)

    if not todos:
        print(f"No TODOs found matching: {args.query}")
        return

    for todo in todos:
        print(todo)


def cmd_summary(args, storage: TodoStorage):
    """Show TODO summary."""
    summary = storage.get_summary(project=args.project)

    print(f"Total: {summary['total']}")
    print(f"  Pending: {summary['pending']}")
    print(f"  In Progress: {summary['in_progress']}")
    print(f"  Completed: {summary['completed']}")

    if summary['by_priority']:
        print("\nBy Priority:")
        for pri, count in summary['by_priority'].items():
            print(f"  {pri}: {count}")


def cmd_export(args, storage: TodoStorage):
    """Export TODOs as Markdown."""
    markdown = storage.export_markdown(project=args.project)
    print(markdown)


def cmd_clear_completed(args, storage: TodoStorage):
    """Clear completed TODOs."""
    count = storage.clear_completed(project=args.project)
    print(f"Cleared {count} completed TODOs")


def main():
    parser = argparse.ArgumentParser(
        description="MCP TODO CLI - Manage your tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    mcp-todo add "Fix the bug" --priority high --tags "bug,urgent"
    mcp-todo list --status pending
    mcp-todo complete abc123
    mcp-todo search "authentication"
        """
    )

    parser.add_argument(
        "--storage-dir",
        help="Directory for TODO storage (default: ~/.mcp_todo/)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new TODO")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("-d", "--description", help="Task description")
    add_parser.add_argument(
        "-p", "--priority",
        choices=["low", "medium", "high", "urgent"],
        default="medium",
        help="Priority level"
    )
    add_parser.add_argument("-t", "--tags", help="Comma-separated tags")
    add_parser.add_argument("--project", help="Project name")
    add_parser.add_argument("--due", help="Due date (YYYY-MM-DD)")
    add_parser.add_argument("-c", "--context", help="Additional context")

    # List command
    list_parser = subparsers.add_parser("list", aliases=["ls"], help="List TODOs")
    list_parser.add_argument("--project", help="Filter by project")
    list_parser.add_argument(
        "--status",
        choices=["pending", "in_progress", "completed", "blocked", "cancelled"],
        help="Filter by status"
    )
    list_parser.add_argument(
        "--priority",
        choices=["low", "medium", "high", "urgent"],
        help="Filter by priority"
    )
    list_parser.add_argument("-t", "--tags", help="Filter by tags (comma-separated)")
    list_parser.add_argument(
        "--hide-completed",
        action="store_true",
        help="Hide completed tasks"
    )

    # Get command
    get_parser = subparsers.add_parser("get", help="Get TODO details")
    get_parser.add_argument("id", help="TODO ID")
    get_parser.add_argument("--project", help="Project name")

    # Complete command
    complete_parser = subparsers.add_parser("complete", aliases=["done"], help="Mark TODO complete")
    complete_parser.add_argument("id", help="TODO ID")
    complete_parser.add_argument("--project", help="Project name")

    # Start command
    start_parser = subparsers.add_parser("start", help="Mark TODO as in progress")
    start_parser.add_argument("id", help="TODO ID")
    start_parser.add_argument("--project", help="Project name")

    # Delete command
    delete_parser = subparsers.add_parser("delete", aliases=["rm"], help="Delete a TODO")
    delete_parser.add_argument("id", help="TODO ID")
    delete_parser.add_argument("--project", help="Project name")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search TODOs")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--project", help="Project name")

    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Show TODO summary")
    summary_parser.add_argument("--project", help="Project name")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export as Markdown")
    export_parser.add_argument("--project", help="Project name")

    # Clear completed command
    clear_parser = subparsers.add_parser("clear-completed", help="Clear completed TODOs")
    clear_parser.add_argument("--project", help="Project name")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    storage = TodoStorage(args.storage_dir)

    commands = {
        "add": cmd_add,
        "list": cmd_list,
        "ls": cmd_list,
        "get": cmd_get,
        "complete": cmd_complete,
        "done": cmd_complete,
        "start": cmd_start,
        "delete": cmd_delete,
        "rm": cmd_delete,
        "search": cmd_search,
        "summary": cmd_summary,
        "export": cmd_export,
        "clear-completed": cmd_clear_completed,
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        cmd_func(args, storage)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
