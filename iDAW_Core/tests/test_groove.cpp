/**
 * test_groove.cpp - Unit tests for Groove Engine
 */

#include <gtest/gtest.h>
#include "groove/GrooveEngine.h"
#include "groove/GrooveTemplate.h"

using namespace iDAW::groove;

// ============================================================================
// GrooveTemplate Tests
// ============================================================================

class GrooveTemplateTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Create test notes
        testNotes = {
            {36, 100, 0, 480, 0},      // Kick
            {42, 60, 120, 240, 0},     // Hi-hat
            {38, 110, 480, 480, 0},    // Snare
            {42, 55, 600, 240, 0},     // Hi-hat
            {36, 95, 960, 480, 0},     // Kick
            {42, 58, 1080, 240, 0},    // Hi-hat
            {38, 108, 1440, 480, 0},   // Snare
            {42, 52, 1560, 240, 0},    // Hi-hat
        };
    }
    
    std::vector<MidiNote> testNotes;
    GrooveEngine& engine = GrooveEngine::getInstance();
};

TEST_F(GrooveTemplateTest, GrooveTemplateCreation) {
    GrooveTemplate tmpl("Test Groove", "test.mid");
    
    EXPECT_EQ(tmpl.name(), "Test Groove");
    EXPECT_EQ(tmpl.sourceFile(), "test.mid");
    EXPECT_EQ(tmpl.ppq(), 480);
    EXPECT_EQ(tmpl.tempoBpm(), 120.0f);
}

TEST_F(GrooveTemplateTest, GrooveTemplateProperties) {
    GrooveTemplate tmpl;
    
    tmpl.setName("Funk Groove");
    tmpl.setPpq(960);
    tmpl.setTempoBpm(95.0f);
    tmpl.setSwingFactor(0.58f);
    tmpl.setTimeSignature(4, 4);
    
    EXPECT_EQ(tmpl.name(), "Funk Groove");
    EXPECT_EQ(tmpl.ppq(), 960);
    EXPECT_FLOAT_EQ(tmpl.tempoBpm(), 95.0f);
    EXPECT_FLOAT_EQ(tmpl.swingFactor(), 0.58f);
    EXPECT_EQ(tmpl.timeSignature().first, 4);
    EXPECT_EQ(tmpl.timeSignature().second, 4);
}

// ============================================================================
// Groove Extraction Tests
// ============================================================================

TEST_F(GrooveTemplateTest, ExtractGroove) {
    auto groove = engine.extractGroove(testNotes, 480, 120.0f);
    
    EXPECT_TRUE(groove.isValid());
    EXPECT_FALSE(groove.events().empty());
    EXPECT_EQ(groove.events().size(), testNotes.size());
}

TEST_F(GrooveTemplateTest, ExtractGroove_TimingDeviations) {
    // Create notes with deviations
    std::vector<MidiNote> notes = {
        {36, 100, 5, 480, 0},       // 5 ticks early
        {38, 100, 485, 480, 0},     // 5 ticks late
        {36, 100, 958, 480, 0},     // 2 ticks early
        {38, 100, 1445, 480, 0},    // 5 ticks late
    };
    
    auto groove = engine.extractGroove(notes, 480, 120.0f);
    
    EXPECT_FALSE(groove.timingDeviations().empty());
}

TEST_F(GrooveTemplateTest, ExtractGroove_VelocityStats) {
    auto groove = engine.extractGroove(testNotes, 480, 120.0f);
    
    VelocityStats stats = groove.velocityStats();
    EXPECT_GT(stats.max, stats.min);
    EXPECT_GT(stats.mean, 0.0f);
}

TEST_F(GrooveTemplateTest, ExtractGroove_GhostNotes) {
    // Create notes with ghost notes (velocity < 40)
    std::vector<MidiNote> notes = {
        {36, 100, 0, 480, 0},
        {42, 35, 120, 240, 0},     // Ghost note
        {38, 110, 480, 480, 0},
        {42, 30, 600, 240, 0},     // Ghost note
    };
    
    auto groove = engine.extractGroove(notes, 480, 120.0f);
    
    EXPECT_EQ(groove.velocityStats().ghostCount, 2);
}

// ============================================================================
// Swing Calculation Tests
// ============================================================================

