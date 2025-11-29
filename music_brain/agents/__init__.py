"""
DAiW Music Brain - Agent System

LOCAL SYSTEM - No cloud APIs required after initial Ollama setup.

Components:
- AbletonBridge: OSC/MIDI communication with Ableton Live
- MusicCrew: AI agents for music production (local Ollama LLM)
- UnifiedHub: Central orchestration

One-Time Setup:
    # Install Ollama (https://ollama.ai)
    curl -fsSL https://ollama.ai/install.sh | sh

    # Pull a model (one-time download)
    ollama pull llama3

    # Start the server (runs locally)
    ollama serve

Then the system runs 100% locally with no internet required.

Usage:
    # Quick start
    from music_brain.agents import start_hub, stop_hub

    hub = start_hub()
    hub.connect_daw()
    hub.speak("Hello world")
    hub.play()
    response = hub.ask_agent("composer", "Write a sad progression")
    stop_hub()

    # Or with context manager
    from music_brain.agents import UnifiedHub

    with UnifiedHub() as hub:
        hub.connect_daw()
        hub.send_chord([60, 64, 67], velocity=100, duration_ms=1000)

Shutdown Methods:
    All classes support multiple shutdown patterns:

    1. Context manager (recommended):
       with UnifiedHub() as hub:
           hub.play()
       # Automatically stopped

    2. Explicit shutdown:
       hub = UnifiedHub()
       hub.start()
       # ... use hub ...
       hub.stop()

    3. Force stop (immediate):
       force_stop_hub()

    4. Global shutdown:
       shutdown_all()

    5. Automatic cleanup:
       - All classes register with atexit
       - MIDI sends CC 123 (all notes off) before closing
       - OSC server threads are joined with timeout
"""

# =============================================================================
# Ableton Bridge - DAW Communication
# =============================================================================

from .ableton_bridge import (
    # Main classes
    AbletonBridge,
    AbletonOSCBridge,
    AbletonMIDIBridge,

    # Configuration
    OSCConfig,
    MIDIConfig,

    # State classes
    TransportState,
    TrackInfo,

    # Voice control
    VoiceCC,
    VOWEL_FORMANTS,

    # Convenience functions
    get_bridge,
    connect_daw,
    disconnect_daw,

    # MCP tools
    get_mcp_tools as get_bridge_mcp_tools,
)

# =============================================================================
# CrewAI Music Agents - Local LLM Agents
# =============================================================================

from .crewai_music_agents import (
    # LLM
    LocalLLM,
    LocalLLMConfig,
    LLMBackend,

    # Tools
    Tool,
    ToolManager,

    # Agents
    AgentRole,
    MusicAgent,
    AGENT_ROLES,

    # Crew
    MusicCrew,

    # Pre-defined tasks
    voice_production_task,
    song_production_task,

    # Convenience functions
    get_crew,
    shutdown_crew,
)

# =============================================================================
# Voice Profiles - Customizable Voice Characteristics
# =============================================================================

from .voice_profiles import (
    # Main classes
    VoiceProfileManager,
    VoiceProfile,

    # Enums
    Gender,
    AccentRegion,
    SpeechPattern,

    # Convenience functions
    get_voice_manager,
    apply_voice_profile,
    learn_word,
    list_accents,
    list_speech_patterns,
)

# =============================================================================
# Unified Hub - Central Orchestration
# =============================================================================

from .unified_hub import (
    # Main class
    UnifiedHub,

    # Configuration
    HubConfig,
    SessionConfig,

    # State classes
    VoiceState,
    DAWState,

    # Voice synthesis
    LocalVoiceSynth,

    # Global functions
    get_hub,
    start_hub,
    stop_hub,
    force_stop_hub,
    shutdown_all,

    # MCP tools
    get_hub_mcp_tools,
)

# =============================================================================
# Convenience Aliases
# =============================================================================

# Shutdown aliases
shutdown_tools = shutdown_crew
get_tool_manager = lambda: get_crew().tools if get_crew() else None

# =============================================================================
# Module Info
# =============================================================================

__all__ = [
    # Ableton Bridge
    "AbletonBridge",
    "AbletonOSCBridge",
    "AbletonMIDIBridge",
    "OSCConfig",
    "MIDIConfig",
    "TransportState",
    "TrackInfo",
    "VoiceCC",
    "VOWEL_FORMANTS",
    "get_bridge",
    "connect_daw",
    "disconnect_daw",
    "get_bridge_mcp_tools",

    # Local LLM
    "LocalLLM",
    "LocalLLMConfig",
    "LLMBackend",

    # Tools
    "Tool",
    "ToolManager",

    # Agents
    "AgentRole",
    "MusicAgent",
    "AGENT_ROLES",
    "MusicCrew",
    "voice_production_task",
    "song_production_task",
    "get_crew",
    "shutdown_crew",

    # Voice Profiles
    "VoiceProfileManager",
    "VoiceProfile",
    "Gender",
    "AccentRegion",
    "SpeechPattern",
    "get_voice_manager",
    "apply_voice_profile",
    "learn_word",
    "list_accents",
    "list_speech_patterns",

    # Unified Hub
    "UnifiedHub",
    "HubConfig",
    "SessionConfig",
    "VoiceState",
    "DAWState",
    "LocalVoiceSynth",
    "get_hub",
    "start_hub",
    "stop_hub",
    "force_stop_hub",
    "shutdown_all",
    "get_hub_mcp_tools",

    # Aliases
    "shutdown_tools",
    "get_tool_manager",
]

__version__ = "1.0.0"
__author__ = "DAiW"


# =============================================================================
# Quick Test
# =============================================================================

def _test():
    """Quick test of the agent system."""
    print("DAiW Agent System - Quick Test")
    print("=" * 50)
    print("LOCAL SYSTEM - No cloud APIs")
    print()

    # Check LLM
    llm = LocalLLM()
    print(f"Ollama available: {llm.is_available}")

    if not llm.is_available:
        print()
        print("To enable AI agents, run:")
        print("  ollama serve")
        print("  ollama pull llama3")

    print()
    print("Available components:")
    print("  - AbletonBridge (OSC/MIDI)")
    print("  - MusicCrew (6 AI agents)")
    print("  - UnifiedHub (orchestration)")
    print()
    print("Usage:")
    print("  from music_brain.agents import start_hub, stop_hub")
    print("  hub = start_hub()")
    print("  hub.connect_daw()")
    print("  stop_hub()")


if __name__ == "__main__":
    _test()
