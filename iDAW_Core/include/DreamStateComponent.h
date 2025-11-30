/**
 * DreamStateComponent.h - Side B UI Component for iDAW
 * 
 * The "Dream State" interface with:
 * - Blueprint look (Cyan background)
 * - Hybrid Layout with RotarySliders and TextEditor
 * - Ghost Hands listener for AI-driven knob updates
 * - OpenGL fragment shader for hand-drawn wobble effect
 * - CONFIRM button triggering call_iMIDI
 */

#pragma once

#include <JuceHeader.h>
#include "PythonBridge.h"
#include "MemoryManager.h"

namespace iDAW {

/**
 * Custom LookAndFeel for the Dream State "Blueprint" aesthetic
 */
class BlueprintLookAndFeel : public juce::LookAndFeel_V4 {
public:
    BlueprintLookAndFeel() {
        // Cyan/Blueprint color palette
        setColour(juce::ResizableWindow::backgroundColourId, juce::Colour(0xFF0A2540));  // Dark blueprint
        setColour(juce::Slider::thumbColourId, juce::Colour(0xFF00D4FF));  // Cyan highlight
        setColour(juce::Slider::rotarySliderFillColourId, juce::Colour(0xFF00D4FF));
        setColour(juce::Slider::rotarySliderOutlineColourId, juce::Colour(0xFF1A4A6E));
        setColour(juce::TextEditor::backgroundColourId, juce::Colour(0xFF0D3050));
        setColour(juce::TextEditor::textColourId, juce::Colour(0xFF00D4FF));
        setColour(juce::TextEditor::outlineColourId, juce::Colour(0xFF00D4FF));
        setColour(juce::TextButton::buttonColourId, juce::Colour(0xFF00D4FF));
        setColour(juce::TextButton::textColourOffId, juce::Colour(0xFF0A2540));
    }
    
