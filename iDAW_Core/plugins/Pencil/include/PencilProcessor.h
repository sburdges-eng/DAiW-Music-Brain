/**
 * PencilProcessor.h - Plugin 002: "The Pencil"
 * 
 * Profile: 'Graphite' (Tube Saturation / Additive EQ)
 * 
 * A parallel multi-band saturation processor that adds warmth and harmonic content.
 * Uses tube-style non-linear transfer functions to generate 2nd order harmonics.
 * 
 * Features:
 * - 3 Parallel Bandpass Filters (Low, Mid, High)
 * - TubeDrive per band with tanh/polynomial saturation
 * - Parallel dry/wet mixing
 * - Ghost Hands AI integration for "Warmth" suggestions
 * - Visual feedback: Drive → LineThickness/LineNoise mapping
 */

#pragma once

#include <JuceHeader.h>
#include <array>
#include <atomic>
#include <cmath>

namespace iDAW {

/**
 * Configuration for The Pencil processor
 */
struct PencilConfig {
    // Band frequency crossovers
    static constexpr float LOW_CROSSOVER = 250.0f;    // Hz
    static constexpr float HIGH_CROSSOVER = 4000.0f;  // Hz
    
    // Default Q factors for bandpass filters
    static constexpr float LOW_Q = 0.707f;
    static constexpr float MID_Q = 1.0f;
    static constexpr float HIGH_Q = 0.707f;
    
    // Saturation parameters
    static constexpr float MAX_DRIVE = 10.0f;         // Maximum drive amount
    static constexpr float HEADROOM_DB = -6.0f;       // Headroom to prevent clipping
};

/**
 * Band parameters for each frequency band
 */
struct BandParameters {
    float frequency = 1000.0f;  // Center frequency (Hz)
    float q = 1.0f;             // Q factor
    float drive = 1.0f;         // Drive amount (1.0 = unity, >1 = saturation)
    float mix = 0.5f;           // Dry/wet mix (0 = dry, 1 = wet)
    bool enabled = true;        // Band enable/bypass
};

/**
 * Visual feedback state for OpenGL shader
 */
struct GraphiteVisualState {
    float lineThickness = 1.0f;   // Maps to shader LineThickness uniform
    float lineNoise = 0.0f;       // Maps to shader LineNoise uniform (graininess)
    float overallDrive = 0.0f;    // Combined drive for visual feedback
    std::array<float, 3> bandLevels = {0.0f, 0.0f, 0.0f};  // Per-band output levels
};

/**
 * Biquad filter state for each band
 */
struct BiquadState {
    float x1 = 0.0f, x2 = 0.0f;  // Input history
    float y1 = 0.0f, y2 = 0.0f;  // Output history
};

/**
 * Biquad filter coefficients
 */
struct BiquadCoeffs {
    float b0 = 1.0f, b1 = 0.0f, b2 = 0.0f;  // Numerator
    float a1 = 0.0f, a2 = 0.0f;              // Denominator (a0 normalized to 1)
};

/**
 * PencilProcessor - Tube Saturation / Additive EQ Processor
 * 
 * Algorithm:
 * 1. Split input into 3 frequency bands (Low, Mid, High)
 * 2. Apply TubeDrive saturation to each band
 * 3. Mix saturated bands back with dry signal (parallel processing)
 * 4. Sum all bands to output
 * 
 * Saturation uses tanh-based soft clipping with asymmetric
 * characteristics to generate even (2nd order) harmonics.
 */
class PencilProcessor : public juce::AudioProcessor {
public:
    //==========================================================================
    // Constructor / Destructor
    //==========================================================================
    
    PencilProcessor();
    ~PencilProcessor() override;
    
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
    const juce::String getName() const override { return "The Pencil"; }
    bool acceptsMidi() const override { return false; }
    bool producesMidi() const override { return false; }
    double getTailLengthSeconds() const override { return 0.0; }
    
    // Programs (not used)
    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram(int) override {}
    const juce::String getProgramName(int) override { return {}; }
    void changeProgramName(int, const juce::String&) override {}
    
    // State save/load
    void getStateInformation(juce::MemoryBlock& destData) override;
    void setStateInformation(const void* data, int sizeInBytes) override;
    
    //==========================================================================
    // Band Parameters
    //==========================================================================
    
    /**
     * Set parameters for a specific band
     * @param bandIndex 0=Low, 1=Mid, 2=High
     * @param params Band parameters
     */
    void setBandParameters(int bandIndex, const BandParameters& params);
    BandParameters getBandParameters(int bandIndex) const;
    
    /**
     * Set drive for a specific band
     */
    void setBandDrive(int bandIndex, float drive);
    float getBandDrive(int bandIndex) const;
    
    /**
     * Set mix for a specific band
     */
    void setBandMix(int bandIndex, float mix);
    
    /**
     * Set global output gain
     */
    void setOutputGain(float gainDb);
    float getOutputGain() const { return m_outputGainDb.load(); }
    
    //==========================================================================
    // Ghost Hands Integration
    //==========================================================================
    
    /**
     * Apply AI suggestion for "Warmth"
     * Boosts Low-Mids and increases Drive
     * @param warmthAmount 0-1 normalized warmth intensity
     */
    void applyWarmthFromAI(float warmthAmount);
    
    /**
     * Set all parameters from AI
     * @param lowDrive Low band drive (0-1 normalized)
     * @param midDrive Mid band drive (0-1 normalized)
     * @param highDrive High band drive (0-1 normalized)
     */
    void setParametersFromAI(float lowDrive, float midDrive, float highDrive);
    
    //==========================================================================
    // Visual Feedback
    //==========================================================================
    
    /**
     * Get visual state for shader uniforms
     */
    GraphiteVisualState getVisualState() const;
    
    /**
     * Get per-band output levels for metering
     */
    std::array<float, 3> getBandLevels() const;
    
private:
    //==========================================================================
    // DSP Processing
    //==========================================================================
    
    /**
     * Process a single sample through all bands
     */
    float processSample(float input, int channel);
    
    /**
     * Apply bandpass filter
     */
    float applyBandpass(float input, int bandIndex, int channel);
    
    /**
     * Apply tube drive saturation
     * Generates 2nd order harmonics using asymmetric tanh
     */
    float applyTubeDrive(float input, float drive);
    
    /**
     * Tanh-based soft saturation with asymmetry for even harmonics
     */
    float tubeSaturate(float x, float drive);
    
    /**
     * Calculate biquad coefficients for bandpass filter
     */
    void calculateBandpassCoeffs(int bandIndex);
    
    /**
     * Update visual state from current parameters
     */
    void updateVisualState();
    
    //==========================================================================
    // Filter State
    //==========================================================================
    
    // 3 bands x 2 channels
    std::array<std::array<BiquadState, 2>, 3> m_filterState;
    std::array<BiquadCoeffs, 3> m_filterCoeffs;
    
    //==========================================================================
    // Parameters
    //==========================================================================
    
    std::array<BandParameters, 3> m_bandParams;
    std::atomic<float> m_outputGainDb{0.0f};
    std::atomic<float> m_outputGainLinear{1.0f};
    
    //==========================================================================
    // Visual State
    //==========================================================================
    
    GraphiteVisualState m_visualState;
    mutable std::mutex m_visualStateMutex;
    
    // Per-band level tracking
    std::array<std::atomic<float>, 3> m_bandLevels;
    static constexpr float LEVEL_DECAY = 0.99f;
    
    //==========================================================================
    // State
    //==========================================================================
    
    double m_sampleRate = 44100.0;
    bool m_prepared = false;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(PencilProcessor)
};

} // namespace iDAW
