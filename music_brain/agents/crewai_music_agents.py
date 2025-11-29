#!/usr/bin/env python3
"""
CrewAI Music Production Agents

LOCAL SYSTEM - Uses Ollama for LLM, no cloud APIs after initial setup.

Agent Roles:
1. VoiceDirector - Vowel modification, register breaks, emotional delivery
2. Composer - Chord progressions, harmony, melody
3. MixEngineer - Levels, EQ, effects
4. DAWController - Transport, track management
5. Producer - Coordinates all agents, makes creative decisions
6. Lyricist - Lyrics, phrasing, syllable stress

One-Time Setup:
    # Install Ollama (https://ollama.ai)
    ollama pull llama3
    ollama pull codellama

Then the system runs 100% locally.
"""

import os
import json
import threading
import atexit
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Callable
from enum import Enum


# =============================================================================
# Local LLM Configuration
# =============================================================================

@dataclass
class LocalLLMConfig:
    """Configuration for local LLM (Ollama)."""
    model: str = "llama3"           # Default model
    base_url: str = "http://localhost:11434"
    temperature: float = 0.7
    context_length: int = 4096
    # Specialized models for different tasks
    code_model: str = "codellama"   # For code generation
    music_model: str = "llama3"     # For music/creative tasks


class LLMBackend(Enum):
    """Available LLM backends."""
    OLLAMA = "ollama"
    LLAMA_CPP = "llama_cpp"
    LOCAL_AI = "local_ai"


# =============================================================================
# Local LLM Client
# =============================================================================

