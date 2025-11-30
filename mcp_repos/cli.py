"""
MCP Repos - Command Line Interface

CLI for managing sburdges-eng repository connections.
"""

import argparse
import json
import sys
from pathlib import Path

from .manager import get_repo_manager, RepoManager
from .models import RepoStatus


def cmd_connect(args):
    """Connect to repositories."""
    manager = get_repo_manager()

    if args.all:
        print("Connecting to all sburdges-eng repositories...")
        results = manager.connect_all()
        print()
        for name, conn in results.items():
            status = "OK" if conn.repository.status == RepoStatus.CONNECTED else "DISCONNECTED"
            print(f"  [{status}] {conn.repository.full_name}")
            if conn.repository.status == RepoStatus.CONNECTED:
                print(f"         Branch: {conn.current_branch}")
                print(f"         Sync: {conn.repository.sync_status.value}")
        print()
        connected = sum(1 for c in results.values() if c.repository.status == RepoStatus.CONNECTED)
        print(f"Connected to {connected}/{len(results)} repositories")
    else:
        repo_name = args.repo_name
        local_path = args.path

        print(f"Connecting to {repo_name}...")
        conn = manager.connect_repo(repo_name, local_path)

        if conn and conn.repository.status == RepoStatus.CONNECTED:
            print(f"  Status: Connected")
            print(f"  Full name: {conn.repository.full_name}")
            print(f"  Branch: {conn.current_branch}")
            print(f"  Sync status: {conn.repository.sync_status.value}")
            print(f"  Uncommitted changes: {conn.uncommitted_changes}")
        else:
            print(f"  Status: Disconnected")
            print(f"  Note: Repository may not be cloned locally")


def cmd_list(args):
    """List all repositories."""
    manager = get_repo_manager()

    print("sburdges-eng Repositories")
    print("=" * 50)
    print()

    repos = manager.list_all()
    for repo in repos:
        status_icon = {
            "connected": "[OK]",
            "disconnected": "[--]",
            "connecting": "[..]",
            "syncing": "[~~]",
            "error": "[!!]",
        }.get(repo["status"], "[??]")

        print(f"{status_icon} {repo['full_name']}")
        print(f"    {repo['description']}")
        if repo["topics"]:
            print(f"    Topics: {', '.join(repo['topics'])}")
        print()


def cmd_status(args):
    """Get status of a repository."""
    manager = get_repo_manager()

    if args.repo_name:
        status = manager.get_repo_status(args.repo_name)
        if status:
            print(json.dumps(status, indent=2))
        else:
            print(f"Repository not found: {args.repo_name}")
    else:
        # Show all status
        all_status = manager.get_all_status()
        print(json.dumps(all_status, indent=2))


def cmd_dashboard(args):
    """Show repository dashboard."""
    manager = get_repo_manager()
    print(manager.get_dashboard())


def cmd_task(args):
    """Manage cross-repo tasks."""
    manager = get_repo_manager()

    if args.action == "create":
        task = manager.create_cross_repo_task(
            title=args.title,
            description=args.description or "",
            repos=args.repos.split(",") if args.repos else [],
            priority=args.priority or 5,
        )
        print(f"Created task: {task.id}")
        print(f"  Title: {task.title}")
        print(f"  Repos: {', '.join(task.repos)}")

    elif args.action == "list":
        tasks = manager.get_cross_repo_tasks(args.repo)
        if tasks:
            print("Cross-Repository Tasks")
            print("=" * 50)
            for task in tasks:
                print(f"\n[{task.status}] {task.title} (#{task.id})")
                print(f"  Repos: {', '.join(task.repos)}")
                print(f"  Priority: {task.priority}")
                if task.description:
                    print(f"  {task.description[:80]}...")
        else:
            print("No cross-repo tasks found")

    elif args.action == "complete":
        success = manager.update_task_status(args.task_id, "completed")
        if success:
            print(f"Task {args.task_id} marked as completed")
        else:
            print(f"Task not found: {args.task_id}")


def cmd_disconnect(args):
    """Disconnect from a repository."""
    manager = get_repo_manager()
    success = manager.disconnect_repo(args.repo_name)
    if success:
        print(f"Disconnected from {args.repo_name}")
    else:
        print(f"Not connected to {args.repo_name}")


def cmd_reset(args):
    """Reset repository manager state."""
    manager = get_repo_manager()
    if args.confirm:
        manager.reset()
        print("Repository manager state reset")
    else:
        print("Use --confirm to reset state")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="mcp-repos",
        description="Manage sburdges-eng repository connections",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # connect command
    connect_parser = subparsers.add_parser("connect", help="Connect to repositories")
    connect_parser.add_argument("repo_name", nargs="?", help="Repository name")
    connect_parser.add_argument("--all", "-a", action="store_true", help="Connect to all repos")
    connect_parser.add_argument("--path", "-p", help="Local path if already cloned")
    connect_parser.set_defaults(func=cmd_connect)

    # list command
    list_parser = subparsers.add_parser("list", help="List all repositories")
    list_parser.set_defaults(func=cmd_list)

    # status command
    status_parser = subparsers.add_parser("status", help="Get repository status")
    status_parser.add_argument("repo_name", nargs="?", help="Repository name (optional)")
    status_parser.set_defaults(func=cmd_status)

    # dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Show repository dashboard")
    dashboard_parser.set_defaults(func=cmd_dashboard)

    # task command
    task_parser = subparsers.add_parser("task", help="Manage cross-repo tasks")
    task_parser.add_argument("action", choices=["create", "list", "complete"])
    task_parser.add_argument("--title", "-t", help="Task title (for create)")
    task_parser.add_argument("--description", "-d", help="Task description")
    task_parser.add_argument("--repos", "-r", help="Comma-separated repo names")
    task_parser.add_argument("--priority", "-p", type=int, help="Priority 1-10")
    task_parser.add_argument("--repo", help="Filter by repo (for list)")
    task_parser.add_argument("--task-id", help="Task ID (for complete)")
    task_parser.set_defaults(func=cmd_task)

    # disconnect command
    disconnect_parser = subparsers.add_parser("disconnect", help="Disconnect from a repository")
    disconnect_parser.add_argument("repo_name", help="Repository name")
    disconnect_parser.set_defaults(func=cmd_disconnect)

    # reset command
    reset_parser = subparsers.add_parser("reset", help="Reset manager state")
    reset_parser.add_argument("--confirm", action="store_true", help="Confirm reset")
    reset_parser.set_defaults(func=cmd_reset)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
