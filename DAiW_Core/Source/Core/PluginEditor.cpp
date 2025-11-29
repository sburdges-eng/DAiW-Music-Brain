/**
 * PluginEditor.cpp - Audio Plugin Editor implementation
 *
 * Phase 1: The Foundation
 */

#include "PluginEditor.h"

namespace daiw {

DAiW_CoreAudioProcessorEditor::DAiW_CoreAudioProcessorEditor(DAiW_CoreAudioProcessor& processor)
    : AudioProcessorEditor(&processor), m_processor(processor)
{
    // Create main component
    m_mainComponent = std::make_unique<ui::MainComponent>();
    m_mainComponent->addListener(this);
    addAndMakeVisible(*m_mainComponent);

    // Sync initial state
    m_mainComponent->setDreamState(m_processor.isDreamState());

    // Set plugin window size
    setSize(800, 600);
    setResizable(true, true);
    setResizeLimits(400, 300, 1920, 1080);
}

DAiW_CoreAudioProcessorEditor::~DAiW_CoreAudioProcessorEditor() {
    if (m_mainComponent) {
        m_mainComponent->removeListener(this);
    }
}

void DAiW_CoreAudioProcessorEditor::paint(juce::Graphics& g) {
    // Background is handled by MainComponent
    g.fillAll(juce::Colours::black);
}

void DAiW_CoreAudioProcessorEditor::resized() {
    if (m_mainComponent) {
        m_mainComponent->setBounds(getLocalBounds());
    }
}

void DAiW_CoreAudioProcessorEditor::viewStateChanged(ui::ViewState newState) {
    // Sync state to processor
    bool isDream = (newState == ui::ViewState::Dream);
    m_processor.setDreamState(isDream);
}

} // namespace daiw
