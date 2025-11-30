#pragma once
/**
 * DreamStateComponent.h - Dream State UI (Side B)
 *
 * DAiW Phase 1: The Foundation
 *
 * Dream State characteristics:
 * - Blue background with blueprint aesthetic
 * - Uses Playground allocator (thread-safe, expandable)
 * - Creative/experimental-focused UI
 * - LookAndFeel_Blueprint styling with wobble effect
 */

#include <JuceHeader.h>

namespace daiw {
namespace ui {

/**
 * DreamStateComponent - Creative/experimental UI panel
 *
 * This component represents the "Dream" state of the DAiW interface,
 * designed for creative exploration and experimental features.
 */
class DreamStateComponent : public juce::Component,
                            private juce::Timer {
public:
    DreamStateComponent();
    ~DreamStateComponent() override;

    // Component overrides
    void paint(juce::Graphics& g) override;
    void resized() override;

    // Access test controls (for development)
    juce::Slider& getTestSlider() { return m_testSlider; }
    juce::TextButton& getFlipButton() { return m_flipButton; }

    // Callback for flip button
    std::function<void()> onFlipRequested;

private:
    // Timer callback for animations
    void timerCallback() override;

    // Background color
    static constexpr uint32_t BACKGROUND_COLOR = 0xff1a237e;  // Deep blue

    // Animation state
    float m_wobblePhase{0.0f};
    static constexpr float WOBBLE_SPEED = 0.05f;
    static constexpr float WOBBLE_AMOUNT = 3.0f;

    // Grid for blueprint effect
    static constexpr int GRID_SIZE = 20;

    // Test UI elements
    juce::Slider m_testSlider;
    juce::Label m_titleLabel;
    juce::TextButton m_flipButton;

    // State indicator
    juce::Label m_stateLabel;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(DreamStateComponent)
};

} // namespace ui
} // namespace daiw
