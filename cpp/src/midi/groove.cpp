/**
 * @file groove.cpp
 * @brief Groove extraction and application
 */

#include "daiw/types.hpp"
#include <vector>
#include <cmath>
#include <random>

namespace daiw {
namespace groove {

/**
 * @brief Groove template from analysis
 */
struct GrooveTemplate {
    std::vector<float> timingOffsets;  // Per-beat timing offset in ms
    std::vector<float> velocityScales; // Per-beat velocity scaling
    float swingAmount = 0.0f;
};

/**
 * @brief Apply swing to a tick position
 */
TickCount applySwing(TickCount tick, float swing, int ppq) {
    if (swing <= 0.0f) return tick;

    int beatPosition = tick % (ppq * 2);  // Position within two beats
    int beat = tick / (ppq * 2);

    // Apply swing to off-beats (8th notes between beats)
    if (beatPosition >= ppq / 2 && beatPosition < ppq) {
        // This is an off-beat, shift it
        float swingOffset = swing * (ppq / 2.0f);
        return beat * ppq * 2 + beatPosition + static_cast<TickCount>(swingOffset);
    }

    return tick;
}

/**
 * @brief Apply humanization to a note event
 */
NoteEvent humanize(const NoteEvent& note, const GrooveSettings& settings,
                   std::mt19937& rng) {
    NoteEvent result = note;

    if (settings.humanization > 0.0f) {
        std::uniform_real_distribution<float> timingDist(-30.0f, 30.0f);
        float timingOffset = timingDist(rng) * settings.humanization;
        result.startTick += static_cast<TickCount>(timingOffset);
    }

    if (settings.velocityVar > 0.0f) {
        std::uniform_int_distribution<int> velDist(-10, 10);
        int velOffset = static_cast<int>(velDist(rng) * settings.velocityVar);
        int newVel = result.velocity + velOffset;
        result.velocity = static_cast<MidiVelocity>(
            std::clamp(newVel, 1, 127)
        );
    }

    if (settings.pushPull != 0.0f) {
        // Push (positive) = early, Pull (negative) = late
        float pushPullTicks = settings.pushPull * 20.0f;  // +/-20 ticks max
        result.startTick += static_cast<TickCount>(pushPullTicks);
    }

    return result;
}

/**
 * @brief Extract groove template from a set of note events
 */
GrooveTemplate extractGroove(const std::vector<NoteEvent>& notes, int ppq) {
    GrooveTemplate groove;

    if (notes.empty()) return groove;

    // Find the first beat position
    TickCount firstBeat = notes[0].startTick / ppq * ppq;

    // Analyze timing deviations from the grid
    std::vector<float> deviations;
    for (const auto& note : notes) {
        TickCount gridPosition = (note.startTick / ppq) * ppq;
        float deviation = static_cast<float>(note.startTick - gridPosition);
        deviations.push_back(deviation);
    }

    // Calculate average deviation (this would be more sophisticated in practice)
    if (!deviations.empty()) {
        groove.timingOffsets = deviations;
    }

    return groove;
}

}  // namespace groove
}  // namespace daiw
