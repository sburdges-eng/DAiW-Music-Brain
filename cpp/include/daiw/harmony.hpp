/**
 * DAiW Harmony Analysis Module
 *
 * Real-time chord detection, key analysis, and harmonic processing.
 * Assigned to: Gemini
 *
 * Features:
 * - Chord recognition from MIDI/audio
 * - Key detection algorithms
 * - Roman numeral analysis
 * - Chord progression suggestions
 * - Voice leading analysis
 */

#pragma once

#include "daiw/types.hpp"

#include <array>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
#include <optional>

namespace daiw {
namespace harmony {

// =============================================================================
// Constants
// =============================================================================

constexpr int NOTES_PER_OCTAVE = 12;
constexpr int MAX_CHORD_NOTES = 8;

// =============================================================================
// Enums
// =============================================================================

/// Note names (pitch class)
enum class NoteName : uint8_t {
    C = 0, Cs = 1, D = 2, Ds = 3, E = 4, F = 5,
    Fs = 6, G = 7, Gs = 8, A = 9, As = 10, B = 11
};

/// Chord qualities
enum class ChordQuality {
    Major,
    Minor,
    Diminished,
    Augmented,
    Dominant7,
    Major7,
    Minor7,
    Diminished7,
    HalfDiminished7,
    Augmented7,
    Sus2,
    Sus4,
    Add9,
    Minor9,
    Major9,
    Dominant9,
    Power,          // 5th chord
    Unknown
};

/// Scale types
enum class ScaleType {
    Major,
    NaturalMinor,
    HarmonicMinor,
    MelodicMinor,
    Dorian,
    Phrygian,
    Lydian,
    Mixolydian,
    Locrian,
    WholeTone,
    Diminished,     // Whole-half
    Chromatic,
    Pentatonic,
    MinorPentatonic,
    Blues
};

/// Roman numeral degree
enum class Degree {
    I = 0, bII, II, bIII, III, IV, bV, V, bVI, VI, bVII, VII
};

// =============================================================================
// Pitch Class Set
// =============================================================================

/**
 * Compact representation of pitch classes present.
 * Uses a 12-bit bitfield for O(1) operations.
 */
class PitchClassSet {
public:
    PitchClassSet() : bits_(0) {}

    explicit PitchClassSet(uint16_t bits) : bits_(bits & 0x0FFF) {}

    /// Add a pitch class
    void add(int pitch_class) {
        bits_ |= (1 << (pitch_class % NOTES_PER_OCTAVE));
    }

    /// Remove a pitch class
    void remove(int pitch_class) {
        bits_ &= ~(1 << (pitch_class % NOTES_PER_OCTAVE));
    }

    /// Check if pitch class is present
    bool contains(int pitch_class) const {
        return bits_ & (1 << (pitch_class % NOTES_PER_OCTAVE));
    }

    /// Get count of pitch classes
    int count() const {
        int c = 0;
        for (int i = 0; i < NOTES_PER_OCTAVE; ++i) {
            if (bits_ & (1 << i)) c++;
        }
        return c;
    }

    /// Clear all pitch classes
    void clear() { bits_ = 0; }

    /// Get raw bits
    uint16_t bits() const { return bits_; }

    /// Transpose by semitones
    PitchClassSet transpose(int semitones) const {
        int shift = ((semitones % NOTES_PER_OCTAVE) + NOTES_PER_OCTAVE) % NOTES_PER_OCTAVE;
        uint16_t rotated = ((bits_ << shift) | (bits_ >> (NOTES_PER_OCTAVE - shift))) & 0x0FFF;
        return PitchClassSet(rotated);
    }

    /// Get intervals from root
    std::vector<int> intervals_from(int root) const {
        std::vector<int> result;
        PitchClassSet rotated = transpose(-root);
        for (int i = 0; i < NOTES_PER_OCTAVE; ++i) {
            if (rotated.contains(i)) {
                result.push_back(i);
            }
        }
        return result;
    }

