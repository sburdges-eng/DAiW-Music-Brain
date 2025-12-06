/**
 * GrooveEngine.cpp - Implementation of C++ Groove Extraction/Application Engine
 */

#include "groove/GrooveEngine.h"
#include <algorithm>
#include <cmath>
#include <random>
#include <numeric>

namespace iDAW {
namespace groove {

// MIDI velocity constants (per MIDI specification)
constexpr int MIN_VELOCITY = 1;
constexpr int MAX_VELOCITY = 127;

// ============================================================================
// GrooveTemplate Implementation
// ============================================================================

GrooveTemplate::GrooveTemplate(const std::string& name, const std::string& sourceFile)
    : m_name(name), m_sourceFile(sourceFile) {}

std::map<std::string, std::string> GrooveTemplate::toMap() const {
    std::map<std::string, std::string> data;
    data["name"] = m_name;
    data["source_file"] = m_sourceFile;
    data["ppq"] = std::to_string(m_ppq);
    data["tempo_bpm"] = std::to_string(m_tempoBpm);
    data["time_signature"] = std::to_string(m_timeSignature.first) + "/" + 
                             std::to_string(m_timeSignature.second);
    data["swing_factor"] = std::to_string(m_swingFactor);
    return data;
}

GrooveTemplate GrooveTemplate::fromMap(const std::map<std::string, std::string>& data) {
    GrooveTemplate tmpl;
    
    auto it = data.find("name");
    if (it != data.end()) tmpl.m_name = it->second;
    
    it = data.find("source_file");
    if (it != data.end()) tmpl.m_sourceFile = it->second;
    
    it = data.find("ppq");
    if (it != data.end()) tmpl.m_ppq = std::stoi(it->second);
    
    it = data.find("tempo_bpm");
    if (it != data.end()) tmpl.m_tempoBpm = std::stof(it->second);
    
    it = data.find("swing_factor");
    if (it != data.end()) tmpl.m_swingFactor = std::stof(it->second);
    
    return tmpl;
}

// ============================================================================
// Genre Preset Templates
// ============================================================================

GrooveTemplate getGenreTemplate(GenrePreset preset) {
    GrooveTemplate tmpl;
    
    switch (preset) {
        case GenrePreset::Funk:
            tmpl.setName("Funk Pocket");
            tmpl.setSwingFactor(0.58f);  // 58% swing
            tmpl.setTempoBpm(95.0f);
            {
                // Funk groove: snare slightly behind, kick slightly ahead
                std::vector<float> deviations = {
                    5.0f,   // Kick 1 - slightly ahead
                    0.0f,   // Hi-hat
                    -8.0f,  // Snare - laid back
                    3.0f,   // Hi-hat - slight push
                    5.0f,   // Kick 2
                    0.0f,   // Hi-hat
                    -10.0f, // Snare - extra laid back
                    2.0f    // Hi-hat
                };
                tmpl.setTimingDeviations(deviations);
                
                std::vector<int> velocities = {100, 60, 110, 55, 95, 58, 108, 52};
                tmpl.setVelocityCurve(velocities);
            }
            break;
            
        case GenrePreset::Jazz:
            tmpl.setName("Jazz Swing");
            tmpl.setSwingFactor(0.67f);  // Triplet swing
            tmpl.setTempoBpm(140.0f);
            {
                std::vector<float> deviations = {
                    0.0f, -5.0f, 8.0f, -3.0f, 2.0f, -7.0f, 10.0f, -4.0f
                };
                tmpl.setTimingDeviations(deviations);
                
                std::vector<int> velocities = {90, 50, 85, 55, 88, 48, 82, 52};
                tmpl.setVelocityCurve(velocities);
            }
            break;
            
        case GenrePreset::Rock:
            tmpl.setName("Rock Solid");
            tmpl.setSwingFactor(0.50f);  // Straight
            tmpl.setTempoBpm(120.0f);
            {
                std::vector<float> deviations = {
                    2.0f, 0.0f, -2.0f, 1.0f, 3.0f, 0.0f, -1.0f, 2.0f
                };
                tmpl.setTimingDeviations(deviations);
                
                std::vector<int> velocities = {110, 70, 115, 65, 108, 72, 112, 68};
                tmpl.setVelocityCurve(velocities);
            }
            break;
            
        case GenrePreset::HipHop:
            tmpl.setName("Hip-Hop Bounce");
            tmpl.setSwingFactor(0.55f);
            tmpl.setTempoBpm(90.0f);
            {
                std::vector<float> deviations = {
                    0.0f, -3.0f, -12.0f, 5.0f, 2.0f, -4.0f, -15.0f, 3.0f
                };
                tmpl.setTimingDeviations(deviations);
                
                std::vector<int> velocities = {100, 55, 105, 50, 98, 58, 102, 52};
                tmpl.setVelocityCurve(velocities);
            }
            break;
            
        case GenrePreset::LoFi:
            tmpl.setName("Lo-Fi Chill");
            tmpl.setSwingFactor(0.60f);
            tmpl.setTempoBpm(75.0f);
            {
                // Lo-fi: behind the beat, relaxed
                std::vector<float> deviations = {
                    8.0f, 5.0f, -15.0f, 10.0f, 6.0f, 8.0f, -18.0f, 12.0f
                };
                tmpl.setTimingDeviations(deviations);
                
                std::vector<int> velocities = {85, 45, 90, 42, 82, 48, 88, 40};
                tmpl.setVelocityCurve(velocities);
            }
            break;
            
        case GenrePreset::BoomBap:
            tmpl.setName("Boom Bap");
            tmpl.setSwingFactor(0.54f);
            tmpl.setTempoBpm(92.0f);
            {
                std::vector<float> deviations = {
                    0.0f, -2.0f, -8.0f, 4.0f, 2.0f, -3.0f, -10.0f, 5.0f
                };
                tmpl.setTimingDeviations(deviations);
                
                std::vector<int> velocities = {105, 55, 110, 50, 102, 58, 108, 52};
                tmpl.setVelocityCurve(velocities);
            }
            break;
            
        case GenrePreset::Dilla:
            tmpl.setName("Dilla Time");
            tmpl.setSwingFactor(0.62f);  // Heavy swing
            tmpl.setTempoBpm(88.0f);
            {
                // J Dilla style: drunk feel, heavy behind-the-beat
                std::vector<float> deviations = {
                    12.0f, 8.0f, -25.0f, 15.0f, 10.0f, 5.0f, -30.0f, 18.0f
                };
                tmpl.setTimingDeviations(deviations);
                
                std::vector<int> velocities = {95, 40, 100, 35, 92, 42, 98, 38};
                tmpl.setVelocityCurve(velocities);
            }
            break;
            
        case GenrePreset::Trap:
            tmpl.setName("Trap");
            tmpl.setSwingFactor(0.51f);  // Almost straight
            tmpl.setTempoBpm(140.0f);
            {
                std::vector<float> deviations = {
                    0.0f, 0.0f, -3.0f, 1.0f, 0.0f, 0.0f, -2.0f, 2.0f
                };
                tmpl.setTimingDeviations(deviations);
                
                std::vector<int> velocities = {110, 60, 112, 55, 108, 62, 110, 58};
                tmpl.setVelocityCurve(velocities);
            }
            break;
            
        case GenrePreset::Straight:
        default:
            tmpl.setName("Straight");
            tmpl.setSwingFactor(0.50f);
            tmpl.setTempoBpm(120.0f);
            {
                std::vector<float> deviations = {0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f};
                tmpl.setTimingDeviations(deviations);
                
                std::vector<int> velocities = {100, 70, 100, 70, 100, 70, 100, 70};
                tmpl.setVelocityCurve(velocities);
            }
            break;
    }
    
    return tmpl;
}

GenrePreset getGenrePresetByName(const std::string& name) {
    std::string lower = name;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);
    
