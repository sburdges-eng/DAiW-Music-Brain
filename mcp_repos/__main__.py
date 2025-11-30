"""
MCP Repos - Main entry point

Allows running as: python -m mcp_repos
"""

import sys
import argparse


def main():
    """Main entry point with server/cli mode selection."""
    parser = argparse.ArgumentParser(
        prog="mcp_repos",
        description="MCP Repository Manager for sburdges-eng repos",
    )
    parser.add_argument(
        "--server", "-s",
        action="store_true",
        help="Run as MCP server (stdio mode)",
    )
    parser.add_argument(
        "--cli", "-c",
        action="store_true",
        help="Run in CLI mode (default)",
    )

    args, remaining = parser.parse_known_args()

    if args.server:
        # Run MCP server
        from .server import run_server
        run_server()
    else:
        # Run CLI
        sys.argv = [sys.argv[0]] + remaining
        from .cli import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()
