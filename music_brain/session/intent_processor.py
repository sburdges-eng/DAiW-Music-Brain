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
        else:
            # Default groove based on genre feel
            feel = self.intent.technical_constraints.technical_groove_feel
            if "laid back" in feel.lower():
                return generate_groove_constant_displacement(self.tempo)
            else:
                return generate_groove_tempo_fluctuation(self.tempo)
    
    def generate_arrangement(self) -> GeneratedArrangement:
        """Generate arrangement based on narrative arc."""
        rule = self.rule_to_break
        
        if rule == "ARRANGEMENT_StructuralMismatch":
            return generate_arrangement_structural_mismatch(self.narrative_arc)
        elif rule == "ARRANGEMENT_ExtremeDynamicRange":
            return generate_arrangement_extreme_dynamics()
        else:
            return generate_arrangement_structural_mismatch(self.narrative_arc)
    
    def generate_production(self) -> GeneratedProduction:
        """Generate production guidelines."""
        return generate_production_guidelines(
            self.rule_to_break,
            self.vulnerability,
            self.imagery
        )
    
    def generate_all(self) -> Dict:
        """Generate all elements and return as dict."""
        return {
            "harmony": self.generate_harmony(),
            "groove": self.generate_groove(),
            "arrangement": self.generate_arrangement(),
            "production": self.generate_production(),
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
