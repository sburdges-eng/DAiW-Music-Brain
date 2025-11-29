#pragma once
/**
 * MainComponent.h - Dual-View Container State Machine
 *
 * DAiW Phase 1: The Foundation
 *
 * The MainComponent manages the flip between:
 * - Work State (Side A): Grey background, metal look
 * - Dream State (Side B): Blue background, blueprint look
 *
 * State transitions are tied to memory allocator switching:
 * - Work State uses Iron Heap (monotonic, no-free)
 * - Dream State uses Playground (dynamic, expandable)
 */

#include <JuceHeader.h>
#include "../Memory/MemoryManager.h"

namespace daiw {
namespace ui {

// Forward declarations
class WorkStateComponent;
class DreamStateComponent;

/**
 * ViewState - Current UI state enumeration
 */
enum class ViewState : uint8_t {
    Work = 0,   // Side A: Production, Iron Heap
    Dream = 1   // Side B: Creative, Playground
};

/**
 * MainComponent - Dual-view container with state machine
 *
 * Manages the visual flip between Work and Dream states,
 * coordinating with MemoryManager for allocator switching.
 *
 * Usage:
 *   MainComponent main;
 *   addAndMakeVisible(main);
 *   main.setDreamState(true);  // Flip to Dream
 *   main.triggerFlip();        // Toggle state
 */
class MainComponent : public juce::Component {
public:
    MainComponent();
    ~MainComponent() override;

    // State machine
    [[nodiscard]] bool isDreamState() const noexcept { return m_isDreamState; }
    [[nodiscard]] ViewState getViewState() const noexcept {
        return m_isDreamState ? ViewState::Dream : ViewState::Work;
    }

    /**
     * Set the dream state directly
     *
     * @param dream True for Dream state, false for Work state
     */
    void setDreamState(bool dream);

    /**
     * Toggle between Work and Dream states
     */
    void triggerFlip();

    /**
     * Get the current memory side being used
     */
    [[nodiscard]] memory::SideID getCurrentSide() const noexcept {
        return m_isDreamState ? memory::SideID::Playground : memory::SideID::IronHeap;
    }

    // Listener interface for state changes
    class Listener {
    public:
        virtual ~Listener() = default;
        virtual void viewStateChanged(ViewState newState) = 0;
    };

    void addListener(Listener* listener);
    void removeListener(Listener* listener);

    // Component overrides
    void paint(juce::Graphics& g) override;
    void resized() override;

private:
    void updateVisibleComponent();
    void notifyListeners();

    // State
    bool m_isDreamState{false};

    // Child components
    std::unique_ptr<WorkStateComponent> m_workComponent;
    std::unique_ptr<DreamStateComponent> m_dreamComponent;

    // Current visible component pointer (for convenience)
    juce::Component* m_currentComponent{nullptr};

    // Listeners
    juce::ListenerList<Listener> m_listeners;

    // Animation (for smooth flip)
    juce::ComponentAnimator m_animator;
    bool m_isAnimating{false};

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MainComponent)
};

} // namespace ui
} // namespace daiw
