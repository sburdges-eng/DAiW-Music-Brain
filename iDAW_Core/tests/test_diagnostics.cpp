/**
 * test_diagnostics.cpp - Unit tests for Diagnostics Engine
 */

#include <gtest/gtest.h>
#include "diagnostics/DiagnosticsEngine.h"
#include "harmony/Progression.h"

using namespace iDAW::diagnostics;
using namespace iDAW::harmony;

// ============================================================================
// Diagnostics Engine Tests
// ============================================================================

class DiagnosticsTest : public ::testing::Test {
protected:
    DiagnosticsEngine& engine = DiagnosticsEngine::getInstance();
};

TEST_F(DiagnosticsTest, DiagnoseSimpleProgression) {
    auto report = engine.diagnose("F-C-Am-Dm");
    
    EXPECT_TRUE(report.success);
    EXPECT_EQ(report.chordNames.size(), 4);
    EXPECT_EQ(report.chordNames[0], "F");
    EXPECT_EQ(report.chordNames[2], "Am");
}

TEST_F(DiagnosticsTest, DiagnoseDetectsKey) {
    auto report = engine.diagnose("C-Am-F-G");
    
    EXPECT_TRUE(report.success);
    EXPECT_EQ(report.detectedKey.root, 0);  // C
    EXPECT_EQ(report.detectedKey.mode, Mode::Major);
}

TEST_F(DiagnosticsTest, DiagnoseDetectsMinorKey) {
    auto report = engine.diagnose("Am-Dm-E-Am");
    
    EXPECT_TRUE(report.success);
    EXPECT_EQ(report.detectedKey.root, 9);  // A
    EXPECT_EQ(report.detectedKey.mode, Mode::Minor);
}

TEST_F(DiagnosticsTest, DiagnoseDetectsBorrowedChord) {
    auto report = engine.diagnose("F-C-Bbm-F");
    
    EXPECT_TRUE(report.success);
    // Bbm should be flagged as borrowed/non-diatonic
    EXPECT_FALSE(report.issues.empty());
}

TEST_F(DiagnosticsTest, DiagnoseEmptyProgression) {
    auto report = engine.diagnose("");
    
    EXPECT_FALSE(report.success);
}

TEST_F(DiagnosticsTest, DiagnoseInvalidProgression) {
    auto report = engine.diagnose("XYZ-123");
    
    EXPECT_FALSE(report.success);
}

// ============================================================================
// Rule Break Identification Tests
// ============================================================================

TEST_F(DiagnosticsTest, IdentifyModalInterchange) {
    auto prog = Progression::fromString("C-Am-Fm-G");  // Fm is borrowed
    ASSERT_TRUE(prog.has_value());
    
    Key key{0, Mode::Major};
    auto ruleBreaks = engine.identifyRuleBreaks(*prog, key);
    
    // Should identify Fm as modal interchange
    bool foundModalInterchange = false;
    for (const auto& rb : ruleBreaks) {
        if (rb.category == RuleBreakCategory::HarmonyModalInterchange) {
            foundModalInterchange = true;
            EXPECT_FALSE(rb.emotionalEffect.empty());
            break;
        }
    }
    EXPECT_TRUE(foundModalInterchange);
}

TEST_F(DiagnosticsTest, IdentifyBVII) {
    auto prog = Progression::fromString("C-Bb-F-C");  // Bb is bVII
    ASSERT_TRUE(prog.has_value());
    
    Key key{0, Mode::Major};
    auto ruleBreaks = engine.identifyRuleBreaks(*prog, key);
    
    EXPECT_FALSE(ruleBreaks.empty());
}

TEST_F(DiagnosticsTest, IdentifyAvoidedResolution) {
    auto prog = Progression::fromString("C-Am-F-Am");  // Ends on Am, not C
    ASSERT_TRUE(prog.has_value());
    
    Key key{0, Mode::Major};
    auto ruleBreaks = engine.identifyRuleBreaks(*prog, key);
    
    // Should identify avoided tonic resolution
    bool foundAvoided = false;
    for (const auto& rb : ruleBreaks) {
        if (rb.category == RuleBreakCategory::HarmonyAvoidTonicResolution) {
            foundAvoided = true;
            break;
        }
    }
    EXPECT_TRUE(foundAvoided);
}

// ============================================================================
// Emotional Character Tests
// ============================================================================

TEST_F(DiagnosticsTest, EmotionalCharacter_BrightMajor) {
    auto prog = Progression::fromString("C-F-G-C");
    ASSERT_TRUE(prog.has_value());
    
    Key key{0, Mode::Major};
    auto character = engine.getEmotionalCharacter(*prog, key);
    
    EXPECT_FALSE(character.empty());
    // Should indicate something positive/bright
}

TEST_F(DiagnosticsTest, EmotionalCharacter_DarkMinor) {
    auto prog = Progression::fromString("Am-Dm-Em-Am");
    ASSERT_TRUE(prog.has_value());
    
    Key key{9, Mode::Minor};
    auto character = engine.getEmotionalCharacter(*prog, key);
    
    EXPECT_FALSE(character.empty());
    // Should indicate something dark/introspective
}

