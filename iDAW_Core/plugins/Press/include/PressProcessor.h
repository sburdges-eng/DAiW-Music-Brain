/**
 * PressProcessor.h - Plugin 003: "The Press"
 * 
 * Profile: 'VCA Workhorse' (Clean, RMS Detection, Feed-Forward)
 * 
 * A clean, transparent VCA-style digital compressor with:
 * - RMS level detection for musical response
 * - Feed-forward topology for predictable behavior
 * - Accurate gain reduction metering
 * - Ghost Hands AI integration (Punchy/Glue presets)
 * - Heartbeat visualization mapping GR to heart animation
 */

#pragma once

#include <JuceHeader.h>
#include <atomic>
#include <cmath>
#include <array>

namespace iDAW {

/**
 * Configuration for The Press compressor
 */
struct PressConfig {
    // Parameter ranges
    static constexpr float MIN_THRESHOLD_DB = -60.0f;
    static constexpr float MAX_THRESHOLD_DB = 0.0f;
    static constexpr float MIN_RATIO = 1.0f;
    static constexpr float MAX_RATIO = 20.0f;
    static constexpr float MIN_ATTACK_MS = 0.1f;
    static constexpr float MAX_ATTACK_MS = 100.0f;
    static constexpr float MIN_RELEASE_MS = 10.0f;
    static constexpr float MAX_RELEASE_MS = 2000.0f;
    static constexpr float MIN_GAIN_DB = -12.0f;
    static constexpr float MAX_GAIN_DB = 24.0f;
    
    // RMS detection window
    static constexpr float RMS_WINDOW_MS = 10.0f;
    
    // Knee width in dB (soft knee)
    static constexpr float KNEE_WIDTH_DB = 6.0f;
};

/**
 * Compressor parameters structure
 */
struct CompressorParams {
    float thresholdDb = -20.0f;  // Threshold in dB
    float ratio = 4.0f;          // Compression ratio (N:1)
    float attackMs = 10.0f;      // Attack time in ms
    float releaseMs = 100.0f;    // Release time in ms
    float makeupGainDb = 0.0f;   // Makeup gain in dB
    bool autoMakeup = false;     // Auto makeup gain
};

/**
 * Visual state for Heartbeat shader
 */
struct HeartbeatVisualState {
    float heartScale = 1.0f;         // Maps to heart size (systole/diastole)
    float heartRelaxationRate = 0.5f; // Maps to release time
    float gainReductionDb = 0.0f;    // Current GR in dB
    float inputLevel = 0.0f;         // Input level for display
    float outputLevel = 0.0f;        // Output level for display
};

/**
 * AI preset types for Ghost Hands
 */
enum class CompressorPreset {
    PUNCHY,  // Attack: 30ms, Ratio: 4:1
    GLUE,    // Attack: 1ms, Ratio: 2:1
    CUSTOM
};

/**
 * PressProcessor - VCA Digital Compressor
 * 
 * Algorithm (Feed-Forward, RMS Detection):
 * 1. Calculate RMS level of input signal
 * 2. Convert to dB scale
 * 3. Calculate gain reduction based on threshold/ratio (with soft knee)
 * 4. Apply attack/release envelope to gain reduction
 * 5. Apply gain reduction to input signal
 * 6. Apply makeup gain
 */
class PressProcessor : public juce::AudioProcessor {
public:
    //==========================================================================
    // Constructor / Destructor
    //==========================================================================
    
    PressProcessor();
    ~PressProcessor() override;
    
    //==========================================================================
    // AudioProcessor Interface
    //==========================================================================
    
    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;
    void processBlock(juce::AudioBuffer<float>& buffer, 
                      juce::MidiBuffer& midiMessages) override;
    
    // Editor
    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }
    
    // Program/State
    const juce::String getName() const override { return "The Press"; }
    bool acceptsMidi() const override { return false; }
    bool producesMidi() const override { return false; }
    double getTailLengthSeconds() const override { return 0.0; }
    
    // Programs
    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram(int) override {}
    const juce::String getProgramName(int) override { return {}; }
    void changeProgramName(int, const juce::String&) override {}
    
