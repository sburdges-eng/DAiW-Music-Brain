"""
DAiW Comprehensive Engine
=========================
Integrates the Therapist (Phase 0/1), Constraints (Phase 2), and
Direct MIDI Generation (Phase 3) into a single production pipeline.

Logic Flow:
1. TherapySession processes text -> AffectResult
2. TherapySession generates HarmonyPlan (with mode/tempo/chords)
3. render_plan_to_midi() converts Plan -> MIDI using music_brain.daw.logic

NoteEvent is the canonical event structure. Anything outside Python
(C++ plugin, OSC bridge) should speak in terms of NoteEvent fields.
"""

import random
from dataclasses import dataclass
from typing import List, Dict, Optional

import numpy as np

# ==============================================================================
# 1. AFFECT ANALYZER (Scored & Ranked)
# ==============================================================================


@dataclass
class AffectResult:
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
        "confusion": {"why", "lost", "don't know", "spinning", "chaos", "strange", "question"},
    }

    def analyze(self, text: str) -> AffectResult:
        if not text:
            return AffectResult("neutral", None, {}, 0.0)

        text = text.lower()
        scores: Dict[str, float] = {k: 0.0 for k in self.KEYWORDS}

        for affect, words in self.KEYWORDS.items():
            for word in words:
                if word in text:
                    scores[affect] += 1.0

        # Sort affects by score descending
        sorted_affects = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        primary = sorted_affects[0][0] if sorted_affects[0][1] > 0 else "neutral"
        secondary = (
            sorted_affects[1][0]
            if len(sorted_affects) > 1 and sorted_affects[1][1] > 0
            else None
        )

        # Calculate intensity (simple saturation at 3 keywords)
        intensity = min(1.0, sorted_affects[0][1] / 3.0) if sorted_affects[0][1] > 0 else 0.0

        return AffectResult(
            primary=primary,
            secondary=secondary,
            scores=scores,
            intensity=intensity,
        )


# ==============================================================================
# 2. DATA MODELS (Source of Truth)
# ==============================================================================


@dataclass
class TherapyState:
    """Single Source of Truth for the session state."""

    # Narrative
    core_wound_name: str = ""
    narrative_entity_name: str = ""

    # Quantifiable
    motivation_scale: int = 5        # 1-10
    chaos_tolerance: float = 0.3     # 0.0 to 1.0

    # Inferred
    affect_result: Optional[AffectResult] = None
    suggested_mode: str = "ionian"


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
    mood_profile: str
    complexity: float         # 0.0 - 1.0 (chaos/complexity dial)


@dataclass
class NoteEvent:
    """
    Canonical note representation.

    This is the API surface for anything that needs to talk to DAiW
    at the MIDI layer (e.g. future C++ plugin, OSC bridge).
    """

    pitch: int           # MIDI note number
    velocity: int        # 0-127
    start_tick: int      # position in ticks
    duration_ticks: int  # length in ticks

    def to_dict(self) -> Dict[str, int]:
        """Convert to the dict format used by LogicProject/add_track."""
        return {
            "pitch": self.pitch,
            "velocity": self.velocity,
            "start_tick": self.start_tick,
            "duration_ticks": self.duration_ticks,
        }


# ==============================================================================
# 3. TENSION CURVE (Song-Level Energy Shape)
# ==============================================================================

# Section type → velocity multiplier
SECTION_ENERGY = {
    "i": 0.6,   # intro
    "v": 0.75,  # verse
    "c": 1.1,   # chorus
    "b": 1.3,   # bridge (chaos peak)
    "o": 0.5,   # outro
}

# Default pattern: intro-verse-verse-chorus-chorus-bridge-outro
DEFAULT_PATTERN = "ivvccbo"


