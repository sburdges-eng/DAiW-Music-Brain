/**
 * DiagnosticsEngine.h - Progression Diagnostics for iDAW
 * 
 * Provides diagnostic analysis of chord progressions:
 * - Issue detection (non-diatonic chords, awkward voice leading)
 * - Suggestions for improvement
 * - Rule-breaking identification with emotional justification
 */

#pragma once

#include "../harmony/Chord.h"
#include "../harmony/Progression.h"
#include "../harmony/HarmonyEngine.h"
#include <string>
#include <vector>
#include <map>

namespace iDAW {
namespace diagnostics {

using namespace harmony;

/**
 * Rule-breaking categories
 */
enum class RuleBreakCategory : uint8_t {
    // Harmony rules
    HarmonyModalInterchange,
    HarmonyParallelMotion,
    HarmonyAvoidTonicResolution,
    HarmonyUnresolvedDissonance,
    HarmonyNonFunctional,
    
    // Rhythm rules
    RhythmConstantDisplacement,
    RhythmTempoFluctuation,
    RhythmMeterAmbiguity,
    
    // Arrangement rules
    ArrangementBuriedVocals,
    ArrangementExtremeDynamics,
    
    // Production rules
    ProductionPitchImperfection,
    ProductionExcessiveMud,
    ProductionLoFiAesthetics
};

/**
 * Get string name for rule break category
 */
inline std::string ruleBreakToString(RuleBreakCategory category) {
    switch (category) {
        case RuleBreakCategory::HarmonyModalInterchange:
            return "HARMONY_ModalInterchange";
        case RuleBreakCategory::HarmonyParallelMotion:
            return "HARMONY_ParallelMotion";
        case RuleBreakCategory::HarmonyAvoidTonicResolution:
            return "HARMONY_AvoidTonicResolution";
        case RuleBreakCategory::HarmonyUnresolvedDissonance:
            return "HARMONY_UnresolvedDissonance";
        case RuleBreakCategory::HarmonyNonFunctional:
            return "HARMONY_NonFunctional";
        case RuleBreakCategory::RhythmConstantDisplacement:
            return "RHYTHM_ConstantDisplacement";
        case RuleBreakCategory::RhythmTempoFluctuation:
            return "RHYTHM_TempoFluctuation";
        case RuleBreakCategory::RhythmMeterAmbiguity:
            return "RHYTHM_MeterAmbiguity";
        case RuleBreakCategory::ArrangementBuriedVocals:
            return "ARRANGEMENT_BuriedVocals";
        case RuleBreakCategory::ArrangementExtremeDynamics:
            return "ARRANGEMENT_ExtremeDynamics";
        case RuleBreakCategory::ProductionPitchImperfection:
            return "PRODUCTION_PitchImperfection";
        case RuleBreakCategory::ProductionExcessiveMud:
            return "PRODUCTION_ExcessiveMud";
        case RuleBreakCategory::ProductionLoFiAesthetics:
            return "PRODUCTION_LoFiAesthetics";
        default:
            return "UNKNOWN";
    }
}

/**
 * Detected rule break with context
 */
struct RuleBreak {
    RuleBreakCategory category;
    std::string chordName;
    std::string context;
    std::string emotionalEffect;
    std::string justification;
    
    std::string toString() const {
        return ruleBreakToString(category) + " at " + chordName + ": " + emotionalEffect;
    }
};

/**
 * Diagnostic issue
 */
struct DiagnosticIssue {
    std::string description;
    std::string chordInvolved;
    int chordIndex;
    bool isWarning;  // Warning vs error
    std::optional<RuleBreak> ruleBreak;  // If this is intentional rule-breaking
};

/**
 * Diagnostic suggestion
 */
struct DiagnosticSuggestion {
    std::string description;
    std::string rationale;
    int priority;  // 1 = high, 3 = low
};

/**
 * Complete diagnostic result
 */
struct DiagnosticReport {
    Key detectedKey;
    std::vector<std::string> chordNames;
    std::vector<std::string> romanNumerals;
    std::vector<DiagnosticIssue> issues;
    std::vector<DiagnosticSuggestion> suggestions;
    std::vector<RuleBreak> ruleBreaks;
    std::map<std::string, std::string> borrowedChords;
    
    // Summary
    std::string emotionalCharacter;
    float harmonyComplexity;  // 0.0 = simple, 1.0 = complex
    bool hasResolution;
    
    bool success = true;
    std::string errorMessage;
};

/**
 * DiagnosticsEngine - Progression analysis and diagnostics
 */
class DiagnosticsEngine {
public:
    /**
     * Get singleton instance
     */
    static DiagnosticsEngine& getInstance();
    
    // Non-copyable
    DiagnosticsEngine(const DiagnosticsEngine&) = delete;
    DiagnosticsEngine& operator=(const DiagnosticsEngine&) = delete;
    
    /**
     * Full diagnostic analysis of a progression string
     */
    DiagnosticReport diagnose(const std::string& progressionStr) const;
    
    /**
     * Diagnose a parsed progression
     */
    DiagnosticReport diagnose(const Progression& progression) const;
    
    /**
     * Identify rule breaks in a progression
     */
    std::vector<RuleBreak> identifyRuleBreaks(
        const Progression& progression,
        const Key& key) const;
    
    /**
     * Get emotional character description
     */
    std::string getEmotionalCharacter(
        const Progression& progression,
        const Key& key) const;
    
    /**
     * Calculate harmonic complexity score
     */
    float calculateComplexity(const Progression& progression) const;
    
    /**
     * Check if progression has proper resolution
     */
    bool hasResolution(
        const Progression& progression,
        const Key& key) const;
    
    /**
     * Suggest rule breaks for emotional effect
     */
    std::vector<RuleBreak> suggestRuleBreaks(
        const std::string& emotion) const;
    
private:
    DiagnosticsEngine() = default;
    ~DiagnosticsEngine() = default;
    
    // Internal analysis helpers
    void analyzeVoiceLeading(
        const Progression& progression,
        std::vector<DiagnosticIssue>& issues) const;
    
    void analyzeBorrowedChords(
        const Progression& progression,
        const Key& key,
        std::vector<RuleBreak>& ruleBreaks) const;
    
    void generateSuggestions(
        const Progression& progression,
        const Key& key,
        const std::vector<DiagnosticIssue>& issues,
        std::vector<DiagnosticSuggestion>& suggestions) const;
};

} // namespace diagnostics
} // namespace iDAW