TEST_F(DiagnosticsTest, EmotionalCharacter_Complex) {
    auto prog = Progression::fromString("C-Bb-Eb-Ab-C");  // Lots of chromatic chords
    ASSERT_TRUE(prog.has_value());
    
    Key key{0, Mode::Major};
    auto character = engine.getEmotionalCharacter(*prog, key);
    
    EXPECT_FALSE(character.empty());
    // Should indicate complexity for non-diatonic progression
    // Valid characters include "complex", "ambiguous", "bittersweet", etc.
    EXPECT_TRUE(
        character.find("complex") != std::string::npos ||
        character.find("ambiguous") != std::string::npos ||
        character.find("bittersweet") != std::string::npos ||
        character.find("dark") != std::string::npos);
}

// ============================================================================
// Complexity Calculation Tests
// ============================================================================

TEST_F(DiagnosticsTest, Complexity_Simple) {
    auto prog = Progression::fromString("C-G-C-G");
    ASSERT_TRUE(prog.has_value());
    
    float complexity = engine.calculateComplexity(*prog);
    
    EXPECT_GE(complexity, 0.0f);
    EXPECT_LE(complexity, 0.5f);  // Should be relatively simple
}

TEST_F(DiagnosticsTest, Complexity_WithExtensions) {
    auto prog = Progression::fromString("Cmaj7-Am7-Dm7-G7");
    ASSERT_TRUE(prog.has_value());
    
    float complexity = engine.calculateComplexity(*prog);
    
    EXPECT_GT(complexity, 0.2f);  // Extended chords add complexity
}

TEST_F(DiagnosticsTest, Complexity_NonDiatonic) {
    auto prog = Progression::fromString("C-Bb-Eb-G");
    ASSERT_TRUE(prog.has_value());
    
    float complexity = engine.calculateComplexity(*prog);
    
    EXPECT_GT(complexity, 0.3f);  // Non-diatonic chords add complexity
}

// ============================================================================
// Resolution Tests
// ============================================================================

TEST_F(DiagnosticsTest, HasResolution_ToTonic) {
    auto prog = Progression::fromString("C-F-G-C");
    ASSERT_TRUE(prog.has_value());
    
    Key key{0, Mode::Major};
    bool hasRes = engine.hasResolution(*prog, key);
    
    EXPECT_TRUE(hasRes);
}

TEST_F(DiagnosticsTest, HasResolution_VtoI) {
    auto prog = Progression::fromString("Am-Dm-E-Am");
    ASSERT_TRUE(prog.has_value());
    
    Key key{9, Mode::Minor};
    bool hasRes = engine.hasResolution(*prog, key);
    
    EXPECT_TRUE(hasRes);
}

TEST_F(DiagnosticsTest, NoResolution) {
    auto prog = Progression::fromString("C-Am-F-Dm");  // Ends on Dm
    ASSERT_TRUE(prog.has_value());
    
    Key key{0, Mode::Major};
    bool hasRes = engine.hasResolution(*prog, key);
    
    EXPECT_FALSE(hasRes);
}

// ============================================================================
// Rule Break Suggestions Tests
// ============================================================================

TEST_F(DiagnosticsTest, SuggestRuleBreaks_Grief) {
    auto suggestions = engine.suggestRuleBreaks("grief");
    
    EXPECT_FALSE(suggestions.empty());
    
    for (const auto& rb : suggestions) {
        EXPECT_FALSE(rb.emotionalEffect.empty());
        EXPECT_FALSE(rb.justification.empty());
    }
}

TEST_F(DiagnosticsTest, SuggestRuleBreaks_Anxiety) {
    auto suggestions = engine.suggestRuleBreaks("anxiety");
    
    EXPECT_FALSE(suggestions.empty());
}

TEST_F(DiagnosticsTest, SuggestRuleBreaks_Anger) {
    auto suggestions = engine.suggestRuleBreaks("anger");
    
    EXPECT_FALSE(suggestions.empty());
    
    // Should include parallel motion for power
    bool foundParallel = false;
    for (const auto& rb : suggestions) {
        if (rb.category == RuleBreakCategory::HarmonyParallelMotion) {
            foundParallel = true;
            break;
        }
    }
    EXPECT_TRUE(foundParallel);
}

TEST_F(DiagnosticsTest, SuggestRuleBreaks_Nostalgia) {
    auto suggestions = engine.suggestRuleBreaks("nostalgia");
    
    EXPECT_FALSE(suggestions.empty());
}

// ============================================================================
// Full Diagnostic Report Tests
// ============================================================================

TEST_F(DiagnosticsTest, FullReport) {
    auto report = engine.diagnose("F-C-Dm-Bbm");
    
    EXPECT_TRUE(report.success);
    EXPECT_EQ(report.chordNames.size(), 4);
    EXPECT_FALSE(report.emotionalCharacter.empty());
    EXPECT_GE(report.harmonyComplexity, 0.0f);
    EXPECT_LE(report.harmonyComplexity, 1.0f);
    
    // Should have suggestions since Bbm is borrowed
    EXPECT_FALSE(report.ruleBreaks.empty());
}

// ============================================================================
// Utility Function Tests
// ============================================================================

TEST(RuleBreakUtilTest, RuleBreakToString) {
    EXPECT_EQ(ruleBreakToString(RuleBreakCategory::HarmonyModalInterchange),
              "HARMONY_ModalInterchange");
    EXPECT_EQ(ruleBreakToString(RuleBreakCategory::HarmonyParallelMotion),
              "HARMONY_ParallelMotion");
    EXPECT_EQ(ruleBreakToString(RuleBreakCategory::RhythmConstantDisplacement),
              "RHYTHM_ConstantDisplacement");
    EXPECT_EQ(ruleBreakToString(RuleBreakCategory::ProductionPitchImperfection),
              "PRODUCTION_PitchImperfection");
}
