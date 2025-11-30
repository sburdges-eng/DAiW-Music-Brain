/**
 * ParrotProcessor.cpp - Plugin 007: "The Parrot"
 * 
 * Implementation of the intelligent vocal/instrument companion
 */

#include "../include/ParrotProcessor.h"
#include <algorithm>
#include <numeric>

namespace iDAW {

// === Phoneme Database for Vocal Synthesis ===
struct PhonemeData {
    float f1, f2, f3;  // Formant frequencies
    float bandwidth1, bandwidth2, bandwidth3;
    float amplitude;
};

// Vowel formants (approximate values in Hz)
static const std::map<std::string, PhonemeData> PHONEME_DB = {
    {"a",  {730, 1090, 2440, 80, 90, 120, 1.0f}},    // as in "father"
    {"ae", {660, 1720, 2410, 70, 100, 120, 0.9f}},   // as in "cat"
    {"e",  {530, 1840, 2480, 60, 90, 120, 0.95f}},   // as in "bed"
    {"i",  {270, 2290, 3010, 50, 80, 100, 0.85f}},   // as in "beet"
    {"o",  {570, 840, 2410, 70, 80, 120, 0.9f}},     // as in "boat"
    {"u",  {300, 870, 2240, 50, 80, 120, 0.8f}},     // as in "boot"
    {"uh", {640, 1190, 2390, 70, 90, 120, 0.85f}},   // as in "but"
    {"er", {490, 1350, 1690, 60, 100, 150, 0.75f}},  // as in "bird"
    {"m",  {250, 1000, 2000, 100, 150, 200, 0.5f}},  // nasal
    {"n",  {250, 1500, 2500, 100, 150, 200, 0.5f}},  // nasal
    {"s",  {0, 0, 0, 0, 0, 0, 0.3f}},                // fricative (noise)
    {"sh", {0, 0, 0, 0, 0, 0, 0.35f}},               // fricative (noise)
    {"_",  {0, 0, 0, 0, 0, 0, 0.0f}},                // silence
};

// === Constructor/Destructor ===

ParrotProcessor::ParrotProcessor()
    : AudioProcessor(BusesProperties()
        .withInput("Input", juce::AudioChannelSet::stereo(), true)
        .withOutput("Output", juce::AudioChannelSet::stereo(), true)),
      parameters(*this, nullptr, "ParrotParams", createParameterLayout())
{
    // Initialize FFT buffers
    fftBuffer.resize(ParrotConfig::FFT_SIZE, 0.0f);
    yinBuffer.resize(ParrotConfig::FFT_SIZE / 2, 0.0f);
    
    // Reserve recording buffer for max phrase length
    recordBuffer.reserve(ParrotConfig::MAX_PHRASE_SECONDS * 48000);
}

ParrotProcessor::~ParrotProcessor() = default;

// === Parameter Layout ===

juce::AudioProcessorValueTreeState::ParameterLayout ParrotProcessor::createParameterLayout()
{
    std::vector<std::unique_ptr<juce::RangedAudioParameter>> params;
    
    params.push_back(std::make_unique<juce::AudioParameterChoice>(
        PARAM_MODE, "Mode",
        juce::StringArray{"Echo", "Harmony", "Vocoder", "Sampler"}, 0));
    
    params.push_back(std::make_unique<juce::AudioParameterChoice>(
        PARAM_HARMONY_INTERVAL, "Harmony Interval",
        juce::StringArray{"Unison", "Minor 3rd", "Major 3rd", "4th", "5th", "Minor 6th", "Major 6th", "Octave"}, 2));
    
    params.push_back(std::make_unique<juce::AudioParameterInt>(
        PARAM_HARMONY_VOICES, "Harmony Voices", 1, 4, 1));
    
    params.push_back(std::make_unique<juce::AudioParameterChoice>(
        PARAM_TARGET_INSTRUMENT, "Target Instrument",
        juce::StringArray{"Synth Lead", "Synth Pad", "Piano", "Strings", "Bass", "Guitar", "Flute", "Brass"}, 0));
    
    params.push_back(std::make_unique<juce::AudioParameterFloat>(
        PARAM_VIBRATO, "Vibrato", 0.0f, 1.0f, 0.3f));
    
    params.push_back(std::make_unique<juce::AudioParameterFloat>(
        PARAM_BREATHINESS, "Breathiness", 0.0f, 1.0f, 0.2f));
    
    params.push_back(std::make_unique<juce::AudioParameterFloat>(
        PARAM_MIX, "Mix", 0.0f, 1.0f, 0.5f));
    
    params.push_back(std::make_unique<juce::AudioParameterInt>(
        PARAM_OCTAVE_SHIFT, "Octave Shift", -2, 2, 0));
    
    return { params.begin(), params.end() };
}

// === Audio Processing Setup ===

void ParrotProcessor::prepareToPlay(double sr, int spb)
{
    sampleRate = sr;
    samplesPerBlock = spb;
    
    // Clear recording buffer
    recordBuffer.clear();
    recordBuffer.reserve(static_cast<size_t>(ParrotConfig::MAX_PHRASE_SECONDS * sampleRate));
    
    // Reset states
    recordPosition = 0;
    silenceCounter = 0;
    playbackPosition = 0;
    currentNoteIndex = 0;
    vocalPhase = 0.0f;
    harmonyPhase = 0.0f;
    
    for (auto& phase : harmonyPhases) {
        phase = 0.0f;
    }
}

void ParrotProcessor::releaseResources()
{
    recordBuffer.clear();
}

// === Main Processing ===

void ParrotProcessor::processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
{
    juce::ScopedNoDenormals noDenormals;
    
    const int numSamples = buffer.getNumSamples();
    const int numChannels = buffer.getNumChannels();
    
    // Get parameters
    currentMode = static_cast<ParrotMode>(
        parameters.getRawParameterValue(PARAM_MODE)->load());
    targetInstrument = static_cast<TargetInstrument>(
        parameters.getRawParameterValue(PARAM_TARGET_INSTRUMENT)->load());
    
    // Process based on mode
    switch (currentMode) {
        case ParrotMode::ECHO:
            processEchoMode(buffer);
            break;
        case ParrotMode::HARMONY:
            processHarmonyMode(buffer);
            break;
        case ParrotMode::VOCODER:
            processVocalSynth(buffer);
            break;
        case ParrotMode::SAMPLER:
            processSamplerMode(buffer);
            break;
    }
    
    // Update visual state
    float rms = calculateRMS(buffer.getReadPointer(0), numSamples);
    visualState.volumeIntensity = juce::jlimit(0.0f, 1.0f, rms * 10.0f);
    visualState.isListening = phrase.isRecording;
    visualState.isSinging = isPlaying || !activeVocalNotes.empty();
    
    if (lastDetectedPitch > 0) {
        // Map pitch to hue (low = red, high = blue)
        visualState.pitchHue = juce::jlimit(0.0f, 1.0f,
            (lastDetectedPitch - ParrotConfig::MIN_PITCH_HZ) / 
            (ParrotConfig::MAX_PITCH_HZ - ParrotConfig::MIN_PITCH_HZ));
    }
}

// === Echo Mode Processing ===

void ParrotProcessor::processEchoMode(juce::AudioBuffer<float>& buffer)
{
    const int numSamples = buffer.getNumSamples();
    const float* inputL = buffer.getReadPointer(0);
    
    // If recording
    if (phrase.isRecording) {
        // Append to record buffer
        for (int i = 0; i < numSamples; ++i) {
            if (recordPosition < static_cast<int>(recordBuffer.capacity())) {
                recordBuffer.push_back(inputL[i]);
                recordPosition++;
            }
        }
        
        // Detect pitch in this block
        float pitch = detectPitch(inputL, numSamples);
        float rms = calculateRMS(inputL, numSamples);
        
        // Silence detection
        if (detectSilence(rms)) {
            silenceCounter++;
            if (silenceCounter >= ParrotConfig::SILENCE_FRAMES) {
                // End of phrase detected
                stopListening();
            }
        } else {
            silenceCounter = 0;
            
            // Track note
            if (pitch > 0 && pitch != lastDetectedPitch) {
                // New note detected
                float currentTime = static_cast<float>(recordPosition) / static_cast<float>(sampleRate);
                
                if (lastDetectedPitch > 0) {
                    // End previous note
                    if (!phrase.notes.empty()) {
                        phrase.notes.back().duration = currentTime - phrase.notes.back().startTime;
                    }
                }
                
                // Start new note
                NoteEvent note;
                note.pitchHz = pitch;
                note.midiNote = frequencyToMidi(pitch);
                note.velocity = juce::jlimit(0.0f, 1.0f, rms * 5.0f);
                note.startTime = currentTime;
                note.confidence = 0.9f;
                phrase.notes.push_back(note);
            }
            lastDetectedPitch = pitch;
        }
    }
    
    // If playing back
    if (isPlaying && phrase.hasContent) {
        float mix = parameters.getRawParameterValue(PARAM_MIX)->load();
        int octaveShift = static_cast<int>(parameters.getRawParameterValue(PARAM_OCTAVE_SHIFT)->load());
        
        // Get current playback time
        float playbackTime = static_cast<float>(playbackPosition) / static_cast<float>(sampleRate);
        
        // Find current note
        while (currentNoteIndex < phrase.notes.size() &&
               playbackTime > phrase.notes[currentNoteIndex].startTime + 
                              phrase.notes[currentNoteIndex].duration) {
            currentNoteIndex++;
        }
        
        if (currentNoteIndex < phrase.notes.size()) {
            NoteEvent currentNote = phrase.notes[currentNoteIndex];
            
            // Apply octave shift
            float targetFreq = midiToFrequency(currentNote.midiNote + octaveShift * 12);
            
            // Synthesize with target instrument
            float* outputL = buffer.getWritePointer(0);
            float* outputR = buffer.getNumChannels() > 1 ? buffer.getWritePointer(1) : nullptr;
            
            float phaseIncrement = targetFreq / static_cast<float>(sampleRate);
            
            for (int i = 0; i < numSamples; ++i) {
                float synthSample = synthesizeSample(targetInstrument, harmonyPhase, targetFreq);
                synthSample *= currentNote.velocity;
                
                // Mix with input
                outputL[i] = outputL[i] * (1.0f - mix) + synthSample * mix;
                if (outputR) {
                    outputR[i] = outputR[i] * (1.0f - mix) + synthSample * mix;
                }
                
                harmonyPhase += phaseIncrement;
                if (harmonyPhase >= 1.0f) harmonyPhase -= 1.0f;
            }
        }
        
        playbackPosition += numSamples;
        visualState.phraseProgress = playbackTime / phrase.totalDuration;
        
        // Check if playback complete
        if (playbackTime >= phrase.totalDuration) {
            isPlaying = false;
            playbackPosition = 0;
            currentNoteIndex = 0;
        }
    }
}

// === Harmony Mode Processing ===

void ParrotProcessor::processHarmonyMode(juce::AudioBuffer<float>& buffer)
{
    const int numSamples = buffer.getNumSamples();
    const float* inputL = buffer.getReadPointer(0);
    float* outputL = buffer.getWritePointer(0);
    float* outputR = buffer.getNumChannels() > 1 ? buffer.getWritePointer(1) : nullptr;
    
    // Detect pitch in real-time
    float pitch = detectPitch(inputL, numSamples);
    lastDetectedPitch = pitch;
    
    if (pitch <= 0) {
        return;  // No pitch detected, pass through
    }
    
    float mix = parameters.getRawParameterValue(PARAM_MIX)->load();
    int numVoices = static_cast<int>(parameters.getRawParameterValue(PARAM_HARMONY_VOICES)->load());
    int intervalChoice = static_cast<int>(parameters.getRawParameterValue(PARAM_HARMONY_INTERVAL)->load());
    
    // Map interval choice to semitones
    static const int intervals[] = {0, 3, 4, 5, 7, 8, 9, 12};
    int semitones = intervals[intervalChoice];
    
    // Generate harmony voices
    for (int i = 0; i < numSamples; ++i) {
        float harmonySum = 0.0f;
        
        for (int v = 0; v < numVoices; ++v) {
            // Each voice can be at different intervals
            int voiceSemitones = semitones * (v + 1);
            if (v > 0 && voiceSemitones > 12) {
                voiceSemitones = voiceSemitones % 12;  // Wrap within octave
            }
            
            float harmonyFreq = pitch * std::pow(2.0f, voiceSemitones / 12.0f);
            float phaseIncrement = harmonyFreq / static_cast<float>(sampleRate);
            
            // Use vocoder-style synthesis for natural sound
            float voiceSample = generateFormantSample(harmonyPhases[v], vocalState);
            voiceSample *= 0.5f;  // Reduce volume for stacking
            
            harmonySum += voiceSample;
            
            harmonyPhases[v] += phaseIncrement;
            if (harmonyPhases[v] >= 1.0f) harmonyPhases[v] -= 1.0f;
        }
        
        harmonySum /= static_cast<float>(numVoices);
        
        // Mix harmony with input
        outputL[i] = inputL[i] * (1.0f - mix * 0.5f) + harmonySum * mix;
        if (outputR) {
            outputR[i] = inputL[i] * (1.0f - mix * 0.5f) + harmonySum * mix;
        }
    }
    
    visualState.harmonySpread = static_cast<float>(numVoices) / 4.0f;
}

// === Vocal Synthesizer Processing ===

void ParrotProcessor::processVocalSynth(juce::AudioBuffer<float>& buffer)
{
    if (activeVocalNotes.empty()) {
        return;
    }
    
    const int numSamples = buffer.getNumSamples();
    float* outputL = buffer.getWritePointer(0);
    float* outputR = buffer.getNumChannels() > 1 ? buffer.getWritePointer(1) : nullptr;
    
    float vibrato = parameters.getRawParameterValue(PARAM_VIBRATO)->load();
    float breathiness = parameters.getRawParameterValue(PARAM_BREATHINESS)->load();
    float mix = parameters.getRawParameterValue(PARAM_MIX)->load();
    
    vocalState.vibrato = vibrato * 0.5f;  // Max ±0.5 semitone
    vocalState.breathiness = breathiness;
    
    // Generate vocal for each active note
    for (int i = 0; i < numSamples; ++i) {
        float vocalSum = 0.0f;
        
        for (int midiNote : activeVocalNotes) {
            float baseFreq = midiToFrequency(midiNote);
            
            // Apply vibrato
            float vibratoMod = std::sin(vocalPhase * vocalState.vibratoRate * 2.0f * M_PI) 
                             * vocalState.vibrato;
            float freq = baseFreq * std::pow(2.0f, vibratoMod / 12.0f);
            
            float phaseIncrement = freq / static_cast<float>(sampleRate);
            
            // Generate formant-based vocal
            float sample = generateFormantSample(vocalPhase, vocalState);
            
            // Add breathiness (noise)
            if (vocalState.breathiness > 0) {
                float noise = (static_cast<float>(rand()) / RAND_MAX * 2.0f - 1.0f);
                sample = sample * (1.0f - vocalState.breathiness * 0.5f) + 
                         noise * vocalState.breathiness * 0.3f;
            }
            
            vocalSum += sample * 0.5f;
        }
        
        vocalSum /= std::max(1, static_cast<int>(activeVocalNotes.size()));
        
        outputL[i] = outputL[i] * (1.0f - mix) + vocalSum * mix;
        if (outputR) {
            outputR[i] = outputR[i] * (1.0f - mix) + vocalSum * mix;
        }
        
        vocalPhase += 1.0f / static_cast<float>(sampleRate);
        if (vocalPhase >= 1.0f) vocalPhase -= 1.0f;
    }
}

// === Sampler Mode Processing ===

void ParrotProcessor::processSamplerMode(juce::AudioBuffer<float>& buffer)
{
    // Same as Echo mode but with user-selected instrument
    processEchoMode(buffer);
}

// === Pitch Detection (YIN Algorithm) ===

float ParrotProcessor::detectPitch(const float* samples, int numSamples)
{
    // Copy to FFT buffer
    int copyLen = std::min(numSamples, ParrotConfig::FFT_SIZE);
    std::fill(fftBuffer.begin(), fftBuffer.end(), 0.0f);
    std::copy(samples, samples + copyLen, fftBuffer.begin());
    
    return yinPitchDetection(fftBuffer.data(), ParrotConfig::FFT_SIZE);
}

float ParrotProcessor::yinPitchDetection(const float* samples, int numSamples)
{
    const int halfSize = numSamples / 2;
    const float threshold = 0.1f;
    
    // Step 1: Calculate difference function
    std::fill(yinBuffer.begin(), yinBuffer.end(), 0.0f);
    
    for (int tau = 1; tau < halfSize; ++tau) {
        float sum = 0.0f;
        for (int j = 0; j < halfSize; ++j) {
            float delta = samples[j] - samples[j + tau];
            sum += delta * delta;
        }
        yinBuffer[tau] = sum;
    }
    
    // Step 2: Cumulative mean normalized difference
    yinBuffer[0] = 1.0f;
    float runningSum = 0.0f;
    
    for (int tau = 1; tau < halfSize; ++tau) {
        runningSum += yinBuffer[tau];
        yinBuffer[tau] *= static_cast<float>(tau) / runningSum;
    }
    
    // Step 3: Absolute threshold
    int tauEstimate = -1;
    for (int tau = 2; tau < halfSize; ++tau) {
        if (yinBuffer[tau] < threshold) {
            while (tau + 1 < halfSize && yinBuffer[tau + 1] < yinBuffer[tau]) {
                ++tau;
            }
            tauEstimate = tau;
            break;
        }
    }
    
    if (tauEstimate < 0) {
        return 0.0f;  // No pitch detected
    }
    
    // Step 4: Parabolic interpolation
    float betterTau;
    if (tauEstimate > 0 && tauEstimate < halfSize - 1) {
        float s0 = yinBuffer[tauEstimate - 1];
        float s1 = yinBuffer[tauEstimate];
        float s2 = yinBuffer[tauEstimate + 1];
        betterTau = tauEstimate + (s2 - s0) / (2.0f * (2.0f * s1 - s2 - s0));
    } else {
        betterTau = static_cast<float>(tauEstimate);
    }
    
    float pitch = static_cast<float>(sampleRate) / betterTau;
    
    // Validate pitch range
    if (pitch < ParrotConfig::MIN_PITCH_HZ || pitch > ParrotConfig::MAX_PITCH_HZ) {
        return 0.0f;
    }
    
    return pitch;
}

// === Formant Synthesis ===

float ParrotProcessor::generateFormantSample(float phase, const VocalSynthState& state)
{
    // Generate glottal pulse (simplified)
    float glottal = std::sin(phase * 2.0f * M_PI);
    glottal = glottal * glottal * (glottal > 0 ? 1.0f : -0.5f);  // Asymmetric pulse
    
    // Apply formants using resonant filters (simplified)
    float sample = glottal;
    
    // Formant 1
    float f1Phase = phase * state.formant1 / 440.0f;
    sample += 0.6f * std::sin(f1Phase * 2.0f * M_PI) * std::exp(-f1Phase * 2.0f);
    
    // Formant 2
    float f2Phase = phase * state.formant2 / 440.0f;
    sample += 0.4f * std::sin(f2Phase * 2.0f * M_PI) * std::exp(-f2Phase * 3.0f);
    
    // Formant 3
    float f3Phase = phase * state.formant3 / 440.0f;
    sample += 0.2f * std::sin(f3Phase * 2.0f * M_PI) * std::exp(-f3Phase * 4.0f);
    
    return juce::jlimit(-1.0f, 1.0f, sample * 0.5f);
}

// === Instrument Synthesis ===

float ParrotProcessor::synthesizeSample(TargetInstrument instrument, float phase, float freq)
{
    switch (instrument) {
        case TargetInstrument::SYNTH_LEAD:
            return synthLead(phase);
        case TargetInstrument::SYNTH_PAD:
            return synthPad(phase, 0.01f);
        case TargetInstrument::PIANO:
            return synthPiano(phase, 0.995f);
        case TargetInstrument::STRINGS:
            return synthStrings(phase, 0.003f);
        case TargetInstrument::BASS:
            return synthBass(phase);
        case TargetInstrument::GUITAR:
            return synthGuitar(phase, 0.9f);
        case TargetInstrument::FLUTE:
            return synthFlute(phase, 0.3f);
        case TargetInstrument::BRASS:
            return synthBrass(phase, 0.7f);
        default:
            return synthLead(phase);
    }
}

float ParrotProcessor::synthLead(float phase)
{
    // Sawtooth with slight detuning
    float saw = 2.0f * phase - 1.0f;
    float saw2 = 2.0f * std::fmod(phase + 0.003f, 1.0f) - 1.0f;
    return (saw + saw2) * 0.4f;
}

float ParrotProcessor::synthPad(float phase, float detune)
{
    // Multiple detuned sines
    float sum = 0.0f;
    for (int i = 0; i < 5; ++i) {
        float detuneAmount = (i - 2) * detune;
        sum += std::sin((phase + detuneAmount) * 2.0f * M_PI) * 0.2f;
    }
    return sum;
}

float ParrotProcessor::synthPiano(float phase, float decay)
{
    // Struck string with harmonics
    float fundamental = std::sin(phase * 2.0f * M_PI);
    float h2 = std::sin(phase * 4.0f * M_PI) * 0.5f;
    float h3 = std::sin(phase * 6.0f * M_PI) * 0.25f;
    return (fundamental + h2 + h3) * 0.4f;
}

float ParrotProcessor::synthStrings(float phase, float detune)
{
    // Ensemble with vibrato
    float vibrato = std::sin(phase * 5.0f) * 0.002f;
    float saw1 = 2.0f * std::fmod(phase + vibrato, 1.0f) - 1.0f;
    float saw2 = 2.0f * std::fmod(phase - vibrato + detune, 1.0f) - 1.0f;
    return (saw1 + saw2) * 0.35f;
}

float ParrotProcessor::synthBass(float phase)
{
    // Sub bass with harmonics
    float sub = std::sin(phase * 2.0f * M_PI);
    float harm = std::sin(phase * 4.0f * M_PI) * 0.3f;
    return (sub + harm) * 0.5f;
}

float ParrotProcessor::synthGuitar(float phase, float pluck)
{
    // Karplus-Strong-ish
    float saw = 2.0f * phase - 1.0f;
    float filtered = saw * pluck;
    return filtered * 0.4f;
}

float ParrotProcessor::synthFlute(float phase, float breath)
{
    // Sine with breath noise
    float tone = std::sin(phase * 2.0f * M_PI);
    float noise = (static_cast<float>(rand()) / RAND_MAX * 2.0f - 1.0f) * breath;
    return (tone + noise) * 0.4f;
}

float ParrotProcessor::synthBrass(float phase, float brightness)
{
    // Sawtooth with variable harmonics
    float saw = 2.0f * phase - 1.0f;
    float square = phase < 0.5f ? 1.0f : -1.0f;
    return (saw * brightness + square * (1.0f - brightness)) * 0.4f;
}

// === Utility Functions ===

float ParrotProcessor::calculateRMS(const float* samples, int numSamples)
{
    float sum = 0.0f;
    for (int i = 0; i < numSamples; ++i) {
        sum += samples[i] * samples[i];
    }
    return std::sqrt(sum / static_cast<float>(numSamples));
}

bool ParrotProcessor::detectSilence(float rms)
{
    return rms < ParrotConfig::SILENCE_THRESHOLD;
}

int ParrotProcessor::frequencyToMidi(float freq)
{
    if (freq <= 0) return 60;
    return static_cast<int>(std::round(69.0f + 12.0f * std::log2(freq / 440.0f)));
}

float ParrotProcessor::midiToFrequency(int midiNote)
{
    return 440.0f * std::pow(2.0f, (midiNote - 69) / 12.0f);
}

// === Recording Control ===

void ParrotProcessor::startListening()
{
    phrase.isRecording = true;
    phrase.hasContent = false;
    phrase.notes.clear();
    recordBuffer.clear();
    recordPosition = 0;
    silenceCounter = 0;
    lastDetectedPitch = 0.0f;
    visualState.isListening = true;
}

void ParrotProcessor::stopListening()
{
    phrase.isRecording = false;
    visualState.isListening = false;
    
    if (!phrase.notes.empty()) {
        // Finalize last note
        float endTime = static_cast<float>(recordPosition) / static_cast<float>(sampleRate);
        if (phrase.notes.back().duration <= 0) {
            phrase.notes.back().duration = endTime - phrase.notes.back().startTime;
        }
        
        phrase.totalDuration = endTime;
        phrase.hasContent = true;
        
        // Analyze phrase
        analyzePhrase();
    }
}

void ParrotProcessor::playPhrase()
{
    if (phrase.hasContent) {
        isPlaying = true;
        playbackPosition = 0;
        currentNoteIndex = 0;
        visualState.isSinging = true;
    }
}

void ParrotProcessor::clearPhrase()
{
    phrase.notes.clear();
    phrase.hasContent = false;
    phrase.isRecording = false;
    phrase.totalDuration = 0.0f;
    recordBuffer.clear();
    recordPosition = 0;
    isPlaying = false;
}

void ParrotProcessor::analyzePhrase()
{
    if (phrase.notes.empty()) return;
    
    phrase.detectedKey = detectKey(phrase.notes);
    phrase.bpm = detectTempo(phrase.notes);
}

std::string ParrotProcessor::detectKey(const std::vector<NoteEvent>& notes)
{
    // Simple key detection based on note histogram
    std::array<int, 12> histogram = {0};
    
    for (const auto& note : notes) {
        histogram[note.midiNote % 12]++;
    }
    
    // Find most common note as root
    int maxIdx = 0;
    for (int i = 1; i < 12; ++i) {
        if (histogram[i] > histogram[maxIdx]) {
            maxIdx = i;
        }
    }
    
    static const char* noteNames[] = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};
    
