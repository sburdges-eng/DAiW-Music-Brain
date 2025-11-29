"""
MCP Workstation - Command Line Interface

CLI for managing the multi-AI workstation.
"""

import argparse
import json
import sys
from typing import Optional

from .models import AIAgent, ProposalCategory, ProposalStatus, PhaseStatus
from .orchestrator import get_workstation, shutdown_workstation
from .ai_specializations import print_ai_summary, TaskType
from .phases import format_phase_progress
from .cpp_planner import format_cpp_plan
from .proposals import format_proposal_list, format_proposal


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MCP Multi-AI Workstation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                     Show workstation dashboard
  %(prog)s register claude            Register as Claude
  %(prog)s propose claude "Title" "Description" architecture
  %(prog)s vote claude PROP_ID 1      Approve a proposal
  %(prog)s phases                     Show phase progress
  %(prog)s cpp                        Show C++ transition plan
  %(prog)s ai                         Show AI specializations
  %(prog)s server                     Run MCP server
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show workstation status")
    status_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Register command
    register_parser = subparsers.add_parser("register", help="Register an AI agent")
    register_parser.add_argument(
        "agent",
        choices=["claude", "chatgpt", "gemini", "github_copilot"],
        help="AI agent to register",
    )

    # Propose command
    propose_parser = subparsers.add_parser("propose", help="Submit a proposal")
    propose_parser.add_argument(
        "agent",
        choices=["claude", "chatgpt", "gemini", "github_copilot"],
    )
    propose_parser.add_argument("title", help="Proposal title")
    propose_parser.add_argument("description", help="Proposal description")
    propose_parser.add_argument(
        "category",
        choices=[c.value for c in ProposalCategory],
        help="Proposal category",
    )
    propose_parser.add_argument(
        "--priority", type=int, default=5, help="Priority 1-10"
    )
    propose_parser.add_argument(
        "--phase", type=int, default=1, help="Target phase 1-3"
    )

    # Vote command
    vote_parser = subparsers.add_parser("vote", help="Vote on a proposal")
    vote_parser.add_argument(
        "agent",
        choices=["claude", "chatgpt", "gemini", "github_copilot"],
    )
    vote_parser.add_argument("proposal_id", help="Proposal ID")
    vote_parser.add_argument(
        "vote",
        type=int,
        choices=[-1, 0, 1],
        help="-1=reject, 0=neutral, 1=approve",
    )
    vote_parser.add_argument("--comment", default="", help="Vote comment")

    # Proposals command
    proposals_parser = subparsers.add_parser("proposals", help="List proposals")
    proposals_parser.add_argument(
        "--agent",
        choices=["claude", "chatgpt", "gemini", "github_copilot"],
    )
    proposals_parser.add_argument(
        "--status",
        choices=[s.value for s in ProposalStatus],
    )
    proposals_parser.add_argument("--json", action="store_true")

    # Phases command
    phases_parser = subparsers.add_parser("phases", help="Show phase progress")
    phases_parser.add_argument("--json", action="store_true")

    # Task command
    task_parser = subparsers.add_parser("task", help="Update a task")
    task_parser.add_argument("phase_id", type=int, help="Phase ID")
    task_parser.add_argument("task_id", help="Task ID")
    task_parser.add_argument(
        "status",
        choices=[s.value for s in PhaseStatus],
    )
    task_parser.add_argument("--progress", type=float)
    task_parser.add_argument("--notes")

    # C++ command
    cpp_parser = subparsers.add_parser("cpp", help="Show C++ transition plan")
    cpp_parser.add_argument("--json", action="store_true")
    cpp_parser.add_argument("--cmake", action="store_true", help="Show CMake plan")

    # AI command
    ai_parser = subparsers.add_parser("ai", help="Show AI specializations")
    ai_parser.add_argument(
        "--agent",
        choices=["claude", "chatgpt", "gemini", "github_copilot"],
    )

    # Assign command
    assign_parser = subparsers.add_parser("assign", help="Suggest task assignments")
    assign_parser.add_argument(
        "--tasks",
        nargs="+",
        help="Tasks in format name:type (e.g., 'refactor:code_refactoring')",
    )

    # Debug command
    debug_parser = subparsers.add_parser("debug", help="Show debug info")
    debug_parser.add_argument("--errors", action="store_true", help="Show recent errors")
    debug_parser.add_argument("--performance", action="store_true")

    # Server command
    server_parser = subparsers.add_parser("server", help="Run MCP server")

    # Reset command
    reset_parser = subparsers.add_parser("reset", help="Reset workstation")
    reset_parser.add_argument("--force", action="store_true", help="Skip confirmation")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        run_command(args)
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        shutdown_workstation()


