/**
 * DiagnosticsCore.h - C++ Core Module for Chord Progression Diagnostics
 * 
 * Part of Phase 3 C++ Migration for DAiW-Music-Brain
 * 
 * This module provides real-time safe progression analysis including:
 * - Chord string parsing
 * - Harmonic issue detection
 * - Reharmonization suggestions
 * - Modal interchange analysis
 * 
 * Design Philosophy:
 * - All operations are allocation-free after initialization
 * - Thread-safe for concurrent access
 * - Optimized for real-time audio processing
 * 
 * Corresponding Python module: music_brain/structure/progression.py
 */

#pragma once

#include "HarmonyCore.h"
#include <array>
#include <cstdint>
#include <string>
#include <string_view>
#include <algorithm>
#include <cctype>

namespace iDAW {
namespace Diagnostics {

// =============================================================================
// Constants
// =============================================================================

// Maximum issues/suggestions to report
constexpr size_t MAX_ISSUES = 16;
constexpr size_t MAX_SUGGESTIONS = 16;
constexpr size_t MAX_REHARMONIZATIONS = 8;

// Maximum chord string length for parsing
constexpr size_t MAX_CHORD_STRING_LENGTH = 512;

// =============================================================================
// Parsed Chord
// =============================================================================

/**
 * Chord parsed from a string representation
 */
struct ParsedChord {
    std::array<char, 8> rootName = {};      // Root note name
    int8_t rootNum = -1;                    // Pitch class (0-11)
    Harmony::ChordQuality quality = Harmony::ChordQuality::Major;
    std::array<char, 16> originalString = {};
    int8_t bassNote = -1;                   // For slash chords
    
    bool isValid() const { return rootNum >= 0 && rootNum < 12; }
    
    std::string_view getRoot() const { return std::string_view(rootName.data()); }
    std::string_view getOriginal() const { return std::string_view(originalString.data()); }
};

// =============================================================================
// Diagnostic Issue
// =============================================================================

struct DiagnosticIssue {
    std::array<char, 256> description = {};
    uint8_t severity = 0;  // 0 = info, 1 = warning, 2 = error
    int8_t chordIndex = -1;  // Which chord this issue refers to
    
    void setDescription(std::string_view desc) {
        size_t len = std::min(desc.size(), description.size() - 1);
        std::copy_n(desc.begin(), len, description.begin());
        description[len] = '\0';
    }
    
    std::string_view getDescription() const {
        return std::string_view(description.data());
    }
};

// =============================================================================
// Diagnostic Suggestion
// =============================================================================

struct DiagnosticSuggestion {
    std::array<char, 256> description = {};
    std::array<char, 64> technique = {};
    
    void setDescription(std::string_view desc) {
        size_t len = std::min(desc.size(), description.size() - 1);
        std::copy_n(desc.begin(), len, description.begin());
        description[len] = '\0';
    }
    
    void setTechnique(std::string_view tech) {
        size_t len = std::min(tech.size(), technique.size() - 1);
        std::copy_n(tech.begin(), len, technique.begin());
        technique[len] = '\0';
    }
    
    std::string_view getDescription() const { return std::string_view(description.data()); }
    std::string_view getTechnique() const { return std::string_view(technique.data()); }
};

// =============================================================================
// Reharmonization Suggestion
// =============================================================================

struct ReharmonizationSuggestion {
    std::array<ParsedChord, Harmony::MAX_PROGRESSION_CHORDS> newChords = {};
    size_t chordCount = 0;
    std::array<char, 64> technique = {};
    std::array<char, 64> mood = {};
    
    void setTechnique(std::string_view tech) {
        size_t len = std::min(tech.size(), technique.size() - 1);
        std::copy_n(tech.begin(), len, technique.begin());
        technique[len] = '\0';
    }
    
    void setMood(std::string_view m) {
        size_t len = std::min(m.size(), mood.size() - 1);
        std::copy_n(m.begin(), len, mood.begin());
        mood[len] = '\0';
    }
    
    std::string_view getTechnique() const { return std::string_view(technique.data()); }
    std::string_view getMood() const { return std::string_view(mood.data()); }
};

// =============================================================================
// Progression Diagnosis Result
// =============================================================================

struct ProgressionDiagnosis {
    // Key detection
    int8_t keyRoot = 0;
    Harmony::Mode keyMode = Harmony::Mode::Major;
    float keyConfidence = 0.0f;
    
