/**
 * @file chord.cpp
 * @brief Chord representation and analysis
 */

#include "daiw/types.hpp"
#include <string>
#include <vector>
#include <map>
#include <array>

namespace daiw {
namespace harmony {

/**
 * @brief Chord quality definitions
 */
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
    MinorMajor7,
    Augmented7,
    Suspended2,
    Suspended4,
    Add9,
    Add11
};

/**
 * @brief Interval sets for chord qualities (semitones from root)
 */
const std::map<ChordQuality, std::vector<int>> CHORD_INTERVALS = {
    {ChordQuality::Major, {0, 4, 7}},
    {ChordQuality::Minor, {0, 3, 7}},
    {ChordQuality::Diminished, {0, 3, 6}},
    {ChordQuality::Augmented, {0, 4, 8}},
    {ChordQuality::Dominant7, {0, 4, 7, 10}},
    {ChordQuality::Major7, {0, 4, 7, 11}},
    {ChordQuality::Minor7, {0, 3, 7, 10}},
    {ChordQuality::Diminished7, {0, 3, 6, 9}},
    {ChordQuality::HalfDiminished7, {0, 3, 6, 10}},
    {ChordQuality::MinorMajor7, {0, 3, 7, 11}},
    {ChordQuality::Augmented7, {0, 4, 8, 10}},
    {ChordQuality::Suspended2, {0, 2, 7}},
    {ChordQuality::Suspended4, {0, 5, 7}},
    {ChordQuality::Add9, {0, 4, 7, 14}},
    {ChordQuality::Add11, {0, 4, 7, 17}},
};

/**
 * @brief Note name to MIDI number mapping (C4 = 60)
 */
const std::map<char, int> NOTE_TO_NUM = {
    {'C', 0}, {'D', 2}, {'E', 4}, {'F', 5},
    {'G', 7}, {'A', 9}, {'B', 11}
};

/**
 * @brief Chord class representation
 */
class Chord {
public:
    Chord(int root, ChordQuality quality)
        : root_(root), quality_(quality) {}

    /**
     * @brief Get MIDI pitches for this chord
     */
    std::vector<MidiNote> getPitches(int octave = 4) const {
        std::vector<MidiNote> pitches;
        int base = 12 * octave + root_;

        auto it = CHORD_INTERVALS.find(quality_);
        if (it != CHORD_INTERVALS.end()) {
            for (int interval : it->second) {
                pitches.push_back(static_cast<MidiNote>(base + interval));
            }
        }

        return pitches;
    }

    /**
     * @brief Get the root note
     */
    int getRoot() const { return root_; }

    /**
     * @brief Get the chord quality
     */
    ChordQuality getQuality() const { return quality_; }

    /**
     * @brief Parse chord from string (e.g., "Cm7", "F#dim")
     */
    static Chord parse(const std::string& symbol);

private:
    int root_;          // 0-11, where 0 = C
    ChordQuality quality_;
};

Chord Chord::parse(const std::string& symbol) {
    if (symbol.empty()) {
        return Chord(0, ChordQuality::Major);
    }

    // Parse root note
    int root = 0;
    size_t pos = 0;

    auto it = NOTE_TO_NUM.find(symbol[0]);
    if (it != NOTE_TO_NUM.end()) {
        root = it->second;
        pos = 1;
    }

    // Check for sharp/flat
    if (pos < symbol.size()) {
        if (symbol[pos] == '#') {
            root = (root + 1) % 12;
            pos++;
        } else if (symbol[pos] == 'b') {
            root = (root + 11) % 12;
            pos++;
        }
    }

    // Parse quality
    std::string qualityStr = symbol.substr(pos);
    ChordQuality quality = ChordQuality::Major;

    if (qualityStr.empty() || qualityStr == "maj") {
        quality = ChordQuality::Major;
    } else if (qualityStr == "m" || qualityStr == "min") {
        quality = ChordQuality::Minor;
    } else if (qualityStr == "dim") {
        quality = ChordQuality::Diminished;
    } else if (qualityStr == "aug" || qualityStr == "+") {
        quality = ChordQuality::Augmented;
    } else if (qualityStr == "7") {
        quality = ChordQuality::Dominant7;
    } else if (qualityStr == "maj7" || qualityStr == "M7") {
        quality = ChordQuality::Major7;
    } else if (qualityStr == "m7" || qualityStr == "min7") {
        quality = ChordQuality::Minor7;
    } else if (qualityStr == "dim7") {
        quality = ChordQuality::Diminished7;
    } else if (qualityStr == "m7b5" || qualityStr == "ø7") {
        quality = ChordQuality::HalfDiminished7;
    }

    return Chord(root, quality);
}

}  // namespace harmony
}  // namespace daiw
