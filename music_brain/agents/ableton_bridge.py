#!/usr/bin/env python3
"""
Ableton Bridge - OSC/MIDI Communication with DAW

LOCAL SYSTEM - No cloud APIs required.
Communicates with Ableton Live via OSC and MIDI.

Features:
- OSC bridge for transport control, track management
- MIDI bridge for note/CC data
- Voice synthesis CC mappings (vowel, formant, breathiness, vibrato)
- Automatic cleanup and shutdown

Usage:
    from music_brain.agents import AbletonBridge

    with AbletonBridge() as bridge:
        bridge.connect()
        bridge.play()
        bridge.send_note(60, 100, 500)
"""

import threading
import queue
import time
import json
import atexit
from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, List, Any, Tuple
from enum import Enum


# =============================================================================
# Voice Control CC Mappings (for formant synthesis)
# =============================================================================

class VoiceCC(Enum):
    """MIDI CC mappings for voice synthesis control."""
    VOWEL = 20        # 0-127 maps to A-E-I-O-U
    FORMANT_SHIFT = 21  # Formant frequency shift
    BREATHINESS = 22    # Breath noise amount
    VIBRATO_RATE = 23   # Vibrato speed
    VIBRATO_DEPTH = 24  # Vibrato amount
    PITCH_BEND = 25     # Fine pitch control
    JITTER = 26         # Pitch randomness
    SHIMMER = 27        # Amplitude randomness
    NASALITY = 28       # Nasal resonance


