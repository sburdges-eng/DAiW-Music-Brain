/**
 * EraserEditor.h - UI Component for Plugin 001: "The Eraser"
 * 
 * Side B visualization with:
 * - Spectral display showing FFT magnitudes
 * - Eraser cursor for frequency scrubbing
 * - Chalk Dust particle rendering
 * - AI threshold control
 */

#pragma once

#include <JuceHeader.h>
#include "EraserProcessor.h"

namespace iDAW {

/**
 * Spectral display component showing FFT magnitudes with eraser overlay
 */
class SpectralDisplay : public juce::Component, private juce::Timer {
public:
    SpectralDisplay(EraserProcessor& processor);
    ~SpectralDisplay() override;
    
    void paint(juce::Graphics& g) override;
    void resized() override;
    
    void mouseDown(const juce::MouseEvent& event) override;
    void mouseDrag(const juce::MouseEvent& event) override;
    void mouseUp(const juce::MouseEvent& event) override;
    
private:
    void timerCallback() override;
    void updateEraserFromMouse(const juce::MouseEvent& event);
    void drawSpectrum(juce::Graphics& g);
    void drawChalkDust(juce::Graphics& g);
    void drawEraserCursor(juce::Graphics& g);
    
    EraserProcessor& m_processor;
    
    std::vector<SpectralBinState> m_spectralData;
    std::vector<ChalkDustParticle> m_particles;
    
