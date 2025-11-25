"""
DAiW Comprehensive Engine
=========================
Integrates the Therapist (Phase 0/1), Constraints (Phase 2), and
Direct MIDI Generation (Phase 3) into a single production pipeline.

Logic Flow:
1. TherapySession processes text -> AffectResult
2. TherapySession generates HarmonyPlan (with mode/tempo/chords)
3. render_plan_to_midi() converts Plan -> MIDI using music_brain.daw.logic

Philosophy: "Interrogate Before Generate" - The tool shouldn't finish art
for people; it should make them braver.
"""

import random
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any

# ==============================================================================
# 1. AFFECT ANALYZER (Scored & Ranked)
# ==============================================================================

@dataclass
class AffectResult:
    """Result of emotional content analysis."""
    primary: str
    secondary: Optional[str]
    scores: Dict[str, float]
    intensity: float  # 0.0 to 1.0


class AffectAnalyzer:
    """
    Analyzes text for emotional content using weighted keywords.
    Exposes raw scores for tie-breaking and nuance.
    """
    KEYWORDS = {
        "grief": {"loss", "gone", "miss", "dead", "died", "funeral", "mourning", "never again", "empty"},
        "rage": {"angry", "furious", "hate", "betrayed", "unfair", "revenge", "burn", "fight", "destroy"},
        "awe": {"wonder", "beautiful", "infinite", "god", "universe", "transcend", "light", "vast"},
        "nostalgia": {"remember", "used to", "childhood", "back when", "old days", "memory", "home"},
        "fear": {"scared", "terrified", "panic", "can't breathe", "trapped", "anxious", "dread"},
        "dissociation": {"numb", "nothing", "floating", "unreal", "detached", "fog", "grey", "wall"},
        "defiance": {"won't", "refuse", "stand", "strong", "break", "free", "my own", "no more"},
        "tenderness": {"soft", "gentle", "hold", "love", "kind", "care", "fragile", "warm"},
        "confusion": {"why", "lost", "don't know", "spinning", "chaos", "strange", "question"}
    }

    def analyze(self, text: str) -> AffectResult:
        """
        Analyze text for emotional content.

        Args:
            text: Raw user input describing their emotional state

        Returns:
            AffectResult with primary/secondary affects, scores, and intensity
        """
        if not text:
            return AffectResult("neutral", None, {}, 0.0)

        text = text.lower()
        scores = {k: 0.0 for k in self.KEYWORDS}

        for affect, words in self.KEYWORDS.items():
            for word in words:
                if word in text:
                    scores[affect] += 1.0

        # Sort affects by score descending
        sorted_affects = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        primary = sorted_affects[0][0] if sorted_affects[0][1] > 0 else "neutral"
        secondary = sorted_affects[1][0] if len(sorted_affects) > 1 and sorted_affects[1][1] > 0 else None

        # Calculate intensity (simple saturation at 3 keywords)
        intensity = min(1.0, sorted_affects[0][1] / 3.0) if sorted_affects[0][1] > 0 else 0.0

        return AffectResult(
            primary=primary,
            secondary=secondary,
            scores=scores,
            intensity=intensity
        )


# ==============================================================================
# 2. DATA MODELS (Source of Truth)
# ==============================================================================

@dataclass
class TherapyState:
    """
    Single Source of Truth for the session state.
    Replaces the deprecated CoreWoundModel with a unified schema.
    """
    # Narrative
    core_wound_name: str = ""
    narrative_entity_name: str = ""  # For externalization: "The Shadow", "Mr. Fog"

    # Quantifiable (from Motivational Interviewing techniques)
    motivation_scale: int = 5        # 1-10: "How much do you need this song to exist?"
    chaos_tolerance: float = 0.3     # 0.0 to 1.0: "How much control do you need?"

    # Inferred from analysis
    affect_result: Optional[AffectResult] = None
    suggested_mode: str = "ionian"


