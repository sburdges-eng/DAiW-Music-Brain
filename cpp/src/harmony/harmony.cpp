/**
 * DAiW Harmony Analysis Implementation
 *
 * Chord detection, key analysis, and harmonic utilities.
 */

#include "daiw/harmony.hpp"
#include "daiw/core.hpp"

#include <cmath>
#include <algorithm>

namespace daiw {
namespace harmony {

// =============================================================================
// Note Names and Formatting
// =============================================================================

const char* note_name(NoteName note, bool use_flats) {
    static const char* sharp_names[] = {
        "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
    };
    static const char* flat_names[] = {
        "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"
    };

    int index = static_cast<int>(note);
    if (index < 0 || index >= 12) return "?";

    return use_flats ? flat_names[index] : sharp_names[index];
}

NoteName note_from_name(const std::string& name) {
    if (name.empty()) return NoteName::C;

    char base = std::toupper(name[0]);
    int note = 0;

    switch (base) {
        case 'C': note = 0; break;
        case 'D': note = 2; break;
        case 'E': note = 4; break;
        case 'F': note = 5; break;
        case 'G': note = 7; break;
        case 'A': note = 9; break;
        case 'B': note = 11; break;
        default: return NoteName::C;
    }

    if (name.size() > 1) {
        if (name[1] == '#' || name[1] == 's') note++;
        else if (name[1] == 'b' || name[1] == 'f') note--;
    }

    return static_cast<NoteName>((note + 12) % 12);
}

// =============================================================================
// Scale Utilities
// =============================================================================

const char* scale_type_name(ScaleType type) {
    switch (type) {
        case ScaleType::Major: return "Major";
        case ScaleType::NaturalMinor: return "Natural Minor";
        case ScaleType::HarmonicMinor: return "Harmonic Minor";
        case ScaleType::MelodicMinor: return "Melodic Minor";
        case ScaleType::Dorian: return "Dorian";
        case ScaleType::Phrygian: return "Phrygian";
        case ScaleType::Lydian: return "Lydian";
        case ScaleType::Mixolydian: return "Mixolydian";
        case ScaleType::Locrian: return "Locrian";
        case ScaleType::WholeTone: return "Whole Tone";
        case ScaleType::Diminished: return "Diminished";
        case ScaleType::Chromatic: return "Chromatic";
        case ScaleType::Pentatonic: return "Pentatonic";
        case ScaleType::MinorPentatonic: return "Minor Pentatonic";
        case ScaleType::Blues: return "Blues";
        default: return "Unknown";
    }
}

// =============================================================================
// Chord Quality Names
// =============================================================================

const char* chord_quality_name(ChordQuality quality) {
    switch (quality) {
        case ChordQuality::Major: return "Major";
        case ChordQuality::Minor: return "Minor";
        case ChordQuality::Diminished: return "Diminished";
        case ChordQuality::Augmented: return "Augmented";
        case ChordQuality::Dominant7: return "Dominant 7";
        case ChordQuality::Major7: return "Major 7";
        case ChordQuality::Minor7: return "Minor 7";
        case ChordQuality::Diminished7: return "Diminished 7";
        case ChordQuality::HalfDiminished7: return "Half Diminished 7";
        case ChordQuality::Augmented7: return "Augmented 7";
        case ChordQuality::Sus2: return "Suspended 2";
        case ChordQuality::Sus4: return "Suspended 4";
        case ChordQuality::Add9: return "Add 9";
        case ChordQuality::Minor9: return "Minor 9";
        case ChordQuality::Major9: return "Major 9";
        case ChordQuality::Dominant9: return "Dominant 9";
        case ChordQuality::Power: return "Power";
        default: return "Unknown";
    }
}

const char* chord_quality_symbol(ChordQuality quality) {
    switch (quality) {
        case ChordQuality::Major: return "";
        case ChordQuality::Minor: return "m";
        case ChordQuality::Diminished: return "dim";
        case ChordQuality::Augmented: return "aug";
        case ChordQuality::Dominant7: return "7";
        case ChordQuality::Major7: return "maj7";
        case ChordQuality::Minor7: return "m7";
        case ChordQuality::Diminished7: return "dim7";
        case ChordQuality::HalfDiminished7: return "m7b5";
        case ChordQuality::Augmented7: return "aug7";
        case ChordQuality::Sus2: return "sus2";
        case ChordQuality::Sus4: return "sus4";
        case ChordQuality::Add9: return "add9";
        case ChordQuality::Minor9: return "m9";
        case ChordQuality::Major9: return "maj9";
        case ChordQuality::Dominant9: return "9";
        case ChordQuality::Power: return "5";
        default: return "?";
    }
}

// =============================================================================
// Interval Calculations
// =============================================================================

namespace intervals {

const char* interval_name(int semitones) {
    static const char* names[] = {
        "P1",   // 0 - Unison
        "m2",   // 1 - Minor 2nd
        "M2",   // 2 - Major 2nd
        "m3",   // 3 - Minor 3rd
        "M3",   // 4 - Major 3rd
        "P4",   // 5 - Perfect 4th
        "TT",   // 6 - Tritone
        "P5",   // 7 - Perfect 5th
        "m6",   // 8 - Minor 6th
        "M6",   // 9 - Major 6th
        "m7",   // 10 - Minor 7th
        "M7",   // 11 - Major 7th
    };

    int idx = ((semitones % 12) + 12) % 12;
    return names[idx];
}

/**
 * Calculate interval between two notes (in semitones, 0-11).
 */
int between(NoteName from, NoteName to) {
    int diff = static_cast<int>(to) - static_cast<int>(from);
    return ((diff % 12) + 12) % 12;
}

/**
 * Check if interval is consonant.
 */
bool is_consonant(int semitones) {
    int interval = ((semitones % 12) + 12) % 12;
    // P1, m3, M3, P4, P5, m6, M6 are consonant
    return interval == 0 || interval == 3 || interval == 4 ||
           interval == 5 || interval == 7 || interval == 8 || interval == 9;
}

/**
 * Check if interval is perfect.
 */
bool is_perfect(int semitones) {
    int interval = ((semitones % 12) + 12) % 12;
    return interval == 0 || interval == 5 || interval == 7;
}

} // namespace intervals

// =============================================================================
// Circle of Fifths Utilities
// =============================================================================

namespace circle_of_fifths {

/**
 * Get the key that is n fifths away from the given key.
 * Positive n = clockwise (sharps), negative = counter-clockwise (flats).
 */
NoteName move(NoteName from, int fifths) {
    int note = static_cast<int>(from);
    note = (note + fifths * 7) % 12;
    if (note < 0) note += 12;
    return static_cast<NoteName>(note);
}

/**
 * Get the number of sharps/flats for a major key.
 * Positive = sharps, negative = flats.
 */
int accidentals(NoteName key) {
    // C=0, G=1, D=2, A=3, E=4, B=5, F#=6, C#=7
    // F=-1, Bb=-2, Eb=-3, Ab=-4, Db=-5, Gb=-6, Cb=-7
    static const int acc[] = {0, 7, 2, -3, 4, -1, 6, 1, -4, 3, -2, 5};
    int idx = static_cast<int>(key);
    return (idx >= 0 && idx < 12) ? acc[idx] : 0;
}

/**
 * Get the relative minor of a major key.
 */
NoteName relative_minor(NoteName major_key) {
    int note = static_cast<int>(major_key) - 3;
    if (note < 0) note += 12;
    return static_cast<NoteName>(note);
}

/**
 * Get the relative major of a minor key.
 */
NoteName relative_major(NoteName minor_key) {
    int note = (static_cast<int>(minor_key) + 3) % 12;
    return static_cast<NoteName>(note);
}

/**
 * Get the parallel minor of a major key (same root).
 */
NoteName parallel_minor(NoteName major_key) {
    return major_key;  // Same root, different mode
}

} // namespace circle_of_fifths

// =============================================================================
// Chord Progression Analysis
// =============================================================================

/**
 * Analyze the function of a chord in a key.
 */
std::string analyze_chord_function(const Chord& chord, const Scale& key) {
    int root_interval = intervals::between(key.root, chord.root);

    // Determine primary function
    switch (root_interval) {
        case 0:  // I
            return "Tonic";
        case 2:  // ii
            return "Subdominant (ii)";
        case 4:  // iii
            return "Tonic substitute (iii)";
        case 5:  // IV
            return "Subdominant";
        case 7:  // V
            return "Dominant";
        case 9:  // vi
            return "Tonic substitute (vi)";
        case 11: // vii
            return "Dominant function (vii°)";
        default:
            return "Chromatic";
    }
}

/**
 * Suggest next chords based on common progressions.
 */
std::vector<Chord> suggest_next_chords(const Chord& current, const Scale& key) {
    std::vector<Chord> suggestions;

    int current_degree = intervals::between(key.root, current.root);

    // Common chord movements
    std::vector<int> next_degrees;

    switch (current_degree) {
        case 0:  // I -> IV, V, vi, ii
            next_degrees = {5, 7, 9, 2};
            break;
        case 2:  // ii -> V, vii
            next_degrees = {7, 11};
            break;
        case 4:  // iii -> vi, IV
            next_degrees = {9, 5};
            break;
        case 5:  // IV -> V, I, ii
            next_degrees = {7, 0, 2};
            break;
        case 7:  // V -> I, vi
            next_degrees = {0, 9};
            break;
        case 9:  // vi -> ii, IV, V
            next_degrees = {2, 5, 7};
            break;
        case 11: // vii -> I, iii
            next_degrees = {0, 4};
            break;
        default:
            next_degrees = {0, 5, 7};  // Default: go to I, IV, or V
    }

    for (int degree : next_degrees) {
        Chord chord = key.chord_at_degree(degree);
        suggestions.push_back(chord);
    }

    return suggestions;
}

} // namespace harmony
} // namespace daiw