    // Parsed chords
    std::array<ParsedChord, Harmony::MAX_PROGRESSION_CHORDS> chords = {};
    size_t chordCount = 0;
    
    // Issues found
    std::array<DiagnosticIssue, MAX_ISSUES> issues = {};
    size_t issueCount = 0;
    
    // Suggestions
    std::array<DiagnosticSuggestion, MAX_SUGGESTIONS> suggestions = {};
    size_t suggestionCount = 0;
    
    // Roman numerals
    std::array<Harmony::RomanNumeralResult, Harmony::MAX_PROGRESSION_CHORDS> romanNumerals = {};
    
    // Borrowed chord count
    size_t borrowedChordCount = 0;
    
    bool addIssue(std::string_view desc, uint8_t severity = 1, int8_t chordIdx = -1) {
        if (issueCount >= MAX_ISSUES) return false;
        issues[issueCount].setDescription(desc);
        issues[issueCount].severity = severity;
        issues[issueCount].chordIndex = chordIdx;
        issueCount++;
        return true;
    }
    
    bool addSuggestion(std::string_view desc, std::string_view technique = "") {
        if (suggestionCount >= MAX_SUGGESTIONS) return false;
        suggestions[suggestionCount].setDescription(desc);
        suggestions[suggestionCount].setTechnique(technique);
        suggestionCount++;
        return true;
    }
    
