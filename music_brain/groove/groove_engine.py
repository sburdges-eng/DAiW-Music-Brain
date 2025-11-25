"""
groove_engine.py
================

Humanization / "Drunken Drummer" layer for DAiW.

Applies psychoacoustically-informed jitter to:
- Micro-timing (start_tick)
- Dynamics (velocity)
- Note probability (dropouts / ghost notes)

Axes:
- complexity: how off-grid / chaotic the timing & structure are
- vulnerability: how fragile / expressive the dynamics and feel are

This module provides a more emotionally-driven approach to humanization
compared to the basic random humanization in applicator.py.
"""

import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


# ==============================================================================
# TUNABLE CONSTANTS (TWIDDLE THESE WHILE LISTENING)
# ==============================================================================

# Chance a quiet "ghost" note is added near an existing hit
GHOST_NOTE_PROBABILITY = 0.15

# Above this random threshold, a hit becomes an "accent"
ACCENT_THRESHOLD = 0.7

# How many ticks a drummer is allowed to drift from perfect grid
MAX_TICKS_DRIFT = 35  # ~a small fraction of a 16th note at 960 PPQ

# Humans tend to land just behind the beat a little
HUMAN_LATENCY_BIAS = 5  # ticks

# Velocity safety bounds (don't blast 127 all the time)
VELOCITY_MIN = 20
VELOCITY_MAX = 120

# When complexity is maxed, how many notes are allowed to drop out (approx)
MAX_DROPOUT_PROB = 0.2  # 20% at complexity=1.0

# Drum MIDI note numbers for special handling
DRUM_NOTES = {
    "kick": [35, 36],           # Acoustic/Electric Bass Drum
    "snare": [38, 40],          # Acoustic/Electric Snare
    "hihat_closed": [42],       # Closed Hi-Hat
    "hihat_open": [46],         # Open Hi-Hat
    "hihat_pedal": [44],        # Pedal Hi-Hat
    "tom_high": [48, 50],       # High/Hi-Mid Tom
    "tom_mid": [45, 47],        # Low/Low-Mid Tom
    "tom_low": [41, 43],        # Floor Tom
    "crash": [49, 57],          # Crash Cymbals
    "ride": [51, 59],           # Ride Cymbal
    "ride_bell": [53],          # Ride Bell
}

# Protection levels: some drum elements shouldn't drop out as easily
PROTECTION_LEVELS = {
    "kick": 0.8,      # Kicks rarely drop (reduce dropout by 80%)
    "snare": 0.7,     # Snares are important
    "hihat_closed": 0.2,  # Hi-hats can drop more freely
    "hihat_open": 0.5,
    "crash": 0.9,     # Crashes are intentional
    "ride": 0.3,
}


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class GrooveSettings:
    """
    Settings for the groove engine humanization.

    These can be loaded from presets or set dynamically based on
    emotional intent from the SongIntent system.
    """
    complexity: float = 0.5       # 0.0-1.0: timing looseness, dropout probability
    vulnerability: float = 0.5    # 0.0-1.0: dynamic range, softness

    # Optional overrides
    timing_sigma_override: Optional[float] = None
    dropout_prob_override: Optional[float] = None
    velocity_range_override: Optional[tuple] = None

    # Per-drum adjustments (multipliers)
    kick_timing_mult: float = 0.5     # Kicks are usually tighter
    snare_timing_mult: float = 0.7    # Snares slightly tighter
    hihat_timing_mult: float = 1.2    # Hi-hats can be looser

    # Ghost note settings
    enable_ghost_notes: bool = True
    ghost_note_probability: float = GHOST_NOTE_PROBABILITY
    ghost_note_velocity_mult: float = 0.4  # Ghost notes at 40% of original

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "complexity": self.complexity,
            "vulnerability": self.vulnerability,
            "timing_sigma_override": self.timing_sigma_override,
            "dropout_prob_override": self.dropout_prob_override,
            "velocity_range_override": self.velocity_range_override,
            "kick_timing_mult": self.kick_timing_mult,
            "snare_timing_mult": self.snare_timing_mult,
            "hihat_timing_mult": self.hihat_timing_mult,
            "enable_ghost_notes": self.enable_ghost_notes,
            "ghost_note_probability": self.ghost_note_probability,
            "ghost_note_velocity_mult": self.ghost_note_velocity_mult,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GrooveSettings":
        """Deserialize from dictionary."""
        return cls(
            complexity=data.get("complexity", 0.5),
            vulnerability=data.get("vulnerability", 0.5),
            timing_sigma_override=data.get("timing_sigma_override"),
            dropout_prob_override=data.get("dropout_prob_override"),
            velocity_range_override=data.get("velocity_range_override"),
            kick_timing_mult=data.get("kick_timing_mult", 0.5),
            snare_timing_mult=data.get("snare_timing_mult", 0.7),
            hihat_timing_mult=data.get("hihat_timing_mult", 1.2),
            enable_ghost_notes=data.get("enable_ghost_notes", True),
            ghost_note_probability=data.get("ghost_note_probability", GHOST_NOTE_PROBABILITY),
            ghost_note_velocity_mult=data.get("ghost_note_velocity_mult", 0.4),
        )


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def _get_drum_category(pitch: int) -> Optional[str]:
    """
    Identify which drum category a MIDI pitch belongs to.

    Args:
        pitch: MIDI note number

    Returns:
        Category name or None if not a recognized drum
    """
    for category, pitches in DRUM_NOTES.items():
        if pitch in pitches:
            return category
    return None


