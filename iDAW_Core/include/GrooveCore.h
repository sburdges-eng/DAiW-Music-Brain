/**
 * GrooveCore.h - C++ Core Module for Groove Extraction and Application
 * 
 * Part of Phase 3 C++ Migration for DAiW-Music-Brain
 * 
 * This module provides real-time safe groove analysis including:
 * - Timing deviation extraction from MIDI
 * - Velocity contour analysis
 * - Swing factor calculation
 * - Groove template application
 * - Ghost note detection
 * 
 * Design Philosophy:
 * - All operations are allocation-free after initialization
 * - Thread-safe for concurrent access
 * - Optimized for real-time audio processing
 * 
 * Corresponding Python module: music_brain/groove/extractor.py
 */

#pragma once

#include <array>
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <string>
#include <string_view>

namespace iDAW {
namespace Groove {

// =============================================================================
// Constants
// =============================================================================

// Maximum events in a groove template
constexpr size_t MAX_GROOVE_EVENTS = 512;

// Maximum timing deviations to store per beat
constexpr size_t MAX_TIMING_DEVIATIONS = 256;

// Standard MIDI PPQ values
constexpr uint16_t DEFAULT_PPQ = 480;

// Velocity thresholds
constexpr uint8_t GHOST_NOTE_THRESHOLD = 40;
constexpr uint8_t ACCENT_THRESHOLD = 100;

// Timing thresholds (in ticks at 480 PPQ)
constexpr int16_t TIMING_WINDOW_TICKS = 48;  // ~10% of quarter note

// =============================================================================
// Note Event Structure
// =============================================================================

/**
 * Single note event with timing and velocity information
 */
struct NoteEvent {
    uint8_t pitch = 0;           // MIDI pitch (0-127)
    uint8_t velocity = 0;        // MIDI velocity (0-127)
    uint8_t channel = 0;         // MIDI channel (0-15)
    uint32_t startTick = 0;      // Start time in ticks
    uint32_t durationTicks = 0;  // Duration in ticks
    
    // Analysis fields
    int16_t deviationTicks = 0;  // Deviation from quantized grid
    bool isGhost = false;        // Ghost note (low velocity)
    bool isAccent = false;       // Accent (high velocity)
    
    /**
     * Check if this is a valid event
     */
    bool isValid() const { return velocity > 0; }
};

// =============================================================================
// Velocity Statistics
// =============================================================================

struct VelocityStats {
    uint8_t min = 127;
    uint8_t max = 0;
    float mean = 0.0f;
    float stdDev = 0.0f;
    uint16_t ghostCount = 0;
    uint16_t accentCount = 0;
};

// =============================================================================
// Timing Statistics
// =============================================================================

struct TimingStats {
    float meanDeviationTicks = 0.0f;
    float meanDeviationMs = 0.0f;
    float maxDeviationTicks = 0.0f;
    float maxDeviationMs = 0.0f;
    float stdDeviationTicks = 0.0f;
    float stdDeviationMs = 0.0f;
};

// =============================================================================
// Groove Template
// =============================================================================

/**
 * Extracted groove pattern that can be applied to other MIDI data
 * 
 * Contains timing deviations, velocity curves, and statistical measures
 * that define the "feel" of the original performance.
 */
struct GrooveTemplate {
    // Identification
    std::array<char, 64> name = {};
    std::array<char, 256> sourceFile = {};
    
    // MIDI metadata
    uint16_t ppq = DEFAULT_PPQ;
    float tempoBpm = 120.0f;
    uint8_t timeSignatureNum = 4;
    uint8_t timeSignatureDenom = 4;
    
    // Timing analysis (per-grid-position deviations in ticks)
    std::array<int16_t, MAX_TIMING_DEVIATIONS> timingDeviations = {};
    size_t timingDeviationCount = 0;
    
    // Swing factor (0.0 = straight, 0.5 = triplet, 0.67 = heavy swing)
    float swingFactor = 0.0f;
    