@dataclass
class HarmonyPlan:
    """
    Complete blueprint for generation.
    Can be passed to music_brain.structure.progression functions
    and rendered to MIDI via music_brain.daw.logic.
    """
    root_note: str         # "C", "F#"
    mode: str              # "minor", "dorian", "phrygian", etc.
    tempo_bpm: int
    time_signature: str    # "4/4", "6/8"
    length_bars: int       # Derived from motivation_scale
    chord_symbols: List[str]  # ["Cm7", "Fm9"]
    harmonic_rhythm: str      # "1_chord_per_bar", "syncopated"
    mood_profile: str         # "rage", "grief", etc.
    complexity: float         # 0.0 - 1.0, influences generation chaos


# ==============================================================================
# 3. OBLIQUE STRATEGIES (Tiered by Chaos Tolerance)
# ==============================================================================

STRATEGIES_MILD = [
    "Remove specifics and convert to ambiguities.",
    "Work at a different speed.",
    "Use fewer notes.",
    "Repetition is a form of change.",
    "What would your closest friend do?"
]

STRATEGIES_WILD = [
    "Honor thy error as a hidden intention.",
    "Use an unacceptable color.",
    "Make a sudden, destructive unpredictable action.",
    "Turn it upside down.",
    "Disconnect from desire.",
    "Abandon normal instruments."
]


def get_strategy(tolerance: float) -> str:
    """
    Select an Oblique Strategy based on chaos tolerance.

    Low tolerance gets safe affirmations.
    High tolerance gets Brian Eno's wilder cards.

    Args:
        tolerance: 0.0 (need control) to 1.0 (let it break)

    Returns:
        A strategy prompt string
    """
    if tolerance < 0.3:
        return "Trust in the you of now."  # Safety strategy
    elif tolerance < 0.7:
        return random.choice(STRATEGIES_MILD)
    else:
        # High tolerance accesses full deck, weighted towards Wild
        deck = STRATEGIES_MILD + (STRATEGIES_WILD * 2)
        return random.choice(deck)


# ==============================================================================
# 4. THERAPY SESSION (Pure Logic Layer - No I/O)
# ==============================================================================

class TherapySession:
    """
    Core logic for the therapy/interrogation workflow.

    This class handles state management and transformation logic.
    It contains NO print statements - decoupled from UI for reuse in
    CLI, GUI, or Web API contexts.
    """

    def __init__(self):
        self.state = TherapyState()
        self.analyzer = AffectAnalyzer()

        # Affect-to-Mode mapping (music theory meets psychology)
        self.AFFECT_TO_MODE = {
            "awe": "lydian",           # Bright, floaty
            "nostalgia": "dorian",     # Sentimental minor
            "rage": "phrygian",        # Aggressive minor (flamenco)
            "fear": "phrygian",        # Tension
            "dissociation": "locrian", # Unstable, diminished
            "grief": "aeolian",        # Sad natural minor
            "defiance": "mixolydian",  # Major with flat 7 (rock/rebellion)
            "tenderness": "ionian",    # Gentle major
            "confusion": "locrian",    # Disoriented
            "neutral": "ionian"
        }

    def process_core_input(self, text: str) -> str:
        """
        Step 1: Ingest the wound, analyze affect.

        Args:
            text: Raw user input describing what's hurting them

        Returns:
            String name of the detected primary affect
        """
        if not text.strip():
            # Edge case handling: Empty input returns neutral state.
            # "silence" is returned to caller to indicate lack of text,
            # but internal state is safely set to Neutral/Ionian.
            self.state.affect_result = AffectResult("neutral", None, {}, 0.0)
            self.state.suggested_mode = "ionian"
            return "silence"

        self.state.core_wound_name = text
        self.state.affect_result = self.analyzer.analyze(text)

        primary = self.state.affect_result.primary
        self.state.suggested_mode = self.AFFECT_TO_MODE.get(primary, "ionian")

        return primary

    def set_scales(self, motivation: int, chaos: float):
        """
        Step 2: Set numerical parameters from user input.

        Args:
            motivation: 1-10 scale ("How much do you need this song?")
            chaos: 0.0-1.0 ("How much control do you need?")
        """
        self.state.motivation_scale = max(1, min(10, motivation))
        self.state.chaos_tolerance = max(0.0, min(1.0, chaos))

    def generate_plan(self) -> HarmonyPlan:
        """
        Step 3: Factory that builds the HarmonyPlan based on State.

        Uses motivation_scale, chaos_tolerance, and affect_result to
        determine tempo, length, complexity, and chord selection.

        Returns:
            HarmonyPlan ready for MIDI rendering
        """
        # Safety Guard
        if self.state.affect_result is None:
            self.state.affect_result = AffectResult("neutral", None, {}, 0.0)

        # 1. Tempo Logic (Affect + Chaos)
        base_tempo = 100
        primary = self.state.affect_result.primary

        if primary in ["rage", "fear", "defiance"]:
            base_tempo = 130
        elif primary in ["grief", "dissociation"]:
            base_tempo = 70
        elif primary in ["awe"]:
            base_tempo = 90

        # Chaos modulates tempo (+/- 20bpm based on tolerance)
        final_tempo = base_tempo + int((self.state.chaos_tolerance * 40) - 20)

        # 2. Length Logic (Derived from Motivation)
        # Low motivation (1-3) -> 16 bars (Quick sketch)
        # Mid motivation (4-7) -> 32 bars (Standard idea)
        # High motivation (8-10) -> 64 bars (Full structure)
        if self.state.motivation_scale <= 3:
            length = 16
        elif self.state.motivation_scale <= 7:
            length = 32
        else:
            length = 64

        # 3. Complexity Nudge
        # If motivation is high, user can handle slightly more complex structures
        eff_complexity = self.state.chaos_tolerance
        if self.state.motivation_scale > 8:
            eff_complexity = min(1.0, eff_complexity + 0.1)

        # 4. Chord Selection Logic (Mode-based progressions)
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

        return HarmonyPlan(
            root_note=root,
            mode=mode,
            tempo_bpm=final_tempo,
            time_signature="4/4",
            length_bars=length,
            chord_symbols=chords,
            harmonic_rhythm="1_chord_per_bar",
            mood_profile=primary,
            complexity=eff_complexity
        )


