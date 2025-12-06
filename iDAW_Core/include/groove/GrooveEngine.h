/**
 * GrooveEngine.h - C++ Groove Extraction and Application Engine
 * 
 * High-performance groove analysis including:
 * - Timing deviation extraction
 * - Swing factor calculation
 * - Velocity pattern analysis
 * - Ghost note detection
 * - Groove application to quantized MIDI
 */

#pragma once

#include "GrooveTemplate.h"
#include <string>
#include <vector>
#include <memory>
#include <functional>

namespace iDAW {
namespace groove {

/**
 * Groove extraction settings
 */
struct ExtractionSettings {
    int quantizeResolution = 16;    // Grid resolution (8=8th, 16=16th, 32=32nd)
    int ghostThreshold = 40;        // Velocity below this = ghost note
    int accentThreshold = 100;      // Velocity above this = accent
    bool detectSwing = true;        // Calculate swing factor
    bool normalizeVelocity = false; // Normalize velocity range
};

/**
 * Groove application settings
 */
struct ApplicationSettings {
    float intensity = 1.0f;         // 0.0-1.0, how much groove to apply
    bool applyTiming = true;        // Apply timing deviations
    bool applyVelocity = true;      // Apply velocity curve
    bool applySwing = true;         // Apply swing factor
    bool preserveGhosts = true;     // Keep ghost notes as ghosts
};

/**
 * MIDI event for processing (simplified)
 */
struct MidiNote {
    int pitch;
    int velocity;
    int startTick;
    int durationTicks;
    int channel = 0;
};

/**
 * GrooveEngine - Main groove processing interface
 * 
 * Thread-safe for use from both audio and UI threads.
 * Real-time safe for groove application (no allocations in apply).
 */
class GrooveEngine {
public:
    /**
     * Get singleton instance
     */
    static GrooveEngine& getInstance();
    
    // Non-copyable
    GrooveEngine(const GrooveEngine&) = delete;
    GrooveEngine& operator=(const GrooveEngine&) = delete;
    
    /**
     * Extract groove from MIDI note events
     * 
     * @param notes Vector of MIDI notes
     * @param ppq Pulses per quarter note
     * @param tempoBpm Tempo in BPM
     * @param settings Extraction settings
     * @return Extracted groove template
     */
    GrooveTemplate extractGroove(
        const std::vector<MidiNote>& notes,
        int ppq,
        float tempoBpm,
        const ExtractionSettings& settings = ExtractionSettings{}) const;
    
    /**
     * Apply groove to MIDI notes
     * 
     * @param notes Input notes (will be modified)
     * @param groove Groove template to apply
     * @param ppq Pulses per quarter note
     * @param settings Application settings
     */
    void applyGroove(
        std::vector<MidiNote>& notes,
        const GrooveTemplate& groove,
        int ppq,
        const ApplicationSettings& settings = ApplicationSettings{}) const;
    
    /**
     * Humanize MIDI notes (add subtle timing/velocity variations)
     * 
     * @param notes Input notes (will be modified)
     * @param complexity Complexity level (0.0-1.0)
     * @param vulnerability Vulnerability level (0.0-1.0)
     * @param ppq Pulses per quarter note
     * @param seed Random seed for reproducibility (-1 for random)
     */
    void humanize(
        std::vector<MidiNote>& notes,
        float complexity,
        float vulnerability,
        int ppq,
        int seed = -1) const;
    
    /**
     * Calculate swing factor from notes
     */
    float calculateSwing(const std::vector<MidiNote>& notes, int ppq) const;
    
    /**
     * Get a built-in genre groove template
     */
    GrooveTemplate getGenreTemplate(const std::string& genre) const;
    GrooveTemplate getGenreTemplate(GenrePreset preset) const;
    
    /**
     * List available genre presets
     */
    std::vector<std::string> listGenrePresets() const;
    
    /**
     * Quantize notes to grid (removes human feel)
     */
    void quantize(
        std::vector<MidiNote>& notes,
        int ppq,
        int resolution = 16) const;
    
private:
    GrooveEngine() = default;
    ~GrooveEngine() = default;
    
    // Internal helpers
    float calculateDeviationForNote(
        const MidiNote& note,
        int ppq,
        int resolution) const;
    
    void applyTimingDeviation(
        MidiNote& note,
        float deviation,
        float intensity) const;
    
    void applyVelocityCurve(
        MidiNote& note,
        const std::vector<int>& velocityCurve,
        int ppq,
        float intensity) const;
};

/**
 * Quick humanization with preset styles
 */
enum class HumanizeStyle : uint8_t {
    Tight,      // Minimal variation
    Natural,    // Subtle human feel
    Loose,      // Relaxed timing
    Drunk,      // Heavy variation
    Robot       // Perfect quantization
};

/**
 * Apply quick humanization with style preset
 */
void quickHumanize(
    std::vector<MidiNote>& notes,
    HumanizeStyle style,
    int ppq);

} // namespace groove
} // namespace iDAW
