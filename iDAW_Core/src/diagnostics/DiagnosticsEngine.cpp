/**
 * DiagnosticsEngine.cpp - Implementation of Progression Diagnostics Engine
 */

#include "diagnostics/DiagnosticsEngine.h"
#include <algorithm>
#include <map>

namespace iDAW {
namespace diagnostics {

using namespace harmony;

// ============================================================================
// DiagnosticsEngine Implementation
// ============================================================================

DiagnosticsEngine& DiagnosticsEngine::getInstance() {
    static DiagnosticsEngine instance;
    return instance;
}

DiagnosticReport DiagnosticsEngine::diagnose(const std::string& progressionStr) const {
    auto progOpt = Progression::fromString(progressionStr);
    if (!progOpt) {
        DiagnosticReport report;
        report.success = false;
        report.errorMessage = "Could not parse chord progression";
        report.issues.push_back({
            "Could not parse chord progression",
            "",
            -1,
            false,
            std::nullopt
        });
        report.suggestions.push_back({
            "Check chord spelling",
            "Ensure chord names are valid (e.g., Am, Cmaj7, F#dim)",
            1
        });
        return report;
    }
    
    return diagnose(*progOpt);
}

DiagnosticReport DiagnosticsEngine::diagnose(const Progression& progression) const {
    DiagnosticReport report;
    
    if (progression.empty()) {
        report.success = false;
        report.errorMessage = "Empty progression";
        return report;
    }
    
    // Detect key
    report.detectedKey = progression.key();
    
    // Get chord names and Roman numerals
    for (const auto& chord : progression.chords()) {
        report.chordNames.push_back(chord.name());
    }
    report.romanNumerals = progression.romanNumerals();
    
    // Identify rule breaks
    report.ruleBreaks = identifyRuleBreaks(progression, report.detectedKey);
    
    // Identify borrowed chords
    report.borrowedChords = progression.identifyBorrowedChords();
    
    // Analyze voice leading and issues
    analyzeVoiceLeading(progression, report.issues);
    
    // Analyze borrowed chords as rule breaks
    analyzeBorrowedChords(progression, report.detectedKey, report.ruleBreaks);
    
    // Generate suggestions
    generateSuggestions(progression, report.detectedKey, report.issues, report.suggestions);
    
    // Calculate complexity
    report.harmonyComplexity = calculateComplexity(progression);
    
    // Check resolution
    report.hasResolution = hasResolution(progression, report.detectedKey);
    
    // Get emotional character
    report.emotionalCharacter = getEmotionalCharacter(progression, report.detectedKey);
    
    report.success = true;
    return report;
}

std::vector<RuleBreak> DiagnosticsEngine::identifyRuleBreaks(
    const Progression& progression,
    const Key& key) const {
    
    std::vector<RuleBreak> ruleBreaks;
    
    auto scale = getScaleDegrees(key.mode);
    
    for (size_t i = 0; i < progression.size(); i++) {
        const auto& chord = progression.at(i);
        int interval = (chord.root() - key.root + 12) % 12;
        
        // Check for modal interchange (borrowed chords)
        if (std::find(scale.begin(), scale.end(), interval) == scale.end()) {
            RuleBreak rb;
            rb.category = RuleBreakCategory::HarmonyModalInterchange;
            rb.chordName = chord.name();
            
            if (interval == 3 && key.mode == Mode::Major) {
                rb.context = "bIII chord borrowed from parallel minor";
                rb.emotionalEffect = "Creates bittersweet, melancholic color";
                rb.justification = "Common in pop/rock for emotional depth";
            } else if (interval == 8 && key.mode == Mode::Major) {
                rb.context = "bVI chord borrowed from parallel minor";
                rb.emotionalEffect = "Creates darkness, drama, or nostalgia";
                rb.justification = "Classic Hollywood dramatic move";
            } else if (interval == 10 && key.mode == Mode::Major) {
                rb.context = "bVII chord from mixolydian/parallel minor";
                rb.emotionalEffect = "Creates rock/blues power, avoids dominant tension";
                rb.justification = "Standard in rock and blues progressions";
            } else if (interval == 5 && chord.quality() == ChordQuality::Minor) {
                rb.context = "iv chord borrowed from parallel minor";
                rb.emotionalEffect = "Creates sadness, resignation, bittersweet feeling";
                rb.justification = "The 'heart-wrenching' sound in pop ballads";
            } else {
                rb.context = "Non-diatonic chord";
                rb.emotionalEffect = "Creates tension or color outside the key";
                rb.justification = "Intentional chromatic movement";
            }
            
            ruleBreaks.push_back(rb);
        }
        
        // Check for parallel motion (consecutive chords with same quality)
        if (i > 0) {
            const auto& prevChord = progression.at(i - 1);
            if (chord.quality() == prevChord.quality()) {
                int motion = (chord.root() - prevChord.root() + 12) % 12;
                
                // Parallel fifths/fourths (power chord movement)
                if (motion == 5 || motion == 7) {
                    RuleBreak rb;
                    rb.category = RuleBreakCategory::HarmonyParallelMotion;
                    rb.chordName = prevChord.name() + " → " + chord.name();
                    rb.context = "Parallel " + (motion == 5 ? "fourth" : "fifth") + " motion";
                    rb.emotionalEffect = "Creates power, unity, medieval quality";
                    rb.justification = "Common in rock, metal, and cinematic music";
                    ruleBreaks.push_back(rb);
                }
            }
        }
    }
    
    // Check for avoided tonic resolution
    if (progression.size() > 0) {
        const auto& lastChord = progression.at(progression.size() - 1);
        int lastInterval = (lastChord.root() - key.root + 12) % 12;
        
        if (lastInterval != 0) {
            RuleBreak rb;
            rb.category = RuleBreakCategory::HarmonyAvoidTonicResolution;
            rb.chordName = lastChord.name();
            rb.context = "Progression does not resolve to tonic";
            rb.emotionalEffect = "Creates unresolved yearning, open-ended feeling";
            rb.justification = "Used in emo/lo-fi for emotional ambiguity";
            ruleBreaks.push_back(rb);
        }
    }
    
    return ruleBreaks;
}

std::string DiagnosticsEngine::getEmotionalCharacter(
    const Progression& progression,
    const Key& key) const {
    
    if (progression.empty()) {
        return "unknown";
    }
    
    // Count different characteristics
    int majorCount = 0;
    int minorCount = 0;
    int dominantCount = 0;
    int nonDiatonicCount = 0;
    
    auto scale = getScaleDegrees(key.mode);
    
    for (const auto& chord : progression.chords()) {
        // Quality counts
        if (chord.quality() == ChordQuality::Major ||
            chord.quality() == ChordQuality::Major7) {
            majorCount++;
        } else if (chord.quality() == ChordQuality::Minor ||
                   chord.quality() == ChordQuality::Minor7) {
            minorCount++;
        } else if (chord.quality() == ChordQuality::Dominant7) {
            dominantCount++;
        }
        
        // Diatonic check
        int interval = (chord.root() - key.root + 12) % 12;
        if (std::find(scale.begin(), scale.end(), interval) == scale.end()) {
            nonDiatonicCount++;
        }
    }
    
    float total = static_cast<float>(progression.size());
    float minorRatio = minorCount / total;
    float nonDiatonicRatio = nonDiatonicCount / total;
    
    // Determine character
    std::string character;
    
    if (nonDiatonicRatio > 0.3f) {
        character = "complex, emotionally ambiguous";
    } else if (minorRatio > 0.5f) {
        if (key.mode == Mode::Minor) {
            character = "dark, introspective";
        } else {
            character = "bittersweet, melancholic";
        }
    } else if (dominantCount > 0) {
        character = "driving, tension-filled";
    } else if (key.mode == Mode::Major && majorCount > minorCount) {
        character = "bright, uplifting";
    } else {
        character = "balanced, versatile";
    }
    
    return character;
}

float DiagnosticsEngine::calculateComplexity(const Progression& progression) const {
    if (progression.empty()) {
        return 0.0f;
    }
    
    float complexity = 0.0f;
    
    // Unique chord count contributes to complexity
    std::set<std::string> uniqueChords;
    for (const auto& chord : progression.chords()) {
        uniqueChords.insert(chord.name());
    }
    complexity += std::min(1.0f, uniqueChords.size() / 8.0f) * 0.3f;
    
    // Extended chords contribute
    int extendedCount = 0;
    for (const auto& chord : progression.chords()) {
        if (chord.quality() == ChordQuality::Major7 ||
            chord.quality() == ChordQuality::Minor7 ||
            chord.quality() == ChordQuality::Dominant7 ||
            chord.quality() == ChordQuality::Dim7 ||
            chord.quality() == ChordQuality::HalfDim7) {
            extendedCount++;
        }
    }
    complexity += (extendedCount / static_cast<float>(progression.size())) * 0.3f;
    
    // Non-diatonic chords contribute
    auto scale = getScaleDegrees(progression.key().mode);
    int nonDiatonicCount = 0;
    for (const auto& chord : progression.chords()) {
        int interval = (chord.root() - progression.key().root + 12) % 12;
        if (std::find(scale.begin(), scale.end(), interval) == scale.end()) {
            nonDiatonicCount++;
        }
    }
    complexity += (nonDiatonicCount / static_cast<float>(progression.size())) * 0.4f;
    
    return std::clamp(complexity, 0.0f, 1.0f);
}

bool DiagnosticsEngine::hasResolution(
    const Progression& progression,
    const Key& key) const {
    
    if (progression.empty()) {
        return false;
    }
    
    const auto& lastChord = progression.at(progression.size() - 1);
    int lastInterval = (lastChord.root() - key.root + 12) % 12;
    
    // Resolves to tonic
    if (lastInterval == 0) {
        return true;
    }
    
    // Check for V-I or IV-I at the end
    if (progression.size() >= 2) {
        const auto& secondLast = progression.at(progression.size() - 2);
        int secondLastInterval = (secondLast.root() - key.root + 12) % 12;
        
        // V → I
        if (secondLastInterval == 7 && lastInterval == 0) {
            return true;
        }
        // IV → I (plagal)
        if (secondLastInterval == 5 && lastInterval == 0) {
            return true;
        }
    }
    
    return false;
}

std::vector<RuleBreak> DiagnosticsEngine::suggestRuleBreaks(
    const std::string& emotion) const {
    
    std::vector<RuleBreak> suggestions;
    std::string lowerEmotion = emotion;
    std::transform(lowerEmotion.begin(), lowerEmotion.end(), lowerEmotion.begin(), ::tolower);
    
    if (lowerEmotion == "grief" || lowerEmotion == "sadness") {
        suggestions.push_back({
            RuleBreakCategory::HarmonyModalInterchange,
            "iv chord",
            "Borrow minor iv from parallel minor",
            "Creates deep sadness, resignation",
            "The 'heart-wrenching' sound"
        });
        suggestions.push_back({
            RuleBreakCategory::HarmonyAvoidTonicResolution,
            "End on IV or vi",
            "Avoid resolving to tonic",
            "Creates unresolved yearning",
            "Lets the emotion linger"
        });
        suggestions.push_back({
            RuleBreakCategory::ProductionPitchImperfection,
            "Slight pitch wobble",
            "Add subtle pitch drift to vocals/instruments",
            "Creates vulnerability, emotional honesty",
            "Lo-fi bedroom emo aesthetic"
        });
    }
    else if (lowerEmotion == "anxiety" || lowerEmotion == "tension") {
        suggestions.push_back({
            RuleBreakCategory::RhythmConstantDisplacement,
            "Off-kilter timing",
            "Displace beats from grid",
            "Creates unease, instability",
            "Mirror internal tension"
        });
        suggestions.push_back({
            RuleBreakCategory::HarmonyUnresolvedDissonance,
            "Avoid resolution",
            "Leave dissonances hanging",
            "Creates persistent tension",
            "Never let listener relax"
        });
    }
    else if (lowerEmotion == "anger" || lowerEmotion == "defiance") {
        suggestions.push_back({
            RuleBreakCategory::HarmonyParallelMotion,
            "Power chord movement",
            "Use parallel fifths/fourths",
            "Creates power, aggression",
            "Standard in punk/metal"
        });
        suggestions.push_back({
            RuleBreakCategory::ArrangementExtremeDynamics,
            "Extreme dynamics",
            "Juxtapose quiet and loud sections",
            "Creates explosive release",
            "The Pixies quiet-loud-quiet"
        });
    }
    else if (lowerEmotion == "nostalgia" || lowerEmotion == "longing") {
        suggestions.push_back({
            RuleBreakCategory::HarmonyModalInterchange,
            "bVI chord",
            "Borrow bVI from parallel minor",
            "Creates nostalgic, dreamy quality",
            "Classic 'looking back' sound"
        });
        suggestions.push_back({
            RuleBreakCategory::ProductionLoFiAesthetics,
            "Lo-fi treatment",
            "Add vinyl crackle, tape wobble",
            "Creates 'memory' aesthetic",
            "Sounds like a faded photograph"
        });
    }
    else if (lowerEmotion == "hope" || lowerEmotion == "uplift") {
        suggestions.push_back({
            RuleBreakCategory::HarmonyModalInterchange,
            "bVII chord",
            "Use mixolydian bVII",
            "Creates triumphant, rock anthem feel",
            "Avoided dominant for earthier resolution"
        });
    }
    
    return suggestions;
}

void DiagnosticsEngine::analyzeVoiceLeading(
    const Progression& progression,
    std::vector<DiagnosticIssue>& issues) const {
    
    for (size_t i = 1; i < progression.size(); i++) {
        const auto& prev = progression.at(i - 1);
        const auto& curr = progression.at(i);
        
        int rootMotion = (curr.root() - prev.root() + 12) % 12;
        
        // Tritone motion
        if (rootMotion == 6) {
            DiagnosticIssue issue;
            issue.description = "Tritone motion between " + prev.name() + 
                               " and " + curr.name() + " - can feel unstable";
            issue.chordInvolved = prev.name() + " → " + curr.name();
            issue.chordIndex = static_cast<int>(i);
            issue.isWarning = true;
            issues.push_back(issue);
        }
    }
}

void DiagnosticsEngine::analyzeBorrowedChords(
    const Progression& progression,
    const Key& key,
    std::vector<RuleBreak>& ruleBreaks) const {
    
    // This is already handled in identifyRuleBreaks
    // Keep for potential future expansion
}

void DiagnosticsEngine::generateSuggestions(
    const Progression& progression,
    const Key& key,
    const std::vector<DiagnosticIssue>& issues,
    std::vector<DiagnosticSuggestion>& suggestions) const {
    
    if (progression.empty()) return;
    
    // Check for resolution
    const auto& lastChord = progression.at(progression.size() - 1);
    int lastInterval = (lastChord.root() - key.root + 12) % 12;
    
    if (lastInterval != 0 && lastInterval != 7) {
        suggestions.push_back({
            "Progression ends on " + lastChord.name() + 
            " - consider resolving to " + std::string(NOTE_NAMES[key.root]),
            "Traditional progressions typically resolve to the tonic for closure",
            2
        });
    }
    
    // Check for dominant
    bool hasDominant = false;
    bool hasTonic = false;
    for (const auto& chord : progression.chords()) {
        int interval = (chord.root() - key.root + 12) % 12;
        if (interval == 7) hasDominant = true;
        if (interval == 0) hasTonic = true;
    }
    
    if (!hasDominant && hasTonic) {
        suggestions.push_back({
            "No dominant (V) chord - consider adding for stronger resolution",
            "The V-I movement is the strongest harmonic resolution",
            2
        });
    }
    
    // If there are tritone issues, suggest passing chords
    for (const auto& issue : issues) {
        if (issue.description.find("Tritone") != std::string::npos) {
            suggestions.push_back({
                "Consider adding a passing chord between " + issue.chordInvolved,
                "A chromatic approach chord can smooth the transition",
                3
            });
        }
    }
}

} // namespace diagnostics
} // namespace iDAW