    bool operator==(const PitchClassSet& other) const {
        return bits_ == other.bits_;
    }

private:
    uint16_t bits_;
};

// =============================================================================
// Chord
// =============================================================================

/**
 * Represents a chord with root, quality, and extensions.
 */
struct Chord {
    NoteName root = NoteName::C;
    ChordQuality quality = ChordQuality::Major;
    std::optional<NoteName> bass;  // For slash chords
    std::vector<int> extensions;   // Additional intervals (9, 11, 13, etc.)

    /// Get pitch class set for this chord
    PitchClassSet pitch_classes() const {
        PitchClassSet pcs;
        int r = static_cast<int>(root);
        pcs.add(r);

        // Add intervals based on quality
        switch (quality) {
            case ChordQuality::Major:
                pcs.add(r + 4);  // Major 3rd
                pcs.add(r + 7);  // Perfect 5th
                break;
            case ChordQuality::Minor:
                pcs.add(r + 3);  // Minor 3rd
                pcs.add(r + 7);  // Perfect 5th
                break;
            case ChordQuality::Diminished:
                pcs.add(r + 3);  // Minor 3rd
                pcs.add(r + 6);  // Diminished 5th
                break;
            case ChordQuality::Augmented:
                pcs.add(r + 4);  // Major 3rd
                pcs.add(r + 8);  // Augmented 5th
                break;
            case ChordQuality::Dominant7:
                pcs.add(r + 4);
                pcs.add(r + 7);
                pcs.add(r + 10); // Minor 7th
                break;
            case ChordQuality::Major7:
                pcs.add(r + 4);
                pcs.add(r + 7);
                pcs.add(r + 11); // Major 7th
                break;
            case ChordQuality::Minor7:
                pcs.add(r + 3);
                pcs.add(r + 7);
                pcs.add(r + 10);
                break;
            case ChordQuality::Diminished7:
                pcs.add(r + 3);
                pcs.add(r + 6);
                pcs.add(r + 9);  // Diminished 7th
                break;
            case ChordQuality::HalfDiminished7:
                pcs.add(r + 3);
                pcs.add(r + 6);
                pcs.add(r + 10);
                break;
            case ChordQuality::Sus2:
                pcs.add(r + 2);  // Major 2nd
                pcs.add(r + 7);
                break;
            case ChordQuality::Sus4:
                pcs.add(r + 5);  // Perfect 4th
                pcs.add(r + 7);
                break;
            case ChordQuality::Power:
                pcs.add(r + 7);  // Just 5th
                break;
            default:
                pcs.add(r + 4);
                pcs.add(r + 7);
                break;
        }

        // Add extensions
        for (int ext : extensions) {
            pcs.add(r + ext);
        }

        return pcs;
    }

    /// Get chord name as string
    std::string name() const {
        static const char* note_names[] = {
            "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
        };

        std::string result = note_names[static_cast<int>(root)];

        switch (quality) {
            case ChordQuality::Major: break;  // No suffix
            case ChordQuality::Minor: result += "m"; break;
            case ChordQuality::Diminished: result += "dim"; break;
            case ChordQuality::Augmented: result += "aug"; break;
            case ChordQuality::Dominant7: result += "7"; break;
            case ChordQuality::Major7: result += "maj7"; break;
            case ChordQuality::Minor7: result += "m7"; break;
            case ChordQuality::Diminished7: result += "dim7"; break;
            case ChordQuality::HalfDiminished7: result += "m7b5"; break;
            case ChordQuality::Sus2: result += "sus2"; break;
            case ChordQuality::Sus4: result += "sus4"; break;
            case ChordQuality::Power: result += "5"; break;
            default: result += "?"; break;
        }

        if (bass.has_value() && bass.value() != root) {
            result += "/";
            result += note_names[static_cast<int>(bass.value())];
        }

        return result;
    }
};

// =============================================================================
// Scale
// =============================================================================

/**
 * Represents a scale with root and type.
 */
struct Scale {
    NoteName root = NoteName::C;
    ScaleType type = ScaleType::Major;

