#!/usr/bin/env python3
"""
Kelly Song Example - Complete Workflow
Demonstrates harmony generation and diagnostic analysis for "When I Found You Sleeping"
"""

import sys
sys.path.insert(0, '/home/claude')

from harmony_generator import HarmonyGenerator, generate_midi_from_harmony
from chord_diagnostics import ChordDiagnostics, print_diagnostic_report
from dataclasses import dataclass


# ============================================================================
# INTENT DEFINITION (matches your three-phase schema)
# ============================================================================

@dataclass
class SongRoot:
    """Phase 0: Core Wound/Desire"""
    core_event: str
    core_resistance: str
    core_longing: str
    core_stakes: str = ""
    core_transformation: str = ""


@dataclass
class SongIntent:
    """Phase 1: Emotional Intent"""
    mood_primary: str
    mood_secondary_tension: float = 0.0
    vulnerability_scale: str = "medium"
    narrative_arc: str = "linear"
    imagery_texture: str = ""


@dataclass
class TechnicalConstraints:
    """Phase 2: Technical Implementation"""
    technical_key: str
    technical_mode: str = "major"
    technical_tempo: int = 82
    technical_genre: str = "lo-fi bedroom emo"
    technical_rule_to_break: str = ""
    rule_breaking_justification: str = ""


@dataclass
class CompleteSongIntent:
    """Complete three-phase intent"""
    song_root: SongRoot
    song_intent: SongIntent
    technical_constraints: TechnicalConstraints


# ============================================================================
# KELLY SONG INTENT
# ============================================================================

kelly_intent = CompleteSongIntent(
    song_root=SongRoot(
        core_event="Finding someone I loved after they chose to leave",
        core_resistance="Fear of making it about me, exploiting the loss",
        core_longing="To process grief without making it performative",
        core_stakes="Her memory deserves honesty, not poetry",
        core_transformation="Accept that grief doesn't resolve neatly"
    ),
    
    song_intent=SongIntent(
        mood_primary="Grief",
        mood_secondary_tension=0.3,  # Some nostalgia, some guilt
        vulnerability_scale="High",
        narrative_arc="Slow Reveal (sounds like love until final line)",
        imagery_texture="soft morning light, stillness, things left behind"
    ),
    
    technical_constraints=TechnicalConstraints(
        technical_key="F",
        technical_mode="major",
        technical_tempo=82,
        technical_genre="lo-fi bedroom emo / confessional acoustic",
        technical_rule_to_break="HARMONY_ModalInterchange",
        rule_breaking_justification="Bbm makes hope feel earned and bittersweet; "
                                   "grief expressed through borrowed darkness"
    )
)


# ============================================================================
# GENERATE HARMONY
# ============================================================================

def generate_kelly_harmony():
    """Generate Kelly song harmony from intent"""
    print("\n" + "=" * 70)
    print("GENERATING HARMONY FROM INTENT: When I Found You Sleeping")
    print("=" * 70)
    
    generator = HarmonyGenerator()
    
    # Generate from intent
    harmony = generator.generate_from_intent(kelly_intent)
    
    # Generate MIDI files
    generate_midi_from_harmony(
        harmony,
        "/mnt/user-data/outputs/kelly_song_harmony.mid",
        tempo_bpm=kelly_intent.technical_constraints.technical_tempo
    )
    
    print(f"\n✓ Key: {harmony.key} {harmony.mode}")
    print(f"✓ Progression: {' - '.join(harmony.chords)}")
    print(f"✓ Roman numerals: {' - '.join([v.roman_numeral for v in harmony.voicings if hasattr(v, 'roman_numeral') and v.roman_numeral])}")
    print(f"✓ Rule break: {harmony.rule_break_applied}")
    print(f"✓ Why: {harmony.emotional_justification}")
    print(f"✓ MIDI saved: /mnt/user-data/outputs/kelly_song_harmony.mid")
    
    return harmony


# ============================================================================
# DIAGNOSE PROGRESSION
# ============================================================================

def diagnose_kelly_progression():
    """Run diagnostic analysis on Kelly song progression"""
    print("\n" + "=" * 70)
    print("DIAGNOSTIC ANALYSIS")
    print("=" * 70)
    
    diagnostics = ChordDiagnostics()
    
    # Analyze the progression
    result = diagnostics.diagnose(
        "F-C-Bbm-F",
        key="F",
        mode="major"
    )
    
    print_diagnostic_report(result)
    
    return result


# ============================================================================
# COMPARE VARIATIONS
# ============================================================================