    // State save/load
    void getStateInformation(juce::MemoryBlock& destData) override;
    void setStateInformation(const void* data, int sizeInBytes) override;
    
    //==========================================================================
    // Compressor Parameters
    //==========================================================================
    
    void setThreshold(float thresholdDb);
    float getThreshold() const { return m_params.thresholdDb; }
    
    void setRatio(float ratio);
    float getRatio() const { return m_params.ratio; }
    
    void setAttack(float attackMs);
    float getAttack() const { return m_params.attackMs; }
    
    void setRelease(float releaseMs);
    float getRelease() const { return m_params.releaseMs; }
    
    void setMakeupGain(float gainDb);
    float getMakeupGain() const { return m_params.makeupGainDb; }
    
    void setAutoMakeup(bool enabled);
    bool getAutoMakeup() const { return m_params.autoMakeup; }
    
    //==========================================================================
    // Ghost Hands Integration
    //==========================================================================
    
    /**
     * Apply AI preset
     * @param preset PUNCHY or GLUE
     */
    void applyPreset(CompressorPreset preset);
    
    /**
     * Apply AI suggestion by name
     * @param suggestionName "Punchy" or "Glue"
     */
    void applyAISuggestion(const juce::String& suggestionName);
    
    //==========================================================================
    // Metering
    //==========================================================================
    
    /**
     * Get current gain reduction in dB (always positive or zero)
     */
    float getGainReduction() const { return m_gainReductionDb.load(); }
    
    /**
     * Get input level in dB
     */
    float getInputLevel() const { return m_inputLevelDb.load(); }
    
    /**
     * Get output level in dB
     */
    float getOutputLevel() const { return m_outputLevelDb.load(); }
    
    /**
     * Get visual state for Heartbeat shader
     */
    HeartbeatVisualState getVisualState() const;
    
private:
    //==========================================================================
    // DSP Processing
    //==========================================================================
    
    /**
     * Calculate RMS level of a buffer
     */
    float calculateRMS(const float* samples, int numSamples);
    
    /**
     * Calculate gain reduction for a given input level
     * Uses soft knee for smoother compression
     */
    float calculateGainReduction(float inputDb);
    
    /**
     * Apply attack/release envelope to gain value
     */
    float applyEnvelope(float targetGain, float currentGain);
    
    /**
     * Convert linear to dB
     */
    static float linearToDb(float linear) {
        return 20.0f * std::log10(std::max(linear, 1e-10f));
    }
    
    /**
     * Convert dB to linear
     */
    static float dbToLinear(float db) {
        return std::pow(10.0f, db / 20.0f);
    }
    
    /**
     * Calculate auto makeup gain based on threshold and ratio
     */
    float calculateAutoMakeup() const;
    
    /**
     * Update envelope coefficients based on attack/release times
     */
    void updateEnvelopeCoeffs();
    
    //==========================================================================
    // Parameters
    //==========================================================================
    
    CompressorParams m_params;
    
    // Envelope coefficients
    float m_attackCoeff = 0.0f;
    float m_releaseCoeff = 0.0f;
    
    // RMS window size in samples
    int m_rmsWindowSamples = 0;
    
    //==========================================================================
    // State
    //==========================================================================
    
    double m_sampleRate = 44100.0;
    bool m_prepared = false;
    
    // Envelope state (gain in linear)
    float m_envelopeState = 1.0f;
    
    // RMS calculation buffer
    std::vector<float> m_rmsBuffer;
    int m_rmsBufferIndex = 0;
    float m_rmsSum = 0.0f;
    
    //==========================================================================
    // Metering (atomic for thread safety)
    //==========================================================================
    
    std::atomic<float> m_gainReductionDb{0.0f};
    std::atomic<float> m_inputLevelDb{-100.0f};
    std::atomic<float> m_outputLevelDb{-100.0f};
    
    // Peak hold for metering
    float m_inputPeak = 0.0f;
    float m_outputPeak = 0.0f;
    static constexpr float METER_DECAY = 0.9995f;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(PressProcessor)
};

} // namespace iDAW
