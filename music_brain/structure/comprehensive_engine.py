# music_brain/structure/comprehensive_engine.py
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

from music_brain.daw.logic import LogicProject, LOGIC_CHANNELS
from music_brain.groove.engine import apply_groove
from music_brain.structure.tension import generate_tension_curve

try:
    from music_brain.structure.progression import parse_progression_string
except ImportError:
    # Fallback stub if progression parser isn't wired yet
    def parse_progression_string(_: str):
        return []


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
    complexity: float
    structure_type: str = "standard"


class AffectAnalyzer:
    KEYWORDS = {
        "grief": {"loss", "gone", "miss", "dead", "died", "funeral", "empty", "heavy"},
        "rage": {"angry", "furious", "hate", "betrayed", "burn", "fight", "destroy", "violent"},
        "awe": {"wonder", "beautiful", "infinite", "god", "universe", "light", "vast"},
        "nostalgia": {"remember", "used to", "childhood", "old days", "memory", "home"},
        "fear": {"scared", "terrified", "panic", "trapped", "anxious", "dread", "dark"},
        "dissociation": {"numb", "nothing", "floating", "unreal", "detached", "fog", "wall"},
        "defiance": {"won't", "refuse", "stand", "strong", "break", "free", "no more"},
        "confusion": {"why", "lost", "spinning", "chaos", "strange", "question"},
    }

    def analyze(self, text: str) -> AffectResult:
        if not text:
            return AffectResult("neutral", None, {}, 0.0)

        lowered = text.lower()
        scores = {k: 0.0 for k in self.KEYWORDS}

        for affect, words in self.KEYWORDS.items():
            for word in words:
                if word in lowered:
                    scores[affect] += 1.0

        sorted_affects = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_affect, top_score = sorted_affects[0]

        if top_score <= 0:
            primary = "neutral"
            secondary = None
            intensity = 0.0
        else:
            primary = top_affect
            secondary = sorted_affects[1][0] if len(sorted_affects) > 1 and sorted_affects[1][1] > 0 else None
            intensity = min(1.0, top_score / 3.0)

        return AffectResult(primary=primary, secondary=secondary, scores=scores, intensity=intensity)


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

    def __init__(self):
        self.state = TherapyState()
        self.analyzer = AffectAnalyzer()

    def process_core_input(self, text: str) -> str:
        """Ingest the wound, analyze affect."""
        if not text.strip():
            # Edge case: "silence" → neutral/ionian, but caller knows it's empty
            self.state.affect_result = AffectResult("neutral", None, {}, 0.0)
            self.state.suggested_mode = "ionian"
            self.state.core_wound_name = ""
            return "silence"

        self.state.core_wound_name = text
        result = self.analyzer.analyze(text)
        self.state.affect_result = result
        self.state.suggested_mode = self.AFFECT_TO_MODE.get(result.primary, "ionian")
        return result.primary

    def set_scales(self, motivation: int, chaos: float):
        self.state.motivation_scale = max(1, min(10, int(motivation)))
        self.state.chaos_tolerance = max(0.0, min(1.0, float(chaos)))

    def generate_plan(self) -> HarmonyPlan:
        """Builds HarmonyPlan based on current TherapyState."""

        if self.state.affect_result is None:
            self.state.affect_result = AffectResult("neutral", None, {}, 0.0)

        primary = self.state.affect_result.primary

        # 1. Tempo Logic
        base_tempo = 100
        if primary in ["rage", "fear", "defiance"]:
            base_tempo = 130
        elif primary in ["grief", "dissociation"]:
            base_tempo = 70
        elif primary == "awe":
            base_tempo = 90

        final_tempo = base_tempo + int((self.state.chaos_tolerance * 40.0) - 20.0)

        # 2. Length Logic (Motivation → bars)
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

        # 4. Chords by mode (placeholder mapping)
        mode = self.state.suggested_mode
        root = "C"

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

        # 5. Structure type mapping
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


def render_plan_to_midi(plan: HarmonyPlan, output_path: str, vulnerability: float = 0.0) -> str:
    """
    Plan -> chord parse -> raw notes (with bar-level tension) -> groove -> MIDI.
    """
    project = LogicProject(name="DAiW_Session", tempo_bpm=plan.tempo_bpm, time_signature=(4, 4))
    project.key = f"{plan.root_note} {plan.mode}"

    # Parse chords
    progression_str = "-".join(plan.chord_symbols)
    parsed_chords = parse_progression_string(progression_str)
    if not parsed_chords:
        print("[DAIW] Chord parser returned empty. Aborting render.")
        return output_path

    ppq = getattr(project, "ppq", 480)
    bar_ticks = 4 * ppq
    total_bars = plan.length_bars

    # Tension map
    structure_type = getattr(plan, "structure_type", "standard")
    tension_map = generate_tension_curve(total_bars, structure_type=structure_type)

    raw_notes: List[Dict[str, int]] = []
    current_bar = 0
    start_tick = 0
    base_complexity = plan.complexity

    while current_bar < total_bars:
        idx = min(current_bar, len(tension_map) - 1)
        tension_mult = float(tension_map[idx])

        bar_base_velocity = 90.0 * tension_mult
        bar_complexity = max(0.0, min(1.0, base_complexity * tension_mult))

        for parsed in parsed_chords:
            if current_bar >= total_bars:
                break

            quality = getattr(parsed, "quality", "maj")
            intervals = CHORD_QUALITIES.get(quality)

            if intervals is None:
                base_quality = "min" if "m" in quality else "maj"
                intervals = CHORD_QUALITIES.get(base_quality, (0, 4, 7))

            root_midi = 48 + getattr(parsed, "root_num", 0)
            duration_ticks = bar_ticks

            for interval in intervals:
                vel = int(random.gauss(bar_base_velocity, 5.0))
                vel = max(20, min(120, vel))
                raw_notes.append(
                    {
                        "pitch": root_midi + interval,
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
    project.add_track(name="Harmony", channel=channel, instrument=None, notes=humanized_notes)
    midi_path = project.export_midi(output_path)
    print(f"[DAIW] MIDI written to {midi_path}")
    return midi_path


def run_cli():
    session = TherapySession()
    print("\n--- DAiW: Core Engine ---")
    txt = input("What is hurting you? > ").strip()

    mood = session.process_core_input(txt)
    print(f"Detected mood: {mood} (mode: {session.state.suggested_mode})")

    try:
        mot = int(input("Motivation (1-10)? > "))
        chaos = int(input("Chaos (1-10)? > "))
    except ValueError:
        print("Bad numeric input. Exiting.")
        return

    session.set_scales(motivation=mot, chaos=chaos / 10.0)
    plan = session.generate_plan()
    print(
        f"Plan → {plan.length_bars} bars, {plan.tempo_bpm} BPM, "
        f"mode {plan.mode}, structure {plan.structure_type}"
    )

    out = "daiw_output.mid"
    render_plan_to_midi(plan, out, vulnerability=0.5)
    print(f"Done. MIDI: {out}")


if __name__ == "__main__":
    run_cli()
