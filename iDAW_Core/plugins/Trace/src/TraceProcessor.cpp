/**
 * TraceProcessor.cpp - Implementation of Plugin 005: "The Trace"
 * 
 * Profile: 'Tape/Digital Delay' with Spirograph UI
 */

#include "TraceProcessor.h"

namespace iDAW {

TraceProcessor::TraceProcessor()
    : AudioProcessor(BusesProperties()
                     .withInput("Input", juce::AudioChannelSet::stereo(), true)
                     .withOutput("Output", juce::AudioChannelSet::stereo(), true))
{
}

TraceProcessor::~TraceProcessor() = default;

void TraceProcessor::prepareToPlay(double sampleRate, int samplesPerBlock) {
    m_sampleRate = sampleRate;
    
    // Calculate buffer size for max delay
    m_bufferSize = static_cast<int>(TraceConfig::MAX_DELAY_MS * sampleRate / 1000.0) + 1;
    
    // Initialize delay buffers
    for (int ch = 0; ch < 2; ++ch) {
        m_delayBuffer[ch].resize(m_bufferSize, 0.0f);
        m_writeIndex[ch] = 0;
    }
    
    m_lfoPhase = 0.0f;
    m_prepared = true;
}

void TraceProcessor::releaseResources() {
    for (auto& buf : m_delayBuffer) buf.clear();
    m_prepared = false;
}

void TraceProcessor::processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer&) {
    if (!m_prepared) return;
    
    juce::ScopedNoDenormals noDenormals;
    
    // Get host tempo if available
    if (auto* playHead = getPlayHead()) {
        updateFromPlayHead(playHead);
    }
    
    const int numSamples = buffer.getNumSamples();
    float delayMs = m_delayTimeMs.load();
    float feedback = m_feedback.load();
    float mix = m_mix.load();
    bool pingPong = m_pingPong.load();
    bool useTape = m_tapeSaturation.load();
    
    // Sync to host if needed
    if (m_syncNote != SyncNote::FREE) {
        delayMs = static_cast<float>(calculateSyncedDelay(m_hostBPM));
    }
    
    float delaySamples = delayMs * static_cast<float>(m_sampleRate) / 1000.0f;
    
    for (int sample = 0; sample < numSamples; ++sample) {
        // Update LFO
        updateLFO();
        
        // Apply modulation to delay time
        float modulatedDelay = delaySamples + m_currentModulation;
        modulatedDelay = std::clamp(modulatedDelay, 1.0f, static_cast<float>(m_bufferSize - 1));
        
        for (int channel = 0; channel < buffer.getNumChannels(); ++channel) {
            float* channelData = buffer.getWritePointer(channel);
            float inputSample = channelData[sample];
            
            // Read from delay buffer with interpolation
            float delayedSample = readFromBuffer(channel, modulatedDelay);
            
            // Apply tape saturation if enabled
            if (useTape) {
                delayedSample = applyTapeSaturation(delayedSample);
            }
            
            // Calculate feedback input
            float feedbackSample;
            if (pingPong && buffer.getNumChannels() > 1) {
                // Ping-pong: feed opposite channel
                int otherChannel = 1 - channel;
                feedbackSample = readFromBuffer(otherChannel, modulatedDelay);
                if (useTape) feedbackSample = applyTapeSaturation(feedbackSample);
            } else {
                feedbackSample = delayedSample;
            }
            
            // Write to buffer: input + feedback
            writeToBuffer(channel, inputSample + feedbackSample * feedback);
            
            // Mix output
            channelData[sample] = inputSample * (1.0f - mix) + delayedSample * mix;
        }
    }
    
    // Update visual state
    {
        std::lock_guard<std::mutex> lock(m_visualMutex);
        m_visualState.outerRadius = std::clamp(delayMs / TraceConfig::MAX_DELAY_MS, 0.1f, 1.0f);
        m_visualState.loopCount = 2.0f + feedback * 10.0f;
        m_visualState.traceProgress = std::fmod(m_visualState.traceProgress + 0.01f, 1.0f);
    }
}

float TraceProcessor::readFromBuffer(int channel, float delaySamples) {
    // Linear interpolation for fractional delay
    int indexA = m_writeIndex[channel] - static_cast<int>(delaySamples);
    int indexB = indexA - 1;
    
    while (indexA < 0) indexA += m_bufferSize;
    while (indexB < 0) indexB += m_bufferSize;
    
    indexA %= m_bufferSize;
    indexB %= m_bufferSize;
    
    float frac = delaySamples - std::floor(delaySamples);
    
    return m_delayBuffer[channel][indexA] * (1.0f - frac) + 
           m_delayBuffer[channel][indexB] * frac;
}

void TraceProcessor::writeToBuffer(int channel, float sample) {
    m_delayBuffer[channel][m_writeIndex[channel]] = sample;
    m_writeIndex[channel] = (m_writeIndex[channel] + 1) % m_bufferSize;
}

float TraceProcessor::applyTapeSaturation(float sample) {
    // Soft saturation using tanh
    float drive = TraceConfig::TAPE_DRIVE;
    return std::tanh(sample * drive) / std::tanh(drive);
}

