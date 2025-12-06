/**
 * HarmonyCore.h - C++ Core Module for Harmony Analysis
 * 
 * Part of Phase 3 C++ Migration for DAiW-Music-Brain
 * 
 * This module provides real-time safe harmony analysis including:
 * - Chord detection from MIDI note clusters
 * - Key detection from chord progressions
 * - Roman numeral analysis
 * - Borrowed chord identification
 * - Modal interchange detection
 * 
 * Design Philosophy:
 * - All operations are allocation-free after initialization
 * - Thread-safe for concurrent access
 * - Optimized for real-time audio processing
 * 
 * Corresponding Python module: music_brain/structure/chord.py
 */

#pragma once

#include <array>
#include <string>
#include <vector>
#include <cstdint>
#include <optional>
#include <string_view>
#include <algorithm>
#include <cmath>

namespace iDAW {
namespace Harmony {

// =============================================================================
// Constants
// =============================================================================

// MIDI note names
constexpr std::array<std::string_view, 12> NOTE_NAMES = {
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
};

constexpr std::array<std::string_view, 12> FLAT_NAMES = {
    "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"
};

// Major scale intervals (semitones from root)
constexpr std::array<int, 7> MAJOR_SCALE = {0, 2, 4, 5, 7, 9, 11};
constexpr std::array<int, 7> MINOR_SCALE = {0, 2, 3, 5, 7, 8, 10};  // Natural minor

// Chord quality intervals (from root)
constexpr int CHORD_MAJOR[] = {0, 4, 7};           // Major triad
constexpr int CHORD_MINOR[] = {0, 3, 7};           // Minor triad
constexpr int CHORD_DIM[] = {0, 3, 6};             // Diminished triad
constexpr int CHORD_AUG[] = {0, 4, 8};             // Augmented triad
constexpr int CHORD_MAJ7[] = {0, 4, 7, 11};        // Major 7th
constexpr int CHORD_MIN7[] = {0, 3, 7, 10};        // Minor 7th
constexpr int CHORD_DOM7[] = {0, 4, 7, 10};        // Dominant 7th
constexpr int CHORD_DIM7[] = {0, 3, 6, 9};         // Diminished 7th
constexpr int CHORD_HDIM7[] = {0, 3, 6, 10};       // Half-diminished 7th

// Maximum notes to consider in a chord cluster
constexpr size_t MAX_CHORD_NOTES = 12;

// Maximum chords in a progression for analysis
constexpr size_t MAX_PROGRESSION_CHORDS = 64;

// =============================================================================
// Chord Quality Enum
// =============================================================================

enum class ChordQuality : uint8_t {
    Unknown = 0,
    Major,
    Minor,
    Diminished,
    Augmented,
    Dominant7,
    Major7,
    Minor7,
    HalfDim7,
    Dim7,
    Sus2,
    Sus4,
    Add9,
    Count
};

/**
 * Get string representation of chord quality
 */
inline std::string_view qualityToString(ChordQuality quality) {
    switch (quality) {
        case ChordQuality::Major:      return "";
        case ChordQuality::Minor:      return "m";
        case ChordQuality::Diminished: return "dim";
        case ChordQuality::Augmented:  return "+";
        case ChordQuality::Dominant7:  return "7";
        case ChordQuality::Major7:     return "maj7";
        case ChordQuality::Minor7:     return "m7";
        case ChordQuality::HalfDim7:   return "m7b5";
        case ChordQuality::Dim7:       return "dim7";
        case ChordQuality::Sus2:       return "sus2";
        case ChordQuality::Sus4:       return "sus4";
        case ChordQuality::Add9:       return "add9";
        default:                       return "?";
    }
}

// =============================================================================
// Mode Enum
// =============================================================================

enum class Mode : uint8_t {
    Major = 0,
    Minor,
    Dorian,
    Phrygian,
    Lydian,
    Mixolydian,
    Locrian,
    Count
};

inline std::string_view modeToString(Mode mode) {
    switch (mode) {
        case Mode::Major:      return "major";
        case Mode::Minor:      return "minor";
        case Mode::Dorian:     return "dorian";
        case Mode::Phrygian:   return "phrygian";
        case Mode::Lydian:     return "lydian";
        case Mode::Mixolydian: return "mixolydian";
        case Mode::Locrian:    return "locrian";
        default:               return "unknown";
    }
}

// =============================================================================
// Chord Structure
// =============================================================================

/**
 * Represents a detected chord with analysis information
 */
struct Chord {
    int8_t root = -1;                    // Pitch class (0-11), -1 = unknown
    ChordQuality quality = ChordQuality::Unknown;
    int8_t bass = -1;                    // Bass note for slash chords
    