# ==============================================================================
# 5. HARMONY -> MIDI BRIDGE (REAL INTEGRATION)
# ==============================================================================

def render_plan_to_midi(plan: HarmonyPlan, output_path: str) -> str:
    """
    Render a HarmonyPlan to a MIDI file using existing music_brain components:
    - music_brain.structure.progression.parse_progression_string
    - music_brain.structure.chord.CHORD_QUALITIES
    - music_brain.daw.logic.LogicProject

    The progression is looped to fill the entire length_bars specified
    in the plan.

    Args:
        plan: The HarmonyPlan containing all generation parameters
        output_path: Where to write the MIDI file

    Returns:
        Path to the generated MIDI file
    """
    try:
        from music_brain.structure.progression import parse_progression_string
        from music_brain.structure.chord import CHORD_QUALITIES
        from music_brain.daw.logic import LogicProject, LOGIC_CHANNELS
    except ImportError as exc:
        print(f"[SYSTEM]: MIDI bridge unavailable: {exc}")
        print(f"          Chords would have been: {plan.chord_symbols}")
        return output_path

    # 1. Build project
    ts_nums = plan.time_signature.split("/")
    if len(ts_nums) != 2:
        time_sig = (4, 4)
    else:
        try:
            time_sig = (int(ts_nums[0]), int(ts_nums[1]))
        except ValueError:
            time_sig = (4, 4)

    project = LogicProject(
        name="DAiW_Session",
        tempo_bpm=plan.tempo_bpm,
        time_signature=time_sig,
    )
    project.key = f"{plan.root_note} {plan.mode}"

    # 2. Parse chords using progression.py
    progression_str = "-".join(plan.chord_symbols)
    parsed_chords = parse_progression_string(progression_str)

    # 3. Build MIDI notes from ParsedChord + CHORD_QUALITIES
    ppq = getattr(project, "ppq", 480)
    beats_per_bar = time_sig[0]
    bar_ticks = int(beats_per_bar * ppq)

    # Loop the progression to fill the entire song length
    notes = []
    start_tick = 0
    current_bar = 0
    total_bars = plan.length_bars

    while current_bar < total_bars:
        for parsed in parsed_chords:
            if current_bar >= total_bars:
                break

            quality = parsed.quality
            intervals = CHORD_QUALITIES.get(quality)

            # Degrade gracefully if quality isn't in the map
            if intervals is None:
                base_quality = "min" if "m" in quality else "maj"
                intervals = CHORD_QUALITIES.get(base_quality, (0, 4, 7))

            root_midi = 48 + parsed.root_num  # C3 as base
            duration_ticks = bar_ticks

            # === FUTURE GROOVE LAYER HOOK ===
            # Here we would modify start_tick and duration_ticks based on
            # plan.complexity (chaos) to create the "Drunken Drummer" feel.
            # The Groove layer will intercept the mathematically perfect
            # values and apply jitter based on chaos_tolerance and
            # vulnerability_scale before writing to disk.
            # ================================

            for interval in intervals:
                notes.append(
                    {
                        "pitch": root_midi + interval,
                        "velocity": 80,  # Static for now; Groove Layer will randomize
                        "start_tick": start_tick,
                        "duration_ticks": duration_ticks,
                    }
                )

            start_tick += duration_ticks
            current_bar += 1

    # 4. Add track & export
    channel = LOGIC_CHANNELS.get("keys", 2)
    project.add_track(
        name="Harmony",
        channel=channel,
        instrument=None,
        notes=notes,
    )

    midi_path = project.export_midi(output_path)
    print(f"[SYSTEM]: MIDI written to {midi_path}")
    return midi_path


