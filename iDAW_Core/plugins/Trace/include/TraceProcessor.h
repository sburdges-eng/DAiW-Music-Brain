/**
 * TraceProcessor.h - Plugin 005: "The Trace"
 * 
 * Profile: 'Tape/Digital Delay' with Spirograph UI
 * 
 * Features:
 * - Circular buffer delay line
 * - Ping-pong stereo mode
 * - Tape saturation on feedback
 * - LFO modulation for wow/flutter
 * - Host BPM sync
 */

#pragma once

#include <JuceHeader.h>
#include <atomic>
#include <array>
#include <cmath>

namespace iDAW {

/**
 * Configuration for The Trace
 */
struct TraceConfig {
    static constexpr float MAX_DELAY_MS = 2000.0f;
    static constexpr float MIN_DELAY_MS = 1.0f;
    static constexpr float MAX_FEEDBACK = 0.95f;
    static constexpr float MAX_MODULATION_DEPTH = 50.0f;  // ms
    static constexpr float MAX_MODULATION_RATE = 10.0f;   // Hz
    static constexpr float TAPE_DRIVE = 2.0f;
};

/**
 * Sync note values
 */
enum class SyncNote {
    FREE,           // Free running (ms)
    WHOLE,          // 1/1
    HALF,           // 1/2
    QUARTER,        // 1/4
    QUARTER_DOT,    // 1/4 dotted
    EIGHTH,         // 1/8
    EIGHTH_DOT,     // 1/8 dotted
    SIXTEENTH,      // 1/16
    TRIPLET_QUARTER,// 1/4 triplet
    TRIPLET_EIGHTH  // 1/8 triplet
};

/**
 * Visual state for Spirograph shader
 */
struct SpirographVisualState {
    float outerRadius = 0.5f;     // R (mapped from delay time)
    float innerRadius = 0.3f;     // r
    float loopCount = 3.0f;       // k (mapped from feedback)
    float rotationSpeed = 1.0f;   // Animation speed
    float lineThickness = 1.0f;   // Pencil thickness
    float traceProgress = 0.0f;   // How much of the trace is drawn
};

/**
 * TraceProcessor - Tape/Digital Delay
 * 
 * Algorithm:
 * 1. Write input to circular buffer
 * 2. Read from buffer with modulated delay time
 * 3. Apply tape saturation to delayed signal
 * 4. Mix feedback into buffer
 * 5. Output dry + wet blend
 */
class TraceProcessor : public juce::AudioProcessor {
public:
    TraceProcessor();
    ~TraceProcessor() override;
    
    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;
    void processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages) override;
    
    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }
    
    const juce::String getName() const override { return "The Trace"; }
    bool acceptsMidi() const override { return false; }
    bool producesMidi() const override { return false; }
    double getTailLengthSeconds() const override;
    
    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram(int) override {}
    const juce::String getProgramName(int) override { return {}; }
    void changeProgramName(int, const juce::String&) override {}
    
    void getStateInformation(juce::MemoryBlock& destData) override;
    void setStateInformation(const void* data, int sizeInBytes) override;
    
    // Parameters
    void setDelayTime(float timeMs);
    float getDelayTime() const { return m_delayTimeMs.load(); }
    
    void setFeedback(float feedback);
    float getFeedback() const { return m_feedback.load(); }
    
    void setMix(float mix);
    float getMix() const { return m_mix.load(); }
    
    void setModulationDepth(float depthMs);
    float getModulationDepth() const { return m_modDepthMs.load(); }
    
    void setModulationRate(float rateHz);
    float getModulationRate() const { return m_modRateHz.load(); }
    
    void setPingPong(bool enabled);
    bool getPingPong() const { return m_pingPong.load(); }
    
    void setSync(SyncNote note);
    SyncNote getSync() const { return m_syncNote; }
    
    void setTapeSaturation(bool enabled);
    bool getTapeSaturation() const { return m_tapeSaturation.load(); }
    
    // Ghost Hands
    void applyAISuggestion(const juce::String& suggestion);
    
    // Visual state
    SpirographVisualState getVisualState() const;
    
    // Host sync
    void updateFromPlayHead(juce::AudioPlayHead* playHead);
    
private:
    float readFromBuffer(int channel, float delaySamples);
    void writeToBuffer(int channel, float sample);
    float applyTapeSaturation(float sample);
    float calculateSyncedDelay(double bpm);
    void updateLFO();
    
    // Circular delay buffer (stereo)
    std::array<std::vector<float>, 2> m_delayBuffer;
    std::array<int, 2> m_writeIndex;
    int m_bufferSize = 0;
    
    // LFO for modulation
    float m_lfoPhase = 0.0f;
    float m_currentModulation = 0.0f;
    
    // Parameters
    std::atomic<float> m_delayTimeMs{300.0f};
    std::atomic<float> m_feedback{0.3f};
    std::atomic<float> m_mix{0.5f};
    std::atomic<float> m_modDepthMs{0.0f};
    std::atomic<float> m_modRateHz{0.5f};
    std::atomic<bool> m_pingPong{false};
    std::atomic<bool> m_tapeSaturation{true};
    SyncNote m_syncNote = SyncNote::FREE;
    
    // Host tempo
    double m_hostBPM = 120.0;
    
    // Visual state
    SpirographVisualState m_visualState;
    mutable std::mutex m_visualMutex;
    
    double m_sampleRate = 44100.0;
    bool m_prepared = false;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(TraceProcessor)
};

} // namespace iDAW