    /// Get intervals for this scale type
    std::vector<int> intervals() const {
        switch (type) {
            case ScaleType::Major:
                return {0, 2, 4, 5, 7, 9, 11};
            case ScaleType::NaturalMinor:
                return {0, 2, 3, 5, 7, 8, 10};
            case ScaleType::HarmonicMinor:
                return {0, 2, 3, 5, 7, 8, 11};
            case ScaleType::MelodicMinor:
                return {0, 2, 3, 5, 7, 9, 11};
            case ScaleType::Dorian:
                return {0, 2, 3, 5, 7, 9, 10};
            case ScaleType::Phrygian:
                return {0, 1, 3, 5, 7, 8, 10};
            case ScaleType::Lydian:
                return {0, 2, 4, 6, 7, 9, 11};
            case ScaleType::Mixolydian:
                return {0, 2, 4, 5, 7, 9, 10};
            case ScaleType::Locrian:
                return {0, 1, 3, 5, 6, 8, 10};
            case ScaleType::WholeTone:
                return {0, 2, 4, 6, 8, 10};
            case ScaleType::Diminished:
                return {0, 2, 3, 5, 6, 8, 9, 11};
            case ScaleType::Pentatonic:
                return {0, 2, 4, 7, 9};
            case ScaleType::MinorPentatonic:
                return {0, 3, 5, 7, 10};
            case ScaleType::Blues:
                return {0, 3, 5, 6, 7, 10};
            default:
                return {0, 2, 4, 5, 7, 9, 11};
        }
    }

    /// Get pitch class set
    PitchClassSet pitch_classes() const {
        PitchClassSet pcs;
        int r = static_cast<int>(root);
        for (int interval : intervals()) {
            pcs.add(r + interval);
        }
        return pcs;
    }

    /// Check if a note is in the scale
    bool contains(int midi_note) const {
        int pc = midi_note % NOTES_PER_OCTAVE;
        int r = static_cast<int>(root);
        int interval = ((pc - r) % NOTES_PER_OCTAVE + NOTES_PER_OCTAVE) % NOTES_PER_OCTAVE;

        for (int i : intervals()) {
            if (i == interval) return true;
        }
        return false;
    }

    /// Get diatonic chord at degree
    Chord chord_at_degree(int degree) const {
        auto ivls = intervals();
        if (degree < 0 || degree >= static_cast<int>(ivls.size())) {
            return Chord{};
        }

        Chord chord;
        int r = static_cast<int>(root);
        chord.root = static_cast<NoteName>((r + ivls[degree]) % NOTES_PER_OCTAVE);

        // Determine quality based on intervals above root
        int third_degree = (degree + 2) % ivls.size();
        int fifth_degree = (degree + 4) % ivls.size();

        int third_interval = (ivls[third_degree] - ivls[degree] + NOTES_PER_OCTAVE) % NOTES_PER_OCTAVE;
        int fifth_interval = (ivls[fifth_degree] - ivls[degree] + NOTES_PER_OCTAVE) % NOTES_PER_OCTAVE;

        if (third_interval == 4 && fifth_interval == 7) {
            chord.quality = ChordQuality::Major;
        } else if (third_interval == 3 && fifth_interval == 7) {
            chord.quality = ChordQuality::Minor;
        } else if (third_interval == 3 && fifth_interval == 6) {
            chord.quality = ChordQuality::Diminished;
        } else if (third_interval == 4 && fifth_interval == 8) {
            chord.quality = ChordQuality::Augmented;
        } else {
            chord.quality = ChordQuality::Unknown;
        }

        return chord;
    }
};

// =============================================================================
// Chord Detector
// =============================================================================

/**
 * Detects chords from pitch class sets.
 * Uses template matching with weighted scoring.
 */
class ChordDetector {
public:
    struct Detection {
        Chord chord;
        float confidence;  // 0.0 - 1.0
    };

