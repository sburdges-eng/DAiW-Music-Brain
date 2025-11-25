"""
DAiW Comprehensive Engine - Interrogate Before Generate

The core therapy-to-music pipeline that:
1. Analyzes emotional content (AffectAnalyzer)
2. Guides the user through deep interrogation (TherapySession)
3. Generates a musically-meaningful plan (HarmonyPlan)
4. Renders to MIDI with guide tones and groove

Philosophy: Emotional intent drives technical decisions, not the other way around.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import re

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    mido = None
    MIDO_AVAILABLE = False


# =================================================================
# CONSTANTS & MAPPINGS
# =================================================================

# Keywords that trigger specific affects
AFFECT_KEYWORDS = {
    "grief": [
        "dead", "death", "dying", "mourning", "loss", "lost", "gone",
        "miss", "missing", "funeral", "grave", "buried", "widow",
        "orphan", "goodbye", "farewell", "departed", "passed",
    ],
    "rage": [
        "furious", "angry", "anger", "burn", "burning", "revenge",
        "hate", "hatred", "destroy", "kill", "violent", "fury",
        "rage", "seething", "livid", "wrathful", "vengeance",
    ],
    "awe": [
        "god", "divine", "infinite", "eternal", "cosmos", "universe",
        "sacred", "holy", "transcendent", "sublime", "wonder",
        "magnificent", "vast", "endless", "miraculous", "spiritual",
    ],
    "nostalgia": [
        "remember", "memory", "memories", "childhood", "youth",
        "before", "once", "used to", "back then", "old days",
        "reminisce", "recall", "yesterday", "past", "forgotten",
    ],
    "fear": [
        "panic", "scared", "afraid", "terrified", "terror", "trapped",
        "nightmare", "horror", "dread", "anxious", "anxiety",
        "helpless", "vulnerable", "danger", "threat", "flee",
    ],
    "dissociation": [
        "numb", "nothing", "empty", "hollow", "void", "detached",
        "floating", "unreal", "distant", "disconnected", "fog",
        "autopilot", "watching", "outside", "nowhere", "blank",
    ],
    "defiance": [
        "refuse", "never", "fight", "resist", "rebel", "strong",
        "survive", "stand", "rise", "overcome", "defy", "reject",
        "won't", "can't stop", "unstoppable", "warrior", "battle",
    ],
    "tenderness": [
        "gentle", "soft", "care", "caring", "tender", "delicate",
        "precious", "nurture", "protect", "hold", "embrace",
        "soothe", "comfort", "warm", "safe", "love", "loving",
    ],
    "confusion": [
        "chaos", "why", "confused", "lost", "uncertain", "unclear",
        "maze", "puzzle", "question", "doubt", "unsure", "what",
        "how", "spinning", "dizzy", "disoriented", "paradox",
    ],
}

# Affect to musical mode mapping
AFFECT_MODE_MAP = {
    "grief": "aeolian",        # Natural minor - melancholy
    "rage": "phrygian",        # Spanish/flamenco - intensity
    "awe": "lydian",           # Raised 4th - ethereal, bright
    "nostalgia": "mixolydian", # Blues/folk - bittersweet
    "fear": "locrian",         # Diminished - unstable, dark
    "dissociation": "locrian", # Most dissonant - disconnection
    "defiance": "mixolydian",  # Dominant - power, resolution
    "tenderness": "ionian",    # Major - warmth, comfort
    "confusion": "dorian",     # Minor with raised 6 - ambiguous
    "neutral": "ionian",       # Default to major
}

# Affect to base tempo mapping
AFFECT_TEMPO_BASE = {
    "grief": 60,
    "rage": 140,
    "awe": 70,
    "nostalgia": 85,
    "fear": 110,
    "dissociation": 55,
    "defiance": 120,
    "tenderness": 75,
    "confusion": 95,
    "neutral": 100,
}

# Chord quality definitions for guide tone generation
CHORD_QUALITIES = {
    "maj": (0, 4, 7),
    "min": (0, 3, 7),
    "dim": (0, 3, 6),
    "aug": (0, 4, 8),
    "7": (0, 4, 7, 10),
    "maj7": (0, 4, 7, 11),
    "min7": (0, 3, 7, 10),
    "dim7": (0, 3, 6, 9),
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
}


# =================================================================
# DATA CLASSES
# =================================================================

@dataclass
class AffectResult:
    """Result of emotional affect analysis."""
    primary: str                    # Primary detected affect
    secondary: Optional[str]        # Secondary affect (if present)
    scores: Dict[str, float]        # Raw scores per affect
    intensity: float               # Overall emotional intensity (0-1)

    def __repr__(self) -> str:
        return f"AffectResult(primary={self.primary}, intensity={self.intensity:.2f})"


@dataclass
class TherapyState:
    """Current state of the therapy session."""
    core_wound_text: str = ""
    core_wound_name: str = ""
    affect_result: Optional[AffectResult] = None
    motivation: float = 5.0        # 1-10 scale
    chaos_tolerance: float = 0.5   # 0-1 scale
    suggested_mode: str = "ionian"
    phase: int = 0


@dataclass
class HarmonyPlan:
    """
    Generated harmony plan from therapy session.

    This is the bridge between emotional intent and musical implementation.
    """
    root_note: str = "C"
    mode: str = "minor"
    tempo_bpm: int = 120
    time_signature: str = "4/4"
    length_bars: int = 16
    chord_symbols: List[str] = field(default_factory=list)
    harmonic_rhythm: str = "1_chord_per_bar"
    mood_profile: str = "neutral"
    complexity: float = 0.5       # 0-1: affects groove humanization
    vulnerability: float = 0.5    # 0-1: affects dynamics

    def __post_init__(self):
        if not self.chord_symbols:
            # Default progression based on mode
            if self.mode in ["minor", "aeolian"]:
                self.chord_symbols = [f"{self.root_note}m", "Fm", f"{self.root_note}m", "Gm"]
            else:
                self.chord_symbols = [self.root_note, "F", self.root_note, "G"]


# =================================================================
# AFFECT ANALYZER
# =================================================================

class AffectAnalyzer:
    """
    Analyzes text for emotional affect.

    Detects emotional keywords and maps them to musical affects
    that drive mode selection and other musical parameters.
    """

    def __init__(self, keywords: Optional[Dict[str, List[str]]] = None):
        self.keywords = keywords or AFFECT_KEYWORDS

    def analyze(self, text: str) -> AffectResult:
        """
        Analyze text for emotional content.

        Args:
            text: Input text (therapy session answers, etc.)

        Returns:
            AffectResult with primary/secondary affects and scores
        """
        if not text or not text.strip():
            return AffectResult(
                primary="neutral",
                secondary=None,
                scores={},
                intensity=0.0,
            )

        text_lower = text.lower()
        scores: Dict[str, float] = {}

        # Count keyword matches for each affect
        for affect, keywords in self.keywords.items():
            count = 0
            for keyword in keywords:
                # Use word boundary matching
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, text_lower)
                count += len(matches)

            if count > 0:
                scores[affect] = float(count)

        if not scores:
            return AffectResult(
                primary="neutral",
                secondary=None,
                scores={},
                intensity=0.0,
            )

        # Sort by score to find primary and secondary
        sorted_affects = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_affects[0][0]
        secondary = sorted_affects[1][0] if len(sorted_affects) > 1 else None

        # Calculate intensity (normalized)
        total_score = sum(scores.values())
        max_possible = len(text.split())  # Rough estimate
        intensity = min(1.0, total_score / max(max_possible * 0.1, 1))

        return AffectResult(
            primary=primary,
            secondary=secondary,
            scores=scores,
            intensity=intensity,
        )


# =================================================================
# THERAPY SESSION
# =================================================================

class TherapySession:
    """
    Guides the user through emotional interrogation and generates
    a music plan based on their responses.

    Implements the "Interrogate Before Generate" philosophy.
    """

    def __init__(self):
        self.analyzer = AffectAnalyzer()
        self.state = TherapyState()

    def process_core_input(self, text: str) -> AffectResult:
        """
        Process the core wound/desire input from Phase 0.

        Args:
            text: User's response to the core wound question

        Returns:
            Analyzed affect result
        """
        self.state.core_wound_text = text
        self.state.affect_result = self.analyzer.analyze(text)
        self.state.core_wound_name = self.state.affect_result.primary

        # Map affect to suggested mode
        self.state.suggested_mode = AFFECT_MODE_MAP.get(
            self.state.affect_result.primary,
            "ionian"
        )

        return self.state.affect_result

    def set_scales(self, motivation: float, chaos_tolerance: float):
        """
        Set the motivation and chaos tolerance scales.

        Args:
            motivation: 1-10 scale of commitment/energy
            chaos_tolerance: 0-1 scale of comfort with disorder
        """
        self.state.motivation = max(1.0, min(10.0, motivation))
        self.state.chaos_tolerance = max(0.0, min(1.0, chaos_tolerance))

    def generate_plan(self) -> HarmonyPlan:
        """
        Generate a HarmonyPlan based on the current therapy state.

        Returns:
            HarmonyPlan ready for MIDI rendering
        """
        affect = self.state.affect_result or AffectResult(
            "neutral", None, {}, 0.0
        )

        # Determine song length based on motivation
        if self.state.motivation <= 3:
            length_bars = 16
        elif self.state.motivation <= 7:
            length_bars = 32
        else:
            length_bars = 64

        # Calculate tempo from affect + chaos
        base_tempo = AFFECT_TEMPO_BASE.get(affect.primary, 100)
        chaos_modifier = int(self.state.chaos_tolerance * 40)  # +0 to +40 BPM
        tempo = base_tempo + chaos_modifier

        # Determine root note (default to C, but could be smarter)
        root_note = "C"

        # Build chord progression based on mode
        mode = self.state.suggested_mode
        chord_symbols = self._generate_progression(root_note, mode)

        # Complexity from chaos tolerance
        complexity = self.state.chaos_tolerance

        # Vulnerability inversely related to motivation (low motivation = more exposed)
        vulnerability = 1.0 - (self.state.motivation / 10.0)

        return HarmonyPlan(
            root_note=root_note,
            mode=mode,
            tempo_bpm=tempo,
            time_signature="4/4",
            length_bars=length_bars,
            chord_symbols=chord_symbols,
            harmonic_rhythm="1_chord_per_bar",
            mood_profile=affect.primary,
            complexity=complexity,
            vulnerability=vulnerability,
        )

    def _generate_progression(self, root: str, mode: str) -> List[str]:
        """Generate a chord progression based on mode."""
        # Simple progressions for each mode
        progressions = {
            "ionian": [f"{root}", "F", "G", f"{root}"],
            "dorian": [f"{root}m", f"{root}m", "Gm", "F"],
            "phrygian": [f"{root}m", "Db", "Eb", f"{root}m"],
            "lydian": [f"{root}", "D", "E", f"{root}"],
            "mixolydian": [f"{root}", "Bb", "F", f"{root}"],
            "aeolian": [f"{root}m", "Fm", f"{root}m", "Gm"],
            "locrian": [f"{root}dim", "Db", "Gbm", f"{root}dim"],
            "minor": [f"{root}m", "Fm", f"{root}m", "Gm"],
        }
        return progressions.get(mode, progressions["ionian"])


# =================================================================
# MIDI RENDERING
# =================================================================

def render_plan_to_midi(
    plan: HarmonyPlan,
    output_path: str = "daiw_therapy_session.mid",
    include_guide_tones: bool = True,
) -> str:
    """
    Render a HarmonyPlan to MIDI file with harmony and guide tones.

    Creates two tracks:
    1. Harmony - Full chord voicings
    2. Guide Tones - 3rds and 7ths for melodic rails

    Args:
        plan: HarmonyPlan to render
        output_path: Output MIDI file path
        include_guide_tones: Whether to include guide tone track

    Returns:
        Path to exported MIDI file
    """
    try:
        from music_brain.daw.logic import LogicProject, LOGIC_CHANNELS
        from music_brain.structure.progression import parse_progression_string
    except ImportError:
        print("[RENDER]: Required modules not available, returning path only")
        return output_path

    if not MIDO_AVAILABLE:
        print("[RENDER]: mido not installed, returning path only")
        return output_path

    # Parse time signature
    try:
        ts_parts = plan.time_signature.split("/")
        time_sig = (int(ts_parts[0]), int(ts_parts[1]))
    except (ValueError, IndexError):
        time_sig = (4, 4)

    # Create Logic project
    project = LogicProject(
        name="DAiW_Session",
        tempo_bpm=plan.tempo_bpm,
        time_signature=time_sig,
    )

    # Parse the chord progression
    progression_str = "-".join(plan.chord_symbols)
    parsed_chords = parse_progression_string(progression_str)

    if not parsed_chords:
        print("[RENDER]: Could not parse chord progression")
        return output_path

    # Build MIDI notes from ParsedChord + CHORD_QUALITIES
    ppq = getattr(project, "ppq", 480)
    beats_per_bar = time_sig[0]
    bar_ticks = int(beats_per_bar * ppq)

    # One chord per bar, looped to fill song length
    harmony_notes = []
    guide_notes = []

    start_tick = 0
    current_bar = 0
    total_bars = plan.length_bars

    while current_bar < total_bars:
        for parsed in parsed_chords:
            if current_bar >= total_bars:
                break

            quality = parsed.quality
            intervals = CHORD_QUALITIES.get(quality)

            if intervals is None:
                # Fall back based on quality string
                if "m" in quality.lower() and "maj" not in quality.lower():
                    intervals = CHORD_QUALITIES.get("min", (0, 3, 7))
                else:
                    intervals = CHORD_QUALITIES.get("maj", (0, 4, 7))

            root_midi = 48 + parsed.root_num  # C3 as base
            duration_ticks = bar_ticks

            # Build velocity based on vulnerability
            base_velocity = 80
            vuln_mod = int((1 - plan.vulnerability) * 20)  # 0-20
            harmony_velocity = base_velocity + vuln_mod

            # Full harmony stack
            for interval in intervals:
                harmony_notes.append({
                    "pitch": root_midi + interval,
                    "velocity": min(127, harmony_velocity),
                    "start_tick": start_tick,
                    "duration_ticks": duration_ticks,
                })

            # Guide tones: 3rd and 7th if available
            if include_guide_tones and len(intervals) >= 3:
                third_interval = intervals[1]  # 3rd is always index 1
                seventh_interval = intervals[3] if len(intervals) >= 4 else intervals[-1]

                guide_notes.append({
                    "pitch": root_midi + third_interval,
                    "velocity": 60,
                    "start_tick": start_tick,
                    "duration_ticks": duration_ticks,
                })
                guide_notes.append({
                    "pitch": root_midi + seventh_interval,
                    "velocity": 60,
                    "start_tick": start_tick,
                    "duration_ticks": duration_ticks,
                })

            start_tick += duration_ticks
            current_bar += 1

    # Apply groove to humanize timing
    try:
        from music_brain.groove_engine import apply_groove

        harmony_notes = apply_groove(
            events=harmony_notes,
            complexity=plan.complexity,
            vulnerability=plan.vulnerability,
            ppq=ppq,
        )

        guide_notes = apply_groove(
            events=guide_notes,
            complexity=plan.complexity * 0.5,  # Keep guides tighter
            vulnerability=plan.vulnerability,
            ppq=ppq,
        )
    except ImportError:
        # No groove engine available, use notes as-is
        pass

    # Add tracks
    keys_channel = LOGIC_CHANNELS.get("keys", 2)
    guide_channel = LOGIC_CHANNELS.get("pad", 5)

    project.add_track(
        name="Harmony",
        channel=keys_channel,
        instrument=None,
        notes=harmony_notes,
    )

    if include_guide_tones and guide_notes:
        project.add_track(
            name="Guide Tones",
            channel=guide_channel,
            instrument=None,
            notes=guide_notes,
        )

    # Export
    return project.export_midi(output_path)


# =================================================================
# CLI INTERFACE
# =================================================================

def run_cli():
    """
    Interactive CLI for the therapy session.

    Guides user through:
    1. Core wound input
    2. Motivation scale
    3. Chaos tolerance scale
    4. Generates and exports MIDI
    """
    print("\n" + "=" * 50)
    print("  DAiW COMPREHENSIVE ENGINE")
    print("  Interrogate Before Generate")
    print("=" * 50 + "\n")

    session = TherapySession()

    # Phase 0: Core wound
    print("PHASE 0: THE CORE WOUND")
    print("-" * 40)
    print("What happened? What's the emotional core of this song?")
    print("(Write freely - include feelings, images, memories)\n")

    while True:
        core_input = input("> ").strip()
        if core_input:
            break
        print("Please share something about your emotional experience.")

    affect = session.process_core_input(core_input)
    print(f"\n[Detected affect: {affect.primary}]")
    print(f"[Suggested mode: {session.state.suggested_mode}]\n")

    # Scales
    print("PHASE 1: SCALES")
    print("-" * 40)

    while True:
        try:
            motivation = float(input("Motivation (1-10, how much energy for this?): "))
            if 1 <= motivation <= 10:
                break
        except ValueError:
            pass
        print("Please enter a number between 1 and 10.")

    while True:
        try:
            chaos = float(input("Chaos tolerance (0-10, comfort with disorder): "))
            if 0 <= chaos <= 10:
                chaos = chaos / 10.0  # Normalize to 0-1
                break
        except ValueError:
            pass
        print("Please enter a number between 0 and 10.")

    session.set_scales(motivation, chaos)

    # Generate plan
    print("\n" + "=" * 50)
    print("GENERATING HARMONY PLAN")
    print("=" * 50 + "\n")

    plan = session.generate_plan()

    print(f"Root: {plan.root_note}")
    print(f"Mode: {plan.mode}")
    print(f"Tempo: {plan.tempo_bpm} BPM")
    print(f"Length: {plan.length_bars} bars")
    print(f"Mood: {plan.mood_profile}")
    print(f"Progression: {' - '.join(plan.chord_symbols)}")
    print(f"Complexity: {plan.complexity:.2f}")
    print(f"Vulnerability: {plan.vulnerability:.2f}")

    # Render MIDI
    print("\n" + "-" * 40)
    print("Rendering MIDI...")

    output_path = render_plan_to_midi(plan)
    print(f"Exported to: {output_path}")
    print("\nDone. Drag into your DAW and make it yours.\n")


if __name__ == "__main__":
    run_cli()
