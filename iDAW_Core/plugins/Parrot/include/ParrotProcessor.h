/**
 * ParrotProcessor.h - Plugin 007: "The Parrot"
 * 
 * Profile: 'Intelligent Vocal/Instrument Companion'
 * 
 * Features:
 * - Mode A (Echo): Replay user input with different instrument
 * - Mode B (Harmony): Real-time pitch detection + harmony generation
 * - Vocal Synthesizer: AI-generated voice (no singing required)
 * - Instrument Sampling: Sing -> Request instrument -> Playback with same notes
 * 
 * The Parrot learns your phrase and plays it back with intelligence.
 */

#pragma once

#include <JuceHeader.h>
#include <atomic>
#include <array>
#include <vector>
#include <deque>
#include <cmath>
#include <complex>
#include <memory>

namespace iDAW {

/**
 * Parrot Configuration
 */
struct ParrotConfig {
    static constexpr int FFT_SIZE = 4096;           // For pitch detection
    static constexpr int HOP_SIZE = 512;            // Analysis hop
    static constexpr int MAX_PHRASE_SECONDS = 30;   // Max recording length
    static constexpr int MAX_HARMONY_VOICES = 4;    // Harmony stack
    static constexpr float MIN_PITCH_HZ = 50.0f;    // Lowest detectable
    static constexpr float MAX_PITCH_HZ = 2000.0f;  // Highest detectable
    static constexpr float SILENCE_THRESHOLD = 0.01f; // RMS for silence detection
    static constexpr int SILENCE_FRAMES = 20;       // Frames of silence to trigger
};

/**
 * Parrot Operating Modes
 */
enum class ParrotMode {
    ECHO,       // Replay with different instrument
    HARMONY,    // Real-time harmony generation
    VOCODER,    // Vocal synthesis from text
    SAMPLER     // Sing and sample to instrument
};

/**
 * Harmony Interval Types
 */
enum class HarmonyInterval {
    UNISON = 0,
    MINOR_THIRD = 3,
    MAJOR_THIRD = 4,
    PERFECT_FOURTH = 5,
    PERFECT_FIFTH = 7,
    MINOR_SIXTH = 8,
    MAJOR_SIXTH = 9,
    OCTAVE = 12
};

/**
 * Target Instrument for Echo/Sampler modes
 */
enum class TargetInstrument {
    SYNTH_LEAD,
    SYNTH_PAD,
    PIANO,
    STRINGS,
    BASS,
    GUITAR,
    FLUTE,
    BRASS,
    CUSTOM_WAVETABLE
};

/**
 * Detected Note Event
 */
struct NoteEvent {
    float pitchHz = 0.0f;
    int midiNote = 60;
    float velocity = 1.0f;
    float startTime = 0.0f;     // In seconds
    float duration = 0.0f;      // In seconds
    float confidence = 0.0f;    // Pitch detection confidence
};

/**
 * Phrase - A recorded sequence of notes
 */
struct Phrase {
    std::vector<NoteEvent> notes;
    float totalDuration = 0.0f;
    float bpm = 120.0f;         // Detected tempo
    std::string detectedKey;    // e.g., "C major"
    bool isRecording = false;
    bool hasContent = false;
};

/**
 * Vocal Synthesizer State
 */
struct VocalSynthState {
    std::string currentPhoneme;
    float formant1 = 700.0f;    // Hz - First formant
    float formant2 = 1200.0f;   // Hz - Second formant
    float formant3 = 2500.0f;   // Hz - Third formant
    float breathiness = 0.2f;   // Noise amount
    float vibrato = 0.0f;       // Vibrato depth
    float vibratoRate = 5.0f;   // Hz
    float glide = 0.0f;         // Portamento time
};

/**
 * Visual state for Parrot shader (Feather pattern)
 */
struct FeatherVisualState {
    float pitchHue = 0.5f;          // Pitch -> color hue
    float volumeIntensity = 0.0f;   // Volume -> brightness
    float harmonySpread = 0.0f;     // Harmony width -> feather spread
    float phraseProgress = 0.0f;    // Playback position
    bool isListening = false;       // Ear animation
    bool isSinging = false;         // Beak animation
    float echoTrailLength = 0.0f;   // Echo visualization
};

/**
 * Ghost Hands integration for Parrot
 */
struct ParrotGhostHands {
    float suggestedHarmony = 4;     // Default: major third
    float suggestedVibrato = 0.3f;
    float suggestedBreathiness = 0.2f;
    TargetInstrument suggestedInstrument = TargetInstrument::SYNTH_LEAD;
    std::string suggestedStyle;     // e.g., "operatic", "whisper", "robot"
};

/**
 * The Parrot Processor - Main audio processor class
 */
class ParrotProcessor : public juce::AudioProcessor {
public:
    ParrotProcessor();
    ~ParrotProcessor() override;

    // AudioProcessor interface
    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;
    void processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages) override;

