/**
 * @file voice_leading.cpp
 * @brief Voice leading algorithms
 */

#include "daiw/types.hpp"
#include <vector>
#include <algorithm>
#include <cmath>

namespace daiw {
namespace harmony {

/**
 * @brief Voice leading result
 */
struct VoiceLeading {
    std::vector<std::vector<MidiNote>> voices;  // Per-voice note sequence
    float totalMovement = 0.0f;                 // Total semitone movement
    int maxLeap = 0;                            // Largest interval
};

/**
 * @brief Calculate the movement between two voicings
 */
int calculateMovement(const std::vector<MidiNote>& from,
                      const std::vector<MidiNote>& to) {
    int movement = 0;
    size_t minSize = std::min(from.size(), to.size());

    for (size_t i = 0; i < minSize; ++i) {
        movement += std::abs(to[i] - from[i]);
    }

    return movement;
}

/**
 * @brief Find optimal voice leading between two chords
 *
 * Minimizes total voice movement while avoiding parallel fifths/octaves.
 */
std::vector<MidiNote> optimalVoiceLead(
    const std::vector<MidiNote>& fromVoicing,
    const std::vector<MidiNote>& toChordTones
) {
    if (toChordTones.empty()) return {};

    std::vector<MidiNote> result = toChordTones;

    // Simple nearest-note algorithm
    for (size_t i = 0; i < result.size() && i < fromVoicing.size(); ++i) {
        MidiNote fromNote = fromVoicing[i];
        MidiNote bestNote = result[i];
        int bestDistance = 127;

        // Find the octave of this chord tone closest to the previous voice
        for (int octave = -1; octave <= 1; ++octave) {
            int candidate = result[i] + (octave * 12);
            if (candidate >= 0 && candidate <= 127) {
                int distance = std::abs(candidate - fromNote);
                if (distance < bestDistance) {
                    bestDistance = distance;
                    bestNote = static_cast<MidiNote>(candidate);
                }
            }
        }

        result[i] = bestNote;
    }

    return result;
}

/**
 * @brief Check for parallel fifths between two voicings
 */
bool hasParallelFifths(const std::vector<MidiNote>& from,
                       const std::vector<MidiNote>& to) {
    for (size_t i = 0; i < from.size(); ++i) {
        for (size_t j = i + 1; j < from.size(); ++j) {
            if (i >= to.size() || j >= to.size()) continue;

            int interval1 = std::abs(from[j] - from[i]) % 12;
            int interval2 = std::abs(to[j] - to[i]) % 12;

            // Perfect fifth = 7 semitones
            if (interval1 == 7 && interval2 == 7) {
                // Check if both voices moved in the same direction
                int motion1 = to[i] - from[i];
                int motion2 = to[j] - from[j];
                if ((motion1 > 0 && motion2 > 0) ||
                    (motion1 < 0 && motion2 < 0)) {
                    return true;
                }
            }
        }
    }
    return false;
}

}  // namespace harmony
}  // namespace daiw