def _get_timing_multiplier(pitch: int, settings: GrooveSettings) -> float:
    """
    Get timing tightness multiplier based on drum type.

    Lower values = tighter timing (less deviation from grid).
    """
    category = _get_drum_category(pitch)
    if category == "kick":
        return settings.kick_timing_mult
    elif category == "snare":
        return settings.snare_timing_mult
    elif category and "hihat" in category:
        return settings.hihat_timing_mult
    return 1.0


def _get_dropout_protection(pitch: int) -> float:
    """
    Get dropout protection level for a drum type.

    Higher values = less likely to be dropped.
    """
    category = _get_drum_category(pitch)
    return PROTECTION_LEVELS.get(category, 0.0)


def _vulnerability_to_velocity_params(vulnerability: float, base_velocity: int) -> tuple:
    """
    Convert vulnerability setting to velocity processing parameters.

    Args:
        vulnerability: 0.0-1.0 scale
        base_velocity: Original velocity value

    Returns:
        (target_velocity, velocity_sigma)
    """
    if vulnerability < 0.3:
        # Low vulnerability: confident, tight, slightly louder
        vel_sigma = 5
        target_vel = base_velocity + 10
    elif vulnerability < 0.6:
        # Medium vulnerability: balanced feel
        vel_sigma = 10 + int((vulnerability - 0.3) * 30)
        target_vel = base_velocity
    else:
        # High vulnerability: wide variance, trending softer
        vel_sigma = 10 + int(vulnerability * 20)
        target_vel = base_velocity - int(vulnerability * 20)

    return target_vel, vel_sigma


# ==============================================================================
# CORE GROOVE FUNCTION
# ==============================================================================