    /// Detect chord from pitch class set
    Detection detect(const PitchClassSet& pcs) const {
        if (pcs.count() < 2) {
            return {Chord{}, 0.0f};
        }

        Detection best{Chord{}, 0.0f};

        // Try each possible root
        for (int root = 0; root < NOTES_PER_OCTAVE; ++root) {
            // Try each chord quality
            for (auto quality : all_qualities_) {
                Chord candidate;
                candidate.root = static_cast<NoteName>(root);
                candidate.quality = quality;

                float score = match_score(pcs, candidate.pitch_classes());
                if (score > best.confidence) {
                    best.chord = candidate;
                    best.confidence = score;
                }
            }
        }

        return best;
    }

    /// Detect chord from MIDI notes
    Detection detect_from_notes(const std::vector<MidiNote>& notes) const {
        PitchClassSet pcs;
        for (MidiNote note : notes) {
            pcs.add(note);
        }
        return detect(pcs);
    }

private:
    float match_score(const PitchClassSet& input, const PitchClassSet& template_pcs) const {
        int matches = 0;
        int template_count = template_pcs.count();
        int input_count = input.count();

        // Count matching pitch classes
        for (int i = 0; i < NOTES_PER_OCTAVE; ++i) {
            if (input.contains(i) && template_pcs.contains(i)) {
                matches++;
            }
        }

        if (template_count == 0) return 0.0f;

        // Score based on:
        // - How many template notes are present
        // - Penalty for extra notes
        float recall = static_cast<float>(matches) / template_count;
        float precision = input_count > 0 ? static_cast<float>(matches) / input_count : 0.0f;

        // F1-like score with slight preference for recall
        return (recall * 0.6f + precision * 0.4f);
    }

    const std::array<ChordQuality, 12> all_qualities_ = {
        ChordQuality::Major,
        ChordQuality::Minor,
        ChordQuality::Diminished,
        ChordQuality::Augmented,
        ChordQuality::Dominant7,
        ChordQuality::Major7,
        ChordQuality::Minor7,
        ChordQuality::Diminished7,
        ChordQuality::HalfDiminished7,
        ChordQuality::Sus2,
        ChordQuality::Sus4,
        ChordQuality::Power
    };
};

// =============================================================================
// Key Detector
// =============================================================================

/**
 * Detects musical key from pitch class distribution.
 * Uses Krumhansl-Schmuckler key-finding algorithm.
 */
class KeyDetector {
public:
    struct Detection {
        Scale scale;
        float confidence;
        bool is_minor;
    };

    KeyDetector() {
        init_profiles();
    }

    /// Detect key from pitch class histogram
    Detection detect(const std::array<float, NOTES_PER_OCTAVE>& histogram) const {
        Detection best{{NoteName::C, ScaleType::Major}, 0.0f, false};

        // Normalize histogram
        float sum = 0.0f;
        for (float v : histogram) sum += v;
        if (sum < 0.001f) return best;

        std::array<float, NOTES_PER_OCTAVE> normalized;
        for (int i = 0; i < NOTES_PER_OCTAVE; ++i) {
            normalized[i] = histogram[i] / sum;
        }

        // Try each key (major and minor)
        for (int root = 0; root < NOTES_PER_OCTAVE; ++root) {
            // Major key
            float major_score = correlate(normalized, major_profile_, root);
            if (major_score > best.confidence) {
                best.scale.root = static_cast<NoteName>(root);
                best.scale.type = ScaleType::Major;
                best.confidence = major_score;
                best.is_minor = false;
            }

            // Minor key
            float minor_score = correlate(normalized, minor_profile_, root);
            if (minor_score > best.confidence) {
                best.scale.root = static_cast<NoteName>(root);
                best.scale.type = ScaleType::NaturalMinor;
                best.confidence = minor_score;
                best.is_minor = true;
            }
        }

        return best;
    }

    /// Accumulate note for key detection
    void accumulate(MidiNote note, float weight = 1.0f) {
        accumulated_[note % NOTES_PER_OCTAVE] += weight;
    }

    /// Clear accumulated data
    void clear() {
        accumulated_.fill(0.0f);
    }

