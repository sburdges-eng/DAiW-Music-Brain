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

    def test_import_cpp_bridge_classes(self):
        from music_brain.integrations import (
            CppBridge,
            CppBridgeConfig,
            BridgeType,
            ThreadingMode,
        )

        assert CppBridge is not None
        assert CppBridgeConfig is not None
        assert BridgeType is not None
        assert ThreadingMode is not None

    def test_import_osc_bridge_classes(self):
        from music_brain.integrations import OSCBridge, OSCMessage

        assert OSCBridge is not None
        assert OSCMessage is not None

    def test_import_data_structures(self):
        from music_brain.integrations import MidiEvent, MidiBuffer, KnobState

        assert MidiEvent is not None
        assert MidiBuffer is not None
        assert KnobState is not None


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


# =============================================================================
# Phase 3: C++/pybind11 Bridge Layer Tests
# =============================================================================


class TestBridgeEnums:
    """Test bridge-related enumerations."""

    def test_bridge_type_values(self):
        from music_brain.integrations import BridgeType

        assert BridgeType.PYBIND11.value == "pybind11"
        assert BridgeType.OSC.value == "osc"
        assert BridgeType.HYBRID.value == "hybrid"

    def test_threading_mode_values(self):
        from music_brain.integrations import ThreadingMode

        assert ThreadingMode.SYNC.value == "sync"
        assert ThreadingMode.ASYNC.value == "async"
        assert ThreadingMode.REALTIME_SAFE.value == "realtime_safe"


class TestCppBridgeConfig:
    """Test CppBridgeConfig dataclass."""

    def test_default_config(self):
        from music_brain.integrations import CppBridgeConfig, BridgeType, ThreadingMode

        config = CppBridgeConfig()
        assert config.bridge_type == BridgeType.PYBIND11
        assert config.osc_host == "127.0.0.1"
        assert config.osc_send_port == 9001
        assert config.osc_receive_port == 9000
        assert config.threading_mode == ThreadingMode.ASYNC
        assert config.enable_ghost_hands is True
        assert config.python_module_path is None
        assert config.genres_json_path is None

    def test_custom_config(self):
        from music_brain.integrations import CppBridgeConfig, BridgeType, ThreadingMode

        config = CppBridgeConfig(
            bridge_type=BridgeType.OSC,
            osc_host="192.168.1.100",
            osc_send_port=8001,
            osc_receive_port=8000,
            threading_mode=ThreadingMode.REALTIME_SAFE,
            enable_ghost_hands=False,
            python_module_path="/path/to/music_brain",
            genres_json_path="/path/to/genres.json",
        )
        assert config.bridge_type == BridgeType.OSC
        assert config.osc_host == "192.168.1.100"
        assert config.osc_send_port == 8001
        assert config.osc_receive_port == 8000
        assert config.threading_mode == ThreadingMode.REALTIME_SAFE
        assert config.enable_ghost_hands is False

    def test_config_serialization(self):
        from music_brain.integrations import CppBridgeConfig, BridgeType

        config = CppBridgeConfig(bridge_type=BridgeType.HYBRID)
        data = config.to_dict()

        assert data["bridge_type"] == "hybrid"
        assert data["osc_host"] == "127.0.0.1"
        assert data["osc_send_port"] == 9001
        assert data["osc_receive_port"] == 9000

    def test_config_deserialization(self):
        from music_brain.integrations import CppBridgeConfig, BridgeType, ThreadingMode

        data = {
            "bridge_type": "osc",
            "osc_host": "localhost",
            "osc_send_port": 7001,
            "osc_receive_port": 7000,
            "threading_mode": "sync",
            "enable_ghost_hands": False,
        }
        config = CppBridgeConfig.from_dict(data)

        assert config.bridge_type == BridgeType.OSC
        assert config.osc_send_port == 7001
        assert config.threading_mode == ThreadingMode.SYNC
        assert config.enable_ghost_hands is False