def generate_variations():
    """Generate alternative progressions for comparison"""
    print("\n" + "=" * 70)
    print("GENERATING VARIATIONS FOR COMPARISON")
    print("=" * 70)
    
    generator = HarmonyGenerator()
    
    # Variation 1: Diatonic (no modal interchange)
    diatonic = generator.generate_basic_progression("F", "major", "I-V-vi-IV")
    generate_midi_from_harmony(
        diatonic,
        "/mnt/user-data/outputs/kelly_diatonic_comparison.mid",
        tempo_bpm=82
    )
    print(f"\n✓ Diatonic version: {' - '.join(diatonic.chords)}")
    print(f"  (Standard pop progression, no rule-breaking)")
    
    # Variation 2: Avoid resolution (end on Dm instead of F)
    @dataclass
    class MockTechnicalConstraints:
        technical_key: str = "F"
        technical_mode: str = "major"
        technical_rule_to_break: str = "HARMONY_AvoidTonicResolution"
        rule_breaking_justification: str = "Ending on vi leaves yearning unresolved"
    
    @dataclass
    class MockIntent:
        technical_constraints: MockTechnicalConstraints
    
    avoid_intent = MockIntent(technical_constraints=MockTechnicalConstraints())
    
    # Manually create progression F-C-Bbm-Dm
    from chord_diagnostics import ChordAnalysis, ProgressionDiagnostic
    
    print(f"\n✓ Unresolved version: F - C - Bbm - Dm")
    print(f"  (Modal interchange + avoided resolution)")
    print(f"  (Even more grief - no return to home)")


# ============================================================================
# EMOTIONAL JUSTIFICATION BREAKDOWN
# ============================================================================

def explain_emotional_mapping():
    """Explain how emotional intent maps to harmonic choices"""
    print("\n" + "=" * 70)
    print("EMOTIONAL INTENT → HARMONIC CHOICES")
    print("=" * 70)
    
    print("\nCORE WOUND:")
    print(f"  '{kelly_intent.song_root.core_event}'")
    print(f"  → Grief as primary emotion")
    
    print("\nEMOTIONAL INTENT:")
    print(f"  Mood: {kelly_intent.song_intent.mood_primary}")
    print(f"  Vulnerability: {kelly_intent.song_intent.vulnerability_scale}")
    print(f"  → Needs complex, bittersweet harmony")
    
    print("\nTECHNICAL DECISION:")
    print(f"  Rule to break: {kelly_intent.technical_constraints.technical_rule_to_break}")
    print(f"  Why: {kelly_intent.technical_constraints.rule_breaking_justification}")
    
    print("\nRESULTING PROGRESSION:")
    print("  F (I)  - home, major key suggests hope")
    print("  C (V)  - dominant, movement away from home")
    print("  Bbm (iv) - BORROWED FROM F MINOR")
    print("             ↳ This is the grief speaking")
    print("             ↳ 'Bittersweet darkness, borrowed sadness'")
    print("             ↳ Hope doesn't come easy; it's earned through pain")
    print("  F (I)  - return home, but we've been changed")
    
    print("\nEMOTIONAL ARC:")
    print("  Verse 1-3: Sounds like falling in love (misdirection)")
    print("  Final line: Reveals it's grief")
    print("  Harmonic arc: Major context → borrowed darkness → return")
    print("              = 'Processing loss while maintaining hope'")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("=" * 70)
    print("KELLY SONG: 'When I Found You Sleeping'")
    print("Complete Workflow Demonstration")
    print("=" * 70)
    
    # Step 1: Generate harmony from intent
    harmony = generate_kelly_harmony()
    
    # Step 2: Diagnose the progression
    diagnostic = diagnose_kelly_progression()
    
    # Step 3: Generate comparison variations
    generate_variations()
    
    # Step 4: Explain emotional mapping
    explain_emotional_mapping()
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: Files Generated")
    print("=" * 70)
    print("\n✓ kelly_song_harmony.mid - Main progression with modal interchange")
    print("✓ kelly_diatonic_comparison.mid - Diatonic version for comparison")
    print("\nNext steps:")
    print("  1. Import MIDI into Logic Pro X")
    print("  2. Add fingerpicking guitar pattern")
    print("  3. Record vocals with intentional register breaks")
    print("  4. Keep lo-fi production aesthetic (imperfection = authenticity)")
    
    print("\n" + "=" * 70)
    print("'Interrogate Before Generate' - Mission Accomplished")
    print("=" * 70)
    print("\n")