    bool m_isErasing = false;
    float m_eraserX = 0.0f;
    float m_eraserY = 0.0f;
    float m_eraserSize = 50.0f;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(SpectralDisplay)
};

/**
 * EraserEditor - Main editor component for The Eraser plugin
 */
class EraserEditor : public juce::AudioProcessorEditor,
                     public juce::Slider::Listener {
public:
    explicit EraserEditor(EraserProcessor& processor);
    ~EraserEditor() override;
    
    void paint(juce::Graphics& g) override;
    void resized() override;
    
    // Slider::Listener
    void sliderValueChanged(juce::Slider* slider) override;
    
private:
    EraserProcessor& m_processor;
    
    // Spectral display
    std::unique_ptr<SpectralDisplay> m_spectralDisplay;
    
    // Controls
    juce::Slider m_thresholdSlider;
    juce::Label m_thresholdLabel;
    
    juce::Slider m_eraserSizeSlider;
    juce::Label m_eraserSizeLabel;
    
    juce::TextButton m_clearButton;
    
    // Title
    juce::Label m_titleLabel;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(EraserEditor)
};

// ============================================================================
// Implementation
// ============================================================================

inline SpectralDisplay::SpectralDisplay(EraserProcessor& processor)
    : m_processor(processor)
{
    startTimerHz(30);  // 30 FPS refresh
}

inline SpectralDisplay::~SpectralDisplay() {
    stopTimer();
}

inline void SpectralDisplay::timerCallback() {
    m_spectralData = m_processor.getSpectralState();
    m_particles = m_processor.getChalkDustParticles();
    repaint();
}

inline void SpectralDisplay::paint(juce::Graphics& g) {
    // Background
    g.fillAll(juce::Colour(0xFF0A1520));
    
    // Draw spectrum
    drawSpectrum(g);
    
    // Draw chalk dust particles
    drawChalkDust(g);
    
    // Draw eraser cursor if active
    if (m_isErasing) {
        drawEraserCursor(g);
    }
    
    // Border
    g.setColour(juce::Colour(0xFF00D4FF));
    g.drawRect(getLocalBounds(), 1);
}

inline void SpectralDisplay::resized() {
    // Nothing specific needed
}

inline void SpectralDisplay::drawSpectrum(juce::Graphics& g) {
    if (m_spectralData.empty()) return;
    
    const float width = static_cast<float>(getWidth());
    const float height = static_cast<float>(getHeight());
    const int numBins = static_cast<int>(m_spectralData.size());
    
    juce::Path spectrumPath;
    spectrumPath.startNewSubPath(0, height);
    
    for (int i = 0; i < numBins; ++i) {
        float x = (static_cast<float>(i) / numBins) * width;
        float magnitude = m_spectralData[i].magnitude;
        float y = height - (magnitude * height * 0.9f);
        
        if (i == 0) {
            spectrumPath.lineTo(x, y);
        } else {
            spectrumPath.lineTo(x, y);
        }
    }
    
    spectrumPath.lineTo(width, height);
    spectrumPath.closeSubPath();
    
    // Fill with gradient
    juce::ColourGradient gradient(
        juce::Colour(0xFF00D4FF).withAlpha(0.6f), 0, height,
        juce::Colour(0xFF00D4FF).withAlpha(0.1f), 0, 0, false
    );
    g.setGradientFill(gradient);
    g.fillPath(spectrumPath);
    
    // Draw outline
    g.setColour(juce::Colour(0xFF00D4FF));
    g.strokePath(spectrumPath, juce::PathStrokeType(1.5f));
    
    // Draw erased regions
    for (int i = 0; i < numBins; ++i) {
        if (m_spectralData[i].erased) {
            float x = (static_cast<float>(i) / numBins) * width;
            float intensity = m_spectralData[i].eraserIntensity;
            
            g.setColour(juce::Colour(0xFFFF3366).withAlpha(intensity * 0.5f));
            g.drawLine(x, 0, x, height, 2.0f);
        }
    }
}

inline void SpectralDisplay::drawChalkDust(juce::Graphics& g) {
    for (const auto& particle : m_particles) {
        float x = particle.x * getWidth();
        float y = particle.y * getHeight();
        float size = particle.size;
        float alpha = particle.life * particle.brightness;
        
        // Chalk dust color (white/cyan mix)
        juce::Colour dustColor = juce::Colour(0xFFFFFFFF)
            .interpolatedWith(juce::Colour(0xFF00D4FF), 0.3f)
            .withAlpha(alpha);
        
        g.setColour(dustColor);
        g.fillEllipse(x - size/2, y - size/2, size, size);
        
        // Soft glow
        g.setColour(dustColor.withAlpha(alpha * 0.3f));
        g.fillEllipse(x - size, y - size, size * 2, size * 2);
    }
}

inline void SpectralDisplay::drawEraserCursor(juce::Graphics& g) {
    // Draw eraser cursor (circular brush)
    g.setColour(juce::Colour(0xFFFF6688).withAlpha(0.3f));
    g.fillEllipse(m_eraserX - m_eraserSize/2, m_eraserY - m_eraserSize/2,
                  m_eraserSize, m_eraserSize);
    
    g.setColour(juce::Colour(0xFFFF6688));
    g.drawEllipse(m_eraserX - m_eraserSize/2, m_eraserY - m_eraserSize/2,
                  m_eraserSize, m_eraserSize, 2.0f);
    
    // Crosshair
    g.setColour(juce::Colour(0xFFFF6688).withAlpha(0.5f));
    g.drawLine(m_eraserX, m_eraserY - m_eraserSize/4,
               m_eraserX, m_eraserY + m_eraserSize/4, 1.0f);
    g.drawLine(m_eraserX - m_eraserSize/4, m_eraserY,
               m_eraserX + m_eraserSize/4, m_eraserY, 1.0f);
}

inline void SpectralDisplay::mouseDown(const juce::MouseEvent& event) {
    m_isErasing = true;
    updateEraserFromMouse(event);
}

inline void SpectralDisplay::mouseDrag(const juce::MouseEvent& event) {
    if (m_isErasing) {
        updateEraserFromMouse(event);
    }
}

inline void SpectralDisplay::mouseUp(const juce::MouseEvent& /*event*/) {
    m_isErasing = false;
    m_processor.clearEraserCursor();
}

inline void SpectralDisplay::updateEraserFromMouse(const juce::MouseEvent& event) {
    m_eraserX = static_cast<float>(event.x);
    m_eraserY = static_cast<float>(event.y);
    
    // Convert X position to frequency
    float normalizedX = m_eraserX / static_cast<float>(getWidth());
    float frequencyHz = normalizedX * 22050.0f;  // Nyquist at 44.1kHz
    
    // Bandwidth based on eraser size
    float bandwidthHz = (m_eraserSize / getWidth()) * 22050.0f;
    
    // Intensity based on Y position (lower = stronger)
    float intensity = 1.0f - (m_eraserY / getHeight());
    intensity = std::clamp(intensity * 2.0f, 0.0f, 1.0f);
    
    m_processor.setEraserCursor(frequencyHz, bandwidthHz, intensity);
    
    repaint();
}

// ============================================================================
// EraserEditor Implementation
// ============================================================================

inline EraserEditor::EraserEditor(EraserProcessor& processor)
    : AudioProcessorEditor(&processor), m_processor(processor)
{
    setSize(600, 400);
    
    // Title
    addAndMakeVisible(m_titleLabel);
    m_titleLabel.setText("THE ERASER", juce::dontSendNotification);
    m_titleLabel.setFont(juce::Font(24.0f, juce::Font::bold));
    m_titleLabel.setColour(juce::Label::textColourId, juce::Colour(0xFF00D4FF));
    m_titleLabel.setJustificationType(juce::Justification::centred);
    
    // Spectral display
    m_spectralDisplay = std::make_unique<SpectralDisplay>(m_processor);
    addAndMakeVisible(m_spectralDisplay.get());
    
    // Threshold slider
    addAndMakeVisible(m_thresholdSlider);
    m_thresholdSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    m_thresholdSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 60, 20);
    m_thresholdSlider.setRange(-60.0, 0.0, 0.1);
    m_thresholdSlider.setValue(m_processor.getThreshold());
    m_thresholdSlider.setTextValueSuffix(" dB");
    m_thresholdSlider.addListener(this);
    