def build_tension_curve(length_bars: int, pattern: str = DEFAULT_PATTERN) -> List[float]:
    """
    Build a per-bar tension curve with numpy smoothing.

    Args:
        length_bars: Total bars in the song
        pattern: Section pattern string where each char maps to SECTION_ENERGY
                 e.g., "ivvccbo" = intro-verse-verse-chorus-chorus-bridge-outro

    Returns:
        List of per-bar tension multipliers (smoothed).
    """
    if length_bars <= 0:
        return [1.0]

    pattern = pattern.lower()
    pattern_len = len(pattern)

    # Assign section energy for each bar
    sections = []
    for i in range(length_bars):
        idx = int((i / length_bars) * pattern_len)
        idx = min(pattern_len - 1, idx)
        char = pattern[idx]
        sections.append(SECTION_ENERGY.get(char, 1.0))

    # Smooth with a 3-bar moving average so transitions aren't brick-step
    arr = np.array(sections, dtype=float)
    kernel = np.ones(3) / 3.0
    smoothed = np.convolve(arr, kernel, mode="same")

    return smoothed.tolist()


def tension_multiplier(progress: float, curve: Optional[List[float]] = None) -> float:
    """
    Map 0.0–1.0 song progress to an energy multiplier.

    Args:
        progress: Song position as 0.0-1.0
        curve: Optional pre-built tension curve. If None, uses default pattern.

    Returns:
        Energy multiplier for this position.
    """
    if curve is None:
        # Fallback to simple 6-segment curve
        fallback = [0.6, 0.75, 1.1, 1.1, 1.3, 0.5]
        if progress <= 0.0:
            return fallback[0]
        if progress >= 1.0:
            return fallback[-1]
        idx = int(progress * len(fallback))
        idx = max(0, min(len(fallback) - 1, idx))
        return fallback[idx]

    # Use provided curve
    if progress <= 0.0:
        return curve[0]
    if progress >= 1.0:
        return curve[-1]

    idx = int(progress * len(curve))
    idx = max(0, min(len(curve) - 1, idx))
    return curve[idx]


# ==============================================================================
# 4. OBLIQUE STRATEGIES (Tiered)
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
# 5. THERAPY SESSION (Pure Logic)
# ==============================================================================


class TherapySession:
    def __init__(self) -> None:
        self.state = TherapyState()
        self.analyzer = AffectAnalyzer()
        self.AFFECT_TO_MODE: Dict[str, str] = {
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

    def process_core_input(self, text: str) -> str:
        """Ingest the wound, analyze affect."""
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

    def set_scales(self, motivation: int, chaos: float) -> None:
        """Set numeric dials derived from user answers."""
        self.state.motivation_scale = max(1, min(10, motivation))
        self.state.chaos_tolerance = max(0.0, min(1.0, chaos))

    def generate_plan(self) -> HarmonyPlan:
        """Factory that builds the HarmonyPlan based on TherapyState."""

        # Safety Guard
        if self.state.affect_result is None:
            self.state.affect_result = AffectResult("neutral", None, {}, 0.0)

        primary = self.state.affect_result.primary

        # 1. Tempo Logic (Affect + Chaos)
        base_tempo = 100
        if primary in ["rage", "fear", "defiance"]:
            base_tempo = 130
        elif primary in ["grief", "dissociation"]:
            base_tempo = 70
        elif primary in ["awe"]:
            base_tempo = 90

        # Chaos modulates tempo (+/- 20bpm based on tolerance)
        final_tempo = base_tempo + int((self.state.chaos_tolerance * 40) - 20)

        # 2. Length Logic (Derived from Motivation)
        # Low motivation (1-3)  -> 16 bars (Quick sketch)
        # Mid motivation (4-7)  -> 32 bars (Standard idea)
        # High motivation (8-10) -> 64 bars (Full structure)
        if self.state.motivation_scale <= 3:
            length = 16
        elif self.state.motivation_scale <= 7:
            length = 32
        else:
            length = 64

        # 3. Complexity Nudge
        eff_complexity = self.state.chaos_tolerance
        if self.state.motivation_scale > 8:
            eff_complexity = min(1.0, eff_complexity + 0.1)

        # 4. Chord Selection Logic (Placeholder for full graph traversal)
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
            complexity=eff_complexity,
        )


# ==============================================================================
# 6. HARMONY -> MIDI BRIDGE (REAL INTEGRATION)
# ==============================================================================