def run_command(args):
    """Execute the selected command."""
    ws = get_workstation()

    if args.command == "status":
        if args.json:
            print(json.dumps(ws.get_status(), indent=2))
        else:
            print(ws.get_dashboard())

    elif args.command == "register":
        agent = AIAgent(args.agent)
        ws.register_agent(agent)
        print(f"Registered: {agent.display_name}")
        caps = ws.get_agent_capabilities(agent)
        print(f"\nRecommended for:")
        for item in caps["recommended_for"][:5]:
            print(f"  - {item}")

    elif args.command == "propose":
        result = ws.submit_proposal(
            agent=AIAgent(args.agent),
            title=args.title,
            description=args.description,
            category=ProposalCategory(args.category),
            priority=args.priority,
            phase_target=args.phase,
        )
        if result:
            print(f"Proposal submitted: {result['id']}")
            print(f"Title: {result['title']}")
        else:
            print("Failed to submit proposal (limit reached?)")

    elif args.command == "vote":
        result = ws.vote_on_proposal(
            agent=AIAgent(args.agent),
            proposal_id=args.proposal_id,
            vote=args.vote,
            comment=args.comment,
        )
        if result:
            vote_str = {-1: "REJECTED", 0: "NEUTRAL", 1: "APPROVED"}[args.vote]
            print(f"Vote recorded: {vote_str}")
        else:
            print("Failed to vote")

    elif args.command == "proposals":
        all_props = ws.get_all_proposals()
        proposals = all_props["proposals"]

        if args.agent:
            proposals = [p for p in proposals if p["agent"] == args.agent]
        if args.status:
            proposals = [p for p in proposals if p["status"] == args.status]

        if args.json:
            print(json.dumps(proposals, indent=2))
        else:
            from .models import Proposal
            props = [Proposal.from_dict(p) for p in proposals]
            print(format_proposal_list(props))
            print(f"\nSummary: {all_props['summary']}")

    elif args.command == "phases":
        if args.json:
            print(json.dumps(ws.phases.get_phase_summary(), indent=2))
        else:
            print(ws.get_phase_progress())

    elif args.command == "task":
        ws.update_task(
            phase_id=args.phase_id,
            task_id=args.task_id,
            status=args.status,
            progress=args.progress,
            notes=args.notes,
        )
        print(f"Task {args.task_id} updated to {args.status}")

    elif args.command == "cpp":
        if args.cmake:
            print(ws.get_cmake_plan())
        elif args.json:
            print(json.dumps(ws.get_cpp_plan(), indent=2))
        else:
            print(ws.get_cpp_progress())

    elif args.command == "ai":
        if args.agent:
            agent = AIAgent(args.agent)
            caps = ws.get_agent_capabilities(agent)
            print(json.dumps(caps, indent=2))
        else:
            print_ai_summary()

    elif args.command == "assign":
        if not args.tasks:
            print("Usage: assign --tasks 'task1:type1' 'task2:type2' ...")
            return

        tasks = []
        for t in args.tasks:
            if ":" not in t:
                print(f"Invalid task format: {t} (expected name:type)")
                continue
            name, task_type = t.split(":", 1)
            try:
                tasks.append((name, TaskType(task_type)))
            except ValueError:
                print(f"Unknown task type: {task_type}")
                continue

        if tasks:
            assignments = ws.suggest_assignments(tasks)
            print("Suggested Assignments:")
            for task, agent in assignments.items():
                print(f"  {task}: {agent}")

    elif args.command == "debug":
        summary = ws.get_debug_summary()
        if args.errors:
            print("Recent Errors:")
            for e in summary["recent_errors"]:
                print(f"  [{e['timestamp']}] {e['message']}")
        elif args.performance:
            print("Performance Report:")
            print(json.dumps(summary["performance"], indent=2))
        else:
            print(json.dumps(summary, indent=2))

    elif args.command == "server":
        from .server import run_server
        print("Starting MCP server...", file=sys.stderr)
        run_server()

    elif args.command == "reset":
        if not args.force:
            confirm = input("Reset workstation? This will clear all data. [y/N]: ")
            if confirm.lower() != "y":
                print("Cancelled")
                return
        ws.reset()
        print("Workstation reset")


if __name__ == "__main__":
    main()