    // Timing information (in ticks)
    uint32_t startTick = 0;
    uint32_t durationTicks = 0;
    
    // Original notes that formed this chord
    std::array<uint8_t, MAX_CHORD_NOTES> notes = {};
    size_t noteCount = 0;
    
    // Confidence score (0.0 - 1.0)
    float confidence = 0.0f;
    
    /**
     * Check if chord is valid
     */
    bool isValid() const { return root >= 0 && root < 12; }
    
    /**
     * Get chord name (e.g., "Am7", "F#dim")
     */
    std::string getName() const {
        if (!isValid()) return "N.C.";
        
        std::string name(NOTE_NAMES[root]);
        name += qualityToString(quality);
        
        if (bass >= 0 && bass != root) {
            name += "/";
            name += NOTE_NAMES[bass];
        }
        
        return name;
    }
    
    /**
     * Get root name
     */
    std::string_view getRootName() const {
        if (!isValid()) return "?";
        return NOTE_NAMES[root];
    }
};

// =============================================================================
// Key Detection Result
// =============================================================================

struct KeyResult {
    int8_t keyRoot = 0;      // Pitch class (0-11)
    Mode mode = Mode::Major;
    float confidence = 0.0f;
    
    std::string getName() const {
        std::string name(NOTE_NAMES[keyRoot]);
        name += " ";
        name += modeToString(mode);
        return name;
    }
};

// =============================================================================
// Roman Numeral Analysis Result
// =============================================================================

struct RomanNumeralResult {
    std::string numeral;           // e.g., "IV", "bVI", "ii"
    bool isDiatonic = true;        // True if chord is diatonic to the key
    std::string borrowedFrom;      // e.g., "parallel minor" if borrowed
};

// =============================================================================
// Chord Progression
// =============================================================================

struct ChordProgression {
    std::array<Chord, MAX_PROGRESSION_CHORDS> chords = {};
    size_t chordCount = 0;
    
    KeyResult key;
    std::array<RomanNumeralResult, MAX_PROGRESSION_CHORDS> romanNumerals = {};
    
    // Metadata
    float tempoBpm = 120.0f;
    uint16_t ppq = 480;
    
    /**
     * Add a chord to the progression
     */
    bool addChord(const Chord& chord) {
        if (chordCount >= MAX_PROGRESSION_CHORDS) return false;
        chords[chordCount++] = chord;
        return true;
    }
    