def render_plan_to_midi(
    plan: HarmonyPlan,
    output_path: str,
    vulnerability: float = 0.5
) -> str:
    """
    Render a HarmonyPlan to a MIDI file using existing music_brain components:

    - music_brain.structure.progression.parse_progression_string
    - music_brain.structure.chord.CHORD_QUALITIES
    - music_brain.daw.logic.LogicProject, LOGIC_CHANNELS (if present)
    - music_brain.groove.engine.apply_groove (V2 humanization)

    Args:
        plan: HarmonyPlan with chord symbols, tempo, length, complexity
        output_path: Where to write the MIDI file
        vulnerability: 0.0-1.0 controls dynamic range (fragility)

    Returns: path to the written MIDI file (or the intended path if degraded).
    """

    try:
        from music_brain.structure.progression import parse_progression_string
        from music_brain.structure.chord import CHORD_QUALITIES
        from music_brain.daw.logic import LogicProject, LOGIC_CHANNELS
    except ImportError as exc:
        # Degrade gracefully: no MIDI engine available
        print(f"[SYSTEM]: MIDI bridge unavailable: {exc}")
        print(f"          Chords would have been: {plan.chord_symbols}")
        return output_path

    # Import V2 groove engine (optional - degrades gracefully)
    try:
        from music_brain.groove.engine import apply_groove
        groove_available = True
    except ImportError:
        groove_available = False

    # 1. Build LogicProject
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

    # 3. Build NoteEvents from ParsedChord + CHORD_QUALITIES (with Tension Curve)
    ppq = getattr(project, "ppq", 480)
    beats_per_bar = time_sig[0]
    bar_ticks = int(beats_per_bar * ppq)

    note_events: List[NoteEvent] = []

    # One chord per bar, LOOPED to fill song length
    start_tick = 0
    current_bar = 0
    total_bars = plan.length_bars

    # Build per-bar tension curve (numpy-smoothed)
    tension_curve = build_tension_curve(total_bars)

    while current_bar < total_bars:
        for parsed in parsed_chords:
            if current_bar >= total_bars:
                break

            quality = parsed.quality
            intervals = CHORD_QUALITIES.get(quality)

            # degrade gracefully if quality isn't in the map
            if intervals is None:
                base_quality = "min" if "m" in quality else "maj"
                intervals = CHORD_QUALITIES.get(base_quality, (0, 4, 7))

            root_midi = 48 + parsed.root_num  # C3 as base
            duration_ticks = bar_ticks

            # Get per-bar tension from pre-built curve
            t = tension_curve[current_bar] if current_bar < len(tension_curve) else 1.0
            base_vel = int(90 * t)
            base_vel = max(30, min(120, base_vel))  # Clamp to sane range

            for interval in intervals:
                note_events.append(
                    NoteEvent(
                        pitch=root_midi + interval,
                        velocity=base_vel,
                        start_tick=start_tick,
                        duration_ticks=duration_ticks,
                    )
                )

            start_tick += duration_ticks
            current_bar += 1

    # 4. Convert to dicts for groove processing
    notes_dicts = [ne.to_dict() for ne in note_events]

    # 5. Apply V2 groove humanization
    if groove_available:
        notes_dicts = apply_groove(
            notes_dicts,
            complexity=plan.complexity,
            vulnerability=vulnerability,
        )

    # 6. Add track & export
    try:
        channel = LOGIC_CHANNELS.get("keys", 2)
    except Exception:
        channel = 2

    project.add_track(
        name="Harmony",
        channel=channel,
        instrument=None,
        notes=notes_dicts,
    )

    midi_path = project.export_midi(output_path)
    print(f"[SYSTEM]: MIDI written to {midi_path}")
    return midi_path


# ==============================================================================
# 7. VAULT INTEGRATION (One-shot phrase → MIDI in AudioVault)
# ==============================================================================


