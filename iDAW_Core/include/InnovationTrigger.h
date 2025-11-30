/**
 * InnovationTrigger.h - iDAW v1.1 Innovation Logic
 *
 * Implements the "Rule Break" suggestion system:
 * - Tracks user rejections of AI suggestions
 * - After THRESHOLD rejections, suggests breaking conventional rules
 * - Deploys "Ghost Track" with experimental variations
 *
 * Philosophy: "If they keep saying no, maybe we're not being brave enough."
 */

#pragma once

#include <JuceHeader.h>
#include <atomic>
#include <functional>
#include <string>
#include <vector>
#include <random>

namespace iDAW {

/**
 * User action types for feedback processing
 */
enum class UserAction {
    ACCEPT,         // User accepted the suggestion
    REJECT,         // User rejected the suggestion
    TWEAK_PARAM,    // User manually adjusted parameters
    FLIP_VIEW,      // User switched between Side A/B
    UNDO,           // User hit undo
    CONFIRM         // User confirmed final output
};

/**
 * Rule breaking categories (from DAiW philosophy)
 */
enum class RuleBreakCategory {
    HARMONY,        // Break harmonic conventions
    RHYTHM,         // Break rhythmic expectations
    ARRANGEMENT,    // Break arrangement norms
    PRODUCTION,     // Break production "rules"
    NONE
};

/**
 * Suggested rule breaks
 */
struct RuleBreakSuggestion {
    RuleBreakCategory category;
    std::string ruleName;
    std::string description;
    std::string emotionalJustification;
    float intensity;  // 0.0 - 1.0, how extreme the break
};

/**
 * Ghost Track configuration
 */
struct GhostTrackConfig {
    bool enabled = false;
    float chaosLevel = 0.5f;
    float complexityLevel = 0.5f;
    RuleBreakSuggestion activeRuleBreak;
    std::vector<int> affectedBars;
};

/**
 * Innovation Trigger - Core Logic
 *
 * From v0.3.x specifications:
 * - rejectionCounter tracks consecutive rejections
 * - THRESHOLD = 3 (Revision C)
 * - When threshold reached, deployGhostTrack()
 */
class InnovationTrigger {
public:
    // Configuration
    static constexpr int REJECTION_THRESHOLD = 3;  // v0.3.1 Revision C
    static constexpr int MAX_GHOST_TRACKS = 4;
    static constexpr float MIN_CHAOS_BOOST = 0.1f;
    static constexpr float MAX_CHAOS_BOOST = 0.4f;

    using GhostTrackCallback = std::function<void(const GhostTrackConfig&)>;
    using RuleBreakCallback = std::function<void(const RuleBreakSuggestion&)>;

    InnovationTrigger()
        : m_rejectionCounter(0)
        , m_totalRejections(0)
        , m_totalAccepts(0)
        , m_ghostTracksDeployed(0)
        , m_currentChaosBoost(0.0f)
    {
        initializeRuleBreaks();
    }

    /**
     * Process user feedback on AI suggestions
     *
     * From v0.3.x spec:
     * - REJECT increments counter
     * - TWEAK_PARAM resets counter (v0.3.2.1: The Refinement Loop)
     * - ACCEPT resets counter
     * - When counter >= THRESHOLD, deploy Ghost Track
     */
    void processFeedback(UserAction action, const std::string& context = "") {
        switch (action) {
            case UserAction::REJECT:
                m_rejectionCounter++;
                m_totalRejections++;
                m_lastContext = context;

                // Check if we've hit the innovation threshold
                if (m_rejectionCounter >= REJECTION_THRESHOLD) {
                    triggerInnovation();
                }
                break;

            case UserAction::ACCEPT:
                // User accepted - reset counter, record success
                m_rejectionCounter = 0;
                m_totalAccepts++;
                m_currentChaosBoost = 0.0f;  // Reset chaos boost
                break;

            case UserAction::TWEAK_PARAM:
                // v0.3.2.1: The Refinement Loop
                // User is engaging with parameters - they're close to what they want
                m_rejectionCounter = 0;
                // Don't reset chaos boost - they might be refining the innovation
                break;

            case UserAction::FLIP_VIEW:
                // Switching views doesn't affect rejection counter
                break;

            case UserAction::UNDO:
                // Undo is a soft rejection
                if (m_rejectionCounter > 0) {
                    m_rejectionCounter--;
                }
                break;

            case UserAction::CONFIRM:
                // Final confirmation - full reset
                m_rejectionCounter = 0;
                m_currentChaosBoost = 0.0f;
                break;
        }
    }

    /**
     * Get current rejection count
     */
    int getRejectionCount() const noexcept {
        return m_rejectionCounter;
    }

    /**
     * Get distance to innovation trigger (0 = triggered)
     */
    int getDistanceToInnovation() const noexcept {
        return std::max(0, REJECTION_THRESHOLD - m_rejectionCounter);
    }

    /**
     * Check if innovation mode is active
     */
    bool isInnovationModeActive() const noexcept {
        return m_rejectionCounter >= REJECTION_THRESHOLD;
    }

    /**
     * Get current chaos boost (applied to AI suggestions)
     */
    float getChaosBoost() const noexcept {
        return m_currentChaosBoost;
    }

    /**
     * Get suggested rule break based on context
     */
    RuleBreakSuggestion getSuggestedRuleBreak() const {
        if (m_ruleBreaks.empty()) {
            return RuleBreakSuggestion{RuleBreakCategory::NONE, "", "", "", 0.0f};
        }

        // Select based on rejection pattern and randomness
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(0, static_cast<int>(m_ruleBreaks.size()) - 1);

        return m_ruleBreaks[dis(gen)];
    }

