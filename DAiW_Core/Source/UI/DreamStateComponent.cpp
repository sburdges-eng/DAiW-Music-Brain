/**
 * DreamStateComponent.cpp - Dream State UI implementation
 *
 * Phase 1: The Foundation - Dual-View Container
 */

#include "DreamStateComponent.h"
#include "LookAndFeel_Blueprint.h"

namespace daiw {
namespace ui {

DreamStateComponent::DreamStateComponent() {
    // Apply blueprint look and feel
    static LookAndFeel_Blueprint blueprintLnF;
    setLookAndFeel(&blueprintLnF);

    // Title label
    m_titleLabel.setText("DREAM STATE", juce::dontSendNotification);
    m_titleLabel.setFont(juce::Font(24.0f, juce::Font::bold));
    m_titleLabel.setColour(juce::Label::textColourId, juce::Colours::white);
    m_titleLabel.setJustificationType(juce::Justification::centred);
    addAndMakeVisible(m_titleLabel);

    // State label
    m_stateLabel.setText("Playground Active | Pool Allocator", juce::dontSendNotification);
    m_stateLabel.setFont(juce::Font(12.0f));
    m_stateLabel.setColour(juce::Label::textColourId, juce::Colours::lightblue);
    m_stateLabel.setJustificationType(juce::Justification::centred);
    addAndMakeVisible(m_stateLabel);

    // Test rotary slider with blueprint styling
    m_testSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    m_testSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    m_testSlider.setRange(0.0, 100.0, 1.0);
    m_testSlider.setValue(50.0);
    m_testSlider.setColour(juce::Slider::textBoxTextColourId, juce::Colours::white);
    addAndMakeVisible(m_testSlider);

    // Flip button
    m_flipButton.setButtonText("Switch to Work");
    m_flipButton.setColour(juce::TextButton::buttonColourId, juce::Colour(0xff3949ab));
    m_flipButton.setColour(juce::TextButton::textColourOffId, juce::Colours::white);
    m_flipButton.onClick = [this]() {
        if (onFlipRequested) {
            onFlipRequested();
        }
    };
    addAndMakeVisible(m_flipButton);

    // Start wobble animation timer
    startTimerHz(60);  // 60fps for smooth animation
}

DreamStateComponent::~DreamStateComponent() {
    stopTimer();
    setLookAndFeel(nullptr);
}

void DreamStateComponent::timerCallback() {
    // Update wobble phase
    m_wobblePhase += WOBBLE_SPEED;
    if (m_wobblePhase > juce::MathConstants<float>::twoPi) {
        m_wobblePhase -= juce::MathConstants<float>::twoPi;
    }

    // Trigger repaint for animation
    repaint();
}

void DreamStateComponent::paint(juce::Graphics& g) {
    // Blue gradient background
    juce::ColourGradient gradient(
        juce::Colour(BACKGROUND_COLOR),
        0.0f, 0.0f,
        juce::Colour(0xff283593),
        static_cast<float>(getWidth()),
        static_cast<float>(getHeight()),
        false
    );
    g.setGradientFill(gradient);
    g.fillRect(getLocalBounds());

    // Blueprint grid effect with wobble
    float wobbleOffset = std::sin(m_wobblePhase) * WOBBLE_AMOUNT;

    g.setColour(juce::Colours::white.withAlpha(0.1f));

    // Vertical lines with wobble
    for (int x = GRID_SIZE; x < getWidth(); x += GRID_SIZE) {
        float xPos = static_cast<float>(x) + wobbleOffset * std::sin(x * 0.02f);
        g.drawLine(xPos, 0.0f, xPos, static_cast<float>(getHeight()), 0.5f);
    }

    // Horizontal lines with wobble
    for (int y = GRID_SIZE; y < getHeight(); y += GRID_SIZE) {
        float yPos = static_cast<float>(y) + wobbleOffset * std::cos(y * 0.02f);
        g.drawLine(0.0f, yPos, static_cast<float>(getWidth()), yPos, 0.5f);
    }

    // Glowing border effect
    g.setColour(juce::Colours::cyan.withAlpha(0.3f + 0.1f * std::sin(m_wobblePhase)));
    g.drawRect(getLocalBounds().reduced(2), 2);
}

void DreamStateComponent::resized() {
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
