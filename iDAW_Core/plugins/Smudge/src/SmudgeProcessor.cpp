/**
 * SmudgeProcessor.cpp - Implementation of Plugin 004: "The Smudge"
 * 
 * Profile: 'Convolution Reverb' with Scrapbook UI
 */

#include "SmudgeProcessor.h"

namespace iDAW {

SmudgeProcessor::SmudgeProcessor()
    : AudioProcessor(BusesProperties()
                     .withInput("Input", juce::AudioChannelSet::stereo(), true)
                     .withOutput("Output", juce::AudioChannelSet::stereo(), true))
{
    m_fft = std::make_unique<juce::dsp::FFT>(SmudgeConfig::FFT_ORDER);
    
    // Initialize IR library mapping
    m_irLibrary["Cave"] = "IR_Cave.wav";
    m_irLibrary["Room"] = "IR_Studio.wav";
    m_irLibrary["Hall"] = "IR_Hall.wav";
    m_irLibrary["Plate"] = "IR_Plate.wav";
    m_irLibrary["Spring"] = "IR_Spring.wav";
}

SmudgeProcessor::~SmudgeProcessor() = default;

void SmudgeProcessor::prepareToPlay(double sampleRate, int samplesPerBlock) {
    m_sampleRate = sampleRate;
    
    // Initialize buffers
    m_inputBuffer.resize(SmudgeConfig::FFT_SIZE * 2, 0.0f);
    m_outputBuffer.resize(SmudgeConfig::FFT_SIZE * 2, 0.0f);
    m_fftBuffer.resize(SmudgeConfig::FFT_SIZE + 1);
    
    // Pre-delay buffer
    int maxPreDelaySamples = static_cast<int>(SmudgeConfig::MAX_PREDELAY_MS * sampleRate / 1000.0);
    m_preDelayBuffer.resize(maxPreDelaySamples, 0.0f);
    m_preDelayWriteIndex = 0;
    
    // High-cut filter
    updateHighCutFilter();
    
    m_prepared = true;
}

void SmudgeProcessor::releaseResources() {
    m_inputBuffer.clear();
    m_outputBuffer.clear();
    m_prepared = false;
}

void SmudgeProcessor::processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer&) {
    if (!m_prepared || m_irPartitions.empty()) {
        // Pass through if no IR loaded
        return;
    }
    
    juce::ScopedNoDenormals noDenormals;
    
    const int numSamples = buffer.getNumSamples();
    float mix = m_mix.load();
    
    // Process left channel (mono convolution for simplicity)
    const float* inputL = buffer.getReadPointer(0);
    float* outputL = buffer.getWritePointer(0);
    
    // Temporary buffers
    std::vector<float> wetSignal(numSamples, 0.0f);
    
    // Process convolution
    processConvolution(const_cast<float*>(inputL), wetSignal.data(), numSamples);
    
    // Mix dry/wet
    for (int i = 0; i < numSamples; ++i) {
        outputL[i] = inputL[i] * (1.0f - mix) + wetSignal[i] * mix;
    }
    
    // Copy to right channel
    if (buffer.getNumChannels() > 1) {
        float* outputR = buffer.getWritePointer(1);
        std::memcpy(outputR, outputL, numSamples * sizeof(float));
    }
}

void SmudgeProcessor::processConvolution(float* input, float* output, int numSamples) {
    // Simplified uniformly-partitioned convolution
    for (int i = 0; i < numSamples; ++i) {
        // Apply pre-delay
        int preDelaySamples = static_cast<int>(m_preDelayMs.load() * m_sampleRate / 1000.0);
        preDelaySamples = std::min(preDelaySamples, static_cast<int>(m_preDelayBuffer.size()) - 1);
        
        int readIndex = (m_preDelayWriteIndex - preDelaySamples + m_preDelayBuffer.size()) % m_preDelayBuffer.size();
        float delayedSample = m_preDelayBuffer[readIndex];
        m_preDelayBuffer[m_preDelayWriteIndex] = input[i];
        m_preDelayWriteIndex = (m_preDelayWriteIndex + 1) % m_preDelayBuffer.size();
        
        // Simple convolution (first partition only for demo)
        if (!m_currentIR.samples.empty()) {
            // Direct convolution for short IRs
            float sum = 0.0f;
            int irLen = std::min(static_cast<int>(m_currentIR.samples.size()), 512);
            
            for (int j = 0; j < irLen && (i - j) >= 0; ++j) {
                sum += input[i - j] * m_currentIR.samples[j];
            }
            output[i] = sum;
        } else {
            output[i] = delayedSample;
        }
    }
}

void SmudgeProcessor::prepareIR() {
    if (m_currentIR.samples.empty()) return;
    
    // Partition IR for FFT convolution
    int numPartitions = (static_cast<int>(m_currentIR.samples.size()) + SmudgeConfig::FFT_SIZE - 1) / SmudgeConfig::FFT_SIZE;
    m_irPartitions.resize(numPartitions);
    
    for (int p = 0; p < numPartitions; ++p) {
        m_irPartitions[p].resize(SmudgeConfig::FFT_SIZE + 1);
        
        std::vector<float> partitionData(SmudgeConfig::FFT_SIZE * 2, 0.0f);
        int startIdx = p * SmudgeConfig::FFT_SIZE;
        int copyLen = std::min(SmudgeConfig::FFT_SIZE, static_cast<int>(m_currentIR.samples.size()) - startIdx);
        
        for (int i = 0; i < copyLen; ++i) {
            partitionData[i] = m_currentIR.samples[startIdx + i];
        }
        
        // FFT the partition
        m_fft->performRealOnlyForwardTransform(partitionData.data());
        
        // Store as complex
        for (int i = 0; i <= SmudgeConfig::FFT_SIZE / 2; ++i) {
            m_irPartitions[p][i] = std::complex<float>(partitionData[i * 2], partitionData[i * 2 + 1]);
        }
    }
    
    // Initialize FDL buffer
    m_fdlBuffer.resize(numPartitions);
    for (auto& fdl : m_fdlBuffer) {
        fdl.resize(SmudgeConfig::FFT_SIZE + 1, std::complex<float>(0, 0));
    }
    m_fdlIndex = 0;
}

