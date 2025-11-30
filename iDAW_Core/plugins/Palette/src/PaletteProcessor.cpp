/**
 * PaletteProcessor.cpp - Implementation of Plugin 006: "The Palette"
 * 
 * Profile: 'Wavetable Synth' with Watercolor UI
 */

#include "PaletteProcessor.h"

namespace iDAW {

PaletteProcessor::PaletteProcessor()
    : AudioProcessor(BusesProperties()
                     .withOutput("Output", juce::AudioChannelSet::stereo(), true))
{
    generateWavetables();
}

PaletteProcessor::~PaletteProcessor() = default;

void PaletteProcessor::generateWavetables() {
    const int size = PaletteConfig::WAVETABLE_SIZE;
    
    // Resize wavetables
    for (auto& wt : m_wavetables) {
        wt.resize(size);
    }
    
    // Sine
    for (int i = 0; i < size; ++i) {
        float phase = static_cast<float>(i) / size;
        m_wavetables[0][i] = std::sin(phase * 2.0f * juce::MathConstants<float>::pi);
    }
    
    // Saw (band-limited approximation)
    for (int i = 0; i < size; ++i) {
        float phase = static_cast<float>(i) / size;
        m_wavetables[1][i] = 2.0f * phase - 1.0f;
    }
    
    // Square (band-limited approximation)
    for (int i = 0; i < size; ++i) {
        float phase = static_cast<float>(i) / size;
        m_wavetables[2][i] = phase < 0.5f ? 1.0f : -1.0f;
    }
    
    // Noise (stored values)
    for (int i = 0; i < size; ++i) {
        m_wavetables[3][i] = (static_cast<float>(rand()) / RAND_MAX) * 2.0f - 1.0f;
    }
}

void PaletteProcessor::prepareToPlay(double sampleRate, int samplesPerBlock) {
    m_sampleRate = sampleRate;
    
    // Reset all voices
    for (auto& voice : m_voices) {
        voice.active = false;
        voice.phase1 = 0.0f;
        voice.phase2 = 0.0f;
    }
    
    // Reset filter
    m_filterState1 = 0.0f;
    m_filterState2 = 0.0f;
    
    // Reset LFOs
    m_lfo1.phase = 0.0f;
    m_lfo2.phase = 0.0f;
    
    m_prepared = true;
}

void PaletteProcessor::releaseResources() {
    m_prepared = false;
}

void PaletteProcessor::processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages) {
    if (!m_prepared) return;
    
    juce::ScopedNoDenormals noDenormals;
    
    buffer.clear();
    
    // Handle MIDI
    for (const auto metadata : midiMessages) {
        handleMidiEvent(metadata.getMessage());
    }
    
    const int numSamples = buffer.getNumSamples();
    float* outputL = buffer.getWritePointer(0);
    float* outputR = buffer.getNumChannels() > 1 ? buffer.getWritePointer(1) : outputL;
    
    // Update LFOs
    float lfo1Inc = m_lfo1.rate / static_cast<float>(m_sampleRate);
    float lfo2Inc = m_lfo2.rate / static_cast<float>(m_sampleRate);
    
    for (int sample = 0; sample < numSamples; ++sample) {
        // Update LFO phases
        m_lfo1.phase += lfo1Inc;
        if (m_lfo1.phase >= 1.0f) m_lfo1.phase -= 1.0f;
        m_lfo2.phase += lfo2Inc;
        if (m_lfo2.phase >= 1.0f) m_lfo2.phase -= 1.0f;
        
        float lfo1Value = readWavetable(m_lfo1.shape, m_lfo1.phase) * m_lfo1.depth;
        float lfo2Value = readWavetable(m_lfo2.shape, m_lfo2.phase) * m_lfo2.depth;
        
        float mixedSample = 0.0f;
        
        // Process all active voices
        for (auto& voice : m_voices) {
            if (voice.active) {
                mixedSample += processVoice(voice);
            }
        }
        
        // Apply LFO modulation to filter if targeted
        float cutoff = m_filterCutoff.load();
        if (m_lfo1Target == 1) cutoff *= (1.0f + lfo1Value * 0.5f);
        if (m_lfo2Target == 1) cutoff *= (1.0f + lfo2Value * 0.5f);
        m_filterCutoff.store(std::clamp(cutoff, 20.0f, 20000.0f));
        
        // Apply filter
        mixedSample = processFilter(mixedSample);
        
        // Apply LFO to amp if targeted
        float amp = 1.0f;
        if (m_lfo1Target == 2) amp *= (0.5f + lfo1Value * 0.5f);
        if (m_lfo2Target == 2) amp *= (0.5f + lfo2Value * 0.5f);
        
        // Master volume
        mixedSample *= amp * m_masterVolume.load();
        
        outputL[sample] = mixedSample;
        outputR[sample] = mixedSample;
    }
    
    updateVisualState();
}