TEST_F(GrooveTemplateTest, CalculateSwing_Straight) {
    // Create perfectly straight 8th notes
    std::vector<MidiNote> notes;
    for (int i = 0; i < 8; i++) {
        notes.push_back({42, 80, i * 240, 120, 0});  // 8th notes at 240 ticks
    }
    
    float swing = engine.calculateSwing(notes, 480);
    
    // Straight swing should be around 0.5
    EXPECT_NEAR(swing, 0.5f, 0.1f);
}

TEST_F(GrooveTemplateTest, CalculateSwing_Swung) {
    // Create swung 8th notes (off-beats pushed late)
    std::vector<MidiNote> notes;
    for (int i = 0; i < 4; i++) {
        // On-beat
        notes.push_back({42, 80, i * 480, 120, 0});
        // Off-beat (pushed late by 60 ticks, ~25%)
        notes.push_back({42, 80, i * 480 + 240 + 60, 120, 0});
    }
    
    float swing = engine.calculateSwing(notes, 480);
    
    // Should be > 0.5 (swung)
    EXPECT_GT(swing, 0.5f);
}

// ============================================================================
// Groove Application Tests
// ============================================================================

TEST_F(GrooveTemplateTest, ApplyGroove) {
    // Create quantized notes
    std::vector<MidiNote> notes = {
        {36, 80, 0, 480, 0},
        {38, 80, 480, 480, 0},
        {36, 80, 960, 480, 0},
        {38, 80, 1440, 480, 0},
    };
    
    // Get funk groove template
    auto funk = engine.getGenreTemplate("funk");
    
    // Apply groove
    engine.applyGroove(notes, funk, 480);
    
    // Notes should be modified (timing and/or velocity changed)
    // We can't assert exact values but can check notes are still valid
    for (const auto& note : notes) {
        EXPECT_GE(note.startTick, 0);
        EXPECT_GT(note.velocity, 0);
        EXPECT_LE(note.velocity, 127);
    }
}

TEST_F(GrooveTemplateTest, ApplyGroove_IntensityZero) {
    std::vector<MidiNote> notes = {
        {36, 80, 0, 480, 0},
        {38, 80, 480, 480, 0},
    };
    
    std::vector<MidiNote> original = notes;
    
    auto groove = engine.getGenreTemplate("funk");
    ApplicationSettings settings;
    settings.intensity = 0.0f;
    
    engine.applyGroove(notes, groove, 480, settings);
    
    // With zero intensity, notes should be unchanged
    for (size_t i = 0; i < notes.size(); i++) {
        EXPECT_EQ(notes[i].startTick, original[i].startTick);
    }
}

// ============================================================================
// Humanization Tests
// ============================================================================

TEST_F(GrooveTemplateTest, Humanize) {
    std::vector<MidiNote> notes = {
        {36, 80, 0, 480, 0},
        {38, 80, 480, 480, 0},
        {36, 80, 960, 480, 0},
        {38, 80, 1440, 480, 0},
    };
    
    std::vector<MidiNote> original = notes;
    
    engine.humanize(notes, 0.5f, 0.5f, 480, 42);
    
    // Notes should be modified
    bool anyChanged = false;
    for (size_t i = 0; i < notes.size(); i++) {
        if (notes[i].startTick != original[i].startTick ||
            notes[i].velocity != original[i].velocity) {
            anyChanged = true;
            break;
        }
    }
    EXPECT_TRUE(anyChanged);
}

TEST_F(GrooveTemplateTest, Humanize_ZeroComplexity) {
    std::vector<MidiNote> notes = {
        {36, 80, 0, 480, 0},
        {38, 80, 480, 480, 0},
    };
    
    std::vector<MidiNote> original = notes;
    
    engine.humanize(notes, 0.0f, 0.0f, 480, 42);
    
    // With zero complexity and vulnerability, changes should be minimal
    // (only human latency bias applied)
    for (size_t i = 0; i < notes.size(); i++) {
        EXPECT_NEAR(notes[i].startTick, original[i].startTick, 15);
    }
}