    void drawRotarySlider(juce::Graphics& g, int x, int y, int width, int height,
                          float sliderPos, float rotaryStartAngle, float rotaryEndAngle,
                          juce::Slider& slider) override {
        auto outline = slider.findColour(juce::Slider::rotarySliderOutlineColourId);
        auto fill = slider.findColour(juce::Slider::rotarySliderFillColourId);
        
        auto bounds = juce::Rectangle<int>(x, y, width, height).toFloat().reduced(10);
        auto radius = juce::jmin(bounds.getWidth(), bounds.getHeight()) / 2.0f;
        auto toAngle = rotaryStartAngle + sliderPos * (rotaryEndAngle - rotaryStartAngle);
        auto lineW = 2.0f;
        auto arcRadius = radius - lineW * 0.5f;
        
        // Blueprint grid background
        g.setColour(outline.withAlpha(0.3f));
        for (float i = 0; i < bounds.getWidth(); i += 10) {
            g.drawLine(bounds.getX() + i, bounds.getY(), 
                      bounds.getX() + i, bounds.getBottom(), 0.5f);
        }
        for (float i = 0; i < bounds.getHeight(); i += 10) {
            g.drawLine(bounds.getX(), bounds.getY() + i,
                      bounds.getRight(), bounds.getY() + i, 0.5f);
        }
        
        // Background arc
        juce::Path backgroundArc;
        backgroundArc.addCentredArc(bounds.getCentreX(), bounds.getCentreY(),
                                     arcRadius, arcRadius, 0.0f,
                                     rotaryStartAngle, rotaryEndAngle, true);
        g.setColour(outline);
        g.strokePath(backgroundArc, juce::PathStrokeType(lineW, 
                     juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
        
        // Value arc (filled portion)
        if (slider.isEnabled()) {
            juce::Path valueArc;
            valueArc.addCentredArc(bounds.getCentreX(), bounds.getCentreY(),
                                   arcRadius, arcRadius, 0.0f,
                                   rotaryStartAngle, toAngle, true);
            g.setColour(fill);
            g.strokePath(valueArc, juce::PathStrokeType(lineW * 2, 
                         juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
        }
        
        // Center circle with "hand-drawn" effect (slight wobble)
        auto thumbWidth = lineW * 3.0f;
        juce::Point<float> thumbPoint(
            bounds.getCentreX() + arcRadius * 0.7f * std::cos(toAngle - juce::MathConstants<float>::halfPi),
            bounds.getCentreY() + arcRadius * 0.7f * std::sin(toAngle - juce::MathConstants<float>::halfPi)
        );
        
        g.setColour(fill);
        g.fillEllipse(juce::Rectangle<float>(thumbWidth, thumbWidth).withCentre(thumbPoint));
        
        // Center dot
        g.fillEllipse(juce::Rectangle<float>(thumbWidth * 1.5f, thumbWidth * 1.5f)
                      .withCentre(bounds.getCentre()));
    }
};

/**
 * Animated knob that supports "Ghost Hands" - AI-driven value changes
 * with scribble animation effect
 */
class GhostHandsSlider : public juce::Slider, private juce::Timer {
public:
    GhostHandsSlider() : juce::Slider(juce::Slider::RotaryHorizontalVerticalDrag,
                                       juce::Slider::TextBoxBelow) {
        setTextBoxStyle(juce::Slider::TextBoxBelow, false, 50, 15);
    }
    
    /**
     * Set value from AI with scribble animation
     */
    void setValueFromAI(double newValue) {
        m_targetValue = newValue;
        m_animating = true;
        m_animationPhase = 0.0f;
        m_startValue = getValue();
        startTimerHz(60);  // 60 FPS animation
    }
    
    bool isAnimating() const { return m_animating; }
    
private:
    void timerCallback() override {
        if (!m_animating) {
            stopTimer();
            return;
        }
        
        m_animationPhase += 0.05f;  // ~1 second animation
        
        if (m_animationPhase >= 1.0f) {
            // Animation complete
            setValue(m_targetValue, juce::sendNotificationAsync);
            m_animating = false;
            stopTimer();
            return;
        }
        
        // Scribble effect: oscillate around path to target
        float t = m_animationPhase;
        float scribble = std::sin(t * 20.0f) * (1.0f - t) * 0.1f;  // Decreasing oscillation
        float progress = t * t * (3.0f - 2.0f * t);  // Smoothstep
        
        double currentValue = m_startValue + (m_targetValue - m_startValue) * progress;
        currentValue += scribble * (m_targetValue - m_startValue);
        
        setValue(currentValue, juce::dontSendNotification);
        repaint();
    }
    
    bool m_animating = false;
    float m_animationPhase = 0.0f;
    double m_targetValue = 0.0;
    double m_startValue = 0.0;
};

/**
 * DreamStateComponent - The Side B UI with OpenGL shader overlay
 */
class DreamStateComponent : public juce::Component,
                            public juce::Button::Listener,
                            public juce::TextEditor::Listener,
                            private juce::Timer {
public:
    DreamStateComponent() {
        setLookAndFeel(&m_blueprintLookAndFeel);
        
        // Row 1: Grid, Gate, Swing
        addAndMakeVisible(m_gridSlider);
        m_gridSlider.setRange(4.0, 32.0, 1.0);
        m_gridSlider.setValue(16.0);
        m_gridSlider.setName("Grid");
        
        addAndMakeVisible(m_gridLabel);
        m_gridLabel.setText("GRID", juce::dontSendNotification);
        m_gridLabel.setJustificationType(juce::Justification::centred);
        m_gridLabel.setColour(juce::Label::textColourId, juce::Colour(0xFF00D4FF));
        
        addAndMakeVisible(m_gateSlider);
        m_gateSlider.setRange(0.1, 1.0, 0.01);
        m_gateSlider.setValue(0.75);
        m_gateSlider.setName("Gate");
        
        addAndMakeVisible(m_gateLabel);
        m_gateLabel.setText("GATE", juce::dontSendNotification);
        m_gateLabel.setJustificationType(juce::Justification::centred);
        m_gateLabel.setColour(juce::Label::textColourId, juce::Colour(0xFF00D4FF));
        
        addAndMakeVisible(m_swingSlider);
        m_swingSlider.setRange(0.5, 0.75, 0.01);
        m_swingSlider.setValue(0.5);
        m_swingSlider.setName("Swing");
        
        addAndMakeVisible(m_swingLabel);
        m_swingLabel.setText("SWING", juce::dontSendNotification);
        m_swingLabel.setJustificationType(juce::Justification::centred);
        m_swingLabel.setColour(juce::Label::textColourId, juce::Colour(0xFF00D4FF));
        
        // Row 2: Chaos, Complexity
        addAndMakeVisible(m_chaosSlider);
        m_chaosSlider.setRange(0.0, 1.0, 0.01);
        m_chaosSlider.setValue(0.5);
        m_chaosSlider.setName("Chaos");
        
        addAndMakeVisible(m_chaosLabel);
        m_chaosLabel.setText("CHAOS", juce::dontSendNotification);
        m_chaosLabel.setJustificationType(juce::Justification::centred);
        m_chaosLabel.setColour(juce::Label::textColourId, juce::Colour(0xFF00D4FF));
        
        addAndMakeVisible(m_complexitySlider);
        m_complexitySlider.setRange(0.0, 1.0, 0.01);
        m_complexitySlider.setValue(0.5);
        m_complexitySlider.setName("Complexity");
        
        addAndMakeVisible(m_complexityLabel);
        m_complexityLabel.setText("COMPLEXITY", juce::dontSendNotification);
        m_complexityLabel.setJustificationType(juce::Justification::centred);
        m_complexityLabel.setColour(juce::Label::textColourId, juce::Colour(0xFF00D4FF));
        
        // Row 3: Prompt Input
        addAndMakeVisible(m_promptInput);
        m_promptInput.setMultiLine(false);
        m_promptInput.setReturnKeyStartsNewLine(false);
        m_promptInput.setTextToShowWhenEmpty("Describe your music...", 
                                              juce::Colour(0xFF00D4FF).withAlpha(0.5f));
        m_promptInput.addListener(this);
        
        // CONFIRM button
        addAndMakeVisible(m_confirmButton);
        m_confirmButton.setButtonText("CONFIRM");
        m_confirmButton.addListener(this);
        
        // Status label
        addAndMakeVisible(m_statusLabel);
        m_statusLabel.setText("Ready", juce::dontSendNotification);
        m_statusLabel.setJustificationType(juce::Justification::centred);
        m_statusLabel.setColour(juce::Label::textColourId, juce::Colour(0xFF00D4FF).withAlpha(0.7f));
        
        // Register Ghost Hands callback with Python Bridge
        PythonBridge::getInstance().setGhostHandsCallback(
            [this](float chaos, float complexity) {
                // Must dispatch to message thread for UI updates
                juce::MessageManager::callAsync([this, chaos, complexity]() {
                    updateKnobsFromAI(chaos, complexity);
                });
            }
        );
        
        // Start wobble animation timer
        startTimerHz(30);
    }
    
    ~DreamStateComponent() override {
        setLookAndFeel(nullptr);
        stopTimer();
    }
    
    void paint(juce::Graphics& g) override {
        // Blueprint background
        g.fillAll(juce::Colour(0xFF0A2540));
        
        // Hand-drawn grid with wobble effect
        g.setColour(juce::Colour(0xFF1A4A6E));
        
        float wobbleTime = m_wobblePhase;
        float gridSpacing = 30.0f;
        
        // Vertical lines with wobble
        for (float x = 0; x < getWidth(); x += gridSpacing) {
            juce::Path linePath;
            linePath.startNewSubPath(x, 0);
            
            for (float y = 0; y < getHeight(); y += 5) {
                float wobble = std::sin(y * 0.02f + wobbleTime + x * 0.01f) * 2.0f;
                linePath.lineTo(x + wobble, y);
            }
            
            g.strokePath(linePath, juce::PathStrokeType(0.5f));
        }
        
        // Horizontal lines with wobble
        for (float y = 0; y < getHeight(); y += gridSpacing) {
            juce::Path linePath;
            linePath.startNewSubPath(0, y);
            
            for (float x = 0; x < getWidth(); x += 5) {
                float wobble = std::sin(x * 0.02f + wobbleTime + y * 0.01f) * 2.0f;
                linePath.lineTo(x, y + wobble);
            }
            
            g.strokePath(linePath, juce::PathStrokeType(0.5f));
        }
        
        // Title
        g.setColour(juce::Colour(0xFF00D4FF));
        g.setFont(juce::Font(24.0f, juce::Font::bold));
        g.drawText("DREAM STATE", getLocalBounds().removeFromTop(40), 
                   juce::Justification::centred);
    }
    
    void resized() override {
        auto area = getLocalBounds().reduced(20);
        area.removeFromTop(40);  // Title space
        
        int sliderSize = 80;
        int labelHeight = 20;
        int rowHeight = sliderSize + labelHeight + 10;
        
        // Row 1: Grid, Gate, Swing
        auto row1 = area.removeFromTop(rowHeight);
        int sliderSpacing = (row1.getWidth() - sliderSize * 3) / 4;
        
        auto gridArea = row1.removeFromLeft(sliderSpacing + sliderSize);
        gridArea.removeFromLeft(sliderSpacing);
        m_gridLabel.setBounds(gridArea.removeFromTop(labelHeight));
        m_gridSlider.setBounds(gridArea.removeFromTop(sliderSize));
        
        auto gateArea = row1.removeFromLeft(sliderSpacing + sliderSize);
        gateArea.removeFromLeft(sliderSpacing);
        m_gateLabel.setBounds(gateArea.removeFromTop(labelHeight));
        m_gateSlider.setBounds(gateArea.removeFromTop(sliderSize));
        
        auto swingArea = row1.removeFromLeft(sliderSpacing + sliderSize);
        swingArea.removeFromLeft(sliderSpacing);
        m_swingLabel.setBounds(swingArea.removeFromTop(labelHeight));
        m_swingSlider.setBounds(swingArea.removeFromTop(sliderSize));
        
        area.removeFromTop(10);  // Spacing
        
        // Row 2: Chaos, Complexity
        auto row2 = area.removeFromTop(rowHeight);
        int row2Spacing = (row2.getWidth() - sliderSize * 2) / 3;
        
        auto chaosArea = row2.removeFromLeft(row2Spacing + sliderSize);
        chaosArea.removeFromLeft(row2Spacing);
        m_chaosLabel.setBounds(chaosArea.removeFromTop(labelHeight));
        m_chaosSlider.setBounds(chaosArea.removeFromTop(sliderSize));
        
        auto complexityArea = row2.removeFromLeft(row2Spacing + sliderSize);
        complexityArea.removeFromLeft(row2Spacing);
        m_complexityLabel.setBounds(complexityArea.removeFromTop(labelHeight));
        m_complexitySlider.setBounds(complexityArea.removeFromTop(sliderSize));
        
        area.removeFromTop(20);  // Spacing
        
        // Row 3: Prompt Input
        m_promptInput.setBounds(area.removeFromTop(35));
        
        area.removeFromTop(10);  // Spacing
        
        // CONFIRM button
        auto buttonArea = area.removeFromTop(40);
        m_confirmButton.setBounds(buttonArea.withSizeKeepingCentre(150, 35));
        
        area.removeFromTop(10);  // Spacing
        
        // Status label
        m_statusLabel.setBounds(area.removeFromTop(20));
    }
    
    /**
     * Ghost Hands: Update knobs from AI suggestions
     */
    void updateKnobsFromAI(float chaos, float complexity) {
        m_chaosSlider.setValueFromAI(chaos);
        m_complexitySlider.setValueFromAI(complexity);
        
        m_statusLabel.setText("AI adjusted: Chaos=" + juce::String(chaos, 2) + 
                              ", Complexity=" + juce::String(complexity, 2),
                              juce::dontSendNotification);
    }
    
    // Button::Listener
    void buttonClicked(juce::Button* button) override {
        if (button == &m_confirmButton) {
            triggerMidiGeneration();
        }
    }
    
    // TextEditor::Listener
    void textEditorReturnKeyPressed(juce::TextEditor& editor) override {
        if (&editor == &m_promptInput) {
            triggerMidiGeneration();
        }
    }
    
    void textEditorTextChanged(juce::TextEditor&) override {}
    void textEditorEscapeKeyPressed(juce::TextEditor&) override {}
    void textEditorFocusLost(juce::TextEditor&) override {}
    
private:
    void timerCallback() override {
        m_wobblePhase += 0.05f;
        repaint();
    }
    
    void triggerMidiGeneration() {
        m_statusLabel.setText("Generating...", juce::dontSendNotification);
        
        // Gather knob state
        KnobState knobs;
        knobs.grid = static_cast<float>(m_gridSlider.getValue());
        knobs.gate = static_cast<float>(m_gateSlider.getValue());
        knobs.swing = static_cast<float>(m_swingSlider.getValue());
        knobs.chaos = static_cast<float>(m_chaosSlider.getValue());
        knobs.complexity = static_cast<float>(m_complexitySlider.getValue());
        
        // Get text prompt
        std::string prompt = m_promptInput.getText().toStdString();
        
        // Call Python asynchronously
        auto futureResult = PythonBridge::getInstance().call_iMIDI_async(knobs, prompt);
        
        // Process result when ready (simplified - real implementation would use proper async handling)
        std::thread([this, futureResult = std::move(futureResult)]() mutable {
            auto result = futureResult.get();
            
            juce::MessageManager::callAsync([this, result]() {
                if (result.success) {
                    m_statusLabel.setText("Generated " + juce::String(result.events.size()) + 
                                          " MIDI events (" + juce::String(result.genre) + ")",
                                          juce::dontSendNotification);
                    
                    // Push MIDI events to ring buffer for audio thread
                    auto& ringBuffer = MemoryManager::getInstance().getMidiBuffer();
                    for (const auto& event : result.events) {
                        ringBuffer.tryPush(event);
                    }
                } else {
                    m_statusLabel.setText("Error: " + juce::String(result.errorMessage),
                                          juce::dontSendNotification);
                }
            });
        }).detach();
    }
    
    // LookAndFeel
    BlueprintLookAndFeel m_blueprintLookAndFeel;
    
    // Row 1 controls
    GhostHandsSlider m_gridSlider;
    juce::Label m_gridLabel;
    GhostHandsSlider m_gateSlider;
    juce::Label m_gateLabel;
    GhostHandsSlider m_swingSlider;
    juce::Label m_swingLabel;
    
    // Row 2 controls
    GhostHandsSlider m_chaosSlider;
    juce::Label m_chaosLabel;
    GhostHandsSlider m_complexitySlider;
    juce::Label m_complexityLabel;
    
    // Row 3 controls
    juce::TextEditor m_promptInput;
    juce::TextButton m_confirmButton;
    juce::Label m_statusLabel;
    
    // Animation
    float m_wobblePhase = 0.0f;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(DreamStateComponent)
};

} // namespace iDAW
