/**
 * PencilEditor.h - UI Component for Plugin 002: "The Pencil"
 * 
 * Profile: 'Graphite' (Tube Saturation / Additive EQ)
 * 
 * Side B visualization with:
 * - 3-band drive/mix controls
 * - Visual feedback showing graphite intensity
 * - Ghost Hands warmth indicator
 */

#pragma once

#include <JuceHeader.h>
#include "PencilProcessor.h"

namespace iDAW {

/**
 * Graphite visualization component showing pencil stroke intensity
 */
class GraphiteDisplay : public juce::Component, private juce::Timer {
public:
    GraphiteDisplay(PencilProcessor& processor);
    ~GraphiteDisplay() override;
    
    void paint(juce::Graphics& g) override;
    void resized() override;
    
private:
    void timerCallback() override;
    void drawPaperTexture(juce::Graphics& g, juce::Rectangle<float> bounds);
    void drawPencilStrokes(juce::Graphics& g, juce::Rectangle<float> bounds);
    void drawBandMeters(juce::Graphics& g, juce::Rectangle<float> bounds);
    
    PencilProcessor& m_processor;
    GraphiteVisualState m_visualState;
    
    // Animation
    float m_time = 0.0f;
    
    // Pseudo-random for texture
    juce::Random m_random;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(GraphiteDisplay)
};

/**
 * Band control strip with drive and mix knobs
 */
class BandControlStrip : public juce::Component,
                          public juce::Slider::Listener {
public:
    BandControlStrip(const juce::String& bandName, juce::Colour bandColor);
    
    void resized() override;
    void paint(juce::Graphics& g) override;
    
    void sliderValueChanged(juce::Slider* slider) override;
    
    void setDrive(float drive);
    float getDrive() const;
    
    void setMix(float mix);
    float getMix() const;
    
    std::function<void(float drive, float mix)> onParametersChanged;
    
private:
    juce::String m_bandName;
    juce::Colour m_bandColor;
    
    juce::Slider m_driveSlider;
    juce::Label m_driveLabel;
    
    juce::Slider m_mixSlider;
    juce::Label m_mixLabel;
    
    juce::Label m_bandLabel;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(BandControlStrip)
};

/**
 * PencilEditor - Main editor component for The Pencil plugin
 */
class PencilEditor : public juce::AudioProcessorEditor,
                     public juce::Slider::Listener,
                     public juce::Button::Listener {
public:
    explicit PencilEditor(PencilProcessor& processor);
    ~PencilEditor() override;
    
    void paint(juce::Graphics& g) override;
    void resized() override;
    
    void sliderValueChanged(juce::Slider* slider) override;
    void buttonClicked(juce::Button* button) override;
    
private:
    void updateBandFromStrip(int bandIndex, float drive, float mix);
    
    PencilProcessor& m_processor;
    
    // Graphite display
    std::unique_ptr<GraphiteDisplay> m_graphiteDisplay;
    
    // Band controls
    std::array<std::unique_ptr<BandControlStrip>, 3> m_bandStrips;
    
    // Output gain
    juce::Slider m_outputSlider;
    juce::Label m_outputLabel;
    
    // Warmth (Ghost Hands) control
    juce::Slider m_warmthSlider;
    juce::Label m_warmthLabel;
    juce::TextButton m_aiWarmthButton;
    
    // Title
    juce::Label m_titleLabel;
    
    // Colors
    static constexpr juce::uint32 LOW_COLOR = 0xFFE57373;   // Red-ish
    static constexpr juce::uint32 MID_COLOR = 0xFF81C784;   // Green-ish
    static constexpr juce::uint32 HIGH_COLOR = 0xFF64B5F6;  // Blue-ish
    static constexpr juce::uint32 BG_COLOR = 0xFF2A2A2A;    // Dark grey
    static constexpr juce::uint32 GRAPHITE_COLOR = 0xFF404040;  // Graphite
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(PencilEditor)
};

// ============================================================================
// GraphiteDisplay Implementation
// ============================================================================

inline GraphiteDisplay::GraphiteDisplay(PencilProcessor& processor)
    : m_processor(processor)
{
    startTimerHz(30);
}

inline GraphiteDisplay::~GraphiteDisplay() {
    stopTimer();
}

inline void GraphiteDisplay::timerCallback() {
    m_visualState = m_processor.getVisualState();
    m_time += 0.033f;  // ~30 FPS
    repaint();
}

inline void GraphiteDisplay::paint(juce::Graphics& g) {
    auto bounds = getLocalBounds().toFloat();
    
    // Paper texture background
    drawPaperTexture(g, bounds);
    
    // Pencil strokes based on activity
    drawPencilStrokes(g, bounds);
    
    // Band level meters
    drawBandMeters(g, bounds);
    
    // Border
    g.setColour(juce::Colour(0xFF606060));
    g.drawRect(bounds, 1.0f);
}

inline void GraphiteDisplay::resized() {}

inline void GraphiteDisplay::drawPaperTexture(juce::Graphics& g, juce::Rectangle<float> bounds) {
    // Cream/off-white paper color
    g.setColour(juce::Colour(0xFFF5F0E6));
    g.fillRect(bounds);
    
    // Add subtle paper grain
    m_random.setSeed(42);
    g.setColour(juce::Colour(0x08000000));  // Very transparent black
    
    for (int i = 0; i < 200; ++i) {
        float x = m_random.nextFloat() * bounds.getWidth();
        float y = m_random.nextFloat() * bounds.getHeight();
        float size = m_random.nextFloat() * 2.0f + 0.5f;
        g.fillEllipse(x, y, size, size);
    }
}

inline void GraphiteDisplay::drawPencilStrokes(juce::Graphics& g, juce::Rectangle<float> bounds) {
    // Draw graphite strokes based on visual state
    float thickness = m_visualState.lineThickness;
    float noise = m_visualState.lineNoise;
    
    // Graphite color (darker with more drive)
    juce::uint8 graphiteIntensity = static_cast<juce::uint8>(60 - noise * 30);
    juce::Colour graphiteColor(graphiteIntensity, graphiteIntensity, graphiteIntensity);
    
    m_random.setSeed(static_cast<juce::int64>(m_time * 1000) % 10000);
    
    // Draw horizontal strokes
    int numStrokes = static_cast<int>(5 + m_visualState.overallDrive * 10);
    
    for (int i = 0; i < numStrokes; ++i) {
        float y = bounds.getY() + m_random.nextFloat() * bounds.getHeight();
        float startX = bounds.getX();
        float endX = bounds.getRight();
        
        // Stroke path with slight waviness
        juce::Path strokePath;
        strokePath.startNewSubPath(startX, y);
        
        float currentX = startX;
        while (currentX < endX) {
            float step = 5.0f + m_random.nextFloat() * 10.0f;
            currentX += step;
            
            // Add noise-based displacement
            float yOffset = (m_random.nextFloat() - 0.5f) * noise * 10.0f;
            strokePath.lineTo(std::min(currentX, endX), y + yOffset);
        }
        
        // Draw with variable opacity based on drive
        float alpha = 0.1f + m_visualState.overallDrive * 0.05f;
        g.setColour(graphiteColor.withAlpha(alpha));
        g.strokePath(strokePath, juce::PathStrokeType(thickness * 0.5f));
    }
}

inline void GraphiteDisplay::drawBandMeters(juce::Graphics& g, juce::Rectangle<float> bounds) {
    const float meterWidth = bounds.getWidth() / 5.0f;
    const float meterGap = meterWidth * 0.2f;
    const float meterHeight = bounds.getHeight() * 0.6f;
    const float meterY = bounds.getHeight() * 0.2f;
    
    std::array<juce::Colour, 3> colors = {
        juce::Colour(0xFFE57373),  // Low - Red
        juce::Colour(0xFF81C784),  // Mid - Green
        juce::Colour(0xFF64B5F6)   // High - Blue
    };
    
    for (int i = 0; i < 3; ++i) {
        float x = bounds.getX() + meterWidth * (i + 1) + meterGap * (i + 1);
        float level = m_visualState.bandLevels[i];
        
        // Background
        g.setColour(juce::Colour(0x20000000));
        g.fillRect(x, meterY, meterWidth - meterGap, meterHeight);
        
        // Level fill
        float fillHeight = level * meterHeight;
        g.setColour(colors[i].withAlpha(0.8f));
        g.fillRect(x, meterY + meterHeight - fillHeight, 
                   meterWidth - meterGap, fillHeight);
        
        // Graphite overlay effect
        if (m_visualState.lineNoise > 0.3f) {
            m_random.setSeed(i * 100 + static_cast<juce::int64>(m_time * 100));
            g.setColour(juce::Colour(0x30303030));
            
            for (int j = 0; j < 10; ++j) {
                float lineY = meterY + m_random.nextFloat() * fillHeight;
                if (lineY > meterY + meterHeight - fillHeight) continue;
                
                g.drawLine(x, meterY + meterHeight - lineY,
                           x + meterWidth - meterGap, meterY + meterHeight - lineY,
                           m_visualState.lineThickness * 0.3f);
            }
        }
    }
}

// ============================================================================
// BandControlStrip Implementation
// ============================================================================

inline BandControlStrip::BandControlStrip(const juce::String& bandName, juce::Colour bandColor)
    : m_bandName(bandName), m_bandColor(bandColor)
{
    // Band label
    addAndMakeVisible(m_bandLabel);
    m_bandLabel.setText(bandName, juce::dontSendNotification);
    m_bandLabel.setFont(juce::Font(14.0f, juce::Font::bold));
    m_bandLabel.setColour(juce::Label::textColourId, bandColor);
    m_bandLabel.setJustificationType(juce::Justification::centred);
    
    // Drive slider
    addAndMakeVisible(m_driveSlider);
    m_driveSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    m_driveSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 50, 15);
    m_driveSlider.setRange(1.0, 10.0, 0.1);
    m_driveSlider.setValue(1.0);
    m_driveSlider.addListener(this);
    
