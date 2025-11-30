#!/usr/bin/env python3
"""
Penta-Core MCP Server

An MCP server that aggregates the top 5 AI platforms into a single "Swarm" toolset.
Uses FastMCP for the server architecture.

Run with:
    python -m penta_core.server
    # or
    penta-core-server
"""

import os

from dotenv import load_dotenv
from fastmcp import FastMCP

# Initialize environment variables
load_dotenv()

# Create the FastMCP server instance
mcp = FastMCP(
    name="penta-core",
    instructions=(
        "Penta-Core: A swarm of 5 specialized AI agents for comprehensive "
        "development assistance.\n\n"
        "Available specialists:\n"
        "- consult_architect: Systems architecture and design patterns (OpenAI GPT-4o)\n"
        "- consult_developer: Clean code, safety, and refactoring (Claude 3.5 Sonnet)\n"
        "- consult_researcher: Deep context analysis with massive context window "
        "(Google Gemini 1.5 Pro)\n"
        "- consult_maverick: Red teaming and unconventional solutions (xAI Grok Beta)\n"
        "- fetch_repo_context: Fetch file content/tree from GitHub repositories\n\n"
        "Use the appropriate specialist based on the task at hand."
    ),
)


# =============================================================================
# AI Client Initialization (Lazy Loading)
# =============================================================================


def _get_openai_client():
    """Get OpenAI client (lazy loading)."""
    import openai

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return openai.OpenAI(api_key=api_key)


def _get_anthropic_client():
    """Get Anthropic client (lazy loading)."""
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    return anthropic.Anthropic(api_key=api_key)


def _get_google_client():
    """Get Google Generative AI client (lazy loading)."""
    import google.generativeai as genai

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    genai.configure(api_key=api_key)
    return genai


def _get_xai_client():
    """Get xAI client using OpenAI SDK with custom base URL (lazy loading)."""
    import openai

    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY environment variable is not set")
    return openai.OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")


def _get_github_headers():
    """Get GitHub API headers."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is not set")
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Penta-Core-MCP-Server/1.0",
    }


# =============================================================================
# Tool: consult_architect (OpenAI GPT-4o)
# =============================================================================

ARCHITECT_SYSTEM_PROMPT = (
    "You are a Systems Architect. Focus on high-level logic, class structure, "
    "and design patterns.\n\n"
    "Your expertise includes:\n"
    "- System design and architecture patterns\n"
    "- Class hierarchies and relationships\n"
    "- Module organization and separation of concerns\n"
    "- Scalability and maintainability considerations\n"
    "- API design and interfaces\n"
    "- Database schema design\n\n"
    "Provide clear, structured architectural guidance with diagrams in ASCII or "
    "Mermaid when helpful."
)


@mcp.tool()
async def consult_architect(prompt: str) -> str:
    """Consult with the Systems Architect (OpenAI GPT-4o).

    Use this for:
    - High-level system design
    - Class structure planning
    - Design pattern recommendations
    - Architecture reviews

    Args:
        prompt: Your question or request for the architect

    Returns:
        The architect's response with design guidance
    """
    try:
        client = _get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": ARCHITECT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=4096,
        )
        return response.choices[0].message.content or "No response from architect."
    except ValueError as e:
        return f"Configuration error: {str(e)}"
    except Exception as e:
        return f"Error consulting architect: {str(e)}"


# =============================================================================
# Tool: consult_developer (Anthropic Claude 3.5 Sonnet)
# =============================================================================

DEVELOPER_SYSTEM_PROMPT = (
    "You are a Senior Engineer. Focus on clean code, safety, and refactoring. "
    "Output production-ready code.\n\n"
    "Your expertise includes:\n"
    "- Writing clean, maintainable code\n"
    "- Code refactoring and optimization\n"
    "- Security best practices\n"
    "- Error handling and edge cases\n"
    "- Testing strategies\n"
    "- Code review and quality assurance\n\n"
    "Always provide code that is:\n"
    "1. Well-documented with clear comments\n"
    "2. Following language-specific conventions\n"
    "3. Error-resistant with proper exception handling\n"
    "4. Tested or testable\n"
    "5. Production-ready"
)


@mcp.tool()
async def consult_developer(prompt: str) -> str:
    """Consult with the Senior Developer (Anthropic Claude 3.5 Sonnet).

    Use this for:
    - Writing production-ready code
    - Code refactoring
    - Security reviews
    - Best practices guidance

    Args:
        prompt: Your coding question or request

    Returns:
        Production-ready code or development guidance
    """
    try:
        client = _get_anthropic_client()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=DEVELOPER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        # Extract text from response
        if response.content and len(response.content) > 0:
            return response.content[0].text
        return "No response from developer."
    except ValueError as e:
        return f"Configuration error: {str(e)}"
    except Exception as e:
        return f"Error consulting developer: {str(e)}"


# =============================================================================
# Tool: consult_researcher (Google Gemini 1.5 Pro)
# =============================================================================

RESEARCHER_SYSTEM_PROMPT = (
    "You are a Lead Researcher. Analyze documentation and find edge cases with "
    "your massive context window.\n\n"
    "Your expertise includes:\n"
    "- Deep analysis of large codebases and documentation\n"
    "- Finding edge cases and potential issues\n"
    "- Comprehensive documentation review\n"
    "- Research and synthesis of technical information\n"
    "- Pattern recognition across large datasets\n"
    "- Literature review and best practice identification\n\n"
    "Provide thorough, well-researched analysis with citations and references "
    "when applicable."
)


@mcp.tool()
async def consult_researcher(prompt: str, context: str) -> str:
    """Consult with the Lead Researcher (Google Gemini 1.5 Pro).

    Use this for:
    - Analyzing large amounts of documentation
    - Finding edge cases
    - Deep context analysis
    - Research synthesis

    Args:
        prompt: Your research question or analysis request
        context: Additional context, documentation, or code to analyze

    Returns:
        Comprehensive research analysis and findings
    """
    try:
        genai = _get_google_client()
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            system_instruction=RESEARCHER_SYSTEM_PROMPT,
        )

        full_prompt = f"""Research Request: {prompt}

