/**
 * PressProcessor.cpp - Implementation of Plugin 003: "The Press"
 * 
 * Profile: 'VCA Workhorse' (Clean, RMS Detection, Feed-Forward)
 * 
 * Implements a clean VCA-style digital compressor with:
 * - RMS level detection for musical response
 * - Feed-forward topology
 * - Soft knee compression
 * - Accurate gain reduction metering
 */

#include "PressProcessor.h"
#include <algorithm>

// x86 SIMD intrinsics for denormal protection
#if defined(__SSE__) || defined(_M_X64) || defined(_M_IX86)
#include <xmmintrin.h>
#endif

namespace iDAW {

//==============================================================================
// Constructor / Destructor
//==============================================================================

PressProcessor::PressProcessor()
    : AudioProcessor(BusesProperties()
                     .withInput("Input", juce::AudioChannelSet::stereo(), true)
                     .withOutput("Output", juce::AudioChannelSet::stereo(), true))
{
    // Default parameters (neutral compression)
    m_params.thresholdDb = -20.0f;
    m_params.ratio = 4.0f;
    m_params.attackMs = 10.0f;
    m_params.releaseMs = 100.0f;
    m_params.makeupGainDb = 0.0f;
    m_params.autoMakeup = false;
}

PressProcessor::~PressProcessor() = default;

//==============================================================================
// AudioProcessor Interface
//==============================================================================

void PressProcessor::prepareToPlay(double sampleRate, int /*samplesPerBlock*/) {
    m_sampleRate = sampleRate;
    
    // Calculate RMS window size
    m_rmsWindowSamples = static_cast<int>(PressConfig::RMS_WINDOW_MS * sampleRate / 1000.0);
    m_rmsWindowSamples = std::max(m_rmsWindowSamples, 1);
    
    // Initialize RMS buffer
    m_rmsBuffer.resize(m_rmsWindowSamples, 0.0f);
    m_rmsBufferIndex = 0;
    m_rmsSum = 0.0f;
    
    // Initialize envelope
    m_envelopeState = 1.0f;
    
    // Calculate envelope coefficients
    updateEnvelopeCoeffs();
    
    // Reset meters
    m_gainReductionDb.store(0.0f);
    m_inputLevelDb.store(-100.0f);
    m_outputLevelDb.store(-100.0f);
    m_inputPeak = 0.0f;
    m_outputPeak = 0.0f;
    
    m_prepared = true;
}

void PressProcessor::releaseResources() {
    m_rmsBuffer.clear();
    m_prepared = false;
}

void PressProcessor::processBlock(juce::AudioBuffer<float>& buffer,
                                   juce::MidiBuffer& /*midiMessages*/) {
    if (!m_prepared) return;
    
    // ==========================================================================
    // SAFETY: Disable Denormals for this thread (prevents CPU spikes)
    // ==========================================================================
    juce::ScopedNoDenormals noDenormals;
    
    // Additional x86 denormal protection (belt and suspenders)
    #if defined(__SSE__) || defined(_M_X64) || defined(_M_IX86)
    unsigned int mxcsr = _mm_getcsr();
    _mm_setcsr(mxcsr | 0x8040);  // DAZ and FTZ bits
    #endif
    
    // ==========================================================================
    // SAFETY: Enforce minimum release time to prevent aliasing/distortion
    // ==========================================================================
    const float safeReleaseMs = std::max(m_params.releaseMs, 10.0f);
    if (safeReleaseMs != m_params.releaseMs) {
        m_params.releaseMs = safeReleaseMs;
        updateEnvelopeCoeffs();
    }
    
    const int numChannels = buffer.getNumChannels();
    const int numSamples = buffer.getNumSamples();
    
    // Get makeup gain (auto or manual)
    float makeupGain = m_params.autoMakeup ? 
                       dbToLinear(calculateAutoMakeup()) : 
                       dbToLinear(m_params.makeupGainDb);
    
    // Track peak levels for metering
    float blockInputPeak = 0.0f;
    float blockOutputPeak = 0.0f;
    float blockGainReduction = 0.0f;
    
    // Process sample by sample for accurate envelope following
    for (int sample = 0; sample < numSamples; ++sample) {
        // Calculate input level (sum of squares across channels)
        float sumSquares = 0.0f;
        for (int channel = 0; channel < numChannels; ++channel) {
            float inputSample = buffer.getSample(channel, sample);
            sumSquares += inputSample * inputSample;
            blockInputPeak = std::max(blockInputPeak, std::abs(inputSample));
        }
        
        // Update RMS buffer (running sum for efficiency)
        m_rmsSum -= m_rmsBuffer[m_rmsBufferIndex];
        m_rmsBuffer[m_rmsBufferIndex] = sumSquares / numChannels;
        m_rmsSum += m_rmsBuffer[m_rmsBufferIndex];
        m_rmsBufferIndex = (m_rmsBufferIndex + 1) % m_rmsWindowSamples;
        
        // Calculate RMS level
        float rmsLevel = std::sqrt(m_rmsSum / m_rmsWindowSamples);
        float inputDb = linearToDb(rmsLevel);
        
        // Calculate target gain reduction
        float targetGainDb = calculateGainReduction(inputDb);
        float targetGainLinear = dbToLinear(targetGainDb);
        
        // Apply envelope (attack/release)
        m_envelopeState = applyEnvelope(targetGainLinear, m_envelopeState);
        
        // Calculate actual gain reduction in dB
        float actualGainReductionDb = -linearToDb(m_envelopeState);
        blockGainReduction = std::max(blockGainReduction, actualGainReductionDb);
        
        // Apply gain reduction and makeup gain to all channels
        float totalGain = m_envelopeState * makeupGain;
        
        for (int channel = 0; channel < numChannels; ++channel) {
            float* channelData = buffer.getWritePointer(channel);
            channelData[sample] *= totalGain;
            blockOutputPeak = std::max(blockOutputPeak, std::abs(channelData[sample]));
        }
    }
    
    // Update meters with decay
    m_inputPeak = std::max(blockInputPeak, m_inputPeak * METER_DECAY);
    m_outputPeak = std::max(blockOutputPeak, m_outputPeak * METER_DECAY);
    
    m_inputLevelDb.store(linearToDb(m_inputPeak));
    m_outputLevelDb.store(linearToDb(m_outputPeak));
    m_gainReductionDb.store(blockGainReduction);
}

float PressProcessor::calculateRMS(const float* samples, int numSamples) {
    float sum = 0.0f;
    for (int i = 0; i < numSamples; ++i) {
        sum += samples[i] * samples[i];
    }
    return std::sqrt(sum / numSamples);
}

float PressProcessor::calculateGainReduction(float inputDb) {
    const float threshold = m_params.thresholdDb;
    const float ratio = m_params.ratio;
    const float kneeWidth = PressConfig::KNEE_WIDTH_DB;
    
    // Below threshold: no compression
    if (inputDb < threshold - kneeWidth / 2.0f) {
        return 0.0f;  // 0 dB gain reduction
    }
    
    // Above threshold + knee: full compression
    if (inputDb > threshold + kneeWidth / 2.0f) {
        float overThreshold = inputDb - threshold;
        float targetOutput = threshold + overThreshold / ratio;
        return targetOutput - inputDb;  // Negative value (gain reduction)
    }
    
    // In knee region: soft knee compression
    float kneeStart = threshold - kneeWidth / 2.0f;
    float kneePosition = (inputDb - kneeStart) / kneeWidth;  // 0 to 1
    
    // Quadratic interpolation for soft knee
    float kneeRatio = 1.0f + (ratio - 1.0f) * kneePosition * kneePosition;
    float overThreshold = inputDb - threshold;
    float targetOutput = threshold + overThreshold / kneeRatio;
    
    return targetOutput - inputDb;
}

float PressProcessor::applyEnvelope(float targetGain, float currentGain) {
    // Feed-forward: target gain is what we want to apply
    // Use attack when gain is decreasing (compressing more)
    // Use release when gain is increasing (compressing less)
    
    if (targetGain < currentGain) {
        // Attack: compressing more
        return currentGain + m_attackCoeff * (targetGain - currentGain);
    } else {
        // Release: compressing less
        return currentGain + m_releaseCoeff * (targetGain - currentGain);
    }
}

void PressProcessor::updateEnvelopeCoeffs() {
    // Time constant formula: coeff = 1 - exp(-1 / (time * sampleRate))
    // This gives ~63% of the way to target in the specified time
    
    float attackTimeSamples = m_params.attackMs * static_cast<float>(m_sampleRate) / 1000.0f;
    float releaseTimeSamples = m_params.releaseMs * static_cast<float>(m_sampleRate) / 1000.0f;
    
    m_attackCoeff = 1.0f - std::exp(-1.0f / attackTimeSamples);
    m_releaseCoeff = 1.0f - std::exp(-1.0f / releaseTimeSamples);
}

float PressProcessor::calculateAutoMakeup() const {
    // Estimate makeup gain based on threshold and ratio
    // Assumes program material averages around -18 dBFS
    float averageLevel = -18.0f;
    
    if (averageLevel > m_params.thresholdDb) {
        float overThreshold = averageLevel - m_params.thresholdDb;
        float reduction = overThreshold - (overThreshold / m_params.ratio);
        return reduction * 0.7f;  // Apply 70% of calculated makeup
    }
    
    return 0.0f;
}

//==============================================================================
// Parameter Setters
//==============================================================================

void PressProcessor::setThreshold(float thresholdDb) {
    m_params.thresholdDb = std::clamp(thresholdDb, 
                                       PressConfig::MIN_THRESHOLD_DB, 
                                       PressConfig::MAX_THRESHOLD_DB);
}

void PressProcessor::setRatio(float ratio) {
    m_params.ratio = std::clamp(ratio, 
                                 PressConfig::MIN_RATIO, 
                                 PressConfig::MAX_RATIO);
}

void PressProcessor::setAttack(float attackMs) {
    m_params.attackMs = std::clamp(attackMs, 
                                    PressConfig::MIN_ATTACK_MS, 
                                    PressConfig::MAX_ATTACK_MS);
    if (m_prepared) {
        updateEnvelopeCoeffs();
    }
}

void PressProcessor::setRelease(float releaseMs) {
    m_params.releaseMs = std::clamp(releaseMs, 
                                     PressConfig::MIN_RELEASE_MS, 
                                     PressConfig::MAX_RELEASE_MS);
    if (m_prepared) {
        updateEnvelopeCoeffs();
    }
}

void PressProcessor::setMakeupGain(float gainDb) {
    m_params.makeupGainDb = std::clamp(gainDb, 
                                        PressConfig::MIN_GAIN_DB, 
                                        PressConfig::MAX_GAIN_DB);
}

void PressProcessor::setAutoMakeup(bool enabled) {
    m_params.autoMakeup = enabled;
}

//==============================================================================
// Ghost Hands Integration
//==============================================================================

void PressProcessor::applyPreset(CompressorPreset preset) {
    switch (preset) {
        case CompressorPreset::PUNCHY:
            // Punchy: slower attack lets transients through, moderate ratio
            setAttack(30.0f);
            setRatio(4.0f);
            setRelease(150.0f);
            break;
            
        case CompressorPreset::GLUE:
            // Glue: fast attack catches everything, gentle ratio for cohesion
            setAttack(1.0f);
            setRatio(2.0f);
            setRelease(300.0f);
            break;
            
        case CompressorPreset::CUSTOM:
        default:
            // No changes
            break;
    }
}

void PressProcessor::applyAISuggestion(const juce::String& suggestionName) {
    if (suggestionName.containsIgnoreCase("Punchy") || 
        suggestionName.containsIgnoreCase("punch")) {
        applyPreset(CompressorPreset::PUNCHY);
    }
    else if (suggestionName.containsIgnoreCase("Glue") || 
             suggestionName.containsIgnoreCase("cohesion")) {
        applyPreset(CompressorPreset::GLUE);
    }
}

//==============================================================================
// Visual State
//==============================================================================

HeartbeatVisualState PressProcessor::getVisualState() const {
    HeartbeatVisualState state;
    
    // Map gain reduction to heart scale
    // More GR = smaller heart (systole)
    // Less GR = larger heart (diastole)
    float grDb = m_gainReductionDb.load();
    float normalizedGR = std::min(grDb / 20.0f, 1.0f);  // Normalize to 0-1 (20dB max)
    state.heartScale = 1.0f - normalizedGR * 0.3f;  // Scale from 1.0 to 0.7
    
    // Map release time to relaxation rate
    // Faster release = faster relaxation
    float normalizedRelease = (m_params.releaseMs - PressConfig::MIN_RELEASE_MS) / 
                              (PressConfig::MAX_RELEASE_MS - PressConfig::MIN_RELEASE_MS);
    state.heartRelaxationRate = 1.0f - normalizedRelease;  // Invert: fast release = fast relaxation
    
    state.gainReductionDb = grDb;
    state.inputLevel = m_inputLevelDb.load();
    state.outputLevel = m_outputLevelDb.load();
    
    return state;
}

//==============================================================================
// State Save/Load
//==============================================================================

void PressProcessor::getStateInformation(juce::MemoryBlock& destData) {
    destData.append(&m_params.thresholdDb, sizeof(float));
    destData.append(&m_params.ratio, sizeof(float));
    destData.append(&m_params.attackMs, sizeof(float));
    destData.append(&m_params.releaseMs, sizeof(float));
    destData.append(&m_params.makeupGainDb, sizeof(float));
    
    int autoMakeup = m_params.autoMakeup ? 1 : 0;
    destData.append(&autoMakeup, sizeof(int));
}

void PressProcessor::setStateInformation(const void* data, int sizeInBytes) {
    const int expectedSize = 5 * sizeof(float) + sizeof(int);
    
    if (sizeInBytes >= expectedSize) {
        const char* byteData = static_cast<const char*>(data);
        int offset = 0;
        
        std::memcpy(&m_params.thresholdDb, byteData + offset, sizeof(float));
        offset += sizeof(float);
        
        std::memcpy(&m_params.ratio, byteData + offset, sizeof(float));
        offset += sizeof(float);
        
        std::memcpy(&m_params.attackMs, byteData + offset, sizeof(float));
        offset += sizeof(float);
        
        std::memcpy(&m_params.releaseMs, byteData + offset, sizeof(float));
        offset += sizeof(float);
        
        std::memcpy(&m_params.makeupGainDb, byteData + offset, sizeof(float));
        offset += sizeof(float);
        
        int autoMakeup;
        std::memcpy(&autoMakeup, byteData + offset, sizeof(int));
        m_params.autoMakeup = (autoMakeup != 0);
        
        if (m_prepared) {
            updateEnvelopeCoeffs();
        }
    }
}

//==============================================================================
// Editor
//==============================================================================

juce::AudioProcessorEditor* PressProcessor::createEditor() {
    return new juce::GenericAudioProcessorEditor(*this);
}

} // namespace iDAW

//==============================================================================
// Plugin Entry Point
//==============================================================================

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter() {
    return new iDAW::PressProcessor();
}
