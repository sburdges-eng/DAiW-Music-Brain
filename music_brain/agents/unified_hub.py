#!/usr/bin/env python3
"""
Unified Hub - Central Orchestration for DAiW Music Brain

LOCAL SYSTEM - No cloud APIs required after initial Ollama setup.

The UnifiedHub coordinates:
- Voice synthesis (formant, MIDI CC control)
- DAW control (Ableton via OSC/MIDI)
- AI agents (local Ollama LLM)
- Session management (save/load)

One-Time Setup:
    1. Install Ollama: https://ollama.ai
    2. Pull models: ollama pull llama3
    3. Start server: ollama serve

Then everything runs locally.

Usage:
    from music_brain.agents import UnifiedHub

    with UnifiedHub() as hub:
        hub.connect_daw()
        hub.speak("Hello world", vowel="O")
        hub.play()
        response = hub.ask_agent("composer", "Write a sad progression")
"""

import os
import json
import time
import threading
import queue
import atexit
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable, Tuple
from enum import Enum

from .ableton_bridge import (
    AbletonBridge,
    AbletonOSCBridge,
    AbletonMIDIBridge,
    OSCConfig,
    MIDIConfig,
    TransportState,
    VoiceCC,
    VOWEL_FORMANTS,
)
from .crewai_music_agents import (
    MusicCrew,
    MusicAgent,
    LocalLLM,
    LocalLLMConfig,
    ToolManager,
    AGENT_ROLES,
)
from .voice_profiles import (
    VoiceProfileManager,
    VoiceProfile,
    Gender,
    AccentRegion,
    SpeechPattern,
    get_voice_manager,
)


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class HubConfig:
    """Configuration for the UnifiedHub."""
    # Paths
    session_dir: str = "~/.daiw/sessions"
    config_dir: str = "~/.daiw/config"

    # DAW
    osc_host: str = "127.0.0.1"
    osc_send_port: int = 9000
    osc_receive_port: int = 9001
    midi_port: str = "DAiW Voice"

    # LLM
    llm_model: str = "llama3"
    llm_url: str = "http://localhost:11434"

    # Voice
    default_voice_channel: int = 0
    default_voice_profile: str = "default"

    def __post_init__(self):
        self.session_dir = os.path.expanduser(self.session_dir)
        self.config_dir = os.path.expanduser(self.config_dir)


@dataclass
class SessionConfig:
    """Session-specific configuration."""
    name: str = "untitled"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tempo: float = 120.0
    key: str = "C"
    mode: str = "major"
    emotion: str = "neutral"
    voice_profile: str = "default"
    notes: List[str] = field(default_factory=list)


@dataclass
class VoiceState:
    """Current state of voice synthesis."""
    vowel: str = "A"
    formant_shift: float = 0.0
    breathiness: float = 0.0
    vibrato_rate: float = 0.0
    vibrato_depth: float = 0.0
    pitch: int = 60  # MIDI note
    velocity: int = 100
    active: bool = False


@dataclass
class DAWState:
    """Current state of DAW connection."""
    connected: bool = False
    playing: bool = False
    recording: bool = False
    tempo: float = 120.0
    position: float = 0.0


# =============================================================================
# Voice Synthesizer (Local)
# =============================================================================

