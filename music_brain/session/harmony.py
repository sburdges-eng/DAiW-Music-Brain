"""
Harmony Generator - Clean API for intent-driven chord progression generation

This module provides the main `generate_harmony()` function that takes a
CompleteSongIntent and returns a fully-analyzed harmonic result with
modal interchange and diagnostics.

Example:
    kelly_harmony = generate_harmony(kelly_intent)
    # Result: F-C-Dm-Bbm with modal interchange
    # Diagnostics confirm: "bittersweet darkness, borrowed sadness"
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class HarmonyDiagnostic:
    """Diagnostic information for a single chord"""
    symbol: str  # e.g., "Bbm"
    roman_numeral: str  # e.g., "iv"
    is_diatonic: bool
    borrowed_from: Optional[str] = None
    emotional_function: str = ""


@dataclass
class HarmonyResult:
    """
    Complete harmony generation result with progression and diagnostics.

    Attributes:
        chords: List of chord symbols (e.g., ["F", "C", "Dm", "Bbm"])
        progression_string: Hyphen-separated chord string (e.g., "F-C-Dm-Bbm")
        key: Musical key (e.g., "F")
        mode: "major" or "minor"
        roman_numerals: List of Roman numerals (e.g., ["I", "V", "vi", "iv"])
        roman_progression: Hyphen-separated Roman string (e.g., "I-V-vi-iv")
        rule_break_applied: Which rule was intentionally broken
        rule_break_effect: Emotional effect of the rule break
        emotional_justification: Why this rule was broken (from intent)
        diagnostics: Per-chord diagnostic analysis
        emotional_character: Overall emotional reading
    """
    chords: List[str]
    progression_string: str
    key: str
    mode: str
    roman_numerals: List[str]
    roman_progression: str
    rule_break_applied: Optional[str] = None
    rule_break_effect: Optional[str] = None
    emotional_justification: Optional[str] = None
    diagnostics: List[HarmonyDiagnostic] = field(default_factory=list)
    emotional_character: str = ""

    def __str__(self) -> str:
        """Pretty string representation"""
        lines = [
            f"Progression: {self.progression_string}",
            f"Key: {self.key} {self.mode}",
            f"Roman: {self.roman_progression}",
        ]
        if self.rule_break_applied:
            lines.append(f"Rule break: {self.rule_break_applied}")
            lines.append(f"Effect: {self.rule_break_effect}")
        if self.emotional_character:
            lines.append(f"Character: {self.emotional_character}")
        return "\n".join(lines)


# =============================================================================
# CORE MUSIC THEORY DATA
# =============================================================================

# MIDI note mapping
NOTE_TO_MIDI = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

# Scale intervals (semitones from root)
SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'natural_minor': [0, 2, 3, 5, 7, 8, 10],
}

# Diatonic chord qualities
MAJOR_QUALITIES = ['maj', 'min', 'min', 'maj', 'maj', 'min', 'dim']
MINOR_QUALITIES = ['min', 'dim', 'maj', 'min', 'min', 'maj', 'maj']

# Roman numerals
MAJOR_ROMAN = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']
MINOR_ROMAN = ['i', 'ii°', 'III', 'iv', 'v', 'VI', 'VII']

# Note names (prefer flats for readability)
NOTE_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

# Rule breaking effects
RULE_EFFECTS = {
    'HARMONY_ModalInterchange': 'Borrowed chord creates bittersweet color - darkness within light',
    'HARMONY_AvoidTonicResolution': 'Unresolved yearning - the song never truly arrives home',
    'HARMONY_ParallelMotion': 'Power chord parallel fifths - defiance, raw energy',
    'HARMONY_UnresolvedDissonance': 'Tension left hanging - emotional ambiguity',
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _midi_to_note(midi: int) -> str:
    """Convert MIDI note number (mod 12) to note name"""
    return NOTE_NAMES[midi % 12]


def _roman_to_chord(roman: str, key: str, mode: str) -> str:
    """
    Convert Roman numeral to chord symbol in given key.

    Args:
        roman: Roman numeral (e.g., "I", "iv", "V")
        key: Root key (e.g., "F")
        mode: "major" or "minor"

    Returns:
        Chord symbol (e.g., "F", "Bbm", "C")
    """
    scale = SCALES.get(mode, SCALES['major'])
    key_midi = NOTE_TO_MIDI.get(key, 0)

    # Parse the Roman numeral
    roman_upper = roman.upper().rstrip('°')
    is_minor_quality = roman.islower() or 'm' in roman.lower()

    # Handle flats (e.g., "bVI", "bVII")
    flat_offset = 0
    if roman_upper.startswith('B') and len(roman_upper) > 1:
        flat_offset = -1
        roman_upper = roman_upper[1:]

    # Map to scale degree - check longest matches first to avoid I matching inside IV/VI
    degree_map = [
        ('VII', 6), ('VI', 5), ('IV', 3), ('V', 4),
        ('III', 2), ('II', 1), ('I', 0)
    ]

    for deg, idx in degree_map:
        if roman_upper == deg or roman_upper.startswith(deg):
            interval = scale[idx] if idx < len(scale) else 0
            root_midi = (key_midi + interval + flat_offset) % 12
            root = _midi_to_note(root_midi)

            # Add quality suffix
            if is_minor_quality:
                return root + 'm'
            return root

    return key  # Fallback


def _chord_to_roman(chord: str, key: str, mode: str) -> tuple:
    """
    Convert chord symbol to Roman numeral and analysis.

    Returns:
        Tuple of (roman_numeral, scale_degree, is_diatonic, borrowed_from)
    """
    # Parse chord
    if len(chord) > 1 and chord[1] in ['#', 'b']:
        root = chord[:2]
        quality = chord[2:]
    else:
        root = chord[0]
        quality = chord[1:]

    is_minor = quality == 'm' or quality.lower() == 'min'

    # Calculate scale degree
    key_midi = NOTE_TO_MIDI.get(key, 0)
    root_midi = NOTE_TO_MIDI.get(root, 0)
    semitones = (root_midi - key_midi) % 12

    scale = SCALES.get(mode, SCALES['major'])

    # Find scale degree
    try:
        degree = scale.index(semitones)
    except ValueError:
        degree = -1

    if degree < 0:
        return (f"?{root}", -1, False, "chromatic")

    # Get expected quality
    if mode == 'major':
        expected_quality = MAJOR_QUALITIES[degree]
        base_roman = MAJOR_ROMAN[degree]
    else:
        expected_quality = MINOR_QUALITIES[degree]
        base_roman = MINOR_ROMAN[degree]

    actual_quality = 'min' if is_minor else 'maj'

    # Check if diatonic
    if actual_quality == expected_quality:
        return (base_roman, degree, True, None)
    else:
        # Borrowed chord
        borrowed_roman = base_roman.lower() if is_minor else base_roman.upper()
        return (borrowed_roman, degree, False, "parallel minor (modal interchange)")


def _generate_base_progression(key: str, mode: str) -> List[str]:
    """Generate base I-V-vi-IV progression in key"""
    if mode == 'major':
        romans = ['I', 'V', 'vi', 'IV']
    else:
        romans = ['i', 'VI', 'III', 'VII']

    return [_roman_to_chord(r, key, mode) for r in romans]


def _apply_modal_interchange(chords: List[str], key: str, mode: str) -> List[str]:
    """
    Apply modal interchange - borrow iv from parallel minor.

    In F major: Bb (IV) becomes Bbm (iv)
    This creates "bittersweet darkness, borrowed sadness"
    """
    if mode != 'major':
        return chords

    scale = SCALES['major']
    key_midi = NOTE_TO_MIDI.get(key, 0)
    fourth_degree_midi = (key_midi + scale[3]) % 12

    result = []
    for chord in chords:
        # Parse chord root
        if len(chord) > 1 and chord[1] in ['#', 'b']:
            root = chord[:2]
            quality = chord[2:]
        else:
            root = chord[0]
            quality = chord[1:]

        root_midi = NOTE_TO_MIDI.get(root, -1)

        # If this is the IV chord, make it minor
        if root_midi == fourth_degree_midi and quality != 'm':
            result.append(root + 'm')
        else:
            result.append(chord)

    return result


def _get_emotional_function(degree: int, is_diatonic: bool, is_minor: bool, mode: str) -> str:
    """Get emotional function description for chord"""
    if not is_diatonic:
        if is_minor:
            return "bittersweet darkness, borrowed sadness"
        return "unexpected light, borrowed brightness"

    if mode == 'major':
        functions = [
            'home, resolution',
            'preparation, subdominant minor feel',
            'mediant, bridge to relative minor',
            'subdominant, away from home',
            'dominant, tension seeking resolution',
            'relative minor, melancholy',
            'leading tone diminished, unstable'
        ]
    else:
        functions = [
            'home, minor tonic',
            'diminished supertonic, tension',
            'relative major, hopeful',
            'subdominant, darker preparation',
            'minor dominant, softer tension',
            'submediant major, brighter color',
            'subtonic major, modal flavor'
        ]

    if 0 <= degree < len(functions):
        return functions[degree]
    return "chromatic, unexpected"


# =============================================================================
# MAIN API
# =============================================================================

def generate_harmony(intent: Any) -> HarmonyResult:
    """
    Generate chord progression from song intent with modal interchange.

    This is the main entry point for harmony generation. It takes a
    CompleteSongIntent and returns a fully-analyzed HarmonyResult.

    Args:
        intent: CompleteSongIntent with technical_constraints containing:
            - technical_key: Key (e.g., "F")
            - technical_mode: Mode (e.g., "major")
            - technical_rule_to_break: Rule to break (e.g., "HARMONY_ModalInterchange")
            - rule_breaking_justification: Why break this rule

    Returns:
        HarmonyResult with progression, roman numerals, and diagnostics

    Example:
        >>> kelly_harmony = generate_harmony(kelly_intent)
        >>> print(kelly_harmony.progression_string)
        "F-C-Dm-Bbm"
        >>> print(kelly_harmony.diagnostics[3].emotional_function)
        "bittersweet darkness, borrowed sadness"
    """
    # Extract parameters from intent
    tc = intent.technical_constraints
    key = getattr(tc, 'technical_key', 'F')
    mode = getattr(tc, 'technical_mode', 'major')
    rule_to_break = getattr(tc, 'technical_rule_to_break', '')
    justification = getattr(tc, 'rule_breaking_justification', '')

    # Generate base progression
    chords = _generate_base_progression(key, mode)

    # Apply rule-breaking
    rule_effect = None
    if rule_to_break == 'HARMONY_ModalInterchange':
        chords = _apply_modal_interchange(chords, key, mode)
        rule_effect = RULE_EFFECTS.get(rule_to_break)
    elif rule_to_break == 'HARMONY_AvoidTonicResolution':
        # Replace last chord with V instead of I
        if chords:
            fifth_midi = (NOTE_TO_MIDI.get(key, 0) + SCALES['major'][4]) % 12
            chords[-1] = _midi_to_note(fifth_midi)
        rule_effect = RULE_EFFECTS.get(rule_to_break)

    # Analyze each chord
    diagnostics = []
    roman_numerals = []

    for chord in chords:
        roman, degree, is_diatonic, borrowed = _chord_to_roman(chord, key, mode)
        roman_numerals.append(roman)

        is_minor = 'm' in chord and chord != key
        emotional = _get_emotional_function(degree, is_diatonic, is_minor, mode)

        diag = HarmonyDiagnostic(
            symbol=chord,
            roman_numeral=roman,
            is_diatonic=is_diatonic,
            borrowed_from=borrowed,
            emotional_function=emotional
        )
        diagnostics.append(diag)

    # Determine overall character
    borrowed_count = sum(1 for d in diagnostics if not d.is_diatonic)
    if borrowed_count > 0:
        emotional_character = "complex, emotionally ambiguous with modal interchange"
    else:
        emotional_character = "diatonic, straightforward emotional arc"

    # Build result
    progression_string = '-'.join(chords)
    roman_progression = '-'.join(roman_numerals)

    return HarmonyResult(
        chords=chords,
        progression_string=progression_string,
        key=key,
        mode=mode,
        roman_numerals=roman_numerals,
        roman_progression=roman_progression,
        rule_break_applied=rule_to_break if rule_to_break else None,
        rule_break_effect=rule_effect,
        emotional_justification=justification if justification else None,
        diagnostics=diagnostics,
        emotional_character=emotional_character
    )


def diagnose_progression(
    progression: str,
    key: str = "C",
    mode: str = "major"
) -> Dict[str, Any]:
    """
    Diagnose an existing chord progression.

    Args:
        progression: Hyphen-separated chord string (e.g., "F-C-Dm-Bbm")
        key: Musical key
        mode: "major" or "minor"

    Returns:
        Dictionary with analysis results
    """
    chords = [c.strip() for c in progression.split('-')]

    diagnostics = []
    roman_numerals = []

    for chord in chords:
        roman, degree, is_diatonic, borrowed = _chord_to_roman(chord, key, mode)
        roman_numerals.append(roman)

        is_minor = 'm' in chord and chord != key
        emotional = _get_emotional_function(degree, is_diatonic, is_minor, mode)

        diagnostics.append({
            'chord': chord,
            'roman': roman,
            'is_diatonic': is_diatonic,
            'borrowed_from': borrowed,
            'emotional_function': emotional
        })

    return {
        'progression': progression,
        'key': key,
        'mode': mode,
        'roman_progression': '-'.join(roman_numerals),
        'diagnostics': diagnostics
    }


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == "__main__":
    # Test with mock intent
    from dataclasses import dataclass

    @dataclass
    class MockTechnicalConstraints:
        technical_key: str = "F"
        technical_mode: str = "major"
        technical_rule_to_break: str = "HARMONY_ModalInterchange"
        rule_breaking_justification: str = "Bbm makes hope feel earned and bittersweet; grief expressed through borrowed darkness"

    @dataclass
    class MockSongRoot:
        core_event: str = "Finding someone I loved after they chose to leave"
        core_resistance: str = "Fear of making it about me"
        core_longing: str = "To process grief without making it performative"
        core_stakes: str = "Her memory deserves honesty"
        core_transformation: str = "Accept that grief doesn't resolve neatly"

    @dataclass
    class MockSongIntent:
        mood_primary: str = "Grief"
        mood_secondary_tension: float = 0.3
        vulnerability_scale: str = "High"
        narrative_arc: str = "Slow Reveal"
        imagery_texture: str = "soft morning light, stillness"

    @dataclass
    class MockIntent:
        song_root: MockSongRoot
        song_intent: MockSongIntent
        technical_constraints: MockTechnicalConstraints

    # Create Kelly intent
    kelly_intent = MockIntent(
        song_root=MockSongRoot(),
        song_intent=MockSongIntent(),
        technical_constraints=MockTechnicalConstraints()
    )

    # Generate harmony
    print("=" * 70)
    print("KELLY SONG: generate_harmony(kelly_intent)")
    print("=" * 70)

    kelly_harmony = generate_harmony(kelly_intent)

    print(f"\nResult: {kelly_harmony.progression_string} with modal interchange")
    print(f"Roman: {kelly_harmony.roman_progression}")
    print(f"\nDiagnostics:")
    for d in kelly_harmony.diagnostics:
        status = "BORROWED" if not d.is_diatonic else "diatonic"
        print(f"  {d.symbol:6} ({d.roman_numeral:4}) - {status:10} - {d.emotional_function}")

    # Find the borrowed chord
    borrowed = [d for d in kelly_harmony.diagnostics if not d.is_diatonic]
    if borrowed:
        print(f"\nDiagnostics confirm: \"{borrowed[0].emotional_function}\" \u2713")

    print("\n" + "=" * 70)
