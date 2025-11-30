/**
 * PencilProcessor.cpp - Implementation of Plugin 002: "The Pencil"
 * 
 * Profile: 'Graphite' (Tube Saturation / Additive EQ)
 * 
 * Implements parallel multi-band saturation with:
 * - 3 Parallel Bandpass Filters (Low, Mid, High)
 * - TubeDrive per band generating 2nd order harmonics
 * - Parallel dry/wet processing
 * - Ghost Hands AI integration
 */

#include "PencilProcessor.h"
#include <algorithm>

namespace iDAW {

//==============================================================================
// Constructor / Destructor
//==============================================================================

PencilProcessor::PencilProcessor()
    : AudioProcessor(BusesProperties()
                     .withInput("Input", juce::AudioChannelSet::stereo(), true)
                     .withOutput("Output", juce::AudioChannelSet::stereo(), true))
{
    // Initialize band parameters with defaults
    
    // Low band: 80-250 Hz
    m_bandParams[0].frequency = 120.0f;
    m_bandParams[0].q = PencilConfig::LOW_Q;
    m_bandParams[0].drive = 1.5f;
    m_bandParams[0].mix = 0.5f;
    m_bandParams[0].enabled = true;
    
    // Mid band: 250-4000 Hz
    m_bandParams[1].frequency = 1000.0f;
    m_bandParams[1].q = PencilConfig::MID_Q;
    m_bandParams[1].drive = 1.2f;
    m_bandParams[1].mix = 0.5f;
    m_bandParams[1].enabled = true;
    
    // High band: 4000-20000 Hz
    m_bandParams[2].frequency = 8000.0f;
    m_bandParams[2].q = PencilConfig::HIGH_Q;
    m_bandParams[2].drive = 1.0f;
    m_bandParams[2].mix = 0.3f;
    m_bandParams[2].enabled = true;
    
    // Initialize band levels
    for (auto& level : m_bandLevels) {
        level.store(0.0f);
    }
}

PencilProcessor::~PencilProcessor() = default;

//==============================================================================
// AudioProcessor Interface
//==============================================================================

void PencilProcessor::prepareToPlay(double sampleRate, int /*samplesPerBlock*/) {
    m_sampleRate = sampleRate;
    
    // Clear filter states
    for (auto& bandState : m_filterState) {
        for (auto& channelState : bandState) {
            channelState = BiquadState();
        }
    }
    
    // Calculate filter coefficients for each band
    for (int band = 0; band < 3; ++band) {
        calculateBandpassCoeffs(band);
    }
    
    m_prepared = true;
}

void PencilProcessor::releaseResources() {
    m_prepared = false;
}

void PencilProcessor::processBlock(juce::AudioBuffer<float>& buffer,
                                    juce::MidiBuffer& /*midiMessages*/) {
    if (!m_prepared) return;
    
    juce::ScopedNoDenormals noDenormals;
    
    const int numChannels = buffer.getNumChannels();
    const int numSamples = buffer.getNumSamples();
    
    // Process each sample
    for (int channel = 0; channel < std::min(numChannels, 2); ++channel) {
        float* channelData = buffer.getWritePointer(channel);
        
        for (int sample = 0; sample < numSamples; ++sample) {
            channelData[sample] = processSample(channelData[sample], channel);
        }
    }
    
    // Apply output gain
    float outputGain = m_outputGainLinear.load();
    if (std::abs(outputGain - 1.0f) > 0.001f) {
        buffer.applyGain(outputGain);
    }
    
    // Update visual state
    updateVisualState();
}

float PencilProcessor::processSample(float input, int channel) {
    float output = 0.0f;
    float drySignal = input;
    
    // Process each band in parallel
    for (int band = 0; band < 3; ++band) {
        if (!m_bandParams[band].enabled) continue;
        
        // 1. Bandpass filter
        float filtered = applyBandpass(input, band, channel);
        
        // 2. Apply tube drive saturation
        float saturated = applyTubeDrive(filtered, m_bandParams[band].drive);
        
        // 3. Parallel mix (dry + wet)
        float bandOutput = filtered * (1.0f - m_bandParams[band].mix) + 
                          saturated * m_bandParams[band].mix;
        
        // 4. Track level for metering
        float level = std::abs(bandOutput);
        float currentLevel = m_bandLevels[band].load();
        m_bandLevels[band].store(std::max(level, currentLevel * LEVEL_DECAY));
        
        // 5. Sum to output
        output += bandOutput;
    }
    
    // Mix parallel bands with original signal for additive EQ effect
    // Original signal provides foundation, bands add color
    output = drySignal * 0.5f + output * 0.5f;
    
    return output;
}

float PencilProcessor::applyBandpass(float input, int bandIndex, int channel) {
    auto& state = m_filterState[bandIndex][channel];
    auto& coeffs = m_filterCoeffs[bandIndex];
    
    // Direct Form I biquad
    float output = coeffs.b0 * input + 
                   coeffs.b1 * state.x1 + 
                   coeffs.b2 * state.x2 -
                   coeffs.a1 * state.y1 - 
                   coeffs.a2 * state.y2;
    
    // Update state
    state.x2 = state.x1;
    state.x1 = input;
    state.y2 = state.y1;
    state.y1 = output;
    
    return output;
}

float PencilProcessor::applyTubeDrive(float input, float drive) {
    if (drive <= 1.0f) {
        return input;
    }
    
    // Apply tube saturation
    return tubeSaturate(input, drive);
}

float PencilProcessor::tubeSaturate(float x, float drive) {
    // Asymmetric soft clipping to generate 2nd order harmonics
    // Based on triode tube characteristics
    
    // Scale input by drive
    float scaled = x * drive;
    
    // Asymmetric tanh with different curves for positive/negative
    // This generates even harmonics (2nd, 4th, etc.)
    float saturated;
    
    if (scaled >= 0.0f) {
        // Positive half: softer clipping (triode-like)
        saturated = std::tanh(scaled * 0.8f);
    } else {
        // Negative half: slightly harder clipping
        // The asymmetry creates 2nd order harmonics
        saturated = std::tanh(scaled * 1.0f) * 0.95f;
    }
    
    // Add subtle 2nd harmonic explicitly for extra warmth
    float secondHarmonic = scaled * scaled * 0.05f;
    saturated += secondHarmonic * (1.0f - std::abs(saturated));
    
    // Soft knee polynomial for smoother transition
    // Adds subtle compression character
    float polynomial = scaled - (scaled * scaled * scaled) / 3.0f;
    
    // Blend tanh and polynomial based on drive amount
    float blendFactor = std::min((drive - 1.0f) / (PencilConfig::MAX_DRIVE - 1.0f), 1.0f);
    float result = saturated * blendFactor + polynomial * (1.0f - blendFactor);
    
    // Output gain compensation (drive reduces level)
    float compensation = 1.0f / std::sqrt(drive);
    
    return result * compensation;
}

void PencilProcessor::calculateBandpassCoeffs(int bandIndex) {
    const float freq = m_bandParams[bandIndex].frequency;
    const float q = m_bandParams[bandIndex].q;
    
    // Bandpass filter coefficient calculation (RBJ Audio EQ Cookbook)
    const float w0 = 2.0f * juce::MathConstants<float>::pi * freq / static_cast<float>(m_sampleRate);
    const float cosW0 = std::cos(w0);
    const float sinW0 = std::sin(w0);
    const float alpha = sinW0 / (2.0f * q);
    
    // Bandpass (constant skirt gain, peak gain = Q)
    const float b0 = alpha;
    const float b1 = 0.0f;
    const float b2 = -alpha;
    const float a0 = 1.0f + alpha;
    const float a1 = -2.0f * cosW0;
    const float a2 = 1.0f - alpha;
    
    // Normalize coefficients
    m_filterCoeffs[bandIndex].b0 = b0 / a0;
    m_filterCoeffs[bandIndex].b1 = b1 / a0;
    m_filterCoeffs[bandIndex].b2 = b2 / a0;
    m_filterCoeffs[bandIndex].a1 = a1 / a0;
    m_filterCoeffs[bandIndex].a2 = a2 / a0;
}

//==============================================================================
// Band Parameters
//==============================================================================

void PencilProcessor::setBandParameters(int bandIndex, const BandParameters& params) {
    if (bandIndex < 0 || bandIndex >= 3) return;
    
    m_bandParams[bandIndex] = params;
    
    if (m_prepared) {
        calculateBandpassCoeffs(bandIndex);
    }
}

BandParameters PencilProcessor::getBandParameters(int bandIndex) const {
    if (bandIndex < 0 || bandIndex >= 3) return BandParameters();
    return m_bandParams[bandIndex];
}

void PencilProcessor::setBandDrive(int bandIndex, float drive) {
    if (bandIndex < 0 || bandIndex >= 3) return;
    m_bandParams[bandIndex].drive = std::clamp(drive, 1.0f, PencilConfig::MAX_DRIVE);
}

float PencilProcessor::getBandDrive(int bandIndex) const {
    if (bandIndex < 0 || bandIndex >= 3) return 1.0f;
    return m_bandParams[bandIndex].drive;
}

void PencilProcessor::setBandMix(int bandIndex, float mix) {
    if (bandIndex < 0 || bandIndex >= 3) return;
    m_bandParams[bandIndex].mix = std::clamp(mix, 0.0f, 1.0f);
}

void PencilProcessor::setOutputGain(float gainDb) {
    m_outputGainDb.store(gainDb);
    m_outputGainLinear.store(std::pow(10.0f, gainDb / 20.0f));
}

//==============================================================================
// Ghost Hands Integration
//==============================================================================

void PencilProcessor::applyWarmthFromAI(float warmthAmount) {
    // Warmth = boost Low-Mids and increase Drive
    warmthAmount = std::clamp(warmthAmount, 0.0f, 1.0f);
    
    // Low band: moderate drive increase
    m_bandParams[0].drive = 1.0f + warmthAmount * 3.0f;  // 1.0 to 4.0
    m_bandParams[0].mix = 0.3f + warmthAmount * 0.4f;    // 0.3 to 0.7
    
    // Mid band: strongest boost for warmth (low-mids)
    m_bandParams[1].drive = 1.0f + warmthAmount * 4.0f;  // 1.0 to 5.0
    m_bandParams[1].mix = 0.4f + warmthAmount * 0.4f;    // 0.4 to 0.8
    m_bandParams[1].frequency = 800.0f - warmthAmount * 400.0f;  // Focus on low-mids (800 -> 400 Hz)
    
    // High band: reduce for warmth
    m_bandParams[2].drive = 1.0f + warmthAmount * 0.5f;  // 1.0 to 1.5 (subtle)
    m_bandParams[2].mix = 0.3f - warmthAmount * 0.2f;    // 0.3 to 0.1
    
    // Recalculate mid band filter for new frequency
    if (m_prepared) {
        calculateBandpassCoeffs(1);
    }
}

void PencilProcessor::setParametersFromAI(float lowDrive, float midDrive, float highDrive) {
    // Map 0-1 normalized values to actual drive range
    m_bandParams[0].drive = 1.0f + lowDrive * (PencilConfig::MAX_DRIVE - 1.0f);
    m_bandParams[1].drive = 1.0f + midDrive * (PencilConfig::MAX_DRIVE - 1.0f);
    m_bandParams[2].drive = 1.0f + highDrive * (PencilConfig::MAX_DRIVE - 1.0f);
}

//==============================================================================
// Visual Feedback
//==============================================================================

void PencilProcessor::updateVisualState() {
    std::lock_guard<std::mutex> lock(m_visualStateMutex);
    
    // Calculate overall drive (weighted average)
    float overallDrive = (m_bandParams[0].drive * 0.3f +
                          m_bandParams[1].drive * 0.5f +
                          m_bandParams[2].drive * 0.2f);
    
    m_visualState.overallDrive = overallDrive;
    
    // Map drive to visual parameters
    // Higher drive = thicker, grainier lines
    float normalizedDrive = (overallDrive - 1.0f) / (PencilConfig::MAX_DRIVE - 1.0f);
    
    // LineThickness: 1.0 (clean) to 4.0 (heavy charcoal)
    m_visualState.lineThickness = 1.0f + normalizedDrive * 3.0f;
    
    // LineNoise: 0.0 (clean) to 1.0 (maximum grain)
    m_visualState.lineNoise = normalizedDrive;
    
    // Per-band levels
    for (int i = 0; i < 3; ++i) {
        m_visualState.bandLevels[i] = m_bandLevels[i].load();
    }
}

GraphiteVisualState PencilProcessor::getVisualState() const {
    std::lock_guard<std::mutex> lock(m_visualStateMutex);
    return m_visualState;
}

std::array<float, 3> PencilProcessor::getBandLevels() const {
    return {
        m_bandLevels[0].load(),
        m_bandLevels[1].load(),
        m_bandLevels[2].load()
    };
}

//==============================================================================
// State Save/Load
//==============================================================================

void PencilProcessor::getStateInformation(juce::MemoryBlock& destData) {
    // Save band parameters
    for (int i = 0; i < 3; ++i) {
        destData.append(&m_bandParams[i].frequency, sizeof(float));
        destData.append(&m_bandParams[i].q, sizeof(float));
        destData.append(&m_bandParams[i].drive, sizeof(float));
        destData.append(&m_bandParams[i].mix, sizeof(float));
    }
    
    // Save output gain
    float outputGain = m_outputGainDb.load();
    destData.append(&outputGain, sizeof(float));
}

void PencilProcessor::setStateInformation(const void* data, int sizeInBytes) {
    const int expectedSize = 3 * 4 * sizeof(float) + sizeof(float);  // 3 bands * 4 params + output gain
    
    if (sizeInBytes >= expectedSize) {
        const float* floatData = static_cast<const float*>(data);
        int idx = 0;
        
        for (int i = 0; i < 3; ++i) {
            m_bandParams[i].frequency = floatData[idx++];
            m_bandParams[i].q = floatData[idx++];
            m_bandParams[i].drive = floatData[idx++];
            m_bandParams[i].mix = floatData[idx++];
            
            if (m_prepared) {
                calculateBandpassCoeffs(i);
            }
        }
        
        setOutputGain(floatData[idx]);
    }
}

//==============================================================================
// Editor
//==============================================================================

juce::AudioProcessorEditor* PencilProcessor::createEditor() {
    return new juce::GenericAudioProcessorEditor(*this);
}

} // namespace iDAW

//==============================================================================
// Plugin Entry Point
//==============================================================================

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter() {
    return new iDAW::PencilProcessor();
}
