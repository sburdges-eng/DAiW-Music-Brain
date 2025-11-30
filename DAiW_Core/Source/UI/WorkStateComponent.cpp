/**
 * WorkStateComponent.cpp - Work State UI implementation
 *
 * Phase 1: The Foundation - Dual-View Container
 */

#include "WorkStateComponent.h"
#include "LookAndFeel_Metal.h"

namespace daiw {
namespace ui {

WorkStateComponent::WorkStateComponent() {
    // Apply metal look and feel
    static LookAndFeel_Metal metalLnF;
    setLookAndFeel(&metalLnF);

    // Title label
    m_titleLabel.setText("WORK STATE", juce::dontSendNotification);
    m_titleLabel.setFont(juce::Font(24.0f, juce::Font::bold));
    m_titleLabel.setColour(juce::Label::textColourId, juce::Colours::lightgrey);
    m_titleLabel.setJustificationType(juce::Justification::centred);
    addAndMakeVisible(m_titleLabel);

    // State label
    m_stateLabel.setText("Iron Heap Active | Monotonic Allocator", juce::dontSendNotification);
    m_stateLabel.setFont(juce::Font(12.0f));
    m_stateLabel.setColour(juce::Label::textColourId, juce::Colours::grey);
    m_stateLabel.setJustificationType(juce::Justification::centred);
    addAndMakeVisible(m_stateLabel);

    // Test rotary slider with metal styling
    m_testSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    m_testSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    m_testSlider.setRange(0.0, 100.0, 1.0);
    m_testSlider.setValue(50.0);
    m_testSlider.setColour(juce::Slider::textBoxTextColourId, juce::Colours::white);
    addAndMakeVisible(m_testSlider);

    // Flip button
    m_flipButton.setButtonText("Switch to Dream");
    m_flipButton.setColour(juce::TextButton::buttonColourId, juce::Colour(0xff5a5a5a));
    m_flipButton.setColour(juce::TextButton::textColourOffId, juce::Colours::white);
    m_flipButton.onClick = [this]() {
        if (onFlipRequested) {
            onFlipRequested();
        }
    };
    addAndMakeVisible(m_flipButton);
}

WorkStateComponent::~WorkStateComponent() {
    setLookAndFeel(nullptr);
}

void WorkStateComponent::paint(juce::Graphics& g) {
    // Brushed metal gradient background
    juce::ColourGradient gradient(
        juce::Colour(BACKGROUND_COLOR),
        0.0f, 0.0f,
        juce::Colour(0xff4a4a4a),
        static_cast<float>(getWidth()),
        static_cast<float>(getHeight()),
        false
    );
    g.setGradientFill(gradient);
    g.fillRect(getLocalBounds());

    // Add subtle horizontal lines for brushed metal effect
    g.setColour(juce::Colours::white.withAlpha(0.02f));
    for (int y = 0; y < getHeight(); y += 2) {
        g.drawHorizontalLine(y, 0.0f, static_cast<float>(getWidth()));
    }

    // Border
    g.setColour(juce::Colour(0xff2a2a2a));
    g.drawRect(getLocalBounds(), 1);
}

void WorkStateComponent::resized() {
    auto bounds = getLocalBounds().reduced(20);

    // Title at top
    m_titleLabel.setBounds(bounds.removeFromTop(40));

    // State label below title
    m_stateLabel.setBounds(bounds.removeFromTop(20));

    bounds.removeFromTop(20);  // Spacing

    // Center area for controls
    auto centerArea = bounds.reduced(40);

    // Rotary slider in center
    auto sliderBounds = centerArea.withSizeKeepingCentre(150, 150);
    m_testSlider.setBounds(sliderBounds);

    // Flip button at bottom
    auto bottomArea = bounds.removeFromBottom(40);
    m_flipButton.setBounds(bottomArea.withSizeKeepingCentre(150, 30));
}

} // namespace ui
} // namespace daiw
