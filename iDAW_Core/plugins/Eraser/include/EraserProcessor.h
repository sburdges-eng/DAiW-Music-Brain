/**
 * EraserProcessor.h - Plugin 001: "The Eraser"
 * 
 * Profile: 'Digital Surgeon' (Transparent, Linear Phase)
 * 
 * A spectral gating processor that allows surgical removal of frequency content.
 * Uses FFT-based processing with linear phase response for transparent operation.
 * 
 * Features:
 * - 2048-sample FFT window for high frequency resolution
 * - Spectral gating with AI-controlled threshold
 * - "Chalk Dust" particle visualization of erased frequencies
 * - Cursor-based frequency bin selection ("Eraser scrubbing")
 * - Safe look-ahead buffer management
 */

#pragma once

#include <JuceHeader.h>
#include <array>
#include <atomic>
#include <vector>
#include <complex>
#include <memory>

namespace iDAW {

/**
 * Configuration for the Eraser processor
 */
struct EraserConfig {
    static constexpr int FFT_ORDER = 11;                    // 2^11 = 2048 samples
    static constexpr int FFT_SIZE = 1 << FFT_ORDER;         // 2048 samples
    static constexpr int HOP_SIZE = FFT_SIZE / 4;           // 75% overlap (512 samples)
    static constexpr int NUM_BINS = FFT_SIZE / 2 + 1;       // 1025 frequency bins
    static constexpr float WINDOW_CORRECTION = 1.5f;        // Hann window correction factor
};

/**
 * Spectral bin state for visualization
 */
struct SpectralBinState {
    float magnitude;      // Current magnitude (0-1 normalized)
    float phase;          // Current phase
    bool erased;          // Whether this bin is being erased
    float eraserIntensity; // Intensity of erasure (for animation)
};

/**
 * Chalk Dust Particle for visualization
 */
struct ChalkDustParticle {
    float x, y;           // Position
    float vx, vy;         // Velocity
    float life;           // Remaining lifetime (0-1)
    float size;           // Particle size
    float brightness;     // Brightness (based on erased magnitude)
    int binIndex;         // Source frequency bin
};

/**
 * EraserProcessor - Linear Phase Spectral Gating Processor
 * 
 * Algorithm:
 * 1. Window input samples with Hann window
 * 2. FFT to frequency domain
 * 3. For each bin: if magnitude > threshold, multiply by 0 (silence)
 * 4. IFFT back to time domain
 * 5. Overlap-add with previous frames
 * 
 * The processor maintains a look-ahead buffer for linear phase operation.
 */
class EraserProcessor : public juce::AudioProcessor {
public:
    //==========================================================================
    // Constructor / Destructor
    //==========================================================================
    
    EraserProcessor();
    ~EraserProcessor() override;
    
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
    const juce::String getName() const override { return "The Eraser"; }
    bool acceptsMidi() const override { return false; }
    bool producesMidi() const override { return false; }
    double getTailLengthSeconds() const override;
    
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
    // Eraser-Specific Interface
    //==========================================================================
    
    /**
     * Set the global threshold for spectral gating.
     * @param thresholdDb Threshold in dB (typically -60 to 0)
     */
    void setThreshold(float thresholdDb);
    float getThreshold() const { return m_thresholdDb.load(); }
    
    /**
     * Set threshold from AI (Python callback)
     * @param normalizedValue 0-1 normalized threshold
     */
    void setThresholdFromAI(float normalizedValue);
    
    /**
     * Set eraser cursor position (for manual frequency scrubbing)
     * @param frequencyHz Center frequency of eraser
     * @param bandwidthHz Width of eraser in Hz
     * @param intensity Erasure intensity (0-1)
     */
    void setEraserCursor(float frequencyHz, float bandwidthHz, float intensity);
    
    /**
     * Clear the eraser cursor (stop manual erasing)
     */
    void clearEraserCursor();
    
    /**
     * Get spectral data for visualization
     * Thread-safe copy of current FFT magnitudes
     */
    std::vector<SpectralBinState> getSpectralState() const;
    
    /**
     * Get active chalk dust particles for visualization
     */
    std::vector<ChalkDustParticle> getChalkDustParticles() const;
    
    /**
     * Set frequency bins to erase (from UI scrubbing)
     * @param binIndices Vector of bin indices to silence
     */
    void setErasedBins(const std::vector<int>& binIndices);
    
    /**
     * Clear all erased bins
     */
    void clearErasedBins();
    
    /**
     * Called when playback stops - clears look-ahead buffer
     */
    void playbackStopped();
    
private:
    //==========================================================================
    // DSP Processing
    //==========================================================================
    
    /**
     * Process a single channel through the spectral gate
     */
    void processChannel(int channel, float* samples, int numSamples);
    
    /**
     * Apply Hann window to samples
     */
    void applyWindow(float* samples, int numSamples);
    
    /**
     * Perform spectral gating on frequency domain data
     */
    void performSpectralGating(std::complex<float>* fftData);
    
    /**
     * Convert bin index to frequency
     */
    float binToFrequency(int binIndex) const;
    
    /**
     * Convert frequency to bin index
     */
    int frequencyToBin(float frequencyHz) const;
    
    /**
     * Generate chalk dust particles from erased bins
     */
    void generateChalkDust(int binIndex, float magnitude);
    
    /**
     * Update particle physics
     */
    void updateParticles(float deltaTime);
    
    /**
     * Clear all processing buffers (for look-ahead safety)
     */
    void clearBuffers();
    
    //==========================================================================
    // FFT
    //==========================================================================
    
    std::unique_ptr<juce::dsp::FFT> m_fft;
    std::unique_ptr<juce::dsp::WindowingFunction<float>> m_window;
    
    //==========================================================================
    // Processing Buffers
    //==========================================================================
    
    // Input FIFO for overlap-add
    std::array<std::vector<float>, 2> m_inputFIFO;     // Per channel
    std::array<int, 2> m_inputFIFOIndex;
    
    // Output FIFO for overlap-add
    std::array<std::vector<float>, 2> m_outputFIFO;    // Per channel
    std::array<int, 2> m_outputFIFOIndex;
    
    // FFT working buffers
    std::vector<float> m_fftBuffer;
    std::vector<std::complex<float>> m_frequencyData;
    
    // Look-ahead buffer for linear phase
    std::array<std::vector<float>, 2> m_lookAheadBuffer;
    std::array<int, 2> m_lookAheadIndex;
    
    //==========================================================================
    // Parameters
    //==========================================================================
    
    std::atomic<float> m_thresholdDb{-40.0f};
    std::atomic<float> m_thresholdLinear{0.01f};  // Pre-computed linear threshold
    
    // Eraser cursor state
    std::atomic<bool> m_eraserActive{false};
    std::atomic<float> m_eraserCenterHz{1000.0f};
    std::atomic<float> m_eraserBandwidthHz{200.0f};
    std::atomic<float> m_eraserIntensity{1.0f};
    
    // Manual bin erasure
    std::vector<bool> m_erasedBins;
    mutable std::mutex m_erasedBinsMutex;
    
    //==========================================================================
    // Visualization State
    //==========================================================================
    
    std::vector<SpectralBinState> m_spectralState;
    mutable std::mutex m_spectralStateMutex;
    
    std::vector<ChalkDustParticle> m_particles;
    mutable std::mutex m_particlesMutex;
    static constexpr int MAX_PARTICLES = 500;
    
    //==========================================================================
    // State
    //==========================================================================
    
    double m_sampleRate = 44100.0;
    int m_samplesPerBlock = 512;
    bool m_prepared = false;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(EraserProcessor)
};

} // namespace iDAW