    // Editor
    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }

    // Program/State
    const juce::String getName() const override { return "The Parrot"; }
    bool acceptsMidi() const override { return true; }
    bool producesMidi() const override { return true; }
    double getTailLengthSeconds() const override { return 2.0; }
    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram(int) override {}
    const juce::String getProgramName(int) override { return {}; }
    void changeProgramName(int, const juce::String&) override {}

    // State persistence
    void getStateInformation(juce::MemoryBlock& destData) override;
    void setStateInformation(const void* data, int sizeInBytes) override;

    // === Parrot-specific API ===

    // Mode control
    void setMode(ParrotMode mode) { currentMode = mode; }
    ParrotMode getMode() const { return currentMode; }

    // Recording/Playback
    void startListening();
    void stopListening();
    void playPhrase();
    void clearPhrase();
    bool isListening() const { return phrase.isRecording; }
    bool hasPhrase() const { return phrase.hasContent; }

    // Target instrument for Echo/Sampler
    void setTargetInstrument(TargetInstrument inst) { targetInstrument = inst; }
    TargetInstrument getTargetInstrument() const { return targetInstrument; }

    // Harmony settings
    void setHarmonyInterval(HarmonyInterval interval) { harmonyInterval = interval; }
    void setHarmonyVoices(int voices) { harmonyVoices = juce::jlimit(1, 4, voices); }

    // Vocal synth settings
    void setVocalText(const std::string& text);
    void setVocalStyle(const std::string& style);
    void triggerVocalNote(int midiNote, float velocity);
    void releaseVocalNote(int midiNote);

    // Ghost Hands integration
    void applyGhostHandsSuggestion(const ParrotGhostHands& suggestion);
    void applyStyleFromAI(const std::string& style);

    // Visual state for OpenGL
    FeatherVisualState getVisualState() const { return visualState; }

    // Parameters
    juce::AudioProcessorValueTreeState parameters;

private:
    // === Pitch Detection ===
    float detectPitch(const float* samples, int numSamples);
    float autocorrelationPitch(const float* samples, int numSamples);
    float yinPitchDetection(const float* samples, int numSamples);
    int frequencyToMidi(float freq);
    float midiToFrequency(int midiNote);

    // === Audio Analysis ===
    float calculateRMS(const float* samples, int numSamples);
    bool detectSilence(float rms);
    void analyzePhrase();
    std::string detectKey(const std::vector<NoteEvent>& notes);
    float detectTempo(const std::vector<NoteEvent>& notes);

    // === Echo Mode ===
    void processEchoMode(juce::AudioBuffer<float>& buffer);
    void synthesizeWithInstrument(juce::AudioBuffer<float>& buffer, 
                                   const NoteEvent& note, 
                                   TargetInstrument instrument);

    // === Harmony Mode ===
    void processHarmonyMode(juce::AudioBuffer<float>& buffer);
    float generateHarmonyVoice(float inputPitch, HarmonyInterval interval);
    void vocoderProcess(juce::AudioBuffer<float>& buffer, float targetPitch);

    // === Vocal Synthesizer ===
    void processVocalSynth(juce::AudioBuffer<float>& buffer);
    void textToPhonemes(const std::string& text);
    float generateFormantSample(float phase, const VocalSynthState& state);
    void applyFormants(float* buffer, int numSamples, float pitch);

    // === Sampler Mode ===
    void processSamplerMode(juce::AudioBuffer<float>& buffer);
    void resampleToInstrument(const Phrase& inputPhrase, TargetInstrument instrument);

    // === Instrument Synthesis ===
    float synthesizeSample(TargetInstrument instrument, float phase, float freq);
    float synthLead(float phase);
    float synthPad(float phase, float detune);
    float synthPiano(float phase, float decay);
    float synthStrings(float phase, float detune);
    float synthBass(float phase);
    float synthGuitar(float phase, float pluck);
    float synthFlute(float phase, float breath);
    float synthBrass(float phase, float brightness);

    // === State ===
    ParrotMode currentMode = ParrotMode::ECHO;
    TargetInstrument targetInstrument = TargetInstrument::SYNTH_LEAD;
    HarmonyInterval harmonyInterval = HarmonyInterval::MAJOR_THIRD;
    int harmonyVoices = 1;
    double sampleRate = 44100.0;
    int samplesPerBlock = 512;

    // Recording state
    Phrase phrase;
    std::vector<float> recordBuffer;
    int recordPosition = 0;
    int silenceCounter = 0;
    float lastDetectedPitch = 0.0f;
    float currentNoteStart = 0.0f;

    // Playback state
    bool isPlaying = false;
    int playbackPosition = 0;
    size_t currentNoteIndex = 0;

    // Vocal synth state
    VocalSynthState vocalState;
    std::vector<std::string> phonemeSequence;
    size_t currentPhonemeIndex = 0;
    float vocalPhase = 0.0f;
    std::vector<int> activeVocalNotes;

    // Harmony state
    float harmonyPhase = 0.0f;
    std::array<float, ParrotConfig::MAX_HARMONY_VOICES> harmonyPhases = {0};

    // Visual state
    FeatherVisualState visualState;

    // FFT for pitch detection
    std::vector<float> fftBuffer;
    std::vector<float> yinBuffer;

    // Parameter IDs
    static constexpr const char* PARAM_MODE = "mode";
    static constexpr const char* PARAM_HARMONY_INTERVAL = "harmonyInterval";
    static constexpr const char* PARAM_HARMONY_VOICES = "harmonyVoices";
    static constexpr const char* PARAM_TARGET_INSTRUMENT = "targetInstrument";
    static constexpr const char* PARAM_VIBRATO = "vibrato";
    static constexpr const char* PARAM_BREATHINESS = "breathiness";
    static constexpr const char* PARAM_MIX = "mix";
    static constexpr const char* PARAM_OCTAVE_SHIFT = "octaveShift";

    // Create parameter layout
    static juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout();

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(ParrotProcessor)
};

} // namespace iDAW