# ==============================================================================
# 6. CLI HANDLER (The "View" Layer)
# ==============================================================================

def run_cli():
    """
    Interactive command-line interface for the Therapy Engine.

    Follows the DAiW philosophy: "Interrogate Before Generate"

    Flow:
    1. Ask what's hurting
    2. Analyze and reflect back
    3. Get scaling parameters (motivation, chaos)
    4. Inject strategy if chaos is high
    5. Generate and export plan
    """
    session = TherapySession()
    print("--- DAiW THERAPY TERMINAL ---")

    # 1. Input Loop
    while True:
        text = input("[THERAPIST]: What is hurting you? >> ").strip()
        if text:
            break
        print("[THERAPIST]: Silence is an answer, but I need words to build structure.")

    # 2. Process
    affect = session.process_core_input(text)

    # 3. Reflect (Mirroring)
    if session.state.affect_result:
        print(f"\n[ANALYSIS]: Detected affect '{affect}' with intensity {session.state.affect_result.intensity:.2f}")
        if session.state.affect_result.secondary:
            print(f"[ANALYSIS]: Underlying undertone: '{session.state.affect_result.secondary}'")

    # 4. Scaling
    try:
        mot = int(input("\n[THERAPIST]: Motivation (1-10)? >> "))
        chaos_in = int(input("[THERAPIST]: Tolerance for Chaos (1-10)? >> "))
        session.set_scales(mot, chaos_in / 10.0)
    except ValueError:
        print("[SYSTEM]: Invalid input. Defaulting to safe values.")
        session.set_scales(5, 0.3)

    # 5. Strategy Injection
    if session.state.chaos_tolerance > 0.6:
        strat = get_strategy(session.state.chaos_tolerance)
        print(f"\n[OBLIQUE STRATEGY]: {strat}")

    # 6. Plan Generation
    plan = session.generate_plan()

    # 7. Summary
    print("\n" + "=" * 40)
    print("GENERATION DIRECTIVE")
    print("=" * 40)
    print(f"Target Mode: {plan.root_note} {plan.mode}")
    print(f"Tempo: {plan.tempo_bpm} BPM")
    print(f"Length: {plan.length_bars} bars")
    print(f"Progression: {' - '.join(plan.chord_symbols)}")
    print(f"Complexity: {plan.complexity:.2f}")

    # 8. MIDI Export
    output_path = "daiw_therapy_session.mid"
    render_plan_to_midi(plan, output_path)


if __name__ == "__main__":
    run_cli()