class LocalVoiceSynth:
    """
    Local voice synthesis using system TTS and MIDI CC for formant control.

    NO CLOUD APIs - Uses macOS 'say' or espeak on Linux.

    Supports:
    - Voice profiles with pitch, accent, speech patterns
    - Learning custom pronunciations
    - Speech impediment simulation
    """

    def __init__(self, midi_bridge: Optional[AbletonMIDIBridge] = None):
        self.midi = midi_bridge
        self._speaking = False
        self._current_note = None
        self._platform = self._detect_platform()
        self._profile_manager = get_voice_manager()
        self._active_profile: Optional[str] = None

        # Initialize preset profiles
        self._profile_manager.create_preset_profiles()

    def _detect_platform(self) -> str:
        import platform
        system = platform.system()
        if system == "Darwin":
            return "macos"
        elif system == "Linux":
            return "linux"
        elif system == "Windows":
            return "windows"
        return "unknown"

    def speak(
        self,
        text: str,
        vowel: Optional[str] = None,
        rate: Optional[int] = None,
        pitch: Optional[int] = None,
        profile: Optional[str] = None
    ) -> bool:
        """
        Speak text using local TTS with voice profile support.

        Args:
            text: Text to speak
            vowel: Optional vowel hint for formant control
            rate: Speech rate (words per minute) - auto from profile if None
            pitch: Base pitch (0-100) - auto from profile if None
            profile: Voice profile name to use

        Returns:
            True if speaking started
        """
        # Apply voice profile if specified or active
        use_profile = profile or self._active_profile
        voice_params = {}

        if use_profile:
            text, voice_params = self._profile_manager.apply_profile(text, use_profile)

        # Get rate and pitch from profile or defaults
        if rate is None:
            rate = int(175 * voice_params.get("rate", 1.0))
        if pitch is None:
            # Map Hz to 0-100 scale (roughly 80-400 Hz)
            base_hz = voice_params.get("pitch", 170)
            pitch = int((base_hz - 80) / 320 * 100)
            pitch = max(0, min(100, pitch))

        if vowel and self.midi:
            self.set_vowel(vowel)

        # Apply voice quality to MIDI if available
        if self.midi and voice_params:
            if "breathiness" in voice_params:
                self.set_breathiness(voice_params["breathiness"])
            if "formant_shift" in voice_params:
                self.set_formant_shift(voice_params["formant_shift"])

        self._speaking = True

        try:
            if self._platform == "macos":
                import subprocess
                # macOS say supports voice selection
                cmd = ["say", "-r", str(rate)]
                subprocess.Popen(
                    cmd + [text],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True
            elif self._platform == "linux":
                import subprocess
                subprocess.Popen(
                    ["espeak", "-s", str(rate), "-p", str(pitch), text],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True
            else:
                print(f"TTS not implemented for {self._platform}")
                return False
        except Exception as e:
            print(f"TTS error: {e}")
            return False
        finally:
            self._speaking = False

    def set_profile(self, profile_name: str):
        """Set the active voice profile."""
        self._active_profile = profile_name

    def get_profile(self) -> Optional[str]:
        """Get the active voice profile name."""
        return self._active_profile

    def create_profile(
        self,
        name: str,
        gender: str = "neutral",
        base_pitch: Optional[float] = None,
        accent: str = "american_general",
        speech_patterns: Optional[List[str]] = None,
        **kwargs
    ) -> VoiceProfile:
        """
        Create a new voice profile.

        Args:
            name: Profile name
            gender: male/female/neutral/child
            base_pitch: Base pitch in Hz
            accent: Accent region (see list_accents())
            speech_patterns: List of speech patterns (see list_speech_patterns())

        Returns:
            Created VoiceProfile
        """
        gender_enum = Gender(gender) if isinstance(gender, str) else gender
        accent_enum = AccentRegion(accent) if isinstance(accent, str) else accent
        patterns = [
            SpeechPattern(p) if isinstance(p, str) else p
            for p in (speech_patterns or [])
        ]

        return self._profile_manager.create_profile(
            name=name,
            gender=gender_enum,
            base_pitch=base_pitch,
            accent=accent_enum,
            speech_patterns=patterns,
            **kwargs
        )

    def learn_pronunciation(self, word: str, pronunciation: str):
        """Learn a custom pronunciation for the active profile."""
        if self._active_profile:
            self._profile_manager.learn_pronunciation(
                self._active_profile, word, pronunciation
            )

    def learn_phrase(self, phrase: str, replacement: str):
        """Learn a phrase replacement for the active profile."""
        if self._active_profile:
            self._profile_manager.learn_phrase(
                self._active_profile, phrase, replacement
            )

    def list_profiles(self) -> List[str]:
        """List available voice profiles."""
        return self._profile_manager.list_profiles()

    def list_accents(self) -> List[str]:
        """List available accents."""
        return [a.value for a in AccentRegion]

    def list_speech_patterns(self) -> List[str]:
        """List available speech patterns."""
        return [p.value for p in SpeechPattern]

    def set_formant_shift(self, shift: float, channel: int = 0):
        """Set formant shift (-1 to 1)."""
        if self.midi:
            value = int((shift + 1) * 63.5)
            self.midi.send_cc(VoiceCC.FORMANT_SHIFT.value, value, channel)

    def note_on(self, pitch: int, velocity: int = 100, channel: int = 0):
        """Start a note (for vocoder/synth voice)."""
        if self.midi:
            self.midi.send_note_on(pitch, velocity, channel)
            self._current_note = (pitch, channel)

    def note_off(self, pitch: Optional[int] = None, channel: int = 0):
        """Stop a note."""
        if self.midi:
            if pitch is None and self._current_note:
                pitch, channel = self._current_note
            if pitch is not None:
                self.midi.send_note_off(pitch, channel)
            self._current_note = None

    def set_vowel(self, vowel: str, channel: int = 0):
        """Set vowel for formant synthesis."""
        if self.midi:
            self.midi.set_vowel(vowel, channel)

    def set_formants(self, f1: int, f2: int, channel: int = 0):
        """Set formant frequencies directly (via CC)."""
        if self.midi:
            # Map F1 (200-1000 Hz) to CC value
            f1_cc = int((f1 - 200) / 800 * 127)
            # Map F2 (500-3000 Hz) to CC value
            f2_cc = int((f2 - 500) / 2500 * 127)
            self.midi.send_cc(VoiceCC.FORMANT_SHIFT.value, f1_cc, channel)
            # Could add F2 CC if available

    def set_breathiness(self, amount: float, channel: int = 0):
        """Set breathiness (0-1)."""
        if self.midi:
            self.midi.set_breathiness(amount, channel)

    def set_vibrato(self, rate: float, depth: float, channel: int = 0):
        """Set vibrato (0-1 each)."""
        if self.midi:
            self.midi.set_vibrato(rate, depth, channel)

    @property
    def is_speaking(self) -> bool:
        return self._speaking


# =============================================================================
# Unified Hub
# =============================================================================

class UnifiedHub:
    """
    Central orchestration hub for DAiW Music Brain.

    LOCAL SYSTEM - All processing runs locally:
    - LLM: Ollama (local)
    - Voice: System TTS + MIDI CC
    - DAW: OSC/MIDI to Ableton

    Usage:
        with UnifiedHub() as hub:
            # Connect to DAW
            hub.connect_daw()

            # Control voice
            hub.speak("Hello")
            hub.note_on(60)
            hub.set_vowel("O")

            # Control DAW
            hub.play()
            hub.set_tempo(90)

            # Ask AI agents
            response = hub.ask_agent("composer", "Write a grief progression")

            # Save session
            hub.save_session("my_session")
    """

    def __init__(self, config: Optional[HubConfig] = None):
        self.config = config or HubConfig()

        # Components
        self._bridge: Optional[AbletonBridge] = None
        self._voice: Optional[LocalVoiceSynth] = None
        self._crew: Optional[MusicCrew] = None
        self._llm: Optional[LocalLLM] = None

        # State
        self._session = SessionConfig()
        self._voice_state = VoiceState()
        self._daw_state = DAWState()
        self._running = False

        # Callbacks
        self._callbacks: Dict[str, List[Callable]] = {}

        # Ensure directories exist
        os.makedirs(self.config.session_dir, exist_ok=True)
        os.makedirs(self.config.config_dir, exist_ok=True)

        # Register cleanup
        atexit.register(self._shutdown)

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def start(self) -> "UnifiedHub":
        """Start the hub and all components."""
        self._running = True

        # Initialize LLM
        self._llm = LocalLLM(LocalLLMConfig(
            model=self.config.llm_model,
            base_url=self.config.llm_url
        ))

        # Initialize bridge
        self._bridge = AbletonBridge(
            osc_config=OSCConfig(
                host=self.config.osc_host,
                send_port=self.config.osc_send_port,
                receive_port=self.config.osc_receive_port
            ),
            midi_config=MIDIConfig(
                output_port=self.config.midi_port,
                virtual=True
            )
        )

        # Initialize voice
        self._voice = LocalVoiceSynth(self._bridge.midi)

        # Initialize crew
        self._crew = MusicCrew(LocalLLMConfig(
            model=self.config.llm_model,
            base_url=self.config.llm_url
        ))
        self._crew.setup(self._bridge)

        return self

    def stop(self):
        """Stop the hub gracefully."""
        self._running = False

        # Stop any active notes
        if self._voice_state.active:
            self.note_off()

        # Shutdown components in order
        if self._crew:
            self._crew.shutdown()
            self._crew = None

        if self._bridge:
            self._bridge.disconnect()
            self._bridge = None

        self._voice = None
        self._callbacks.clear()

    def force_stop(self):
        """Force immediate stop."""
        self._running = False

        # Kill all notes
        if self._bridge and self._bridge.midi:
            self._bridge.midi.all_notes_off()

        self.stop()

    def _shutdown(self):
        """Atexit shutdown handler."""
        if self._running:
            self.force_stop()

    @property
    def is_running(self) -> bool:
        return self._running

    # =========================================================================
    # DAW Control
    # =========================================================================

    def connect_daw(self) -> bool:
        """Connect to Ableton Live."""
        if self._bridge:
            success = self._bridge.connect()
            self._daw_state.connected = success
            self._trigger_callback("daw_connected", success)
            return success
        return False

    def disconnect_daw(self):
        """Disconnect from DAW."""
        if self._bridge:
            self._bridge.disconnect()
            self._daw_state.connected = False

    def play(self):
        """Start DAW playback."""
        if self._bridge:
            self._bridge.play()
            self._daw_state.playing = True

    def stop_playback(self):
        """Stop DAW playback."""
        if self._bridge:
            self._bridge.stop()
            self._daw_state.playing = False

    def record(self):
        """Start DAW recording."""
        if self._bridge:
            self._bridge.record()
            self._daw_state.recording = True

    def set_tempo(self, bpm: float):
        """Set DAW tempo."""
        if self._bridge:
            self._bridge.set_tempo(bpm)
            self._daw_state.tempo = bpm
            self._session.tempo = bpm

    def send_note(self, note: int, velocity: int = 100, duration_ms: int = 500):
        """Send a MIDI note to DAW."""
        if self._bridge:
            self._bridge.send_note(note, velocity, duration_ms)

    def send_chord(self, notes: List[int], velocity: int = 100, duration_ms: int = 500):
        """Send a chord to DAW."""
        if self._bridge:
            self._bridge.send_chord(notes, velocity, duration_ms)

    # =========================================================================
    # Voice Control
    # =========================================================================

    def speak(self, text: str, vowel: Optional[str] = None, rate: int = 175):
        """Speak text using local TTS."""
        if self._voice:
            self._voice.speak(text, vowel, rate)

    def note_on(self, pitch: int, velocity: int = 100, channel: Optional[int] = None):
        """Start a voice note."""
        ch = channel if channel is not None else self.config.default_voice_channel
        if self._voice:
            self._voice.note_on(pitch, velocity, ch)
            self._voice_state.pitch = pitch
            self._voice_state.velocity = velocity
            self._voice_state.active = True

    def note_off(self, pitch: Optional[int] = None, channel: Optional[int] = None):
        """Stop a voice note."""
        ch = channel if channel is not None else self.config.default_voice_channel
        if self._voice:
            self._voice.note_off(pitch, ch)
            self._voice_state.active = False

    def set_vowel(self, vowel: str, channel: Optional[int] = None):
        """Set voice vowel (A, E, I, O, U)."""
        ch = channel if channel is not None else self.config.default_voice_channel
        if self._voice:
            self._voice.set_vowel(vowel, ch)
            self._voice_state.vowel = vowel.upper()

    def set_breathiness(self, amount: float, channel: Optional[int] = None):
        """Set voice breathiness (0-1)."""
        ch = channel if channel is not None else self.config.default_voice_channel
        if self._voice:
            self._voice.set_breathiness(amount, ch)
            self._voice_state.breathiness = amount

    def set_vibrato(self, rate: float, depth: float, channel: Optional[int] = None):
        """Set voice vibrato."""
        ch = channel if channel is not None else self.config.default_voice_channel
        if self._voice:
            self._voice.set_vibrato(rate, depth, ch)
            self._voice_state.vibrato_rate = rate
            self._voice_state.vibrato_depth = depth

    def sing_vowel_sequence(
        self,
        vowels: List[str],
        pitch: int = 60,
        duration_ms: int = 300,
        channel: Optional[int] = None
    ):
        """Sing a sequence of vowels on a single pitch."""
        ch = channel if channel is not None else self.config.default_voice_channel

        def sequence():
            self.note_on(pitch, 100, ch)
            for vowel in vowels:
                self.set_vowel(vowel, ch)
                time.sleep(duration_ms / 1000)
            self.note_off(pitch, ch)

        threading.Thread(target=sequence, daemon=True).start()

    # =========================================================================
    # AI Agents
    # =========================================================================

    def ask_agent(self, role_id: str, task: str) -> str:
        """
        Ask a specific AI agent about a task.

        Args:
            role_id: One of: voice_director, composer, mix_engineer,
                     daw_controller, producer, lyricist
            task: The question or task

        Returns:
            Agent's response
        """
        if self._crew:
            return self._crew.ask(role_id, task)
        return "AI agents not initialized"

    def produce(self, brief: str) -> Dict[str, str]:
        """
        Have the Producer coordinate a production task.

        Args:
            brief: Creative brief

        Returns:
            Dict with responses from relevant agents
        """
        if self._crew:
            return self._crew.produce(brief)
        return {"error": "AI agents not initialized"}

    def analyze_lyrics(self, lyrics: str) -> Dict[str, str]:
        """
        Analyze lyrics for vocal production.

        Returns vowel guide, break points, delivery notes.
        """
        results = {}

        if self._crew:
            # Lyricist analysis
            results["syllables"] = self._crew.ask(
                "lyricist",
                f"Analyze syllable stress and vowel sounds:\n{lyrics}"
            )

            # Voice Director guidance
            results["vocal_guidance"] = self._crew.ask(
                "voice_director",
                f"Provide vowel modification and break point guidance:\n{lyrics}"
            )

        return results

    def suggest_progression(self, emotion: str, key: str = "C") -> str:
        """
        Suggest a chord progression for an emotion.

        Args:
            emotion: Target emotion (grief, anxiety, joy, etc.)
            key: Musical key

        Returns:
            Suggested progression with explanation
        """
        if self._crew:
            return self._crew.ask(
                "composer",
                f"Suggest a chord progression in {key} for the emotion: {emotion}\n"
                f"Include modal interchange if appropriate and explain the emotional effect."
            )
        return "AI agents not initialized"

    @property
    def llm_available(self) -> bool:
        """Check if local LLM is available."""
        return self._llm is not None and self._llm.is_available

    # =========================================================================
    # Session Management
    # =========================================================================

    def new_session(self, name: str = "untitled"):
        """Create a new session."""
        self._session = SessionConfig(name=name)
        self._voice_state = VoiceState()
        self._trigger_callback("session_new", name)

    def save_session(self, name: Optional[str] = None) -> str:
        """
        Save current session to file.

        Returns:
            Path to saved session file
        """
        if name:
            self._session.name = name

        self._session.updated_at = datetime.now().isoformat()

        # Build session data
        data = {
            "session": asdict(self._session),
            "voice_state": asdict(self._voice_state),
            "daw_state": asdict(self._daw_state),
        }

        # Save to file
        filename = f"{self._session.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.config.session_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        self._trigger_callback("session_saved", filepath)
        return filepath

    def load_session(self, filepath: str) -> bool:
        """
        Load a session from file.

        Returns:
            True if loaded successfully
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Restore session
            self._session = SessionConfig(**data.get("session", {}))

            # Restore voice state
            vs_data = data.get("voice_state", {})
            self._voice_state = VoiceState(**vs_data)

            # Apply voice state
            if self._voice:
                self.set_vowel(self._voice_state.vowel)
                self.set_breathiness(self._voice_state.breathiness)
                self.set_vibrato(
                    self._voice_state.vibrato_rate,
                    self._voice_state.vibrato_depth
                )

            # Apply DAW state
            if self._bridge and self._daw_state.connected:
                self.set_tempo(self._session.tempo)

            self._trigger_callback("session_loaded", filepath)
            return True

        except Exception as e:
            print(f"Error loading session: {e}")
            return False

    def list_sessions(self) -> List[str]:
        """List available session files."""
        session_dir = Path(self.config.session_dir)
        return [f.name for f in session_dir.glob("*.json")]

    # =========================================================================
    # Callbacks
    # =========================================================================

    def on(self, event: str, callback: Callable):
        """Register a callback for an event."""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)

    def off(self, event: str, callback: Optional[Callable] = None):
        """Remove callback(s)."""
        if callback:
            self._callbacks.get(event, []).remove(callback)
        else:
            self._callbacks.pop(event, None)

    def _trigger_callback(self, event: str, data: Any = None):
        """Trigger callbacks for an event."""
        for cb in self._callbacks.get(event, []):
            try:
                cb(data)
            except Exception as e:
                print(f"Callback error for {event}: {e}")

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def session(self) -> SessionConfig:
        return self._session

    @property
    def voice_state(self) -> VoiceState:
        return self._voice_state

    @property
    def daw_state(self) -> DAWState:
        return self._daw_state

    @property
    def daw_connected(self) -> bool:
        return self._daw_state.connected

    # =========================================================================
    # Context Manager
    # =========================================================================

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __del__(self):
        self._shutdown()


# =============================================================================
# Global Instance Management
# =============================================================================

_default_hub: Optional[UnifiedHub] = None


def get_hub() -> UnifiedHub:
    """Get or create the default hub."""
    global _default_hub
    if _default_hub is None:
        _default_hub = UnifiedHub()
        _default_hub.start()
    return _default_hub


def start_hub() -> UnifiedHub:
    """Start and return the default hub."""
    return get_hub()


def stop_hub():
    """Stop the default hub gracefully."""
    global _default_hub
    if _default_hub:
        _default_hub.stop()
        _default_hub = None


def force_stop_hub():
    """Force stop the default hub immediately."""
    global _default_hub
    if _default_hub:
        _default_hub.force_stop()
        _default_hub = None


def shutdown_all():
    """Complete system shutdown."""
    force_stop_hub()


# =============================================================================
# MCP Tools (for AI access)
# =============================================================================

def get_hub_mcp_tools() -> List[Dict[str, Any]]:
    """Return MCP tool definitions for the hub."""
    return [
        {
            "name": "hub_connect_daw",
            "description": "Connect to Ableton Live",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "hub_play",
            "description": "Start DAW playback",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "hub_stop",
            "description": "Stop DAW playback",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "hub_speak",
            "description": "Speak text using local TTS",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to speak"},
                    "vowel": {"type": "string", "description": "Vowel hint (A/E/I/O/U)"}
                },
                "required": ["text"]
            }
        },
        {
            "name": "hub_ask_agent",
            "description": "Ask an AI agent about a music production task",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "enum": ["voice_director", "composer", "mix_engineer",
                                 "daw_controller", "producer", "lyricist"],
                        "description": "Agent role to ask"
                    },
                    "task": {"type": "string", "description": "Task or question"}
                },
                "required": ["role", "task"]
            }
        },
        {
            "name": "hub_analyze_lyrics",
            "description": "Analyze lyrics for vocal production",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "lyrics": {"type": "string", "description": "Lyrics to analyze"}
                },
                "required": ["lyrics"]
            }
        },
        {
            "name": "hub_suggest_progression",
            "description": "Suggest chord progression for an emotion",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "emotion": {"type": "string", "description": "Target emotion"},
                    "key": {"type": "string", "description": "Musical key (default: C)"}
                },
                "required": ["emotion"]
            }
        },
    ]


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("Testing UnifiedHub (LOCAL - no cloud APIs)")
    print("=" * 60)

    with UnifiedHub() as hub:
        print(f"\nHub started: {hub.is_running}")
        print(f"LLM available: {hub.llm_available}")

        if not hub.llm_available:
            print("\nTo enable AI agents:")
            print("  1. Install Ollama: https://ollama.ai")
            print("  2. Pull model: ollama pull llama3")
            print("  3. Start server: ollama serve")

        # Test DAW connection
        print("\nConnecting to DAW...")
        if hub.connect_daw():
            print("DAW connected!")

            # Test voice
            print("\nTesting voice...")
            hub.set_vowel("A")
            hub.speak("Hello, this is the DAiW Music Brain")

            time.sleep(2)

            # Test note
            print("Testing note...")
            hub.note_on(60, 100)
            time.sleep(0.5)
            hub.note_off(60)
        else:
            print("DAW not connected (Ableton may not be running)")

        # Test AI if available
        if hub.llm_available:
            print("\nTesting AI agent...")
            response = hub.ask_agent(
                "composer",
                "Suggest a 4-chord progression for grief"
            )
            print(f"Composer says:\n{response}")

        # Save session
        print("\nSaving session...")
        path = hub.save_session("test_session")
        print(f"Saved to: {path}")

    print("\nHub stopped cleanly.")