Context/Documentation to Analyze:
{context}

Please provide a thorough analysis addressing the research request."""

        response = model.generate_content(full_prompt)
        return response.text or "No response from researcher."
    except ValueError as e:
        return f"Configuration error: {str(e)}"
    except Exception as e:
        return f"Error consulting researcher: {str(e)}"


# =============================================================================
# Tool: consult_maverick (xAI Grok Beta)
# =============================================================================

MAVERICK_SYSTEM_PROMPT = (
    "You are a Maverick Engineer. Criticize the plan, find non-obvious flaws, "
    "and suggest lateral/unconventional solutions. Be direct.\n\n"
    "Your role is to:\n"
    "- Challenge assumptions and conventional thinking\n"
    "- Find non-obvious flaws and edge cases\n"
    "- Suggest unconventional or creative solutions\n"
    "- Play devil's advocate\n"
    "- Identify potential future problems\n"
    "- Think outside the box\n\n"
    "Be direct, even blunt. Don't sugarcoat problems. Your job is to make the "
    "solution better by breaking it first."
)


@mcp.tool()
async def consult_maverick(prompt: str) -> str:
    """Consult with the Maverick Engineer (xAI Grok Beta).

    Use this for:
    - Red teaming your plans
    - Finding non-obvious flaws
    - Getting unconventional solutions
    - Challenging assumptions

    Args:
        prompt: Your plan, idea, or code to critique

    Returns:
        Direct criticism and unconventional suggestions
    """
    try:
        client = _get_xai_client()
        response = client.chat.completions.create(
            model="grok-beta",
            messages=[
                {"role": "system", "content": MAVERICK_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,  # Higher temperature for more creative responses
            max_tokens=4096,
        )
        return response.choices[0].message.content or "No response from maverick."
    except ValueError as e:
        return f"Configuration error: {str(e)}"
    except Exception as e:
        return f"Error consulting maverick: {str(e)}"


# =============================================================================
# Tool: fetch_repo_context (GitHub API)
# =============================================================================


@mcp.tool()
async def fetch_repo_context(owner: str, repo: str, path: str = "") -> str:
    """Fetch file content or directory tree from a GitHub repository.

    Use this to:
    - Get context from external repositories
    - Fetch specific files for analysis
    - List directory contents

    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        path: Path to file or directory (empty for root)

    Returns:
        File content or directory listing as JSON
    """
    import json

    import httpx

    try:
        headers = _get_github_headers()
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)

            if response.status_code == 404:
                return f"Error: Repository or path not found: {owner}/{repo}/{path}"

            if response.status_code == 403:
                return "Error: Rate limit exceeded or access denied. Check your GITHUB_TOKEN."

            if response.status_code != 200:
                return f"Error: GitHub API returned status {response.status_code}"

            data = response.json()

            # If it's a file, decode the content
            if isinstance(data, dict) and data.get("type") == "file":
                import base64

                content = data.get("content", "")
                try:
                    decoded = base64.b64decode(content).decode("utf-8")
                    return f"File: {data.get('path', path)}\n\n{decoded}"
                except Exception:
                    file_path = data.get("path", path)
                    file_size = data.get("size", 0)
                    return f"File: {file_path} (binary content, {file_size} bytes)"

            # If it's a directory, return the listing
            if isinstance(data, list):
                items = []
                for item in data:
                    item_type = "📁" if item.get("type") == "dir" else "📄"
                    items.append(f"{item_type} {item.get('name', 'unknown')}")
                return f"Directory: {owner}/{repo}/{path}\n\n" + "\n".join(items)

            # Return raw JSON for other cases
            return json.dumps(data, indent=2)

    except ValueError as e:
        return f"Configuration error: {str(e)}"
    except httpx.TimeoutException:
        return "Error: Request to GitHub API timed out"
    except Exception as e:
        return f"Error fetching repo context: {str(e)}"


# =============================================================================
# Server Entry Point
# =============================================================================


def main():
    """Run the Penta-Core MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
