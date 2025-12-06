"""
Penta-Core Integration Module.

This module provides the interface for integrating DAiW-Music-Brain
with the penta-core system (https://github.com/sburdges-eng/penta-core).

The integration follows DAiW-Music-Brain's core philosophy:
"Interrogate Before Generate" - emotional intent drives technical decisions.

Phase 3 Integration Architecture:
    - Python "brain" communicates with C++ "body" via pybind11 or OSC
    - Real-time audio processing happens in C++/JUCE
    - Intent processing and emotional analysis remain in Python
    - Bridge layer handles GIL management and thread safety

Usage:
    from music_brain.integrations.penta_core import PentaCoreIntegration

    integration = PentaCoreIntegration()

    # Send song intent to penta-core
    result = integration.send_intent(complete_song_intent)

    # Check connection status
    if integration.is_connected():
        suggestions = integration.receive_suggestions()

Bridge Usage (Phase 3):
    from music_brain.integrations.penta_core import CppBridgeConfig, CppBridge

    # Configure the C++ bridge
    bridge_config = CppBridgeConfig(
        bridge_type=BridgeType.PYBIND11,
        osc_send_port=9001,
        osc_receive_port=9000,
    )

    # Create bridge instance
    bridge = CppBridge(config=bridge_config)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


# =============================================================================
# Constants
# =============================================================================

# Default note duration in ticks (quarter note at 480 PPQ)
DEFAULT_NOTE_DURATION_TICKS = 480

# Number of consecutive rejections before triggering innovation mode
INNOVATION_THRESHOLD = 3


@dataclass
class PentaCoreConfig:
    """Configuration for penta-core integration.

    Attributes:
        endpoint_url: The URL of the penta-core service endpoint.
        api_key: Optional API key for authentication.
        timeout_seconds: Request timeout in seconds.
        verify_ssl: Whether to verify SSL certificates.
    """

    endpoint_url: Optional[str] = None
    api_key: Optional[str] = None
    timeout_seconds: int = 30
    verify_ssl: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            "endpoint_url": self.endpoint_url,
            "api_key": self.api_key,
            "timeout_seconds": self.timeout_seconds,
            "verify_ssl": self.verify_ssl,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PentaCoreConfig":
        """Create configuration from dictionary."""
        return cls(
            endpoint_url=data.get("endpoint_url"),
            api_key=data.get("api_key"),
            timeout_seconds=data.get("timeout_seconds", 30),
            verify_ssl=data.get("verify_ssl", True),
        )


class PentaCoreIntegration:
    """Integration interface for penta-core system.

    This class provides methods for communicating with the penta-core
    service, enabling data exchange while preserving emotional intent
    context from DAiW-Music-Brain's three-phase intent schema.

    The integration supports:
    - Sending song intents (Phase 0, 1, 2 data)
    - Sending groove templates
    - Sending chord progression analysis
    - Receiving suggestions and feedback

    Example:
        >>> from music_brain.integrations.penta_core import PentaCoreIntegration
        >>> integration = PentaCoreIntegration()
        >>> integration.is_connected()
        False  # Not configured yet

        >>> from music_brain.integrations.penta_core import PentaCoreConfig
        >>> config = PentaCoreConfig(endpoint_url="http://localhost:8000")
        >>> integration = PentaCoreIntegration(config=config)

    Note:
        This is a placeholder implementation. Actual integration logic
        will be implemented once the penta-core API is defined.
    """

    def __init__(self, config: Optional[PentaCoreConfig] = None):
        """Initialize the penta-core integration.

        Args:
            config: Optional configuration for the integration.
                    If not provided, defaults will be used.
        """
        self._config = config or PentaCoreConfig()
        self._connected = False

    @property
    def config(self) -> PentaCoreConfig:
        """Get the current configuration."""
        return self._config

    def is_connected(self) -> bool:
        """Check if the integration is connected to penta-core.

        Returns:
            True if connected and authenticated, False otherwise.

        Note:
            This is a placeholder. Actual connection check will be
            implemented when penta-core API is available.
        """
        return self._connected and self._config.endpoint_url is not None

    def connect(self) -> bool:
        """Establish connection to penta-core service.

        Returns:
            True if connection was successful, False otherwise.

        Raises:
            ValueError: If endpoint_url is not configured.

        Note:
            This is a placeholder. Actual connection logic will be
            implemented when penta-core API is available.
        """
        if not self._config.endpoint_url:
            raise ValueError(
                "Cannot connect: endpoint_url not configured. "
                "Set config.endpoint_url before calling connect()."
            )

        # Placeholder: actual connection logic to be implemented
        # when penta-core API is defined
        self._connected = False
        return self._connected

    def disconnect(self) -> None:
        """Disconnect from penta-core service.

        Note:
            This is a placeholder. Actual disconnection logic will be
            implemented when penta-core API is available.
        """
        self._connected = False

    def send_intent(self, intent: Any) -> Dict[str, Any]:
        """Send a song intent to penta-core.

        Sends the complete song intent (Phase 0, 1, 2 data) to penta-core
        for processing. The emotional context from Phase 0 is preserved
        to ensure that any suggestions returned align with the creator's
        core wound/desire.

        Args:
            intent: A CompleteSongIntent object or compatible dict
                   containing the three-phase intent data.

        Returns:
            A dictionary containing the response from penta-core,
            including any processing status or immediate feedback.

        Raises:
            ConnectionError: If not connected to penta-core.

        Note:
            This is a placeholder. Actual implementation will serialize
            the intent and send it when penta-core API is available.
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to penta-core. Call connect() first.")

        # Placeholder: serialize and send intent
        # Preserve emotional context per DAiW philosophy
        return {
            "status": "not_implemented",
            "message": "Penta-core integration pending API definition",
        }

    def send_groove(self, groove_template: Any) -> Dict[str, Any]:
        """Send a groove template to penta-core.

        Sends extracted groove data for processing or storage.

        Args:
            groove_template: A GrooveTemplate object or compatible dict.

        Returns:
            A dictionary containing the response from penta-core.

        Raises:
            ConnectionError: If not connected to penta-core.

        Note:
            This is a placeholder implementation.
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to penta-core. Call connect() first.")

        return {
            "status": "not_implemented",
            "message": "Penta-core integration pending API definition",
        }

    def send_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Send chord progression analysis to penta-core.

        Sends analysis results including emotional character,
        rule breaks, and suggestions.

        Args:
            analysis: A dictionary containing progression analysis data.

        Returns:
            A dictionary containing the response from penta-core.

        Raises:
            ConnectionError: If not connected to penta-core.

        Note:
            This is a placeholder implementation.
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to penta-core. Call connect() first.")

        return {
            "status": "not_implemented",
            "message": "Penta-core integration pending API definition",
        }

    def receive_suggestions(self) -> List[str]:
        """Receive creative suggestions from penta-core.

        Retrieves suggestions that have been generated based on
        previously sent intents or analysis data.

        Returns:
            A list of suggestion strings.

        Raises:
            ConnectionError: If not connected to penta-core.

        Note:
            This is a placeholder implementation.
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to penta-core. Call connect() first.")

        return []

    def receive_feedback(self) -> Dict[str, Any]:
        """Receive processing feedback from penta-core.

        Retrieves feedback on previously sent data, including
        validation results and processing status.

        Returns:
            A dictionary containing feedback data.

        Raises:
            ConnectionError: If not connected to penta-core.

        Note:
            This is a placeholder implementation.
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to penta-core. Call connect() first.")

        return {
            "status": "not_implemented",
            "feedback": None,
        }


# =============================================================================
# Phase 3: C++/pybind11 Bridge Layer
# =============================================================================


class BridgeType(str, Enum):
    """Type of bridge connection to C++ layer.

    Attributes:
        PYBIND11: Direct Python/C++ interop via pybind11 bindings.
        OSC: Open Sound Control protocol over UDP (for real-time communication).
        HYBRID: Combination of pybind11 (for data) and OSC (for real-time signals).
    """

    PYBIND11 = "pybind11"
    OSC = "osc"
    HYBRID = "hybrid"


class ThreadingMode(str, Enum):
    """Threading mode for bridge operations.

    Attributes:
        SYNC: Synchronous calls (blocks until completion).
        ASYNC: Asynchronous calls with callback.
        REALTIME_SAFE: Special mode for audio-thread-safe operations.
    """

    SYNC = "sync"
    ASYNC = "async"
    REALTIME_SAFE = "realtime_safe"


@dataclass
class CppBridgeConfig:
    """Configuration for C++/pybind11 bridge connection.

    This configuration defines how Python communicates with the C++ layer
    in penta-core. It supports multiple bridge types for different use cases.

    Attributes:
        bridge_type: Type of bridge to use (pybind11, OSC, or hybrid).
        osc_host: Host address for OSC communication (default: localhost).
        osc_send_port: Port for sending OSC messages to C++ (default: 9001).
        osc_receive_port: Port for receiving OSC messages from C++ (default: 9000).
        threading_mode: Threading mode for bridge operations.
        enable_ghost_hands: Enable "Ghost Hands" feature (C++ can adjust Python params).
        python_module_path: Path to Python modules for pybind11 initialization.
        genres_json_path: Path to genre definitions JSON for C++ bridge.
    """

    bridge_type: BridgeType = BridgeType.PYBIND11
    osc_host: str = "127.0.0.1"
    osc_send_port: int = 9001
    osc_receive_port: int = 9000
    threading_mode: ThreadingMode = ThreadingMode.ASYNC
    enable_ghost_hands: bool = True
    python_module_path: Optional[str] = None
    genres_json_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            "bridge_type": self.bridge_type.value,
            "osc_host": self.osc_host,
            "osc_send_port": self.osc_send_port,
            "osc_receive_port": self.osc_receive_port,
            "threading_mode": self.threading_mode.value,
            "enable_ghost_hands": self.enable_ghost_hands,
            "python_module_path": self.python_module_path,
            "genres_json_path": self.genres_json_path,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CppBridgeConfig":
        """Create configuration from dictionary."""
        return cls(
            bridge_type=BridgeType(data.get("bridge_type", "pybind11")),
            osc_host=data.get("osc_host", "127.0.0.1"),
            osc_send_port=data.get("osc_send_port", 9001),
            osc_receive_port=data.get("osc_receive_port", 9000),
            threading_mode=ThreadingMode(data.get("threading_mode", "async")),
            enable_ghost_hands=data.get("enable_ghost_hands", True),
            python_module_path=data.get("python_module_path"),
            genres_json_path=data.get("genres_json_path"),
        )


@dataclass
class MidiEvent:
    """MIDI event data structure for C++ interop.

    Mirrors the C++ MidiEvent struct in PythonBridge.h.

    Attributes:
        status: MIDI status byte (e.g., 0x90 for note on, 0x80 for note off).
        data1: First data byte (typically note number).
        data2: Second data byte (typically velocity).
        timestamp: Event timestamp in samples or ticks.
    """

    status: int
    data1: int
    data2: int
    timestamp: int = 0

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary for serialization."""
        return {
            "status": self.status,
            "data1": self.data1,
            "data2": self.data2,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "MidiEvent":
        """Create from dictionary."""
        return cls(
            status=data["status"],
            data1=data["data1"],
            data2=data["data2"],
            timestamp=data.get("timestamp", 0),
        )

    @classmethod
    def note_on(cls, note: int, velocity: int, timestamp: int = 0) -> "MidiEvent":
        """Create a note-on event."""
        return cls(status=0x90, data1=note, data2=velocity, timestamp=timestamp)

    @classmethod
    def note_off(cls, note: int, timestamp: int = 0) -> "MidiEvent":
        """Create a note-off event."""
        return cls(status=0x80, data1=note, data2=0, timestamp=timestamp)


@dataclass
class KnobState:
    """UI knob state for C++ interop.

    Mirrors the C++ KnobState struct in PythonBridge.h.
    Represents the current state of Side B UI knobs.

    Attributes:
        grid: Grid resolution (4-32).
        gate: Note gate duration (0.1-1.0).
        swing: Swing amount (0.5-0.75).
        chaos: Chaos/randomization level (0-1).
        complexity: Harmonic/rhythmic complexity (0-1).
    """

    grid: float = 16.0
    gate: float = 0.8
    swing: float = 0.5
    chaos: float = 0.5
    complexity: float = 0.5

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for serialization/pybind11."""
        return {
            "grid": self.grid,
            "gate": self.gate,
            "swing": self.swing,
            "chaos": self.chaos,
            "complexity": self.complexity,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "KnobState":
        """Create from dictionary."""
        return cls(
            grid=data.get("grid", 16.0),
            gate=data.get("gate", 0.8),
            swing=data.get("swing", 0.5),
            chaos=data.get("chaos", 0.5),
            complexity=data.get("complexity", 0.5),
        )


@dataclass
class MidiBuffer:
    """MIDI buffer result from C++ processing.

    Mirrors the C++ MidiBuffer struct in PythonBridge.h.

    Attributes:
        events: List of MIDI events.
        suggested_chaos: AI-suggested chaos value ("Ghost Hands" feature).
        suggested_complexity: AI-suggested complexity value ("Ghost Hands" feature).
        genre: Detected or applied genre.
        success: Whether the operation was successful.
        error_message: Error message if operation failed.
    """

    events: List[MidiEvent] = field(default_factory=list)
    suggested_chaos: float = 0.5
    suggested_complexity: float = 0.5
    genre: str = ""
    success: bool = True
    error_message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "events": [e.to_dict() for e in self.events],
            "suggested_chaos": self.suggested_chaos,
            "suggested_complexity": self.suggested_complexity,
            "genre": self.genre,
            "success": self.success,
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MidiBuffer":
        """Create from dictionary."""
        events = [MidiEvent.from_dict(e) for e in data.get("events", [])]
        return cls(
            events=events,
            suggested_chaos=data.get("suggested_chaos", 0.5),
            suggested_complexity=data.get("suggested_complexity", 0.5),
            genre=data.get("genre", ""),
            success=data.get("success", True),
            error_message=data.get("error_message", ""),
        )

    @classmethod
    def failsafe(cls) -> "MidiBuffer":
        """Create a fail-safe MIDI buffer (C major chord).

        Returns a basic C major chord as fallback when C++ execution fails.
        This mirrors the createFailsafeMidiBuffer() in PythonBridge.cpp.
        """
        return cls(
            events=[
                MidiEvent.note_on(60, 80),  # C4
                MidiEvent.note_on(64, 80),  # E4
                MidiEvent.note_on(67, 80),  # G4
                MidiEvent(status=0x80, data1=60, data2=0, timestamp=DEFAULT_NOTE_DURATION_TICKS),
                MidiEvent(status=0x80, data1=64, data2=0, timestamp=DEFAULT_NOTE_DURATION_TICKS),
                MidiEvent(status=0x80, data1=67, data2=0, timestamp=DEFAULT_NOTE_DURATION_TICKS),
            ],
            success=False,
            error_message="Python execution failed - using fail-safe",
            genre="fail_safe",
        )


# Type alias for Ghost Hands callback
GhostHandsCallback = Callable[[float, float], None]


class CppBridge:
    """Bridge interface for C++/pybind11 communication.

    This class provides the Python-side interface for communicating with
    the C++ layer in penta-core. It mirrors the functionality defined in
    iDAW_Core/include/PythonBridge.h.

    The bridge supports:
    - Calling into C++ for MIDI generation (call_iMIDI)
    - Receiving "Ghost Hands" knob updates from C++
    - OSC-based real-time communication
    - Thread-safe operation with proper GIL management

    Example:
        >>> from music_brain.integrations.penta_core import CppBridge, CppBridgeConfig
        >>> config = CppBridgeConfig(bridge_type=BridgeType.PYBIND11)
        >>> bridge = CppBridge(config=config)
        >>> bridge.initialize("/path/to/music_brain", "/path/to/genres.json")
        True

    Note:
        This is a stub implementation. The actual bridge will be implemented
        when penta-core C++ modules are available.
    """

    def __init__(self, config: Optional[CppBridgeConfig] = None):
        """Initialize the C++ bridge.

        Args:
            config: Bridge configuration. If not provided, defaults will be used.
        """
        self._config = config or CppBridgeConfig()
        self._initialized = False
        self._ghost_hands_callback: Optional[GhostHandsCallback] = None
        self._rejection_count = 0

    @property
    def config(self) -> CppBridgeConfig:
        """Get the current configuration."""
        return self._config

    def is_initialized(self) -> bool:
        """Check if the bridge is initialized.

        Returns:
            True if the C++ interpreter is initialized, False otherwise.
        """
        return self._initialized

    def initialize(
        self, python_path: Optional[str] = None, genres_json_path: Optional[str] = None
    ) -> bool:
        """Initialize the C++ bridge and Python interpreter.

        This method initializes the embedded Python interpreter in C++ (Side B)
        and loads the genre definitions. Must be called from a non-audio thread.

        Args:
            python_path: Path to Python modules (music_brain package).
                        Overrides config if provided.
            genres_json_path: Path to GenreDefinitions.json.
                             Overrides config if provided.

        Returns:
            True if initialization was successful, False otherwise.

        Note:
            Stub implementation. Actual initialization will connect to
            the C++ PythonBridge::initialize() method via pybind11.
        """
        # Use provided paths or fall back to config
        self._config.python_module_path = python_path or self._config.python_module_path
        self._config.genres_json_path = genres_json_path or self._config.genres_json_path

        # Stub: actual implementation will call C++ initialization
        # self._initialized = idaw_bridge.PythonBridge.getInstance().initialize(...)
        self._initialized = False
        return self._initialized

    def shutdown(self) -> None:
        """Shutdown the C++ bridge.

        Cleans up the embedded Python interpreter and releases resources.
        Call before application exit.

        Note:
            Stub implementation. Actual shutdown will call
            C++ PythonBridge::shutdown() via pybind11.
        """
        self._initialized = False
        self._ghost_hands_callback = None

    def call_imidi(self, knobs: KnobState, text_prompt: str) -> MidiBuffer:
        """Call into C++ for MIDI generation.

        The main interface function for Brain→Body communication.
        Takes current knob state and text prompt, passes to C++ pipeline,
        returns MIDI buffer with events and suggested knob values.

        This mirrors PythonBridge::call_iMIDI() in C++.

        Args:
            knobs: Current UI knob values (grid, gate, swing, chaos, complexity).
            text_prompt: User text input describing the desired music.

        Returns:
            MidiBuffer with generated MIDI events and AI suggestions.

        Raises:
            RuntimeError: If bridge is not initialized.

        Note:
            Stub implementation. Actual call will invoke
            C++ PythonBridge::call_iMIDI() via pybind11.

            SAFETY: User input is sanitized in C++ before processing.
            Returns C major chord (fail-safe) if C++ execution fails.
        """
        if not self._initialized:
            raise RuntimeError("Bridge not initialized. Call initialize() first.")

        # Stub: actual implementation will call C++ method
        # result = idaw_bridge.PythonBridge.getInstance().call_iMIDI(
        #     knobs.to_dict(), text_prompt
        # )

        # Return fail-safe for stub
        return MidiBuffer.failsafe()

    def call_imidi_async(
        self, knobs: KnobState, text_prompt: str, callback: Callable[[MidiBuffer], None]
    ) -> None:
        """Async version of call_imidi for non-blocking UI.

        Args:
            knobs: Current UI knob values.
            text_prompt: User text input.
            callback: Function to call with result when complete.

        Note:
            Stub implementation. Actual call will use std::future
            via pybind11 or asyncio integration.
        """
        # Stub: would normally run in background thread
        result = MidiBuffer.failsafe()
        result.error_message = "Async call stub - bridge not implemented"
        callback(result)

    def set_ghost_hands_callback(self, callback: GhostHandsCallback) -> None:
        """Register callback for "Ghost Hands" knob updates.

        The "Ghost Hands" feature allows the C++ layer to suggest
        knob value changes based on AI analysis. When C++ suggests
        new chaos/complexity values, this callback is invoked.

        Args:
            callback: Function taking (chaos: float, complexity: float).

        Example:
            >>> def on_ghost_hands(chaos: float, complexity: float):
            ...     print(f"AI suggests: chaos={chaos}, complexity={complexity}")
            >>> bridge.set_ghost_hands_callback(on_ghost_hands)
        """
        self._ghost_hands_callback = callback

    def has_ghost_hands_callback(self) -> bool:
        """Check if a Ghost Hands callback is registered.

        Returns:
            True if a callback is registered, False otherwise.
        """
        return self._ghost_hands_callback is not None

    def register_rejection(self) -> None:
        """Register a user rejection of generated content.

        Tracks rejections for the "Rejection Protocol" which triggers
        innovation mode after 3 consecutive rejections.

        Note:
            Mirrors PythonBridge::registerRejection() in C++.
        """
        self._rejection_count += 1

    def reset_rejection_counter(self) -> None:
        """Reset the rejection counter.

        Called when user accepts generated content or when
        innovation mode is triggered.
        """
        self._rejection_count = 0

    @property
    def rejection_count(self) -> int:
        """Get the current rejection count."""
        return self._rejection_count

    def should_trigger_innovation(self) -> bool:
        """Check if innovation mode should be triggered.

        Returns:
            True if rejection count >= INNOVATION_THRESHOLD (default: 3), False otherwise.
        """
        return self._rejection_count >= INNOVATION_THRESHOLD


# =============================================================================
# OSC Bridge Layer (for real-time communication)
# =============================================================================


@dataclass
class OSCMessage:
    """OSC message structure for Python ↔ C++ communication.

    Represents an Open Sound Control message with address and arguments.

    Attributes:
        address: OSC address pattern (e.g., "/daiw/generate").
        args: Message arguments (floats, ints, strings, etc.).
    """

    address: str
    args: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"address": self.address, "args": self.args}


class OSCBridge:
    """OSC-based bridge for real-time Python ↔ C++ communication.

    This bridge uses Open Sound Control (OSC) protocol over UDP for
    low-latency, real-time communication between the Python brain
    and the C++ audio engine.

    OSC is preferred over direct pybind11 calls for:
    - Real-time audio thread safety (no GIL contention)
    - Process isolation (Python and C++ can run in separate processes)
    - Network-transparent communication (future distributed support)

    Message Protocol:
        Plugin → Python:
            /daiw/generate (float chaos, float vulnerability)
            /daiw/set_intent (string json)
            /daiw/ping

        Python → Plugin:
            /daiw/midi/note (int note, int velocity, int duration_ms)
            /daiw/midi/chord (int[] notes, int velocity, int duration_ms)
            /daiw/progression (string json)
            /daiw/status (string message)

    Example:
        >>> from music_brain.integrations.penta_core import OSCBridge, CppBridgeConfig
        >>> config = CppBridgeConfig(bridge_type=BridgeType.OSC)
        >>> osc = OSCBridge(config=config)
        >>> osc.start()
        >>> osc.send_midi_note(60, 100, 500)  # C4, velocity 100, 500ms
        >>> osc.stop()

    Note:
        Stub implementation. Actual OSC communication requires
        python-osc package: pip install python-osc
    """

    def __init__(self, config: Optional[CppBridgeConfig] = None):
        """Initialize OSC bridge.

        Args:
            config: Bridge configuration with OSC port settings.
        """
        self._config = config or CppBridgeConfig(bridge_type=BridgeType.OSC)
        self._running = False
        self._handlers: Dict[str, Callable[..., None]] = {}

    @property
    def config(self) -> CppBridgeConfig:
        """Get the current configuration."""
        return self._config

    def is_running(self) -> bool:
        """Check if OSC server is running."""
        return self._running

    def start(self) -> bool:
        """Start the OSC server.

        Starts listening for incoming OSC messages from C++ plugin.

        Returns:
            True if server started successfully, False otherwise.

        Note:
            Stub implementation. Actual server uses python-osc:
            osc_server.ThreadingOSCUDPServer
        """
        self._running = False  # Stub: would be True when implemented
        return self._running

    def stop(self) -> None:
        """Stop the OSC server."""
        self._running = False

    def register_handler(self, address: str, handler: Callable[..., None]) -> None:
        """Register a handler for an OSC address pattern.

        Args:
            address: OSC address pattern (e.g., "/daiw/generate").
            handler: Callback function for handling messages.

        Example:
            >>> def on_generate(chaos: float, vulnerability: float):
            ...     print(f"Generate request: chaos={chaos}, vuln={vulnerability}")
            >>> osc.register_handler("/daiw/generate", on_generate)
        """
        self._handlers[address] = handler

    def has_handler(self, address: str) -> bool:
        """Check if a handler is registered for an OSC address.

        Args:
            address: OSC address pattern to check.

        Returns:
            True if a handler is registered, False otherwise.
        """
        return address in self._handlers

    def get_registered_addresses(self) -> List[str]:
        """Get list of all registered OSC addresses.

        Returns:
            List of OSC address patterns with registered handlers.
        """
        return list(self._handlers.keys())

    def send_midi_note(self, note: int, velocity: int, duration_ms: int) -> None:
        """Send a MIDI note to the C++ plugin.

        Args:
            note: MIDI note number (0-127).
            velocity: Note velocity (0-127).
            duration_ms: Note duration in milliseconds.

        Note:
            Stub implementation. Actual send uses python-osc:
            udp_client.SimpleUDPClient.send_message()
        """
        pass  # Stub: would send OSC message

    def send_chord(self, notes: List[int], velocity: int, duration_ms: int) -> None:
        """Send a chord (multiple notes) to the C++ plugin.

        Args:
            notes: List of MIDI note numbers.
            velocity: Chord velocity.
            duration_ms: Chord duration in milliseconds.
        """
        pass  # Stub

    def send_progression(self, progression_json: str) -> None:
        """Send a complete progression as JSON to the C++ plugin.

        Args:
            progression_json: JSON string containing progression data.
        """
        pass  # Stub

    def send_status(self, status: str) -> None:
        """Send status update to the C++ plugin.

        Args:
            status: Status message string.
        """
        pass  # Stub

    def ping(self) -> bool:
        """Send ping to check C++ plugin connection.

        Returns:
            True if pong received, False otherwise.
        """
        return False  # Stub
