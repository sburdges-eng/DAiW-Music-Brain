/**
 * test_harmony.cpp - Unit tests for Harmony Engine
 */

#include <gtest/gtest.h>
#include "harmony/HarmonyEngine.h"
#include "harmony/Chord.h"
#include "harmony/Progression.h"

using namespace iDAW::harmony;

// ============================================================================
// Chord Tests
// ============================================================================

class ChordTest : public ::testing::Test {
protected:
    HarmonyEngine& engine = HarmonyEngine::getInstance();
};

TEST_F(ChordTest, ChordFromMidiNotes_CMajor) {
    std::vector<int> notes = {60, 64, 67};  // C4, E4, G4
    Chord chord = detectChord(notes);
    
    EXPECT_TRUE(chord.isValid());
    EXPECT_EQ(chord.root(), 0);  // C
    EXPECT_EQ(chord.quality(), ChordQuality::Major);
    EXPECT_EQ(chord.name(), "C");
}

TEST_F(ChordTest, ChordFromMidiNotes_AMinor) {
    std::vector<int> notes = {57, 60, 64};  // A3, C4, E4
    Chord chord = detectChord(notes);
    
    EXPECT_TRUE(chord.isValid());
    EXPECT_EQ(chord.root(), 9);  // A
    EXPECT_EQ(chord.quality(), ChordQuality::Minor);
    EXPECT_EQ(chord.name(), "Am");
}

TEST_F(ChordTest, ChordFromMidiNotes_Dominant7) {
    std::vector<int> notes = {55, 59, 62, 65};  // G3, B3, D4, F4
    Chord chord = detectChord(notes);
    
    EXPECT_TRUE(chord.isValid());
    EXPECT_EQ(chord.root(), 7);  // G
    EXPECT_EQ(chord.quality(), ChordQuality::Dominant7);
}

TEST_F(ChordTest, ChordFromString_Am) {
    auto chord = Chord::fromString("Am");
    ASSERT_TRUE(chord.has_value());
    EXPECT_EQ(chord->root(), 9);
    EXPECT_EQ(chord->quality(), ChordQuality::Minor);
}

TEST_F(ChordTest, ChordFromString_FSharpDim) {
    auto chord = Chord::fromString("F#dim");
    ASSERT_TRUE(chord.has_value());
    EXPECT_EQ(chord->root(), 6);
    EXPECT_EQ(chord->quality(), ChordQuality::Diminished);
}

TEST_F(ChordTest, ChordFromString_CMaj7) {
    auto chord = Chord::fromString("Cmaj7");
    ASSERT_TRUE(chord.has_value());
    EXPECT_EQ(chord->root(), 0);
    EXPECT_EQ(chord->quality(), ChordQuality::Major7);
}

TEST_F(ChordTest, ChordFromString_SlashChord) {
    auto chord = Chord::fromString("Am/E");
    ASSERT_TRUE(chord.has_value());
    EXPECT_EQ(chord->root(), 9);
    EXPECT_EQ(chord->quality(), ChordQuality::Minor);
    EXPECT_TRUE(chord->hasBass());
    EXPECT_EQ(chord->bass(), 4);  // E
}

TEST_F(ChordTest, ChordName) {
    Chord cmaj(0, ChordQuality::Major);
    EXPECT_EQ(cmaj.name(), "C");
    
    Chord amin(9, ChordQuality::Minor);
    EXPECT_EQ(amin.name(), "Am");
    
    Chord fsharp7(6, ChordQuality::Dominant7);
    EXPECT_EQ(fsharp7.name(), "F#7");
}

TEST_F(ChordTest, ChordMidiNotes) {
    Chord cmaj(0, ChordQuality::Major);
    auto notes = cmaj.midiNotes(4);
    
    EXPECT_EQ(notes.size(), 3);
    EXPECT_EQ(notes[0], 60);  // C4
    EXPECT_EQ(notes[1], 64);  // E4
    EXPECT_EQ(notes[2], 67);  // G4
}

// ============================================================================
// Progression Tests
// ============================================================================

class ProgressionTest : public ::testing::Test {
protected:
    HarmonyEngine& engine = HarmonyEngine::getInstance();
};

TEST_F(ProgressionTest, ParseProgression_FCAmDm) {
    auto prog = Progression::fromString("F-C-Am-Dm");
    ASSERT_TRUE(prog.has_value());
    
    EXPECT_EQ(prog->size(), 4);
    EXPECT_EQ(prog->at(0).name(), "F");
    EXPECT_EQ(prog->at(1).name(), "C");
    EXPECT_EQ(prog->at(2).name(), "Am");
    EXPECT_EQ(prog->at(3).name(), "Dm");
}

TEST_F(ProgressionTest, ParseProgression_SpaceSeparated) {
    auto prog = Progression::fromString("G D Em C");
    ASSERT_TRUE(prog.has_value());
    
    EXPECT_EQ(prog->size(), 4);
    EXPECT_EQ(prog->at(0).name(), "G");
}

