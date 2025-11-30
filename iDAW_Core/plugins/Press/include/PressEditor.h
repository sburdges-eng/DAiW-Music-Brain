/**
 * PressEditor.h - UI Component for Plugin 003: "The Press"
 * 
 * Profile: 'VCA Workhorse' (Clean, RMS Detection, Feed-Forward)
 * 
 * Minimal LookAndFeel: White text on Black background
 * Standard JUCE Rotary sliders
 * Accurate GR metering
 */

#pragma once

#include <JuceHeader.h>
#include "PressProcessor.h"

namespace iDAW {

/**
 * Minimal black/white LookAndFeel for VCA Workhorse
 */
class VCALookAndFeel : public juce::LookAndFeel_V4 {
public:
    VCALookAndFeel() {
        // Dark theme
        setColour(juce::ResizableWindow::backgroundColourId, juce::Colour(0xFF1A1A1A));
        setColour(juce::Slider::thumbColourId, juce::Colours::white);
        setColour(juce::Slider::rotarySliderFillColourId, juce::Colours::white);
        setColour(juce::Slider::rotarySliderOutlineColourId, juce::Colour(0xFF404040));
        setColour(juce::Slider::textBoxTextColourId, juce::Colours::white);
        setColour(juce::Slider::textBoxBackgroundColourId, juce::Colour(0xFF2A2A2A));
        setColour(juce::Slider::textBoxOutlineColourId, juce::Colour(0xFF404040));
        setColour(juce::Label::textColourId, juce::Colours::white);
        setColour(juce::TextButton::buttonColourId, juce::Colour(0xFF333333));
        setColour(juce::TextButton::textColourOffId, juce::Colours::white);
    }
    
    void drawRotarySlider(juce::Graphics& g, int x, int y, int width, int height,
                          float sliderPos, float rotaryStartAngle, float rotaryEndAngle,
                          juce::Slider& slider) override {
        auto bounds = juce::Rectangle<int>(x, y, width, height).toFloat().reduced(5);
        auto radius = juce::jmin(bounds.getWidth(), bounds.getHeight()) / 2.0f;
        auto toAngle = rotaryStartAngle + sliderPos * (rotaryEndAngle - rotaryStartAngle);
        auto lineW = 2.0f;
        auto arcRadius = radius - lineW * 2.0f;
        
        // Background circle
        g.setColour(juce::Colour(0xFF2A2A2A));
        g.fillEllipse(bounds.getCentreX() - radius, bounds.getCentreY() - radius,
                      radius * 2.0f, radius * 2.0f);
        
        // Track
        juce::Path backgroundArc;
        backgroundArc.addCentredArc(bounds.getCentreX(), bounds.getCentreY(),
                                     arcRadius, arcRadius, 0.0f,
                                     rotaryStartAngle, rotaryEndAngle, true);
        g.setColour(juce::Colour(0xFF404040));
        g.strokePath(backgroundArc, juce::PathStrokeType(lineW));
        
        // Value arc
        if (slider.isEnabled()) {
            juce::Path valueArc;
            valueArc.addCentredArc(bounds.getCentreX(), bounds.getCentreY(),
                                   arcRadius, arcRadius, 0.0f,
                                   rotaryStartAngle, toAngle, true);
            g.setColour(juce::Colours::white);
            g.strokePath(valueArc, juce::PathStrokeType(lineW * 1.5f));
        }
        
        // Pointer line
        juce::Path pointer;
        auto pointerLength = arcRadius * 0.7f;
        auto pointerThickness = 2.0f;
        pointer.addRectangle(-pointerThickness * 0.5f, -arcRadius, pointerThickness, pointerLength);
        pointer.applyTransform(juce::AffineTransform::rotation(toAngle)
                               .translated(bounds.getCentreX(), bounds.getCentreY()));
        g.setColour(juce::Colours::white);
        g.fillPath(pointer);
        
        // Center dot
        g.fillEllipse(bounds.getCentreX() - 3, bounds.getCentreY() - 3, 6, 6);
    }
};

/**
 * GR Meter component
 */
class GRMeter : public juce::Component, private juce::Timer {
public:
    GRMeter(PressProcessor& processor) : m_processor(processor) {
        startTimerHz(30);
    }
    