    if (lower == "funk") return GenrePreset::Funk;
    if (lower == "jazz") return GenrePreset::Jazz;
    if (lower == "rock") return GenrePreset::Rock;
    if (lower == "hiphop" || lower == "hip-hop" || lower == "hip hop") 
        return GenrePreset::HipHop;
    if (lower == "lofi" || lower == "lo-fi" || lower == "lo fi") 
        return GenrePreset::LoFi;
    if (lower == "boombap" || lower == "boom-bap" || lower == "boom bap") 
        return GenrePreset::BoomBap;
    if (lower == "dilla") return GenrePreset::Dilla;
    if (lower == "trap") return GenrePreset::Trap;
    
    return GenrePreset::Straight;
}

// ============================================================================
// GrooveEngine Implementation
// ============================================================================

GrooveEngine& GrooveEngine::getInstance() {
    static GrooveEngine instance;
    return instance;
}

GrooveTemplate GrooveEngine::extractGroove(
    const std::vector<MidiNote>& notes,
    int ppq,
    float tempoBpm,
    const ExtractionSettings& settings) const {
    
    GrooveTemplate tmpl;
    tmpl.setPpq(ppq);
    tmpl.setTempoBpm(tempoBpm);
    
    if (notes.empty()) {
        return tmpl;
    }
    
    // Calculate grid resolution in ticks
    int ticksPerGrid = ppq * 4 / settings.quantizeResolution;
    
    // Extract timing deviations
    std::vector<float> deviations;
    std::vector<int> velocities;
    int ghostCount = 0;
    int accentCount = 0;
    
    for (const auto& note : notes) {
        // Calculate deviation from nearest grid position
        int nearestGrid = static_cast<int>(std::round(
            static_cast<float>(note.startTick) / ticksPerGrid) * ticksPerGrid);
        float deviation = static_cast<float>(note.startTick - nearestGrid);
        deviations.push_back(deviation);
        
        // Collect velocity
        velocities.push_back(note.velocity);
        
        // Count ghost/accent notes
        if (note.velocity < settings.ghostThreshold) ghostCount++;
        if (note.velocity > settings.accentThreshold) accentCount++;
        
        // Add note event
        NoteEvent event;
        event.pitch = note.pitch;
        event.velocity = note.velocity;
        event.startTick = note.startTick;
        event.durationTicks = note.durationTicks;
        event.deviationTicks = deviation;
        event.isGhost = (note.velocity < settings.ghostThreshold);
        event.isAccent = (note.velocity > settings.accentThreshold);
        tmpl.addEvent(event);
    }
    
    tmpl.setTimingDeviations(deviations);
    
    // Calculate swing factor
    if (settings.detectSwing) {
        float swing = calculateSwing(notes, ppq);
        tmpl.setSwingFactor(swing);
    }
    
    // Calculate velocity stats
    VelocityStats velStats;
    if (!velocities.empty()) {
        velStats.min = *std::min_element(velocities.begin(), velocities.end());
        velStats.max = *std::max_element(velocities.begin(), velocities.end());
        velStats.mean = std::accumulate(velocities.begin(), velocities.end(), 0.0f) / 
                        velocities.size();
        velStats.ghostCount = ghostCount;
        velStats.accentCount = accentCount;
        
        // Calculate standard deviation
        float sumSq = 0.0f;
        for (int v : velocities) {
            float diff = v - velStats.mean;
            sumSq += diff * diff;
        }
        velStats.stdDev = std::sqrt(sumSq / velocities.size());
    }
    tmpl.setVelocityStats(velStats);
    
    // Calculate timing stats
    TimingStats timeStats;
    if (!deviations.empty()) {
        float sumDev = std::accumulate(deviations.begin(), deviations.end(), 0.0f);
        timeStats.meanDeviationTicks = sumDev / deviations.size();
        timeStats.meanDeviationMs = timeStats.meanDeviationTicks * (60000.0f / tempoBpm / ppq);
        
        float maxDev = 0.0f;
        for (float d : deviations) {
            maxDev = std::max(maxDev, std::abs(d));
        }
        timeStats.maxDeviationTicks = maxDev;
        timeStats.maxDeviationMs = maxDev * (60000.0f / tempoBpm / ppq);
        
        // Standard deviation
        float sumSq = 0.0f;
        for (float d : deviations) {
            float diff = d - timeStats.meanDeviationTicks;
            sumSq += diff * diff;
        }
        timeStats.stdDeviationTicks = std::sqrt(sumSq / deviations.size());
        timeStats.stdDeviationMs = timeStats.stdDeviationTicks * (60000.0f / tempoBpm / ppq);
    }
    tmpl.setTimingStats(timeStats);
    
    // Build velocity curve (per beat)
    int totalBeats = 0;
    if (!notes.empty()) {
        int maxTick = 0;
        for (const auto& note : notes) {
            maxTick = std::max(maxTick, note.startTick);
        }
        totalBeats = maxTick / ppq + 1;
    }
    
    std::vector<int> velocityCurve(totalBeats, 0);
    std::vector<int> noteCounts(totalBeats, 0);
    
    for (const auto& note : notes) {
        int beat = note.startTick / ppq;
        if (beat < totalBeats) {
            velocityCurve[beat] += note.velocity;
            noteCounts[beat]++;
        }
    }
    
    for (int i = 0; i < totalBeats; i++) {
        if (noteCounts[i] > 0) {
            velocityCurve[i] /= noteCounts[i];
        }
    }
    
    tmpl.setVelocityCurve(velocityCurve);
    
    return tmpl;
}

void GrooveEngine::applyGroove(
    std::vector<MidiNote>& notes,
    const GrooveTemplate& groove,
    int ppq,
    const ApplicationSettings& settings) const {
    
    if (notes.empty() || !groove.isValid()) {
        return;
    }
    
    const auto& deviations = groove.timingDeviations();
    const auto& velocityCurve = groove.velocityCurve();
    
    for (size_t i = 0; i < notes.size(); i++) {
        auto& note = notes[i];
        
        // Apply timing deviation
        if (settings.applyTiming && !deviations.empty()) {
            size_t devIdx = i % deviations.size();
            float deviation = deviations[devIdx] * settings.intensity;
            applyTimingDeviation(note, deviation, settings.intensity);
        }
        
        // Apply velocity curve
        if (settings.applyVelocity && !velocityCurve.empty()) {
            applyVelocityCurve(note, velocityCurve, ppq, settings.intensity);
        }
    }
    
    // Apply swing
    if (settings.applySwing && groove.swingFactor() != 0.5f) {
        int eighthNoteTicks = ppq / 2;
        
        for (auto& note : notes) {
            int positionInBeat = note.startTick % ppq;
            
            // Check if on off-beat (near middle of beat)
            if (std::abs(positionInBeat - eighthNoteTicks) < ppq * 0.15) {
                // Apply swing offset
                float swingOffset = (groove.swingFactor() - 0.5f) * eighthNoteTicks * 2.0f;
                swingOffset *= settings.intensity;
                note.startTick += static_cast<int>(swingOffset);
            }
        }
    }
}

void GrooveEngine::humanize(
    std::vector<MidiNote>& notes,
    float complexity,
    float vulnerability,
    int ppq,
    int seed) const {
    
    if (notes.empty()) {
        return;
    }
    
    std::mt19937 rng;
    if (seed >= 0) {
        rng.seed(static_cast<unsigned int>(seed));
    } else {
        std::random_device rd;
        rng.seed(rd());
    }
    
    // Calculate timing range based on complexity
    float maxTimingDeviation = complexity * 30.0f;  // Up to 30 ticks at max complexity
    
    // Calculate velocity range based on vulnerability
    float velocityRange = vulnerability * 20.0f;  // ±20 velocity at max vulnerability
    
    std::normal_distribution<float> timingDist(0.0f, maxTimingDeviation / 3.0f);
    std::normal_distribution<float> velocityDist(0.0f, velocityRange / 3.0f);
    
    // Human latency bias (slightly behind the beat)
    float latencyBias = 5.0f * complexity;
    
    for (auto& note : notes) {
        // Apply timing humanization
        float timingOffset = timingDist(rng) + latencyBias;
        note.startTick += static_cast<int>(timingOffset);
        if (note.startTick < 0) note.startTick = 0;
        
        // Apply velocity humanization
        float velocityOffset = velocityDist(rng);
        note.velocity += static_cast<int>(velocityOffset);
        note.velocity = std::clamp(note.velocity, MIN_VELOCITY, MAX_VELOCITY);
    }
}

float GrooveEngine::calculateSwing(const std::vector<MidiNote>& notes, int ppq) const {
    if (notes.size() < 4) {
        return 0.5f;  // Default straight
    }
    
    int eighthNoteTicks = ppq / 2;
    
    std::vector<MidiNote> offBeatNotes;
    for (const auto& note : notes) {
        int positionInBeat = note.startTick % ppq;
        
        // Off-beat (near middle of beat)
        if (std::abs(positionInBeat - eighthNoteTicks) < ppq * 0.15) {
            offBeatNotes.push_back(note);
        }
    }
    
    if (offBeatNotes.empty()) {
        return 0.5f;
    }
    
    // Calculate average offset of off-beat notes
    float sumOffset = 0.0f;
    for (const auto& note : offBeatNotes) {
        int positionInBeat = note.startTick % ppq;
        float offset = static_cast<float>(positionInBeat - eighthNoteTicks) / eighthNoteTicks;
        sumOffset += offset;
    }
    
    float avgOffset = sumOffset / offBeatNotes.size();
    
    // Normalize to 0.0-1.0 range
    return std::clamp(avgOffset + 0.5f, 0.0f, 1.0f);
}

GrooveTemplate GrooveEngine::getGenreTemplate(const std::string& genre) const {
    GenrePreset preset = getGenrePresetByName(genre);
    return groove::getGenreTemplate(preset);
}

GrooveTemplate GrooveEngine::getGenreTemplate(GenrePreset preset) const {
    return groove::getGenreTemplate(preset);
}

std::vector<std::string> GrooveEngine::listGenrePresets() const {
    return {"funk", "jazz", "rock", "hiphop", "lofi", "boombap", "dilla", "trap", "straight"};
}

void GrooveEngine::quantize(
    std::vector<MidiNote>& notes,
    int ppq,
    int resolution) const {
    
    int ticksPerGrid = ppq * 4 / resolution;
    
    for (auto& note : notes) {
        int nearestGrid = static_cast<int>(std::round(
            static_cast<float>(note.startTick) / ticksPerGrid) * ticksPerGrid);
        note.startTick = nearestGrid;
    }
}

float GrooveEngine::calculateDeviationForNote(
    const MidiNote& note,
    int ppq,
    int resolution) const {
    
    int ticksPerGrid = ppq * 4 / resolution;
    int nearestGrid = static_cast<int>(std::round(
        static_cast<float>(note.startTick) / ticksPerGrid) * ticksPerGrid);
    return static_cast<float>(note.startTick - nearestGrid);
}

void GrooveEngine::applyTimingDeviation(
    MidiNote& note,
    float deviation,
    float intensity) const {
    
    note.startTick += static_cast<int>(deviation * intensity);
    if (note.startTick < 0) note.startTick = 0;
}

void GrooveEngine::applyVelocityCurve(
    MidiNote& note,
    const std::vector<int>& velocityCurve,
    int ppq,
    float intensity) const {
    
    if (velocityCurve.empty()) return;
    
    int beat = note.startTick / ppq;
    if (beat >= static_cast<int>(velocityCurve.size())) {
        beat = beat % velocityCurve.size();
    }
    
    int targetVelocity = velocityCurve[beat];
    float blend = intensity;
    
    note.velocity = static_cast<int>(note.velocity * (1.0f - blend) + targetVelocity * blend);
    note.velocity = std::clamp(note.velocity, MIN_VELOCITY, MAX_VELOCITY);
}

// ============================================================================
// Quick Humanize
// ============================================================================

void quickHumanize(
    std::vector<MidiNote>& notes,
    HumanizeStyle style,
    int ppq) {
    
    float complexity = 0.0f;
    float vulnerability = 0.0f;
    
    switch (style) {
        case HumanizeStyle::Tight:
            complexity = 0.1f;
            vulnerability = 0.1f;
            break;
        case HumanizeStyle::Natural:
            complexity = 0.3f;
            vulnerability = 0.3f;
            break;
        case HumanizeStyle::Loose:
            complexity = 0.5f;
            vulnerability = 0.5f;
            break;
        case HumanizeStyle::Drunk:
            complexity = 0.8f;
            vulnerability = 0.8f;
            break;
        case HumanizeStyle::Robot:
            // No humanization
            GrooveEngine::getInstance().quantize(notes, ppq, 16);
            return;
    }
    
    GrooveEngine::getInstance().humanize(notes, complexity, vulnerability, ppq);
}

} // namespace groove
} // namespace iDAW