class TestMidiEvent:
    """Test MidiEvent dataclass."""

    def test_default_values(self):
        from music_brain.integrations import MidiEvent

        event = MidiEvent(status=0x90, data1=60, data2=100)
        assert event.status == 0x90
        assert event.data1 == 60
        assert event.data2 == 100
        assert event.timestamp == 0

    def test_note_on_factory(self):
        from music_brain.integrations import MidiEvent

        event = MidiEvent.note_on(60, 80, timestamp=480)
        assert event.status == 0x90
        assert event.data1 == 60
        assert event.data2 == 80
        assert event.timestamp == 480

    def test_note_off_factory(self):
        from music_brain.integrations import MidiEvent

        event = MidiEvent.note_off(60, timestamp=960)
        assert event.status == 0x80
        assert event.data1 == 60
        assert event.data2 == 0
        assert event.timestamp == 960

    def test_serialization(self):
        from music_brain.integrations import MidiEvent

        event = MidiEvent.note_on(64, 100, 120)
        data = event.to_dict()

        assert data["status"] == 0x90
        assert data["data1"] == 64
        assert data["data2"] == 100
        assert data["timestamp"] == 120

    def test_deserialization(self):
        from music_brain.integrations import MidiEvent

        data = {"status": 0x80, "data1": 67, "data2": 0, "timestamp": 240}
        event = MidiEvent.from_dict(data)

        assert event.status == 0x80
        assert event.data1 == 67
        assert event.data2 == 0
        assert event.timestamp == 240


class TestKnobState:
    """Test KnobState dataclass."""

    def test_default_values(self):
        from music_brain.integrations import KnobState

        knobs = KnobState()
        assert knobs.grid == 16.0
        assert knobs.gate == 0.8
        assert knobs.swing == 0.5
        assert knobs.chaos == 0.5
        assert knobs.complexity == 0.5

    def test_custom_values(self):
        from music_brain.integrations import KnobState

        knobs = KnobState(grid=8.0, gate=0.6, swing=0.58, chaos=0.7, complexity=0.8)
        assert knobs.grid == 8.0
        assert knobs.gate == 0.6
        assert knobs.swing == 0.58
        assert knobs.chaos == 0.7
        assert knobs.complexity == 0.8

    def test_serialization(self):
        from music_brain.integrations import KnobState

        knobs = KnobState(chaos=0.9, complexity=0.3)
        data = knobs.to_dict()

        assert data["chaos"] == 0.9
        assert data["complexity"] == 0.3
        assert data["grid"] == 16.0

    def test_deserialization(self):
        from music_brain.integrations import KnobState

        data = {"grid": 32.0, "gate": 0.5, "swing": 0.66, "chaos": 0.1, "complexity": 0.9}
        knobs = KnobState.from_dict(data)

        assert knobs.grid == 32.0
        assert knobs.swing == 0.66
        assert knobs.chaos == 0.1


class TestMidiBuffer:
    """Test MidiBuffer dataclass."""

    def test_default_values(self):
        from music_brain.integrations import MidiBuffer

        buffer = MidiBuffer()
        assert buffer.events == []
        assert buffer.suggested_chaos == 0.5
        assert buffer.suggested_complexity == 0.5
        assert buffer.genre == ""
        assert buffer.success is True
        assert buffer.error_message == ""

    def test_failsafe_buffer(self):
        from music_brain.integrations import MidiBuffer

        buffer = MidiBuffer.failsafe()

        # Should have C major chord (6 events: 3 note on, 3 note off)
        assert len(buffer.events) == 6
        assert buffer.success is False
        assert "fail-safe" in buffer.error_message
        assert buffer.genre == "fail_safe"

        # Check C major chord notes (C4, E4, G4)
        note_ons = [e for e in buffer.events if e.status == 0x90]
        assert len(note_ons) == 3
        notes = {e.data1 for e in note_ons}
        assert notes == {60, 64, 67}

    def test_serialization(self):
        from music_brain.integrations import MidiBuffer, MidiEvent

        buffer = MidiBuffer(
            events=[MidiEvent.note_on(60, 100)],
            suggested_chaos=0.7,
            genre="jazz",
            success=True,
        )
        data = buffer.to_dict()

        assert len(data["events"]) == 1
        assert data["suggested_chaos"] == 0.7
        assert data["genre"] == "jazz"
        assert data["success"] is True

    def test_deserialization(self):
        from music_brain.integrations import MidiBuffer

        data = {
            "events": [{"status": 0x90, "data1": 64, "data2": 80, "timestamp": 0}],
            "suggested_chaos": 0.3,
            "suggested_complexity": 0.8,
            "genre": "funk",
            "success": True,
            "error_message": "",
        }
        buffer = MidiBuffer.from_dict(data)

        assert len(buffer.events) == 1
        assert buffer.events[0].data1 == 64
        assert buffer.suggested_chaos == 0.3
        assert buffer.genre == "funk"