def apply_groove(
    events: List[Dict[str, Any]],
    complexity: float,
    vulnerability: float,
    ppq: int = 480,
    settings: Optional[GrooveSettings] = None,
    seed: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Applies "Humanization" via Gaussian timing jitter and velocity shaping.

    This is the "Drunken Drummer" algorithm - it makes MIDI feel more human
    by introducing psychoacoustically-informed variations in timing and dynamics.

    Args:
        events:
            List of note dicts with at least:
            - 'start_tick' : int
            - 'velocity'   : int
            - 'pitch'      : int (optional, for drum-specific handling)
        complexity (0.0 - 1.0):
            Controls timing looseness and dropped notes.
            High = off-grid, occasional dropouts.
        vulnerability (0.0 - 1.0):
            Controls dynamic range and perceived fragility.
            High = wider dynamic range, generally softer & more unstable.
        ppq:
            Pulses Per Quarter-note. Used for scaling relative to tempo/grid.
        settings:
            Optional GrooveSettings for fine-tuned control.
        seed:
            Optional random seed for reproducibility.

    Returns:
        New list of note events with updated start_tick and velocity.
    """
    if seed is not None:
        random.seed(seed)

    # Clamp parameters
    complexity = max(0.0, min(1.0, complexity))
    vulnerability = max(0.0, min(1.0, vulnerability))

    # Use settings if provided, otherwise create default
    if settings is None:
        settings = GrooveSettings(complexity=complexity, vulnerability=vulnerability)
    else:
        # Override settings with passed parameters
        settings.complexity = complexity
        settings.vulnerability = vulnerability

    processed_events: List[Dict[str, Any]] = []

    # Timing sigma: how far we can realistically move from the grid.
    # At complexity=0 -> very tight; at 1 -> near MAX_TICKS_DRIFT.
    # Scale based on PPQ (default constants assume 480 PPQ)
    ppq_scale = ppq / 480.0
    base_timing_sigma = (
        settings.timing_sigma_override
        if settings.timing_sigma_override is not None
        else MAX_TICKS_DRIFT * ppq_scale
    )

    # Dropout probability calculation
    base_dropout_prob = (
        settings.dropout_prob_override
        if settings.dropout_prob_override is not None
        else complexity * MAX_DROPOUT_PROB
    )

    for note in events:
        start_tick = int(note.get("start_tick", 0))
        base_velocity = int(note.get("velocity", 80))
        pitch = int(note.get("pitch", 0))

        # ----------------------------------------------------------------------
        # 1. CHAOS: Dropped notes (probability mask)
        # ----------------------------------------------------------------------
        # At max complexity, we allow up to MAX_DROPOUT_PROB chance of dropping.
        # Protected drums (kick, snare, crash) have reduced dropout probability.

        protection = _get_dropout_protection(pitch)
        effective_dropout = base_dropout_prob * (1.0 - protection)

        if effective_dropout > 0.0 and random.random() < effective_dropout:
            # Drop this note altogether
            continue

        # ----------------------------------------------------------------------
        # 2. CHAOS: Timing jitter (Gaussian, not uniform)
        # ----------------------------------------------------------------------
        # Gaussian around 0, sigma scaled by complexity and drum type.
        timing_mult = _get_timing_multiplier(pitch, settings)
        timing_sigma = base_timing_sigma * complexity * timing_mult

        if timing_sigma <= 0.0:
            jitter = 0
        else:
            jitter = int(random.gauss(0, timing_sigma))

        # Clamp jitter to a safe band
        max_drift = int(MAX_TICKS_DRIFT * ppq_scale)
        jitter = max(-max_drift, min(max_drift, jitter))

        # Human latency bias: most humans are slightly late, not early
        latency_bias = int(HUMAN_LATENCY_BIAS * ppq_scale)
        jitter += latency_bias

        new_tick = max(0, start_tick + jitter)

        # ----------------------------------------------------------------------
        # 3. VULNERABILITY: Velocity shaping
        # ----------------------------------------------------------------------
        target_vel, vel_sigma = _vulnerability_to_velocity_params(
            vulnerability, base_velocity
        )

        # Apply velocity range override if specified
        vel_min = VELOCITY_MIN
        vel_max = VELOCITY_MAX
        if settings.velocity_range_override:
            vel_min, vel_max = settings.velocity_range_override

        new_vel = int(random.gauss(target_vel, vel_sigma))
        new_vel = max(vel_min, min(vel_max, new_vel))

        # Create processed note
        new_note = note.copy()
        new_note["start_tick"] = new_tick
        new_note["velocity"] = new_vel

        processed_events.append(new_note)

        # ----------------------------------------------------------------------
        # 4. Optional: Ghost notes
        # ----------------------------------------------------------------------
        if (settings.enable_ghost_notes and
            vulnerability > 0.6 and
            random.random() < settings.ghost_note_probability):

            ghost = new_note.copy()
            ghost["velocity"] = max(
                vel_min,
                int(new_vel * settings.ghost_note_velocity_mult)
            )
            ghost["start_tick"] = max(
                0,
                new_tick + random.randint(-int(10 * ppq_scale), int(10 * ppq_scale))
            )
            ghost["is_ghost"] = True
            processed_events.append(ghost)

    return processed_events


def humanize_drums(
    events: List[Dict[str, Any]],
    complexity: float = 0.5,
    vulnerability: float = 0.5,
    ppq: int = 480,
    settings: Optional[GrooveSettings] = None,
    seed: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Alias for apply_groove with a more descriptive name for drum-specific use.

    This is the main entry point for drum humanization in the DAiW system.
    """
    return apply_groove(
        events=events,
        complexity=complexity,
        vulnerability=vulnerability,
        ppq=ppq,
        settings=settings,
        seed=seed,
    )


# ==============================================================================
# MIDI FILE PROCESSING
# ==============================================================================

def humanize_midi_file(
    input_path: str,
    output_path: Optional[str] = None,
    complexity: float = 0.5,
    vulnerability: float = 0.5,
    drum_channel: int = 9,
    settings: Optional[GrooveSettings] = None,
    seed: Optional[int] = None,
) -> str:
    """
    Apply drum humanization to a MIDI file.

    Args:
        input_path: Path to input MIDI file
        output_path: Path for output file (default: input_humanized.mid)
        complexity: Timing chaos level (0.0-1.0)
        vulnerability: Dynamic fragility (0.0-1.0)
        drum_channel: MIDI channel for drums (default: 9, i.e. channel 10)
        settings: Optional GrooveSettings for fine control
        seed: Random seed for reproducibility

    Returns:
        Path to the output file
    """
    try:
        import mido
    except ImportError:
        raise ImportError("mido package required. Install with: pip install mido")

    from pathlib import Path

    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"MIDI file not found: {input_path}")

    # Load MIDI
    mid = mido.MidiFile(str(input_path))
    output_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)

    for track in mid.tracks:
        new_track = mido.MidiTrack()
        output_mid.tracks.append(new_track)

        # Extract note events from this track
        current_tick = 0
        events = []
        event_indices = []  # Track which messages are note events

        for i, msg in enumerate(track):
            current_tick += msg.time

            if msg.type == 'note_on' and msg.velocity > 0:
                # Check if this is on the drum channel
                if hasattr(msg, 'channel') and msg.channel == drum_channel:
                    events.append({
                        "start_tick": current_tick,
                        "velocity": msg.velocity,
                        "pitch": msg.note,
                        "original_index": i,
                    })
                    event_indices.append(i)

        # Apply humanization to drum events
        if events:
            humanized = humanize_drums(
                events=events,
                complexity=complexity,
                vulnerability=vulnerability,
                ppq=mid.ticks_per_beat,
                settings=settings,
                seed=seed,
            )

            # Create mapping from original to humanized
            humanized_map = {}
            for h_event in humanized:
                if "original_index" in h_event and not h_event.get("is_ghost"):
                    humanized_map[h_event["original_index"]] = h_event

            # Collect ghost notes for later insertion
            ghost_notes = [e for e in humanized if e.get("is_ghost")]
        else:
            humanized_map = {}
            ghost_notes = []

        # Rebuild track with humanized timing/velocity
        current_tick = 0
        pending_ghost_notes = sorted(ghost_notes, key=lambda x: x["start_tick"])

        for i, msg in enumerate(track):
            target_tick = current_tick + msg.time

            # Insert any ghost notes that should come before this message
            while pending_ghost_notes and pending_ghost_notes[0]["start_tick"] <= target_tick:
                ghost = pending_ghost_notes.pop(0)
                ghost_delta = ghost["start_tick"] - current_tick
                ghost_msg = mido.Message(
                    'note_on',
                    note=ghost["pitch"],
                    velocity=ghost["velocity"],
                    channel=drum_channel,
                    time=max(0, ghost_delta)
                )
                new_track.append(ghost_msg)
                current_tick = ghost["start_tick"]

                # Add note_off for ghost
                ghost_off = mido.Message(
                    'note_off',
                    note=ghost["pitch"],
                    velocity=0,
                    channel=drum_channel,
                    time=mid.ticks_per_beat // 8  # Short duration
                )
                new_track.append(ghost_off)
                current_tick += mid.ticks_per_beat // 8

            if i in humanized_map:
                h_event = humanized_map[i]

                # Calculate delta from current position
                delta = h_event["start_tick"] - current_tick
                delta = max(0, delta)  # Ensure non-negative

                new_msg = msg.copy(time=delta, velocity=h_event["velocity"])
                new_track.append(new_msg)
                current_tick = h_event["start_tick"]
            else:
                # Non-drum event or note_off: preserve original timing relative to current
                delta = target_tick - current_tick
                delta = max(0, delta)
                new_msg = msg.copy(time=delta)
                new_track.append(new_msg)
                current_tick = target_tick

    # Determine output path
    if output_path is None:
        output_path = str(input_path.stem) + "_humanized.mid"

    output_path = Path(output_path)
    output_mid.save(str(output_path))

    return str(output_path)