    ~GRMeter() override { stopTimer(); }
    
    void paint(juce::Graphics& g) override {
        auto bounds = getLocalBounds().toFloat();
        
        // Background
        g.setColour(juce::Colour(0xFF1A1A1A));
        g.fillRect(bounds);
        
        // Border
        g.setColour(juce::Colour(0xFF404040));
        g.drawRect(bounds, 1.0f);
        
        // GR fill (from top)
        float grDb = m_processor.getGainReduction();
        float normalizedGR = std::min(grDb / 20.0f, 1.0f);  // 20dB max
        
        float fillHeight = normalizedGR * bounds.getHeight();
        
        // Gradient from orange to red
        juce::ColourGradient gradient(
            juce::Colour(0xFFFF6600), bounds.getCentreX(), bounds.getY(),
            juce::Colour(0xFFFF0000), bounds.getCentreX(), bounds.getBottom(),
            false
        );
        g.setGradientFill(gradient);
        g.fillRect(bounds.getX() + 1, bounds.getY() + 1,
                   bounds.getWidth() - 2, fillHeight);
        
        // GR value text
        g.setColour(juce::Colours::white);
        g.setFont(12.0f);
        juce::String grText = juce::String(grDb, 1) + " dB";
        g.drawText(grText, bounds.reduced(2), juce::Justification::centredBottom);
        
        // Label
        g.drawText("GR", bounds.reduced(2), juce::Justification::centredTop);
    }
    
private:
    void timerCallback() override { repaint(); }
    
    PressProcessor& m_processor;
};

/**
 * PressEditor - Main editor component for The Press
 */
class PressEditor : public juce::AudioProcessorEditor,
                    public juce::Slider::Listener,
                    public juce::Button::Listener {
public:
    explicit PressEditor(PressProcessor& processor);
    ~PressEditor() override;
    
    void paint(juce::Graphics& g) override;
    void resized() override;
    
    void sliderValueChanged(juce::Slider* slider) override;
    void buttonClicked(juce::Button* button) override;
    
private:
    void updateFromProcessor();
    
    PressProcessor& m_processor;
    VCALookAndFeel m_lookAndFeel;
    
    // Controls
    juce::Slider m_thresholdSlider;
    juce::Label m_thresholdLabel;
    
    juce::Slider m_ratioSlider;
    juce::Label m_ratioLabel;
    
    juce::Slider m_attackSlider;
    juce::Label m_attackLabel;
    
    juce::Slider m_releaseSlider;
    juce::Label m_releaseLabel;
    
    juce::Slider m_gainSlider;
    juce::Label m_gainLabel;
    
    // GR Meter
    std::unique_ptr<GRMeter> m_grMeter;
    
    // Ghost Hands presets
    juce::TextButton m_punchyButton;
    juce::TextButton m_glueButton;
    
    // Auto makeup
    juce::ToggleButton m_autoMakeupButton;
    
    // Title
    juce::Label m_titleLabel;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(PressEditor)
};

// ============================================================================
// Implementation
// ============================================================================

inline PressEditor::PressEditor(PressProcessor& processor)
    : AudioProcessorEditor(&processor), m_processor(processor)
{
    setSize(450, 300);
    setLookAndFeel(&m_lookAndFeel);
    
    // Title
    addAndMakeVisible(m_titleLabel);
    m_titleLabel.setText("THE PRESS", juce::dontSendNotification);
    m_titleLabel.setFont(juce::Font(22.0f, juce::Font::bold));
    m_titleLabel.setColour(juce::Label::textColourId, juce::Colours::white);
    m_titleLabel.setJustificationType(juce::Justification::centred);
    
    // Threshold
    addAndMakeVisible(m_thresholdSlider);
    m_thresholdSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    m_thresholdSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 60, 18);
    m_thresholdSlider.setRange(-60.0, 0.0, 0.1);
    m_thresholdSlider.setValue(m_processor.getThreshold());
    m_thresholdSlider.setTextValueSuffix(" dB");
    m_thresholdSlider.addListener(this);
    