    // Velocity curve (average velocity per beat)
    std::array<uint8_t, MAX_TIMING_DEVIATIONS> velocityCurve = {};
    size_t velocityCurveLength = 0;
    
    // Statistics
    VelocityStats velocityStats;
    TimingStats timingStats;
    
    // Events (optional, for detailed analysis)
    std::array<NoteEvent, MAX_GROOVE_EVENTS> events = {};
    size_t eventCount = 0;
    
    /**
     * Set template name
     */
    void setName(std::string_view n) {
        size_t len = std::min(n.size(), name.size() - 1);
        std::copy_n(n.begin(), len, name.begin());
        name[len] = '\0';
    }
    
    /**
     * Get template name
     */
    std::string_view getName() const {
        return std::string_view(name.data());
    }
    
    /**
     * Add an event to the template
     */
    bool addEvent(const NoteEvent& event) {
        if (eventCount >= MAX_GROOVE_EVENTS) return false;
        events[eventCount++] = event;
        return true;
    }
    
    /**
     * Add a timing deviation
     */
    bool addTimingDeviation(int16_t deviation) {
        if (timingDeviationCount >= MAX_TIMING_DEVIATIONS) return false;
        timingDeviations[timingDeviationCount++] = deviation;
        return true;
    }
};

// =============================================================================
// Genre Groove Templates
// =============================================================================

enum class GenreGroove : uint8_t {
    Straight = 0,
    Funk,
    Jazz,
    BoomBap,
    Dilla,
    Trap,
    Rock,
    HipHop,
    LoFi,
    Count
};

/**
 * Get string name for genre groove
 */
inline std::string_view genreGrooveToString(GenreGroove genre) {
    switch (genre) {
        case GenreGroove::Straight: return "Straight";
        case GenreGroove::Funk:     return "Funk";
        case GenreGroove::Jazz:     return "Jazz";
        case GenreGroove::BoomBap:  return "Boom Bap";
        case GenreGroove::Dilla:    return "Dilla/Neo-Soul";
        case GenreGroove::Trap:     return "Trap";
        case GenreGroove::Rock:     return "Rock";
        case GenreGroove::HipHop:   return "Hip Hop";
        case GenreGroove::LoFi:     return "Lo-Fi";
        default:                    return "Unknown";
    }
}

/**
 * Get genre-specific groove parameters
 */
struct GenreGrooveParams {
    float swingFactor = 0.0f;       // 0.0 = straight, 0.5 = triplet swing
    int16_t kickOffset = 0;         // Kick timing offset in ticks
    int16_t snareOffset = 0;        // Snare timing offset in ticks
    int16_t hihatOffset = 0;        // Hi-hat timing offset in ticks
    float velocityVariation = 0.0f; // Velocity humanization amount (0-1)
    float timingVariation = 0.0f;   // Timing humanization amount (0-1)
};

inline GenreGrooveParams getGenreGrooveParams(GenreGroove genre) {
    GenreGrooveParams params;
    
    switch (genre) {
        case GenreGroove::Straight:
            params.swingFactor = 0.0f;
            params.velocityVariation = 0.05f;
            params.timingVariation = 0.02f;
            break;
            
        case GenreGroove::Funk:
            params.swingFactor = 0.08f;   // Slight swing (~58% ratio)
            params.kickOffset = 0;
            params.snareOffset = -8;      // Snare slightly laid back
            params.hihatOffset = 5;       // Hi-hats slightly ahead
            params.velocityVariation = 0.15f;
            params.timingVariation = 0.08f;
            break;
            
        case GenreGroove::Jazz:
            params.swingFactor = 0.17f;   // Triplet swing (~66%)
            params.kickOffset = -10;
            params.snareOffset = -15;
            params.hihatOffset = -5;
            params.velocityVariation = 0.2f;
            params.timingVariation = 0.12f;
            break;
            
        case GenreGroove::BoomBap:
            params.swingFactor = 0.04f;   // Subtle swing (~54%)
            params.kickOffset = 5;
            params.snareOffset = -10;     // Snare laid back
            params.hihatOffset = 0;
            params.velocityVariation = 0.1f;
            params.timingVariation = 0.06f;
            break;
            
        case GenreGroove::Dilla:
            params.swingFactor = 0.12f;   // Moderate swing (~62%)
            params.kickOffset = 15;       // Drunken kick feel
            params.snareOffset = -20;     // Very laid back snare
            params.hihatOffset = 8;
            params.velocityVariation = 0.25f;
            params.timingVariation = 0.15f;
            break;
            
        case GenreGroove::Trap:
            params.swingFactor = 0.01f;   // Nearly straight (~51%)
            params.kickOffset = 0;
            params.snareOffset = 0;
            params.hihatOffset = 0;
            params.velocityVariation = 0.1f;
            params.timingVariation = 0.03f;
            break;
            
        case GenreGroove::Rock:
            params.swingFactor = 0.0f;    // Straight
            params.kickOffset = 3;        // Slightly ahead
            params.snareOffset = -5;      // Slightly back
            params.hihatOffset = 0;
            params.velocityVariation = 0.12f;
            params.timingVariation = 0.05f;
            break;
            
        case GenreGroove::HipHop:
            params.swingFactor = 0.06f;   // Light swing
            params.kickOffset = 8;
            params.snareOffset = -12;
            params.hihatOffset = 3;
            params.velocityVariation = 0.15f;
            params.timingVariation = 0.08f;
            break;
            
        case GenreGroove::LoFi:
            params.swingFactor = 0.1f;    // Moderate swing
            params.kickOffset = 10;
            params.snareOffset = -18;
            params.hihatOffset = -5;
            params.velocityVariation = 0.2f;
            params.timingVariation = 0.12f;
            break;
            
        default:
            break;
    }
    
    return params;
}

// =============================================================================
// Groove Analysis Functions
// =============================================================================

/**
 * Calculate swing factor from note events
 * 
 * Swing is the ratio of the first 8th note to the second in a pair.
 * - 0.0 = straight (even 8ths, 50% ratio)
 * - 0.17 = triplet swing (2:1 ratio, 66%)
 * - 0.5 = maximum swing
 * 
 * @param events Array of note events
 * @param eventCount Number of events
 * @param ppq Pulses per quarter note
 * @return Swing factor (0.0 - 0.5)
 */
inline float calculateSwing(const NoteEvent* events, size_t eventCount, uint16_t ppq) {
    if (eventCount < 4) return 0.0f;
    
    // Look at 8th note pairs
    int eighthNoteTicks = ppq / 2;
    
    int onBeatCount = 0;
    int offBeatCount = 0;
    int64_t offBeatOffsetSum = 0;
    
    for (size_t i = 0; i < eventCount; ++i) {
        int positionInBeat = events[i].startTick % ppq;
        
        // On beat (within 10% of beat start)
        if (positionInBeat < ppq / 10 || positionInBeat > ppq * 9 / 10) {
            onBeatCount++;
        }
        // Off beat (near middle of beat)
        else if (std::abs(positionInBeat - eighthNoteTicks) < ppq * 15 / 100) {
            offBeatCount++;
            offBeatOffsetSum += (positionInBeat - eighthNoteTicks);
        }
    }
    
    if (offBeatCount == 0) return 0.0f;
    
    // Calculate average offset of off-beat notes
    float avgOffset = static_cast<float>(offBeatOffsetSum) / offBeatCount;
    float normalizedOffset = avgOffset / eighthNoteTicks;
    
    // Normalize to 0.0-0.5 range
    // Positive offset = swing (off-beats pushed late)
    float swingFactor = std::max(0.0f, std::min(0.5f, normalizedOffset * 0.5f + 0.25f)) - 0.25f;
    
    return std::max(0.0f, swingFactor);
}

/**
 * Calculate timing deviation from quantized grid
 * 
 * @param startTick Note start time in ticks
 * @param ppq Pulses per quarter note
 * @param gridResolution Grid resolution (8 = 8th notes, 16 = 16th notes)
 * @return Deviation in ticks
 */
inline int16_t calculateTimingDeviation(uint32_t startTick, uint16_t ppq, int gridResolution) {
    int ticksPerGrid = ppq * 4 / gridResolution;
    int nearestGrid = static_cast<int>(std::round(static_cast<float>(startTick) / ticksPerGrid)) * ticksPerGrid;
    return static_cast<int16_t>(startTick - nearestGrid);
}

/**
 * Extract groove template from note events
 * 
 * @param events Array of note events
 * @param eventCount Number of events
 * @param ppq Pulses per quarter note
 * @param tempoBpm Tempo in BPM
 * @param gridResolution Quantization grid (8, 16, 32)
 * @return Extracted groove template
 */
inline GrooveTemplate extractGroove(
    const NoteEvent* events,
    size_t eventCount,
    uint16_t ppq = DEFAULT_PPQ,
    float tempoBpm = 120.0f,
    int gridResolution = 16
) {
    GrooveTemplate tmpl;
    tmpl.ppq = ppq;
    tmpl.tempoBpm = tempoBpm;
    
    if (eventCount == 0) return tmpl;
    
    // Copy events with analysis
    for (size_t i = 0; i < eventCount && i < MAX_GROOVE_EVENTS; ++i) {
        NoteEvent event = events[i];
        
        // Calculate timing deviation
        event.deviationTicks = calculateTimingDeviation(event.startTick, ppq, gridResolution);
        
        // Classify ghost notes and accents
        event.isGhost = event.velocity < GHOST_NOTE_THRESHOLD;
        event.isAccent = event.velocity > ACCENT_THRESHOLD;
        
        tmpl.events[tmpl.eventCount++] = event;
        tmpl.addTimingDeviation(event.deviationTicks);
    }
    
    // Calculate swing
    tmpl.swingFactor = calculateSwing(events, eventCount, ppq);
    
    // Calculate velocity statistics
    uint32_t velocitySum = 0;
    for (size_t i = 0; i < tmpl.eventCount; ++i) {
        uint8_t vel = tmpl.events[i].velocity;
        velocitySum += vel;
        tmpl.velocityStats.min = std::min(tmpl.velocityStats.min, vel);
        tmpl.velocityStats.max = std::max(tmpl.velocityStats.max, vel);
        if (tmpl.events[i].isGhost) tmpl.velocityStats.ghostCount++;
        if (tmpl.events[i].isAccent) tmpl.velocityStats.accentCount++;
    }
    tmpl.velocityStats.mean = static_cast<float>(velocitySum) / tmpl.eventCount;
    
    // Calculate velocity standard deviation
    float varSum = 0.0f;
    for (size_t i = 0; i < tmpl.eventCount; ++i) {
        float diff = tmpl.events[i].velocity - tmpl.velocityStats.mean;
        varSum += diff * diff;
    }
    tmpl.velocityStats.stdDev = std::sqrt(varSum / tmpl.eventCount);
    
    // Calculate timing statistics
    int32_t timingSum = 0;
    int16_t maxDev = 0;
    for (size_t i = 0; i < tmpl.timingDeviationCount; ++i) {
        timingSum += tmpl.timingDeviations[i];
        maxDev = std::max(maxDev, static_cast<int16_t>(std::abs(tmpl.timingDeviations[i])));
    }
    tmpl.timingStats.meanDeviationTicks = static_cast<float>(timingSum) / tmpl.timingDeviationCount;
    tmpl.timingStats.maxDeviationTicks = static_cast<float>(maxDev);
    
    // Convert to milliseconds
    float msPerTick = 60000.0f / (tempoBpm * ppq);
    tmpl.timingStats.meanDeviationMs = tmpl.timingStats.meanDeviationTicks * msPerTick;
    tmpl.timingStats.maxDeviationMs = tmpl.timingStats.maxDeviationTicks * msPerTick;
    
    // Calculate timing standard deviation
    float timingVarSum = 0.0f;
    for (size_t i = 0; i < tmpl.timingDeviationCount; ++i) {
        float diff = tmpl.timingDeviations[i] - tmpl.timingStats.meanDeviationTicks;
        timingVarSum += diff * diff;
    }
    tmpl.timingStats.stdDeviationTicks = std::sqrt(timingVarSum / tmpl.timingDeviationCount);
    tmpl.timingStats.stdDeviationMs = tmpl.timingStats.stdDeviationTicks * msPerTick;
    
    // Build velocity curve (per beat)
    if (tmpl.eventCount > 0) {
        uint32_t maxTick = 0;
        for (size_t i = 0; i < tmpl.eventCount; ++i) {
            maxTick = std::max(maxTick, tmpl.events[i].startTick);
        }
        
        size_t totalBeats = (maxTick / ppq) + 1;
        totalBeats = std::min(totalBeats, MAX_TIMING_DEVIATIONS);
        
        for (size_t beat = 0; beat < totalBeats; ++beat) {
            uint32_t beatStart = beat * ppq;
            uint32_t beatEnd = (beat + 1) * ppq;
            
            uint32_t beatVelSum = 0;
            uint32_t beatEventCount = 0;
            
            for (size_t i = 0; i < tmpl.eventCount; ++i) {
                if (tmpl.events[i].startTick >= beatStart && 
                    tmpl.events[i].startTick < beatEnd) {
                    beatVelSum += tmpl.events[i].velocity;
                    beatEventCount++;
                }
            }
            
            if (beatEventCount > 0) {
                tmpl.velocityCurve[beat] = static_cast<uint8_t>(beatVelSum / beatEventCount);
            }
            tmpl.velocityCurveLength++;
        }
    }
    
    return tmpl;
}

// =============================================================================
// Groove Application Functions
// =============================================================================

/**
 * Apply groove template to a note event
 * 
 * @param event Note event to modify
 * @param tmpl Groove template to apply
 * @param intensity How strongly to apply the groove (0.0 - 1.0)
 * @param eventIndex Index of the event for pattern matching
 */
inline void applyGrooveToEvent(
    NoteEvent& event,
    const GrooveTemplate& tmpl,
    float intensity = 1.0f,
    size_t eventIndex = 0
) {
    if (tmpl.timingDeviationCount == 0) return;
    
    // Get timing deviation from template (cycling through pattern)
    size_t patternIndex = eventIndex % tmpl.timingDeviationCount;
    int16_t deviation = tmpl.timingDeviations[patternIndex];
    
    // Apply deviation with intensity
    int32_t newTick = static_cast<int32_t>(event.startTick) + 
                      static_cast<int32_t>(deviation * intensity);
    event.startTick = static_cast<uint32_t>(std::max(0, newTick));
    
    // Apply velocity curve if available
    if (tmpl.velocityCurveLength > 0) {
        size_t beatIndex = (event.startTick / tmpl.ppq) % tmpl.velocityCurveLength;
        uint8_t templateVel = tmpl.velocityCurve[beatIndex];
        
        // Blend original velocity with template velocity
        float blendedVel = event.velocity * (1.0f - intensity * 0.5f) + 
                           templateVel * (intensity * 0.5f);
        event.velocity = static_cast<uint8_t>(std::clamp(blendedVel, 1.0f, 127.0f));
    }
}

/**
 * Apply genre groove to note events
 * 
 * @param events Array of note events to modify
 * @param eventCount Number of events
 * @param genre Genre groove to apply
 * @param intensity How strongly to apply (0.0 - 1.0)
 * @param ppq Pulses per quarter note
 */
inline void applyGenreGroove(
    NoteEvent* events,
    size_t eventCount,
    GenreGroove genre,
    float intensity = 1.0f,
    uint16_t ppq = DEFAULT_PPQ
) {
    GenreGrooveParams params = getGenreGrooveParams(genre);
    
    // Common drum pitches (General MIDI)
    constexpr uint8_t KICK_PITCH = 36;
    constexpr uint8_t SNARE_PITCH = 38;
    constexpr uint8_t HIHAT_CLOSED = 42;
    constexpr uint8_t HIHAT_OPEN = 46;
    
    for (size_t i = 0; i < eventCount; ++i) {
        NoteEvent& event = events[i];
        
        // Apply instrument-specific offsets
        int16_t offset = 0;
        if (event.pitch == KICK_PITCH) {
            offset = params.kickOffset;
        } else if (event.pitch == SNARE_PITCH) {
            offset = params.snareOffset;
        } else if (event.pitch == HIHAT_CLOSED || event.pitch == HIHAT_OPEN) {
            offset = params.hihatOffset;
        }
        
        // Apply offset with intensity
        int32_t newTick = static_cast<int32_t>(event.startTick) + 
                          static_cast<int32_t>(offset * intensity);
        event.startTick = static_cast<uint32_t>(std::max(0, newTick));
        
        // Apply swing to off-beat 8th notes
        int positionInBeat = event.startTick % ppq;
        int eighthNoteTicks = ppq / 2;
        
        if (std::abs(positionInBeat - eighthNoteTicks) < ppq / 10) {
            // This is an off-beat 8th note, apply swing
            int32_t swingOffset = static_cast<int32_t>(params.swingFactor * eighthNoteTicks * intensity);
            event.startTick += swingOffset;
        }
        
        // Apply velocity variation (simple humanization)
        if (params.velocityVariation > 0.0f) {
            // Use simple hash-based variation (deterministic for reproducibility)
            int hash = (event.startTick * 31 + event.pitch * 17) % 100;
            float variation = (hash - 50) / 50.0f * params.velocityVariation;
            int newVel = static_cast<int>(event.velocity * (1.0f + variation * intensity));
            event.velocity = static_cast<uint8_t>(std::clamp(newVel, 1, 127));
        }
    }
}

/**
 * Humanize note events with random variations
 * 
 * @param events Array of note events to modify
 * @param eventCount Number of events
 * @param timingVariation Max timing variation in ticks
 * @param velocityVariation Max velocity variation (0-127)
 * @param seed Random seed for reproducibility (0 = use default)
 */
inline void humanize(
    NoteEvent* events,
    size_t eventCount,
    int16_t timingVariation = 15,
    uint8_t velocityVariation = 10,
    uint32_t seed = 0
) {
    // Simple deterministic pseudo-random based on position
    for (size_t i = 0; i < eventCount; ++i) {
        NoteEvent& event = events[i];
        
        // Hash-based pseudo-random
        uint32_t hash = event.startTick ^ (event.pitch << 8) ^ (seed * 2654435769u);
        hash ^= hash >> 16;
        hash *= 0x85ebca6b;
        hash ^= hash >> 13;
        
        // Apply timing variation
        int16_t timingOffset = static_cast<int16_t>((hash % (2 * timingVariation + 1)) - timingVariation);
        int32_t newTick = static_cast<int32_t>(event.startTick) + timingOffset;
        event.startTick = static_cast<uint32_t>(std::max(0, newTick));
        
        // Apply velocity variation
        hash ^= hash >> 11;
        int velOffset = static_cast<int>((hash % (2 * velocityVariation + 1)) - velocityVariation);
        int newVel = static_cast<int>(event.velocity) + velOffset;
        event.velocity = static_cast<uint8_t>(std::clamp(newVel, 1, 127));
    }
}

} // namespace Groove
} // namespace iDAW
