#pragma once
/**
 * LookAndFeel_Metal.h - Brushed Metal UI Style (Side A)
 *
 * DAiW Phase 1: The Foundation
 *
 * Metal look characteristics:
 * - Brushed metal texture on knobs
 * - Grey/silver color scheme
 * - Industrial, production-focused aesthetic
 * - Used in Work State
 */

#include <JuceHeader.h>

namespace daiw {
namespace ui {

/**
 * LookAndFeel_Metal - Industrial metal styling for Work state
 *
 * Overrides JUCE's default look for a professional production feel.
 */
class LookAndFeel_Metal : public juce::LookAndFeel_V4 {
public:
    LookAndFeel_Metal();
    ~LookAndFeel_Metal() override = default;

    /**
     * Draw rotary slider with brushed metal knob effect
     */
    void drawRotarySlider(juce::Graphics& g,
                          int x, int y, int width, int height,
                          float sliderPosProportional,
                          float rotaryStartAngle,
                          float rotaryEndAngle,
                          juce::Slider& slider) override;

    /**
     * Draw button with metal styling
     */
    void drawButtonBackground(juce::Graphics& g,
                              juce::Button& button,
                              const juce::Colour& backgroundColour,
                              bool shouldDrawButtonAsHighlighted,
                              bool shouldDrawButtonAsDown) override;

    /**
     * Draw label with industrial styling
     */
    void drawLabel(juce::Graphics& g, juce::Label& label) override;

private:
    // Color scheme
    juce::Colour m_metalBase{0xff5a5a5a};
    juce::Colour m_metalHighlight{0xff8a8a8a};
    juce::Colour m_metalShadow{0xff3a3a3a};
    juce::Colour m_accentColor{0xffff9800};  // Orange accent

    // Helper to draw brushed metal effect
    void drawBrushedMetalCircle(juce::Graphics& g,
                                float centreX, float centreY,
                                float radius);

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(LookAndFeel_Metal)
};

} // namespace ui
} // namespace daiw