bool SmudgeProcessor::loadIR(const juce::File& file) {
    juce::AudioFormatManager formatManager;
    formatManager.registerBasicFormats();
    
    std::unique_ptr<juce::AudioFormatReader> reader(formatManager.createReaderFor(file));
    if (!reader) return false;
    
    // Read IR samples
    int numSamples = static_cast<int>(reader->lengthInSamples);
    numSamples = std::min(numSamples, SmudgeConfig::MAX_IR_LENGTH);
    
    m_currentIR.samples.resize(numSamples);
    juce::AudioBuffer<float> tempBuffer(1, numSamples);
    reader->read(&tempBuffer, 0, numSamples, 0, true, false);
    
    std::memcpy(m_currentIR.samples.data(), tempBuffer.getReadPointer(0), numSamples * sizeof(float));
    m_currentIR.sampleRate = static_cast<int>(reader->sampleRate);
    m_currentIR.name = file.getFileNameWithoutExtension();
    m_currentIRName = m_currentIR.name;
    
    prepareIR();
    return true;
}

bool SmudgeProcessor::loadIRFromLibrary(const juce::String& name) {
    auto it = m_irLibrary.find(name);
    if (it == m_irLibrary.end()) return false;
    
    // In a real implementation, load from bundled resources
    // For now, generate a simple synthetic IR
    m_currentIR.samples.resize(static_cast<int>(m_sampleRate * 2));  // 2 second IR
    
    for (size_t i = 0; i < m_currentIR.samples.size(); ++i) {
        float t = static_cast<float>(i) / m_sampleRate;
        float decay = std::exp(-t * 3.0f);  // 3 second decay time
        float noise = (static_cast<float>(rand()) / RAND_MAX * 2.0f - 1.0f);
        m_currentIR.samples[i] = noise * decay * 0.5f;
    }
    
    m_currentIR.name = name;
    m_currentIRName = name;
    
    {
        std::lock_guard<std::mutex> lock(m_visualMutex);
        m_visualState.currentSpace = name;
        m_visualState.tearProgress = 1.0f;  // Trigger tear animation
    }
    
    prepareIR();
    return true;
}

std::vector<juce::String> SmudgeProcessor::getAvailableIRs() const {
    std::vector<juce::String> names;
    for (const auto& pair : m_irLibrary) {
        names.push_back(pair.first);
    }
    return names;
}

void SmudgeProcessor::applyAISuggestion(const juce::String& spaceName) {
    loadIRFromLibrary(spaceName);
}

void SmudgeProcessor::setMix(float mix) { m_mix.store(std::clamp(mix, 0.0f, 1.0f)); }
void SmudgeProcessor::setDecay(float decay) { m_decay.store(std::clamp(decay, 0.5f, SmudgeConfig::MAX_DECAY)); }
void SmudgeProcessor::setPreDelay(float ms) { m_preDelayMs.store(std::clamp(ms, 0.0f, SmudgeConfig::MAX_PREDELAY_MS)); }
void SmudgeProcessor::setHighCut(float hz) { m_highCutHz.store(std::clamp(hz, 1000.0f, 20000.0f)); updateHighCutFilter(); }

void SmudgeProcessor::updateHighCutFilter() {
    if (m_sampleRate > 0) {
        m_highCutCoeffs = juce::dsp::IIR::Coefficients<float>::makeLowPass(m_sampleRate, m_highCutHz.load());
        m_highCutFilter.coefficients = m_highCutCoeffs;
    }
}

ScrapbookVisualState SmudgeProcessor::getVisualState() const {
    std::lock_guard<std::mutex> lock(m_visualMutex);
    return m_visualState;
}

void SmudgeProcessor::setPhotoCorner(float x, float y) {
    std::lock_guard<std::mutex> lock(m_visualMutex);
    m_visualState.photoCornerX = x;
    m_visualState.photoCornerY = y;
    
    // Map corner position to decay
    float decay = 0.5f + (x * 0.5f + y * 0.5f) * 2.5f;
    m_decay.store(decay);
}

double SmudgeProcessor::getTailLengthSeconds() const {
    return m_decay.load() * 2.0;
}

void SmudgeProcessor::getStateInformation(juce::MemoryBlock& destData) {
    float mix = m_mix.load();
    float decay = m_decay.load();
    float preDelay = m_preDelayMs.load();
    float highCut = m_highCutHz.load();
    
    destData.append(&mix, sizeof(float));
    destData.append(&decay, sizeof(float));
    destData.append(&preDelay, sizeof(float));
    destData.append(&highCut, sizeof(float));
}

void SmudgeProcessor::setStateInformation(const void* data, int sizeInBytes) {
    if (sizeInBytes >= 4 * sizeof(float)) {
        const float* floatData = static_cast<const float*>(data);
        m_mix.store(floatData[0]);
        m_decay.store(floatData[1]);
        m_preDelayMs.store(floatData[2]);
        m_highCutHz.store(floatData[3]);
    }
}

juce::AudioProcessorEditor* SmudgeProcessor::createEditor() {
    return new juce::GenericAudioProcessorEditor(*this);
}

} // namespace iDAW

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter() {
    return new iDAW::SmudgeProcessor();
}