TEST_F(GrooveTemplateTest, Humanize_Reproducible) {
    std::vector<MidiNote> notes1 = {
        {36, 80, 0, 480, 0},
        {38, 80, 480, 480, 0},
    };
    std::vector<MidiNote> notes2 = notes1;
    
    // Same seed should produce same results
    engine.humanize(notes1, 0.5f, 0.5f, 480, 42);
    engine.humanize(notes2, 0.5f, 0.5f, 480, 42);
    
    for (size_t i = 0; i < notes1.size(); i++) {
        EXPECT_EQ(notes1[i].startTick, notes2[i].startTick);
        EXPECT_EQ(notes1[i].velocity, notes2[i].velocity);
    }
}

// ============================================================================
// Quantization Tests
// ============================================================================

TEST_F(GrooveTemplateTest, Quantize) {
    std::vector<MidiNote> notes = {
        {36, 80, 25, 480, 0},     // Should snap to 0
        {38, 80, 505, 480, 0},    // Should snap to 480
        {36, 80, 935, 480, 0},    // Should snap to 960
    };
    
    engine.quantize(notes, 480, 16);  // 16th note quantize
    
    // 16th notes at 480 PPQ = 120 ticks per grid
    // Notes should snap to nearest grid
    EXPECT_EQ(notes[0].startTick, 0);
    EXPECT_EQ(notes[1].startTick, 480);
    EXPECT_EQ(notes[2].startTick, 960);
}

// ============================================================================
// Genre Preset Tests
// ============================================================================

TEST_F(GrooveTemplateTest, GenrePresets) {
    auto presets = engine.listGenrePresets();
    
    EXPECT_FALSE(presets.empty());
    EXPECT_GT(presets.size(), 5);
    
    // Check that all presets can be loaded
    for (const auto& preset : presets) {
        auto groove = engine.getGenreTemplate(preset);
        EXPECT_FALSE(groove.name().empty());
    }
}

TEST_F(GrooveTemplateTest, GenrePreset_Funk) {
    auto funk = engine.getGenreTemplate("funk");
    
    EXPECT_EQ(funk.name(), "Funk Pocket");
    EXPECT_GT(funk.swingFactor(), 0.5f);  // Funk should have swing
}

TEST_F(GrooveTemplateTest, GenrePreset_Dilla) {
    auto dilla = engine.getGenreTemplate("dilla");
    
    EXPECT_EQ(dilla.name(), "Dilla Time");
    EXPECT_GT(dilla.swingFactor(), 0.6f);  // Heavy swing
}

TEST_F(GrooveTemplateTest, GenrePreset_Straight) {
    auto straight = engine.getGenreTemplate("straight");
    
    EXPECT_FLOAT_EQ(straight.swingFactor(), 0.5f);  // No swing
}

// ============================================================================
// Quick Humanize Tests
// ============================================================================

TEST(QuickHumanizeTest, AllStyles) {
    std::vector<HumanizeStyle> styles = {
        HumanizeStyle::Tight,
        HumanizeStyle::Natural,
        HumanizeStyle::Loose,
        HumanizeStyle::Drunk,
        HumanizeStyle::Robot
    };
    
    for (auto style : styles) {
        std::vector<MidiNote> notes = {
            {36, 80, 0, 480, 0},
            {38, 80, 480, 480, 0},
        };
        
        quickHumanize(notes, style, 480);
        
        // All styles should produce valid results
        for (const auto& note : notes) {
            EXPECT_GE(note.startTick, 0);
            EXPECT_GT(note.velocity, 0);
            EXPECT_LE(note.velocity, 127);
        }
    }
}

// ============================================================================
// Genre Preset By Name Tests
// ============================================================================

TEST(GenrePresetTest, GetByName) {
    EXPECT_EQ(getGenrePresetByName("funk"), GenrePreset::Funk);
    EXPECT_EQ(getGenrePresetByName("jazz"), GenrePreset::Jazz);
    EXPECT_EQ(getGenrePresetByName("hiphop"), GenrePreset::HipHop);
    EXPECT_EQ(getGenrePresetByName("hip-hop"), GenrePreset::HipHop);
    EXPECT_EQ(getGenrePresetByName("lofi"), GenrePreset::LoFi);
    EXPECT_EQ(getGenrePresetByName("lo-fi"), GenrePreset::LoFi);
    EXPECT_EQ(getGenrePresetByName("unknown"), GenrePreset::Straight);
}
