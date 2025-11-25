"""
Progression Analysis - Diagnose and reharmonize chord progressions.

Tools for:
- Parsing chord progression strings
- Diagnosing harmonic issues
- Generating reharmonization suggestions
- Modal interchange analysis
"""

from typing import List, Dict, Optional, Tuple
import re
from dataclasses import dataclass


# Note mappings
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
FLAT_TO_SHARP = {
    'Db': 'C#', 'Eb': 'D#', 'Fb': 'E', 'Gb': 'F#', 
    'Ab': 'G#', 'Bb': 'A#', 'Cb': 'B'
}

# Scale degrees for common modes
MODES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'lydian': [0, 2, 4, 6, 7, 9, 11],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'locrian': [0, 1, 3, 5, 6, 8, 10],
}

# Common substitution patterns
SUBSTITUTIONS = {
    'tritone': {
        'description': 'Replace V7 with bII7 (tritone sub)',
        'original': 'V7',
        'replacement': 'bII7',
    },
    'relative_minor': {
        'description': 'Replace I with vi',
        'original': 'I',
        'replacement': 'vi',
    },
    'backdoor': {
        'description': 'Replace V7 with bVII7',
        'original': 'V7',
        'replacement': 'bVII7',
    },
    'secondary_dominant': {
        'description': 'Add V/V before V',
        'original': 'V',
        'insertion': 'II7',
    },
}

# Reharmonization techniques by style
REHARM_TECHNIQUES = {
    'jazz': [
        'tritone_substitution',
        'chromatic_approach',
        'secondary_dominants',
        'diminished_passing',
        'coltrane_changes',
    ],
    'pop': [
        'borrowed_from_parallel',
        'pedal_point',
        'sus_chords',
        'add9_extensions',
    ],
    'rnb': [
        'extended_dominants',
        'neo_soul_voicings',
        'minor_9_substitution',
        'chromatic_mediants',
    ],
    'classical': [
        'voice_leading_optimization',
        'secondary_function',
        'augmented_sixth',
        'neapolitan',
    ],
    'experimental': [
        'parallel_motion',
        'polytonality',
        'quartal_voicings',
        'planing',
    ],
}


@dataclass
class ParsedChord:
    """Parsed chord with root, quality, and extensions."""
    root: str
    root_num: int  # 0-11
    quality: str  # 'maj', 'min', 'dim', 'aug', '7', etc.
    extensions: List[str]
    bass: Optional[str] = None
    original: str = ""


def parse_chord(chord_str: str) -> Optional[ParsedChord]:
    """
    Parse a chord string into components.
    
    Examples: "Am7", "F#dim", "Cmaj7", "G/B", "Dm9"
    """
    chord_str = chord_str.strip()
    if not chord_str:
        return None
    
    # Handle slash chords
    bass = None
    if '/' in chord_str:
        parts = chord_str.split('/')
        chord_str = parts[0]
        bass = parts[1] if len(parts) > 1 else None
    
    # Extract root
    root_match = re.match(r'^([A-Ga-g][#b]?)', chord_str)
    if not root_match:
        return None
    
    root = root_match.group(1).capitalize()
    remainder = chord_str[len(root_match.group(1)):]
    
    # Normalize flats to sharps
    if root in FLAT_TO_SHARP:
        root = FLAT_TO_SHARP[root]
    
    # Get root number
    try:
        root_num = NOTE_NAMES.index(root)
    except ValueError:
        return None
    
    # Parse quality and extensions
    quality = 'maj'  # Default
    extensions = []

    # Check for major 7th first (before minor check, since 'maj' starts with 'm')
    if remainder.startswith(('maj7', 'Maj7', 'M7')):
        quality = 'maj7'
        if remainder.startswith(('maj7', 'Maj7')):
            remainder = remainder[4:]
        else:
            remainder = remainder[2:]
    elif remainder.startswith('maj'):
        quality = 'maj'
        remainder = remainder[3:]
    # Check for minor variations
    elif remainder.startswith(('min', '-')):
        quality = 'min'
        remainder = re.sub(r'^(min|-)', '', remainder)
    elif remainder.lower().startswith('m') and not remainder.lower().startswith('maj'):
        # Single 'm' for minor, but not 'maj'
        quality = 'min'
        remainder = remainder[1:]
    elif remainder.startswith(('dim', '°', 'o')):
        quality = 'dim'
        remainder = re.sub(r'^(dim|°|o)', '', remainder)
    elif remainder.startswith(('+', 'aug')):
        quality = 'aug'
        remainder = re.sub(r'^(\+|aug)', '', remainder)
    elif remainder.startswith('sus'):
        sus_match = re.match(r'sus([24])?', remainder)
        if sus_match:
            quality = f"sus{sus_match.group(1) or '4'}"
            remainder = remainder[len(sus_match.group(0)):]
    
    # Parse extensions (7, 9, 11, 13, add, etc.)
    ext_match = re.findall(r'(maj7|M7|7|9|11|13|add\d+|b\d+|#\d+)', remainder)
    if ext_match:
        # Handle maj7 vs dominant 7
        if 'maj7' in ext_match or 'M7' in ext_match:
            quality = 'maj7' if quality == 'maj' else f'{quality}maj7'
        elif '7' in ext_match:
            if quality == 'maj':
                quality = '7'  # Dominant
            elif quality == 'min':
                quality = 'min7'
            elif quality == 'dim':
                quality = 'dim7'
        
        extensions = [e for e in ext_match if e not in ('7', 'maj7', 'M7')]
    
    return ParsedChord(
        root=root,
        root_num=root_num,
        quality=quality,
        extensions=extensions,
        bass=bass,
        original=chord_str + (f'/{bass}' if bass else ''),
    )