# Vowel positions (F1, F2 frequencies in Hz)
VOWEL_FORMANTS = {
    'A': (800, 1200),   # open front
    'E': (400, 2200),   # mid front
    'I': (300, 2800),   # close front
    'O': (500, 900),    # mid back
    'U': (350, 700),    # close back
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class OSCConfig:
    """OSC connection configuration."""
    host: str = "127.0.0.1"
    send_port: int = 9000      # Send to Ableton
    receive_port: int = 9001   # Receive from Ableton
    timeout: float = 2.0


@dataclass
class MIDIConfig:
    """MIDI connection configuration."""
    output_port: str = "DAiW Voice"
    input_port: str = "DAiW Input"
    virtual: bool = True       # Create virtual ports


@dataclass
class TransportState:
    """Current DAW transport state."""
    playing: bool = False
    recording: bool = False
    tempo: float = 120.0
    time_signature: Tuple[int, int] = (4, 4)
    position_bars: float = 0.0
    position_beats: float = 0.0


@dataclass
class TrackInfo:
    """Information about a DAW track."""
    index: int
    name: str
    armed: bool = False
    muted: bool = False
    soloed: bool = False
    volume: float = 0.0  # dB
    pan: float = 0.0     # -1 to 1


# =============================================================================
# OSC Bridge
# =============================================================================

class AbletonOSCBridge:
    """
    OSC communication bridge to Ableton Live.

    Requires AbletonOSC or similar OSC server running in Ableton.
    All communication is LOCAL - no cloud APIs.
    """

    def __init__(self, config: Optional[OSCConfig] = None):
        self.config = config or OSCConfig()
        self._server = None
        self._client = None
        self._server_thread = None
        self._running = False
        self._callbacks: Dict[str, List[Callable]] = {}
        self._message_queue = queue.Queue()
        self._transport = TransportState()
        self._tracks: Dict[int, TrackInfo] = {}

        # Register cleanup
        atexit.register(self._shutdown)

    def connect(self) -> bool:
        """Connect to Ableton via OSC."""
        try:
            from pythonosc import udp_client, dispatcher, osc_server

            # Create client (send to Ableton)
            self._client = udp_client.SimpleUDPClient(
                self.config.host,
                self.config.send_port
            )

            # Create server (receive from Ableton)
            self._dispatcher = dispatcher.Dispatcher()
            self._setup_handlers()

            self._server = osc_server.ThreadingOSCUDPServer(
                (self.config.host, self.config.receive_port),
                self._dispatcher
            )

            # Start server thread
            self._server_thread = threading.Thread(
                target=self._server.serve_forever,
                daemon=True
            )
            self._server_thread.start()
            self._running = True

            # Send ping
            self.ping()
            return True

        except ImportError:
            print("ERROR: python-osc not installed. Run: pip install python-osc")
            return False
        except Exception as e:
            print(f"OSC connection failed: {e}")
            return False

    def _setup_handlers(self):
        """Register OSC message handlers."""
        handlers = {
            "/live/transport/playing": self._on_playing,
            "/live/transport/recording": self._on_recording,
            "/live/transport/tempo": self._on_tempo,
            "/live/transport/position": self._on_position,
            "/live/track/info": self._on_track_info,
            "/daiw/pong": self._on_pong,
            "/daiw/status": self._on_status,
        }

        for address, handler in handlers.items():
            self._dispatcher.map(address, handler)

        # Default handler for logging
        self._dispatcher.set_default_handler(self._on_unknown)

    def _on_playing(self, address, *args):
        self._transport.playing = bool(args[0]) if args else False
        self._trigger_callback("transport", self._transport)

    def _on_recording(self, address, *args):
        self._transport.recording = bool(args[0]) if args else False
        self._trigger_callback("transport", self._transport)

    def _on_tempo(self, address, *args):
        self._transport.tempo = float(args[0]) if args else 120.0
        self._trigger_callback("tempo", self._transport.tempo)

    def _on_position(self, address, *args):
        if len(args) >= 2:
            self._transport.position_bars = float(args[0])
            self._transport.position_beats = float(args[1])

    def _on_track_info(self, address, *args):
        if len(args) >= 2:
            index = int(args[0])
            name = str(args[1])
            self._tracks[index] = TrackInfo(index=index, name=name)
            self._trigger_callback("track", self._tracks[index])

    def _on_pong(self, address, *args):
        self._trigger_callback("pong", time.time())

    def _on_status(self, address, *args):
        status = args[0] if args else ""
        self._trigger_callback("status", status)

    def _on_unknown(self, address, *args):
        self._message_queue.put((address, args))

    def _trigger_callback(self, event: str, data: Any):
        """Trigger registered callbacks for an event."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Callback error for {event}: {e}")

    def on(self, event: str, callback: Callable):
        """Register a callback for an event."""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)

    def off(self, event: str, callback: Optional[Callable] = None):
        """Remove callback(s) for an event."""
        if callback:
            self._callbacks.get(event, []).remove(callback)
        else:
            self._callbacks.pop(event, None)

    # Transport Controls
    def play(self):
        """Start playback."""
        self._send("/live/transport/play")

    def stop(self):
        """Stop playback."""
        self._send("/live/transport/stop")

    def record(self):
        """Start recording."""
        self._send("/live/transport/record")

    def set_tempo(self, bpm: float):
        """Set tempo."""
        self._send("/live/transport/tempo", bpm)

    def set_position(self, bars: float, beats: float = 0.0):
        """Set playhead position."""
        self._send("/live/transport/position", bars, beats)

    # Track Controls
    def create_track(self, track_type: str = "midi") -> int:
        """Create a new track. Returns track index."""
        self._send("/live/track/create", track_type)
        return len(self._tracks)

    def arm_track(self, index: int, armed: bool = True):
        """Arm/disarm a track for recording."""
        self._send("/live/track/arm", index, int(armed))

    def mute_track(self, index: int, muted: bool = True):
        """Mute/unmute a track."""
        self._send("/live/track/mute", index, int(muted))

    def solo_track(self, index: int, soloed: bool = True):
        """Solo/unsolo a track."""
        self._send("/live/track/solo", index, int(soloed))

    def set_track_volume(self, index: int, volume_db: float):
        """Set track volume in dB."""
        self._send("/live/track/volume", index, volume_db)

    def set_track_pan(self, index: int, pan: float):
        """Set track pan (-1 to 1)."""
        self._send("/live/track/pan", index, pan)

    # Clip Controls
    def fire_clip(self, track: int, clip: int):
        """Fire a clip."""
        self._send("/live/clip/fire", track, clip)

    def stop_clip(self, track: int, clip: int):
        """Stop a clip."""
        self._send("/live/clip/stop", track, clip)

    # DAiW Specific
    def ping(self):
        """Send ping to check connection."""
        self._send("/daiw/ping")

    def send_progression(self, progression_json: str):
        """Send a chord progression to Ableton."""
        self._send("/daiw/progression", progression_json)

    def send_intent(self, intent_json: str):
        """Send song intent to Ableton."""
        self._send("/daiw/intent", intent_json)

    def _send(self, address: str, *args):
        """Send OSC message."""
        if self._client:
            self._client.send_message(address, list(args) if args else [])

    @property
    def is_connected(self) -> bool:
        return self._running and self._client is not None

    @property
    def transport(self) -> TransportState:
        return self._transport

    @property
    def tracks(self) -> Dict[int, TrackInfo]:
        return self._tracks.copy()

    def disconnect(self):
        """Disconnect from Ableton."""
        self._shutdown()

    def _shutdown(self):
        """Clean shutdown."""
        self._running = False

        if self._server:
            try:
                self._server.shutdown()
            except:
                pass
            self._server = None

        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=2.0)

        self._client = None
        self._callbacks.clear()

        # Clear queue
        while not self._message_queue.empty():
            try:
                self._message_queue.get_nowait()
            except:
                pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def __del__(self):
        self._shutdown()


# =============================================================================
# MIDI Bridge
# =============================================================================

class AbletonMIDIBridge:
    """
    MIDI communication bridge to Ableton Live.

    Creates virtual MIDI ports for note/CC data.
    All communication is LOCAL - no cloud APIs.
    """

    def __init__(self, config: Optional[MIDIConfig] = None):
        self.config = config or MIDIConfig()
        self._output = None
        self._input = None
        self._running = False
        self._input_thread = None
        self._callbacks: Dict[str, List[Callable]] = {}
        self._active_notes: Dict[Tuple[int, int], int] = {}  # (channel, note) -> velocity

        atexit.register(self._shutdown)

    def connect(self) -> bool:
        """Connect MIDI ports."""
        try:
            import mido

            # Create output port
            if self.config.virtual:
                self._output = mido.open_output(
                    self.config.output_port,
                    virtual=True
                )
            else:
                # Find existing port
                ports = mido.get_output_names()
                matching = [p for p in ports if self.config.output_port in p]
                if matching:
                    self._output = mido.open_output(matching[0])
                else:
                    print(f"MIDI output port not found: {self.config.output_port}")
                    return False

            self._running = True
            return True

        except ImportError:
            print("ERROR: mido not installed. Run: pip install mido python-rtmidi")
            return False
        except Exception as e:
            print(f"MIDI connection failed: {e}")
            return False

    def send_note_on(self, note: int, velocity: int = 100, channel: int = 0):
        """Send note on message."""
        if self._output:
            import mido
            msg = mido.Message('note_on', note=note, velocity=velocity, channel=channel)
            self._output.send(msg)
            self._active_notes[(channel, note)] = velocity

    def send_note_off(self, note: int, channel: int = 0):
        """Send note off message."""
        if self._output:
            import mido
            msg = mido.Message('note_off', note=note, velocity=0, channel=channel)
            self._output.send(msg)
            self._active_notes.pop((channel, note), None)

    def send_note(self, note: int, velocity: int, duration_ms: int, channel: int = 0):
        """Send a note with duration (non-blocking)."""
        self.send_note_on(note, velocity, channel)

        def note_off_later():
            time.sleep(duration_ms / 1000.0)
            self.send_note_off(note, channel)

        threading.Thread(target=note_off_later, daemon=True).start()

    def send_chord(self, notes: List[int], velocity: int = 100,
                   duration_ms: int = 500, channel: int = 0):
        """Send multiple notes as a chord."""
        for note in notes:
            self.send_note_on(note, velocity, channel)

        def notes_off_later():
            time.sleep(duration_ms / 1000.0)
            for note in notes:
                self.send_note_off(note, channel)

        threading.Thread(target=notes_off_later, daemon=True).start()

    def send_cc(self, cc: int, value: int, channel: int = 0):
        """Send control change message."""
        if self._output:
            import mido
            msg = mido.Message('control_change', control=cc, value=value, channel=channel)
            self._output.send(msg)

    def send_pitch_bend(self, value: int, channel: int = 0):
        """Send pitch bend (-8192 to 8191)."""
        if self._output:
            import mido
            msg = mido.Message('pitchwheel', pitch=value, channel=channel)
            self._output.send(msg)

    # Voice Control Methods
    def set_vowel(self, vowel: str, channel: int = 0):
        """Set vowel for voice synthesis (A, E, I, O, U)."""
        vowel_map = {'A': 0, 'E': 32, 'I': 64, 'O': 96, 'U': 127}
        value = vowel_map.get(vowel.upper(), 64)
        self.send_cc(VoiceCC.VOWEL.value, value, channel)

    def set_formant_shift(self, shift: float, channel: int = 0):
        """Set formant shift (-1 to 1)."""
        value = int((shift + 1) * 63.5)  # Map to 0-127
        self.send_cc(VoiceCC.FORMANT_SHIFT.value, value, channel)

    def set_breathiness(self, amount: float, channel: int = 0):
        """Set breathiness (0 to 1)."""
        value = int(amount * 127)
        self.send_cc(VoiceCC.BREATHINESS.value, value, channel)

    def set_vibrato(self, rate: float, depth: float, channel: int = 0):
        """Set vibrato parameters (0 to 1 each)."""
        self.send_cc(VoiceCC.VIBRATO_RATE.value, int(rate * 127), channel)
        self.send_cc(VoiceCC.VIBRATO_DEPTH.value, int(depth * 127), channel)

    def all_notes_off(self, channel: Optional[int] = None):
        """Send all notes off message."""
        if self._output:
            import mido
            channels = [channel] if channel is not None else range(16)
            for ch in channels:
                # CC 123 = All Notes Off
                msg = mido.Message('control_change', control=123, value=0, channel=ch)
                self._output.send(msg)
        self._active_notes.clear()

    @property
    def is_connected(self) -> bool:
        return self._running and self._output is not None

    @property
    def active_notes(self) -> Dict[Tuple[int, int], int]:
        return self._active_notes.copy()

    def disconnect(self):
        """Disconnect MIDI."""
        self._shutdown()

    def _shutdown(self):
        """Clean shutdown."""
        self._running = False

        # Send all notes off before closing
        if self._output:
            try:
                self.all_notes_off()
                time.sleep(0.05)  # Brief delay for messages to send
                self._output.close()
            except:
                pass
            self._output = None

        if self._input:
            try:
                self._input.close()
            except:
                pass
            self._input = None

        self._callbacks.clear()
        self._active_notes.clear()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def __del__(self):
        self._shutdown()


# =============================================================================
# Combined Bridge
# =============================================================================

class AbletonBridge:
    """
    Combined OSC + MIDI bridge to Ableton Live.

    LOCAL SYSTEM - All communication happens on localhost.
    No cloud APIs, no internet required.

    Usage:
        with AbletonBridge() as bridge:
            bridge.connect()
            bridge.play()
            bridge.send_note(60, 100, 500)
    """

    def __init__(
        self,
        osc_config: Optional[OSCConfig] = None,
        midi_config: Optional[MIDIConfig] = None
    ):
        self.osc = AbletonOSCBridge(osc_config)
        self.midi = AbletonMIDIBridge(midi_config)
        self._connected = False

        atexit.register(self._shutdown)

    def connect(self) -> bool:
        """Connect both OSC and MIDI."""
        osc_ok = self.osc.connect()
        midi_ok = self.midi.connect()
        self._connected = osc_ok or midi_ok
        return self._connected

    # Delegate transport to OSC
    def play(self):
        self.osc.play()

    def stop(self):
        self.osc.stop()

    def record(self):
        self.osc.record()

    def set_tempo(self, bpm: float):
        self.osc.set_tempo(bpm)

    # Delegate notes to MIDI
    def send_note(self, note: int, velocity: int, duration_ms: int, channel: int = 0):
        self.midi.send_note(note, velocity, duration_ms, channel)

    def send_chord(self, notes: List[int], velocity: int = 100,
                   duration_ms: int = 500, channel: int = 0):
        self.midi.send_chord(notes, velocity, duration_ms, channel)

    def send_cc(self, cc: int, value: int, channel: int = 0):
        self.midi.send_cc(cc, value, channel)

    # Voice control
    def set_vowel(self, vowel: str, channel: int = 0):
        self.midi.set_vowel(vowel, channel)

    def set_breathiness(self, amount: float, channel: int = 0):
        self.midi.set_breathiness(amount, channel)

    def set_vibrato(self, rate: float, depth: float, channel: int = 0):
        self.midi.set_vibrato(rate, depth, channel)

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def transport(self) -> TransportState:
        return self.osc.transport

    def disconnect(self):
        self._shutdown()

    def _shutdown(self):
        self._connected = False
        self.midi.disconnect()
        self.osc.disconnect()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def __del__(self):
        self._shutdown()


# =============================================================================
# MCP Tool Definitions (for AI access)
# =============================================================================

def get_mcp_tools() -> List[Dict[str, Any]]:
    """Return MCP tool definitions for the Ableton bridge."""
    return [
        {
            "name": "ableton_play",
            "description": "Start Ableton Live playback",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "ableton_stop",
            "description": "Stop Ableton Live playback",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "ableton_record",
            "description": "Start Ableton Live recording",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "ableton_tempo",
            "description": "Set Ableton Live tempo",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bpm": {"type": "number", "description": "Tempo in BPM"}
                },
                "required": ["bpm"]
            }
        },
        {
            "name": "ableton_send_note",
            "description": "Send a MIDI note to Ableton",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "note": {"type": "integer", "description": "MIDI note number (0-127)"},
                    "velocity": {"type": "integer", "description": "Velocity (0-127)"},
                    "duration_ms": {"type": "integer", "description": "Duration in milliseconds"}
                },
                "required": ["note", "velocity", "duration_ms"]
            }
        },
        {
            "name": "ableton_send_chord",
            "description": "Send a chord (multiple notes) to Ableton",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "notes": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of MIDI note numbers"
                    },
                    "velocity": {"type": "integer", "description": "Velocity (0-127)"},
                    "duration_ms": {"type": "integer", "description": "Duration in milliseconds"}
                },
                "required": ["notes"]
            }
        },
        {
            "name": "voice_set_vowel",
            "description": "Set vowel for voice synthesis",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "vowel": {
                        "type": "string",
                        "enum": ["A", "E", "I", "O", "U"],
                        "description": "Vowel sound"
                    }
                },
                "required": ["vowel"]
            }
        },
        {
            "name": "voice_set_breathiness",
            "description": "Set breathiness for voice synthesis",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "Breathiness amount (0-1)"
                    }
                },
                "required": ["amount"]
            }
        },
    ]


# =============================================================================
# Convenience Functions
# =============================================================================

_default_bridge: Optional[AbletonBridge] = None


def get_bridge() -> AbletonBridge:
    """Get or create the default bridge."""
    global _default_bridge
    if _default_bridge is None:
        _default_bridge = AbletonBridge()
    return _default_bridge


def connect_daw() -> bool:
    """Connect to Ableton Live."""
    return get_bridge().connect()


def disconnect_daw():
    """Disconnect from Ableton Live."""
    global _default_bridge
    if _default_bridge:
        _default_bridge.disconnect()
        _default_bridge = None


if __name__ == "__main__":
    # Test the bridge
    print("Testing Ableton Bridge (LOCAL - no cloud APIs)")
    print("=" * 50)

    with AbletonBridge() as bridge:
        if bridge.is_connected:
            print("Connected to Ableton")

            # Test MIDI
            print("Sending C major chord...")
            bridge.send_chord([60, 64, 67], velocity=100, duration_ms=1000)
            time.sleep(1.5)

            print("Done!")
        else:
            print("Could not connect to Ableton")
            print("Make sure:")
            print("  1. python-osc is installed: pip install python-osc")
            print("  2. mido is installed: pip install mido python-rtmidi")
            print("  3. Ableton Live is running with OSC enabled")