    addAndMakeVisible(m_thresholdLabel);
    m_thresholdLabel.setText("THRESHOLD", juce::dontSendNotification);
    m_thresholdLabel.setJustificationType(juce::Justification::centred);
    
    // Ratio
    addAndMakeVisible(m_ratioSlider);
    m_ratioSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    m_ratioSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 60, 18);
    m_ratioSlider.setRange(1.0, 20.0, 0.1);
    m_ratioSlider.setValue(m_processor.getRatio());
    m_ratioSlider.setTextValueSuffix(":1");
    m_ratioSlider.addListener(this);
    
    addAndMakeVisible(m_ratioLabel);
    m_ratioLabel.setText("RATIO", juce::dontSendNotification);
    m_ratioLabel.setJustificationType(juce::Justification::centred);
    
    // Attack
    addAndMakeVisible(m_attackSlider);
    m_attackSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    m_attackSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 60, 18);
    m_attackSlider.setRange(0.1, 100.0, 0.1);
    m_attackSlider.setValue(m_processor.getAttack());
    m_attackSlider.setTextValueSuffix(" ms");
    m_attackSlider.setSkewFactorFromMidPoint(10.0);
    m_attackSlider.addListener(this);
    
    addAndMakeVisible(m_attackLabel);
    m_attackLabel.setText("ATTACK", juce::dontSendNotification);
    m_attackLabel.setJustificationType(juce::Justification::centred);
    
    // Release
    addAndMakeVisible(m_releaseSlider);
    m_releaseSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    m_releaseSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 60, 18);
    m_releaseSlider.setRange(10.0, 2000.0, 1.0);
    m_releaseSlider.setValue(m_processor.getRelease());
    m_releaseSlider.setTextValueSuffix(" ms");
    m_releaseSlider.setSkewFactorFromMidPoint(200.0);
    m_releaseSlider.addListener(this);
    
    addAndMakeVisible(m_releaseLabel);
    m_releaseLabel.setText("RELEASE", juce::dontSendNotification);
    m_releaseLabel.setJustificationType(juce::Justification::centred);
    
    // Makeup Gain
    addAndMakeVisible(m_gainSlider);
    m_gainSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    m_gainSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 60, 18);
    m_gainSlider.setRange(-12.0, 24.0, 0.1);
    m_gainSlider.setValue(m_processor.getMakeupGain());
    m_gainSlider.setTextValueSuffix(" dB");
    m_gainSlider.addListener(this);
    
    addAndMakeVisible(m_gainLabel);
    m_gainLabel.setText("GAIN", juce::dontSendNotification);
    m_gainLabel.setJustificationType(juce::Justification::centred);
    
    // GR Meter
    m_grMeter = std::make_unique<GRMeter>(m_processor);
    addAndMakeVisible(m_grMeter.get());
    
    // Ghost Hands buttons
    addAndMakeVisible(m_punchyButton);
    m_punchyButton.setButtonText("PUNCHY");
    m_punchyButton.addListener(this);
    
    addAndMakeVisible(m_glueButton);
    m_glueButton.setButtonText("GLUE");
    m_glueButton.addListener(this);
    
    // Auto makeup
    addAndMakeVisible(m_autoMakeupButton);
    m_autoMakeupButton.setButtonText("AUTO");
    m_autoMakeupButton.setToggleState(m_processor.getAutoMakeup(), juce::dontSendNotification);
    m_autoMakeupButton.onClick = [this]() {
        m_processor.setAutoMakeup(m_autoMakeupButton.getToggleState());
    };
}

inline PressEditor::~PressEditor() {
    setLookAndFeel(nullptr);
}

inline void PressEditor::paint(juce::Graphics& g) {
    g.fillAll(juce::Colour(0xFF1A1A1A));
    
    // Subtle grid lines
    g.setColour(juce::Colour(0xFF252525));
    for (int x = 0; x < getWidth(); x += 20) {
        g.drawVerticalLine(x, 0.0f, static_cast<float>(getHeight()));
    }
    for (int y = 0; y < getHeight(); y += 20) {
        g.drawHorizontalLine(y, 0.0f, static_cast<float>(getWidth()));
    }
}