float PaletteProcessor::processVoice(Voice& voice) {
    // Get frequency from note
    float freq = 440.0f * std::pow(2.0f, (voice.noteNumber - 69) / 12.0f);
    
    // Apply detune
    float freq1 = freq * std::pow(2.0f, m_osc1Detune.load() / 1200.0f);
    float freq2 = freq * std::pow(2.0f, m_osc2Detune.load() / 1200.0f);
    
    // FM modulation: Osc1 -> Osc2
    float fmAmount = m_fmAmount.load() * PaletteConfig::MAX_FM_AMOUNT;
    float osc1Sample = readWavetable(m_osc1Type, voice.phase1) * m_osc1Level.load();
    
    // Calculate phase increment with FM
    float phaseInc1 = freq1 / static_cast<float>(m_sampleRate);
    float phaseInc2 = (freq2 + osc1Sample * fmAmount) / static_cast<float>(m_sampleRate);
    
    // Read oscillators
    float osc2Sample = readWavetable(m_osc2Type, voice.phase2) * m_osc2Level.load();
    
    // Update phases
    voice.phase1 += phaseInc1;
    if (voice.phase1 >= 1.0f) voice.phase1 -= 1.0f;
    voice.phase2 += phaseInc2;
    while (voice.phase2 >= 1.0f) voice.phase2 -= 1.0f;
    while (voice.phase2 < 0.0f) voice.phase2 += 1.0f;
    
    // Mix oscillators
    float mixed = osc1Sample + osc2Sample;
    
    // Apply amplitude envelope
    float ampEnv = processEnvelope(voice.ampEnv);
    mixed *= ampEnv * voice.velocity;
    
    // Check if voice should be released
    if (voice.ampEnv.stage == ADSREnvelope::Stage::IDLE) {
        voice.active = false;
    }
    
    return mixed;
}

float PaletteProcessor::readWavetable(WavetableType type, float phase) {
    int idx = static_cast<int>(type);
    if (idx < 0 || idx >= 4) return 0.0f;
    
    const auto& table = m_wavetables[idx];
    float scaledPhase = phase * PaletteConfig::WAVETABLE_SIZE;
    int index = static_cast<int>(scaledPhase) % PaletteConfig::WAVETABLE_SIZE;
    int nextIndex = (index + 1) % PaletteConfig::WAVETABLE_SIZE;
    float frac = scaledPhase - std::floor(scaledPhase);
    
    return table[index] * (1.0f - frac) + table[nextIndex] * frac;
}

float PaletteProcessor::processFilter(float input) {
    // State Variable Filter
    float cutoff = m_filterCutoff.load();
    float resonance = m_filterResonance.load();
    
    float f = 2.0f * std::sin(juce::MathConstants<float>::pi * cutoff / static_cast<float>(m_sampleRate));
    f = std::min(f, 0.99f);
    
    float q = std::sqrt(1.0f - std::atan(std::sqrt(resonance)) * 2.0f / juce::MathConstants<float>::pi);
    q = std::max(q, 0.01f);
    
    // SVF algorithm
    float lowpass = m_filterState2 + f * m_filterState1;
    float highpass = input - lowpass - q * m_filterState1;
    float bandpass = f * highpass + m_filterState1;
    
    m_filterState1 = bandpass;
    m_filterState2 = lowpass;
    
    switch (m_filterType) {
        case FilterType::LOWPASS: return lowpass;
        case FilterType::HIGHPASS: return highpass;
        case FilterType::BANDPASS: return bandpass;
        default: return lowpass;
    }
}

