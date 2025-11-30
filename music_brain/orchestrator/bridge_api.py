"""
iDAW Bridge API - Python side of the Dual Engine

This module provides the Python API that the C++ PythonBridge calls into.
It processes text prompts with knob parameters and returns MIDI data.

Data Flow:
    C++ Side B UI -> call_iMIDI() -> Python Bridge API -> music_brain orchestrator
    -> MIDI events + Ghost Hands suggestions -> Ring Buffer -> C++ Audio Engine

Usage from C++:
    MidiBuffer result = PythonBridge::getInstance().call_iMIDI(knobs, "make it jazzy");
    
Usage from Python (testing):
    from music_brain.orchestrator.bridge_api import process_prompt
    result = await process_prompt("make it jazzy", knobs={"chaos": 0.5})
"""

import json
import asyncio
import math
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from music_brain.orchestrator import AIOrchestrator, Pipeline, OrchestratorConfig
from music_brain.orchestrator.processors import IntentProcessor, HarmonyProcessor, GrooveProcessor
from music_brain.orchestrator.interfaces import ProcessorResult, ExecutionContext


# =============================================================================
# SAFETY & ROBUSTNESS FUNCTIONS
# =============================================================================

def resolve_contradictions(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve contradictory parameter values to ensure safe operation.
    
    Handles cases like:
    - Infinite gain with positive modulation
    - Velocity min > velocity max
    - Other logical contradictions
    
    Args:
        params: Parameter dictionary to validate and fix
        
    Returns:
        Cleaned parameter dictionary with contradictions resolved
    """
    resolved = params.copy()
    
    # Handle gain contradictions
    if 'gain' in resolved and 'gain_mod' in resolved:
        if resolved['gain'] == -math.inf and resolved['gain_mod'] > 0:
            resolved['gain'] = -6.0  # Default to safe volume if contradiction
    
    # Handle velocity range contradictions
    if 'velocity_min' in resolved and 'velocity_max' in resolved:
        if resolved['velocity_min'] > resolved['velocity_max']:
            avg = (resolved['velocity_min'] + resolved['velocity_max']) / 2
            resolved['velocity_min'] = avg
            resolved['velocity_max'] = avg
    
    # Handle chaos/complexity range clipping
    for key in ['chaos', 'complexity', 'swing', 'gate']:
        if key in resolved:
            resolved[key] = max(0.0, min(1.0, resolved[key]))
    
    # Handle tempo contradictions (too slow or too fast)
    if 'tempo' in resolved:
        resolved['tempo'] = max(20, min(300, resolved['tempo']))
    
    # Handle grid resolution contradictions
    if 'grid' in resolved:
        resolved['grid'] = max(1, min(64, resolved['grid']))
    
    # Handle attack/release time contradictions (attack > release)
    if 'attack' in resolved and 'release' in resolved:
        if resolved['attack'] > resolved['release']:
            # Swap them if attack is longer than release
            resolved['attack'], resolved['release'] = resolved['release'], resolved['attack']
    
    return resolved


# Synesthesia word-to-parameter dictionary
_synesthesia_dictionary: Dict[str, Dict[str, float]] = {
    # Emotions
    "happy": {"chaos": 0.3, "complexity": 0.4},
    "sad": {"chaos": 0.2, "complexity": 0.6},
    "angry": {"chaos": 0.8, "complexity": 0.7},
    "calm": {"chaos": 0.1, "complexity": 0.3},
    "excited": {"chaos": 0.6, "complexity": 0.5},
    "melancholic": {"chaos": 0.25, "complexity": 0.65},
    "peaceful": {"chaos": 0.05, "complexity": 0.2},
    "intense": {"chaos": 0.7, "complexity": 0.8},
    
    # Musical descriptors
    "funky": {"chaos": 0.5, "complexity": 0.6},
    "smooth": {"chaos": 0.15, "complexity": 0.4},
    "groovy": {"chaos": 0.4, "complexity": 0.5},
    "ambient": {"chaos": 0.2, "complexity": 0.3},
    "punchy": {"chaos": 0.3, "complexity": 0.4},
    "ethereal": {"chaos": 0.35, "complexity": 0.7},
    "driving": {"chaos": 0.45, "complexity": 0.55},
    "dreamy": {"chaos": 0.3, "complexity": 0.5},
    
    # Textures
    "warm": {"chaos": 0.2, "complexity": 0.4},
    "bright": {"chaos": 0.4, "complexity": 0.5},
    "dark": {"chaos": 0.3, "complexity": 0.6},
    "crisp": {"chaos": 0.25, "complexity": 0.35},
    "muddy": {"chaos": 0.5, "complexity": 0.3},
    "airy": {"chaos": 0.2, "complexity": 0.45},
    
    # Dynamics
    "loud": {"chaos": 0.6, "complexity": 0.5},
    "soft": {"chaos": 0.15, "complexity": 0.35},
    "dynamic": {"chaos": 0.55, "complexity": 0.6},
    "static": {"chaos": 0.1, "complexity": 0.2},
}


def get_parameter(word: str, dictionary: Optional[Dict[str, Dict[str, float]]] = None) -> Dict[str, float]:
    """
    Get parameters for a word from dictionary, with Synesthesia fallback.
    
    If word is not in dictionary, generates deterministic random values
    based on word hash - turning unknown words into musical parameters.
    
    Args:
        word: The word to look up
        dictionary: Optional custom dictionary. Uses default if None.
        
    Returns:
        Dict with 'chaos' and 'complexity' values (0.0-1.0)
    """
    if dictionary is None:
        dictionary = _synesthesia_dictionary
    
    word_lower = word.lower().strip()
    
    if word_lower in dictionary:
        return dictionary[word_lower]
    else:
        # The "Synesthesia" Fallback
        # Turn unknown words into deterministic random values
        word_hash = hashlib.sha256(word_lower.encode('utf-8')).hexdigest()
        seed = int(word_hash, 16) % 100
        
        # Generate chaos from first part of hash
        chaos = seed / 100.0
        
        # Generate complexity from different part of hash for variety
        complexity_seed = int(word_hash[16:32], 16) % 100
        complexity = complexity_seed / 100.0
        
        return {"chaos": chaos, "complexity": complexity}


@dataclass
class MidiEvent:
    """MIDI event matching C++ MidiEvent struct."""
    status: int      # MIDI status byte
    data1: int       # First data byte (note/CC number)
    data2: int       # Second data byte (velocity/value)
    timestamp: int   # Sample offset within buffer
    
    def to_dict(self) -> Dict[str, int]:
        return {
            "status": self.status,
            "data1": self.data1,
            "data2": self.data2,
            "timestamp": self.timestamp,
        }


@dataclass
class KnobState:
    """Current state of Side B UI knobs."""
    grid: float = 16.0       # Grid resolution (4-32)
    gate: float = 0.75       # Note gate (0.1-1.0)
    swing: float = 0.5       # Swing amount (0.5-0.75)
    chaos: float = 0.5       # Chaos/randomization (0-1)
    complexity: float = 0.5  # Harmonic/rhythmic complexity (0-1)
    
    @classmethod
    def from_dict(cls, d: Dict[str, float]) -> "KnobState":
        return cls(
            grid=d.get("grid", 16.0),
            gate=d.get("gate", 0.75),
            swing=d.get("swing", 0.5),
            chaos=d.get("chaos", 0.5),
            complexity=d.get("complexity", 0.5),
        )


@dataclass
class BridgeResult:
    """Result from the Python bridge processing."""
    success: bool
    midi_events: List[MidiEvent] = field(default_factory=list)
    suggested_chaos: float = 0.5
    suggested_complexity: float = 0.5
    detected_genre: str = ""
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "midi_events": [e.to_dict() for e in self.midi_events],
            "suggested_chaos": self.suggested_chaos,
            "suggested_complexity": self.suggested_complexity,
            "detected_genre": self.detected_genre,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


# Global genre definitions cache
_genre_definitions: Dict[str, Any] = {}


def load_genre_definitions(path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load genre definitions from JSON file.
    
    Args:
        path: Path to GenreDefinitions.json. If None, uses default location.
        
    Returns:
        Dict of genre definitions
    """
    global _genre_definitions
    
    if _genre_definitions:
        return _genre_definitions
    
    if path is None:
        # Try default locations
        possible_paths = [
            Path(__file__).parent.parent.parent.parent / "iDAW_Core" / "data" / "GenreDefinitions.json",
            Path("iDAW_Core/data/GenreDefinitions.json"),
            Path("data/GenreDefinitions.json"),
        ]
        for p in possible_paths:
            if p.exists():
                path = str(p)
                break
    
    if path and Path(path).exists():
        with open(path, 'r') as f:
            data = json.load(f)
            _genre_definitions = data.get("genres", {})
    
    return _genre_definitions


def detect_genre_from_text(text: str, genres: Dict[str, Any]) -> Tuple[str, float]:
    """
    Detect genre from text prompt using emotional tags.
    
    Args:
        text: User text prompt
        genres: Available genre definitions
        
    Returns:
        Tuple of (genre_name, confidence)
    """
    text_lower = text.lower()
    
    best_genre = ""
    best_score = 0.0
    
    for genre_name, genre_data in genres.items():
        score = 0.0
        emotional_tags = genre_data.get("emotional_tags", [])
        
        # Check for genre name mention
        if genre_name.replace("_", " ") in text_lower:
            score += 2.0
        
        # Check for emotional tags
        for tag in emotional_tags:
            if tag.lower() in text_lower:
                score += 1.0
        
        # Check for mode mentions
        modes = genre_data.get("harmony", {}).get("preferred_modes", [])
        for mode in modes:
            if mode.lower() in text_lower:
                score += 0.5
        
        if score > best_score:
            best_score = score
            best_genre = genre_name
    
    # Normalize confidence
    confidence = min(best_score / 5.0, 1.0)
    
    return best_genre, confidence


def compute_ghost_hands_suggestions(
    text: str,
    genre_data: Dict[str, Any],
    current_knobs: KnobState,
) -> Tuple[float, float]:
    """
    Compute AI suggestions for chaos and complexity knobs ("Ghost Hands").
    
    The knobs should visually update to reflect the AI's interpretation
    of the user's text input. Uses Synesthesia fallback for unknown words.
    
    Args:
        text: User text prompt
        genre_data: Detected genre definition
        current_knobs: Current knob values
        
    Returns:
        Tuple of (suggested_chaos, suggested_complexity)
    """
    text_lower = text.lower()
    words = text_lower.split()
    
    # Start with genre defaults
    base_chaos = genre_data.get("velocity", {}).get("humanization", 0.15)
    base_complexity = 0.5
    
    # Adjust based on text keywords
    chaos_modifiers = {
        "random": 0.3,
        "chaotic": 0.4,
        "wild": 0.35,
        "crazy": 0.3,
        "unpredictable": 0.25,
        "stable": -0.2,
        "consistent": -0.25,
        "steady": -0.2,
        "clean": -0.15,
        "tight": -0.2,
    }
    
    complexity_modifiers = {
        "simple": -0.3,
        "basic": -0.25,
        "minimal": -0.3,
        "sparse": -0.2,
        "complex": 0.3,
        "intricate": 0.35,
        "sophisticated": 0.25,
        "jazzy": 0.3,
        "advanced": 0.2,
        "dense": 0.25,
        "layered": 0.2,
    }
    
    suggested_chaos = base_chaos
    suggested_complexity = base_complexity
    matched_words = 0
    
    for word, modifier in chaos_modifiers.items():
        if word in text_lower:
            suggested_chaos += modifier
            matched_words += 1
    
    for word, modifier in complexity_modifiers.items():
        if word in text_lower:
            suggested_complexity += modifier
            matched_words += 1
    
    # Use Synesthesia fallback for unmatched descriptive words
    # (words not in our known modifiers dictionary)
    descriptive_words = [w for w in words if len(w) > 3 and w.isalpha()]
    known_words = set(chaos_modifiers.keys()) | set(complexity_modifiers.keys())
    unknown_words = [w for w in descriptive_words if w not in known_words]
    
    if unknown_words and matched_words == 0:
        # No known words matched - use Synesthesia for the first unknown word
        synesthesia_params = get_parameter(unknown_words[0])
        suggested_chaos = synesthesia_params["chaos"]
        suggested_complexity = synesthesia_params["complexity"]
    elif unknown_words:
        # Blend unknown words with existing suggestions
        for word in unknown_words[:2]:  # Max 2 unknown words
            params = get_parameter(word)
            suggested_chaos = (suggested_chaos + params["chaos"]) / 2
            suggested_complexity = (suggested_complexity + params["complexity"]) / 2
    
    # Clamp to valid range
    suggested_chaos = max(0.0, min(1.0, suggested_chaos))
    suggested_complexity = max(0.0, min(1.0, suggested_complexity))
    
    return suggested_chaos, suggested_complexity


def generate_midi_from_harmony(
    chords: List[str],
    key: str,
    tempo: int,
    knobs: KnobState,
    genre_data: Dict[str, Any],
) -> List[MidiEvent]:
    """
    Generate MIDI events from harmony data.
    
    Args:
        chords: List of chord names
        key: Key signature
        tempo: Tempo in BPM
        knobs: Current knob values
        genre_data: Genre definition
        
    Returns:
        List of MIDI events
    """
    events = []
    
    # Note mappings for common chord roots
    root_to_midi = {
        "C": 60, "C#": 61, "Db": 61, "D": 62, "D#": 63, "Eb": 63,
        "E": 64, "F": 65, "F#": 66, "Gb": 66, "G": 67, "G#": 68,
        "Ab": 68, "A": 69, "A#": 70, "Bb": 70, "B": 71,
    }
    
    # Samples per beat at 44100 Hz
    samples_per_beat = int(44100 * 60 / tempo)
    
    # Velocity from genre
    base_velocity = genre_data.get("velocity", {}).get("base", 80)
    humanization = knobs.chaos * 20  # ±20 velocity variation
    
    timestamp = 0
    
    for i, chord in enumerate(chords):
        # Parse chord root
        root = chord[0]
        if len(chord) > 1 and chord[1] in ('#', 'b'):
            root = chord[:2]
        
        base_note = root_to_midi.get(root, 60)
        
        # Determine chord tones
        if 'm' in chord.lower() and 'maj' not in chord.lower():
            # Minor chord
            intervals = [0, 3, 7]
        elif 'dim' in chord.lower():
            # Diminished
            intervals = [0, 3, 6]
        elif 'aug' in chord.lower():
            # Augmented
            intervals = [0, 4, 8]
        else:
            # Major chord
            intervals = [0, 4, 7]
        
        # Add 7th based on complexity
        if knobs.complexity > 0.5:
            if '7' in chord or 'maj7' in chord.lower():
                intervals.append(11 if 'maj7' in chord.lower() else 10)
        
        # Calculate velocity with humanization
        import random
        velocity = int(base_velocity + random.uniform(-humanization, humanization))
        velocity = max(1, min(127, velocity))
        
        # Generate note on/off for each chord tone
        for interval in intervals:
            note = base_note + interval
            
            # Note On
            events.append(MidiEvent(
                status=0x90,  # Note On, channel 1
                data1=note,
                data2=velocity,
                timestamp=timestamp,
            ))
        
        # Calculate note duration based on gate
        duration_samples = int(samples_per_beat * knobs.gate)
        
        # Note Offs
        for interval in intervals:
            note = base_note + interval
            events.append(MidiEvent(
                status=0x80,  # Note Off, channel 1
                data1=note,
                data2=0,
                timestamp=timestamp + duration_samples,
            ))
        
        # Move to next beat
        timestamp += samples_per_beat
    
    return events


async def process_prompt(
    text_prompt: str,
    knobs: Optional[Dict[str, float]] = None,
    genres: Optional[Dict[str, Any]] = None,
    trigger_innovation: bool = False,
) -> BridgeResult:
    """
    Main entry point for processing a text prompt from C++ Side B.
    
    This function:
    1. Detects genre from text
    2. Computes Ghost Hands suggestions
    3. Runs the orchestrator pipeline
    4. Generates MIDI events
    
    Args:
        text_prompt: User text input
        knobs: Current knob values
        genres: Available genre definitions
        trigger_innovation: Whether to trigger innovation protocol
        
    Returns:
        BridgeResult with MIDI events and suggestions
    """
    try:
        # Parse knobs
        knob_state = KnobState.from_dict(knobs or {})
        
        # Load genres if not provided
        if genres is None:
            genres = load_genre_definitions()
        
        # Detect genre from text
        detected_genre, confidence = detect_genre_from_text(text_prompt, genres)
        genre_data = genres.get(detected_genre, {})
        
        # If no genre detected, use defaults
        if not genre_data:
            detected_genre = "lofi_hiphop"  # Default genre
            genre_data = genres.get(detected_genre, {})
        
        # Compute Ghost Hands suggestions
        suggested_chaos, suggested_complexity = compute_ghost_hands_suggestions(
            text_prompt, genre_data, knob_state
        )
        
        # Prepare input for orchestrator
        emotion = "neutral"
        emotional_tags = genre_data.get("emotional_tags", [])
        if emotional_tags:
            # Use first matching emotional tag from text
            text_lower = text_prompt.lower()
            for tag in emotional_tags:
                if tag.lower() in text_lower:
                    emotion = tag
                    break
            if emotion == "neutral":
                emotion = emotional_tags[0]
        
        # Get key from text or use default
        key = "C"
        for k in ["C", "D", "E", "F", "G", "A", "B"]:
            if f" {k} " in f" {text_prompt} " or f" {k} major" in text_prompt.lower():
                key = k
                break
            if f" {k}m " in f" {text_prompt} " or f" {k} minor" in text_prompt.lower():
                key = k
                break
        
        # Create orchestrator and pipeline
        config = OrchestratorConfig(enable_logging=True)
        orchestrator = AIOrchestrator(config)
        
        pipeline = Pipeline("idaw_bridge")
        pipeline.add_stage("intent", IntentProcessor())
        pipeline.add_stage("harmony", HarmonyProcessor())
        pipeline.add_stage("groove", GrooveProcessor())
        
        # Execute pipeline
        input_data = {
            "mood_primary": emotion,
            "emotion": emotion,
            "technical_key": key,
            "key": key,
            "technical_mode": "minor" if "minor" in text_prompt.lower() else "major",
            "mode": "minor" if "minor" in text_prompt.lower() else "major",
            "text_prompt": text_prompt,
            "trigger_innovation": trigger_innovation,
        }
        
        result = await orchestrator.execute(pipeline, input_data)
        
        if not result.success:
            return BridgeResult(
                success=False,
                error_message=result.error or "Pipeline execution failed",
                suggested_chaos=suggested_chaos,
                suggested_complexity=suggested_complexity,
                detected_genre=detected_genre,
            )
        
        # Extract harmony data from result
        harmony_data = result.context.get_shared("harmony") if result.context else None
        chords = []
        if harmony_data:
            chords = harmony_data.get("chords", ["C", "G", "Am", "F"])
        else:
            # Default progression
            chords = ["C", "G", "Am", "F"]
        
        # Get tempo from genre
        bpm_range = genre_data.get("bpm_range", [100, 120])
        tempo = (bpm_range[0] + bpm_range[1]) // 2
        
        # SAFETY: Resolve any contradictions in parameters before MIDI generation
        generation_params = {
            "chaos": knob_state.chaos,
            "complexity": knob_state.complexity,
            "gate": knob_state.gate,
            "swing": knob_state.swing,
            "tempo": tempo,
            "grid": knob_state.grid,
            "velocity_min": genre_data.get("velocity", {}).get("min", 40),
            "velocity_max": genre_data.get("velocity", {}).get("max", 120),
        }
        resolved_params = resolve_contradictions(generation_params)
        
        # Apply resolved parameters back to knob state
        knob_state.chaos = resolved_params["chaos"]
        knob_state.complexity = resolved_params["complexity"]
        knob_state.gate = resolved_params["gate"]
        knob_state.swing = resolved_params["swing"]
        tempo = int(resolved_params["tempo"])
        
        # Generate MIDI events
        midi_events = generate_midi_from_harmony(
            chords, key, tempo, knob_state, genre_data
        )
        
        return BridgeResult(
            success=True,
            midi_events=midi_events,
            suggested_chaos=suggested_chaos,
            suggested_complexity=suggested_complexity,
            detected_genre=detected_genre,
            metadata={
                "chords": chords,
                "key": key,
                "tempo": tempo,
                "emotion": emotion,
                "confidence": confidence,
            },
        )
        
    except Exception as e:
        return BridgeResult(
            success=False,
            error_message=str(e),
        )


def process_prompt_sync(
    text_prompt: str,
    knobs: Optional[Dict[str, float]] = None,
    genres: Optional[Dict[str, Any]] = None,
    trigger_innovation: bool = False,
) -> BridgeResult:
    """
    Synchronous wrapper for process_prompt.
    Used by C++ pybind11 bridge.
    """
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(
            process_prompt(text_prompt, knobs, genres, trigger_innovation)
        )
    finally:
        loop.close()
