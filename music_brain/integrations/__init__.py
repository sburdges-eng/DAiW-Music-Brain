"""
Integrations module for DAiW-Music-Brain.

This module provides integration interfaces with external systems while
maintaining the core philosophy of "Interrogate Before Generate" -
emotional intent should drive technical decisions.

Phase 3 Integration:
    The penta-core integration provides the bridge between the Python "brain"
    and the C++ "body" for real-time audio processing. It supports:

    - PentaCoreIntegration: High-level API for penta-core communication
    - CppBridge: Direct pybind11 bridge for Python/C++ interop
    - OSCBridge: Real-time OSC communication for audio-thread safety

Example:
    >>> from music_brain.integrations import PentaCoreIntegration
    >>> integration = PentaCoreIntegration()
    >>> integration.is_connected()
    False

    >>> from music_brain.integrations import CppBridge, CppBridgeConfig
    >>> bridge = CppBridge()
"""

from music_brain.integrations.penta_core import (
    # High-level integration
    PentaCoreIntegration,
    PentaCoreConfig,
    # C++ bridge layer
    CppBridge,
    CppBridgeConfig,
    BridgeType,
    ThreadingMode,
    # OSC bridge layer
    OSCBridge,
    OSCMessage,
    # Data structures
    MidiEvent,
    MidiBuffer,
    KnobState,
    # Type aliases
    GhostHandsCallback,
)

__all__ = [
    # High-level integration
    "PentaCoreIntegration",
    "PentaCoreConfig",
    # C++ bridge layer
    "CppBridge",
    "CppBridgeConfig",
    "BridgeType",
    "ThreadingMode",
    # OSC bridge layer
    "OSCBridge",
    "OSCMessage",
    # Data structures
    "MidiEvent",
    "MidiBuffer",
    "KnobState",
    # Type aliases
    "GhostHandsCallback",
]
