/**
 * LookAndFeel_Metal.cpp - Brushed Metal UI Style implementation
 *
 * Phase 1: The Foundation - Look & Feel Stubs
 */

#include "LookAndFeel_Metal.h"

namespace daiw {
namespace ui {

LookAndFeel_Metal::LookAndFeel_Metal() {
    // Set default colors for metal theme
    setColour(juce::Slider::thumbColourId, m_metalBase);
    setColour(juce::Slider::rotarySliderFillColourId, m_accentColor);
    setColour(juce::Slider::rotarySliderOutlineColourId, m_metalShadow);
    setColour(juce::Slider::textBoxTextColourId, juce::Colours::white);
    setColour(juce::Slider::textBoxBackgroundColourId, m_metalShadow);
    setColour(juce::Slider::textBoxOutlineColourId, m_metalBase);

    setColour(juce::TextButton::buttonColourId, m_metalBase);
    setColour(juce::TextButton::textColourOffId, juce::Colours::white);
    setColour(juce::TextButton::textColourOnId, m_accentColor);

    setColour(juce::Label::textColourId, juce::Colours::lightgrey);
}

void LookAndFeel_Metal::drawRotarySlider(
    juce::Graphics& g,
    int x, int y, int width, int height,
    float sliderPosProportional,
    float rotaryStartAngle,
    float rotaryEndAngle,
    juce::Slider& slider)
{
    // Calculate dimensions
    auto bounds = juce::Rectangle<int>(x, y, width, height).toFloat();
    auto radius = juce::jmin(bounds.getWidth(), bounds.getHeight()) / 2.0f;
    auto centreX = bounds.getCentreX();
    auto centreY = bounds.getCentreY();
    auto knobRadius = radius * 0.8f;
    auto pointerLength = knobRadius * 0.6f;
    auto lineWidth = 3.0f;

    // Draw outer ring (track)
    g.setColour(m_metalShadow);
    juce::Path outerArc;
    outerArc.addCentredArc(centreX, centreY, radius - 2.0f, radius - 2.0f,
                           0.0f, rotaryStartAngle, rotaryEndAngle, true);
    g.strokePath(outerArc, juce::PathStrokeType(4.0f));

    // Draw filled arc (value indicator)
    auto angle = rotaryStartAngle + sliderPosProportional * (rotaryEndAngle - rotaryStartAngle);
    g.setColour(m_accentColor);
    juce::Path filledArc;
    filledArc.addCentredArc(centreX, centreY, radius - 2.0f, radius - 2.0f,
                            0.0f, rotaryStartAngle, angle, true);
    g.strokePath(filledArc, juce::PathStrokeType(4.0f));

    // Draw brushed metal knob
    drawBrushedMetalCircle(g, centreX, centreY, knobRadius);

    // Draw knob border
    g.setColour(m_metalShadow);
    g.drawEllipse(centreX - knobRadius, centreY - knobRadius,
                  knobRadius * 2.0f, knobRadius * 2.0f, 2.0f);

    // Draw pointer
    juce::Path pointer;
    auto pointerThickness = 4.0f;
    pointer.addRectangle(-pointerThickness * 0.5f, -pointerLength,
                         pointerThickness, pointerLength);
    pointer.applyTransform(
        juce::AffineTransform::rotation(angle).translated(centreX, centreY));

    g.setColour(m_accentColor);
    g.fillPath(pointer);

    // Pointer shadow
    g.setColour(m_metalShadow);
    g.strokePath(pointer, juce::PathStrokeType(1.0f));
}

void LookAndFeel_Metal::drawBrushedMetalCircle(
    juce::Graphics& g,
    float centreX, float centreY,
    float radius)
{
    // Base gradient for 3D effect
    juce::ColourGradient gradient(
        m_metalHighlight,
        centreX - radius * 0.3f, centreY - radius * 0.3f,
        m_metalShadow,
        centreX + radius * 0.5f, centreY + radius * 0.5f,
        true  // Radial
    );
    g.setGradientFill(gradient);
    g.fillEllipse(centreX - radius, centreY - radius, radius * 2.0f, radius * 2.0f);

    // Add brushed metal lines
    g.saveState();
    g.reduceClipRegion(juce::Path().addEllipse(centreX - radius, centreY - radius,
                                                radius * 2.0f, radius * 2.0f));

    g.setColour(juce::Colours::white.withAlpha(0.05f));
    for (float lineY = centreY - radius; lineY < centreY + radius; lineY += 2.0f) {
        g.drawHorizontalLine(static_cast<int>(lineY),
                             centreX - radius, centreX + radius);
    }

    // Add subtle circular highlight
    g.setColour(juce::Colours::white.withAlpha(0.1f));
    g.fillEllipse(centreX - radius * 0.5f, centreY - radius * 0.6f,
                  radius * 0.6f, radius * 0.3f);

    g.restoreState();
}

void LookAndFeel_Metal::drawButtonBackground(
    juce::Graphics& g,
    juce::Button& button,
    const juce::Colour& backgroundColour,
    bool shouldDrawButtonAsHighlighted,
    bool shouldDrawButtonAsDown)
{
    auto bounds = button.getLocalBounds().toFloat().reduced(1.0f);
    auto cornerSize = 4.0f;

    // Base color with state variations
    auto baseColour = backgroundColour;
    if (shouldDrawButtonAsDown) {
        baseColour = baseColour.darker(0.2f);
    } else if (shouldDrawButtonAsHighlighted) {
        baseColour = baseColour.brighter(0.1f);
    }

    // Draw button with gradient
    juce::ColourGradient gradient(
        baseColour.brighter(0.1f),
        0.0f, bounds.getY(),
        baseColour.darker(0.1f),
        0.0f, bounds.getBottom(),
        false
    );
    g.setGradientFill(gradient);
    g.fillRoundedRectangle(bounds, cornerSize);

    // Border
    g.setColour(m_metalShadow);
    g.drawRoundedRectangle(bounds, cornerSize, 1.0f);

    // Highlight on top edge
    g.setColour(juce::Colours::white.withAlpha(0.1f));
    g.drawLine(bounds.getX() + cornerSize, bounds.getY() + 1.0f,
               bounds.getRight() - cornerSize, bounds.getY() + 1.0f);
}

void LookAndFeel_Metal::drawLabel(juce::Graphics& g, juce::Label& label) {
    g.fillAll(label.findColour(juce::Label::backgroundColourId));

    if (!label.isBeingEdited()) {
        auto textArea = label.getBorderSize().subtractedFrom(label.getLocalBounds());
        auto textColour = label.findColour(juce::Label::textColourId);

        g.setColour(textColour);
        g.setFont(label.getFont());
        g.drawFittedText(label.getText(), textArea, label.getJustificationType(),
                         juce::jmax(1, static_cast<int>(textArea.getHeight() / label.getFont().getHeight())),
                         label.getMinimumHorizontalScale());
    }
}

} // namespace ui
} // namespace daiw
