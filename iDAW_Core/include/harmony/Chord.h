/**
 * Chord.h - Chord representation for iDAW Harmony Engine
 * 
 * Provides efficient C++ chord data structures for real-time
 * chord detection and analysis.
 */

#pragma once

#include <array>
#include <string>
#include <vector>
#include <optional>
#include <cstdint>

namespace iDAW {
namespace harmony {

// Note name constants
constexpr std::array<const char*, 12> NOTE_NAMES = {
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
};

constexpr std::array<const char*, 12> FLAT_NAMES = {
    "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"
};

/**
 * Chord Quality enumeration
 */
enum class ChordQuality : uint8_t {
    Major = 0,
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
    Major6,
    Minor6,
    Unknown
};

/**
 * Get string representation of chord quality
 */
inline std::string qualityToString(ChordQuality quality) {
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
        case ChordQuality::Major6:     return "6";
        case ChordQuality::Minor6:     return "m6";
        default:                       return "?";
    }
}

/**
 * Chord quality interval templates (semitones from root)
 */
struct ChordTemplate {
    ChordQuality quality;
    std::vector<int> intervals;
};

inline const std::vector<ChordTemplate>& getChordTemplates() {
    static const std::vector<ChordTemplate> templates = {
        {ChordQuality::Major,      {0, 4, 7}},
        {ChordQuality::Minor,      {0, 3, 7}},
        {ChordQuality::Diminished, {0, 3, 6}},
        {ChordQuality::Augmented,  {0, 4, 8}},
        {ChordQuality::Major7,     {0, 4, 7, 11}},
        {ChordQuality::Minor7,     {0, 3, 7, 10}},
        {ChordQuality::Dominant7,  {0, 4, 7, 10}},
        {ChordQuality::Dim7,       {0, 3, 6, 9}},
        {ChordQuality::HalfDim7,   {0, 3, 6, 10}},
        {ChordQuality::Sus2,       {0, 2, 7}},
        {ChordQuality::Sus4,       {0, 5, 7}},
        {ChordQuality::Add9,       {0, 4, 7, 14}},
        {ChordQuality::Major6,     {0, 4, 7, 9}},
        {ChordQuality::Minor6,     {0, 3, 7, 9}},
    };
    return templates;
}

/**
 * Chord - Represents a single chord with root, quality, and optional extensions
 * 
 * Optimized for real-time processing with minimal allocations.
 */
class Chord {
public:
    /**
     * Default constructor - creates an empty/invalid chord
     */
    Chord() : m_root(0), m_quality(ChordQuality::Unknown), m_bass(-1) {}
    
    /**
     * Construct chord from root (0-11) and quality
     */
    Chord(int root, ChordQuality quality, int bass = -1)
        : m_root(root % 12), m_quality(quality), m_bass(bass) {}
    
    /**
     * Construct chord from note list (auto-detect quality)
     */
    explicit Chord(const std::vector<int>& midiNotes);
    
    /**
     * Parse chord from string (e.g., "Am7", "F#dim", "Cmaj7")
     */
    static std::optional<Chord> fromString(const std::string& chordStr);
    
    // Getters
    int root() const noexcept { return m_root; }
    ChordQuality quality() const noexcept { return m_quality; }
    int bass() const noexcept { return m_bass; }
    bool hasBass() const noexcept { return m_bass >= 0 && m_bass != m_root; }
    bool isValid() const noexcept { return m_quality != ChordQuality::Unknown; }
    
    /**
     * Get chord name (e.g., "Am7", "F#dim")
     */
    std::string name(bool useFlats = false) const;
    
    /**
     * Get root note name
     */
    std::string rootName(bool useFlats = false) const;
    
    /**
     * Get intervals from root
     */
    std::vector<int> intervals() const;
    
    /**
     * Check if chord contains a specific interval
     */
    bool hasInterval(int interval) const;
    
    /**
     * Get MIDI note numbers for this chord (in a specific octave)
     */
    std::vector<int> midiNotes(int octave = 4) const;
    
    // Comparison
    bool operator==(const Chord& other) const {
        return m_root == other.m_root && m_quality == other.m_quality;
    }
    
    bool operator!=(const Chord& other) const {
        return !(*this == other);
    }
    
private:
    int m_root;           // 0-11 (C=0, C#=1, ..., B=11)
    ChordQuality m_quality;
    int m_bass;           // For slash chords (-1 if same as root)
    std::vector<int> m_notes;  // Original MIDI notes (if constructed from notes)
};

/**
 * Detect chord from a set of MIDI note numbers
 */
Chord detectChord(const std::vector<int>& midiNotes);

/**
 * Get the pitch class (0-11) from a MIDI note number
 */
inline int midiToPitchClass(int midiNote) {
    return ((midiNote % 12) + 12) % 12;  // Handle negative values
}

/**
 * Convert pitch class to MIDI note in given octave
 */
inline int pitchClassToMidi(int pitchClass, int octave = 4) {
    return (octave + 1) * 12 + (pitchClass % 12);
}

} // namespace harmony
} // namespace iDAW