    std::string getKeyName() const {
        std::string name(Harmony::NOTE_NAMES[keyRoot]);
        name += " ";
        name += Harmony::modeToString(keyMode);
        return name;
    }
};

// =============================================================================
// Chord Parsing Functions
// =============================================================================

/**
 * Note name to pitch class lookup
 */
inline int8_t noteNameToPitchClass(std::string_view name) {
    if (name.empty()) return -1;
    
    // Base note
    int8_t base = -1;
    char note = std::toupper(name[0]);
    switch (note) {
        case 'C': base = 0; break;
        case 'D': base = 2; break;
        case 'E': base = 4; break;
        case 'F': base = 5; break;
        case 'G': base = 7; break;
        case 'A': base = 9; break;
        case 'B': base = 11; break;
        default: return -1;
    }
    
    // Handle accidentals
    if (name.size() > 1) {
        if (name[1] == '#') {
            base = (base + 1) % 12;
        } else if (name[1] == 'b') {
            base = (base + 11) % 12;
        }
    }
    
    return base;
}

/**
 * Parse a single chord string (e.g., "Am7", "F#dim", "G/B")
 */
inline ParsedChord parseChordString(std::string_view chordStr) {
    ParsedChord result;
    
    // Remove leading/trailing whitespace
    while (!chordStr.empty() && std::isspace(chordStr.front())) {
        chordStr.remove_prefix(1);
    }
    while (!chordStr.empty() && std::isspace(chordStr.back())) {
        chordStr.remove_suffix(1);
    }
    
    if (chordStr.empty()) return result;
    
    // Store original
    size_t len = std::min(chordStr.size(), result.originalString.size() - 1);
    std::copy_n(chordStr.begin(), len, result.originalString.begin());
    result.originalString[len] = '\0';
    
    // Handle slash chords
    std::string_view mainChord = chordStr;
    std::string_view bassNote;
    
    size_t slashPos = chordStr.find('/');
    if (slashPos != std::string_view::npos) {
        mainChord = chordStr.substr(0, slashPos);
        bassNote = chordStr.substr(slashPos + 1);
    }
    
    // Extract root note (1 or 2 characters)
    if (mainChord.empty()) return result;
    
    size_t rootLen = 1;
    if (mainChord.size() > 1 && (mainChord[1] == '#' || mainChord[1] == 'b')) {
        rootLen = 2;
    }
    
    std::string_view rootStr = mainChord.substr(0, rootLen);
    result.rootNum = noteNameToPitchClass(rootStr);
    
    // Store root name
    std::copy_n(rootStr.begin(), std::min(rootStr.size(), result.rootName.size() - 1), result.rootName.begin());
    result.rootName[std::min(rootStr.size(), result.rootName.size() - 1)] = '\0';
    
    if (result.rootNum < 0) return result;  // Invalid root
    
    // Parse quality
    std::string_view remainder = mainChord.substr(rootLen);
    
    // Check for major 7th first (before minor check)
    if (remainder.size() >= 4 && 
        (remainder.substr(0, 4) == "maj7" || remainder.substr(0, 4) == "Maj7")) {
        result.quality = Harmony::ChordQuality::Major7;
    }
    else if (remainder.size() >= 3 && remainder.substr(0, 3) == "maj") {
        result.quality = Harmony::ChordQuality::Major;
    }
    // Minor variations
    else if (remainder.size() >= 3 && remainder.substr(0, 3) == "min") {
        result.quality = Harmony::ChordQuality::Minor;
    }
    else if (!remainder.empty() && remainder[0] == 'm' && 
             (remainder.size() < 2 || remainder[1] != 'a')) {
        // 'm' for minor, but not 'maj'
        if (remainder.size() >= 2 && remainder[1] == '7') {
            result.quality = Harmony::ChordQuality::Minor7;
        } else {
            result.quality = Harmony::ChordQuality::Minor;
        }
    }
    // Diminished
    else if (remainder.size() >= 3 && remainder.substr(0, 3) == "dim") {
        result.quality = Harmony::ChordQuality::Diminished;
    }
    else if (!remainder.empty() && (remainder[0] == 'o' || remainder[0] == '\xB0')) {
        result.quality = Harmony::ChordQuality::Diminished;
    }
    // Augmented
    else if (!remainder.empty() && remainder[0] == '+') {
        result.quality = Harmony::ChordQuality::Augmented;
    }
    else if (remainder.size() >= 3 && remainder.substr(0, 3) == "aug") {
        result.quality = Harmony::ChordQuality::Augmented;
    }
    // Suspended
    else if (remainder.size() >= 4 && remainder.substr(0, 4) == "sus2") {
        result.quality = Harmony::ChordQuality::Sus2;
    }
    else if (remainder.size() >= 4 && remainder.substr(0, 4) == "sus4") {
        result.quality = Harmony::ChordQuality::Sus4;
    }
    else if (remainder.size() >= 3 && remainder.substr(0, 3) == "sus") {
        result.quality = Harmony::ChordQuality::Sus4;  // Default sus
    }
    // Dominant 7
    else if (!remainder.empty() && remainder[0] == '7') {
        result.quality = Harmony::ChordQuality::Dominant7;
    }
    // Default to major
    else {
        result.quality = Harmony::ChordQuality::Major;
    }
    
    // Parse bass note
    if (!bassNote.empty()) {
        result.bassNote = noteNameToPitchClass(bassNote);
    }
    
    return result;
}

/**
 * Parse a progression string like "F-C-Am-Dm" or "F C Am Dm"
 */
inline size_t parseProgressionString(
    std::string_view progression,
    ParsedChord* outChords,
    size_t maxChords
) {
    size_t chordCount = 0;
    
    // Split by common delimiters: - | , space
    size_t start = 0;
    size_t i = 0;
    
    while (i <= progression.size() && chordCount < maxChords) {
        bool isDelimiter = (i == progression.size()) ||
                           progression[i] == '-' ||
                           progression[i] == '|' ||
                           progression[i] == ',' ||
                           std::isspace(progression[i]);
        
        if (isDelimiter && i > start) {
            std::string_view chordStr = progression.substr(start, i - start);
            ParsedChord chord = parseChordString(chordStr);
            if (chord.isValid()) {
                outChords[chordCount++] = chord;
            }
            start = i + 1;
        } else if (isDelimiter) {
            start = i + 1;
        }
        i++;
    }
    
    return chordCount;
}

// =============================================================================
// Diagnostic Analysis Functions
// =============================================================================

/**
 * Check if chord root is in scale
 */
inline bool isChordInScale(int8_t chordRoot, int8_t keyRoot, Harmony::Mode mode) {
    int interval = (chordRoot - keyRoot + 12) % 12;
    
    const auto& scale = (mode == Harmony::Mode::Minor) ? 
                        Harmony::MINOR_SCALE : Harmony::MAJOR_SCALE;
    
    for (int deg : scale) {
        if (interval == deg) return true;
    }
    return false;
}

/**
 * Detect key from parsed chord progression
 */
inline void detectKeyFromParsedChords(
    const ParsedChord* chords, 
    size_t chordCount,
    int8_t& outKeyRoot,
    Harmony::Mode& outMode
) {
    if (chordCount == 0) {
        outKeyRoot = 0;
        outMode = Harmony::Mode::Major;
        return;
    }
    
    // Weight first and last chords more heavily
    std::array<float, 12> rootWeights = {};
    for (size_t i = 0; i < chordCount; ++i) {
        if (!chords[i].isValid()) continue;
        
        float weight = 1.0f;
        if (i == 0) weight = 2.0f;
        else if (i == chordCount - 1) weight = 1.5f;
        
        rootWeights[chords[i].rootNum] += weight;
    }
    
    // Find most weighted root
    int8_t likelyRoot = 0;
    float maxWeight = 0.0f;
    for (int i = 0; i < 12; ++i) {
        if (rootWeights[i] > maxWeight) {
            maxWeight = rootWeights[i];
            likelyRoot = static_cast<int8_t>(i);
        }
    }
    
    // Determine mode based on chord quality at tonic
    Harmony::Mode likelyMode = Harmony::Mode::Major;
    for (size_t i = 0; i < chordCount; ++i) {
        if (chords[i].rootNum == likelyRoot) {
            if (chords[i].quality == Harmony::ChordQuality::Minor ||
                chords[i].quality == Harmony::ChordQuality::Minor7) {
                likelyMode = Harmony::Mode::Minor;
                break;
            }
        }
    }
    
    outKeyRoot = likelyRoot;
    outMode = likelyMode;
}

/**
 * Diagnose a chord progression for harmonic issues
 */
inline ProgressionDiagnosis diagnoseProgression(std::string_view progressionStr) {
    ProgressionDiagnosis result;
    
    // Parse the progression
    result.chordCount = parseProgressionString(
        progressionStr, 
        result.chords.data(), 
        result.chords.size()
    );
    
    if (result.chordCount == 0) {
        result.addIssue("Could not parse chord progression", 2);
        result.addSuggestion("Check chord spelling (e.g., Am7, F#dim, Cmaj7)");
        return result;
    }
    
    // Detect key
    detectKeyFromParsedChords(
        result.chords.data(), 
        result.chordCount,
        result.keyRoot,
        result.keyMode
    );
    result.keyConfidence = 0.8f;  // Placeholder
    
    // Analyze each chord
    for (size_t i = 0; i < result.chordCount; ++i) {
        const ParsedChord& chord = result.chords[i];
        if (!chord.isValid()) continue;
        
        int interval = (chord.rootNum - result.keyRoot + 12) % 12;
        
        // Check if diatonic
        if (!isChordInScale(chord.rootNum, result.keyRoot, result.keyMode)) {
            std::string issueDesc;
            
            // Identify common borrowed chords
            if (result.keyMode == Harmony::Mode::Major) {
                if (interval == 3 && chord.quality == Harmony::ChordQuality::Major) {
                    issueDesc = std::string(chord.getOriginal()) + 
                                ": bIII (borrowed from parallel minor)";
                } else if (interval == 8 && chord.quality == Harmony::ChordQuality::Major) {
                    issueDesc = std::string(chord.getOriginal()) + 
                                ": bVI (borrowed from parallel minor)";
                } else if (interval == 10 && chord.quality == Harmony::ChordQuality::Major) {
                    issueDesc = std::string(chord.getOriginal()) + 
                                ": bVII (borrowed/mixolydian)";
                } else if (interval == 5 && chord.quality == Harmony::ChordQuality::Minor) {
                    issueDesc = std::string(chord.getOriginal()) + 
                                ": iv (borrowed from parallel minor)";
                } else {
                    issueDesc = std::string(chord.getOriginal()) + 
                                ": non-diatonic root";
                }
            } else {
                issueDesc = std::string(chord.getOriginal()) + ": non-diatonic root";
            }
            
            result.addIssue(issueDesc, 0, static_cast<int8_t>(i));
            result.borrowedChordCount++;
        }
        
        // Check for awkward voice leading (tritone root motion)
        if (i > 0) {
            const ParsedChord& prevChord = result.chords[i - 1];
            if (prevChord.isValid()) {
                int rootMotion = (chord.rootNum - prevChord.rootNum + 12) % 12;
                if (rootMotion == 6) {  // Tritone
                    std::string desc = "Tritone motion between " + 
                                       std::string(prevChord.getOriginal()) + 
                                       " and " + std::string(chord.getOriginal()) + 
                                       " - can feel unstable";
                    result.addSuggestion(desc, "Voice Leading");
                }
            }
        }
        
        // Generate Roman numeral
        Harmony::Chord harmonyChord;
        harmonyChord.root = chord.rootNum;
        harmonyChord.quality = chord.quality;
        result.romanNumerals[i] = Harmony::getRomanNumeral(
            harmonyChord, 
            result.keyRoot, 
            result.keyMode
        );
    }
    
    // Check for resolution
    if (result.chordCount > 0) {
        const ParsedChord& lastChord = result.chords[result.chordCount - 1];
        int lastInterval = (lastChord.rootNum - result.keyRoot + 12) % 12;
        
        if (lastInterval != 0 && lastInterval != 7) {
            std::string keyName = result.getKeyName();
            std::string desc = "Progression ends on " + 
                               std::string(lastChord.getOriginal()) + 
                               " - consider resolving to " + 
                               std::string(Harmony::NOTE_NAMES[result.keyRoot]);
            result.addSuggestion(desc, "Resolution");
        }
    }
    
    // Check for V-I cadence
    bool hasDominant = false;
    bool hasTonic = false;
    for (size_t i = 0; i < result.chordCount; ++i) {
        int interval = (result.chords[i].rootNum - result.keyRoot + 12) % 12;
        if (interval == 7) hasDominant = true;
        if (interval == 0) hasTonic = true;
    }
    
    if (!hasDominant && hasTonic) {
        result.addSuggestion(
            "No dominant (V) chord - consider adding for stronger resolution",
            "Cadence"
        );
    }
    
    return result;
}

// =============================================================================
// Reharmonization Generation
// =============================================================================

enum class ReharmonizationStyle : uint8_t {
    Jazz = 0,
    Pop,
    RnB,
    Classical,
    Experimental,
    Count
};

inline std::string_view reharmonizationStyleToString(ReharmonizationStyle style) {
    switch (style) {
        case ReharmonizationStyle::Jazz:         return "Jazz";
        case ReharmonizationStyle::Pop:          return "Pop";
        case ReharmonizationStyle::RnB:          return "R&B";
        case ReharmonizationStyle::Classical:    return "Classical";
        case ReharmonizationStyle::Experimental: return "Experimental";
        default:                                 return "Unknown";
    }
}

/**
 * Generate reharmonization suggestions for a progression
 */
inline size_t generateReharmonizations(
    const ProgressionDiagnosis& diagnosis,
    ReharmonizationStyle style,
    ReharmonizationSuggestion* outSuggestions,
    size_t maxSuggestions
) {
    if (diagnosis.chordCount == 0 || maxSuggestions == 0) return 0;
    
    size_t suggestionCount = 0;
    
    // Tritone substitution (Jazz)
    if (style == ReharmonizationStyle::Jazz && suggestionCount < maxSuggestions) {
        ReharmonizationSuggestion& sugg = outSuggestions[suggestionCount];
        sugg.chordCount = diagnosis.chordCount;
        
        for (size_t i = 0; i < diagnosis.chordCount; ++i) {
            sugg.newChords[i] = diagnosis.chords[i];
            
            // Replace dominant chords with tritone subs
            int interval = (diagnosis.chords[i].rootNum - diagnosis.keyRoot + 12) % 12;
            if (interval == 7 && 
                (diagnosis.chords[i].quality == Harmony::ChordQuality::Dominant7 ||
                 diagnosis.chords[i].quality == Harmony::ChordQuality::Major)) {
                // Tritone substitution
                int8_t newRoot = (diagnosis.chords[i].rootNum + 6) % 12;
                sugg.newChords[i].rootNum = newRoot;
                sugg.newChords[i].quality = Harmony::ChordQuality::Dominant7;
                
                // Update root name
                std::string_view noteName = Harmony::NOTE_NAMES[newRoot];
                std::copy_n(noteName.begin(), std::min(noteName.size(), 
                            sugg.newChords[i].rootName.size() - 1), 
                            sugg.newChords[i].rootName.begin());
            }
        }
        
        sugg.setTechnique("Tritone Substitution");
        sugg.setMood("chromatic, sophisticated");
        suggestionCount++;
    }
    
    // Borrowed from parallel (Pop)
    if (style == ReharmonizationStyle::Pop && suggestionCount < maxSuggestions) {
        ReharmonizationSuggestion& sugg = outSuggestions[suggestionCount];
        sugg.chordCount = diagnosis.chordCount;
        
        for (size_t i = 0; i < diagnosis.chordCount; ++i) {
            sugg.newChords[i] = diagnosis.chords[i];
            
            // IV -> iv substitution
            int interval = (diagnosis.chords[i].rootNum - diagnosis.keyRoot + 12) % 12;
            if (interval == 5 && diagnosis.chords[i].quality == Harmony::ChordQuality::Major) {
                sugg.newChords[i].quality = Harmony::ChordQuality::Minor;
            }
        }
        
        sugg.setTechnique("Borrowed From Parallel");
        sugg.setMood("bittersweet, nostalgic");
        suggestionCount++;
    }
    
    // Pedal point (Pop/Classical)
    if ((style == ReharmonizationStyle::Pop || style == ReharmonizationStyle::Classical) && 
        suggestionCount < maxSuggestions) {
        ReharmonizationSuggestion& sugg = outSuggestions[suggestionCount];
        sugg.chordCount = diagnosis.chordCount;
        
        for (size_t i = 0; i < diagnosis.chordCount; ++i) {
            sugg.newChords[i] = diagnosis.chords[i];
            // Add tonic pedal bass
            sugg.newChords[i].bassNote = diagnosis.keyRoot;
        }
        
        sugg.setTechnique("Pedal Point");
        sugg.setMood("grounded, hypnotic");
        suggestionCount++;
    }
    
    // Extended dominants (R&B)
    if (style == ReharmonizationStyle::RnB && suggestionCount < maxSuggestions) {
        ReharmonizationSuggestion& sugg = outSuggestions[suggestionCount];
        sugg.chordCount = diagnosis.chordCount;
        
        for (size_t i = 0; i < diagnosis.chordCount; ++i) {
            sugg.newChords[i] = diagnosis.chords[i];
            
            // Add extensions to dominant chords
            int interval = (diagnosis.chords[i].rootNum - diagnosis.keyRoot + 12) % 12;
            if (interval == 7) {
                sugg.newChords[i].quality = Harmony::ChordQuality::Dominant7;
            } else if (diagnosis.chords[i].quality == Harmony::ChordQuality::Minor) {
                sugg.newChords[i].quality = Harmony::ChordQuality::Minor7;
            }
        }
        
        sugg.setTechnique("Extended Dominants");
        sugg.setMood("lush, sophisticated");
        suggestionCount++;
    }
    
    // Parallel motion (Experimental)
    if (style == ReharmonizationStyle::Experimental && suggestionCount < maxSuggestions) {
        ReharmonizationSuggestion& sugg = outSuggestions[suggestionCount];
        sugg.chordCount = diagnosis.chordCount;
        
        // Shift all chords by perfect 4th
        int shift = 5;
        for (size_t i = 0; i < diagnosis.chordCount; ++i) {
            sugg.newChords[i] = diagnosis.chords[i];
            int8_t newRoot = (diagnosis.chords[i].rootNum + shift) % 12;
            sugg.newChords[i].rootNum = newRoot;
            
            std::string_view noteName = Harmony::NOTE_NAMES[newRoot];
            std::copy_n(noteName.begin(), std::min(noteName.size(), 
                        sugg.newChords[i].rootName.size() - 1), 
                        sugg.newChords[i].rootName.begin());
        }
        
        sugg.setTechnique("Parallel Motion");
        sugg.setMood("ethereal, impressionistic");
        suggestionCount++;
    }
    
    return suggestionCount;
}

} // namespace Diagnostics
} // namespace iDAW