    /**
     * Set callback for ghost track deployment
     */
    void setGhostTrackCallback(GhostTrackCallback callback) {
        m_ghostTrackCallback = std::move(callback);
    }

    /**
     * Set callback for rule break suggestions
     */
    void setRuleBreakCallback(RuleBreakCallback callback) {
        m_ruleBreakCallback = std::move(callback);
    }

    /**
     * Get statistics
     */
    struct Stats {
        int totalRejections;
        int totalAccepts;
        int ghostTracksDeployed;
        float acceptanceRate;
    };

    Stats getStats() const {
        int total = m_totalRejections + m_totalAccepts;
        float rate = total > 0 ? static_cast<float>(m_totalAccepts) / total : 0.0f;
        return Stats{m_totalRejections, m_totalAccepts, m_ghostTracksDeployed, rate};
    }

    /**
     * Reset all counters
     */
    void reset() {
        m_rejectionCounter = 0;
        m_totalRejections = 0;
        m_totalAccepts = 0;
        m_ghostTracksDeployed = 0;
        m_currentChaosBoost = 0.0f;
        m_lastContext.clear();
    }

private:
    /**
     * Trigger innovation mode - deploy Ghost Track
     * v0.3.3 specification
     */
    void triggerInnovation() {
        // Calculate chaos boost based on rejection intensity
        m_currentChaosBoost = std::min(
            MAX_CHAOS_BOOST,
            MIN_CHAOS_BOOST * static_cast<float>(m_rejectionCounter)
        );

        // Get a rule break suggestion
        RuleBreakSuggestion suggestion = getSuggestedRuleBreak();

        // Configure ghost track
        GhostTrackConfig ghostConfig;
        ghostConfig.enabled = true;
        ghostConfig.chaosLevel = 0.5f + m_currentChaosBoost;
        ghostConfig.complexityLevel = 0.5f + (m_currentChaosBoost * 0.5f);
        ghostConfig.activeRuleBreak = suggestion;

        // Notify callbacks
        if (m_ruleBreakCallback) {
            m_ruleBreakCallback(suggestion);
        }

        if (m_ghostTrackCallback) {
            m_ghostTrackCallback(ghostConfig);
        }

        m_ghostTracksDeployed++;

        // Partial reset - give them a chance with the new suggestion
        m_rejectionCounter = 1;  // Not full reset, they might reject this too
    }

    /**
     * Initialize rule break suggestions
     * Based on DAiW philosophy
     */
    void initializeRuleBreaks() {
        m_ruleBreaks = {
            // Harmony rule breaks
            {RuleBreakCategory::HARMONY, "AvoidTonicResolution",
             "End on the V or IV chord instead of I",
             "Unresolved yearning - the story isn't finished",
             0.6f},

            {RuleBreakCategory::HARMONY, "ModalInterchange",
             "Borrow chords from parallel minor/major",
             "Bittersweet complexity - light and shadow together",
             0.5f},

            {RuleBreakCategory::HARMONY, "TritoneSubstitution",
             "Replace V7 with bII7",
             "Jazz sophistication - unexpected resolution",
             0.7f},

            // Rhythm rule breaks
            {RuleBreakCategory::RHYTHM, "ConstantDisplacement",
             "Shift all accents by an eighth note",
             "Anxiety, restlessness - something's off",
             0.6f},

            {RuleBreakCategory::RHYTHM, "TempoFluctuation",
             "Allow 2-5 BPM drift within phrases",
             "Human breathing - organic, alive",
             0.4f},

            {RuleBreakCategory::RHYTHM, "PolyrhythmicLayer",
             "Add a 3-against-4 ghost percussion",
             "Complexity beneath simplicity",
             0.5f},

            // Arrangement rule breaks
            {RuleBreakCategory::ARRANGEMENT, "BuriedVocals",
             "Push lead vocal 3dB below instruments",
             "Dissociation - voice lost in the noise",
             0.7f},

            {RuleBreakCategory::ARRANGEMENT, "ExtremeDynamicRange",
             "Whisper verses, scream choruses",
             "Emotional whiplash - can't stay numb",
             0.8f},

            {RuleBreakCategory::ARRANGEMENT, "InstrumentSwap",
             "Replace expected instrument with opposite",
             "Subverted expectations - nothing is what it seems",
             0.5f},

            // Production rule breaks
            {RuleBreakCategory::PRODUCTION, "PitchImperfection",
             "Leave vocals slightly off-pitch",
             "Emotional honesty - perfection is a lie",
             0.6f},

            {RuleBreakCategory::PRODUCTION, "ExcessiveMud",
             "Allow low-mid buildup in emotional peaks",
             "Claustrophobia - walls closing in",
             0.5f},

            {RuleBreakCategory::PRODUCTION, "ClippingAsTexture",
             "Intentional soft clipping on drums",
             "Aggression breaking through",
             0.7f}
        };
    }

    // State
    int m_rejectionCounter;
    int m_totalRejections;
    int m_totalAccepts;
    int m_ghostTracksDeployed;
    float m_currentChaosBoost;
    std::string m_lastContext;

    // Rule breaks database
    std::vector<RuleBreakSuggestion> m_ruleBreaks;

    // Callbacks
    GhostTrackCallback m_ghostTrackCallback;
    RuleBreakCallback m_ruleBreakCallback;
};

} // namespace iDAW