class TestCppBridge:
    """Test CppBridge class."""

    def test_initialization_default(self):
        from music_brain.integrations import CppBridge

        bridge = CppBridge()
        assert bridge.config is not None
        assert bridge.is_initialized() is False
        assert bridge.rejection_count == 0

    def test_initialization_with_config(self):
        from music_brain.integrations import CppBridge, CppBridgeConfig, BridgeType

        config = CppBridgeConfig(bridge_type=BridgeType.HYBRID)
        bridge = CppBridge(config=config)

        assert bridge.config.bridge_type == BridgeType.HYBRID

    def test_initialize_stub(self):
        from music_brain.integrations import CppBridge

        bridge = CppBridge()
        # Stub returns False (not implemented)
        result = bridge.initialize("/path/to/module", "/path/to/genres.json")
        assert result is False
        assert bridge.is_initialized() is False

    def test_shutdown(self):
        from music_brain.integrations import CppBridge

        bridge = CppBridge()
        bridge.shutdown()  # Should not raise
        assert bridge.is_initialized() is False

    def test_call_imidi_not_initialized_raises(self):
        from music_brain.integrations import CppBridge, KnobState

        bridge = CppBridge()
        knobs = KnobState()

        with pytest.raises(RuntimeError, match="not initialized"):
            bridge.call_imidi(knobs, "test prompt")

    def test_rejection_protocol(self):
        from music_brain.integrations import CppBridge

        bridge = CppBridge()

        assert bridge.rejection_count == 0
        assert bridge.should_trigger_innovation() is False

        bridge.register_rejection()
        assert bridge.rejection_count == 1

        bridge.register_rejection()
        bridge.register_rejection()
        assert bridge.rejection_count == 3
        assert bridge.should_trigger_innovation() is True

        bridge.reset_rejection_counter()
        assert bridge.rejection_count == 0
        assert bridge.should_trigger_innovation() is False

    def test_ghost_hands_callback(self):
        from music_brain.integrations import CppBridge

        bridge = CppBridge()
        callback_called = []

        def on_ghost_hands(chaos: float, complexity: float):
            callback_called.append((chaos, complexity))

        bridge.set_ghost_hands_callback(on_ghost_hands)
        assert bridge._ghost_hands_callback is not None


class TestOSCBridge:
    """Test OSCBridge class."""

    def test_initialization_default(self):
        from music_brain.integrations import OSCBridge

        osc = OSCBridge()
        assert osc.config is not None
        assert osc.is_running() is False

    def test_initialization_with_config(self):
        from music_brain.integrations import OSCBridge, CppBridgeConfig, BridgeType

        config = CppBridgeConfig(
            bridge_type=BridgeType.OSC,
            osc_send_port=8001,
        )
        osc = OSCBridge(config=config)

        assert osc.config.osc_send_port == 8001

    def test_start_stop(self):
        from music_brain.integrations import OSCBridge

        osc = OSCBridge()

        # Stub returns False
        result = osc.start()
        assert result is False
        assert osc.is_running() is False

        osc.stop()
        assert osc.is_running() is False

    def test_register_handler(self):
        from music_brain.integrations import OSCBridge

        osc = OSCBridge()

        def handler(chaos: float, vuln: float):
            pass

        osc.register_handler("/daiw/generate", handler)
        assert "/daiw/generate" in osc._handlers
        assert osc._handlers["/daiw/generate"] is handler

    def test_send_methods_do_not_raise(self):
        from music_brain.integrations import OSCBridge

        osc = OSCBridge()

        # Stub methods should not raise
        osc.send_midi_note(60, 100, 500)
        osc.send_chord([60, 64, 67], 80, 1000)
        osc.send_progression('{"chords": ["C", "G", "Am"]}')
        osc.send_status("ready")

    def test_ping(self):
        from music_brain.integrations import OSCBridge

        osc = OSCBridge()
        # Stub returns False
        result = osc.ping()
        assert result is False


class TestOSCMessage:
    """Test OSCMessage dataclass."""

    def test_basic_message(self):
        from music_brain.integrations import OSCMessage

        msg = OSCMessage(address="/daiw/generate", args=[0.5, 0.3])
        assert msg.address == "/daiw/generate"
        assert msg.args == [0.5, 0.3]

    def test_empty_args(self):
        from music_brain.integrations import OSCMessage

        msg = OSCMessage(address="/daiw/ping")
        assert msg.address == "/daiw/ping"
        assert msg.args == []

    def test_serialization(self):
        from music_brain.integrations import OSCMessage

        msg = OSCMessage(address="/daiw/midi/note", args=[60, 100, 500])
        data = msg.to_dict()

        assert data["address"] == "/daiw/midi/note"
        assert data["args"] == [60, 100, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