float PaletteProcessor::processEnvelope(ADSREnvelope& env) {
    float sampleTime = 1.0f / static_cast<float>(m_sampleRate);
    
    switch (env.stage) {
        case ADSREnvelope::Stage::ATTACK:
            env.level += sampleTime / env.attack;
            if (env.level >= 1.0f) {
                env.level = 1.0f;
                env.stage = ADSREnvelope::Stage::DECAY;
            }
            break;
            
        case ADSREnvelope::Stage::DECAY:
            env.level -= (1.0f - env.sustain) * sampleTime / env.decay;
            if (env.level <= env.sustain) {
                env.level = env.sustain;
                env.stage = ADSREnvelope::Stage::SUSTAIN;
            }
            break;
            
        case ADSREnvelope::Stage::SUSTAIN:
            env.level = env.sustain;
            break;
            
        case ADSREnvelope::Stage::RELEASE:
            env.level -= env.releaseLevel * sampleTime / env.release;
            if (env.level <= 0.0f) {
                env.level = 0.0f;
                env.stage = ADSREnvelope::Stage::IDLE;
            }
            break;
            
        case ADSREnvelope::Stage::IDLE:
        default:
            env.level = 0.0f;
            break;
    }
    
    return env.level;
}

void PaletteProcessor::handleMidiEvent(const juce::MidiMessage& msg) {
    if (msg.isNoteOn()) {
        noteOn(msg.getNoteNumber(), msg.getFloatVelocity());
    } else if (msg.isNoteOff()) {
        noteOff(msg.getNoteNumber());
    }
}

void PaletteProcessor::noteOn(int note, float velocity) {
    // Find free voice
    for (auto& voice : m_voices) {
        if (!voice.active) {
            voice.active = true;
            voice.noteNumber = note;
            voice.velocity = velocity;
            voice.phase1 = 0.0f;
            voice.phase2 = 0.0f;
            
            // Copy envelope templates
            voice.ampEnv = m_ampEnvTemplate;
            voice.ampEnv.stage = ADSREnvelope::Stage::ATTACK;
            voice.ampEnv.level = 0.0f;
            
            voice.filterEnv = m_filterEnvTemplate;
            voice.filterEnv.stage = ADSREnvelope::Stage::ATTACK;
            voice.filterEnv.level = 0.0f;
            
            return;
        }
    }
    
    // Voice stealing: replace oldest voice
    m_voices[0].active = true;
    m_voices[0].noteNumber = note;
    m_voices[0].velocity = velocity;
    m_voices[0].phase1 = 0.0f;
    m_voices[0].phase2 = 0.0f;
    m_voices[0].ampEnv.stage = ADSREnvelope::Stage::ATTACK;
    m_voices[0].ampEnv.level = 0.0f;
}

void PaletteProcessor::noteOff(int note) {
    for (auto& voice : m_voices) {
        if (voice.active && voice.noteNumber == note) {
            voice.ampEnv.stage = ADSREnvelope::Stage::RELEASE;
            voice.ampEnv.releaseLevel = voice.ampEnv.level;
            voice.filterEnv.stage = ADSREnvelope::Stage::RELEASE;
            voice.filterEnv.releaseLevel = voice.filterEnv.level;
        }
    }
}

void PaletteProcessor::updateVisualState() {
    std::lock_guard<std::mutex> lock(m_visualMutex);
    
    // Filter cutoff -> blur strength
    float normalizedCutoff = (m_filterCutoff.load() - 20.0f) / 19980.0f;
    m_visualState.blurStrength = 1.0f - normalizedCutoff;
    
    // Resonance -> edge sharpening (coffee ring)
    m_visualState.edgeSharpening = m_filterResonance.load();
    
    // Wavetable position -> color
    // Blue (Sine) -> Red (Saw) -> Yellow (Square)
    switch (m_osc1Type) {
        case WavetableType::SINE:
            m_visualState.colorR = 0.2f;
            m_visualState.colorG = 0.4f;
            m_visualState.colorB = 0.9f;
            break;
        case WavetableType::SAW:
            m_visualState.colorR = 0.9f;
            m_visualState.colorG = 0.3f;
            m_visualState.colorB = 0.2f;
            break;
        case WavetableType::SQUARE:
            m_visualState.colorR = 0.9f;
            m_visualState.colorG = 0.9f;
            m_visualState.colorB = 0.2f;
            break;
        default:
            m_visualState.colorR = 0.5f;
            m_visualState.colorG = 0.5f;
            m_visualState.colorB = 0.5f;
    }
}