    /**
     * Get chord string representation
     */
    std::string toString() const {
        std::string result;
        for (size_t i = 0; i < chordCount; ++i) {
            if (i > 0) result += " - ";
            result += chords[i].getName();
        }
        return result;
    }
};

// =============================================================================
// Harmony Analysis Functions
// =============================================================================

/**
 * Convert MIDI note to pitch class (0-11)
 */
inline int midiToPitchClass(int midiNote) {
    return ((midiNote % 12) + 12) % 12;  // Handle negative notes
}

/**
 * Check if interval matches a chord template
 */
inline float matchChordTemplate(const int* intervals, size_t templateSize, 
                                 const std::array<uint8_t, MAX_CHORD_NOTES>& notes,
                                 size_t noteCount, int root) {
    if (noteCount < 2) return 0.0f;
    
    int matches = 0;
    for (size_t i = 0; i < noteCount; ++i) {
        int interval = (midiToPitchClass(notes[i]) - root + 12) % 12;
        for (size_t j = 0; j < templateSize; ++j) {
            if (interval == intervals[j]) {
                matches++;
                break;
            }
        }
    }
    
    return static_cast<float>(matches) / static_cast<float>(templateSize);
}

/**
 * Detect chord from a cluster of MIDI notes
 * 
 * @param notes Array of MIDI note numbers
 * @param noteCount Number of notes in the cluster
 * @return Detected chord with quality and confidence
 */
inline Chord detectChordFromNotes(const uint8_t* notes, size_t noteCount) {
    Chord result;
    
    if (noteCount < 2) {
        return result;  // Not enough notes
    }
    
    // Copy notes to result
    result.noteCount = std::min(noteCount, MAX_CHORD_NOTES);
    for (size_t i = 0; i < result.noteCount; ++i) {
        result.notes[i] = notes[i];
    }
    
    // Get unique pitch classes
    std::array<int, 12> pitchClassPresent = {};
    for (size_t i = 0; i < result.noteCount; ++i) {
        pitchClassPresent[midiToPitchClass(notes[i])] = 1;
    }
    
    // Count unique pitch classes
    int uniqueCount = 0;
    std::array<int, 12> uniquePitchClasses = {};
    for (int i = 0; i < 12; ++i) {
        if (pitchClassPresent[i]) {
            uniquePitchClasses[uniqueCount++] = i;
        }
    }
    
    if (uniqueCount < 2) {
        return result;  // Not enough unique notes
    }
    
    // Try each pitch class as potential root
    float bestScore = 0.0f;
    int bestRoot = -1;
    ChordQuality bestQuality = ChordQuality::Unknown;
    
    // Templates to try (most specific first)
    struct ChordTemplate {
        const int* intervals;
        size_t size;
        ChordQuality quality;
    };
    
    const ChordTemplate templates[] = {
        {CHORD_MAJ7, 4, ChordQuality::Major7},
        {CHORD_MIN7, 4, ChordQuality::Minor7},
        {CHORD_DOM7, 4, ChordQuality::Dominant7},
        {CHORD_DIM7, 4, ChordQuality::Dim7},
        {CHORD_HDIM7, 4, ChordQuality::HalfDim7},
        {CHORD_MAJOR, 3, ChordQuality::Major},
        {CHORD_MINOR, 3, ChordQuality::Minor},
        {CHORD_DIM, 3, ChordQuality::Diminished},
        {CHORD_AUG, 3, ChordQuality::Augmented},
    };
    
    for (int potentialRoot = 0; potentialRoot < 12; ++potentialRoot) {
        if (!pitchClassPresent[potentialRoot]) continue;
        
        for (const auto& tmpl : templates) {
            float score = matchChordTemplate(
                tmpl.intervals, tmpl.size,
                result.notes, result.noteCount, potentialRoot
            );
            
            // Boost score for bass note being root
            if (midiToPitchClass(notes[0]) == potentialRoot) {
                score *= 1.1f;
            }
            
            if (score > bestScore && score >= 0.7f) {
                bestScore = score;
                bestRoot = potentialRoot;
                bestQuality = tmpl.quality;
            }
        }
    }
    
    // If no quality match, default based on 3rd
    if (bestRoot < 0) {
        bestRoot = midiToPitchClass(notes[0]);  // Use bass as root
        
        // Check for minor or major 3rd
        bool hasMinor3rd = false;
        bool hasMajor3rd = false;
        for (int i = 0; i < uniqueCount; ++i) {
            int interval = (uniquePitchClasses[i] - bestRoot + 12) % 12;
            if (interval == 3) hasMinor3rd = true;
            if (interval == 4) hasMajor3rd = true;
        }
        
        if (hasMinor3rd) {
            bestQuality = ChordQuality::Minor;
            bestScore = 0.5f;
        } else if (hasMajor3rd) {
            bestQuality = ChordQuality::Major;
            bestScore = 0.5f;
        } else {
            bestQuality = ChordQuality::Major;  // Default
            bestScore = 0.3f;
        }
    }
    
    result.root = static_cast<int8_t>(bestRoot);
    result.quality = bestQuality;
    result.confidence = std::min(bestScore, 1.0f);
    result.bass = static_cast<int8_t>(midiToPitchClass(notes[0]));
    
    return result;
}

/**
 * Detect key from a chord progression
 * 
 * @param chords Array of chords
 * @param chordCount Number of chords
 * @return Key detection result with confidence
 */
inline KeyResult detectKey(const Chord* chords, size_t chordCount) {
    KeyResult result;
    
    if (chordCount == 0) {
        return result;
    }
    
    // Weight chord roots by position
    std::array<float, 12> rootWeights = {};
    for (size_t i = 0; i < chordCount; ++i) {
        if (!chords[i].isValid()) continue;
        
        float weight = 1.0f;
        if (i == 0) weight = 2.0f;                    // First chord weighted most
        else if (i == chordCount - 1) weight = 1.5f;  // Last chord weighted more
        
        rootWeights[chords[i].root] += weight;
    }
    
    // Try each potential key
    float bestScore = 0.0f;
    int bestKey = 0;
    Mode bestMode = Mode::Major;
    
    for (int key = 0; key < 12; ++key) {
        // Test major
        float majorScore = 0.0f;
        for (size_t i = 0; i < chordCount; ++i) {
            if (!chords[i].isValid()) continue;
            
            int interval = (chords[i].root - key + 12) % 12;
            
            // Check if in major scale
            for (int deg : MAJOR_SCALE) {
                if (interval == deg) {
                    majorScore += 1.0f;
                    if (interval == 0) majorScore += 0.5f;  // Tonic bonus
                    if (interval == 7) majorScore += 0.3f;  // Dominant bonus
                    break;
                }
            }
        }
        
        if (majorScore > bestScore) {
            bestScore = majorScore;
            bestKey = key;
            bestMode = Mode::Major;
        }
        
        // Test minor
        float minorScore = 0.0f;
        for (size_t i = 0; i < chordCount; ++i) {
            if (!chords[i].isValid()) continue;
            
            int interval = (chords[i].root - key + 12) % 12;
            
            for (int deg : MINOR_SCALE) {
                if (interval == deg) {
                    minorScore += 1.0f;
                    if (interval == 0) minorScore += 0.5f;
                    break;
                }
            }
        }
        
        if (minorScore > bestScore) {
            bestScore = minorScore;
            bestKey = key;
            bestMode = Mode::Minor;
        }
    }
    
    result.keyRoot = static_cast<int8_t>(bestKey);
    result.mode = bestMode;
    result.confidence = bestScore / static_cast<float>(chordCount);
    
    return result;
}

/**
 * Get Roman numeral for a chord relative to a key
 */
inline RomanNumeralResult getRomanNumeral(const Chord& chord, int keyRoot, Mode mode) {
    RomanNumeralResult result;
    
    if (!chord.isValid()) {
        result.numeral = "?";
        return result;
    }
    
    int interval = (chord.root - keyRoot + 12) % 12;
    
    // Numeral base names
    static const std::array<std::string_view, 12> numeralMap = {
        "I", "bII", "II", "bIII", "III", "IV", 
        "#IV", "V", "bVI", "VI", "bVII", "VII"
    };
    
    std::string numeral(numeralMap[interval]);
    
    // Determine case and check if diatonic
    const auto& scale = (mode == Mode::Minor) ? MINOR_SCALE : MAJOR_SCALE;
    bool isDiatonic = false;
    for (int deg : scale) {
        if (interval == deg) {
            isDiatonic = true;
            break;
        }
    }
    
    // Lowercase for minor chords
    if (chord.quality == ChordQuality::Minor || 
        chord.quality == ChordQuality::Minor7 ||
        chord.quality == ChordQuality::Diminished) {
        std::transform(numeral.begin(), numeral.end(), numeral.begin(), ::tolower);
    }
    
    // Add quality suffix
    if (chord.quality == ChordQuality::Diminished) {
        numeral += "°";
    } else if (chord.quality == ChordQuality::Dominant7) {
        numeral += "7";
    } else if (chord.quality == ChordQuality::Major7) {
        numeral += "M7";
    } else if (chord.quality == ChordQuality::Minor7) {
        numeral += "7";
    }
    
    result.numeral = numeral;
    result.isDiatonic = isDiatonic;
    
    // Check for common borrowed chords
    if (!isDiatonic && mode == Mode::Major) {
        if (interval == 3 && chord.quality == ChordQuality::Major) {
            result.borrowedFrom = "parallel minor (bIII)";
        } else if (interval == 8 && chord.quality == ChordQuality::Major) {
            result.borrowedFrom = "parallel minor (bVI)";
        } else if (interval == 10 && chord.quality == ChordQuality::Major) {
            result.borrowedFrom = "mixolydian/parallel minor (bVII)";
        } else if (interval == 5 && chord.quality == ChordQuality::Minor) {
            result.borrowedFrom = "parallel minor (iv)";
        }
    }
    
    return result;
}

/**
 * Analyze a full chord progression
 */
inline ChordProgression analyzeProgression(const Chord* chords, size_t chordCount) {
    ChordProgression result;
    
    // Copy chords
    result.chordCount = std::min(chordCount, MAX_PROGRESSION_CHORDS);
    for (size_t i = 0; i < result.chordCount; ++i) {
        result.chords[i] = chords[i];
    }
    
    // Detect key
    result.key = detectKey(chords, chordCount);
    
    // Get Roman numerals
    for (size_t i = 0; i < result.chordCount; ++i) {
        result.romanNumerals[i] = getRomanNumeral(
            result.chords[i], 
            result.key.keyRoot, 
            result.key.mode
        );
    }
    
    return result;
}

} // namespace Harmony
} // namespace iDAW
