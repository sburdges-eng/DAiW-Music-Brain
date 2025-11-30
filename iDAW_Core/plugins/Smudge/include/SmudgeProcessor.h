/**
 * SmudgeProcessor.h - Plugin 004: "The Smudge"
 * 
 * Profile: 'Convolution Reverb' with Scrapbook UI
 * 
 * A zero-latency convolution engine with:
 * - FFT partitioning for efficient convolution
 * - IR library with .wav loading
 * - Time stretching for decay control
 * - Ghost Hands AI for space selection
 */

#pragma once

#include <JuceHeader.h>
#include <atomic>
#include <vector>
#include <complex>
#include <map>

namespace iDAW {

/**
 * Configuration for The Smudge
 */
struct SmudgeConfig {
    static constexpr int FFT_ORDER = 10;           // 2^10 = 1024 samples
    static constexpr int FFT_SIZE = 1 << FFT_ORDER;
    static constexpr int MAX_IR_LENGTH = 48000 * 10; // 10 seconds at 48kHz
    static constexpr float MAX_PREDELAY_MS = 200.0f;
    static constexpr float MAX_DECAY = 3.0f;       // Time stretch factor
};

/**
 * Impulse Response data
 */
struct ImpulseResponse {
    std::vector<float> samples;
    int sampleRate = 44100;
    juce::String name;
    juce::String category;  // "Cave", "Room", "Hall", etc.
};

/**
 * Visual state for Scrapbook shader
 */
struct ScrapbookVisualState {
    float photoCornerX = 0.5f;    // Photo corner position (for decay drag)
    float photoCornerY = 0.5f;
    float paperGrain = 0.5f;      // Paper texture intensity
    float tearProgress = 0.0f;    // Paper tear animation (0-1)
    juce::String currentSpace;    // Current IR name
};

/**
 * SmudgeProcessor - Zero-Latency Convolution Reverb
 * 
 * Algorithm (Uniformly Partitioned Convolution):
 * 1. Partition IR into FFT-sized blocks
 * 2. For each audio block:
 *    a. FFT the input
 *    b. Multiply with all IR partitions (frequency domain)
 *    c. Accumulate in overlap-add buffer
 *    d. IFFT and output
 */
class SmudgeProcessor : public juce::AudioProcessor {
public:
    SmudgeProcessor();
    ~SmudgeProcessor() override;
    
    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;
    void processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages) override;
    
    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }
    
    const juce::String getName() const override { return "The Smudge"; }
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
    void setMix(float mix);
    float getMix() const { return m_mix.load(); }
    
    void setDecay(float decay);
    float getDecay() const { return m_decay.load(); }
    
    void setPreDelay(float preDelayMs);
    float getPreDelay() const { return m_preDelayMs.load(); }
    
    void setHighCut(float freqHz);
    float getHighCut() const { return m_highCutHz.load(); }
    
    // IR Management
    bool loadIR(const juce::File& file);
    bool loadIRFromLibrary(const juce::String& name);
    std::vector<juce::String> getAvailableIRs() const;
    juce::String getCurrentIRName() const { return m_currentIRName; }
    
    // Ghost Hands
    void applyAISuggestion(const juce::String& spaceName);
    
    // Visual state
    ScrapbookVisualState getVisualState() const;
    void setPhotoCorner(float x, float y);
    
private:
    void processConvolution(float* input, float* output, int numSamples);
    void prepareIR();
    void applyTimeStretch(float stretchFactor);
    void updateHighCutFilter();
    
    // FFT
    std::unique_ptr<juce::dsp::FFT> m_fft;
    
    // IR data
    ImpulseResponse m_currentIR;
    std::vector<std::vector<std::complex<float>>> m_irPartitions;
    juce::String m_currentIRName;
    
    // Convolution buffers
    std::vector<float> m_inputBuffer;
    std::vector<float> m_outputBuffer;
    std::vector<std::complex<float>> m_fftBuffer;
    std::vector<std::vector<std::complex<float>>> m_fdlBuffer; // Frequency-domain delay line
    int m_fdlIndex = 0;
    
    // Pre-delay
    std::vector<float> m_preDelayBuffer;
    int m_preDelayWriteIndex = 0;
    int m_preDelaySamples = 0;
    
    // High-cut filter
    juce::dsp::IIR::Filter<float> m_highCutFilter;
    juce::dsp::IIR::Coefficients<float>::Ptr m_highCutCoeffs;
    
    // Parameters
    std::atomic<float> m_mix{0.5f};
    std::atomic<float> m_decay{1.0f};
    std::atomic<float> m_preDelayMs{0.0f};
    std::atomic<float> m_highCutHz{20000.0f};
    
    // IR Library
    std::map<juce::String, juce::String> m_irLibrary;  // name -> category
    
    // Visual state
    ScrapbookVisualState m_visualState;
    mutable std::mutex m_visualMutex;
    
    double m_sampleRate = 44100.0;
    bool m_prepared = false;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(SmudgeProcessor)
};

} // namespace iDAW