    addAndMakeVisible(m_driveLabel);
    m_driveLabel.setText("DRIVE", juce::dontSendNotification);
    m_driveLabel.setJustificationType(juce::Justification::centred);
    m_driveLabel.setColour(juce::Label::textColourId, juce::Colours::white);
    
    // Mix slider
    addAndMakeVisible(m_mixSlider);
    m_mixSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    m_mixSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 50, 15);
    m_mixSlider.setRange(0.0, 1.0, 0.01);
    m_mixSlider.setValue(0.5);
    m_mixSlider.addListener(this);
    
    addAndMakeVisible(m_mixLabel);
    m_mixLabel.setText("MIX", juce::dontSendNotification);
    m_mixLabel.setJustificationType(juce::Justification::centred);
    m_mixLabel.setColour(juce::Label::textColourId, juce::Colours::white);
}

inline void BandControlStrip::resized() {
    auto area = getLocalBounds().reduced(5);
    
    m_bandLabel.setBounds(area.removeFromTop(20));
    
    auto controlsArea = area;
    int sliderHeight = (controlsArea.getHeight() - 40) / 2;
    
    m_driveLabel.setBounds(controlsArea.removeFromTop(15));
    m_driveSlider.setBounds(controlsArea.removeFromTop(sliderHeight));
    
    controlsArea.removeFromTop(5);
    
    m_mixLabel.setBounds(controlsArea.removeFromTop(15));
    m_mixSlider.setBounds(controlsArea.removeFromTop(sliderHeight));
}

