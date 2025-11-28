"""
DAiW Comprehensive Engine
=========================
TherapySession -> HarmonyPlan -> bar-shaped NoteEvents -> Groove Engine -> MIDI.

This is the main "brain" that the UI and CLI talk to.

Logic Flow:
1. TherapySession processes text -> AffectResult
2. TherapySession generates HarmonyPlan (with mode/tempo/chords)
3. render_plan_to_midi() converts Plan -> MIDI using music_brain.daw.logic

NoteEvent is the canonical event structure. Anything outside Python
(C++ plugin, OSC bridge) should speak in terms of NoteEvent fields.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

from music_brain.structure.progression import parse_progression_string
from music_brain.structure.chord import CHORD_QUALITIES
from music_brain.daw.logic import LogicProject, LOGIC_CHANNELS
from music_brain.groove.engine import apply_groove
from music_brain.structure.tension import (
    generate_tension_curve,
    choose_structure_type_for_mood,
)


# ==============================================================================
# DATA MODELS
# ==============================================================================


@dataclass
class AffectResult:
    """Result of emotional text analysis."""
    primary: str
    secondary: Optional[str]
    scores: Dict[str, float]
    intensity: float  # 0.0 to 1.0


@dataclass
class TherapyState:
    """Single Source of Truth for the session state."""
    core_wound_name: str = ""
    motivation_scale: int = 5       # 1-10
    chaos_tolerance: float = 0.3    # 0.0 to 1.0
    affect_result: Optional[AffectResult] = None
    suggested_mode: str = "ionian"


@dataclass(frozen=True)
class NoteEvent:
    """
    Canonical note representation.

    This is the API surface for anything that needs to talk to DAiW
    at the MIDI layer (e.g. future C++ plugin, OSC bridge).

    The frozen=True makes NoteEvent hashable for deduplication.
    """
    pitch: int           # MIDI note number
    velocity: int        # 0-127
    start_tick: int      # position in ticks
    duration_ticks: int  # length in ticks
    channel: int = 0     # MIDI channel
    bar_index: int = 0   # which bar this note belongs to
    complexity: float = 0.0  # bar-level complexity for groove processing
    accent: bool = False     # whether this is an accented note


@dataclass
class HarmonyPlan:
    """
    Complete blueprint for generation.
    This is what a "brain" outputs and a renderer consumes.
    """
    root_note: str           # "C", "F#"
    mode: str                # "ionian", "aeolian", "phrygian", etc.
    tempo_bpm: int
    time_signature: str      # "4/4"
    length_bars: int
    chord_symbols: List[str]  # ["Cm7", "Fm9"]
    harmonic_rhythm: str      # "1_chord_per_bar"
    mood_profile: str         # Primary affect driving this plan
    complexity: float         # 0.0 - 1.0 (chaos/complexity dial)
    structure_type: str = "standard"  # Tension curve shape
    tension_curve: List[float] = field(default_factory=list)  # Bar-by-bar tension


# ==============================================================================
# OBLIQUE STRATEGIES (Tiered)
# ==============================================================================

STRATEGIES_MILD = [
    "Remove specifics and convert to ambiguities.",
    "Work at a different speed.",
    "Use fewer notes.",
    "Repetition is a form of change.",
    "What would your closest friend do?",
]

STRATEGIES_WILD = [
    "Honor thy error as a hidden intention.",
    "Use an unacceptable color.",
    "Make a sudden, destructive unpredictable action.",
    "Turn it upside down.",
    "Disconnect from desire.",
    "Abandon normal instruments.",
]


def get_strategy(tolerance: float) -> str:
    """Selects a strategy based on chaos tolerance."""
    if tolerance < 0.3:
        return "Trust in the you of now."  # Safety strategy
    elif tolerance < 0.7:
        return random.choice(STRATEGIES_MILD)
    else:
        deck = STRATEGIES_MILD + (STRATEGIES_WILD * 2)
        return random.choice(deck)


# ==============================================================================
# AFFECT ANALYZER
# ==============================================================================


class AffectAnalyzer:
    """
    Analyzes text for emotional content using weighted keywords.
    Exposes raw scores for tie-breaking and nuance.
    """

    KEYWORDS = {
        "grief": {
            "loss", "gone", "miss", "dead", "died", "funeral",
            "empty", "heavy", "sleeping", "found", "mourning", "never again"
        },
        "rage": {
            "angry", "furious", "hate", "betrayed", "burn",
            "fight", "destroy", "violent", "revenge", "unfair",
        },
        "awe": {
            "wonder", "beautiful", "infinite", "god", "universe",
            "light", "vast", "divine", "transcend"
        },
        "nostalgia": {
            "remember", "used to", "childhood", "old days", "memory", "home",
            "back when"
        },
        "fear": {
            "scared", "terrified", "panic", "trapped", "anxious",
            "dread", "dark", "can't breathe"
        },
        "dissociation": {
            "numb", "nothing", "floating", "unreal", "detached",
            "fog", "wall", "grey"
        },
        "defiance": {
            "won't", "refuse", "stand", "strong", "break", "free", "no more",
            "my own"
        },
        "tenderness": {
            "soft", "gentle", "hold", "love", "kind", "care", "fragile", "warm"
        },
        "confusion": {
            "why", "lost", "spinning", "chaos", "strange", "question",
            "don't know"
        },
    }

    def analyze(self, text: str) -> AffectResult:
        if not text:
            return AffectResult("neutral", None, {}, 0.0)

        text_l = text.lower()
        scores = {k: 0.0 for k in self.KEYWORDS}

        for affect, words in self.KEYWORDS.items():
            for word in words:
                if word in text_l:
                    scores[affect] += 1.0

        sorted_affects = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if not sorted_affects or sorted_affects[0][1] == 0:
            return AffectResult("neutral", None, scores, 0.0)

        primary, p_score = sorted_affects[0]
        secondary = (
            sorted_affects[1][0]
            if len(sorted_affects) > 1 and sorted_affects[1][1] > 0
            else None
        )
        intensity = min(1.0, p_score / 3.0)

        return AffectResult(primary, secondary, scores, intensity)


# ==============================================================================
# THERAPY SESSION
# ==============================================================================


class TherapySession:
    """
    The emotional processing engine.
    Converts raw wound text into musical parameters.
    """

    AFFECT_TO_MODE = {
        "awe": "lydian",
        "nostalgia": "dorian",
        "rage": "phrygian",
        "fear": "phrygian",
        "dissociation": "locrian",
        "grief": "aeolian",
        "defiance": "mixolydian",
        "tenderness": "ionian",
        "confusion": "locrian",
        "neutral": "ionian",
    }

    def __init__(self) -> None:
        self.state = TherapyState()
        self.analyzer = AffectAnalyzer()

    def process_core_input(self, text: str) -> str:
        """
        Ingests the wound text and sets affect/mode.
        Returns the primary affect detected.
        """
        if not text.strip():
            self.state.core_wound_name = ""
            self.state.affect_result = AffectResult("neutral", None, {}, 0.0)
            self.state.suggested_mode = "ionian"
            return "neutral"

        self.state.core_wound_name = text
        self.state.affect_result = self.analyzer.analyze(text)
        primary = self.state.affect_result.primary
        self.state.suggested_mode = self.AFFECT_TO_MODE.get(primary, "ionian")
        return primary

    def set_scales(
        self,
        motivation: int,
        chaos: Optional[float] = None,
        *,
        chaos_tolerance: Optional[float] = None,
    ) -> None:
        """
        Set numeric dials derived from user answers.

        Args:
            motivation: 1-10 scale for motivation
            chaos: 0.0-1.0 scale for chaos tolerance (positional)
            chaos_tolerance: 0.0-1.0 scale for chaos tolerance (keyword, for backward compat)
        """
        self.state.motivation_scale = max(1, min(10, int(motivation)))
        # Accept either positional 'chaos' or keyword 'chaos_tolerance'
        effective_chaos = chaos if chaos is not None else chaos_tolerance
        if effective_chaos is not None:
            self.state.chaos_tolerance = max(0.0, min(1.0, float(effective_chaos)))

    def generate_plan(self) -> HarmonyPlan:
        """
        Factory that builds the HarmonyPlan based on current state.
        """
        if self.state.affect_result is None:
            self.state.affect_result = AffectResult("neutral", None, {}, 0.0)

        primary = self.state.affect_result.primary

        # Tempo Logic (Affect + Chaos)
        base_tempo = 100
        if primary in ["rage", "fear", "defiance"]:
            base_tempo = 130
        elif primary in ["grief", "dissociation"]:
            base_tempo = 70
        elif primary in ["awe", "tenderness"]:
            base_tempo = 90

        # Chaos modulates tempo (+/- 20bpm based on tolerance)
        final_tempo = base_tempo + int((self.state.chaos_tolerance * 40) - 20)

        # Length from motivation
        if self.state.motivation_scale <= 3:
            length = 16
        elif self.state.motivation_scale <= 7:
            length = 32
        else:
            length = 64

        # Complexity nudge
        eff_complexity = self.state.chaos_tolerance
        if self.state.motivation_scale > 8:
            eff_complexity = min(1.0, eff_complexity + 0.1)

        # Chord selection based on mode
        root = "C"
        mode = self.state.suggested_mode

        if mode == "locrian":
            chords = ["Cdim", "DbMaj7", "Ebm", "Cdim"]
        elif mode == "phrygian":
            chords = ["Cm", "Db", "Bbm", "Cm"]
        elif mode == "lydian":
            chords = ["C", "D", "Bm", "C"]
        elif mode == "mixolydian":
            chords = ["C", "Bb", "F", "C"]
        elif mode == "aeolian":
            chords = ["Cm", "Ab", "Fm", "Cm"]
        elif mode == "dorian":
            chords = ["Cm", "F", "Gm", "Cm"]
        else:  # Ionian/Neutral
            chords = ["C", "Am", "F", "G"]

        # Select structure type based on mood
        structure_type = choose_structure_type_for_mood(primary)
        tension_curve = list(generate_tension_curve(length, structure_type))

        return HarmonyPlan(
            root_note=root,
            mode=mode,
            tempo_bpm=final_tempo,
            time_signature="4/4",
            length_bars=length,
            chord_symbols=chords,
            harmonic_rhythm="1_chord_per_bar",
            mood_profile=primary,
            complexity=eff_complexity,
            structure_type=structure_type,
            tension_curve=tension_curve,
        )


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================


def select_kit_for_mood(mood: str) -> str:
    """
    Select an appropriate drum kit based on emotional mood.

    Args:
        mood: Primary emotional state

    Returns:
        Kit name string for use with sample libraries
    """
    mood_l = (mood or "").lower()
    if mood_l in {"grief", "dissociation", "broken"}:
        return "LoFi_Bedroom_Kit"
    if mood_l in {"rage", "defiance", "fear"}:
        return "Industrial_Glitch_Kit"
    if mood_l in {"awe", "nostalgia"}:
        return "Ambient_Shimmer_Kit"
    return "Standard_Kit"


def _note_event_to_dict(ev: NoteEvent) -> Dict:
    """Convert a NoteEvent to dict format for groove engine."""
    return asdict(ev)


# ==============================================================================
# HARMONY -> MIDI BRIDGE
# ==============================================================================


def render_plan_to_midi(
    plan: HarmonyPlan,
    output_path: str,
    vulnerability: float = 0.0,
    seed: Optional[int] = None,
) -> str:
    """
    Plan -> Parsed chords -> bar-shaped NoteEvents -> Groove Engine -> MIDI file.

    Args:
        plan: HarmonyPlan containing all musical parameters
        output_path: Where to write the MIDI file
        vulnerability: Emotional vulnerability scale (0.0-1.0) for humanization
        seed: Random seed for reproducibility

    Returns:
        Path to the written MIDI file
    """
    project = LogicProject(
        name="DAiW_Session",
        tempo_bpm=plan.tempo_bpm,
        time_signature=(4, 4),
    )
    project.key = f"{plan.root_note} {plan.mode}"

    progression_str = "-".join(plan.chord_symbols)
    parsed_chords = parse_progression_string(progression_str)
    if not parsed_chords:
        print("[DAiW]: Chord parser returned empty; aborting render.")
        return output_path

    ppq = getattr(project, "ppq", 480)
    bar_ticks = 4 * ppq
    total_bars = plan.length_bars

    # Use plan.tension_curve if present, else regenerate
    if plan.tension_curve and len(plan.tension_curve) >= total_bars:
        tension_curve = plan.tension_curve[:total_bars]
    else:
        tension_curve = list(
            generate_tension_curve(total_bars, structure_type=plan.structure_type)
        )

    # Build NoteEvents
    note_events: List[NoteEvent] = []
    current_bar = 0
    start_tick = 0
    base_complexity = plan.complexity

    while current_bar < total_bars:
        idx = min(current_bar, len(tension_curve) - 1)
        tension_mult = float(tension_curve[idx])

        # Bar-level velocity anchor
        bar_base_velocity = 90.0 * tension_mult
        # Bar-level complexity scaled by tension
        bar_complexity = max(0.0, min(1.0, base_complexity * tension_mult))

        for chord in parsed_chords:
            if current_bar >= total_bars:
                break

            quality = getattr(chord, "quality", "maj")
            intervals = CHORD_QUALITIES.get(quality)
            if intervals is None:
                base_q = "min" if "m" in quality else "maj"
                intervals = CHORD_QUALITIES.get(base_q, (0, 4, 7))

            root_midi = 48 + int(getattr(chord, "root_num", 0))
            duration_ticks = bar_ticks

            # Accent on downbeats of each chord's first bar
            accent = True

            for interval in intervals:
                vel = int(random.gauss(bar_base_velocity, 5.0))
                vel = max(20, min(120, vel))

                note_events.append(
                    NoteEvent(
                        pitch=root_midi + int(interval),
                        velocity=vel,
                        start_tick=start_tick,
                        duration_ticks=duration_ticks,
                        channel=LOGIC_CHANNELS.get("keys", 0),
                        bar_index=current_bar,
                        complexity=bar_complexity,
                        accent=accent,
                    )
                )

                accent = False  # only first tone accented

            start_tick += duration_ticks
            current_bar += 1

    # Convert to dict and send through groove engine
    raw_notes_dicts = [_note_event_to_dict(ev) for ev in note_events]

    humanized_notes = apply_groove(
        raw_notes_dicts,
        complexity=base_complexity,
        vulnerability=vulnerability,
        seed=seed,
    )

    project.add_track(
        name="Harmony",
        channel=LOGIC_CHANNELS.get("keys", 0),
        instrument=None,
        notes=humanized_notes,
    )

    midi_path = project.export_midi(output_path)
    print(f"[DAiW]: MIDI written to {midi_path}")
    return midi_path


# ==============================================================================
# CLI HANDLER
# ==============================================================================


def run_cli() -> None:
    """
    Minimal interactive CLI for quick testing.
    """
    session = TherapySession()
    print("\n--- DAiW: Interrogate Before Generate ---")
    print("This tool makes you braver, not finished.\n")

    # 1. Core wound input
    while True:
        text = input("[THERAPIST]: What is hurting you? >> ").strip()
        if text:
            break
        print("[THERAPIST]: Silence is an answer, but I need words to build structure.")

    # 2. Process affect
    affect = session.process_core_input(text)

    # 3. Reflect (Mirroring)
    if session.state.affect_result:
        print(
            f"\n[ANALYSIS]: Detected affect '{affect}' "
            f"with intensity {session.state.affect_result.intensity:.2f}"
        )
        if session.state.affect_result.secondary:
            print(
                f"[ANALYSIS]: Underlying undertone: "
                f"'{session.state.affect_result.secondary}'"
            )
        print(f"[ANALYSIS]: Suggested mode: {session.state.suggested_mode}")

    # 4. Scaling questions
    try:
        mot = int(input("\n[THERAPIST]: Motivation (1-10)? >> "))
        chaos_in = int(input("[THERAPIST]: Tolerance for Chaos (1-10)? >> "))
        session.set_scales(mot, chaos_in / 10.0)
    except ValueError:
        print("[SYSTEM]: Invalid input. Defaulting to safe values.")
        session.set_scales(5, 0.3)

    # 5. Vulnerability (for humanization)
    try:
        vuln_in = int(input("[THERAPIST]: Vulnerability level (1-10)? >> "))
        vulnerability = max(0.0, min(1.0, vuln_in / 10.0))
    except ValueError:
        print("[SYSTEM]: Invalid input. Defaulting to medium vulnerability.")
        vulnerability = 0.5

    # 6. Strategy injection (if chaos is high)
    if session.state.chaos_tolerance > 0.6:
        strat = get_strategy(session.state.chaos_tolerance)
        print(f"\n[OBLIQUE STRATEGY]: {strat}")

    # 7. Plan generation
    plan = session.generate_plan()

    # 8. Summary
    print("\n" + "=" * 50)
    print("GENERATION DIRECTIVE")
    print("=" * 50)
    print(f"Target Mode: {plan.root_note} {plan.mode}")
    print(f"Tempo: {plan.tempo_bpm} BPM")
    print(f"Length: {plan.length_bars} bars")
    print(f"Progression: {' - '.join(plan.chord_symbols)}")
    print(f"Structure: {plan.structure_type}")
    print(f"Complexity: {plan.complexity:.2f}")
    print(f"Vulnerability: {vulnerability:.2f}")

    # Show selected kit
    kit = select_kit_for_mood(plan.mood_profile)
    print(f"Suggested Kit: {kit}")

    # Show tension curve summary
    if plan.tension_curve:
        avg_tension = sum(plan.tension_curve) / len(plan.tension_curve)
        max_tension = max(plan.tension_curve)
        min_tension = min(plan.tension_curve)
        print(f"Tension Range: {min_tension:.2f} - {max_tension:.2f} (avg: {avg_tension:.2f})")

    # 9. MIDI Export
    output_path = "daiw_therapy_session.mid"
    render_plan_to_midi(plan, output_path, vulnerability=vulnerability)

    print("\n[THERAPIST]: Your structure awaits. Make it mean something.")


if __name__ == "__main__":
    run_cli()
