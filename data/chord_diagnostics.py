"""
Chord Diagnostics - Analyze and diagnose chord progressions

This module provides Roman numeral analysis, borrowed chord detection,
voice-leading diagnostics, and emotional function identification.

Philosophy: "Understanding the rules helps you break them with intention."
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ChordQuality(Enum):
    """Chord quality types"""
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    DOMINANT7 = "dominant7"
    MAJOR7 = "major7"
    MINOR7 = "minor7"


@dataclass
class ChordAnalysis:
    """Analysis result for a single chord"""
    symbol: str  # Original chord symbol (e.g., "Bbm")
    root: str  # Root note (e.g., "Bb")
    quality: ChordQuality
    roman_numeral: str  # e.g., "iv"
    scale_degree: int  # 0-6 (0=I, 1=ii, etc.)
    is_diatonic: bool  # True if in key, False if borrowed
    borrowed_from: Optional[str] = None  # e.g., "parallel minor"
    emotional_function: Optional[str] = None


@dataclass
class ProgressionDiagnostic:
    """Complete diagnostic of a chord progression"""
    progression_string: str  # Original input
    chords: List[str]  # Chord symbols
    key: str
    mode: str
    analyses: List[ChordAnalysis]
    roman_progression: str  # e.g., "I-V-vi-iv"
    rule_breaks: List[str]  # Detected rule violations
    emotional_character: str  # Overall emotional reading
    suggestions: List[str]  # Improvement/variation suggestions


class ChordDiagnostics:
    """
    Analyzes chord progressions for:
    - Roman numeral analysis
    - Borrowed chord detection
    - Rule-breaking identification
    - Emotional function analysis
    - Reharmonization suggestions
    """
    
    # MIDI note numbers for chord root detection
    NOTE_TO_MIDI = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
        'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }
    
    # Scale intervals
    SCALES = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'natural_minor': [0, 2, 3, 5, 7, 8, 10],
        'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
    }
    
    # Diatonic chord qualities in major and minor
    MAJOR_DIATONIC_QUALITIES = ['maj', 'min', 'min', 'maj', 'maj', 'min', 'dim']
    MINOR_DIATONIC_QUALITIES = ['min', 'dim', 'maj', 'min', 'min', 'maj', 'maj']
    
    # Roman numerals
    MAJOR_ROMAN = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']
    MINOR_ROMAN = ['i', 'ii°', 'III', 'iv', 'v', 'VI', 'VII']
    
    # Emotional associations for common progressions
    EMOTIONAL_PATTERNS = {
        'I-V-vi-IV': 'hopeful, pop ballad energy',
        'I-IV-V-IV': 'triumphant, anthemic',
        'i-VI-III-VII': 'dark, descending tragedy',
        'I-V-vi-iii-IV-I-IV-V': 'Axis of Awesome, everything sounds like this',
        'I-vi-IV-V': '50s progression, nostalgic doo-wop',
        'i-VII-VI-V': 'Andalusian cadence, mysterious descent',
    }
    
    def __init__(self):
        """Initialize chord diagnostics"""
        pass
    
    def diagnose(
        self,
        progression_string: str,
        key: str = "C",
        mode: str = "major"
    ) -> ProgressionDiagnostic:
        """
        Main diagnostic function - analyzes a chord progression.
        
        Args:
            progression_string: Chord progression (e.g., "F-C-Am-Dm" or "I-V-vi-IV")
            key: Musical key (default "C")
            mode: "major" or "minor" (default "major")
            
        Returns:
            ProgressionDiagnostic with complete analysis
            
        Example:
            >>> diag = ChordDiagnostics()
            >>> result = diag.diagnose("F-C-Bbm-F", key="F", mode="major")
            >>> print(result.roman_progression)  # "I-V-iv-I"
        """
        # Clean key notation (strip 'm' if present, e.g., "Am" -> "A")
        clean_key = key.rstrip('m')
        
        # Parse chord progression
        if self._is_roman_numeral_progression(progression_string):
            chords = self._roman_to_chords(progression_string, clean_key, mode)
        else:
            chords = [c.strip() for c in progression_string.split('-')]
        
        # Analyze each chord
        analyses = []
        for chord in chords:
            analysis = self._analyze_chord(chord, clean_key, mode)
            analyses.append(analysis)
        
        # Build Roman numeral progression string
        roman_progression = '-'.join([a.roman_numeral for a in analyses])
        
        # Detect rule breaks
        rule_breaks = self._detect_rule_breaks(analyses, chords)
        
        # Determine emotional character
        emotional_character = self._determine_emotional_character(
            analyses, roman_progression
        )
        
        # Generate suggestions
        suggestions = self._generate_suggestions(analyses, clean_key, mode, rule_breaks)
        
        return ProgressionDiagnostic(
            progression_string=progression_string,
            chords=chords,
            key=clean_key,
            mode=mode,
            analyses=analyses,
            roman_progression=roman_progression,
            rule_breaks=rule_breaks,
            emotional_character=emotional_character,
            suggestions=suggestions
        )
    
    def _is_roman_numeral_progression(self, prog: str) -> bool:
        """Check if string is Roman numerals vs chord symbols"""
        # Simple check: if it contains 'I', 'V', 'i', 'v', it's probably Roman
        return any(numeral in prog for numeral in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'i', 'v'])
    
    def _roman_to_chords(self, roman_prog: str, key: str, mode: str) -> List[str]:
        """Convert Roman numeral progression to chord symbols"""
        # Use the harmony generator's logic
        from harmony_generator import HarmonyGenerator
        gen = HarmonyGenerator()
        roman_list = roman_prog.split('-')
        # Strip 'm' from key if present (e.g., "Am" -> "A")
        clean_key = key.rstrip('m')
        return gen._roman_to_chord_symbols(roman_list, clean_key, mode)
    
    def _parse_chord_symbol(self, chord: str) -> Tuple[str, ChordQuality]:
        """
        Parse chord symbol to extract root and quality.
        
        Returns:
            Tuple of (root_note, quality_enum)
        """
        chord = chord.strip()
        
        # Extract root (handle sharps/flats)
        if len(chord) > 1 and chord[1] in ['#', 'b']:
            root = chord[:2]
            quality_str = chord[2:]
        else:
            root = chord[0]
            quality_str = chord[1:]
        
        # Determine quality
        if quality_str == '' or quality_str.upper() == 'MAJ':
            quality = ChordQuality.MAJOR
        elif quality_str == 'm' or quality_str.upper() == 'MIN':
            quality = ChordQuality.MINOR
        elif quality_str == 'dim' or quality_str == '°':
            quality = ChordQuality.DIMINISHED
        elif quality_str == 'aug' or quality_str == '+':
            quality = ChordQuality.AUGMENTED
        elif quality_str == '7':
            quality = ChordQuality.DOMINANT7
        elif quality_str == 'maj7' or quality_str == 'M7':
            quality = ChordQuality.MAJOR7
        elif quality_str == 'm7':
            quality = ChordQuality.MINOR7
        else:
            quality = ChordQuality.MAJOR  # Default
        
        return root, quality
    
    def _analyze_chord(
        self,
        chord_symbol: str,
        key: str,
        mode: str
    ) -> ChordAnalysis:
        """Analyze a single chord in context of key"""
        root, quality = self._parse_chord_symbol(chord_symbol)
        
        # Calculate scale degree
        key_midi = self.NOTE_TO_MIDI[key]
        root_midi = self.NOTE_TO_MIDI[root]
        semitones_from_root = (root_midi - key_midi) % 12
        
        # Find which scale degree this is
        scale = self.SCALES['major'] if mode == 'major' else self.SCALES['natural_minor']
        
        try:
            scale_degree = scale.index(semitones_from_root)
        except ValueError:
            # Not in scale - it's chromatic
            scale_degree = -1
        
        # Determine if diatonic
        is_diatonic, borrowed_from = self._check_diatonic(
            scale_degree, quality, mode
        )
        
        # Get Roman numeral
        if scale_degree >= 0:
            if mode == 'major':
                roman_numeral = self.MAJOR_ROMAN[scale_degree]
                expected_quality = self.MAJOR_DIATONIC_QUALITIES[scale_degree]
            else:
                roman_numeral = self.MINOR_ROMAN[scale_degree]
                expected_quality = self.MINOR_DIATONIC_QUALITIES[scale_degree]
            
            # Adjust Roman numeral if quality doesn't match
            if not is_diatonic:
                roman_numeral = self._adjust_roman_for_borrowed(
                    roman_numeral, quality, expected_quality
                )
        else:
            # Chromatic chord
            roman_numeral = f"♭{self._semitones_to_degree(semitones_from_root)}"
            is_diatonic = False
            borrowed_from = "chromatic"
        
        # Determine emotional function
        emotional_function = self._get_emotional_function(
            scale_degree, quality, is_diatonic, mode
        )
        
        return ChordAnalysis(
            symbol=chord_symbol,
            root=root,
            quality=quality,
            roman_numeral=roman_numeral,
            scale_degree=scale_degree,
            is_diatonic=is_diatonic,
            borrowed_from=borrowed_from,
            emotional_function=emotional_function
        )
    
    def _check_diatonic(
        self,
        scale_degree: int,
        quality: ChordQuality,
        mode: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if chord quality matches diatonic expectation.
        
        Returns:
            Tuple of (is_diatonic, borrowed_from_description)
        """
        if scale_degree < 0 or scale_degree >= 7:
            return False, "chromatic"
        
        if mode == 'major':
            expected = self.MAJOR_DIATONIC_QUALITIES[scale_degree]
        else:
            expected = self.MINOR_DIATONIC_QUALITIES[scale_degree]
        
        # Match quality to expected
        quality_str = self._quality_to_string(quality)
        
        if quality_str == expected:
            return True, None
        else:
            # It's borrowed
            if mode == 'major':
                return False, "parallel minor (modal interchange)"
            else:
                return False, "parallel major (modal interchange)"
    
    def _quality_to_string(self, quality: ChordQuality) -> str:
        """Convert ChordQuality enum to expected string"""
        if quality == ChordQuality.MAJOR:
            return 'maj'
        elif quality == ChordQuality.MINOR:
            return 'min'
        elif quality == ChordQuality.DIMINISHED:
            return 'dim'
        elif quality == ChordQuality.AUGMENTED:
            return 'aug'
        else:
            return 'maj'  # Default for 7ths
    
    def _adjust_roman_for_borrowed(
        self,
        roman: str,
        actual_quality: ChordQuality,
        expected_quality: str
    ) -> str:
        """
        Adjust Roman numeral notation for borrowed chords.
        
        Example: iv in major key (borrowed from minor) stays as 'iv'
        """
        # If minor when should be major, use lowercase
        if actual_quality == ChordQuality.MINOR and expected_quality == 'maj':
            return roman.lower()
        # If major when should be minor, use uppercase
        elif actual_quality == ChordQuality.MAJOR and expected_quality == 'min':
            return roman.upper()
        else:
            return roman
    
    def _semitones_to_degree(self, semitones: int) -> str:
        """Convert semitones to scale degree notation"""
        degrees = ['I', '♭II', 'II', '♭III', 'III', 'IV', '♭V', 'V', '♭VI', 'VI', '♭VII', 'VII']
        return degrees[semitones % 12]
    
    def _get_emotional_function(
        self,
        scale_degree: int,
        quality: ChordQuality,
        is_diatonic: bool,
        mode: str
    ) -> str:
        """Determine emotional function of chord in context"""
        if not is_diatonic:
            if quality == ChordQuality.MINOR:
                return "bittersweet darkness, borrowed sadness"
            else:
                return "unexpected light, borrowed brightness"
        
        # Diatonic functions
        if mode == 'major':
            functions = [
                'home, resolution',  # I
                'preparation, subdominant minor feel',  # ii
                'mediant, bridge to relative minor',  # iii
                'subdominant, away from home',  # IV
                'dominant, tension seeking resolution',  # V
                'relative minor, melancholy',  # vi
                'leading tone diminished, unstable'  # vii°
            ]
        else:
            functions = [
                'home, minor tonic',  # i
                'diminished supertonic, tension',  # ii°
                'relative major, hopeful',  # III
                'subdominant, darker preparation',  # iv
                'minor dominant, softer tension',  # v
                'submediant major, brighter color',  # VI
                'subtonic major, modal flavor'  # VII
            ]
        
        if 0 <= scale_degree < len(functions):
            return functions[scale_degree]
        
        return "chromatic, unexpected"
    
    def _detect_rule_breaks(
        self,
        analyses: List[ChordAnalysis],
        chords: List[str]
    ) -> List[str]:
        """Detect rule-breaking patterns in the progression"""
        rule_breaks = []
        
        # Check for borrowed chords (modal interchange)
        borrowed_chords = [a for a in analyses if not a.is_diatonic and a.borrowed_from]
        if borrowed_chords:
            borrowed_info = ', '.join([
                f"{a.symbol} ({a.roman_numeral})" for a in borrowed_chords
            ])
            rule_breaks.append(
                f"HARMONY_ModalInterchange: {borrowed_info} - {borrowed_chords[0].borrowed_from}"
            )
        
        # Check for unresolved progressions (doesn't end on I)
        if len(analyses) > 0:
            last_chord = analyses[-1]
            if last_chord.scale_degree != 0:
                rule_breaks.append(
                    f"HARMONY_AvoidTonicResolution: Ends on {last_chord.roman_numeral} instead of tonic"
                )
        
        # Check for parallel motion (would need voice-leading analysis)
        # For now, detect power chord indicators
        if all('5' in c or len(c) <= 2 for c in chords):
            rule_breaks.append(
                "HARMONY_ParallelMotion: Power chords (parallel fifths)"
            )
        
        return rule_breaks
    
    def _determine_emotional_character(
        self,
        analyses: List[ChordAnalysis],
        roman_progression: str
    ) -> str:
        """Determine overall emotional character of progression"""
        # Check for known emotional patterns
        for pattern, emotion in self.EMOTIONAL_PATTERNS.items():
            if pattern == roman_progression:
                return emotion
        
        # Analyze based on borrowed chords and functions
        borrowed_count = sum(1 for a in analyses if not a.is_diatonic)
        
        if borrowed_count > 0:
            return "complex, emotionally ambiguous with modal interchange"
        elif all(a.is_diatonic for a in analyses):
            return "diatonic, straightforward emotional arc"
        else:
            return "chromatic, adventurous harmony"
    
    def _generate_suggestions(
        self,
        analyses: List[ChordAnalysis],
        key: str,
        mode: str,
        rule_breaks: List[str]
    ) -> List[str]:
        """Generate suggestions for variations or improvements"""
        suggestions = []
        
        # Suggest modal interchange if not present
        if not any('ModalInterchange' in rb for rb in rule_breaks):
            if mode == 'major':
                suggestions.append(
                    "Try modal interchange: Replace IV with iv for bittersweet color"
                )
            else:
                suggestions.append(
                    "Try modal interchange: Replace VI with ♭VI for darker descent"
                )
        
        # Suggest resolution alternatives
        if analyses and analyses[-1].scale_degree == 0:
            suggestions.append(
                "Try avoiding resolution: End on V or vi for unresolved yearning"
            )
        
        # Suggest reharmonizations
        roman_prog = '-'.join([a.roman_numeral for a in analyses])
        if roman_prog == 'I-V-vi-IV':
            suggestions.append(
                "Classic pop progression. Try: I-V-vi-iii-IV-I-IV-V (Axis of Awesome)"
            )
        
        return suggestions