    /// Detect from accumulated data
    Detection detect_accumulated() const {
        return detect(accumulated_);
    }

private:
    void init_profiles() {
        // Krumhansl-Kessler major profile
        major_profile_ = {
            6.35f, 2.23f, 3.48f, 2.33f, 4.38f, 4.09f,
            2.52f, 5.19f, 2.39f, 3.66f, 2.29f, 2.88f
        };

        // Krumhansl-Kessler minor profile
        minor_profile_ = {
            6.33f, 2.68f, 3.52f, 5.38f, 2.60f, 3.53f,
            2.54f, 4.75f, 3.98f, 2.69f, 3.34f, 3.17f
        };
    }

    float correlate(const std::array<float, NOTES_PER_OCTAVE>& input,
                   const std::array<float, NOTES_PER_OCTAVE>& profile,
                   int rotation) const {
        // Pearson correlation coefficient
        float sum_xy = 0.0f, sum_x = 0.0f, sum_y = 0.0f;
        float sum_x2 = 0.0f, sum_y2 = 0.0f;
        const int n = NOTES_PER_OCTAVE;

        for (int i = 0; i < n; ++i) {
            float x = input[(i + rotation) % n];
            float y = profile[i];
            sum_xy += x * y;
            sum_x += x;
            sum_y += y;
            sum_x2 += x * x;
            sum_y2 += y * y;
        }

        float numerator = n * sum_xy - sum_x * sum_y;
        float denominator = std::sqrt((n * sum_x2 - sum_x * sum_x) *
                                       (n * sum_y2 - sum_y * sum_y));

        if (denominator < 0.0001f) return 0.0f;
        return numerator / denominator;
    }

    std::array<float, NOTES_PER_OCTAVE> major_profile_;
    std::array<float, NOTES_PER_OCTAVE> minor_profile_;
    std::array<float, NOTES_PER_OCTAVE> accumulated_{};
};

// =============================================================================
// Roman Numeral Analyzer
// =============================================================================

/**
 * Analyzes chords in context of a key using Roman numerals.
 */
class RomanNumeralAnalyzer {
public:
    struct Analysis {
        std::string numeral;     // e.g., "IV", "viio", "V7"
        Degree degree;
        bool is_diatonic;
        std::string function;    // "tonic", "subdominant", "dominant"
    };

    /// Analyze chord in context of key
    Analysis analyze(const Chord& chord, const Scale& key) const {
        Analysis result;

        int key_root = static_cast<int>(key.root);
        int chord_root = static_cast<int>(chord.root);
        int interval = ((chord_root - key_root) % NOTES_PER_OCTAVE + NOTES_PER_OCTAVE) % NOTES_PER_OCTAVE;

        result.degree = static_cast<Degree>(interval);

        // Get diatonic chord at this degree
        auto scale_intervals = key.intervals();
        bool on_scale_degree = false;
        int scale_degree = -1;

        for (int i = 0; i < static_cast<int>(scale_intervals.size()); ++i) {
            if (scale_intervals[i] == interval) {
                on_scale_degree = true;
                scale_degree = i;
                break;
            }
        }

        result.is_diatonic = on_scale_degree;

        // Build Roman numeral
        static const char* numerals[] = {
            "I", "bII", "II", "bIII", "III", "IV", "bV", "V", "bVI", "VI", "bVII", "VII"
        };

        std::string base = numerals[interval];

        // Lowercase for minor chords
        if (chord.quality == ChordQuality::Minor ||
            chord.quality == ChordQuality::Minor7 ||
            chord.quality == ChordQuality::Diminished ||
            chord.quality == ChordQuality::HalfDiminished7) {
            for (char& c : base) {
                c = std::tolower(c);
            }
        }

        // Add quality suffix
        switch (chord.quality) {
            case ChordQuality::Diminished:
                base += "°";
                break;
            case ChordQuality::Augmented:
                base += "+";
                break;
            case ChordQuality::Dominant7:
                base += "7";
                break;
            case ChordQuality::Major7:
                base += "Δ7";
                break;
            case ChordQuality::Minor7:
                base += "7";
                break;
            case ChordQuality::Diminished7:
                base += "°7";
                break;
            case ChordQuality::HalfDiminished7:
                base += "ø7";
                break;
            default:
                break;
        }

        result.numeral = base;

        // Determine function
        if (interval == 0) {
            result.function = "tonic";
        } else if (interval == 5 || interval == 2) {
            result.function = "subdominant";
        } else if (interval == 7 || interval == 11) {
            result.function = "dominant";
        } else {
            result.function = "other";
        }

        return result;
    }
};

// =============================================================================
// Voice Leading Analyzer
// =============================================================================

/**
 * Analyzes voice leading between chords.
 */
class VoiceLeadingAnalyzer {
public:
    struct VoiceMovement {
        int from_pitch;
        int to_pitch;
        int interval;  // Positive = up, negative = down
    };

