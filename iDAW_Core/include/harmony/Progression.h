/**
 * Progression.h - Chord progression analysis for iDAW
 * 
 * Provides progression parsing, key detection, and Roman numeral analysis.
 */

#pragma once

#include "Chord.h"
#include <string>
#include <vector>
#include <map>
#include <optional>

namespace iDAW {
namespace harmony {

/**
 * Musical modes with their scale degrees (semitones from root)
 */
enum class Mode : uint8_t {
    Major = 0,
    Minor,
    Dorian,
    Phrygian,
    Lydian,
    Mixolydian,
    Locrian
};

/**
 * Get scale degrees for a mode
 */
inline std::vector<int> getScaleDegrees(Mode mode) {
    switch (mode) {
        case Mode::Major:      return {0, 2, 4, 5, 7, 9, 11};
        case Mode::Minor:      return {0, 2, 3, 5, 7, 8, 10};
        case Mode::Dorian:     return {0, 2, 3, 5, 7, 9, 10};
        case Mode::Phrygian:   return {0, 1, 3, 5, 7, 8, 10};
        case Mode::Lydian:     return {0, 2, 4, 6, 7, 9, 11};
        case Mode::Mixolydian: return {0, 2, 4, 5, 7, 9, 10};
        case Mode::Locrian:    return {0, 1, 3, 5, 6, 8, 10};
        default:               return {0, 2, 4, 5, 7, 9, 11};
    }
}

/**
 * Get mode name as string
 */
inline std::string modeToString(Mode mode) {
    switch (mode) {
        case Mode::Major:      return "major";
        case Mode::Minor:      return "minor";
        case Mode::Dorian:     return "dorian";
        case Mode::Phrygian:   return "phrygian";
        case Mode::Lydian:     return "lydian";
        case Mode::Mixolydian: return "mixolydian";
        case Mode::Locrian:    return "locrian";
        default:               return "major";
    }
}

/**
 * Key signature representation
 */
struct Key {
    int root;      // 0-11
    Mode mode;
    
    std::string toString() const {
        return std::string(NOTE_NAMES[root % 12]) + " " + modeToString(mode);
    }
    
    bool operator==(const Key& other) const {
        return root == other.root && mode == other.mode;
    }
};

/**
 * Chord progression with analysis data
 */
class Progression {
public:
    Progression() = default;
    
    /**
     * Construct from vector of chords
     */
    explicit Progression(const std::vector<Chord>& chords);
    
    /**
     * Parse progression from string (e.g., "F-C-Am-Dm")
     */
    static std::optional<Progression> fromString(const std::string& progressionStr);
    
    // Accessors
    const std::vector<Chord>& chords() const noexcept { return m_chords; }
    const Key& key() const noexcept { return m_key; }
    const std::vector<std::string>& romanNumerals() const noexcept { return m_romanNumerals; }
    
    /**
     * Get chord at index
     */
    const Chord& at(size_t index) const { return m_chords.at(index); }
    Chord& at(size_t index) { return m_chords.at(index); }
    
    /**
     * Get number of chords
     */
    size_t size() const noexcept { return m_chords.size(); }
    bool empty() const noexcept { return m_chords.empty(); }
    
    /**
     * Add chord to progression
     */
    void addChord(const Chord& chord);
    
    /**
     * Detect key from chord content
     */
    Key detectKey() const;
    
    /**
     * Analyze and compute Roman numerals
     */
    void analyze();
    
    /**
     * Get Roman numeral for a chord relative to key
     */
    std::string getRomanNumeral(const Chord& chord) const;
    
    /**
     * Identify borrowed chords (from parallel mode)
     */
    std::map<std::string, std::string> identifyBorrowedChords() const;
    
    /**
     * Check if chord root is diatonic to key
     */
    bool isDiatonic(const Chord& chord) const;
    
    /**
     * Get progression as string
     */
    std::string toString() const;
    
private:
    std::vector<Chord> m_chords;
    Key m_key{0, Mode::Major};
    std::vector<std::string> m_romanNumerals;
    bool m_analyzed = false;
};

/**
 * Parse a chord string into a Chord object
 */
std::optional<Chord> parseChord(const std::string& chordStr);

/**
 * Parse a progression string into individual chord strings
 */
std::vector<std::string> splitProgressionString(const std::string& progressionStr);

} // namespace harmony
} // namespace iDAW