    // Check for major/minor based on third
    int majorThird = (maxIdx + 4) % 12;
    int minorThird = (maxIdx + 3) % 12;
    
    std::string key = noteNames[maxIdx];
    if (histogram[minorThird] > histogram[majorThird]) {
        key += " minor";
    } else {
        key += " major";
    }
    
    return key;
}

float ParrotProcessor::detectTempo(const std::vector<NoteEvent>& notes)
{
    if (notes.size() < 2) return 120.0f;
    
    // Calculate average inter-onset interval
    float totalInterval = 0.0f;
    int count = 0;
    
    for (size_t i = 1; i < notes.size(); ++i) {
        float interval = notes[i].startTime - notes[i-1].startTime;
        if (interval > 0.1f && interval < 2.0f) {  // Reasonable beat interval
            totalInterval += interval;
            count++;
        }
    }
    
    if (count == 0) return 120.0f;
    
    float avgInterval = totalInterval / static_cast<float>(count);
    return 60.0f / avgInterval;
}

// === Vocal Synth Control ===

void ParrotProcessor::setVocalText(const std::string& text)
{
    textToPhonemes(text);
}

void ParrotProcessor::textToPhonemes(const std::string& text)
{
    phonemeSequence.clear();
    
    // Simple text-to-phoneme conversion (very basic)
    for (char c : text) {
        char lower = std::tolower(c);
        switch (lower) {
            case 'a': phonemeSequence.push_back("a"); break;
            case 'e': phonemeSequence.push_back("e"); break;
            case 'i': phonemeSequence.push_back("i"); break;
            case 'o': phonemeSequence.push_back("o"); break;
            case 'u': phonemeSequence.push_back("u"); break;
            case ' ': phonemeSequence.push_back("_"); break;
            case 'm': phonemeSequence.push_back("m"); break;
            case 'n': phonemeSequence.push_back("n"); break;
            case 's': phonemeSequence.push_back("s"); break;
            default:
                if (std::isalpha(lower)) {
                    phonemeSequence.push_back("uh");
                }
                break;
        }
    }
    
    currentPhonemeIndex = 0;
}

