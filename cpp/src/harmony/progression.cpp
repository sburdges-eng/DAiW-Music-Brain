/**
 * @file progression.cpp
 * @brief Chord progression analysis and generation
 */

#include "daiw/types.hpp"
#include <string>
#include <vector>
#include <sstream>

namespace daiw {
namespace harmony {

// Forward declaration
class Chord;

/**
 * @brief Chord progression container
 */
class Progression {
public:
    void addChord(const std::string& symbol) {
        chordSymbols_.push_back(symbol);
    }

    const std::vector<std::string>& getChords() const {
        return chordSymbols_;
    }

    size_t length() const { return chordSymbols_.size(); }

    void clear() { chordSymbols_.clear(); }

    /**
     * @brief Parse progression from dash-separated string
     */
    static Progression parse(const std::string& str) {
        Progression prog;
        std::stringstream ss(str);
        std::string chord;

        while (std::getline(ss, chord, '-')) {
            // Trim whitespace
            size_t start = chord.find_first_not_of(" \t");
            size_t end = chord.find_last_not_of(" \t");
            if (start != std::string::npos) {
                prog.addChord(chord.substr(start, end - start + 1));
            }
        }

        return prog;
    }

    /**
     * @brief Get string representation
     */
    std::string toString() const {
        std::string result;
        for (size_t i = 0; i < chordSymbols_.size(); ++i) {
            if (i > 0) result += "-";
            result += chordSymbols_[i];
        }
        return result;
    }

private:
    std::vector<std::string> chordSymbols_;
};

/**
 * @brief Analyze emotional character of a progression
 */
struct ProgressionAnalysis {
    std::string key;
    std::string mode;
    float tension = 0.0f;    // 0-1, overall tension level
    float darkness = 0.0f;   // 0-1, minor vs major character
    bool hasModalInterchange = false;
    bool hasChromatic = false;
    std::vector<std::string> emotionalTags;
};

/**
 * @brief Analyze a chord progression
 */
ProgressionAnalysis analyzeProgression(const Progression& prog) {
    ProgressionAnalysis analysis;

    const auto& chords = prog.getChords();
    if (chords.empty()) return analysis;

    // Simple analysis: count minors vs majors
    int minorCount = 0;
    int majorCount = 0;

    for (const auto& chord : chords) {
        bool hasMinor = chord.find('m') != std::string::npos &&
                        chord.find("maj") == std::string::npos;
        if (hasMinor) {
            minorCount++;
        } else {
            majorCount++;
        }
    }

    analysis.darkness = static_cast<float>(minorCount) /
                        static_cast<float>(chords.size());

    // Emotional tagging based on analysis
    if (analysis.darkness > 0.6f) {
        analysis.emotionalTags.push_back("melancholic");
    } else if (analysis.darkness < 0.3f) {
        analysis.emotionalTags.push_back("bright");
    } else {
        analysis.emotionalTags.push_back("bittersweet");
    }

    return analysis;
}

}  // namespace harmony
}  // namespace daiw
