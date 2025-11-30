/**
 * @file humanizer.cpp
 * @brief Drum and MIDI humanization engine
 */

#include "daiw/types.hpp"
#include <vector>
#include <random>
#include <cmath>

namespace daiw {
namespace humanizer {

/**
 * @brief Humanization preset
 */
struct HumanizePreset {
    std::string name;
    float timingVar = 0.3f;      // Timing variation (0-1)
    float velocityVar = 0.2f;    // Velocity variation (0-1)
    float ghostNoteChance = 0.1f; // Chance of ghost notes
    float rushDrag = 0.0f;       // -1 = drag, +1 = rush
    bool protectDownbeats = true;
};

/**
 * @brief Preset definitions
 */
const HumanizePreset PRESET_LOFI = {
    "lo-fi-depression",
    0.4f,  // More timing variation
    0.3f,  // Moderate velocity
    0.15f, // Some ghost notes
    -0.2f, // Slight drag
    true
};

const HumanizePreset PRESET_MECHANICAL = {
    "mechanical-dissociation",
    0.05f, // Very tight
    0.1f,
    0.0f,  // No ghost notes
    0.0f,
    true
};

const HumanizePreset PRESET_PUNK = {
    "defiant-punk",
    0.35f,
    0.5f,  // Wide velocity swings
    0.05f,
    0.15f, // Slight rush
    false  // Even downbeats get hit hard
};

/**
 * @brief Humanize a sequence of notes
 */
std::vector<NoteEvent> humanize(
    const std::vector<NoteEvent>& notes,
    const HumanizePreset& preset,
    int ppq = DEFAULT_PPQ
) {
    std::random_device rd;
    std::mt19937 rng(rd());

    std::vector<NoteEvent> result;
    result.reserve(notes.size());

    std::uniform_real_distribution<float> timingDist(-1.0f, 1.0f);
    std::uniform_real_distribution<float> velDist(-1.0f, 1.0f);
    std::uniform_real_distribution<float> ghostDist(0.0f, 1.0f);

    for (const auto& note : notes) {
        NoteEvent humanized = note;

        // Check if this is a downbeat
        bool isDownbeat = (note.startTick % ppq) < 10;

        // Apply timing variation
        if (!preset.protectDownbeats || !isDownbeat) {
            float timingOffset = timingDist(rng) * preset.timingVar * 30.0f;
            timingOffset += preset.rushDrag * 15.0f;  // Rush/drag bias
            humanized.startTick += static_cast<TickCount>(timingOffset);
        }

        // Apply velocity variation
        float velOffset = velDist(rng) * preset.velocityVar * 30.0f;
        int newVel = note.velocity + static_cast<int>(velOffset);
        humanized.velocity = static_cast<MidiVelocity>(
            std::clamp(newVel, 1, 127)
        );

        result.push_back(humanized);

        // Maybe add ghost note
        if (ghostDist(rng) < preset.ghostNoteChance) {
            NoteEvent ghost = note;
            ghost.startTick += ppq / 4;  // Quarter beat later
            ghost.velocity = static_cast<MidiVelocity>(note.velocity * 0.3f);
            result.push_back(ghost);
        }
    }

    return result;
}

}  // namespace humanizer
}  // namespace daiw