TEST_F(ProgressionTest, DetectKey_FMajor) {
    auto prog = Progression::fromString("F-C-Am-Dm");
    ASSERT_TRUE(prog.has_value());
    
    Key key = prog->detectKey();
    EXPECT_EQ(key.root, 5);  // F
    EXPECT_EQ(key.mode, Mode::Major);
}

TEST_F(ProgressionTest, DetectKey_AMinor) {
    auto prog = Progression::fromString("Am-Dm-E-Am");
    ASSERT_TRUE(prog.has_value());
    
    Key key = prog->detectKey();
    EXPECT_EQ(key.root, 9);  // A
    EXPECT_EQ(key.mode, Mode::Minor);
}

TEST_F(ProgressionTest, RomanNumerals) {
    auto prog = Progression::fromString("C-Am-F-G");
    ASSERT_TRUE(prog.has_value());
    
    prog->analyze();
    auto numerals = prog->romanNumerals();
    
    EXPECT_EQ(numerals.size(), 4);
    EXPECT_EQ(numerals[0], "I");
    EXPECT_EQ(numerals[1], "vi");
    EXPECT_EQ(numerals[2], "IV");
    EXPECT_EQ(numerals[3], "V");
}

TEST_F(ProgressionTest, BorrowedChords) {
    auto prog = Progression::fromString("F-C-Bbm-F");  // Bbm is borrowed
    ASSERT_TRUE(prog.has_value());
    
    auto borrowed = prog->identifyBorrowedChords();
    
    // Bbm should be identified as borrowed
    EXPECT_FALSE(borrowed.empty());
}

TEST_F(ProgressionTest, DiagnosticsResult) {
    auto result = engine.diagnoseProgression("F-C-Am-Dm");
    
    EXPECT_TRUE(result.success);
    EXPECT_EQ(result.chordNames.size(), 4);
    EXPECT_FALSE(result.detectedKey.toString().empty());
}

TEST_F(ProgressionTest, DiagnosticsDetectsNonDiatonic) {
    auto result = engine.diagnoseProgression("F-C-Bbm-F");
    
    EXPECT_TRUE(result.success);
    EXPECT_FALSE(result.issues.empty());  // Should flag Bbm
}

// ============================================================================
// Reharmonization Tests
// ============================================================================

TEST_F(ProgressionTest, GenerateReharmonizations) {
    auto suggestions = engine.generateReharmonizations("C-G-Am-F", "jazz", 3);
    
    EXPECT_FALSE(suggestions.empty());
    EXPECT_LE(suggestions.size(), 3);
    
    // Each suggestion should have chords
    for (const auto& sug : suggestions) {
        EXPECT_FALSE(sug.chords.empty());
        EXPECT_FALSE(sug.mood.empty());
    }
}

// ============================================================================
// Utility Function Tests
// ============================================================================

TEST(UtilityTest, MidiToPitchClass) {
    EXPECT_EQ(midiToPitchClass(60), 0);   // C4 -> C
    EXPECT_EQ(midiToPitchClass(61), 1);   // C#4 -> C#
    EXPECT_EQ(midiToPitchClass(72), 0);   // C5 -> C
    EXPECT_EQ(midiToPitchClass(69), 9);   // A4 -> A
}

TEST(UtilityTest, PitchClassToMidi) {
    EXPECT_EQ(pitchClassToMidi(0, 4), 60);   // C4
    EXPECT_EQ(pitchClassToMidi(9, 4), 69);   // A4
    EXPECT_EQ(pitchClassToMidi(0, 5), 72);   // C5
}

TEST(UtilityTest, QualityToString) {
    EXPECT_EQ(qualityToString(ChordQuality::Major), "");
    EXPECT_EQ(qualityToString(ChordQuality::Minor), "m");
    EXPECT_EQ(qualityToString(ChordQuality::Diminished), "dim");
    EXPECT_EQ(qualityToString(ChordQuality::Dominant7), "7");
}

TEST(UtilityTest, ModeToString) {
    EXPECT_EQ(modeToString(Mode::Major), "major");
    EXPECT_EQ(modeToString(Mode::Minor), "minor");
    EXPECT_EQ(modeToString(Mode::Dorian), "dorian");
}

TEST(UtilityTest, GetScaleDegrees) {
    auto major = getScaleDegrees(Mode::Major);
    EXPECT_EQ(major.size(), 7);
    EXPECT_EQ(major[0], 0);
    EXPECT_EQ(major[1], 2);
    EXPECT_EQ(major[2], 4);
    
    auto minor = getScaleDegrees(Mode::Minor);
    EXPECT_EQ(minor.size(), 7);
    EXPECT_EQ(minor[2], 3);  // Minor 3rd
}
