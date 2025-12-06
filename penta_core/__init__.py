"""
Penta-Core MCP Server

An MCP (Model Context Protocol) server that aggregates the top 5 AI platforms
into a single "Swarm" toolset for IDE integration (Cursor/VS Code).

The Swarm consists of 5 specialized AI tools:
- consult_architect: OpenAI GPT-4o for high-level logic and design patterns
- consult_developer: Anthropic Claude 3.5 Sonnet for clean code and refactoring
- consult_researcher: Google Gemini 1.5 Pro for deep context analysis
- consult_maverick: xAI Grok Beta for creative problem-solving and red teaming
- fetch_repo_context: GitHub API for fetching repository context
"""

__version__ = "1.0.0"