def parse_progression_string(progression: str) -> List[ParsedChord]:
    """
    Parse a progression string like "F-C-Am-Dm" or "F C Am Dm".
    
    Returns list of ParsedChord objects.
    """
    # Split by common delimiters
    chords = re.split(r'[-–—\s|,]+', progression)
    
    parsed = []
    for chord_str in chords:
        chord_str = chord_str.strip()
        if chord_str:
            parsed_chord = parse_chord(chord_str)
            if parsed_chord:
                parsed.append(parsed_chord)
    
    return parsed


def detect_key_from_progression(chords: List[ParsedChord]) -> Tuple[str, str]:
    """
    Detect key from parsed chord progression.
    
    Returns (key, mode) tuple.
    """
    if not chords:
        return ('C', 'major')
    
    # Weight first and last chords more heavily
    root_weights = {}
    for i, chord in enumerate(chords):
        weight = 1.0
        if i == 0:
            weight = 2.0  # First chord most likely tonic
        elif i == len(chords) - 1:
            weight = 1.5
        
        root_weights[chord.root_num] = root_weights.get(chord.root_num, 0) + weight
    
    # Find most weighted root
    likely_root = max(root_weights, key=root_weights.get)
    
    # Determine mode based on chord qualities at tonic
    mode = 'major'
    for chord in chords:
        if chord.root_num == likely_root:
            if chord.quality in ['min', 'min7', 'min9']:
                mode = 'minor'
                break
    
    return (NOTE_NAMES[likely_root], mode)


def diagnose_progression(progression: str) -> Dict:
    """
    Diagnose potential issues in a chord progression.
    
    Args:
        progression: Chord progression string (e.g., "F-C-Am-Dm")
    
    Returns:
        Dict with key, mode, issues, suggestions
    """
    chords = parse_progression_string(progression)
    
    if not chords:
        return {
            'key': 'unknown',
            'mode': 'unknown',
            'issues': ['Could not parse chord progression'],
            'suggestions': ['Check chord spelling'],
            'chords': [],
        }
    
    # Detect key
    key, mode = detect_key_from_progression(chords)
    key_num = NOTE_NAMES.index(key)
    
    issues = []
    suggestions = []
    
    # Analyze each chord
    scale = MODES.get(mode, MODES['major'])
    
    for i, chord in enumerate(chords):
        interval = (chord.root_num - key_num) % 12
        
        # Check if chord root is diatonic
        if interval not in scale:
            if interval == 3 and mode == 'major':
                issues.append(f"{chord.original}: bIII (borrowed from parallel minor)")
            elif interval == 8 and mode == 'major':
                issues.append(f"{chord.original}: bVI (borrowed from parallel minor)")  
            elif interval == 10 and mode == 'major':
                issues.append(f"{chord.original}: bVII (borrowed/mixolydian)")
            else:
                issues.append(f"{chord.original}: non-diatonic root ({NOTE_NAMES[interval]} in {key} {mode})")
        
        # Check for awkward voice leading (parallel root motion)
        if i > 0:
            prev_chord = chords[i - 1]
            root_motion = (chord.root_num - prev_chord.root_num) % 12
            if root_motion == 6:  # Tritone motion
                suggestions.append(f"Tritone motion between {prev_chord.original} and {chord.original} - can feel unstable")
    
    # Check for resolution
    last_chord = chords[-1]
    last_interval = (last_chord.root_num - key_num) % 12
    if last_interval not in [0, 7]:  # Not tonic or dominant
        suggestions.append(f"Progression ends on {last_chord.original} - consider resolving to {key}")
    
    # Check for missing V-I
    has_dominant = any((c.root_num - key_num) % 12 == 7 for c in chords)
    has_tonic = any((c.root_num - key_num) % 12 == 0 for c in chords)
    if not has_dominant and has_tonic:
        suggestions.append("No dominant (V) chord - consider adding for stronger resolution")
    
    return {
        'key': key,
        'mode': mode,
        'issues': issues if issues else [],
        'suggestions': suggestions,
        'chords': [c.original for c in chords],
    }


