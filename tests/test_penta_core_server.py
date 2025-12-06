"""
Tests for Penta-Core MCP Server.

Run with: pytest tests/test_penta_core_server.py -v
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestPentaCoreServerImports:
    """Test that server modules can be imported."""

    def test_import_server_module(self):
        from penta_core import server

        assert server is not None

    def test_import_mcp_instance(self):
        from penta_core.server import mcp

        assert mcp is not None
        assert mcp.name == "penta-core"

    def test_import_tool_functions(self):
        from penta_core.server import (
            consult_architect,
            consult_developer,
            consult_maverick,
            consult_researcher,
            fetch_repo_context,
        )

        assert consult_architect is not None
        assert consult_developer is not None
        assert consult_researcher is not None
        assert consult_maverick is not None
        assert fetch_repo_context is not None


class TestPentaCoreClientInitialization:
    """Test client initialization functions."""

    def test_get_openai_client_missing_key(self):
        from penta_core.server import _get_openai_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
            # Remove the key if it exists
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                _get_openai_client()

    def test_get_anthropic_client_missing_key(self):
        from penta_core.server import _get_anthropic_client

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}, clear=False):
            if "ANTHROPIC_API_KEY" in os.environ:
                del os.environ["ANTHROPIC_API_KEY"]
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                _get_anthropic_client()

    def test_get_google_client_missing_key(self):
        from penta_core.server import _get_google_client

        with patch.dict(os.environ, {"GOOGLE_API_KEY": ""}, clear=False):
            if "GOOGLE_API_KEY" in os.environ:
                del os.environ["GOOGLE_API_KEY"]
            with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
                _get_google_client()

    def test_get_xai_client_missing_key(self):
        from penta_core.server import _get_xai_client

        with patch.dict(os.environ, {"XAI_API_KEY": ""}, clear=False):
            if "XAI_API_KEY" in os.environ:
                del os.environ["XAI_API_KEY"]
            with pytest.raises(ValueError, match="XAI_API_KEY"):
                _get_xai_client()

    def test_get_github_headers_missing_token(self):
        from penta_core.server import _get_github_headers

        with patch.dict(os.environ, {"GITHUB_TOKEN": ""}, clear=False):
            if "GITHUB_TOKEN" in os.environ:
                del os.environ["GITHUB_TOKEN"]
            with pytest.raises(ValueError, match="GITHUB_TOKEN"):
                _get_github_headers()


class TestConsultArchitect:
    """Test consult_architect tool."""

    @pytest.mark.asyncio
    async def test_consult_architect_missing_api_key(self):
        from penta_core.server import consult_architect

        # Access the underlying function via .fn attribute
        fn = consult_architect.fn
        with patch.dict(os.environ, {}, clear=True):
            result = await fn("Design a REST API")
            assert "Configuration error" in result or "OPENAI_API_KEY" in result

    @pytest.mark.asyncio
    async def test_consult_architect_success(self):
        from penta_core.server import consult_architect

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Architectural guidance"))]

        fn = consult_architect.fn
        with patch("penta_core.server._get_openai_client") as mock_client:
            mock_client.return_value.chat.completions.create.return_value = mock_response
            result = await fn("Design a REST API")
            assert result == "Architectural guidance"


class TestConsultDeveloper:
    """Test consult_developer tool."""

    @pytest.mark.asyncio
    async def test_consult_developer_missing_api_key(self):
        from penta_core.server import consult_developer

        fn = consult_developer.fn
        with patch.dict(os.environ, {}, clear=True):
            result = await fn("Refactor this code")
            assert "Configuration error" in result or "ANTHROPIC_API_KEY" in result

    @pytest.mark.asyncio
    async def test_consult_developer_success(self):
        from penta_core.server import consult_developer

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Refactored code here")]

        fn = consult_developer.fn
        with patch("penta_core.server._get_anthropic_client") as mock_client:
            mock_client.return_value.messages.create.return_value = mock_response
            result = await fn("Refactor this code")
            assert result == "Refactored code here"


class TestConsultResearcher:
    """Test consult_researcher tool."""

    @pytest.mark.asyncio
    async def test_consult_researcher_missing_api_key(self):
        from penta_core.server import consult_researcher

        fn = consult_researcher.fn
        with patch.dict(os.environ, {}, clear=True):
            result = await fn("Research topic", "Context text")
            assert "Configuration error" in result or "GOOGLE_API_KEY" in result

    @pytest.mark.asyncio
    async def test_consult_researcher_success(self):
        from penta_core.server import consult_researcher

        mock_response = MagicMock()
        mock_response.text = "Research findings"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        fn = consult_researcher.fn
        with patch("penta_core.server._get_google_client") as mock_client:
            mock_client.return_value.GenerativeModel.return_value = mock_model
            result = await fn("Research topic", "Context text")
            assert result == "Research findings"


class TestConsultMaverick:
    """Test consult_maverick tool."""

    @pytest.mark.asyncio
    async def test_consult_maverick_missing_api_key(self):
        from penta_core.server import consult_maverick

        fn = consult_maverick.fn
        with patch.dict(os.environ, {}, clear=True):
            result = await fn("Critique this plan")
            assert "Configuration error" in result or "XAI_API_KEY" in result

    @pytest.mark.asyncio
    async def test_consult_maverick_success(self):
        from penta_core.server import consult_maverick

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Critical feedback"))]

        fn = consult_maverick.fn
        with patch("penta_core.server._get_xai_client") as mock_client:
            mock_client.return_value.chat.completions.create.return_value = mock_response
            result = await fn("Critique this plan")
            assert result == "Critical feedback"


class TestFetchRepoContext:
    """Test fetch_repo_context tool."""

    @pytest.mark.asyncio
    async def test_fetch_repo_context_missing_token(self):
        from penta_core.server import fetch_repo_context

        fn = fetch_repo_context.fn
        with patch.dict(os.environ, {}, clear=True):
            result = await fn("owner", "repo", "path")
            assert "Configuration error" in result or "GITHUB_TOKEN" in result

    @pytest.mark.asyncio
    async def test_fetch_repo_context_file_success(self):
        from penta_core.server import fetch_repo_context

        import base64

        file_content = base64.b64encode(b"Hello, World!").decode()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "type": "file",
            "path": "README.md",
            "content": file_content,
        }

        fn = fetch_repo_context.fn
        with patch("penta_core.server._get_github_headers") as mock_headers:
            mock_headers.return_value = {"Authorization": "token test"}
            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                    return_value=mock_response
                )
                result = await fn("owner", "repo", "README.md")
                assert "Hello, World!" in result

    @pytest.mark.asyncio
    async def test_fetch_repo_context_directory_success(self):
        from penta_core.server import fetch_repo_context

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "src", "type": "dir"},
            {"name": "README.md", "type": "file"},
        ]

        fn = fetch_repo_context.fn
        with patch("penta_core.server._get_github_headers") as mock_headers:
            mock_headers.return_value = {"Authorization": "token test"}
            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                    return_value=mock_response
                )
                result = await fn("owner", "repo", "")
                assert "📁 src" in result
                assert "📄 README.md" in result

    @pytest.mark.asyncio
    async def test_fetch_repo_context_not_found(self):
        from penta_core.server import fetch_repo_context

        mock_response = MagicMock()
        mock_response.status_code = 404

        fn = fetch_repo_context.fn
        with patch("penta_core.server._get_github_headers") as mock_headers:
            mock_headers.return_value = {"Authorization": "token test"}
            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                    return_value=mock_response
                )
                result = await fn("owner", "repo", "nonexistent")
                assert "not found" in result


class TestSystemPrompts:
    """Test system prompts are properly defined."""

    def test_architect_system_prompt(self):
        from penta_core.server import ARCHITECT_SYSTEM_PROMPT

        assert "Systems Architect" in ARCHITECT_SYSTEM_PROMPT
        assert "design patterns" in ARCHITECT_SYSTEM_PROMPT

    def test_developer_system_prompt(self):
        from penta_core.server import DEVELOPER_SYSTEM_PROMPT

        assert "Senior Engineer" in DEVELOPER_SYSTEM_PROMPT
        assert "production-ready" in DEVELOPER_SYSTEM_PROMPT.lower()

    def test_researcher_system_prompt(self):
        from penta_core.server import RESEARCHER_SYSTEM_PROMPT

        assert "Lead Researcher" in RESEARCHER_SYSTEM_PROMPT
        assert "context window" in RESEARCHER_SYSTEM_PROMPT

    def test_maverick_system_prompt(self):
        from penta_core.server import MAVERICK_SYSTEM_PROMPT

        assert "Maverick Engineer" in MAVERICK_SYSTEM_PROMPT
        assert "unconventional" in MAVERICK_SYSTEM_PROMPT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