    struct Analysis {
        std::vector<VoiceMovement> movements;
        int total_movement;      // Sum of absolute intervals
        int largest_leap;        // Largest single voice movement
        bool has_parallel_5ths;
        bool has_parallel_8ves;
        float smoothness_score;  // 0.0-1.0, higher = smoother
    };

    /// Analyze voice leading from chord1 to chord2
    Analysis analyze(const std::vector<int>& chord1_pitches,
                    const std::vector<int>& chord2_pitches) const {
        Analysis result;
        result.total_movement = 0;
        result.largest_leap = 0;
        result.has_parallel_5ths = false;
        result.has_parallel_8ves = false;

        if (chord1_pitches.empty() || chord2_pitches.empty()) {
            result.smoothness_score = 0.0f;
            return result;
        }

        // Simple nearest-voice matching
        std::vector<bool> used(chord2_pitches.size(), false);

        for (int from : chord1_pitches) {
            int best_idx = -1;
            int best_distance = 999;

            for (size_t i = 0; i < chord2_pitches.size(); ++i) {
                if (!used[i]) {
                    int dist = std::abs(chord2_pitches[i] - from);
                    if (dist < best_distance) {
                        best_distance = dist;
                        best_idx = static_cast<int>(i);
                    }
                }
            }

            if (best_idx >= 0) {
                used[best_idx] = true;
                int to = chord2_pitches[best_idx];
                int interval = to - from;

                result.movements.push_back({from, to, interval});
                result.total_movement += std::abs(interval);
                result.largest_leap = std::max(result.largest_leap, std::abs(interval));
            }
        }

        // Check for parallel 5ths and octaves
        for (size_t i = 0; i < result.movements.size(); ++i) {
            for (size_t j = i + 1; j < result.movements.size(); ++j) {
                int interval1_before = std::abs(result.movements[i].from_pitch -
                                                result.movements[j].from_pitch) % NOTES_PER_OCTAVE;
                int interval1_after = std::abs(result.movements[i].to_pitch -
                                               result.movements[j].to_pitch) % NOTES_PER_OCTAVE;

                // Both voices move in same direction
                bool same_direction = (result.movements[i].interval > 0) ==
                                      (result.movements[j].interval > 0);

                if (same_direction && interval1_before == 7 && interval1_after == 7) {
                    result.has_parallel_5ths = true;
                }
                if (same_direction && interval1_before == 0 && interval1_after == 0) {
                    result.has_parallel_8ves = true;
                }
            }
        }

        // Calculate smoothness (inverse of average movement)
        if (!result.movements.empty()) {
            float avg_movement = static_cast<float>(result.total_movement) / result.movements.size();
            result.smoothness_score = std::max(0.0f, 1.0f - (avg_movement / 12.0f));
        }

        return result;
    }
};

// =============================================================================
// Convenience Functions
// =============================================================================

/// Detect chord from MIDI notes
inline Chord detect_chord(const std::vector<MidiNote>& notes) {
    ChordDetector detector;
    return detector.detect_from_notes(notes).chord;
}

/// Detect key from note histogram
inline Scale detect_key(const std::array<float, NOTES_PER_OCTAVE>& histogram) {
    KeyDetector detector;
    return detector.detect(histogram).scale;
}

/// Get Roman numeral for chord in key
inline std::string roman_numeral(const Chord& chord, const Scale& key) {
    RomanNumeralAnalyzer analyzer;
    return analyzer.analyze(chord, key).numeral;
}

} // namespace harmony
} // namespace daiw