inline void BandControlStrip::paint(juce::Graphics& g) {
    g.setColour(m_bandColor.withAlpha(0.1f));
    g.fillRoundedRectangle(getLocalBounds().toFloat(), 5.0f);
    
    g.setColour(m_bandColor.withAlpha(0.3f));
    g.drawRoundedRectangle(getLocalBounds().toFloat().reduced(1), 5.0f, 1.0f);
}

inline void BandControlStrip::sliderValueChanged(juce::Slider*) {
    if (onParametersChanged) {
        onParametersChanged(static_cast<float>(m_driveSlider.getValue()),
                            static_cast<float>(m_mixSlider.getValue()));
    }
}

inline void BandControlStrip::setDrive(float drive) {
    m_driveSlider.setValue(drive, juce::dontSendNotification);
}

inline float BandControlStrip::getDrive() const {
    return static_cast<float>(m_driveSlider.getValue());
}

inline void BandControlStrip::setMix(float mix) {
    m_mixSlider.setValue(mix, juce::dontSendNotification);
}

inline float BandControlStrip::getMix() const {
    return static_cast<float>(m_mixSlider.getValue());
}

// ============================================================================
// PencilEditor Implementation
// ============================================================================

inline PencilEditor::PencilEditor(PencilProcessor& processor)
    : AudioProcessorEditor(&processor), m_processor(processor)
{
    setSize(500, 450);
    
    // Title
    addAndMakeVisible(m_titleLabel);
    m_titleLabel.setText("THE PENCIL", juce::dontSendNotification);
    m_titleLabel.setFont(juce::Font(24.0f, juce::Font::bold));
    m_titleLabel.setColour(juce::Label::textColourId, juce::Colour(0xFFE0E0E0));
    m_titleLabel.setJustificationType(juce::Justification::centred);
    
    // Graphite display
    m_graphiteDisplay = std::make_unique<GraphiteDisplay>(m_processor);
    addAndMakeVisible(m_graphiteDisplay.get());
    
    // Band control strips
    std::array<juce::Colour, 3> bandColors = {
        juce::Colour(LOW_COLOR),
        juce::Colour(MID_COLOR),
        juce::Colour(HIGH_COLOR)
    };
    std::array<juce::String, 3> bandNames = { "LOW", "MID", "HIGH" };
    
    for (int i = 0; i < 3; ++i) {
        m_bandStrips[i] = std::make_unique<BandControlStrip>(bandNames[i], bandColors[i]);
        addAndMakeVisible(m_bandStrips[i].get());
        
        // Connect callback
        int bandIndex = i;
        m_bandStrips[i]->onParametersChanged = [this, bandIndex](float drive, float mix) {
            updateBandFromStrip(bandIndex, drive, mix);
        };
        
        // Set initial values
        auto params = m_processor.getBandParameters(i);
        m_bandStrips[i]->setDrive(params.drive);
        m_bandStrips[i]->setMix(params.mix);
    }
    
    // Warmth slider (Ghost Hands)
    addAndMakeVisible(m_warmthSlider);
    m_warmthSlider.setSliderStyle(juce::Slider::LinearHorizontal);
    m_warmthSlider.setTextBoxStyle(juce::Slider::TextBoxRight, false, 40, 20);
    m_warmthSlider.setRange(0.0, 1.0, 0.01);
    m_warmthSlider.setValue(0.0);
    m_warmthSlider.addListener(this);
    
    addAndMakeVisible(m_warmthLabel);
    m_warmthLabel.setText("WARMTH", juce::dontSendNotification);
    m_warmthLabel.setColour(juce::Label::textColourId, juce::Colour(0xFFFFB74D));
    
    addAndMakeVisible(m_aiWarmthButton);
    m_aiWarmthButton.setButtonText("AI");
    m_aiWarmthButton.addListener(this);
    m_aiWarmthButton.setColour(juce::TextButton::buttonColourId, juce::Colour(0xFF7E57C2));
    
    // Output gain
    addAndMakeVisible(m_outputSlider);
    m_outputSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    m_outputSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 50, 20);
    m_outputSlider.setRange(-12.0, 12.0, 0.1);
    m_outputSlider.setValue(m_processor.getOutputGain());
    m_outputSlider.setTextValueSuffix(" dB");
    m_outputSlider.addListener(this);
    
    addAndMakeVisible(m_outputLabel);
    m_outputLabel.setText("OUTPUT", juce::dontSendNotification);
    m_outputLabel.setJustificationType(juce::Justification::centred);
    m_outputLabel.setColour(juce::Label::textColourId, juce::Colours::white);
}