void ParrotProcessor::setVocalStyle(const std::string& style)
{
    if (style == "operatic") {
        vocalState.vibrato = 0.5f;
        vocalState.breathiness = 0.1f;
        vocalState.vibratoRate = 6.0f;
    } else if (style == "whisper") {
        vocalState.vibrato = 0.0f;
        vocalState.breathiness = 0.8f;
    } else if (style == "robot") {
        vocalState.vibrato = 0.0f;
        vocalState.breathiness = 0.0f;
        vocalState.formant1 = 500.0f;
        vocalState.formant2 = 1000.0f;
        vocalState.formant3 = 2000.0f;
    }
}

void ParrotProcessor::triggerVocalNote(int midiNote, float velocity)
{
    if (std::find(activeVocalNotes.begin(), activeVocalNotes.end(), midiNote) == activeVocalNotes.end()) {
        activeVocalNotes.push_back(midiNote);
    }
}

void ParrotProcessor::releaseVocalNote(int midiNote)
{
    activeVocalNotes.erase(
        std::remove(activeVocalNotes.begin(), activeVocalNotes.end(), midiNote),
        activeVocalNotes.end());
}

// === Ghost Hands Integration ===

void ParrotProcessor::applyGhostHandsSuggestion(const ParrotGhostHands& suggestion)
{
    // Apply harmony interval
    int intervalValue = static_cast<int>(suggestion.suggestedHarmony);
    // Map to parameter
    parameters.getParameter(PARAM_HARMONY_INTERVAL)->setValueNotifyingHost(
        intervalValue / 12.0f);
    
    // Apply vibrato
    parameters.getParameter(PARAM_VIBRATO)->setValueNotifyingHost(
        suggestion.suggestedVibrato);
    
    // Apply breathiness
    parameters.getParameter(PARAM_BREATHINESS)->setValueNotifyingHost(
        suggestion.suggestedBreathiness);
    
    // Apply instrument
    parameters.getParameter(PARAM_TARGET_INSTRUMENT)->setValueNotifyingHost(
        static_cast<float>(suggestion.suggestedInstrument) / 8.0f);
    
    // Apply vocal style
    if (!suggestion.suggestedStyle.empty()) {
        setVocalStyle(suggestion.suggestedStyle);
    }
}