# ==============================================================================
# PRESET INTEGRATION
# ==============================================================================

def settings_from_intent(
    vulnerability_scale: str,
    groove_feel: str,
    mood_tension: float = 0.5,
) -> GrooveSettings:
    """
    Create GrooveSettings from song intent parameters.

    Maps emotional intent to concrete humanization settings.

    Args:
        vulnerability_scale: "Low", "Medium", or "High"
        groove_feel: From GrooveFeel enum (e.g., "Laid Back", "Mechanical")
        mood_tension: Secondary tension level (0.0-1.0)

    Returns:
        GrooveSettings configured for the emotional intent
    """
    # Map vulnerability scale to numeric value
    vulnerability_map = {
        "Low": 0.2,
        "Medium": 0.5,
        "High": 0.8,
    }
    vulnerability = vulnerability_map.get(vulnerability_scale, 0.5)

    # Map groove feel to complexity
    complexity_map = {
        "Straight/Driving": 0.2,
        "Mechanical": 0.0,
        "Laid Back": 0.6,
        "Swung": 0.4,
        "Syncopated": 0.5,
        "Rubato/Free": 0.9,
        "Organic/Breathing": 0.7,
        "Push-Pull": 0.5,
    }
    complexity = complexity_map.get(groove_feel, 0.5)

    # Adjust based on mood tension
    complexity = complexity * (0.8 + mood_tension * 0.4)
    complexity = min(1.0, complexity)

    # Create settings
    settings = GrooveSettings(
        complexity=complexity,
        vulnerability=vulnerability,
    )

    # Special adjustments for certain feels
    if groove_feel == "Mechanical":
        settings.enable_ghost_notes = False
        settings.kick_timing_mult = 0.1
        settings.snare_timing_mult = 0.1
        settings.hihat_timing_mult = 0.1
    elif groove_feel == "Laid Back":
        settings.kick_timing_mult = 0.3
        settings.snare_timing_mult = 0.8
        settings.hihat_timing_mult = 1.0
    elif groove_feel == "Rubato/Free":
        settings.enable_ghost_notes = True
        settings.ghost_note_probability = 0.25

    return settings


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def quick_humanize(
    events: List[Dict[str, Any]],
    style: str = "natural",
    ppq: int = 480,
) -> List[Dict[str, Any]]:
    """
    Quick humanization with preset styles.

    Args:
        events: List of note events
        style: One of "tight", "natural", "loose", "drunk"
        ppq: Pulses per quarter note

    Returns:
        Humanized events
    """
    style_presets = {
        "tight": (0.1, 0.2),      # Tight, confident
        "natural": (0.4, 0.5),    # Natural human feel
        "loose": (0.6, 0.6),      # Relaxed, laid back
        "drunk": (0.9, 0.8),      # Very loose, vulnerable
    }

    complexity, vulnerability = style_presets.get(style, (0.4, 0.5))

    return apply_groove(
        events=events,
        complexity=complexity,
        vulnerability=vulnerability,
        ppq=ppq,
    )


