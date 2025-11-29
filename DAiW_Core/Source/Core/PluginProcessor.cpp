/**
 * PluginProcessor.cpp - Audio Plugin Processor implementation
 *
 * Phase 1: The Foundation
 */

#include "PluginProcessor.h"
#include "PluginEditor.h"

namespace daiw {

DAiW_CoreAudioProcessor::DAiW_CoreAudioProcessor()
    : AudioProcessor(BusesProperties()
                     .withInput("Input", juce::AudioChannelSet::stereo(), true)
                     .withOutput("Output", juce::AudioChannelSet::stereo(), true)),
      m_parameters(*this, nullptr, "DAiW_Parameters", createParameterLayout())
{
    // Initialize MemoryManager (happens on first access)
    auto& mm = memory::MemoryManager::getInstance();
    jassert(mm.isInitialized());
}

DAiW_CoreAudioProcessor::~DAiW_CoreAudioProcessor() {
    // Clean up any Iron Heap allocations if transitioning between sessions
    // In production, would call resetIronHeap() here if appropriate
}

juce::AudioProcessorValueTreeState::ParameterLayout
DAiW_CoreAudioProcessor::createParameterLayout() {
    std::vector<std::unique_ptr<juce::RangedAudioParameter>> params;

    // Add main parameters
    params.push_back(std::make_unique<juce::AudioParameterFloat>(
        juce::ParameterID{"gain", 1},
        "Gain",
        juce::NormalisableRange<float>(0.0f, 2.0f, 0.01f),
        1.0f
    ));

    params.push_back(std::make_unique<juce::AudioParameterFloat>(
        juce::ParameterID{"mix", 1},
        "Mix",
        juce::NormalisableRange<float>(0.0f, 1.0f, 0.01f),
        1.0f
    ));

    params.push_back(std::make_unique<juce::AudioParameterBool>(
        juce::ParameterID{"dreamMode", 1},
        "Dream Mode",
        false
    ));

    return {params.begin(), params.end()};
}

void DAiW_CoreAudioProcessor::prepareToPlay(double sampleRate, int samplesPerBlock) {
    m_sampleRate = sampleRate;
    m_blockSize = samplesPerBlock;

    // Allocate process buffer using Iron Heap (critical audio path)
    m_processBuffer = std::make_unique<memory::AudioBuffer>(
        static_cast<size_t>(samplesPerBlock * 2),  // Stereo
        memory::SideID::IronHeap
    );
}

void DAiW_CoreAudioProcessor::releaseResources() {
    // Note: m_processBuffer will be deallocated, but for Iron Heap
    // this is a no-op until resetIronHeap() is called
    m_processBuffer.reset();
}

bool DAiW_CoreAudioProcessor::isBusesLayoutSupported(const BusesLayout& layouts) const {
    // Support mono or stereo
    if (layouts.getMainOutputChannelSet() != juce::AudioChannelSet::mono()
        && layouts.getMainOutputChannelSet() != juce::AudioChannelSet::stereo()) {
        return false;
    }

    // Input should match output
    if (layouts.getMainOutputChannelSet() != layouts.getMainInputChannelSet()) {
        return false;
    }

    return true;
}

void DAiW_CoreAudioProcessor::processBlock(juce::AudioBuffer<float>& buffer,
                                            juce::MidiBuffer& midiMessages) {
    juce::ScopedNoDenormals noDenormals;

    auto totalNumInputChannels = getTotalNumInputChannels();
    auto totalNumOutputChannels = getTotalNumOutputChannels();

    // Clear any unused output channels
    for (auto i = totalNumInputChannels; i < totalNumOutputChannels; ++i) {
        buffer.clear(i, 0, buffer.getNumSamples());
    }

    // Get parameters
    float gain = *m_parameters.getRawParameterValue("gain");
    float mix = *m_parameters.getRawParameterValue("mix");

    // Process audio
    for (int channel = 0; channel < totalNumInputChannels; ++channel) {
        auto* channelData = buffer.getWritePointer(channel);

        for (int sample = 0; sample < buffer.getNumSamples(); ++sample) {
            // Apply gain (this is a simple example - real processing would be more complex)
            channelData[sample] *= gain * mix;
        }
    }

    // Process MIDI if in dream state (example of state-dependent behavior)
    if (m_isDreamState) {
        // In dream state, we could apply creative MIDI transformations
        // For now, just pass through
    }
}

juce::AudioProcessorEditor* DAiW_CoreAudioProcessor::createEditor() {
    return new DAiW_CoreAudioProcessorEditor(*this);
}

void DAiW_CoreAudioProcessor::getStateInformation(juce::MemoryBlock& destData) {
    // Save parameter state
    auto state = m_parameters.copyState();
    std::unique_ptr<juce::XmlElement> xml(state.createXml());

    // Add custom state
    xml->setAttribute("dreamState", m_isDreamState);

    copyXmlToBinary(*xml, destData);
}

void DAiW_CoreAudioProcessor::setStateInformation(const void* data, int sizeInBytes) {
    std::unique_ptr<juce::XmlElement> xml(getXmlFromBinary(data, sizeInBytes));

    if (xml != nullptr) {
        if (xml->hasTagName(m_parameters.state.getType())) {
            m_parameters.replaceState(juce::ValueTree::fromXml(*xml));
        }

        // Load custom state
        m_isDreamState = xml->getBoolAttribute("dreamState", false);
    }
}

void DAiW_CoreAudioProcessor::setDreamState(bool dream) {
    m_isDreamState = dream;

    // Update parameter
    if (auto* param = m_parameters.getParameter("dreamMode")) {
        param->setValueNotifyingHost(dream ? 1.0f : 0.0f);
    }
}

} // namespace daiw

// Plugin entry point
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter() {
    return new daiw::DAiW_CoreAudioProcessor();
}
