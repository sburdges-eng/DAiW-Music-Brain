/**
 * LookAndFeel_Blueprint.cpp - Blueprint UI Style implementation
 *
 * Phase 1: The Foundation - Look & Feel Stubs
 */

#include "LookAndFeel_Blueprint.h"

namespace daiw {
namespace ui {

LookAndFeel_Blueprint::LookAndFeel_Blueprint() {
    // Set default colors for blueprint theme
    setColour(juce::Slider::thumbColourId, m_outlineColor);
    setColour(juce::Slider::rotarySliderFillColourId, m_accentColor);
    setColour(juce::Slider::rotarySliderOutlineColourId, m_outlineColor);
    setColour(juce::Slider::textBoxTextColourId, juce::Colours::white);
    setColour(juce::Slider::textBoxBackgroundColourId, m_fillColor);
    setColour(juce::Slider::textBoxOutlineColourId, m_outlineColor);

    setColour(juce::TextButton::buttonColourId, m_fillColor);
    setColour(juce::TextButton::textColourOffId, juce::Colours::white);
    setColour(juce::TextButton::textColourOnId, m_accentColor);

    setColour(juce::Label::textColourId, juce::Colours::white);
}

void LookAndFeel_Blueprint::drawRotarySlider(
    juce::Graphics& g,
    int x, int y, int width, int height,
    float sliderPosProportional,
    float rotaryStartAngle,
    float rotaryEndAngle,
    juce::Slider& slider)
{
    // Calculate dimensions with wobble offset
    auto bounds = juce::Rectangle<int>(x, y, width, height).toFloat();
    auto radius = juce::jmin(bounds.getWidth(), bounds.getHeight()) / 2.0f;
    auto centreX = bounds.getCentreX() + m_wobble * 0.5f;
    auto centreY = bounds.getCentreY() + m_wobble * 0.3f;
    auto knobRadius = radius * 0.75f;
    auto pointerLength = knobRadius * 0.6f;

    // Angle calculation
    auto angle = rotaryStartAngle + sliderPosProportional * (rotaryEndAngle - rotaryStartAngle);

    // Draw outer circle (transparent fill, white outline)
    g.setColour(m_fillColor);
    g.fillEllipse(centreX - knobRadius, centreY - knobRadius,
                  knobRadius * 2.0f, knobRadius * 2.0f);

    g.setColour(m_outlineColor.withAlpha(0.5f));
    g.drawEllipse(centreX - knobRadius, centreY - knobRadius,
                  knobRadius * 2.0f, knobRadius * 2.0f, LINE_THICKNESS);

    // Draw arc track with dashed effect
    juce::Path trackArc;
    trackArc.addCentredArc(centreX, centreY, radius - 4.0f, radius - 4.0f,
                           0.0f, rotaryStartAngle, rotaryEndAngle, true);

    // Create dashed stroke
    float dashLengths[] = {5.0f, 3.0f};
    juce::PathStrokeType dashStroke(LINE_THICKNESS);
    g.setColour(m_outlineColor.withAlpha(0.3f));
    g.strokePath(trackArc, dashStroke);

    // Draw filled arc (value indicator)
    juce::Path filledArc;
    filledArc.addCentredArc(centreX, centreY, radius - 4.0f, radius - 4.0f,
                            0.0f, rotaryStartAngle, angle, true);
    g.setColour(m_accentColor);
    g.strokePath(filledArc, juce::PathStrokeType(LINE_THICKNESS + 1.0f));

    // Draw inner circle (detail)
    float innerRadius = knobRadius * 0.4f;
    g.setColour(m_outlineColor.withAlpha(0.3f));
    g.drawEllipse(centreX - innerRadius, centreY - innerRadius,
                  innerRadius * 2.0f, innerRadius * 2.0f, 1.0f);

    // Draw crosshair inside knob
    g.setColour(m_outlineColor.withAlpha(0.2f));
    g.drawLine(centreX - innerRadius, centreY,
               centreX + innerRadius, centreY, 1.0f);
    g.drawLine(centreX, centreY - innerRadius,
               centreX, centreY + innerRadius, 1.0f);

    // Draw pointer
    juce::Path pointer;
    pointer.startNewSubPath(centreX, centreY);
    pointer.lineTo(centreX + std::sin(angle) * pointerLength,
                   centreY - std::cos(angle) * pointerLength);

    g.setColour(m_accentColor);
    g.strokePath(pointer, juce::PathStrokeType(LINE_THICKNESS + 1.0f,
                                                juce::PathStrokeType::curved,
                                                juce::PathStrokeType::rounded));

    // Draw pointer dot
    float dotRadius = 4.0f;
    float dotX = centreX + std::sin(angle) * pointerLength;
    float dotY = centreY - std::cos(angle) * pointerLength;
    g.setColour(m_accentColor);
    g.fillEllipse(dotX - dotRadius, dotY - dotRadius,
                  dotRadius * 2.0f, dotRadius * 2.0f);

    // Glowing effect on pointer dot (wobble-based)
    float glowAlpha = 0.3f + 0.2f * std::abs(m_wobble / 3.0f);
    g.setColour(m_accentColor.withAlpha(glowAlpha));
    g.drawEllipse(dotX - dotRadius * 1.5f, dotY - dotRadius * 1.5f,
                  dotRadius * 3.0f, dotRadius * 3.0f, 1.0f);
}

void LookAndFeel_Blueprint::drawButtonBackground(
    juce::Graphics& g,
    juce::Button& button,
    const juce::Colour& backgroundColour,
    bool shouldDrawButtonAsHighlighted,
    bool shouldDrawButtonAsDown)
{
    auto bounds = button.getLocalBounds().toFloat().reduced(1.0f);
    auto cornerSize = 4.0f;

    // Transparent fill with outline
    auto fillAlpha = 0.1f;
    if (shouldDrawButtonAsDown) {
        fillAlpha = 0.3f;
    } else if (shouldDrawButtonAsHighlighted) {
        fillAlpha = 0.2f;
    }

    g.setColour(m_accentColor.withAlpha(fillAlpha));
    g.fillRoundedRectangle(bounds, cornerSize);

    // Outline with glow effect
    auto outlineAlpha = 0.6f;
    if (shouldDrawButtonAsHighlighted) {
        outlineAlpha = 1.0f;
    }

    g.setColour(m_outlineColor.withAlpha(outlineAlpha));
    g.drawRoundedRectangle(bounds, cornerSize, LINE_THICKNESS);

    // Corner accents (blueprint style)
    float accentSize = 6.0f;
    g.setColour(m_accentColor);

    // Top-left corner
    g.drawLine(bounds.getX(), bounds.getY() + accentSize,
               bounds.getX(), bounds.getY(), LINE_THICKNESS);
    g.drawLine(bounds.getX(), bounds.getY(),
               bounds.getX() + accentSize, bounds.getY(), LINE_THICKNESS);

    // Top-right corner
    g.drawLine(bounds.getRight() - accentSize, bounds.getY(),
               bounds.getRight(), bounds.getY(), LINE_THICKNESS);
    g.drawLine(bounds.getRight(), bounds.getY(),
               bounds.getRight(), bounds.getY() + accentSize, LINE_THICKNESS);

    // Bottom-left corner
    g.drawLine(bounds.getX(), bounds.getBottom() - accentSize,
               bounds.getX(), bounds.getBottom(), LINE_THICKNESS);
    g.drawLine(bounds.getX(), bounds.getBottom(),
               bounds.getX() + accentSize, bounds.getBottom(), LINE_THICKNESS);

    // Bottom-right corner
    g.drawLine(bounds.getRight() - accentSize, bounds.getBottom(),
               bounds.getRight(), bounds.getBottom(), LINE_THICKNESS);
    g.drawLine(bounds.getRight(), bounds.getBottom(),
               bounds.getRight(), bounds.getBottom() - accentSize, LINE_THICKNESS);
}

void LookAndFeel_Blueprint::drawLabel(juce::Graphics& g, juce::Label& label) {
    g.fillAll(label.findColour(juce::Label::backgroundColourId));

    if (!label.isBeingEdited()) {
        auto textArea = label.getBorderSize().subtractedFrom(label.getLocalBounds());
        auto textColour = label.findColour(juce::Label::textColourId);

        // Add slight glow to text in blueprint mode
        g.setColour(m_accentColor.withAlpha(0.2f));
        g.setFont(label.getFont());

        // Draw shadow/glow
        auto offsetBounds = textArea.translated(1, 1);
        g.drawFittedText(label.getText(), offsetBounds, label.getJustificationType(),
                         juce::jmax(1, static_cast<int>(textArea.getHeight() / label.getFont().getHeight())),
                         label.getMinimumHorizontalScale());

        // Draw main text
        g.setColour(textColour);
        g.drawFittedText(label.getText(), textArea, label.getJustificationType(),
                         juce::jmax(1, static_cast<int>(textArea.getHeight() / label.getFont().getHeight())),
                         label.getMinimumHorizontalScale());
    }
}

} // namespace ui
} // namespace daiw