class LocalLLM:
    """
    Local LLM client using Ollama.

    NO CLOUD APIs - All inference runs locally.

    Usage:
        llm = LocalLLM()
        response = llm.generate("Write a chord progression for grief")
    """

    def __init__(self, config: Optional[LocalLLMConfig] = None):
        self.config = config or LocalLLMConfig()
        self._available = False
        self._check_availability()

    def _check_availability(self):
        """Check if Ollama is running."""
        try:
            import requests
            response = requests.get(
                f"{self.config.base_url}/api/tags",
                timeout=2
            )
            self._available = response.status_code == 200
        except:
            self._available = False

    @property
    def is_available(self) -> bool:
        return self._available

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: int = 1024
    ) -> str:
        """
        Generate text using local LLM.

        Args:
            prompt: The user prompt
            model: Model to use (default: config.model)
            system: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        if not self._available:
            return self._fallback_response(prompt)

        try:
            import requests

            data = {
                "model": model or self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature or self.config.temperature,
                    "num_predict": max_tokens,
                }
            }

            if system:
                data["system"] = system

            response = requests.post(
                f"{self.config.base_url}/api/generate",
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return self._fallback_response(prompt)

        except Exception as e:
            print(f"LLM error: {e}")
            return self._fallback_response(prompt)

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Chat with local LLM.

        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            model: Model to use
            temperature: Sampling temperature

        Returns:
            Assistant response
        """
        if not self._available:
            user_msg = messages[-1].get("content", "") if messages else ""
            return self._fallback_response(user_msg)

        try:
            import requests

            response = requests.post(
                f"{self.config.base_url}/api/chat",
                json={
                    "model": model or self.config.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature or self.config.temperature,
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                return response.json().get("message", {}).get("content", "")
            else:
                return self._fallback_response("")

        except Exception as e:
            print(f"LLM chat error: {e}")
            return self._fallback_response("")

    def _fallback_response(self, prompt: str) -> str:
        """Fallback when LLM is not available."""
        return (
            "[Local LLM not available. Please start Ollama: `ollama serve`]\n"
            f"Prompt was: {prompt[:100]}..."
        )


# =============================================================================
# Tool Definitions
# =============================================================================

@dataclass
class Tool:
    """A tool that agents can use."""
    name: str
    description: str
    func: Callable
    enabled: bool = True

    def __call__(self, *args, **kwargs):
        if self.enabled:
            return self.func(*args, **kwargs)
        return {"error": f"Tool {self.name} is disabled"}

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False


class ToolManager:
    """Manages tools available to agents."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._bridge = None
        self._llm = None
        atexit.register(self._shutdown)

    def register(self, name: str, description: str, func: Callable) -> Tool:
        """Register a new tool."""
        tool = Tool(name=name, description=description, func=func)
        self._tools[name] = tool
        return tool

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """List all available tools."""
        return list(self._tools.keys())

    def execute(self, name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        tool = self._tools.get(name)
        if tool:
            return tool(**kwargs)
        return {"error": f"Tool not found: {name}"}

    def set_bridge(self, bridge):
        """Set the DAW bridge for tool access."""
        self._bridge = bridge
        self._register_bridge_tools()

    def set_llm(self, llm: LocalLLM):
        """Set the LLM for tool access."""
        self._llm = llm

    def _register_bridge_tools(self):
        """Register DAW bridge tools."""
        if not self._bridge:
            return

        # Transport tools
        self.register("daw_play", "Start DAW playback", self._bridge.play)
        self.register("daw_stop", "Stop DAW playback", self._bridge.stop)
        self.register("daw_record", "Start DAW recording", self._bridge.record)
        self.register(
            "daw_tempo",
            "Set DAW tempo",
            lambda bpm: self._bridge.set_tempo(bpm)
        )

        # MIDI tools
        self.register(
            "send_note",
            "Send MIDI note",
            lambda note, velocity=100, duration=500: self._bridge.send_note(
                note, velocity, duration
            )
        )
        self.register(
            "send_chord",
            "Send MIDI chord",
            lambda notes, velocity=100, duration=500: self._bridge.send_chord(
                notes, velocity, duration
            )
        )

        # Voice tools
        self.register(
            "voice_vowel",
            "Set voice vowel (A/E/I/O/U)",
            lambda v: self._bridge.set_vowel(v)
        )
        self.register(
            "voice_breathiness",
            "Set voice breathiness (0-1)",
            lambda a: self._bridge.set_breathiness(a)
        )

    def shutdown(self):
        """Shutdown tool manager."""
        self._shutdown()

    def _shutdown(self):
        """Clean shutdown."""
        for tool in self._tools.values():
            tool.disable()
        self._tools.clear()
        self._bridge = None
        self._llm = None

    def __del__(self):
        self._shutdown()


# =============================================================================
# Agent Definitions
# =============================================================================

@dataclass
class AgentRole:
    """Definition of an agent role."""
    name: str
    description: str
    system_prompt: str
    tools: List[str] = field(default_factory=list)
    model: Optional[str] = None  # Use specific model for this role


# Define the 6 agent roles
AGENT_ROLES = {
    "voice_director": AgentRole(
        name="Voice Director",
        description="Expert in vocal production, vowel modification, and emotional delivery",
        system_prompt="""You are an expert Voice Director for music production.
Your expertise includes:
- Vowel modification for register transitions (open vowels favor chest, closed favor head)
- Identifying break points in vocal melodies
- Emotional delivery coaching
- Breath placement and phrasing

When analyzing lyrics, consider:
- Which vowels might cause register breaks
- Where to modify vowels (ah->uh, aw->oh) for smoother transitions
- Where to LET breaks happen for emotional effect
- Breath marks and phrasing

Always provide specific, actionable vocal direction.""",
        tools=["voice_vowel", "voice_breathiness"]
    ),

    "composer": AgentRole(
        name="Composer",
        description="Creates chord progressions, harmonies, and melodies based on emotional intent",
        system_prompt="""You are an expert Composer for emotionally-driven music.
Your philosophy: "Interrogate Before Generate" - emotional intent drives technical choices.

Your expertise includes:
- Chord progressions that serve emotional narratives
- Modal interchange for bittersweet color (e.g., Bbm in F major)
- Tension/resolution and when to break those rules
- The "misdirection technique" - major progressions that resolve to minor tonic

Key emotional mappings:
- Grief: 60-82 BPM, minor/dorian, behind the beat
- Anxiety: 100-140 BPM, phrygian/locrian, ahead of beat
- Nostalgia: 70-90 BPM, mixolydian, behind beat
- Calm: 60-80 BPM, major/lydian, behind beat

Always justify rule-breaking with emotional reasoning.""",
        tools=["send_chord", "send_note", "daw_tempo"]
    ),

    "mix_engineer": AgentRole(
        name="Mix Engineer",
        description="Handles levels, EQ, effects, and sonic balance",
        system_prompt="""You are an expert Mix Engineer.
Your expertise includes:
- Level balancing and gain staging
- EQ decisions that serve the emotional intent
- Effects (reverb, delay, compression) as emotional tools
- Creating space and depth in the mix
- Lo-fi aesthetics: when to add warmth, saturation, imperfection

Remember: "Human imperfection is valued" - pitch drift, timing variation, room noise
can be features, not bugs. The lo-fi bedroom emo aesthetic embraces vulnerability.""",
        tools=[]  # Mix tools would be added when available
    ),

    "daw_controller": AgentRole(
        name="DAW Controller",
        description="Manages transport, tracks, clips, and DAW operations",
        system_prompt="""You are a DAW Controller agent.
Your job is to translate high-level musical intentions into DAW operations.

You can:
- Control transport (play, stop, record)
- Set tempo and time signature
- Manage tracks (create, arm, mute, solo)
- Trigger clips and scenes
- Set positions and loop points

Always confirm operations completed successfully.""",
        tools=["daw_play", "daw_stop", "daw_record", "daw_tempo"]
    ),

    "producer": AgentRole(
        name="Producer",
        description="Coordinates all agents, makes creative decisions, maintains vision",
        system_prompt="""You are the Producer - the creative leader of this music production.
Your job is to:
- Maintain the emotional vision of the song
- Coordinate between Voice Director, Composer, Mix Engineer, and DAW Controller
- Make final creative decisions
- Ensure the "Interrogate Before Generate" philosophy is followed
- Know when to break rules and WHY

Remember the core philosophy:
"The tool shouldn't finish art for people. It should make them braver."
"The audience doesn't hear 'borrowed from Dorian.' They hear 'that part made me cry.'"

Always ask "why" before "how". Emotional intent drives everything.""",
        tools=[]  # Producer coordinates, doesn't directly use tools
    ),

    "lyricist": AgentRole(
        name="Lyricist",
        description="Writes lyrics, analyzes phrasing, identifies syllable stress",
        system_prompt="""You are an expert Lyricist.
Your expertise includes:
- Writing emotionally resonant lyrics
- Analyzing syllable stress patterns
- Identifying problem vowels for singing
- Matching lyrics to melodic contour
- Creating lyrical "fracture points" - where the voice should break

When writing or analyzing lyrics, mark:
- Stressed syllables (CAPS)
- Vowel sounds (phonetic guide)
- Potential break points (*)
- Breath marks (//)

Remember: the best lyrics leave space for the music to speak.""",
        tools=[]
    ),
}


# =============================================================================
# Agent Class
# =============================================================================

class MusicAgent:
    """
    A music production agent powered by local LLM.

    LOCAL SYSTEM - Uses Ollama, no cloud APIs.
    """

    def __init__(
        self,
        role: AgentRole,
        llm: LocalLLM,
        tool_manager: ToolManager
    ):
        self.role = role
        self.llm = llm
        self.tools = tool_manager
        self._conversation: List[Dict[str, str]] = []
        self._enabled = True

    @property
    def name(self) -> str:
        return self.role.name

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def think(self, task: str) -> str:
        """
        Have the agent think about a task.

        Args:
            task: The task or question

        Returns:
            Agent's response
        """
        if not self._enabled:
            return f"[{self.name} is disabled]"

        # Build conversation
        messages = [
            {"role": "system", "content": self.role.system_prompt},
        ]
        messages.extend(self._conversation)
        messages.append({"role": "user", "content": task})

        # Get response from local LLM
        response = self.llm.chat(
            messages,
            model=self.role.model
        )

        # Store in conversation history
        self._conversation.append({"role": "user", "content": task})
        self._conversation.append({"role": "assistant", "content": response})

        return response

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool if the agent has access."""
        if tool_name not in self.role.tools:
            return {"error": f"{self.name} doesn't have access to tool: {tool_name}"}
        return self.tools.execute(tool_name, **kwargs)

    def clear_history(self):
        """Clear conversation history."""
        self._conversation.clear()

    def __str__(self) -> str:
        return f"Agent({self.name})"


# =============================================================================
# Agent Crew
# =============================================================================

class MusicCrew:
    """
    A crew of music production agents.

    LOCAL SYSTEM - All agents use local Ollama LLM.

    Usage:
        crew = MusicCrew()
        crew.setup()

        # Ask specific agent
        response = crew.ask("composer", "Write a progression for grief")

        # Or coordinate task
        result = crew.produce("Create a lo-fi ballad about loss")
    """

    def __init__(self, llm_config: Optional[LocalLLMConfig] = None):
        self.llm_config = llm_config or LocalLLMConfig()
        self.llm = LocalLLM(self.llm_config)
        self.tools = ToolManager()
        self._agents: Dict[str, MusicAgent] = {}
        self._running = False

        atexit.register(self._shutdown)

    def setup(self, bridge=None) -> bool:
        """
        Set up the crew with agents.

        Args:
            bridge: Optional AbletonBridge for DAW control

        Returns:
            True if setup successful
        """
        # Check LLM availability
        if not self.llm.is_available:
            print("WARNING: Local LLM (Ollama) not available.")
            print("To enable AI agents, run: ollama serve")
            print("And pull a model: ollama pull llama3")

        # Set up tools
        if bridge:
            self.tools.set_bridge(bridge)
        self.tools.set_llm(self.llm)

        # Create agents
        for role_id, role in AGENT_ROLES.items():
            self._agents[role_id] = MusicAgent(role, self.llm, self.tools)

        self._running = True
        return True

    def get_agent(self, role_id: str) -> Optional[MusicAgent]:
        """Get an agent by role ID."""
        return self._agents.get(role_id)

    def ask(self, role_id: str, task: str) -> str:
        """
        Ask a specific agent about a task.

        Args:
            role_id: Agent role (voice_director, composer, etc.)
            task: The task or question

        Returns:
            Agent's response
        """
        agent = self._agents.get(role_id)
        if agent:
            return agent.think(task)
        return f"Unknown agent: {role_id}"

    def produce(self, brief: str) -> Dict[str, str]:
        """
        Have the Producer coordinate a production task.

        Args:
            brief: The creative brief

        Returns:
            Dict with responses from each relevant agent
        """
        results = {}

        # Producer analyzes the brief
        producer = self._agents.get("producer")
        if producer:
            results["producer"] = producer.think(
                f"Analyze this creative brief and create a production plan:\n{brief}"
            )

        # Lyricist if lyrics mentioned
        if any(word in brief.lower() for word in ["lyrics", "words", "sing", "vocal"]):
            lyricist = self._agents.get("lyricist")
            if lyricist:
                results["lyricist"] = lyricist.think(
                    f"Based on this brief, provide lyrical guidance:\n{brief}"
                )

        # Composer for harmony
        composer = self._agents.get("composer")
        if composer:
            results["composer"] = composer.think(
                f"Based on this brief, suggest harmony and progression:\n{brief}"
            )

        # Voice Director for vocal approach
        if any(word in brief.lower() for word in ["voice", "vocal", "sing", "delivery"]):
            voice_director = self._agents.get("voice_director")
            if voice_director:
                results["voice_director"] = voice_director.think(
                    f"Based on this brief, provide vocal direction:\n{brief}"
                )

        return results

    @property
    def agents(self) -> Dict[str, MusicAgent]:
        return self._agents.copy()

    @property
    def is_running(self) -> bool:
        return self._running

    def shutdown(self):
        """Shutdown the crew."""
        self._shutdown()

    def _shutdown(self):
        """Clean shutdown."""
        self._running = False
        for agent in self._agents.values():
            agent.disable()
            agent.clear_history()
        self._agents.clear()
        self.tools.shutdown()

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    def __del__(self):
        self._shutdown()


# =============================================================================
# Pre-defined Tasks
# =============================================================================

def voice_production_task(crew: MusicCrew, lyrics: str) -> Dict[str, Any]:
    """
    Complete voice production analysis for lyrics.

    Returns vowel guide, break points, and delivery notes.
    """
    results = {}

    # Lyricist analyzes syllables
    lyricist = crew.get_agent("lyricist")
    if lyricist:
        results["syllable_analysis"] = lyricist.think(
            f"Analyze these lyrics for syllable stress and vowel sounds:\n{lyrics}"
        )

    # Voice Director provides guidance
    voice_director = crew.get_agent("voice_director")
    if voice_director:
        results["vocal_guidance"] = voice_director.think(
            f"Provide detailed vowel modification and break point guidance for:\n{lyrics}"
        )

    return results


def song_production_task(
    crew: MusicCrew,
    emotion: str,
    genre: str = "lo-fi bedroom emo"
) -> Dict[str, Any]:
    """
    Complete song production guidance.

    Returns progression, tempo, arrangement ideas.
    """
    brief = f"Create a {genre} song expressing {emotion}"
    return crew.produce(brief)


# =============================================================================
# Convenience Functions
# =============================================================================

_default_crew: Optional[MusicCrew] = None


def get_crew() -> MusicCrew:
    """Get or create the default crew."""
    global _default_crew
    if _default_crew is None:
        _default_crew = MusicCrew()
        _default_crew.setup()
    return _default_crew


def shutdown_crew():
    """Shutdown the default crew."""
    global _default_crew
    if _default_crew:
        _default_crew.shutdown()
        _default_crew = None


if __name__ == "__main__":
    print("Testing Music Agents (LOCAL - using Ollama)")
    print("=" * 50)

    # Check Ollama
    llm = LocalLLM()
    if llm.is_available:
        print("Ollama is running")
    else:
        print("Ollama not available. Start with: ollama serve")
        print("Then pull a model: ollama pull llama3")
        exit(1)

    # Create crew
    with MusicCrew() as crew:
        print("\nAvailable agents:")
        for name, agent in crew.agents.items():
            print(f"  - {agent.name}: {agent.role.description}")

        # Test composer
        print("\n" + "=" * 50)
        print("Testing Composer agent:")
        response = crew.ask(
            "composer",
            "Write a chord progression for a song about grief and loss. "
            "Use modal interchange to create bittersweet moments."
        )
        print(response)