def generate_reharmonizations(
    progression: str,
    style: str = 'jazz',
    count: int = 3,
) -> List[Dict]:
    """
    Generate reharmonization suggestions for a progression.
    
    Args:
        progression: Original progression string
        style: Reharmonization style (jazz, pop, rnb, classical, experimental)
        count: Number of suggestions to generate
    
    Returns:
        List of reharmonization suggestions with chords, technique, and mood
    """
    chords = parse_progression_string(progression)
    
    if not chords:
        return []
    
    key, mode = detect_key_from_progression(chords)
    key_num = NOTE_NAMES.index(key)
    
    suggestions = []
    techniques = REHARM_TECHNIQUES.get(style, REHARM_TECHNIQUES['jazz'])
    
    # Generate suggestions based on style
    for i, technique in enumerate(techniques[:count]):
        new_chords = []
        mood = "enhanced"
        
        if technique == 'tritone_substitution':
            # Replace dominant chords with tritone subs
            for chord in chords:
                interval = (chord.root_num - key_num) % 12
                if interval == 7 and '7' in chord.quality:
                    # Tritone sub
                    new_root = (chord.root_num + 6) % 12
                    new_chords.append(f"{NOTE_NAMES[new_root]}7")
                else:
                    new_chords.append(chord.original)
            mood = "chromatic, sophisticated"
        
        elif technique == 'chromatic_approach':
            # Add chromatic approach chords
            new_chords = []
            for j, chord in enumerate(chords):
                if j > 0 and j < len(chords) - 1:
                    # Add approach chord a half-step above
                    approach_root = (chord.root_num + 1) % 12
                    new_chords.append(f"{NOTE_NAMES[approach_root]}7")
                new_chords.append(chord.original)
            mood = "tense, sophisticated"
        
        elif technique == 'borrowed_from_parallel':
            # Borrow chords from parallel mode
            for chord in chords:
                interval = (chord.root_num - key_num) % 12
                if interval == 5 and chord.quality == 'maj':
                    # IV -> iv
                    new_chords.append(f"{chord.root}m")
                elif interval == 0 and mode == 'major':
                    # Sometimes replace I with I7
                    new_chords.append(f"{chord.root}maj7")
                else:
                    new_chords.append(chord.original)
            mood = "bittersweet, nostalgic"
        
        elif technique == 'secondary_dominants':
            # Add secondary dominants
            for j, chord in enumerate(chords):
                if j < len(chords) - 1:
                    next_chord = chords[j + 1]
                    # Add V7 of next chord
                    sec_dom_root = (next_chord.root_num + 7) % 12
                    if (chord.root_num - key_num) % 12 != 7:  # Don't replace existing V
                        new_chords.append(f"{NOTE_NAMES[sec_dom_root]}7")
                new_chords.append(chord.original)
            mood = "driving, forward-moving"
        
        elif technique == 'pedal_point':
            # Add pedal bass
            for chord in chords:
                new_chords.append(f"{chord.original}/{key}")
            mood = "grounded, hypnotic"
        
        elif technique == 'sus_chords':
            # Replace some chords with sus variants
            for chord in chords:
                if chord.quality == 'maj':
                    new_chords.append(f"{chord.root}sus4")
                elif chord.quality == 'min':
                    new_chords.append(f"{chord.root}sus2")
                else:
                    new_chords.append(chord.original)
            mood = "open, unresolved"
        
        elif technique == 'extended_dominants':
            # Add extensions to dominant chords
            for chord in chords:
                interval = (chord.root_num - key_num) % 12
                if interval == 7:
                    new_chords.append(f"{chord.root}13")
                elif chord.quality == 'min7':
                    new_chords.append(f"{chord.root}m9")
                else:
                    new_chords.append(chord.original)
            mood = "lush, sophisticated"
        
        elif technique == 'parallel_motion':
            # Move all chords in parallel
            shift = 5  # Perfect 4th
            for chord in chords:
                new_root = (chord.root_num + shift) % 12
                new_chords.append(f"{NOTE_NAMES[new_root]}{chord.quality}")
            mood = "ethereal, impressionistic"
        
        elif technique == 'quartal_voicings':
            # Convert to quartal harmonies
            for chord in chords:
                new_chords.append(f"{chord.root}sus4(add9)")
            mood = "modern, open"
        
        else:
            # Default - return original with extensions
            for chord in chords:
                if 'maj' not in chord.quality and '7' not in chord.quality:
                    new_chords.append(f"{chord.original}7")
                else:
                    new_chords.append(chord.original)
            mood = "richer"
        
        if new_chords:
            suggestions.append({
                'chords': new_chords,
                'technique': technique.replace('_', ' ').title(),
                'mood': mood,
            })
    
    return suggestions[:count]
