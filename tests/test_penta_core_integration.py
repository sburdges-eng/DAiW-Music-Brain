"""
Tests for penta-core integration module.

Run with: pytest tests/test_penta_core_integration.py -v
"""

import pytest


class TestPentaCoreIntegrationImports:
    """Test that integration modules can be imported."""

    def test_import_integration_module(self):
        from music_brain.integrations import PentaCoreIntegration

        assert PentaCoreIntegration is not None

    def test_import_penta_core_module(self):
        from music_brain.integrations.penta_core import (
            PentaCoreIntegration,
            PentaCoreConfig,
        )

        assert PentaCoreIntegration is not None
        assert PentaCoreConfig is not None


class TestPentaCoreConfig:
    """Test PentaCoreConfig dataclass."""

    def test_default_config(self):
        from music_brain.integrations.penta_core import PentaCoreConfig

        config = PentaCoreConfig()
        assert config.endpoint_url is None
        assert config.api_key is None
        assert config.timeout_seconds == 30
        assert config.verify_ssl is True

    def test_custom_config(self):
        from music_brain.integrations.penta_core import PentaCoreConfig

        config = PentaCoreConfig(
            endpoint_url="http://localhost:8000",
            api_key="test-key",
            timeout_seconds=60,
            verify_ssl=False,
        )
        assert config.endpoint_url == "http://localhost:8000"
        assert config.api_key == "test-key"
        assert config.timeout_seconds == 60
        assert config.verify_ssl is False

    def test_config_serialization(self):
        from music_brain.integrations.penta_core import PentaCoreConfig

        config = PentaCoreConfig(
            endpoint_url="http://example.com",
            api_key="my-key",
            timeout_seconds=45,
        )
        data = config.to_dict()

        assert data["endpoint_url"] == "http://example.com"
        assert data["api_key"] == "my-key"
        assert data["timeout_seconds"] == 45
        assert data["verify_ssl"] is True

    def test_config_deserialization(self):
        from music_brain.integrations.penta_core import PentaCoreConfig

        data = {
            "endpoint_url": "http://test.com",
            "api_key": "secret",
            "timeout_seconds": 15,
            "verify_ssl": False,
        }
        config = PentaCoreConfig.from_dict(data)

        assert config.endpoint_url == "http://test.com"
        assert config.api_key == "secret"
        assert config.timeout_seconds == 15
        assert config.verify_ssl is False


class TestPentaCoreIntegration:
    """Test PentaCoreIntegration class."""

    def test_initialization_default(self):
        from music_brain.integrations.penta_core import PentaCoreIntegration

        integration = PentaCoreIntegration()
        assert integration.config is not None
        assert integration.config.endpoint_url is None

    def test_initialization_with_config(self):
        from music_brain.integrations.penta_core import (
            PentaCoreIntegration,
            PentaCoreConfig,
        )

        config = PentaCoreConfig(endpoint_url="http://localhost:8000")
        integration = PentaCoreIntegration(config=config)

        assert integration.config.endpoint_url == "http://localhost:8000"

    def test_is_connected_default(self):
        from music_brain.integrations.penta_core import PentaCoreIntegration

        integration = PentaCoreIntegration()
        assert integration.is_connected() is False

    def test_connect_without_endpoint_raises(self):
        from music_brain.integrations.penta_core import PentaCoreIntegration

        integration = PentaCoreIntegration()
        with pytest.raises(ValueError, match="endpoint_url not configured"):
            integration.connect()

    def test_disconnect(self):
        from music_brain.integrations.penta_core import PentaCoreIntegration

        integration = PentaCoreIntegration()
        integration.disconnect()  # Should not raise
        assert integration.is_connected() is False

    def test_send_intent_not_connected_raises(self):
        from music_brain.integrations.penta_core import PentaCoreIntegration

        integration = PentaCoreIntegration()
        with pytest.raises(ConnectionError, match="Not connected"):
            integration.send_intent({"test": "intent"})

    def test_send_groove_not_connected_raises(self):
        from music_brain.integrations.penta_core import PentaCoreIntegration

        integration = PentaCoreIntegration()
        with pytest.raises(ConnectionError, match="Not connected"):
            integration.send_groove({"test": "groove"})

    def test_send_analysis_not_connected_raises(self):
        from music_brain.integrations.penta_core import PentaCoreIntegration

        integration = PentaCoreIntegration()
        with pytest.raises(ConnectionError, match="Not connected"):
            integration.send_analysis({"test": "analysis"})

    def test_receive_suggestions_not_connected_raises(self):
        from music_brain.integrations.penta_core import PentaCoreIntegration

        integration = PentaCoreIntegration()
        with pytest.raises(ConnectionError, match="Not connected"):
            integration.receive_suggestions()

    def test_receive_feedback_not_connected_raises(self):
        from music_brain.integrations.penta_core import PentaCoreIntegration

        integration = PentaCoreIntegration()
        with pytest.raises(ConnectionError, match="Not connected"):
            integration.receive_feedback()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