    addAndMakeVisible(m_thresholdLabel);
    m_thresholdLabel.setText("THRESHOLD", juce::dontSendNotification);
    m_thresholdLabel.setJustificationType(juce::Justification::centred);
    m_thresholdLabel.setColour(juce::Label::textColourId, juce::Colour(0xFF00D4FF));
    
    // Eraser size slider
    addAndMakeVisible(m_eraserSizeSlider);
    m_eraserSizeSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    m_eraserSizeSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 60, 20);
    m_eraserSizeSlider.setRange(10.0, 200.0, 1.0);
    m_eraserSizeSlider.setValue(50.0);
    m_eraserSizeSlider.setTextValueSuffix(" px");
    m_eraserSizeSlider.addListener(this);
    
    addAndMakeVisible(m_eraserSizeLabel);
    m_eraserSizeLabel.setText("SIZE", juce::dontSendNotification);
    m_eraserSizeLabel.setJustificationType(juce::Justification::centred);
    m_eraserSizeLabel.setColour(juce::Label::textColourId, juce::Colour(0xFF00D4FF));
    
    // Clear button
    addAndMakeVisible(m_clearButton);
    m_clearButton.setButtonText("CLEAR ALL");
    m_clearButton.onClick = [this]() {
        m_processor.clearErasedBins();
    };
}

inline EraserEditor::~EraserEditor() = default;

inline void EraserEditor::paint(juce::Graphics& g) {
    g.fillAll(juce::Colour(0xFF0A1A2A));
}

inline void EraserEditor::resized() {
    auto area = getLocalBounds().reduced(10);
    
    // Title at top
    m_titleLabel.setBounds(area.removeFromTop(40));
    
    // Controls at bottom
    auto controlsArea = area.removeFromBottom(100);
    int sliderWidth = 80;
    int spacing = 20;
    
    auto thresholdArea = controlsArea.removeFromLeft(sliderWidth);
    m_thresholdLabel.setBounds(thresholdArea.removeFromTop(20));
    m_thresholdSlider.setBounds(thresholdArea);
    
    controlsArea.removeFromLeft(spacing);
    
    auto sizeArea = controlsArea.removeFromLeft(sliderWidth);
    m_eraserSizeLabel.setBounds(sizeArea.removeFromTop(20));
    m_eraserSizeSlider.setBounds(sizeArea);
    
    controlsArea.removeFromLeft(spacing);
    
    m_clearButton.setBounds(controlsArea.removeFromLeft(100).withTrimmedTop(30));
    
    // Spectral display takes remaining space
    area.removeFromBottom(10);
    m_spectralDisplay->setBounds(area);
}

inline void EraserEditor::sliderValueChanged(juce::Slider* slider) {
    if (slider == &m_thresholdSlider) {
        m_processor.setThreshold(static_cast<float>(slider->getValue()));
    }
}

} // namespace iDAW
