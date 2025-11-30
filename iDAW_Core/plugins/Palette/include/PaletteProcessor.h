/**
 * PaletteProcessor.h - Plugin 006: "The Palette"
 * 
 * Profile: 'Wavetable Synth' with Watercolor UI
 * 
 * Features:
 * - Dual-oscillator wavetable engine
 * - FM modulation matrix
 * - State variable filter
 * - 2 LFOs + 2 ADSR envelopes
 * - Diffusion-reaction visual system
 */

#pragma once

#include <JuceHeader.h>
#include <atomic>
#include <array>
#include <vector>
#include <cmath>

namespace iDAW {

/**
 * Configuration for The Palette
 */
struct PaletteConfig {
    static constexpr int WAVETABLE_SIZE = 2048;
    static constexpr int NUM_WAVETABLES = 4;  // Sine, Saw, Square, Noise
    static constexpr int MAX_VOICES = 8;
    static constexpr float MAX_FM_AMOUNT = 1000.0f;  // Hz deviation
};

/**
 * Wavetable types
 */
enum class WavetableType {
    SINE,
    SAW,
    SQUARE,
    NOISE,
    CUSTOM
};

/**
 * Filter types
 */
enum class FilterType {
    LOWPASS,
    HIGHPASS,
    BANDPASS
};

/**
 * ADSR Envelope
 */
struct ADSREnvelope {
    float attack = 0.01f;    // seconds
    float decay = 0.1f;      // seconds
    float sustain = 0.7f;    // level (0-1)
    float release = 0.3f;    // seconds
    
    // State
    enum class Stage { IDLE, ATTACK, DECAY, SUSTAIN, RELEASE };
    Stage stage = Stage::IDLE;
    float level = 0.0f;
    float releaseLevel = 0.0f;
};

/**
 * LFO
 */
struct LFO {
    float rate = 1.0f;       // Hz
    float depth = 0.5f;      // 0-1
    WavetableType shape = WavetableType::SINE;
    float phase = 0.0f;
};

/**
 * Visual state for Watercolor shader
 */
struct WatercolorVisualState {
    float blurStrength = 0.5f;      // Filter cutoff -> blur
    float edgeSharpening = 0.0f;    // Resonance -> coffee ring
    float colorR = 0.0f;            // Wave position -> color blend
    float colorG = 0.0f;
    float colorB = 1.0f;            // Default: blue (sine)
    float diffusionRate = 0.05f;    // Paint bleeding speed
};

/**
 * Voice state for polyphony
 */
struct Voice {
    bool active = false;
    int noteNumber = 60;
    float velocity = 1.0f;
    float phase1 = 0.0f;     // Osc 1 phase
    float phase2 = 0.0f;     // Osc 2 phase
    ADSREnvelope ampEnv;
    ADSREnvelope filterEnv;
};

/**
 * PaletteProcessor - Wavetable Synthesizer
 */
class PaletteProcessor : public juce::AudioProcessor {
public:
    PaletteProcessor();
    ~PaletteProcessor() override;
    
    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;
    void processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages) override;
    
    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }
    
    const juce::String getName() const override { return "The Palette"; }
    bool acceptsMidi() const override { return true; }
    bool producesMidi() const override { return false; }
    double getTailLengthSeconds() const override { return 2.0; }
    
    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram(int) override {}
    const juce::String getProgramName(int) override { return {}; }
    void changeProgramName(int, const juce::String&) override {}
    
    void getStateInformation(juce::MemoryBlock& destData) override;
    void setStateInformation(const void* data, int sizeInBytes) override;
    
    // Oscillator 1
    void setOsc1Wavetable(WavetableType type);
    void setOsc1Position(float pos);  // 0-1 blend position
    void setOsc1Level(float level);
    void setOsc1Detune(float cents);
    
    // Oscillator 2
    void setOsc2Wavetable(WavetableType type);
    void setOsc2Position(float pos);
    void setOsc2Level(float level);
    void setOsc2Detune(float cents);
    
    // FM
    void setFMAmount(float amount);  // 0-1 normalized
    float getFMAmount() const { return m_fmAmount.load(); }
    
    // Filter
    void setFilterType(FilterType type);
    void setFilterCutoff(float freqHz);
    float getFilterCutoff() const { return m_filterCutoff.load(); }
    void setFilterResonance(float q);
    float getFilterResonance() const { return m_filterResonance.load(); }
    void setFilterEnvAmount(float amount);
    
    // Envelopes
    void setAmpEnvelope(float a, float d, float s, float r);
    void setFilterEnvelope(float a, float d, float s, float r);
    
    // LFOs
    void setLFO1(float rate, float depth, WavetableType shape);
    void setLFO2(float rate, float depth, WavetableType shape);
    void setLFO1Target(int target);  // 0=pitch, 1=filter, 2=amp
    void setLFO2Target(int target);
    
    // Master
    void setMasterVolume(float volume);
    
    // Ghost Hands
    void applyAISuggestion(const juce::String& suggestion);
    
    // Visual state
    WatercolorVisualState getVisualState() const;
    
private:
    void handleMidiEvent(const juce::MidiMessage& msg);
    void noteOn(int note, float velocity);
    void noteOff(int note);
    float processVoice(Voice& voice);
    float readWavetable(WavetableType type, float phase);
    float processFilter(float input);
    float processEnvelope(ADSREnvelope& env);
    void updateVisualState();
    void generateWavetables();
    
    // Wavetables
    std::array<std::vector<float>, 4> m_wavetables;
    
    // Voices
    std::array<Voice, PaletteConfig::MAX_VOICES> m_voices;
    
    // Oscillator parameters
    WavetableType m_osc1Type = WavetableType::SINE;
    WavetableType m_osc2Type = WavetableType::SAW;
    std::atomic<float> m_osc1Level{0.7f};
    std::atomic<float> m_osc2Level{0.5f};
    std::atomic<float> m_osc1Detune{0.0f};
    std::atomic<float> m_osc2Detune{0.0f};
    std::atomic<float> m_osc1Position{0.0f};
    std::atomic<float> m_osc2Position{0.0f};
    
    // FM
    std::atomic<float> m_fmAmount{0.0f};
    
    // Filter
    FilterType m_filterType = FilterType::LOWPASS;
    std::atomic<float> m_filterCutoff{5000.0f};
    std::atomic<float> m_filterResonance{0.5f};
    std::atomic<float> m_filterEnvAmount{0.0f};
    
    // Filter state (per voice simplified to mono for efficiency)
    float m_filterState1 = 0.0f;
    float m_filterState2 = 0.0f;
    
    // Envelope templates
    ADSREnvelope m_ampEnvTemplate;
    ADSREnvelope m_filterEnvTemplate;
    
    // LFOs
    LFO m_lfo1, m_lfo2;
    int m_lfo1Target = 0;  // 0=pitch, 1=filter, 2=amp
    int m_lfo2Target = 1;
    
    // Master
    std::atomic<float> m_masterVolume{0.8f};
    
    // Visual state
    WatercolorVisualState m_visualState;
    mutable std::mutex m_visualMutex;
    
    double m_sampleRate = 44100.0;
    bool m_prepared = false;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(PaletteProcessor)
};

} // namespace iDAW
