#pragma once
/**
 * WorkStateComponent.h - Work State UI (Side A)
 *
 * DAiW Phase 1: The Foundation
 *
 * Work State characteristics:
 * - Grey background with brushed metal aesthetic
 * - Uses Iron Heap allocator (monotonic, no-free)
 * - Production-focused, stable UI
 * - LookAndFeel_Metal styling
 */

#include <JuceHeader.h>

namespace daiw {
namespace ui {

/**
 * WorkStateComponent - Production-focused UI panel
 *
 * This component represents the "Work" state of the DAiW interface,
 * designed for stable audio production work.
 */
class WorkStateComponent : public juce::Component {
public:
    WorkStateComponent();
    ~WorkStateComponent() override;

    // Component overrides
    void paint(juce::Graphics& g) override;
    void resized() override;

    // Access test controls (for development)
    juce::Slider& getTestSlider() { return m_testSlider; }
    juce::TextButton& getFlipButton() { return m_flipButton; }

    // Callback for flip button
    std::function<void()> onFlipRequested;

private:
    // Background color
    static constexpr uint32_t BACKGROUND_COLOR = 0xff3d3d3d;  // Dark grey

    // Test UI elements (will be replaced with actual controls)
    juce::Slider m_testSlider;
    juce::Label m_titleLabel;
    juce::TextButton m_flipButton;

    // State indicator
    juce::Label m_stateLabel;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(WorkStateComponent)
};

} // namespace ui
} // namespace daiw
