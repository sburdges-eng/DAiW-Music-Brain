-SYSTEM: You are a Senior AI Infrastructure Engineer.
TASK: Create a Model Context Protocol (MCP) Server named "Penta-Core" using Python and the `fastmcp` library.
CONTEXT: This server aggregates the top 5 AI platforms into a single "Swarm" toolset for my IDE (Cursor/VS Code).

REQUIREMENTS:
1. ENVIRONMENT:
   - Use `python-dotenv` to load API keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `GITHUB_TOKEN`, `XAI_API_KEY`.
   - Use `fastmcp` for the server architecture.
   - Use `openai` SDK (compatible with xAI) and other official SDKs.

2. DEFINE 5 TOOLS (The "Swarm"):

   A. Tool: `consult_architect(prompt: str)`
      - BACKEND: OpenAI (GPT-4o or o1).
      - SYSTEM PROMPT: "You are a Systems Architect. Focus on high-level logic, class structure, and design patterns."
      - USE CASE: Planning and Structure.

   B. Tool: `consult_developer(prompt: str)`
      - BACKEND: Anthropic (Claude 3.5 Sonnet).
      - SYSTEM PROMPT: "You are a Senior Engineer. Focus on clean code, safety, and refactoring. Output production-ready code."
      - USE CASE: Coding and Refactoring.

   C. Tool: `consult_researcher(prompt: str, context: str)`
      - BACKEND: Google (Gemini 1.5 Pro).
      - SYSTEM PROMPT: "You are a Lead Researcher. Analyze documentation and find edge cases with your massive context window."
      - USE CASE: Deep Context and Documentation.

   D. Tool: `consult_maverick(prompt: str)`
      - BACKEND: xAI (Grok Beta).
      - SYSTEM PROMPT: "You are a Maverick Engineer. Criticize the plan, find non-obvious flaws, and suggest lateral/unconventional solutions. Be direct."
      - USE CASE: "Red Teaming" or finding creative exploits.

   E. Tool: `fetch_repo_context(owner: str, repo: str, path: str)`
      - BACKEND: GitHub API.
      - FUNCTION: Fetch file content/tree from a repo.
      - USE CASE: Providing context to the agents.

3. ARCHITECTURE:
   - Implement `mcp.server.fastmcp`.
   - Ensure the xAI client uses the `openai` SDK with `base_url="https://api.x.ai/v1"`.
   - robust error handling.

4. DELIVERABLE:
   - Complete `server.py`.
   - `requirements.txt`.
   - `.env.example`.

Start by writing the imports and the `FastMCP` initialization.--
# Fill in the fields below to create a basic custom agent for your repository.
# The Copilot CLI can be used for local testing: https://gh.io/customagents/cli
# To make this agent available, merge this file into the default repository branch.
# For format details, see: https://gh.io/customagents/config

name:
description:
---

# My Agent

Describe what your agent does here...