inline void PressEditor::resized() {
    auto area = getLocalBounds().reduced(10);
    
    // Title
    m_titleLabel.setBounds(area.removeFromTop(30));
    area.removeFromTop(5);
    
    // GR Meter on the right
    auto meterArea = area.removeFromRight(40);
    m_grMeter->setBounds(meterArea.reduced(0, 20));
    area.removeFromRight(10);
    
    // Main controls area
    auto controlsArea = area.removeFromTop(150);
    int sliderWidth = controlsArea.getWidth() / 5;
    
    // Threshold
    auto thresholdArea = controlsArea.removeFromLeft(sliderWidth);
    m_thresholdLabel.setBounds(thresholdArea.removeFromTop(18));
    m_thresholdSlider.setBounds(thresholdArea);
    
    // Ratio
    auto ratioArea = controlsArea.removeFromLeft(sliderWidth);
    m_ratioLabel.setBounds(ratioArea.removeFromTop(18));
    m_ratioSlider.setBounds(ratioArea);
    
    // Attack
    auto attackArea = controlsArea.removeFromLeft(sliderWidth);
    m_attackLabel.setBounds(attackArea.removeFromTop(18));
    m_attackSlider.setBounds(attackArea);
    
    // Release
    auto releaseArea = controlsArea.removeFromLeft(sliderWidth);
    m_releaseLabel.setBounds(releaseArea.removeFromTop(18));
    m_releaseSlider.setBounds(releaseArea);
    
    // Gain
    auto gainArea = controlsArea.removeFromLeft(sliderWidth);
    m_gainLabel.setBounds(gainArea.removeFromTop(18));
    m_gainSlider.setBounds(gainArea);
    
    // Bottom buttons
    area.removeFromTop(15);
    auto buttonsArea = area.removeFromTop(35);
    
    m_punchyButton.setBounds(buttonsArea.removeFromLeft(80).reduced(2));
    buttonsArea.removeFromLeft(5);
    m_glueButton.setBounds(buttonsArea.removeFromLeft(80).reduced(2));
    buttonsArea.removeFromLeft(20);
    m_autoMakeupButton.setBounds(buttonsArea.removeFromLeft(80).reduced(2));
}

inline void PressEditor::sliderValueChanged(juce::Slider* slider) {
    if (slider == &m_thresholdSlider) {
        m_processor.setThreshold(static_cast<float>(slider->getValue()));
    }
    else if (slider == &m_ratioSlider) {
        m_processor.setRatio(static_cast<float>(slider->getValue()));
    }
    else if (slider == &m_attackSlider) {
        m_processor.setAttack(static_cast<float>(slider->getValue()));
    }
    else if (slider == &m_releaseSlider) {
        m_processor.setRelease(static_cast<float>(slider->getValue()));
    }
    else if (slider == &m_gainSlider) {
        m_processor.setMakeupGain(static_cast<float>(slider->getValue()));
    }
}

inline void PressEditor::buttonClicked(juce::Button* button) {
    if (button == &m_punchyButton) {
        m_processor.applyPreset(CompressorPreset::PUNCHY);
        updateFromProcessor();
    }
    else if (button == &m_glueButton) {
        m_processor.applyPreset(CompressorPreset::GLUE);
        updateFromProcessor();
    }
}

inline void PressEditor::updateFromProcessor() {
    m_thresholdSlider.setValue(m_processor.getThreshold(), juce::dontSendNotification);
    m_ratioSlider.setValue(m_processor.getRatio(), juce::dontSendNotification);
    m_attackSlider.setValue(m_processor.getAttack(), juce::dontSendNotification);
    m_releaseSlider.setValue(m_processor.getRelease(), juce::dontSendNotification);
    m_gainSlider.setValue(m_processor.getMakeupGain(), juce::dontSendNotification);
}

} // namespace iDAW