def print_diagnostic_report(diagnostic: ProgressionDiagnostic):
    """Pretty-print a diagnostic report"""
    print("=" * 70)
    print(f"CHORD PROGRESSION DIAGNOSTIC")
    print("=" * 70)
    print(f"\nProgression: {diagnostic.progression_string}")
    print(f"Key: {diagnostic.key} {diagnostic.mode}")
    print(f"Roman Numerals: {diagnostic.roman_progression}")
    print(f"\nEmotional Character: {diagnostic.emotional_character}")
    
    print(f"\n{'CHORD':<10} {'ROMAN':<10} {'DIATONIC':<10} {'EMOTIONAL FUNCTION'}")
    print("-" * 70)
    
    for analysis in diagnostic.analyses:
        diatonic_str = "✓" if analysis.is_diatonic else f"✗ ({analysis.borrowed_from})"
        print(f"{analysis.symbol:<10} {analysis.roman_numeral:<10} {diatonic_str:<10} {analysis.emotional_function}")
    
    if diagnostic.rule_breaks:
        print(f"\nRULE BREAKS DETECTED:")
        for rb in diagnostic.rule_breaks:
            print(f"  • {rb}")
    
    if diagnostic.suggestions:
        print(f"\nSUGGESTIONS:")
        for suggestion in diagnostic.suggestions:
            print(f"  → {suggestion}")
    
    print("=" * 70)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    diagnostics = ChordDiagnostics()
    
    # Example 1: Kelly song (F-C-Bbm-F)
    print("\n")
    kelly_diag = diagnostics.diagnose("F-C-Bbm-F", key="F", mode="major")
    print_diagnostic_report(kelly_diag)
    
    # Example 2: Classic I-V-vi-IV
    print("\n")
    classic_diag = diagnostics.diagnose("C-G-Am-F", key="C", mode="major")
    print_diagnostic_report(classic_diag)
    
    # Example 3: Radiohead "Creep" (G-B-C-Cm)
    print("\n")
    creep_diag = diagnostics.diagnose("G-B-C-Cm", key="G", mode="major")
    print_diagnostic_report(creep_diag)
    
    # Example 4: From Roman numerals
    print("\n")
    roman_diag = diagnostics.diagnose("i-VI-III-VII", key="Am", mode="minor")
    print_diagnostic_report(roman_diag)
