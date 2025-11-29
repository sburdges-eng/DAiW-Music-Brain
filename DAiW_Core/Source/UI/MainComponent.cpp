/**
 * MainComponent.cpp - Dual-view container implementation
 *
 * Phase 1: The Foundation - Dual-View Container
 */

#include "MainComponent.h"
#include "WorkStateComponent.h"
#include "DreamStateComponent.h"

namespace daiw {
namespace ui {

MainComponent::MainComponent() {
    // Create both child components
    m_workComponent = std::make_unique<WorkStateComponent>();
    m_dreamComponent = std::make_unique<DreamStateComponent>();

    // Initially show work state
    addAndMakeVisible(*m_workComponent);
    addChildComponent(*m_dreamComponent);  // Added but not visible

    m_currentComponent = m_workComponent.get();
    m_isDreamState = false;

    // Set a default size
    setSize(800, 600);
}

MainComponent::~MainComponent() {
    // Components cleaned up by unique_ptr
}

void MainComponent::setDreamState(bool dream) {
    if (m_isDreamState == dream) {
        return;  // No change needed
    }

    m_isDreamState = dream;
    updateVisibleComponent();
    notifyListeners();
}

void MainComponent::triggerFlip() {
    setDreamState(!m_isDreamState);
}

void MainComponent::updateVisibleComponent() {
    if (m_isDreamState) {
        // Transition to Dream state
        m_workComponent->setVisible(false);
        m_dreamComponent->setVisible(true);
        m_dreamComponent->setBounds(getLocalBounds());
        m_currentComponent = m_dreamComponent.get();

        // Could add animation here:
        // m_animator.fadeIn(m_dreamComponent.get(), 300);
    } else {
        // Transition to Work state
        m_dreamComponent->setVisible(false);
        m_workComponent->setVisible(true);
        m_workComponent->setBounds(getLocalBounds());
        m_currentComponent = m_workComponent.get();
    }

    repaint();
}

void MainComponent::notifyListeners() {
    ViewState newState = m_isDreamState ? ViewState::Dream : ViewState::Work;
    m_listeners.call([newState](Listener& l) {
        l.viewStateChanged(newState);
    });
}

void MainComponent::addListener(Listener* listener) {
    m_listeners.add(listener);
}

void MainComponent::removeListener(Listener* listener) {
    m_listeners.remove(listener);
}

void MainComponent::paint(juce::Graphics& g) {
    // Background color based on state
    if (m_isDreamState) {
        // Dream state: Deep blue gradient
        juce::ColourGradient gradient(
            juce::Colour(0xff1a237e),  // Dark blue
            0.0f, 0.0f,
            juce::Colour(0xff283593),  // Slightly lighter blue
            static_cast<float>(getWidth()),
            static_cast<float>(getHeight()),
            false
        );
        g.setGradientFill(gradient);
    } else {
        // Work state: Grey gradient
        juce::ColourGradient gradient(
            juce::Colour(0xff3d3d3d),  // Dark grey
            0.0f, 0.0f,
            juce::Colour(0xff4a4a4a),  // Slightly lighter grey
            static_cast<float>(getWidth()),
            static_cast<float>(getHeight()),
            false
        );
        g.setGradientFill(gradient);
    }

    g.fillRect(getLocalBounds());

    // Draw state indicator in corner
    g.setColour(juce::Colours::white.withAlpha(0.3f));
    g.setFont(10.0f);
    juce::String stateText = m_isDreamState ? "DREAM" : "WORK";
    g.drawText(stateText, getLocalBounds().reduced(10).removeFromTop(20),
               juce::Justification::topRight);
}

void MainComponent::resized() {
    auto bounds = getLocalBounds();

    // Resize both components to fill the area
    if (m_workComponent) {
        m_workComponent->setBounds(bounds);
    }
    if (m_dreamComponent) {
        m_dreamComponent->setBounds(bounds);
    }
}

} // namespace ui
} // namespace daiw
