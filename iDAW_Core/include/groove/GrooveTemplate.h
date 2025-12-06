/**
 * GrooveTemplate.h - Groove pattern template for iDAW
 * 
 * Stores timing deviations, velocity patterns, and swing
 * characteristics for groove extraction and application.
 */

#pragma once

#include <string>
#include <vector>
#include <map>
#include <cstdint>

namespace iDAW {
namespace groove {

/**
 * Note event with timing and velocity info
 */
struct NoteEvent {
    int pitch;              // MIDI note number
    int velocity;           // 0-127
    int startTick;          // Absolute tick position
    int durationTicks;      // Note duration
    int channel;            // MIDI channel
    
    float deviationTicks;   // Deviation from quantized grid
    bool isGhost;           // Ghost note (low velocity)
    bool isAccent;          // Accent note (high velocity)
    
    NoteEvent()
        : pitch(0), velocity(0), startTick(0), durationTicks(0), channel(0)
        , deviationTicks(0.0f), isGhost(false), isAccent(false) {}
};

/**
 * Velocity statistics
 */
struct VelocityStats {
    int min = 0;
    int max = 127;
    float mean = 64.0f;
    float stdDev = 0.0f;
    int ghostCount = 0;
    int accentCount = 0;
};

/**
 * Timing statistics
 */
struct TimingStats {
    float meanDeviationTicks = 0.0f;
    float meanDeviationMs = 0.0f;
    float maxDeviationTicks = 0.0f;
    float maxDeviationMs = 0.0f;
    float stdDeviationTicks = 0.0f;
    float stdDeviationMs = 0.0f;
};

/**
 * GrooveTemplate - Extracted groove pattern
 * 
 * Contains timing deviations, velocity curves, and statistical measures
 * that define the "feel" of a performance.
 */
class GrooveTemplate {
public:
    GrooveTemplate() = default;
    
    /**
     * Construct with name and source info
     */
    GrooveTemplate(const std::string& name, const std::string& sourceFile = "");
    
    // Accessors
    const std::string& name() const noexcept { return m_name; }
    void setName(const std::string& name) { m_name = name; }
    
    const std::string& sourceFile() const noexcept { return m_sourceFile; }
    void setSourceFile(const std::string& file) { m_sourceFile = file; }
    
    int ppq() const noexcept { return m_ppq; }
    void setPpq(int ppq) { m_ppq = ppq; }
    
    float tempoBpm() const noexcept { return m_tempoBpm; }
    void setTempoBpm(float bpm) { m_tempoBpm = bpm; }
    
    std::pair<int, int> timeSignature() const noexcept { return m_timeSignature; }
    void setTimeSignature(int num, int denom) { m_timeSignature = {num, denom}; }
    
    // Timing analysis
    const std::vector<float>& timingDeviations() const noexcept { return m_timingDeviations; }
    void setTimingDeviations(const std::vector<float>& deviations) { m_timingDeviations = deviations; }
    
    float swingFactor() const noexcept { return m_swingFactor; }
    void setSwingFactor(float swing) { m_swingFactor = swing; }
    
    // Velocity analysis
    const std::vector<int>& velocityCurve() const noexcept { return m_velocityCurve; }
    void setVelocityCurve(const std::vector<int>& curve) { m_velocityCurve = curve; }
    
    const VelocityStats& velocityStats() const noexcept { return m_velocityStats; }
    void setVelocityStats(const VelocityStats& stats) { m_velocityStats = stats; }
    
    const TimingStats& timingStats() const noexcept { return m_timingStats; }
    void setTimingStats(const TimingStats& stats) { m_timingStats = stats; }
    
    // Events
    const std::vector<NoteEvent>& events() const noexcept { return m_events; }
    void setEvents(const std::vector<NoteEvent>& events) { m_events = events; }
    void addEvent(const NoteEvent& event) { m_events.push_back(event); }
    
    /**
     * Serialize to map for JSON export
     */
    std::map<std::string, std::string> toMap() const;
    
    /**
     * Deserialize from map
     */
    static GrooveTemplate fromMap(const std::map<std::string, std::string>& data);
    
    /**
     * Check if template is valid
     */
    bool isValid() const noexcept { return !m_events.empty() || !m_timingDeviations.empty(); }
    
private:
    std::string m_name = "Untitled Groove";
    std::string m_sourceFile;
    int m_ppq = 480;
    float m_tempoBpm = 120.0f;
    std::pair<int, int> m_timeSignature{4, 4};
    
    std::vector<float> m_timingDeviations;
    float m_swingFactor = 0.0f;
    std::vector<int> m_velocityCurve;
    
    VelocityStats m_velocityStats;
    TimingStats m_timingStats;
    
    std::vector<NoteEvent> m_events;
};

/**
 * Genre-specific groove presets
 */
enum class GenrePreset : uint8_t {
    Funk,
    Jazz,
    Rock,
    HipHop,
    LoFi,
    BoomBap,
    Dilla,
    Trap,
    Straight
};

/**
 * Get groove template for a genre preset
 */
GrooveTemplate getGenreTemplate(GenrePreset preset);

/**
 * Get genre preset by name
 */
GenrePreset getGenrePresetByName(const std::string& name);

} // namespace groove
} // namespace iDAW
