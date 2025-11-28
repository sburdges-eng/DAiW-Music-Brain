"""
Intent Processor - Executes song intent to generate musical elements.

This module takes a CompleteSongIntent and generates:
- Chord progressions with intentional rule-breaking
- Rhythmic patterns with groove modifications
- Arrangement suggestions
- Production guidelines

The core philosophy: Rules are broken INTENTIONALLY based on 
emotional justification from the intent schema.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import random

from music_brain.session.intent_schema import (
    CompleteSongIntent,
    HarmonyRuleBreak,
    RhythmRuleBreak,
    ArrangementRuleBreak,
    ProductionRuleBreak,
    RULE_BREAKING_EFFECTS,
)


# =================================================================
# CHORD/KEY MAPPINGS
# =================================================================

# Notes in chromatic order
CHROMATIC = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
CHROMATIC_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

# Diatonic chords in major key (roman numerals)
MAJOR_DIATONIC = {
    'I': 'maj', 'ii': 'min', 'iii': 'min', 'IV': 'maj', 
    'V': 'maj', 'vi': 'min', 'vii°': 'dim'
}

# Borrowed chords from parallel minor
BORROWED_FROM_MINOR = {
    'iv': 'min',      # Sad IV
    'bVI': 'maj',     # Epic chord  
    'bVII': 'maj',    # Rock swagger
    'bIII': 'maj',    # Brightness from minor
    'ii°': 'dim',     # Tension
}

# Modal interchange options
MODAL_INTERCHANGE = {
    'lydian': {'#IV': 'maj'},      # Raised 4th, dreamy
    'mixolydian': {'bVII': 'maj'}, # Flat 7, rock
    'dorian': {'IV': 'maj'},       # Major IV in minor context
    'phrygian': {'bII': 'maj'},    # Flat 2, Spanish/tension
}


@dataclass
class GeneratedProgression:
    """A generated chord progression with metadata."""
    chords: List[str]
    key: str
    mode: str
    roman_numerals: List[str]
    rule_broken: str
    rule_effect: str
    voice_leading_notes: List[str] = field(default_factory=list)
    emotional_arc: List[str] = field(default_factory=list)


@dataclass
class GeneratedGroove:
    """A generated groove pattern with timing offsets."""
    pattern_name: str
    tempo_bpm: int
    swing_factor: float
    timing_offsets_16th: List[float]  # ms offset per 16th note
    velocity_curve: List[int]  # 0-127 per 16th note
    rule_broken: str
    rule_effect: str


@dataclass 
class GeneratedArrangement:
    """Arrangement structure with sections."""
    sections: List[Dict]  # [{name, bars, energy, chords}]
    dynamic_arc: List[float]  # Energy per section
    rule_broken: str
    rule_effect: str


@dataclass
class GeneratedProduction:
    """Production guidelines based on intent."""
    eq_notes: List[str]
    dynamics_notes: List[str]
    space_notes: List[str]
    vocal_treatment: str
    rule_broken: str
    rule_effect: str


@dataclass
class GeneratedMelody:
    """Melodic guidelines and characteristics based on intent."""
    contour: str  # Shape of the melody (ascending, descending, arch, etc.)
    interval_character: str  # Step-wise, angular, repetitive, etc.
    phrase_structure: str  # Regular, fragmented, through-composed, etc.
    resolution_behavior: str  # Resolves, avoids resolution, hangs, etc.
    rhythmic_character: str  # Syncopated, on-beat, rubato, etc.
    range_notes: str  # Notes about melodic range
    motif_ideas: List[str] = field(default_factory=list)  # Specific melodic ideas
    performance_notes: List[str] = field(default_factory=list)
    rule_broken: str = ""
    rule_effect: str = ""


@dataclass
class GeneratedTexture:
    """Textural/timbral guidelines based on intent."""
    density_level: str  # Sparse, moderate, dense, overwhelming
    frequency_balance: str  # How frequency spectrum is filled
    element_roles: List[Dict] = field(default_factory=list)  # Role of each element
    space_character: str = ""  # Tight, wide, layered, etc.
    timbre_notes: List[str] = field(default_factory=list)
    interaction_notes: List[str] = field(default_factory=list)  # How elements interact
    rule_broken: str = ""
    rule_effect: str = ""


@dataclass
class GeneratedTemporal:
    """Temporal/time-based guidelines based on intent."""
    pacing: str  # Fast, slow, variable, etc.
    section_timing: List[Dict] = field(default_factory=list)  # Duration info per section
    pause_strategy: str = ""  # Where and how to use silence
    transition_style: str = ""  # How sections connect
    time_feel: str = ""  # Rushed, dragging, steady, elastic
    special_moments: List[Dict] = field(default_factory=list)  # Key temporal events
    rule_broken: str = ""
    rule_effect: str = ""


# =================================================================
# HARMONY PROCESSORS
# =================================================================

def _get_note_index(note: str) -> int:
    """Get chromatic index of a note."""
    note = note.replace('b', '#').upper()
    if note in CHROMATIC:
        return CHROMATIC.index(note)
    # Handle flats
    flat_to_sharp = {'DB': 'C#', 'EB': 'D#', 'GB': 'F#', 'AB': 'G#', 'BB': 'A#'}
    if note in flat_to_sharp:
        return CHROMATIC.index(flat_to_sharp[note])
    return 0


def _transpose_chord(chord: str, key: str) -> str:
    """Transpose a chord to a specific key."""
    # Simple implementation - just prepend key
    root_idx = _get_note_index(key)
    return chord  # Full implementation would transpose


def generate_progression_avoid_tonic(key: str, mode: str = "major") -> GeneratedProgression:
    """
    HARMONY_AvoidTonicResolution
    Generate progression that resolves to IV or VI instead of I.
    """
    if mode == "major":
        # End on IV instead of I
        progressions = [
            (['I', 'V', 'vi', 'IV'], "Axis progression ending on IV - unresolved yearning"),
            (['I', 'IV', 'V', 'IV'], "Classic with IV ending - perpetual motion"),
            (['vi', 'IV', 'I', 'vi'], "Start and end on vi - melancholy cycle"),
            (['I', 'V', 'IV', 'vi'], "Deceptive to vi - the hope never lands"),
        ]
    else:
        progressions = [
            (['i', 'VI', 'III', 'VII'], "Minor with bVII ending"),
            (['i', 'iv', 'VI', 'iv'], "Cycling minor, never resolves"),
        ]
    
    choice = random.choice(progressions)
    romans, effect = choice
    
    # Convert to actual chords
    chords = _romans_to_chords(romans, key, mode)
    
    return GeneratedProgression(
        chords=chords,
        key=key,
        mode=mode,
        roman_numerals=romans,
        rule_broken="HARMONY_AvoidTonicResolution",
        rule_effect=effect,
        emotional_arc=["stable", "building", "reaching", "suspended"],
    )


def generate_progression_modal_interchange(key: str, mode: str = "major") -> GeneratedProgression:
    """
    HARMONY_ModalInterchange
    Insert chord borrowed from parallel or related mode.
    """
    if mode == "major":
        # Borrow from parallel minor
        progressions = [
            (['I', 'V', 'iv', 'I'], "iv borrowed from minor - instant melancholy"),
            (['I', 'bVI', 'IV', 'I'], "bVI epic chord - cinematic arrival"),
            (['I', 'IV', 'bVII', 'I'], "bVII rock swagger - avoids cliché V"),
            (['I', 'bIII', 'IV', 'V'], "bIII brightness from minor - unexpected color"),
            (['I', 'V', 'bVI', 'bVII'], "Double borrowed - emotional journey"),
        ]
    else:
        # In minor, borrow from major
        progressions = [
            (['i', 'IV', 'V', 'i'], "Major IV (Dorian) - hope in darkness"),
            (['i', 'bVI', 'III', 'VII'], "Natural minor with major III"),
        ]
    
    choice = random.choice(progressions)
    romans, effect = choice
    chords = _romans_to_chords(romans, key, mode)
    
    return GeneratedProgression(
        chords=chords,
        key=key,
        mode=mode,
        roman_numerals=romans,
        rule_broken="HARMONY_ModalInterchange", 
        rule_effect=effect,
        emotional_arc=["grounded", "questioning", "shifted", "returned"],
        voice_leading_notes=["Watch chromatic movement in borrowed chord"],
    )


def generate_progression_parallel_motion(key: str, mode: str = "major") -> GeneratedProgression:
    """
    HARMONY_ParallelMotion
    Force parallel 5ths/octaves - power chord style.
    """
    # Power chord progressions
    progressions = [
        (['I5', 'bVII5', 'IV5', 'I5'], "Classic rock parallel 5ths"),
        (['I5', 'IV5', 'V5', 'IV5'], "Power ballad motion"),
        (['i5', 'bVII5', 'bVI5', 'V5'], "Metal descent"),
        (['I5', 'bIII5', 'IV5', 'V5'], "Punk parallel climb"),
    ]
    
    choice = random.choice(progressions)
    romans, effect = choice
    chords = _romans_to_chords(romans, key, mode)
    
    return GeneratedProgression(
        chords=chords,
        key=key,
        mode=mode,
        roman_numerals=romans,
        rule_broken="HARMONY_ParallelMotion",
        rule_effect=effect,
        emotional_arc=["power", "defiance", "momentum", "landing"],
        voice_leading_notes=["All voices move in parallel - intentional fusion"],
    )


def generate_progression_unresolved_dissonance(key: str, mode: str = "major") -> GeneratedProgression:
    """
    HARMONY_UnresolvedDissonance
    Leave 7ths, 9ths, tritones hanging.
    """
    progressions = [
        (['Imaj7', 'IVmaj7', 'viim7b5', 'IVmaj7'], "All 7ths, ends on IV7"),
        (['Imaj9', 'vim7', 'IVadd9', 'Vsus4'], "Extensions and sus - nothing fully resolves"),
        (['Im7', 'bVImaj7', 'IVm7', 'bVII7'], "Minor 7th chain - perpetual tension"),
    ]
    
    choice = random.choice(progressions)
    romans, effect = choice
    chords = _romans_to_chords(romans, key, mode)
    
    return GeneratedProgression(
        chords=chords,
        key=key,
        mode=mode,
        roman_numerals=romans,
        rule_broken="HARMONY_UnresolvedDissonance",
        rule_effect=effect,
        emotional_arc=["questioning", "reaching", "suspended", "lingering"],
    )


def generate_progression_tritone_substitution(key: str, mode: str = "major") -> GeneratedProgression:
    """
    HARMONY_TritoneSubstitution
    Replace V7 with bII7 for chromatic bass movement.
    """
    progressions = [
        (['Imaj7', 'vim7', 'bII7', 'Imaj7'], "bII7 replaces V7 - chromatic resolution"),
        (['Imaj7', 'IVmaj7', 'bII7', 'I6'], "Tritone sub before tonic - jazz sophistication"),
        (['iim7', 'bII7', 'Imaj7', 'vim7'], "ii-V becomes ii-bII - smooth chromatic bass"),
        (['Imaj7', 'bVI7', 'bII7', 'I'], "Double tritone subs - maximum color"),
    ]

    choice = random.choice(progressions)
    romans, effect = choice
    chords = _romans_to_chords(romans, key, mode)

    return GeneratedProgression(
        chords=chords,
        key=key,
        mode=mode,
        roman_numerals=romans,
        rule_broken="HARMONY_TritoneSubstitution",
        rule_effect=effect,
        emotional_arc=["grounded", "tension", "chromatic", "resolution"],
        voice_leading_notes=["Bass moves by half-step - emphasize this chromatic movement"],
    )


def generate_progression_polytonality(key: str, mode: str = "major") -> GeneratedProgression:
    """
    HARMONY_Polytonality
    Stack chords from different keys for tension and disorientation.
    """
    # Express as slash chords or compound chords
    progressions = [
        (['I/bII', 'IV/V', 'bVI/bVII', 'I'], "Polytonal clashes - internal conflict"),
        (['Imaj7#11', 'bVImaj7#11', 'IVmaj7#11', 'V7#9'], "Lydian stacks - dreamlike dissonance"),
        (['I', 'I+bV', 'IV', 'IV+bI'], "Bitonal moments - reality shifting"),
        (['Im', 'IM/Im', 'IVm/IVM', 'Vm'], "Major/minor superimposition - emotional duality"),
    ]

    choice = random.choice(progressions)
    romans, effect = choice
    chords = _romans_to_chords(romans, key, mode)

    return GeneratedProgression(
        chords=chords,
        key=key,
        mode=mode,
        roman_numerals=romans,
        rule_broken="HARMONY_Polytonality",
        rule_effect=effect,
        emotional_arc=["stable", "fractured", "disoriented", "reintegrated"],
        voice_leading_notes=["Let the clash be heard - don't bury it in reverb"],
    )


def _romans_to_chords(romans: List[str], key: str, mode: str) -> List[str]:
    """Convert Roman numerals to chord names in key."""
    # Simplified mapping - full implementation would be more complete
    key_root = _get_note_index(key)
    
    # Scale degrees for major
    major_intervals = [0, 2, 4, 5, 7, 9, 11]  # I, ii, iii, IV, V, vi, vii
    minor_intervals = [0, 2, 3, 5, 7, 8, 10]  # i, ii°, III, iv, v, VI, VII
    
    intervals = major_intervals if mode == "major" else minor_intervals
    
    result = []
    for roman in romans:
        chord = _roman_to_chord(roman, key, intervals)
        result.append(chord)
    
    return result


def _roman_to_chord(roman: str, key: str, intervals: List[int]) -> str:
    """Convert single Roman numeral to chord."""
    key_idx = _get_note_index(key)
    
    # Parse the roman numeral
    roman_clean = roman.upper().replace('5', '').replace('°', '')
    
    # Handle flats
    flat_offset = 0
    if roman_clean.startswith('B'):
        flat_offset = -1
        roman_clean = roman_clean[1:]
    
    # Map to scale degree
    degree_map = {'I': 0, 'II': 1, 'III': 2, 'IV': 3, 'V': 4, 'VI': 5, 'VII': 6}
    
    # Handle extensions
    suffix = ''
    for ext in ['MAJ7', 'MAJ9', 'M7', 'M9', 'ADD9', 'SUS4', 'SUS2', '7', '9', '11', '13']:
        if ext in roman.upper():
            suffix = ext.lower().replace('maj', 'maj').replace('add', 'add').replace('sus', 'sus')
            roman_clean = roman_clean.replace(ext, '')
            break
    
    # Get base roman
    for deg, idx in degree_map.items():
        if deg in roman_clean:
            # Calculate root note
            interval = intervals[idx] if idx < len(intervals) else 0
            root_idx = (key_idx + interval + flat_offset) % 12
            root = CHROMATIC_FLAT[root_idx] if flat_offset < 0 else CHROMATIC[root_idx]
            
            # Determine quality from original roman
            if roman.islower() or 'm' in roman.lower():
                quality = 'm' if '°' not in roman else 'dim'
            else:
                quality = ''
            
            # Handle power chords
            if '5' in roman:
                return f"{root}5"
            
            return f"{root}{quality}{suffix}"
    
    return roman  # Fallback


# =================================================================
# RHYTHM PROCESSORS
# =================================================================

def generate_groove_constant_displacement(tempo: int) -> GeneratedGroove:
    """
    RHYTHM_ConstantDisplacement
    Shift pattern one 16th note late.
    """
    # 16 slots per bar at 16th note resolution
    # Positive = late, negative = early
    base_offset_ms = (60000 / tempo) / 4  # Duration of one 16th
    
    # Shift everything late by ~half a 16th
    displacement = base_offset_ms * 0.5
    
    timing = [displacement] * 16  # Constant late feel
    
    # Velocity: emphasize 2 and 4 (backbeat)
    velocity = [90, 60, 80, 60, 100, 60, 80, 60, 90, 60, 80, 60, 100, 60, 80, 60]
    
    return GeneratedGroove(
        pattern_name="Displaced Pocket",
        tempo_bpm=tempo,
        swing_factor=0.0,  # Straight but late
        timing_offsets_16th=timing,
        velocity_curve=velocity,
        rule_broken="RHYTHM_ConstantDisplacement",
        rule_effect="Perpetually behind the beat - unsettling, anxious",
    )


def generate_groove_tempo_fluctuation(tempo: int) -> GeneratedGroove:
    """
    RHYTHM_TempoFluctuation
    Gradual ±5 BPM drift over phrase.
    """
    # Create tempo drift curve over 16 beats (4 bars)
    # Starts at tempo, drifts up to tempo+5, back down
    import math
    
    timing = []
    for i in range(16):
        # Sinusoidal drift
        drift = 5 * math.sin(i * math.pi / 8)  # ±5 BPM
        # Convert BPM drift to ms offset
        base_16th_ms = (60000 / tempo) / 4
        drifted_16th_ms = (60000 / (tempo + drift)) / 4
        offset = drifted_16th_ms - base_16th_ms
        timing.append(offset)
    
    velocity = [95, 70, 85, 70, 100, 70, 85, 70, 95, 70, 85, 70, 100, 70, 85, 70]
    
    return GeneratedGroove(
        pattern_name="Breathing Tempo",
        tempo_bpm=tempo,
        swing_factor=0.15,
        timing_offsets_16th=timing,
        velocity_curve=velocity,
        rule_broken="RHYTHM_TempoFluctuation",
        rule_effect="Organic breathing, tension and release through tempo",
    )


def generate_groove_metric_modulation(tempo: int) -> GeneratedGroove:
    """
    RHYTHM_MetricModulation
    Switch implied time signature within loop.
    """
    # First 12 16ths in 4/4, last 4 feel like 3/4
    # Create accent pattern that implies 3/4 at end
    
    timing = [0] * 16
    
    # Velocity emphasizes different groupings
    # Bars 1-3: normal 4/4
    # Bar 4: implies 3/4 (accents every 3 instead of 4)
    velocity = [
        100, 60, 80, 60,  # Bar 1: 4/4
        100, 60, 80, 60,  # Bar 2: 4/4
        100, 60, 80, 60,  # Bar 3: 4/4
        100, 70, 80, 100, # Bar 4: shifted accents imply 3/4
    ]
    
    return GeneratedGroove(
        pattern_name="Metric Shift",
        tempo_bpm=tempo,
        swing_factor=0.0,
        timing_offsets_16th=timing,
        velocity_curve=velocity,
        rule_broken="RHYTHM_MetricModulation",
        rule_effect="Momentary disorientation as time signature shifts",
    )


def generate_groove_dropped_beats(tempo: int) -> GeneratedGroove:
    """
    RHYTHM_DroppedBeats
    Remove expected beats for emphasis through absence.
    """
    # Create gaps - velocity 0 = silence
    velocity = [
        100, 70, 85, 70,  # Bar 1: normal
        100, 70, 85, 0,   # Bar 2: drop the "and" of 4
        100, 0, 85, 70,   # Bar 3: drop the 2
        100, 70, 0, 70,   # Bar 4: drop the 3
    ]

    timing = [0] * 16

    return GeneratedGroove(
        pattern_name="Breathe Space",
        tempo_bpm=tempo,
        swing_factor=0.1,
        timing_offsets_16th=timing,
        velocity_curve=velocity,
        rule_broken="RHYTHM_DroppedBeats",
        rule_effect="Impact through absence - the silence hits harder",
    )


def generate_groove_polyrhythmic_layers(tempo: int) -> GeneratedGroove:
    """
    RHYTHM_PolyrhythmicLayers
    Layer conflicting rhythmic patterns (3 against 4, 5 against 4, etc.).
    """
    import math

    # Create a polyrhythmic pattern - 3 against 4
    # In 16 16th notes (4 beats), we need accents at 3:4 ratio
    # 4 beats = positions 0, 4, 8, 12 (every 4th 16th)
    # 3 against 4 = positions 0, 5.33, 10.66 (every 5.33 16ths)

    timing = []
    velocity = []

    for i in range(16):
        # Primary layer (4/4 feel)
        is_four_accent = (i % 4 == 0)
        # Secondary layer (3 over 4 - approximated)
        three_positions = [0, 5, 11]  # Approximation of 3 over 4
        is_three_accent = i in three_positions

        if is_four_accent and is_three_accent:
            velocity.append(110)  # Both layers align - maximum accent
        elif is_four_accent:
            velocity.append(95)   # 4/4 accent
        elif is_three_accent:
            velocity.append(85)   # 3/4 accent
        else:
            velocity.append(60)   # Weak

        # Slight timing push on the "3" layer to emphasize conflict
        if is_three_accent and not is_four_accent:
            timing.append(-5)  # Slightly early, creates tension
        else:
            timing.append(0)

    return GeneratedGroove(
        pattern_name="Polyrhythmic Tension",
        tempo_bpm=tempo,
        swing_factor=0.0,  # Keep straight to hear the polyrhythm
        timing_offsets_16th=timing,
        velocity_curve=velocity,
        rule_broken="RHYTHM_PolyrhythmicLayers",
        rule_effect="Competing rhythmic grids create complexity and internal conflict",
    )


# =================================================================
# ARRANGEMENT PROCESSORS
# =================================================================

def generate_arrangement_structural_mismatch(narrative_arc: str) -> GeneratedArrangement:
    """
    ARRANGEMENT_StructuralMismatch
    Use unexpected structure for genre.
    """
    if narrative_arc == "Sudden Shift":
        # Long build, immediate payoff, then reflection
        sections = [
            {"name": "Intro", "bars": 8, "energy": 0.3, "notes": "Restrained, building"},
            {"name": "Verse 1", "bars": 16, "energy": 0.4, "notes": "Constrained energy"},
            {"name": "Build", "bars": 8, "energy": 0.7, "notes": "Rising tension"},
            {"name": "DROP", "bars": 4, "energy": 1.0, "notes": "THE SHIFT - maximum impact"},
            {"name": "Release", "bars": 16, "energy": 0.6, "notes": "Aftermath, processing"},
            {"name": "Outro", "bars": 8, "energy": 0.3, "notes": "Gentle landing"},
        ]
        arc = [0.3, 0.4, 0.7, 1.0, 0.6, 0.3]
    
    elif narrative_arc == "Slow Reveal":
        # Through-composed, no repetition
        sections = [
            {"name": "Movement I", "bars": 16, "energy": 0.3, "notes": "Introduction of theme"},
            {"name": "Movement II", "bars": 16, "energy": 0.5, "notes": "Development"},
            {"name": "Movement III", "bars": 12, "energy": 0.7, "notes": "Complication"},
            {"name": "Movement IV", "bars": 8, "energy": 0.4, "notes": "The reveal"},
            {"name": "Coda", "bars": 8, "energy": 0.2, "notes": "Resolution"},
        ]
        arc = [0.3, 0.5, 0.7, 0.4, 0.2]
    
    elif narrative_arc == "Repetitive Despair":
        # Same section repeating with minor variations
        sections = [
            {"name": "Loop A", "bars": 8, "energy": 0.5, "notes": "The cycle begins"},
            {"name": "Loop A'", "bars": 8, "energy": 0.55, "notes": "Slight variation"},
            {"name": "Loop A''", "bars": 8, "energy": 0.6, "notes": "Building frustration"},
            {"name": "Loop A'''", "bars": 8, "energy": 0.5, "notes": "Back to start - trapped"},
            {"name": "Loop A''''", "bars": 8, "energy": 0.45, "notes": "Fading energy"},
        ]
        arc = [0.5, 0.55, 0.6, 0.5, 0.45]
    
    else:  # Default Climb-to-Climax
        sections = [
            {"name": "Intro", "bars": 4, "energy": 0.2, "notes": "Minimal"},
            {"name": "Verse", "bars": 16, "energy": 0.4, "notes": "Building"},
            {"name": "Pre-Chorus", "bars": 8, "energy": 0.6, "notes": "Rising"},
            {"name": "Chorus", "bars": 16, "energy": 0.8, "notes": "Arrival"},
            {"name": "Bridge", "bars": 8, "energy": 0.5, "notes": "Brief retreat"},
            {"name": "Final Chorus", "bars": 16, "energy": 1.0, "notes": "Peak"},
            {"name": "Outro", "bars": 8, "energy": 0.3, "notes": "Descent"},
        ]
        arc = [0.2, 0.4, 0.6, 0.8, 0.5, 1.0, 0.3]
    
    return GeneratedArrangement(
        sections=sections,
        dynamic_arc=arc,
        rule_broken="ARRANGEMENT_StructuralMismatch",
        rule_effect="Structure serves the story, not genre convention",
    )


def generate_arrangement_extreme_dynamics() -> GeneratedArrangement:
    """
    ARRANGEMENT_ExtremeDynamicRange
    Exceed normal dynamic limits for dramatic impact.
    """
    sections = [
        {"name": "Whisper", "bars": 8, "energy": 0.1, "notes": "Nearly silent, intimate"},
        {"name": "Build", "bars": 8, "energy": 0.4, "notes": "Gradual increase"},
        {"name": "EXPLOSION", "bars": 4, "energy": 1.0, "notes": "Maximum possible volume"},
        {"name": "Silence", "bars": 2, "energy": 0.0, "notes": "Complete stop"},
        {"name": "Resolution", "bars": 16, "energy": 0.5, "notes": "Normal level feels loud after silence"},
    ]

    return GeneratedArrangement(
        sections=sections,
        dynamic_arc=[0.1, 0.4, 1.0, 0.0, 0.5],
        rule_broken="ARRANGEMENT_ExtremeDynamicRange",
        rule_effect="The silence after the explosion is deafening",
    )


def generate_arrangement_unbalanced_dynamics() -> GeneratedArrangement:
    """
    ARRANGEMENT_UnbalancedDynamics
    Keep specific element intentionally too loud or quiet throughout.
    """
    sections = [
        {
            "name": "Intro",
            "bars": 8,
            "energy": 0.5,
            "notes": "Establish the imbalance immediately",
            "mix_notes": "Bass is 6dB too loud - intentional weight"
        },
        {
            "name": "Verse",
            "bars": 16,
            "energy": 0.5,
            "notes": "Maintain the same imbalance",
            "mix_notes": "Don't fix the bass - the weight IS the point"
        },
        {
            "name": "Chorus",
            "bars": 8,
            "energy": 0.7,
            "notes": "Increase energy but keep imbalance",
            "mix_notes": "Everything else comes up, bass stays dominant"
        },
        {
            "name": "Bridge",
            "bars": 8,
            "energy": 0.4,
            "notes": "Brief moment of balance",
            "mix_notes": "Balance temporarily - makes return to imbalance more impactful"
        },
        {
            "name": "Final",
            "bars": 8,
            "energy": 0.8,
            "notes": "Return to imbalance, even more extreme",
            "mix_notes": "Bass now 8dB too loud - obsession made sonic"
        },
    ]

    return GeneratedArrangement(
        sections=sections,
        dynamic_arc=[0.5, 0.5, 0.7, 0.4, 0.8],
        rule_broken="ARRANGEMENT_UnbalancedDynamics",
        rule_effect="The imbalance creates obsessive focus - one element dominates attention",
    )


def generate_arrangement_buried_vocals() -> GeneratedArrangement:
    """
    ARRANGEMENT_BuriedVocals
    Place vocals intentionally below/behind instruments.
    """
    sections = [
        {
            "name": "Intro",
            "bars": 8,
            "energy": 0.4,
            "notes": "Instrumental setup",
            "vocal_level": "none"
        },
        {
            "name": "Verse 1",
            "bars": 16,
            "energy": 0.5,
            "notes": "Vocals emerge but buried",
            "vocal_level": "-6dB from instruments",
            "vocal_notes": "Vocal is texture, not focus. Words half-heard."
        },
        {
            "name": "Chorus",
            "bars": 8,
            "energy": 0.7,
            "notes": "Vocals rise slightly but never dominate",
            "vocal_level": "-3dB from instruments",
            "vocal_notes": "Still fighting through - intimacy through distance"
        },
        {
            "name": "Verse 2",
            "bars": 16,
            "energy": 0.5,
            "notes": "Return to deeply buried",
            "vocal_level": "-8dB from instruments",
            "vocal_notes": "Deeper burial - dissociation intensifies"
        },
        {
            "name": "Bridge - Exposed",
            "bars": 8,
            "energy": 0.3,
            "notes": "Strip away instruments - vocal finally clear",
            "vocal_level": "0dB - solo or near-solo",
            "vocal_notes": "The one moment of clarity - devastating impact"
        },
        {
            "name": "Final Chorus",
            "bars": 8,
            "energy": 0.8,
            "notes": "Instruments return, vocal buried again",
            "vocal_level": "-6dB from instruments",
            "vocal_notes": "Return to burial after clarity - the cost of vulnerability"
        },
    ]

    return GeneratedArrangement(
        sections=sections,
        dynamic_arc=[0.4, 0.5, 0.7, 0.5, 0.3, 0.8],
        rule_broken="ARRANGEMENT_BuriedVocals",
        rule_effect="Intimacy through distance - forcing the listener to lean in",
    )


def generate_arrangement_premature_climax() -> GeneratedArrangement:
    """
    ARRANGEMENT_PrematureClimax
    Put the emotional/sonic peak earlier than expected, then deal with aftermath.
    """
    sections = [
        {
            "name": "Intro",
            "bars": 4,
            "energy": 0.3,
            "notes": "Brief setup"
        },
        {
            "name": "Build",
            "bars": 8,
            "energy": 0.6,
            "notes": "Rapid escalation"
        },
        {
            "name": "CLIMAX",
            "bars": 4,
            "energy": 1.0,
            "notes": "THE PEAK - happens at 30% through the song, not 75%"
        },
        {
            "name": "Aftermath I",
            "bars": 16,
            "energy": 0.5,
            "notes": "Processing what just happened"
        },
        {
            "name": "Aftermath II",
            "bars": 16,
            "energy": 0.4,
            "notes": "Continued reflection, gradual descent"
        },
        {
            "name": "Resolution",
            "bars": 8,
            "energy": 0.3,
            "notes": "Quiet ending - the aftermath IS the story"
        },
    ]

    return GeneratedArrangement(
        sections=sections,
        dynamic_arc=[0.3, 0.6, 1.0, 0.5, 0.4, 0.3],
        rule_broken="ARRANGEMENT_PrematureClimax",
        rule_effect="The aftermath is the story - what happens after the moment of impact",
    )


# =================================================================
# PRODUCTION PROCESSORS
# =================================================================

def generate_production_guidelines(
    rule_to_break: str,
    vulnerability: str,
    imagery: str
) -> GeneratedProduction:
    """Generate production guidelines based on intent."""
    
    # Base guidelines
    eq_notes = []
    dynamics_notes = []
    space_notes = []
    vocal_treatment = ""
    
    # Rule-specific modifications
    if rule_to_break == "PRODUCTION_ExcessiveMud":
        eq_notes = [
            "DO NOT cut 200-400Hz - let the mud exist",
            "The weight is the point",
            "Consider BOOSTING low-mids for claustrophobia",
        ]
        dynamics_notes = ["Heavy compression to emphasize density"]
        space_notes = ["Minimal reverb - keep it close and suffocating"]
        vocal_treatment = "Slightly buried, fighting through the mud"
    
    elif rule_to_break == "PRODUCTION_PitchImperfection":
        eq_notes = ["Natural, minimal processing"]
        dynamics_notes = ["Light compression to preserve dynamics"]
        space_notes = ["Room sound acceptable"]
        vocal_treatment = "NO pitch correction - the drift IS the emotion"
    
    elif rule_to_break == "PRODUCTION_BuriedVocals":
        eq_notes = ["Roll off some highs on vocal for distance"]
        dynamics_notes = ["Compress heavily to make it part of the texture"]
        space_notes = ["Heavy reverb on vocal, less on instruments"]
        vocal_treatment = "Sit BEHIND the instruments - intimacy through distance"
    
    elif rule_to_break == "PRODUCTION_RoomNoise":
        eq_notes = ["Don't filter out room tone"]
        dynamics_notes = ["Let natural dynamics exist"]
        space_notes = ["The room IS the reverb"]
        vocal_treatment = "Record in the space, not the booth"
    
    elif rule_to_break == "PRODUCTION_Distortion":
        eq_notes = ["Saturate the mids", "Let it clip intentionally"]
        dynamics_notes = ["Crush the dynamics on specific elements"]
        space_notes = ["Distortion provides its own 'space'"]
        vocal_treatment = "Consider vocal distortion at emotional peaks"
    
    elif rule_to_break == "PRODUCTION_MonoCollapse":
        eq_notes = ["Check in mono frequently", "Bass and kick center"]
        dynamics_notes = ["Standard"]
        space_notes = ["Narrow stereo field intentionally", "Creates claustrophobia"]
        vocal_treatment = "Dead center, no width"

    elif rule_to_break == "PRODUCTION_LoFiDegradation":
        eq_notes = [
            "Roll off highs aggressively (low-pass around 8-10kHz)",
            "Add subtle low-pass filter modulation for tape wobble",
            "Consider bit-crushing for digital artifacts",
        ]
        dynamics_notes = [
            "Heavy compression with slow attack - pump effect",
            "Let the compression artifacts be audible",
        ]
        space_notes = [
            "Use degraded reverb - spring or plate with noise",
            "Add vinyl crackle or tape hiss as texture layer",
            "Keep it close - lo-fi is intimate",
        ]
        vocal_treatment = "Process through tape emulation or bit crusher - imperfection is memory"

    elif rule_to_break == "PRODUCTION_SilenceAsInstrument":
        eq_notes = ["Standard - make the sound clear so its absence is felt"]
        dynamics_notes = [
            "Use hard gates for sudden dropouts",
            "Automate volume to zero - not fade, CUT",
            "The silence must be absolute, not quiet",
        ]
        space_notes = [
            "Reverb tails should cut with the sound",
            "No ambient bed during silence sections",
            "Consider room tone only - dead silence is unsettling",
        ]
        vocal_treatment = "Cut mid-word for maximum impact - the unfinished thought"

    elif rule_to_break == "PRODUCTION_ClippingPeaks":
        eq_notes = [
            "Don't fix the clipping - it's intentional",
            "Emphasize the clipped frequencies",
            "Consider adding harmonic saturation to spread the damage",
        ]
        dynamics_notes = [
            "Push into the red intentionally",
            "Use hard clipping, not soft limiting",
            "Let transients clip - the crack is the emotion",
        ]
        space_notes = [
            "Dry signal clips better - reverb softens the edge",
            "Consider clipping the reverb return separately",
        ]
        vocal_treatment = "Allow vocal peaks to clip at emotional climax - the voice breaking"

    else:
        # Default based on vulnerability
        if vulnerability == "High":
            eq_notes = ["Gentle, natural EQ", "Don't over-polish"]
            dynamics_notes = ["Preserve natural dynamics"]
            space_notes = ["Intimate reverb, not concert hall"]
            vocal_treatment = "Present but not 'produced'"
        else:
            eq_notes = ["Standard mixing practices"]
            dynamics_notes = ["Appropriate compression"]
            space_notes = ["Genre-appropriate space"]
            vocal_treatment = "Clear and present"
    
    # Imagery texture modifications
    if "vast" in imagery.lower() or "open" in imagery.lower():
        space_notes.append("Wide stereo field")
        space_notes.append("Long reverb tails")
    elif "muffled" in imagery.lower():
        eq_notes.append("Roll off highs aggressively")
        space_notes.append("Distant, filtered reverb")
    elif "sharp" in imagery.lower():
        eq_notes.append("Emphasize presence frequencies (2-5kHz)")
        dynamics_notes.append("Fast attack compression")
    
    return GeneratedProduction(
        eq_notes=eq_notes,
        dynamics_notes=dynamics_notes,
        space_notes=space_notes,
        vocal_treatment=vocal_treatment,
        rule_broken=rule_to_break,
        rule_effect=RULE_BREAKING_EFFECTS.get(rule_to_break, {}).get("effect", ""),
    )


# =================================================================
# MELODY PROCESSORS
# =================================================================

def generate_melody_avoid_resolution(key: str, mode: str = "major") -> GeneratedMelody:
    """
    MELODY_AvoidResolution
    End phrases on non-tonic tones for incompleteness.
    """
    return GeneratedMelody(
        contour="Ascending or arch - reaching but never arriving",
        interval_character="Step-wise with occasional leaps that don't resolve",
        phrase_structure="Phrases end on 2nd, 6th, or 7th scale degree",
        resolution_behavior="NEVER resolve to tonic at phrase end - hang on tensions",
        rhythmic_character="Phrases trail off or sustain rather than land",
        range_notes="Mid-range preferred - high notes imply climax/resolution",
        motif_ideas=[
            "End verse phrases on the 2nd (re) - eternal questioning",
            "Use 7th as final note - perpetual leading",
            "Sustain through expected resolution point",
            "Let phrases fade rather than conclude",
        ],
        performance_notes=[
            "Vocal should sound like thought continuing beyond the phrase",
            "Avoid finality in delivery - everything is ongoing",
            "Consider breath placement that suggests continuation",
        ],
        rule_broken="MELODY_AvoidResolution",
        rule_effect="Incompleteness, searching, yearning - the question without answer",
    )


def generate_melody_excessive_repetition(key: str, mode: str = "major") -> GeneratedMelody:
    """
    MELODY_ExcessiveRepetition
    Repeat melodic cell obsessively beyond comfort.
    """
    return GeneratedMelody(
        contour="Circular - the same shape repeating",
        interval_character="Simple, memorable cell (2-4 notes) repeated obsessively",
        phrase_structure="Same phrase 8+ times with minimal variation",
        resolution_behavior="Resolution exists but becomes meaningless through repetition",
        rhythmic_character="Locked, mechanical, ritualistic",
        range_notes="Narrow range - trapped within a few notes",
        motif_ideas=[
            "3-note descending cell repeated throughout entire verse",
            "Single phrase that IS the chorus - nothing else",
            "Micro-variations only (dynamics, timing) - melody stays identical",
            "Consider the mantra quality - the repetition IS the meaning",
        ],
        performance_notes=[
            "Each repetition should feel both inevitable and maddening",
            "Subtle emotional shift through repetitions despite identical notes",
            "The monotony should become hypnotic, then uncomfortable",
            "Let desperation or acceptance creep in through delivery, not melody",
        ],
        rule_broken="MELODY_ExcessiveRepetition",
        rule_effect="Hypnotic, obsessive, ritualistic - spiral thoughts that can't escape",
    )


def generate_melody_angular_intervals(key: str, mode: str = "major") -> GeneratedMelody:
    """
    MELODY_AngularIntervals
    Use wide, awkward interval leaps for discomfort.
    """
    return GeneratedMelody(
        contour="Jagged, unpredictable - avoiding smooth motion",
        interval_character="Tritones, 7ths, 9ths - the 'wrong' intervals",
        phrase_structure="Fragmented by the leaps - hard to sing along",
        resolution_behavior="Leaps may resolve but to unexpected places",
        rhythmic_character="Syncopated or irregular to emphasize the discomfort",
        range_notes="Wide range required - exploiting the extremes",
        motif_ideas=[
            "Tritone leap at emotional peak - the devil's interval for the unspeakable",
            "Minor 9th drop for sudden isolation/falling",
            "Avoid all stepwise motion - every move is a jump",
            "7th up followed by tritone down - complete destabilization",
        ],
        performance_notes=[
            "Don't smooth out the leaps - the awkwardness is the point",
            "Let voice crack or strain on difficult intervals",
            "The discomfort in singing mirrors the emotional discomfort",
            "Consider speaking sections where melody becomes too difficult",
        ],
        rule_broken="MELODY_AngularIntervals",
        rule_effect="Discomfort, unease, alienation - something is deeply wrong",
    )


def generate_melody_anti_climax(key: str, mode: str = "major") -> GeneratedMelody:
    """
    MELODY_AntiClimax
    Build up then resolve downward/weakly instead of triumphantly.
    """
    return GeneratedMelody(
        contour="Ascending build that deflates - the arch collapses",
        interval_character="Ascending steps that reverse into descending minor intervals",
        phrase_structure="Long build → weak landing, often below starting point",
        resolution_behavior="Resolves DOWN when up is expected - deflation",
        rhythmic_character="Accelerating then suddenly slower/quieter",
        range_notes="Build to high range, but climax arrives low or mid",
        motif_ideas=[
            "Pre-chorus rises a 5th, chorus enters a 3rd BELOW where verse started",
            "Build to the highest note of the song... on a weak syllable, quickly",
            "The big moment arrives as a whisper, not a shout",
            "Melodic peak is a question (rising) that answers itself weakly (falling)",
        ],
        performance_notes=[
            "The deflation should feel like disappointment, resignation, or acceptance",
            "Energy must build authentically so the anticlimax lands",
            "Don't telegraph the anticlimax - let it surprise",
            "The weak resolution should feel inevitable in retrospect",
        ],
        rule_broken="MELODY_AntiClimax",
        rule_effect="Disappointment, deflation, resignation - failed expectations",
    )


def generate_melody_monotone_drone(key: str, mode: str = "major") -> GeneratedMelody:
    """
    MELODY_MonotoneDrone
    Minimal melodic movement, near-monotone for numbness.
    """
    return GeneratedMelody(
        contour="Flat line - horizontal, minimal pitch change",
        interval_character="Unisons and minor 2nds only - micro-movements",
        phrase_structure="Continuous drone with tiny inflections",
        resolution_behavior="No resolution because no tension created",
        rhythmic_character="Speech rhythms over static pitch",
        range_notes="2-3 note range maximum - intentionally limited",
        motif_ideas=[
            "Entire verse on a single note with occasional half-step dips",
            "Recitation tone - like chanting or praying",
            "Harmony moves underneath static melody - world shifts, voice doesn't",
            "Micro-ornaments (quarter-tone bends) are the only 'melody'",
        ],
        performance_notes=[
            "The monotone is dissociation made audible",
            "Emotion comes through timbre and dynamics, not pitch",
            "Consider the state between speaking and singing",
            "Numbness, meditation, or shutdown - voice has given up expression",
        ],
        rule_broken="MELODY_MonotoneDrone",
        rule_effect="Numbness, dissociation, meditation - emotional shutdown",
    )


def generate_melody_fragmented_phrases(key: str, mode: str = "major") -> GeneratedMelody:
    """
    MELODY_FragmentedPhrases
    Break melody into disconnected fragments for fractured thought.
    """
    return GeneratedMelody(
        contour="Interrupted, stop-start, phrases cut short",
        interval_character="Normal intervals but phrases never complete",
        phrase_structure="2-3 words then silence, restart differently",
        resolution_behavior="Phrases end abruptly before resolution possible",
        rhythmic_character="Irregular, gasping, catching breath",
        range_notes="Full range but used in disconnected bursts",
        motif_ideas=[
            "Sentence melody cut mid-word, resume somewhere else",
            "Silences are as long as the sung fragments",
            "Each fragment in different part of range - no continuity",
            "The melody keeps trying to start but can't sustain",
        ],
        performance_notes=[
            "Sound like someone trying to speak through difficulty",
            "Interruptions should feel involuntary, not artistic",
            "Gasps, false starts, abandoned thoughts",
            "The fragmentation IS the trauma made audible",
        ],
        rule_broken="MELODY_FragmentedPhrases",
        rule_effect="Fractured thought, interrupted speech, trauma - difficulty expressing",
    )


# =================================================================
# TEXTURE PROCESSORS
# =================================================================

def generate_texture_frequency_masking() -> GeneratedTexture:
    """
    TEXTURE_FrequencyMasking
    Let elements fight for same frequencies for crowded thoughts.
    """
    return GeneratedTexture(
        density_level="Dense - intentionally too many elements",
        frequency_balance="Mid-heavy - everything competing for 200Hz-2kHz",
        element_roles=[
            {"element": "Guitar 1", "role": "Occupies 200-600Hz", "notes": "Don't carve space"},
            {"element": "Guitar 2", "role": "Also 200-600Hz", "notes": "Let them fight"},
            {"element": "Keys", "role": "300-800Hz", "notes": "Adds to the pile"},
            {"element": "Vocal", "role": "Buried in the conflict", "notes": "Fighting to be heard"},
            {"element": "Bass", "role": "Bleeds into mids", "notes": "No high-pass, let it mud"},
        ],
        space_character="Claustrophobic, no separation between elements",
        timbre_notes=[
            "Similar timbres that blend/fight rather than contrast",
            "Avoid clarity - clarity is not the goal here",
            "The listener should work to hear individual elements",
        ],
        interaction_notes=[
            "Elements step on each other - no polite frequency carving",
            "Ducking/sidechaining would solve this - DON'T use it",
            "The chaos is the internal monologue made sonic",
        ],
        rule_broken="TEXTURE_FrequencyMasking",
        rule_effect="Crowded, competitive, overwhelming - internal voices all talking at once",
    )


def generate_texture_sparse_emptiness() -> GeneratedTexture:
    """
    TEXTURE_SparseEmptiness
    Extreme space between elements for isolation.
    """
    return GeneratedTexture(
        density_level="Skeletal - barely anything present",
        frequency_balance="Huge gaps in spectrum - isolated pockets of sound",
        element_roles=[
            {"element": "Voice", "role": "Solo presence", "notes": "Exposed, nowhere to hide"},
            {"element": "Single instrument", "role": "Occasional support", "notes": "Long gaps between entries"},
            {"element": "Space/silence", "role": "Primary element", "notes": "The emptiness IS the texture"},
        ],
        space_character="Vast, empty, isolating - reverb emphasizes loneliness",
        timbre_notes=[
            "Each sound is precious because it's surrounded by nothing",
            "Imperfections are magnified - let them be heard",
            "The voice has nothing to lean on",
        ],
        interaction_notes=[
            "Elements rarely overlap - isolation is maintained",
            "When elements do meet, it should feel significant",
            "The space between notes is as composed as the notes",
        ],
        rule_broken="TEXTURE_SparseEmptiness",
        rule_effect="Isolation, exposure, vulnerability - nowhere to hide",
    )


def generate_texture_dense_wall() -> GeneratedTexture:
    """
    TEXTURE_DenseWall
    Stack elements into undifferentiated mass for overwhelming force.
    """
    return GeneratedTexture(
        density_level="Overwhelming - too much, intentionally",
        frequency_balance="Full spectrum saturation - every frequency filled",
        element_roles=[
            {"element": "Bass", "role": "Foundation extending into mids", "notes": "Massive"},
            {"element": "Guitars/Keys", "role": "Wall of sound", "notes": "Layered, doubled, stacked"},
            {"element": "Drums", "role": "Constant presence", "notes": "Not leading, supporting the mass"},
            {"element": "Vocal", "role": "Part of the wall OR fighting through", "notes": "Choose one"},
            {"element": "Additional layers", "role": "Fill every remaining gap", "notes": "Pads, drones, noise"},
        ],
        space_character="No space - the wall is solid",
        timbre_notes=[
            "Individual elements lose identity in the mass",
            "The wall becomes its own instrument",
            "Saturation and compression to glue everything together",
        ],
        interaction_notes=[
            "No element should be individually distinguishable",
            "The listener is swept up, not analyzing",
            "Catharsis through overwhelming sonic force",
        ],
        rule_broken="TEXTURE_DenseWall",
        rule_effect="Overwhelming force, loss of self, catharsis - swept away by sound",
    )


def generate_texture_conflicting_timbres() -> GeneratedTexture:
    """
    TEXTURE_ConflictingTimbres
    Combine timbres that traditionally clash for wrongness.
    """
    return GeneratedTexture(
        density_level="Moderate - conflict needs space to be heard",
        frequency_balance="Elements occupying similar ranges with different timbres",
        element_roles=[
            {"element": "Acoustic instrument", "role": "Natural, organic", "notes": "Warm, imperfect"},
            {"element": "Harsh synth", "role": "Cold, synthetic", "notes": "Bright, processed"},
            {"element": "Lo-fi element", "role": "Degraded quality", "notes": "Tape, bitcrushed"},
            {"element": "Clean element", "role": "Pristine production", "notes": "Too clean"},
        ],
        space_character="Each element in its own 'world' - they don't belong together",
        timbre_notes=[
            "The conflict should feel wrong, uncomfortable",
            "Don't blend - let the clash be audible",
            "Mix production eras: 60s with modern digital, acoustic with synthetic",
        ],
        interaction_notes=[
            "Elements coexist but don't converse",
            "The wrongness mirrors emotional dissonance",
            "Things that shouldn't be together, are",
        ],
        rule_broken="TEXTURE_ConflictingTimbres",
        rule_effect="Dissonance, wrongness, tension - things that don't belong together",
    )


def generate_texture_single_element_focus() -> GeneratedTexture:
    """
    TEXTURE_SingleElementFocus
    Strip away all but one element for stark truth.
    """
    return GeneratedTexture(
        density_level="Solo - one element carries everything",
        frequency_balance="Only what that single element provides",
        element_roles=[
            {"element": "The chosen one", "role": "Everything", "notes": "Voice OR single instrument"},
            {"element": "Nothing else", "role": "Absence", "notes": "The support doesn't exist"},
        ],
        space_character="Raw, exposed - the element and the room/void",
        timbre_notes=[
            "Every nuance of the single element is exposed",
            "Imperfections become features - nothing to hide behind",
            "The timbre IS the arrangement",
        ],
        interaction_notes=[
            "No interaction - monologue, not dialogue",
            "If anything else enters, it should be devastating",
            "Confession, revelation - the moment of truth",
        ],
        rule_broken="TEXTURE_SingleElementFocus",
        rule_effect="Stark truth, nowhere to hide, confession - naked honesty",
    )


def generate_texture_timbral_drift() -> GeneratedTexture:
    """
    TEXTURE_TimbralDrift
    Gradually morph timbre over time for transformation.
    """
    return GeneratedTexture(
        density_level="Variable - changes with the drift",
        frequency_balance="Shifting over time - what was low becomes high, etc.",
        element_roles=[
            {"element": "Primary voice/instrument", "role": "The thing that transforms", "notes": "Clear at start"},
            {"element": "Processing", "role": "Gradual morphing agent", "notes": "Automation over minutes"},
            {"element": "Environment", "role": "Also shifts", "notes": "Reverb, space changes"},
        ],
        space_character="Evolving - intimate to vast, or vice versa",
        timbre_notes=[
            "Start clean, end destroyed (or reverse)",
            "The transformation should be slow enough to be subliminal",
            "By the end, the sound should be unrecognizable from the start",
        ],
        interaction_notes=[
            "Other elements may drift at different rates",
            "Asynchronous drifting creates unease",
            "The listener realizes change has happened, not as it happens",
        ],
        rule_broken="TEXTURE_TimbralDrift",
        rule_effect="Transformation, unease, evolution - change happening beneath notice",
    )


# =================================================================
# TEMPORAL PROCESSORS
# =================================================================

def generate_temporal_extended_intro() -> GeneratedTemporal:
    """
    TEMPORAL_ExtendedIntro
    Unusually long intro for anticipation and world-building.
    """
    return GeneratedTemporal(
        pacing="Slow establishment then normal",
        section_timing=[
            {"section": "Intro", "duration": "2-4 minutes", "notes": "The setup IS the story"},
            {"section": "Main content", "duration": "Normal", "notes": "Feels like relief when it arrives"},
        ],
        pause_strategy="Extended anticipation before 'the beginning'",
        transition_style="Gradual accumulation - each element earned",
        time_feel="Patient, deliberately slow - testing the listener",
        special_moments=[
            {"moment": "First vocal/main element entry", "timing": "60+ seconds in", "effect": "Arrival feels significant"},
            {"moment": "Texture builds", "timing": "Throughout intro", "effect": "World construction"},
            {"moment": "Full arrangement", "timing": "2+ minutes", "effect": "Finally here"},
        ],
        rule_broken="TEMPORAL_ExtendedIntro",
        rule_effect="Anticipation, world-building, patience test - earning the beginning",
    )


def generate_temporal_abrupt_ending() -> GeneratedTemporal:
    """
    TEMPORAL_AbruptEnding
    End suddenly without resolution for shock.
    """
    return GeneratedTemporal(
        pacing="Normal then STOP",
        section_timing=[
            {"section": "Normal song", "duration": "Standard", "notes": "Build expectation of ending"},
            {"section": "Cut", "duration": "Instant", "notes": "No fade, no resolution - STOP"},
        ],
        pause_strategy="No pause - the absence of ending IS the ending",
        transition_style="No transition to nothing - the cut is total",
        time_feel="Normal until the last millisecond",
        special_moments=[
            {"moment": "The cut", "timing": "Mid-phrase ideally", "effect": "Maximum shock"},
            {"moment": "What's left out", "timing": "Never happens", "effect": "The resolution we needed but didn't get"},
        ],
        rule_broken="TEMPORAL_AbruptEnding",
        rule_effect="Shock, incompleteness, sudden loss - the story cut short",
    )


def generate_temporal_time_stretch() -> GeneratedTemporal:
    """
    TEMPORAL_TimeStretch
    Stretch or compress time perception for altered reality.
    """
    return GeneratedTemporal(
        pacing="Elastic - time bends",
        section_timing=[
            {"section": "Normal section", "duration": "4 bars feels like 4 bars", "notes": "Establish baseline"},
            {"section": "Stretched section", "duration": "4 bars feels like 16", "notes": "Tempo halves, sparse arrangement"},
            {"section": "Compressed section", "duration": "4 bars feels like 2", "notes": "Double time feel, dense"},
        ],
        pause_strategy="Pauses feel eternal in stretched sections",
        transition_style="Reality shifts at section boundaries",
        time_feel="Disorienting - 'how long has this been playing?'",
        special_moments=[
            {"moment": "First stretch", "timing": "When reality shifts", "effect": "Disassociation onset"},
            {"moment": "Return to normal", "timing": "If it happens", "effect": "Grounding, or more disorientation"},
        ],
        rule_broken="TEMPORAL_TimeStretch",
        rule_effect="Altered reality, time distortion, dream state - time becomes unreliable",
    )


def generate_temporal_loop_hypnosis() -> GeneratedTemporal:
    """
    TEMPORAL_LoopHypnosis
    Loop beyond comfortable repetition for trance state.
    """
    return GeneratedTemporal(
        pacing="Static - the loop IS time",
        section_timing=[
            {"section": "The loop", "duration": "8-32 bars repeated 8+ times", "notes": "Longer than comfortable"},
            {"section": "Micro-variations", "duration": "Within loop", "notes": "Tiny changes maintain engagement"},
        ],
        pause_strategy="No pauses - the loop is continuous",
        transition_style="No traditional transitions - the loop continues or stops",
        time_feel="Hypnotic, meditative, eventually maddening",
        special_moments=[
            {"moment": "When comfort breaks", "timing": "Around repetition 4-5", "effect": "From pleasant to obsessive"},
            {"moment": "If loop breaks", "timing": "After extended repetition", "effect": "Shock, relief, or loss"},
        ],
        rule_broken="TEMPORAL_LoopHypnosis",
        rule_effect="Hypnotic, meditative, obsessive - circular thoughts that won't stop",
    )


def generate_temporal_breath_pauses() -> GeneratedTemporal:
    """
    TEMPORAL_BreathPauses
    Insert pauses like held breath for anticipation.
    """
    return GeneratedTemporal(
        pacing="Normal with significant interruptions",
        section_timing=[
            {"section": "Normal flow", "duration": "Standard", "notes": "Establish rhythm"},
            {"section": "Breath pause", "duration": "1-4 beats of silence", "notes": "Everything stops"},
            {"section": "Resume", "duration": "Standard", "notes": "Continue or transform"},
        ],
        pause_strategy="Strategic silences before key moments - inhale before speaking",
        transition_style="Pauses ARE the transitions",
        time_feel="Punctuated, breathless, gathering courage",
        special_moments=[
            {"moment": "Pre-chorus pause", "timing": "Before the release", "effect": "Anticipation builds"},
            {"moment": "Mid-word pause", "timing": "Maximum tension", "effect": "Holding back what's hard to say"},
            {"moment": "Post-climax pause", "timing": "After the revelation", "effect": "Processing, impact"},
        ],
        rule_broken="TEMPORAL_BreathPauses",
        rule_effect="Tension, anticipation, gathering courage - the moment before speaking",
    )


def generate_temporal_accelerando_decay() -> GeneratedTemporal:
    """
    TEMPORAL_AccelerandoDecay
    Speed up then collapse for panic and exhaustion.
    """
    return GeneratedTemporal(
        pacing="Accelerating then collapsing",
        section_timing=[
            {"section": "Normal", "duration": "Standard tempo", "notes": "Establish baseline"},
            {"section": "Acceleration", "duration": "Gradual then rapid tempo increase", "notes": "Panic setting in"},
            {"section": "Breaking point", "duration": "Maximum speed, unsustainable", "notes": "Can't keep up"},
            {"section": "Collapse", "duration": "Sudden slowdown or stop", "notes": "Exhaustion, surrender"},
        ],
        pause_strategy="No pauses during acceleration - no rest allowed",
        transition_style="Tempo IS the transition - faster = more desperate",
        time_feel="Frantic then exhausted - a sprint that ends in collapse",
        special_moments=[
            {"moment": "When acceleration starts", "timing": "Anxiety trigger", "effect": "Things spinning out"},
            {"moment": "The break", "timing": "Can't be sustained", "effect": "The giving up"},
            {"moment": "The aftermath", "timing": "Whatever remains", "effect": "Exhaustion or peace"},
        ],
        rule_broken="TEMPORAL_AccelerandoDecay",
        rule_effect="Panic, collapse, exhaustion - overwhelm leading to surrender",
    )


# =================================================================
# MAIN PROCESSOR
# =================================================================

class IntentProcessor:
    """
    Processes a CompleteSongIntent to generate musical elements.

    Usage:
        processor = IntentProcessor(intent)
        progression = processor.generate_harmony()
        groove = processor.generate_groove()
        arrangement = processor.generate_arrangement()
        production = processor.generate_production()
        melody = processor.generate_melody()
        texture = processor.generate_texture()
        temporal = processor.generate_temporal()
    """

    def __init__(self, intent: CompleteSongIntent):
        self.intent = intent
        self._parse_intent()

    def _parse_intent(self):
        """Extract key parameters from intent."""
        self.key = self.intent.technical_constraints.technical_key or "F"
        self.mode = self.intent.technical_constraints.technical_mode or "major"
        self.tempo_range = self.intent.technical_constraints.technical_tempo_range
        self.tempo = sum(self.tempo_range) // 2  # Middle of range
        self.rule_to_break = self.intent.technical_constraints.technical_rule_to_break
        self.narrative_arc = self.intent.song_intent.narrative_arc
        self.vulnerability = self.intent.song_intent.vulnerability_scale
        self.imagery = self.intent.song_intent.imagery_texture

    def generate_harmony(self) -> GeneratedProgression:
        """Generate chord progression based on harmony rule to break."""
        rule = self.rule_to_break

        if rule == "HARMONY_AvoidTonicResolution":
            return generate_progression_avoid_tonic(self.key, self.mode)
        elif rule == "HARMONY_ModalInterchange":
            return generate_progression_modal_interchange(self.key, self.mode)
        elif rule == "HARMONY_ParallelMotion":
            return generate_progression_parallel_motion(self.key, self.mode)
        elif rule == "HARMONY_UnresolvedDissonance":
            return generate_progression_unresolved_dissonance(self.key, self.mode)
        elif rule == "HARMONY_TritoneSubstitution":
            return generate_progression_tritone_substitution(self.key, self.mode)
        elif rule == "HARMONY_Polytonality":
            return generate_progression_polytonality(self.key, self.mode)
        else:
            # Default to modal interchange for most emotional contexts
            return generate_progression_modal_interchange(self.key, self.mode)

    def generate_groove(self) -> GeneratedGroove:
        """Generate groove pattern based on rhythm rule to break."""
        rule = self.rule_to_break

        if rule == "RHYTHM_ConstantDisplacement":
            return generate_groove_constant_displacement(self.tempo)
        elif rule == "RHYTHM_TempoFluctuation":
            return generate_groove_tempo_fluctuation(self.tempo)
        elif rule == "RHYTHM_MetricModulation":
            return generate_groove_metric_modulation(self.tempo)
        elif rule == "RHYTHM_DroppedBeats":
            return generate_groove_dropped_beats(self.tempo)
        elif rule == "RHYTHM_PolyrhythmicLayers":
            return generate_groove_polyrhythmic_layers(self.tempo)
        else:
            # Default groove based on genre feel
            feel = self.intent.technical_constraints.technical_groove_feel or ""
            if "laid back" in feel.lower():
                return generate_groove_constant_displacement(self.tempo)
            else:
                return generate_groove_tempo_fluctuation(self.tempo)

    def generate_arrangement(self) -> GeneratedArrangement:
        """Generate arrangement based on narrative arc and arrangement rules."""
        rule = self.rule_to_break

        if rule == "ARRANGEMENT_StructuralMismatch":
            return generate_arrangement_structural_mismatch(self.narrative_arc)
        elif rule == "ARRANGEMENT_ExtremeDynamicRange":
            return generate_arrangement_extreme_dynamics()
        elif rule == "ARRANGEMENT_UnbalancedDynamics":
            return generate_arrangement_unbalanced_dynamics()
        elif rule == "ARRANGEMENT_BuriedVocals":
            return generate_arrangement_buried_vocals()
        elif rule == "ARRANGEMENT_PrematureClimax":
            return generate_arrangement_premature_climax()
        else:
            return generate_arrangement_structural_mismatch(self.narrative_arc)

    def generate_production(self) -> GeneratedProduction:
        """Generate production guidelines."""
        return generate_production_guidelines(
            self.rule_to_break,
            self.vulnerability,
            self.imagery
        )

    def generate_melody(self) -> GeneratedMelody:
        """Generate melody guidelines based on melody rule to break."""
        rule = self.rule_to_break

        if rule == "MELODY_AvoidResolution":
            return generate_melody_avoid_resolution(self.key, self.mode)
        elif rule == "MELODY_ExcessiveRepetition":
            return generate_melody_excessive_repetition(self.key, self.mode)
        elif rule == "MELODY_AngularIntervals":
            return generate_melody_angular_intervals(self.key, self.mode)
        elif rule == "MELODY_AntiClimax":
            return generate_melody_anti_climax(self.key, self.mode)
        elif rule == "MELODY_MonotoneDrone":
            return generate_melody_monotone_drone(self.key, self.mode)
        elif rule == "MELODY_FragmentedPhrases":
            return generate_melody_fragmented_phrases(self.key, self.mode)
        else:
            # Default based on vulnerability - high vulnerability suggests avoiding resolution
            if self.vulnerability == "High":
                return generate_melody_avoid_resolution(self.key, self.mode)
            else:
                return generate_melody_avoid_resolution(self.key, self.mode)

    def generate_texture(self) -> GeneratedTexture:
        """Generate texture guidelines based on texture rule to break."""
        rule = self.rule_to_break

        if rule == "TEXTURE_FrequencyMasking":
            return generate_texture_frequency_masking()
        elif rule == "TEXTURE_SparseEmptiness":
            return generate_texture_sparse_emptiness()
        elif rule == "TEXTURE_DenseWall":
            return generate_texture_dense_wall()
        elif rule == "TEXTURE_ConflictingTimbres":
            return generate_texture_conflicting_timbres()
        elif rule == "TEXTURE_SingleElementFocus":
            return generate_texture_single_element_focus()
        elif rule == "TEXTURE_TimbralDrift":
            return generate_texture_timbral_drift()
        else:
            # Default based on imagery texture
            imagery_lower = self.imagery.lower() if self.imagery else ""
            if "sparse" in imagery_lower or "empty" in imagery_lower:
                return generate_texture_sparse_emptiness()
            elif "dense" in imagery_lower or "heavy" in imagery_lower:
                return generate_texture_dense_wall()
            else:
                return generate_texture_sparse_emptiness()

    def generate_temporal(self) -> GeneratedTemporal:
        """Generate temporal guidelines based on temporal rule to break."""
        rule = self.rule_to_break

        if rule == "TEMPORAL_ExtendedIntro":
            return generate_temporal_extended_intro()
        elif rule == "TEMPORAL_AbruptEnding":
            return generate_temporal_abrupt_ending()
        elif rule == "TEMPORAL_TimeStretch":
            return generate_temporal_time_stretch()
        elif rule == "TEMPORAL_LoopHypnosis":
            return generate_temporal_loop_hypnosis()
        elif rule == "TEMPORAL_BreathPauses":
            return generate_temporal_breath_pauses()
        elif rule == "TEMPORAL_AccelerandoDecay":
            return generate_temporal_accelerando_decay()
        else:
            # Default based on narrative arc
            if self.narrative_arc == "Repetitive Despair":
                return generate_temporal_loop_hypnosis()
            elif self.narrative_arc == "Sudden Shift":
                return generate_temporal_breath_pauses()
            else:
                return generate_temporal_breath_pauses()

    def generate_all(self) -> Dict:
        """Generate all elements and return as dict."""
        return {
            "harmony": self.generate_harmony(),
            "groove": self.generate_groove(),
            "arrangement": self.generate_arrangement(),
            "production": self.generate_production(),
            "melody": self.generate_melody(),
            "texture": self.generate_texture(),
            "temporal": self.generate_temporal(),
            "intent_summary": {
                "mood": self.intent.song_intent.mood_primary,
                "tension": self.intent.song_intent.mood_secondary_tension,
                "narrative": self.narrative_arc,
                "rule_broken": self.rule_to_break,
                "justification": self.intent.technical_constraints.rule_breaking_justification,
            },
        }


def process_intent(intent: CompleteSongIntent) -> Dict:
    """
    Convenience function to process an intent and return all generated elements.
    
    Args:
        intent: Complete song intent
    
    Returns:
        Dict with harmony, groove, arrangement, production, and summary
    """
    processor = IntentProcessor(intent)
    return processor.generate_all()
