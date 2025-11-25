"""
DAiW Comprehensive Engine
=========================
TherapySession → HarmonyPlan → MIDI via LogicProject + Groove Engine.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

# Imports from your repo
try:
    from music_brain.structure.progression import parse_progression_string
    from music_brain.daw.logic import LogicProject, LOGIC_CHANNELS
    try:
        from music_brain.structure.chord import CHORD_QUALITIES
    except ImportError:
        CHORD_QUALITIES = {
            "maj": (0, 4, 7),
            "min": (0, 3, 7),
            "dim": (0, 3, 6),
            "aug": (0, 4, 8),
            "maj7": (0, 4, 7, 11),
            "min7": (0, 3, 7, 10),
            "7": (0, 4, 7, 10),
        }
    from music_brain.groove.engine import apply_groove
    from music_brain.structure.tension import generate_tension_curve
except ImportError as e:
    print(f"⚠️  DAiW engine running in degraded mode: {e}")
    parse_progression_string = lambda s: []  # type: ignore
    apply_groove = lambda n, c, v: n  # type: ignore
    LogicProject = None  # type: ignore
    LOGIC_CHANNELS = {"keys": 0}
    CHORD_QUALITIES = {}
    generate_tension_curve = lambda total_bars, structure_type="standard": [1.0] * max(
        1, total_bars
    )  # type: ignore


# ==============================================================================
# DATA MODELS
# ==============================================================================


@dataclass
class AffectResult:
    primary: str
    secondary: Optional[str]
    scores: Dict[str, float]
    intensity: float


@dataclass
class TherapyState:
    core_wound_name: str = ""
    motivation_scale: int = 5
    chaos_tolerance: float = 0.3
    affect_result: Optional[AffectResult] = None
    suggested_mode: str = "ionian"


@dataclass(frozen=True)
class NoteEvent:
    pitch: int
    velocity: int
    start_tick: int
    duration_ticks: int
    channel: int = 0


@dataclass
class HarmonyPlan:
    root_note: str
    mode: str
    tempo_bpm: int
    time_signature: str
    length_bars: int
    chord_symbols: List[str]
    harmonic_rhythm: str
    mood_profile: str
    complexity: float  # base chaos
    structure_type: str = "standard"


# ==============================================================================
# AFFECT ANALYZER
# ==============================================================================


class AffectAnalyzer:
    KEYWORDS = {
        "grief": {"loss", "gone", "miss", "dead", "died", "funeral", "empty", "heavy"},
        "rage": {
            "angry",
            "furious",
            "hate",
            "betrayed",
            "burn",
            "fight",
            "destroy",
            "violent",
        },
        "awe": {"wonder", "beautiful", "infinite", "god", "universe", "light", "vast"},
        "nostalgia": {"remember", "used to", "childhood", "old days", "memory", "home"},
        "fear": {"scared", "terrified", "panic", "trapped", "anxious", "dread", "dark"},
        "dissociation": {
            "numb",
            "nothing",
            "floating",
            "unreal",
            "detached",
            "fog",
            "wall",
        },
        "defiance": {"won't", "refuse", "stand", "strong", "break", "free", "no more"},
        "confusion": {"why", "lost", "spinning", "chaos", "strange", "question"},
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
    AFFECT_TO_MODE = {
        "awe": "lydian",
        "nostalgia": "dorian",
        "rage": "phrygian",
        "fear": "phrygian",
        "dissociation": "locrian",
        "grief": "aeolian",
        "defiance": "mixolydian",
        "confusion": "locrian",
        "neutral": "ionian",
    }

    def __init__(self) -> None:
        self.state = TherapyState()
        self.analyzer = AffectAnalyzer()

    def process_core_input(self, text: str) -> str:
        """
        Ingests the wound text and sets affect/mode.
        """
        if not text.strip():
            # Edge case: empty input → neutral state
            # "silence" returned so caller knows nothing was said,
            # internal state is safely neutral/ionian.
            self.state.core_wound_name = ""
            self.state.affect_result = AffectResult("neutral", None, {}, 0.0)
            self.state.suggested_mode = "ionian"
            return "silence"

        self.state.core_wound_name = text
        self.state.affect_result = self.analyzer.analyze(text)
        primary = self.state.affect_result.primary
        self.state.suggested_mode = self.AFFECT_TO_MODE.get(primary, "ionian")
        return primary

    def set_scales(self, motivation: int, chaos: float) -> None:
        self.state.motivation_scale = max(1, min(10, int(motivation)))
        self.state.chaos_tolerance = max(0.0, min(1.0, float(chaos)))

    def generate_plan(self) -> HarmonyPlan:
        """
        Factory that builds the HarmonyPlan based on current state.
        Uses affect for tempo/mode, motivation for length, chaos for complexity.
        """
        # Safety guard
        if self.state.affect_result is None:
            self.state.affect_result = AffectResult("neutral", None, {}, 0.0)

        primary = self.state.affect_result.primary

        # 1. Tempo Logic
        base_tempo = 100
        if primary in ["rage", "fear", "defiance"]:
            base_tempo = 130
        elif primary in ["grief", "dissociation"]:
            base_tempo = 70
        elif primary in ["awe"]:
            base_tempo = 90

        final_tempo = base_tempo + int((self.state.chaos_tolerance * 40) - 20)

        # 2. Length from Motivation
        if self.state.motivation_scale <= 3:
            length = 16
        elif self.state.motivation_scale <= 7:
            length = 32
        else:
            length = 64

        # 3. Complexity nudge with high motivation
        eff_complexity = self.state.chaos_tolerance
        if self.state.motivation_scale > 8:
            eff_complexity = min(1.0, eff_complexity + 0.1)

        # 4. Chord Selection (simple mode mapping)
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
        else:
            chords = ["C", "Am", "F", "G"]

        # 5. Structure type from mood
        if primary in ["grief", "dissociation"]:
            structure_type = "climb"
        elif primary in ["rage", "defiance"]:
            structure_type = "standard"
        else:
            structure_type = "constant"

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
        )


# ==============================================================================
# KIT SELECTION
# ==============================================================================


def select_kit_for_mood(mood: str) -> str:
    """
    Maps emotional intent to AudioVault kits.
    """
    mood_l = (mood or "").lower()
    if mood_l in {"grief", "dissociation", "broken"}:
        return "LoFi_Bedroom_Kit"
    if mood_l in {"rage", "defiance"}:
        return "Industrial_Glitch_Kit"
    return "Standard_Kit"


# ==============================================================================
# RENDERER
# ==============================================================================


def render_plan_to_midi(
    plan: HarmonyPlan,
    output_path: str,
    vulnerability: float = 0.0,
) -> str:
    """
    Plan → Parsed chords → bar-shaped notes → Groove Engine → MIDI file.
    """
    if LogicProject is None:
        print("❌ LogicProject not available. Cannot export MIDI.")
        return output_path

    project = LogicProject(
        name="DAiW_Session",
        tempo_bpm=plan.tempo_bpm,
        time_signature=(4, 4),
    )
    project.key = f"{plan.root_note} {plan.mode}"

    progression_str = "-".join(plan.chord_symbols)
    parsed_chords = parse_progression_string(progression_str)
    if not parsed_chords:
        print("❌ Chord parser returned empty; aborting render.")
        return output_path

    ppq = getattr(project, "ppq", 480)
    bar_ticks = 4 * ppq
    total_bars = plan.length_bars

    # Tension curve selection
    structure_type = getattr(plan, "structure_type", "standard")
    tension_map = list(
        generate_tension_curve(total_bars, structure_type=structure_type)
    )

    raw_notes: List[Dict[str, int]] = []
    current_bar = 0
    start_tick = 0
    base_complexity = plan.complexity

    while current_bar < total_bars:
        idx = min(current_bar, len(tension_map) - 1)
        tension_mult = float(tension_map[idx])

        bar_base_velocity = 90.0 * tension_mult
        # If you want tension to modulate chaos too, you can:
        # bar_complexity = max(0.0, min(1.0, base_complexity * tension_mult))

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

            for interval in intervals:
                vel = int(random.gauss(bar_base_velocity, 5.0))
                vel = max(20, min(120, vel))

                raw_notes.append(
                    {
                        "pitch": root_midi + int(interval),
                        "velocity": vel,
                        "start_tick": start_tick,
                        "duration_ticks": duration_ticks,
                    }
                )

            start_tick += duration_ticks
            current_bar += 1

    humanized_notes = apply_groove(
        raw_notes,
        complexity=base_complexity,
        vulnerability=vulnerability,
    )

    channel = LOGIC_CHANNELS.get("keys", 0)
    project.add_track(
        name="Harmony",
        channel=channel,
        instrument=None,
        notes=humanized_notes,
    )

    midi_path = project.export_midi(output_path)
    print(f"[DAiW]: MIDI written to {midi_path}")
    return midi_path


# ==============================================================================
# CLI
# ==============================================================================


def run_cli() -> None:
    """
    Minimal interactive CLI for quick testing.
    """
    session = TherapySession()
    print("\n--- DAiW: Interrogate Before Generate ---")

    txt = input("What is hurting you? > ").strip()
    mood = session.process_core_input(txt)
    if mood == "silence":
        print("You gave me nothing. Neutral blueprint.")
    else:
        print(f"Detected mood: {mood} (Mode: {session.state.suggested_mode})")

    try:
        mot = int(input("Motivation (1-10)? > ").strip() or "5")
        chaos = int(input("Chaos (1-10)? > ").strip() or "5")
    except ValueError:
        mot, chaos = 5, 5

    session.set_scales(motivation=mot, chaos=chaos / 10.0)
    plan = session.generate_plan()
    print(
        f"Plan: {plan.length_bars} bars @ {plan.tempo_bpm} BPM "
        f"in {plan.mode} ({plan.mood_profile})"
    )

    out = "daiw_output.mid"
    render_plan_to_midi(plan, out, vulnerability=0.5)
    print(f"✅ Exported: {out}")


if __name__ == "__main__":
    run_cli()
