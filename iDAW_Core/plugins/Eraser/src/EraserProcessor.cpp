/**
 * EraserProcessor.cpp - Implementation of Plugin 001: "The Eraser"
 * 
 * Profile: 'Digital Surgeon' (Transparent, Linear Phase)
 * 
 * Implements spectral gating with:
 * - 2048-sample FFT with 75% overlap
 * - Hann windowing for smooth transitions
 * - Linear phase processing via look-ahead buffer
 * - AI-controlled threshold
 * - Visual feedback via "Chalk Dust" particles
 */

#include "EraserProcessor.h"
#include <cmath>
#include <algorithm>
#include <random>

namespace iDAW {

//==============================================================================
// Constructor / Destructor
//==============================================================================

EraserProcessor::EraserProcessor()
    : AudioProcessor(BusesProperties()
                     .withInput("Input", juce::AudioChannelSet::stereo(), true)
                     .withOutput("Output", juce::AudioChannelSet::stereo(), true))
{
    // Initialize FFT
    m_fft = std::make_unique<juce::dsp::FFT>(EraserConfig::FFT_ORDER);
    
    // Initialize Hann window
    m_window = std::make_unique<juce::dsp::WindowingFunction<float>>(
        EraserConfig::FFT_SIZE,
        juce::dsp::WindowingFunction<float>::hann
    );
    
    // Allocate buffers
    m_fftBuffer.resize(EraserConfig::FFT_SIZE * 2);  // Real + Imaginary interleaved
    m_frequencyData.resize(EraserConfig::NUM_BINS);
    m_spectralState.resize(EraserConfig::NUM_BINS);
    m_erasedBins.resize(EraserConfig::NUM_BINS, false);
    
    // Reserve particle storage
    m_particles.reserve(MAX_PARTICLES);
}

EraserProcessor::~EraserProcessor() = default;

//==============================================================================
// AudioProcessor Interface
//==============================================================================

void EraserProcessor::prepareToPlay(double sampleRate, int samplesPerBlock) {
    m_sampleRate = sampleRate;
    m_samplesPerBlock = samplesPerBlock;
    
    // Initialize per-channel buffers
    for (int ch = 0; ch < 2; ++ch) {
        m_inputFIFO[ch].resize(EraserConfig::FFT_SIZE, 0.0f);
        m_inputFIFOIndex[ch] = 0;
        
        m_outputFIFO[ch].resize(EraserConfig::FFT_SIZE, 0.0f);
        m_outputFIFOIndex[ch] = 0;
        
        // Look-ahead buffer = half FFT size for linear phase
        m_lookAheadBuffer[ch].resize(EraserConfig::FFT_SIZE / 2, 0.0f);
        m_lookAheadIndex[ch] = 0;
    }
    
    // Clear FFT buffer
    std::fill(m_fftBuffer.begin(), m_fftBuffer.end(), 0.0f);
    
    // Reset spectral state
    for (auto& state : m_spectralState) {
        state.magnitude = 0.0f;
        state.phase = 0.0f;
        state.erased = false;
        state.eraserIntensity = 0.0f;
    }
    
    m_prepared = true;
}

void EraserProcessor::releaseResources() {
    clearBuffers();
    m_prepared = false;
}

void EraserProcessor::processBlock(juce::AudioBuffer<float>& buffer,
                                    juce::MidiBuffer& /*midiMessages*/) {
    if (!m_prepared) return;
    
    juce::ScopedNoDenormals noDenormals;
    
    const int numChannels = buffer.getNumChannels();
    const int numSamples = buffer.getNumSamples();
    
    // Process each channel
    for (int channel = 0; channel < std::min(numChannels, 2); ++channel) {
        float* channelData = buffer.getWritePointer(channel);
        processChannel(channel, channelData, numSamples);
    }
    
    // Update particles
    updateParticles(static_cast<float>(numSamples) / static_cast<float>(m_sampleRate));
}

void EraserProcessor::processChannel(int channel, float* samples, int numSamples) {
    auto& inputFIFO = m_inputFIFO[channel];
    auto& outputFIFO = m_outputFIFO[channel];
    auto& lookAhead = m_lookAheadBuffer[channel];
    int& inputIndex = m_inputFIFOIndex[channel];
    int& outputIndex = m_outputFIFOIndex[channel];
    int& lookAheadIdx = m_lookAheadIndex[channel];
    
    for (int i = 0; i < numSamples; ++i) {
        // Store input sample in FIFO
        inputFIFO[inputIndex] = samples[i];
        
        // Output from look-ahead buffer (introduces latency for linear phase)
        float outputSample = lookAhead[lookAheadIdx];
        
        // Store processed output in look-ahead buffer
        lookAhead[lookAheadIdx] = outputFIFO[outputIndex];
        
        // Clear the output FIFO position we just read
        outputFIFO[outputIndex] = 0.0f;
        
        // Output the delayed sample
        samples[i] = outputSample;
        
        // Advance indices
        inputIndex = (inputIndex + 1) % EraserConfig::FFT_SIZE;
        outputIndex = (outputIndex + 1) % EraserConfig::FFT_SIZE;
        lookAheadIdx = (lookAheadIdx + 1) % (EraserConfig::FFT_SIZE / 2);
        
        // Check if we have enough samples for FFT
        if (inputIndex % EraserConfig::HOP_SIZE == 0) {
            // Copy input FIFO to FFT buffer (with proper ordering)
            for (int j = 0; j < EraserConfig::FFT_SIZE; ++j) {
                int idx = (inputIndex + j) % EraserConfig::FFT_SIZE;
                m_fftBuffer[j] = inputFIFO[idx];
            }
            
            // Apply window
            applyWindow(m_fftBuffer.data(), EraserConfig::FFT_SIZE);
            
            // Perform FFT (in-place, real-to-complex)
            m_fft->performRealOnlyForwardTransform(m_fftBuffer.data());
            
            // Convert to complex for processing
            for (int bin = 0; bin < EraserConfig::NUM_BINS; ++bin) {
                float real = m_fftBuffer[bin * 2];
                float imag = m_fftBuffer[bin * 2 + 1];
                m_frequencyData[bin] = std::complex<float>(real, imag);
            }
            
            // Perform spectral gating
            performSpectralGating(m_frequencyData.data());
            
            // Convert back for IFFT
            for (int bin = 0; bin < EraserConfig::NUM_BINS; ++bin) {
                m_fftBuffer[bin * 2] = m_frequencyData[bin].real();
                m_fftBuffer[bin * 2 + 1] = m_frequencyData[bin].imag();
            }
            
            // Perform IFFT
            m_fft->performRealOnlyInverseTransform(m_fftBuffer.data());
            
            // Apply window again for overlap-add
            applyWindow(m_fftBuffer.data(), EraserConfig::FFT_SIZE);
            
            // Add to output FIFO (overlap-add)
            for (int j = 0; j < EraserConfig::FFT_SIZE; ++j) {
                int idx = (outputIndex + j) % EraserConfig::FFT_SIZE;
                outputFIFO[idx] += m_fftBuffer[j] * EraserConfig::WINDOW_CORRECTION / 
                                   static_cast<float>(EraserConfig::FFT_SIZE);
            }
        }
    }
}

void EraserProcessor::applyWindow(float* samples, int numSamples) {
    m_window->multiplyWithWindowingTable(samples, numSamples);
}

void EraserProcessor::performSpectralGating(std::complex<float>* fftData) {
    const float threshold = m_thresholdLinear.load();
    const bool eraserActive = m_eraserActive.load();
    const float eraserCenterHz = m_eraserCenterHz.load();
    const float eraserBandwidthHz = m_eraserBandwidthHz.load();
    const float eraserIntensity = m_eraserIntensity.load();
    
    // Calculate eraser bin range
    int eraserCenterBin = frequencyToBin(eraserCenterHz);
    int eraserWidthBins = frequencyToBin(eraserBandwidthHz) - frequencyToBin(0.0f);
    int eraserMinBin = std::max(0, eraserCenterBin - eraserWidthBins / 2);
    int eraserMaxBin = std::min(EraserConfig::NUM_BINS - 1, eraserCenterBin + eraserWidthBins / 2);
    
    // Lock for spectral state update
    std::lock_guard<std::mutex> stateLock(m_spectralStateMutex);
    
    // Lock for erased bins check
    std::lock_guard<std::mutex> binsLock(m_erasedBinsMutex);
    
    for (int bin = 0; bin < EraserConfig::NUM_BINS; ++bin) {
        float magnitude = std::abs(fftData[bin]);
        float phase = std::arg(fftData[bin]);
        
        // Normalize magnitude for visualization
        float normalizedMag = std::min(magnitude / 100.0f, 1.0f);
        
        // Update spectral state
        m_spectralState[bin].magnitude = normalizedMag;
        m_spectralState[bin].phase = phase;
        
        bool shouldErase = false;
        float eraseAmount = 0.0f;
        
        // Check threshold gating
        if (magnitude > threshold) {
            shouldErase = true;
            eraseAmount = 1.0f;
        }
        
        // Check manual bin erasure
        if (m_erasedBins[bin]) {
            shouldErase = true;
            eraseAmount = 1.0f;
        }
        
        // Check eraser cursor
        if (eraserActive && bin >= eraserMinBin && bin <= eraserMaxBin) {
            // Smooth falloff at edges
            float distFromCenter = std::abs(bin - eraserCenterBin) / 
                                   static_cast<float>(eraserWidthBins / 2 + 1);
            float cursorAmount = (1.0f - distFromCenter) * eraserIntensity;
            
            if (cursorAmount > eraseAmount) {
                shouldErase = true;
                eraseAmount = cursorAmount;
            }
        }
        
        // Apply erasure
        if (shouldErase && eraseAmount > 0.0f) {
            // Generate chalk dust particles for visual feedback
            if (magnitude > 0.01f) {
                generateChalkDust(bin, magnitude * eraseAmount);
            }
            
            // Erase the frequency content (multiply by complement of erase amount)
            fftData[bin] *= (1.0f - eraseAmount);
            
            m_spectralState[bin].erased = true;
            m_spectralState[bin].eraserIntensity = eraseAmount;
        } else {
            m_spectralState[bin].erased = false;
            m_spectralState[bin].eraserIntensity = 0.0f;
        }
    }
}

float EraserProcessor::binToFrequency(int binIndex) const {
    return static_cast<float>(binIndex) * static_cast<float>(m_sampleRate) / 
           static_cast<float>(EraserConfig::FFT_SIZE);
}

int EraserProcessor::frequencyToBin(float frequencyHz) const {
    return static_cast<int>(frequencyHz * static_cast<float>(EraserConfig::FFT_SIZE) / 
                            static_cast<float>(m_sampleRate));
}

//==============================================================================
// Eraser Control Interface
//==============================================================================

void EraserProcessor::setThreshold(float thresholdDb) {
    m_thresholdDb.store(thresholdDb);
    // Convert dB to linear
    m_thresholdLinear.store(std::pow(10.0f, thresholdDb / 20.0f));
}

void EraserProcessor::setThresholdFromAI(float normalizedValue) {
    // Map 0-1 to -60dB to 0dB
    float thresholdDb = -60.0f + normalizedValue * 60.0f;
    setThreshold(thresholdDb);
}

void EraserProcessor::setEraserCursor(float frequencyHz, float bandwidthHz, float intensity) {
    m_eraserCenterHz.store(frequencyHz);
    m_eraserBandwidthHz.store(bandwidthHz);
    m_eraserIntensity.store(intensity);
    m_eraserActive.store(true);
}

void EraserProcessor::clearEraserCursor() {
    m_eraserActive.store(false);
}

void EraserProcessor::setErasedBins(const std::vector<int>& binIndices) {
    std::lock_guard<std::mutex> lock(m_erasedBinsMutex);
    
    // Clear previous
    std::fill(m_erasedBins.begin(), m_erasedBins.end(), false);
    
    // Set new
    for (int bin : binIndices) {
        if (bin >= 0 && bin < EraserConfig::NUM_BINS) {
            m_erasedBins[bin] = true;
        }
    }
}

void EraserProcessor::clearErasedBins() {
    std::lock_guard<std::mutex> lock(m_erasedBinsMutex);
    std::fill(m_erasedBins.begin(), m_erasedBins.end(), false);
}

std::vector<SpectralBinState> EraserProcessor::getSpectralState() const {
    std::lock_guard<std::mutex> lock(m_spectralStateMutex);
    return m_spectralState;
}

//==============================================================================
// Chalk Dust Particle System
//==============================================================================

void EraserProcessor::generateChalkDust(int binIndex, float magnitude) {
    std::lock_guard<std::mutex> lock(m_particlesMutex);
    
    if (m_particles.size() >= MAX_PARTICLES) {
        // Remove oldest particle
        m_particles.erase(m_particles.begin());
    }
    
    // Random number generator
    static std::random_device rd;
    static std::mt19937 gen(rd());
    static std::uniform_real_distribution<float> dist(-1.0f, 1.0f);
    
    // Create particle at frequency position
    float freq = binToFrequency(binIndex);
    float normalizedX = static_cast<float>(binIndex) / static_cast<float>(EraserConfig::NUM_BINS);
    
    ChalkDustParticle particle;
    particle.x = normalizedX;
    particle.y = 0.5f + dist(gen) * 0.1f;  // Center with some randomness
    particle.vx = dist(gen) * 0.1f;
    particle.vy = -0.2f + dist(gen) * 0.1f;  // Drift upward
    particle.life = 1.0f;
    particle.size = 2.0f + magnitude * 5.0f;
    particle.brightness = std::min(magnitude * 2.0f, 1.0f);
    particle.binIndex = binIndex;
    
    m_particles.push_back(particle);
}

void EraserProcessor::updateParticles(float deltaTime) {
    std::lock_guard<std::mutex> lock(m_particlesMutex);
    
    // Update and remove dead particles
    m_particles.erase(
        std::remove_if(m_particles.begin(), m_particles.end(),
            [deltaTime](ChalkDustParticle& p) {
                // Update physics
                p.x += p.vx * deltaTime;
                p.y += p.vy * deltaTime;
                
                // Add gravity
                p.vy += 0.5f * deltaTime;
                
                // Decay
                p.life -= deltaTime * 0.5f;
                p.brightness *= 0.98f;
                
                // Remove if dead
                return p.life <= 0.0f;
            }
        ),
        m_particles.end()
    );
}

std::vector<ChalkDustParticle> EraserProcessor::getChalkDustParticles() const {
    std::lock_guard<std::mutex> lock(m_particlesMutex);
    return m_particles;
}

//==============================================================================
// Safety: Look-Ahead Buffer Management
//==============================================================================

void EraserProcessor::playbackStopped() {
    clearBuffers();
}

void EraserProcessor::clearBuffers() {
    // Clear all FIFOs and look-ahead buffers
    for (int ch = 0; ch < 2; ++ch) {
        std::fill(m_inputFIFO[ch].begin(), m_inputFIFO[ch].end(), 0.0f);
        std::fill(m_outputFIFO[ch].begin(), m_outputFIFO[ch].end(), 0.0f);
        std::fill(m_lookAheadBuffer[ch].begin(), m_lookAheadBuffer[ch].end(), 0.0f);
        
        m_inputFIFOIndex[ch] = 0;
        m_outputFIFOIndex[ch] = 0;
        m_lookAheadIndex[ch] = 0;
    }
    
    // Clear FFT buffer
    std::fill(m_fftBuffer.begin(), m_fftBuffer.end(), 0.0f);
    
    // Clear particles
    {
        std::lock_guard<std::mutex> lock(m_particlesMutex);
        m_particles.clear();
    }
}

double EraserProcessor::getTailLengthSeconds() const {
    // Look-ahead latency
    return static_cast<double>(EraserConfig::FFT_SIZE) / m_sampleRate;
}

//==============================================================================
// State Save/Load
//==============================================================================

void EraserProcessor::getStateInformation(juce::MemoryBlock& destData) {
    // Save threshold
    float threshold = m_thresholdDb.load();
    destData.append(&threshold, sizeof(float));
}

void EraserProcessor::setStateInformation(const void* data, int sizeInBytes) {
    if (sizeInBytes >= static_cast<int>(sizeof(float))) {
        float threshold;
        std::memcpy(&threshold, data, sizeof(float));
        setThreshold(threshold);
    }
}

//==============================================================================
// Editor
//==============================================================================

juce::AudioProcessorEditor* EraserProcessor::createEditor() {
    // Return generic editor for now - custom editor would be in separate file
    return new juce::GenericAudioProcessorEditor(*this);
}

} // namespace iDAW

//==============================================================================
// Plugin Entry Point
//==============================================================================

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter() {
    return new iDAW::EraserProcessor();
}
