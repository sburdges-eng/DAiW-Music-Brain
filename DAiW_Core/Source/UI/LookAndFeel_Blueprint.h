#pragma once
/**
 * LookAndFeel_Blueprint.h - Blueprint UI Style (Side B)
 *
 * DAiW Phase 1: The Foundation
 *
 * Blueprint look characteristics:
 * - White outline on transparent/blue background
 * - Grid pattern reminiscent of technical drawings
 * - Animated wobble effect for "dream" state feel
 * - Used in Dream State
 */

#include <JuceHeader.h>

namespace daiw {
namespace ui {

/**
 * LookAndFeel_Blueprint - Technical drawing style for Dream state
 *
 * Features animated wobble effect for organic, creative feel.
 */
class LookAndFeel_Blueprint : public juce::LookAndFeel_V4 {
public:
    LookAndFeel_Blueprint();
    ~LookAndFeel_Blueprint() override = default;

    /**
     * Draw rotary slider with blueprint outline style
     */
    void drawRotarySlider(juce::Graphics& g,
                          int x, int y, int width, int height,
                          float sliderPosProportional,
                          float rotaryStartAngle,
                          float rotaryEndAngle,
                          juce::Slider& slider) override;

    /**
     * Draw button with blueprint styling
     */
    void drawButtonBackground(juce::Graphics& g,
                              juce::Button& button,
                              const juce::Colour& backgroundColour,
                              bool shouldDrawButtonAsHighlighted,
                              bool shouldDrawButtonAsDown) override;

    /**
     * Draw label with blueprint styling
     */
    void drawLabel(juce::Graphics& g, juce::Label& label) override;

    /**
     * Set wobble amount for animated effect
     *
     * @param wobble Current wobble value (typically from sin() function)
     */
    void setWobble(float wobble) { m_wobble = wobble; }

    /**
     * Get current wobble value
     */
    [[nodiscard]] float getWobble() const noexcept { return m_wobble; }

private:
    // Color scheme
    juce::Colour m_outlineColor{juce::Colours::white};
    juce::Colour m_fillColor{juce::Colours::cyan.withAlpha(0.2f)};
    juce::Colour m_accentColor{juce::Colours::cyan};
    juce::Colour m_backgroundColor{0x00000000};  // Transparent

    // Animation state
    float m_wobble{0.0f};

    // Line thickness
    static constexpr float LINE_THICKNESS = 2.0f;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(LookAndFeel_Blueprint)
};

} // namespace ui
} // namespace daiw