void PaletteProcessor::applyAISuggestion(const juce::String& suggestion) {
    if (suggestion.containsIgnoreCase("Ice") || suggestion.containsIgnoreCase("cold")) {
        setFilterType(FilterType::HIGHPASS);
        setOsc1Wavetable(WavetableType::SQUARE);
        // Cyan color is handled in updateVisualState
        setFilterCutoff(2000.0f);
        setFilterResonance(0.7f);
    }
    else if (suggestion.containsIgnoreCase("Lava") || suggestion.containsIgnoreCase("hot") || 
             suggestion.containsIgnoreCase("warm")) {
        setFilterType(FilterType::LOWPASS);
        setOsc1Wavetable(WavetableType::SAW);
        setOsc2Wavetable(WavetableType::SAW);
        setOsc2Detune(7.0f);  // Slight detune
        setFilterCutoff(800.0f);
        setFilterResonance(0.4f);
    }
}

// Parameter setters
void PaletteProcessor::setOsc1Wavetable(WavetableType type) { m_osc1Type = type; }
void PaletteProcessor::setOsc1Position(float pos) { m_osc1Position.store(pos); }
void PaletteProcessor::setOsc1Level(float level) { m_osc1Level.store(std::clamp(level, 0.0f, 1.0f)); }
void PaletteProcessor::setOsc1Detune(float cents) { m_osc1Detune.store(std::clamp(cents, -100.0f, 100.0f)); }

void PaletteProcessor::setOsc2Wavetable(WavetableType type) { m_osc2Type = type; }
void PaletteProcessor::setOsc2Position(float pos) { m_osc2Position.store(pos); }
void PaletteProcessor::setOsc2Level(float level) { m_osc2Level.store(std::clamp(level, 0.0f, 1.0f)); }
void PaletteProcessor::setOsc2Detune(float cents) { m_osc2Detune.store(std::clamp(cents, -100.0f, 100.0f)); }

void PaletteProcessor::setFMAmount(float amount) { m_fmAmount.store(std::clamp(amount, 0.0f, 1.0f)); }

void PaletteProcessor::setFilterType(FilterType type) { m_filterType = type; }
void PaletteProcessor::setFilterCutoff(float hz) { m_filterCutoff.store(std::clamp(hz, 20.0f, 20000.0f)); }
void PaletteProcessor::setFilterResonance(float q) { m_filterResonance.store(std::clamp(q, 0.0f, 1.0f)); }
void PaletteProcessor::setFilterEnvAmount(float amount) { m_filterEnvAmount.store(amount); }

void PaletteProcessor::setAmpEnvelope(float a, float d, float s, float r) {
    m_ampEnvTemplate.attack = std::max(a, 0.001f);
    m_ampEnvTemplate.decay = std::max(d, 0.001f);
    m_ampEnvTemplate.sustain = std::clamp(s, 0.0f, 1.0f);
    m_ampEnvTemplate.release = std::max(r, 0.001f);
}

void PaletteProcessor::setFilterEnvelope(float a, float d, float s, float r) {
    m_filterEnvTemplate.attack = std::max(a, 0.001f);
    m_filterEnvTemplate.decay = std::max(d, 0.001f);
    m_filterEnvTemplate.sustain = std::clamp(s, 0.0f, 1.0f);
    m_filterEnvTemplate.release = std::max(r, 0.001f);
}

void PaletteProcessor::setLFO1(float rate, float depth, WavetableType shape) {
    m_lfo1.rate = std::clamp(rate, 0.01f, 20.0f);
    m_lfo1.depth = std::clamp(depth, 0.0f, 1.0f);
    m_lfo1.shape = shape;
}

void PaletteProcessor::setLFO2(float rate, float depth, WavetableType shape) {
    m_lfo2.rate = std::clamp(rate, 0.01f, 20.0f);
    m_lfo2.depth = std::clamp(depth, 0.0f, 1.0f);
    m_lfo2.shape = shape;
}

void PaletteProcessor::setLFO1Target(int target) { m_lfo1Target = std::clamp(target, 0, 2); }
void PaletteProcessor::setLFO2Target(int target) { m_lfo2Target = std::clamp(target, 0, 2); }
void PaletteProcessor::setMasterVolume(float volume) { m_masterVolume.store(std::clamp(volume, 0.0f, 1.0f)); }

WatercolorVisualState PaletteProcessor::getVisualState() const {
    std::lock_guard<std::mutex> lock(m_visualMutex);
    return m_visualState;
}

void PaletteProcessor::getStateInformation(juce::MemoryBlock&) {}
void PaletteProcessor::setStateInformation(const void*, int) {}

juce::AudioProcessorEditor* PaletteProcessor::createEditor() {
    return new juce::GenericAudioProcessorEditor(*this);
}

} // namespace iDAW

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter() {
    return new iDAW::PaletteProcessor();
}
