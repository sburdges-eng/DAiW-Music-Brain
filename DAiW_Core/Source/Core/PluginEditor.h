#pragma once
/**
 * PluginEditor.h - Audio Plugin Editor (UI)
 *
 * DAiW Phase 1: The Foundation
 *
 * The PluginEditor manages the plugin UI and hosts the MainComponent.
 */

#include <JuceHeader.h>
#include "PluginProcessor.h"
#include "../UI/MainComponent.h"

namespace daiw {

/**
 * DAiW_CoreAudioProcessorEditor - Plugin UI
 *
 * Hosts the MainComponent and connects to the processor.
 */
class DAiW_CoreAudioProcessorEditor : public juce::AudioProcessorEditor,
                                       private ui::MainComponent::Listener {
public:
    explicit DAiW_CoreAudioProcessorEditor(DAiW_CoreAudioProcessor& processor);
    ~DAiW_CoreAudioProcessorEditor() override;

    // Component overrides
    void paint(juce::Graphics& g) override;
    void resized() override;

private:
    // MainComponent::Listener override
    void viewStateChanged(ui::ViewState newState) override;

    // Reference to processor
    DAiW_CoreAudioProcessor& m_processor;

    // Main UI component
    std::unique_ptr<ui::MainComponent> m_mainComponent;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(DAiW_CoreAudioProcessorEditor)
};

} // namespace daiw
