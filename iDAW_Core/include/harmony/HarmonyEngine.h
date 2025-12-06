/**
 * HarmonyEngine.h - C++ Harmony Analysis Engine for iDAW
 * 
 * High-performance harmony analysis including:
 * - Chord detection from MIDI notes
 * - Key detection
 * - Progression analysis
 * - Borrowed chord identification
 * - Reharmonization suggestions
 */

#pragma once

#include "Chord.h"
#include "Progression.h"
#include <string>
#include <vector>
#include <map>
#include <memory>

namespace iDAW {
namespace harmony {

/**
 * Reharmonization technique enumeration
 */
enum class ReharmTechnique : uint8_t {
    TritoneSubstitution,
    ChromaticApproach,
    SecondaryDominants,
    DiminishedPassing,
    BorrowedFromParallel,
    PedalPoint,
    SusChords,
    Add9Extensions,
    ExtendedDominants,
    ParallelMotion,
    QuartalVoicings
};

/**
 * Reharmonization suggestion
 */
struct ReharmSuggestion {
    std::vector<Chord> chords;
    ReharmTechnique technique;
    std::string mood;
    std::string description;
};

/**
 * Progression diagnosis result
 */
struct DiagnosisResult {
    Key detectedKey;
    std::vector<std::string> issues;
    std::vector<std::string> suggestions;
    std::vector<std::string> chordNames;
    std::map<std::string, std::string> borrowedChords;
    bool success = true;
};

/**
 * HarmonyEngine - Main harmony analysis interface
 * 
 * Thread-safe for use from both audio and UI threads.
 */
class HarmonyEngine {
public:
    /**
     * Get singleton instance
     */
    static HarmonyEngine& getInstance();
    
    // Non-copyable
    HarmonyEngine(const HarmonyEngine&) = delete;
    HarmonyEngine& operator=(const HarmonyEngine&) = delete;
    
    /**
     * Detect chord from MIDI notes
     */
    Chord detectChord(const std::vector<int>& midiNotes) const;
    
    /**
     * Parse and analyze a progression string
     */
    DiagnosisResult diagnoseProgression(const std::string& progressionStr) const;
    
    /**
     * Detect key from a progression
     */
    Key detectKey(const Progression& progression) const;
    Key detectKey(const std::vector<Chord>& chords) const;
    
    /**
     * Get Roman numeral for chord in key
     */
    std::string getRomanNumeral(const Chord& chord, const Key& key) const;
    
    /**
     * Identify borrowed chords
     */
    std::map<std::string, std::string> identifyBorrowedChords(
        const Progression& progression) const;
    
    /**
     * Generate reharmonization suggestions
     */
    std::vector<ReharmSuggestion> generateReharmonizations(
        const std::string& progressionStr,
        const std::string& style = "jazz",
        int count = 3) const;
    
    /**
     * Check if a chord is diatonic to a key
     */
    bool isDiatonic(const Chord& chord, const Key& key) const;
    
    /**
     * Get interval from key root to chord root
     */
    int getInterval(const Chord& chord, const Key& key) const;
    
private:
    HarmonyEngine() = default;
    ~HarmonyEngine() = default;
    
    // Internal helpers
    Chord detectChordFromPitchClasses(const std::vector<int>& pitchClasses) const;
    std::vector<ReharmSuggestion> applyTechnique(
        const Progression& prog, 
        ReharmTechnique technique) const;
};

/**
 * Utility: Parse chord from string
 */
std::optional<Chord> parseChordString(const std::string& chordStr);

/**
 * Utility: Parse progression string into chords
 */
std::vector<Chord> parseProgressionString(const std::string& progressionStr);

} // namespace harmony
} // namespace iDAW