void ParrotProcessor::applyStyleFromAI(const std::string& style)
{
    if (style == "soulful") {
        setHarmonyInterval(HarmonyInterval::MAJOR_THIRD);
        vocalState.vibrato = 0.4f;
        vocalState.breathiness = 0.2f;
    } else if (style == "electronic") {
        setHarmonyInterval(HarmonyInterval::PERFECT_FIFTH);
        vocalState.vibrato = 0.0f;
        vocalState.breathiness = 0.0f;
    } else if (style == "choir") {
        setHarmonyInterval(HarmonyInterval::PERFECT_FIFTH);
        harmonyVoices = 3;
        vocalState.vibrato = 0.3f;
    }
}

// === State Persistence ===

void ParrotProcessor::getStateInformation(juce::MemoryBlock& destData)
{
    auto state = parameters.copyState();
    std::unique_ptr<juce::XmlElement> xml(state.createXml());
    copyXmlToBinary(*xml, destData);
}

void ParrotProcessor::setStateInformation(const void* data, int sizeInBytes)
{
    std::unique_ptr<juce::XmlElement> xml(getXmlFromBinary(data, sizeInBytes));
    if (xml && xml->hasTagName(parameters.state.getType())) {
        parameters.replaceState(juce::ValueTree::fromXml(*xml));
    }
}

// === Editor ===

juce::AudioProcessorEditor* ParrotProcessor::createEditor()
{
    return new juce::GenericAudioProcessorEditor(*this);
}

} // namespace iDAW