# ==============================================================================
# PRESET LOADING
# ==============================================================================

def load_presets(path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load humanization presets from JSON file.

    Args:
        path: Path to presets JSON file. If None, loads default presets.

    Returns:
        Dictionary of preset configurations
    """
    import json
    from pathlib import Path

    if path is None:
        # Load default presets from package data
        package_dir = Path(__file__).parent.parent
        path = package_dir / "data" / "humanize_presets.json"

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_presets(path: Optional[str] = None) -> List[str]:
    """
    List available preset names.

    Args:
        path: Path to presets JSON file. If None, uses default presets.

    Returns:
        List of preset names
    """
    presets = load_presets(path)
    return list(presets.keys())


def get_preset(name: str, path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get a specific preset by name.

    Args:
        name: Preset name
        path: Path to presets JSON file. If None, uses default presets.

    Returns:
        Preset configuration or None if not found
    """
    presets = load_presets(path)
    return presets.get(name)


def settings_from_preset(preset_name: str, path: Optional[str] = None) -> GrooveSettings:
    """
    Create GrooveSettings from a named preset.

    Args:
        preset_name: Name of the preset to load
        path: Path to presets JSON file. If None, uses default presets.

    Returns:
        GrooveSettings configured according to the preset

    Raises:
        ValueError: If preset not found
    """
    preset = get_preset(preset_name, path)
    if preset is None:
        available = list_presets(path)
        raise ValueError(
            f"Preset '{preset_name}' not found. Available: {', '.join(available)}"
        )

    groove_data = preset.get("groove_settings", {})
    return GrooveSettings.from_dict(groove_data)