void TraceProcessor::updateLFO() {
    float rate = m_modRateHz.load();
    float depth = m_modDepthMs.load();
    
    m_lfoPhase += rate / static_cast<float>(m_sampleRate);
    if (m_lfoPhase >= 1.0f) m_lfoPhase -= 1.0f;
    
    // Sine LFO for wow/flutter
    m_currentModulation = std::sin(m_lfoPhase * 2.0f * juce::MathConstants<float>::pi) * 
                          depth * static_cast<float>(m_sampleRate) / 1000.0f;
}

float TraceProcessor::calculateSyncedDelay(double bpm) {
    if (bpm <= 0) bpm = 120.0;
    
    double beatMs = 60000.0 / bpm;  // Quarter note duration in ms
    
    switch (m_syncNote) {
        case SyncNote::WHOLE:           return static_cast<float>(beatMs * 4.0);
        case SyncNote::HALF:            return static_cast<float>(beatMs * 2.0);
        case SyncNote::QUARTER:         return static_cast<float>(beatMs);
        case SyncNote::QUARTER_DOT:     return static_cast<float>(beatMs * 1.5);
        case SyncNote::EIGHTH:          return static_cast<float>(beatMs * 0.5);
        case SyncNote::EIGHTH_DOT:      return static_cast<float>(beatMs * 0.75);
        case SyncNote::SIXTEENTH:       return static_cast<float>(beatMs * 0.25);
        case SyncNote::TRIPLET_QUARTER: return static_cast<float>(beatMs * 2.0 / 3.0);
        case SyncNote::TRIPLET_EIGHTH:  return static_cast<float>(beatMs / 3.0);
        default: return m_delayTimeMs.load();
    }
}

void TraceProcessor::updateFromPlayHead(juce::AudioPlayHead* playHead) {
    if (auto position = playHead->getPosition()) {
        if (auto bpm = position->getBpm()) {
            m_hostBPM = *bpm;
        }
    }
}

void TraceProcessor::applyAISuggestion(const juce::String& suggestion) {
    if (suggestion.containsIgnoreCase("Slapback") || suggestion.containsIgnoreCase("slap")) {
        // Slapback: 120ms, 0% feedback
        setDelayTime(120.0f);
        setFeedback(0.0f);
        setModulationDepth(0.0f);
        m_syncNote = SyncNote::FREE;
    }
    else if (suggestion.containsIgnoreCase("Ethereal") || suggestion.containsIgnoreCase("ambient")) {
        // Ethereal: 1/4 dotted, 60% feedback, 20% mod
        m_syncNote = SyncNote::QUARTER_DOT;
        setFeedback(0.6f);
        setModulationDepth(20.0f);
        setModulationRate(0.3f);
    }
}

// Parameter setters
void TraceProcessor::setDelayTime(float ms) { m_delayTimeMs.store(std::clamp(ms, TraceConfig::MIN_DELAY_MS, TraceConfig::MAX_DELAY_MS)); }
void TraceProcessor::setFeedback(float fb) { m_feedback.store(std::clamp(fb, 0.0f, TraceConfig::MAX_FEEDBACK)); }
void TraceProcessor::setMix(float mix) { m_mix.store(std::clamp(mix, 0.0f, 1.0f)); }
void TraceProcessor::setModulationDepth(float ms) { m_modDepthMs.store(std::clamp(ms, 0.0f, TraceConfig::MAX_MODULATION_DEPTH)); }
void TraceProcessor::setModulationRate(float hz) { m_modRateHz.store(std::clamp(hz, 0.01f, TraceConfig::MAX_MODULATION_RATE)); }
void TraceProcessor::setPingPong(bool enabled) { m_pingPong.store(enabled); }
void TraceProcessor::setSync(SyncNote note) { m_syncNote = note; }
void TraceProcessor::setTapeSaturation(bool enabled) { m_tapeSaturation.store(enabled); }

SpirographVisualState TraceProcessor::getVisualState() const {
    std::lock_guard<std::mutex> lock(m_visualMutex);
    return m_visualState;
}

double TraceProcessor::getTailLengthSeconds() const {
    float maxDelay = m_delayTimeMs.load() / 1000.0f;
    float fb = m_feedback.load();
    return maxDelay / (1.0f - fb + 0.01f);
}

void TraceProcessor::getStateInformation(juce::MemoryBlock& destData) {
    float delayTime = m_delayTimeMs.load();
    float feedback = m_feedback.load();
    float mix = m_mix.load();
    float modDepth = m_modDepthMs.load();
    float modRate = m_modRateHz.load();
    
    destData.append(&delayTime, sizeof(float));
    destData.append(&feedback, sizeof(float));
    destData.append(&mix, sizeof(float));
    destData.append(&modDepth, sizeof(float));
    destData.append(&modRate, sizeof(float));
}

void TraceProcessor::setStateInformation(const void* data, int sizeInBytes) {
    if (sizeInBytes >= 5 * sizeof(float)) {
        const float* floatData = static_cast<const float*>(data);
        m_delayTimeMs.store(floatData[0]);
        m_feedback.store(floatData[1]);
        m_mix.store(floatData[2]);
        m_modDepthMs.store(floatData[3]);
        m_modRateHz.store(floatData[4]);
    }
}

juce::AudioProcessorEditor* TraceProcessor::createEditor() {
    return new juce::GenericAudioProcessorEditor(*this);
}

} // namespace iDAW

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter() {
    return new iDAW::TraceProcessor();
}
