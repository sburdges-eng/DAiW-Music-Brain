#pragma once
/**
 * PluginProcessor.h - Audio Plugin Processor
 *
 * DAiW Phase 1: The Foundation
 *
 * The PluginProcessor handles all audio processing and plugin state.
 * It uses the MemoryManager for all buffer allocations.
 */

#include <JuceHeader.h>
#include "../Memory/MemoryManager.h"
#include "../Memory/DAiW_Buffer.h"

namespace daiw {

/**
 * DAiW_CoreAudioProcessor - Main audio processor for DAiW plugin
 *
 * Responsibilities:
 * - Audio processing with Iron Heap buffers
 * - Plugin state management
 * - MIDI routing
 */
class DAiW_CoreAudioProcessor : public juce::AudioProcessor {
public:
    DAiW_CoreAudioProcessor();
    ~DAiW_CoreAudioProcessor() override;

    // AudioProcessor interface
    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;

    bool isBusesLayoutSupported(const BusesLayout& layouts) const override;

    void processBlock(juce::AudioBuffer<float>& buffer,
                      juce::MidiBuffer& midiMessages) override;

    // Editor
    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }

    // State
    const juce::String getName() const override { return JucePlugin_Name; }

    bool acceptsMidi() const override { return true; }
    bool producesMidi() const override { return true; }
    bool isMidiEffect() const override { return false; }
    double getTailLengthSeconds() const override { return 0.0; }

    // Programs
    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram(int index) override {}
    const juce::String getProgramName(int index) override { return {}; }
    void changeProgramName(int index, const juce::String& newName) override {}

    // State persistence
    void getStateInformation(juce::MemoryBlock& destData) override;
    void setStateInformation(const void* data, int sizeInBytes) override;

    // DAiW-specific
    [[nodiscard]] bool isDreamState() const noexcept { return m_isDreamState; }
    void setDreamState(bool dream);

    // Parameters (using APVTS for thread-safe access)
    juce::AudioProcessorValueTreeState& getParameters() { return m_parameters; }

private:
    // Create parameter layout
    static juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout();

    // State
    bool m_isDreamState{false};
    double m_sampleRate{44100.0};
    int m_blockSize{512};

    // Parameter tree state
    juce::AudioProcessorValueTreeState m_parameters;

    // Audio buffers using MemoryManager
    std::unique_ptr<memory::AudioBuffer> m_processBuffer;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(DAiW_CoreAudioProcessor)
};

} // namespace daiw