def render_phrase_to_vault(
    phrase: str,
    session: Optional[TherapySession] = None,
    motivation: int = 7,
    chaos: float = 0.5,
    vulnerability: float = 0.5,
) -> str:
    """
    One-shot convenience function: phrase → analyzed → MIDI in AudioVault/output.

    Args:
        phrase: The emotional text to process ("I feel broken")
        session: Optional existing TherapySession (creates new if None)
        motivation: 1-10 scale (used if session is None or not configured)
        chaos: 0.0-1.0 chaos tolerance
        vulnerability: 0.0-1.0 controls dynamic range

    Returns:
        Path to the generated MIDI file in AudioVault/output.
    """
    import re
    from datetime import datetime

    # Try to import vault config (optional - falls back to local dir)
    try:
        from music_brain.audio_vault.config import OUTPUT_DIR
        output_dir = OUTPUT_DIR
    except ImportError:
        from pathlib import Path
        output_dir = Path(".")

    # Create or use session
    if session is None:
        session = TherapySession()
        session.set_scales(motivation, chaos)

    # Process the phrase
    affect = session.process_core_input(phrase)

    # Generate plan
    plan = session.generate_plan()

    # Build filename from phrase + timestamp
    # Clean the phrase for filename: lowercase, underscores, truncate
    clean_phrase = re.sub(r'[^a-z0-9]+', '_', phrase.lower())[:30].strip('_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"daiw_{clean_phrase}_{timestamp}.mid"

    output_path = str(output_dir / filename)

    # Render
    midi_path = render_plan_to_midi(plan, output_path, vulnerability=vulnerability)

    print(f"[VAULT]: Phrase '{phrase[:40]}...' → {affect} → {midi_path}")
    return midi_path


# ==============================================================================
# 7. LYRIC MIRROR (Cut-up / Markov fragments)
# ==============================================================================


def generate_lyric_mirror(
    phrase: str,
    mood: str,
    corpus_root: str = "./corpora",
    n: int = 8,
) -> List[str]:
    """
    Generate lyrical fragments from user phrase + mood-matched corpus.

    Maps mood to corpus subdirectory:
        grief, dissociation, nostalgia, tenderness → "emo"
        rage, defiance, fear → "industrial"
        others → "general"

    Args:
        phrase: The user's emotional text
        mood: Detected mood/affect (from session)
        corpus_root: Root directory containing corpus subdirs
        n: Number of fragments to generate

    Returns:
        List of lyric-like phrases
    """
    from pathlib import Path

    # Import lyrical mirror (optional - degrades gracefully)
    try:
        from music_brain.text.lyrical_mirror import generate_lyrical_fragments
    except ImportError:
        return []

    mood = (mood or "").lower()

    # Map mood to corpus subdirectory
    if mood in ["grief", "dissociation", "nostalgia", "tenderness"]:
        sub = "emo"
    elif mood in ["rage", "defiance", "fear"]:
        sub = "industrial"
    elif mood in ["awe", "wonder"]:
        sub = "ethereal"
    else:
        sub = "general"

    corpus_dir = Path(corpus_root) / sub

    # Gather corpus files if directory exists
    corpus_paths = []
    if corpus_dir.exists():
        corpus_paths = list(corpus_dir.glob("*.txt"))

    # Generate fragments
    fragments = generate_lyrical_fragments(
        session_text=phrase,
        genre_corpus_paths=corpus_paths,
        max_lines=n,
    )

    return fragments


# ==============================================================================
# 8. KIT SELECTION (Mood → Sample Kit)
# ==============================================================================


def select_kit_for_mood(mood: str) -> str:
    """
    Map detected mood to a suggested drum kit name.

    Args:
        mood: Detected affect (grief, rage, etc.)

    Returns:
        Kit name string (for use with audio_vault.kit_loader)
    """
    mood = (mood or "").lower()
    if mood in ["grief", "dissociation", "broken"]:
        return "LoFi_Bedroom_Kit"
    if mood in ["rage", "defiance", "fear"]:
        return "Industrial_Glitch_Kit"
    if mood in ["awe", "tenderness"]:
        return "Ambient_Kit"
    if mood in ["nostalgia"]:
        return "Vinyl_Kit"
    return "Standard_Kit"


# ==============================================================================
# 9. CLI HANDLER (The "View" Layer) - Optional
# ==============================================================================


def run_cli() -> None:
    """Simple terminal interface for debugging and quick use."""
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
        print(
            f"\n[ANALYSIS]: Detected affect '{affect}' "
            f"with intensity {session.state.affect_result.intensity:.2f}"
        )
        if session.state.affect_result.secondary:
            print(
                f"[ANALYSIS]: Underlying undertone: "
                f"'{session.state.affect_result.secondary}'"
            )

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

    # 8. MIDI Export
    output_path = "daiw_therapy_session.mid"
    render_plan_to_midi(plan, output_path)


if __name__ == "__main__":
    run_cli()