inline PencilEditor::~PencilEditor() = default;

inline void PencilEditor::paint(juce::Graphics& g) {
    g.fillAll(juce::Colour(BG_COLOR));
}

inline void PencilEditor::resized() {
    auto area = getLocalBounds().reduced(10);
    
    // Title
    m_titleLabel.setBounds(area.removeFromTop(35));
    area.removeFromTop(5);
    
    // Graphite display (top section)
    m_graphiteDisplay->setBounds(area.removeFromTop(120));
    area.removeFromTop(10);
    
    // Band strips (middle section)
    auto bandsArea = area.removeFromTop(180);
    int stripWidth = bandsArea.getWidth() / 3 - 5;
    
    for (int i = 0; i < 3; ++i) {
        auto stripArea = bandsArea.removeFromLeft(stripWidth);
        if (i < 2) bandsArea.removeFromLeft(8);  // Gap
        m_bandStrips[i]->setBounds(stripArea);
    }
    
    area.removeFromTop(10);
    
    // Bottom controls
    auto bottomArea = area.removeFromTop(50);
    
    // Warmth controls
    auto warmthArea = bottomArea.removeFromLeft(bottomArea.getWidth() * 0.6f);
    m_warmthLabel.setBounds(warmthArea.removeFromLeft(70));
    m_aiWarmthButton.setBounds(warmthArea.removeFromRight(40).reduced(0, 10));
    m_warmthSlider.setBounds(warmthArea);
    
    // Output gain
    auto outputArea = bottomArea;
    m_outputLabel.setBounds(outputArea.removeFromTop(15));
    m_outputSlider.setBounds(outputArea);
}

inline void PencilEditor::sliderValueChanged(juce::Slider* slider) {
    if (slider == &m_warmthSlider) {
        m_processor.applyWarmthFromAI(static_cast<float>(slider->getValue()));
        
        // Update band strips to reflect changes
        for (int i = 0; i < 3; ++i) {
            auto params = m_processor.getBandParameters(i);
            m_bandStrips[i]->setDrive(params.drive);
            m_bandStrips[i]->setMix(params.mix);
        }
    }
    else if (slider == &m_outputSlider) {
        m_processor.setOutputGain(static_cast<float>(slider->getValue()));
    }
}

inline void PencilEditor::buttonClicked(juce::Button* button) {
    if (button == &m_aiWarmthButton) {
        // Simulate AI suggesting warmth
        m_warmthSlider.setValue(0.7, juce::sendNotificationAsync);
    }
}

inline void PencilEditor::updateBandFromStrip(int bandIndex, float drive, float mix) {
    m_processor.setBandDrive(bandIndex, drive);
    m_processor.setBandMix(bandIndex, mix);
}

} // namespace iDAW
