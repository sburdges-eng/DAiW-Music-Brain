/**
 * HarmonyEngine.cpp - Implementation of C++ Harmony Analysis Engine
 */

#include "harmony/HarmonyEngine.h"
#include "harmony/Chord.h"
#include "harmony/Progression.h"
#include <algorithm>
#include <regex>
#include <sstream>
#include <cctype>
#include <cmath>
#include <set>

namespace iDAW {
namespace harmony {

// ============================================================================
// Chord Implementation
// ============================================================================

Chord::Chord(const std::vector<int>& midiNotes) {
    if (midiNotes.size() < 2) {
        m_quality = ChordQuality::Unknown;
        return;
    }
    
    // Get pitch classes
    std::set<int> pitchClasses;
    for (int note : midiNotes) {
        pitchClasses.insert(midiToPitchClass(note));
    }
    
    if (pitchClasses.size() < 2) {
        m_quality = ChordQuality::Unknown;
        return;
    }
    
    // Try each pitch class as potential root
    float bestScore = 0.0f;
    int bestRoot = 0;
    ChordQuality bestQuality = ChordQuality::Unknown;
    
    for (int potentialRoot : pitchClasses) {
        // Calculate intervals from this root
        std::vector<int> intervals;
        for (int pc : pitchClasses) {
            intervals.push_back((pc - potentialRoot + 12) % 12);
        }
        std::sort(intervals.begin(), intervals.end());
        
        // Try to match against chord templates
        for (const auto& tmpl : getChordTemplates()) {
            std::vector<int> tmplIntervals = tmpl.intervals;
            std::sort(tmplIntervals.begin(), tmplIntervals.end());
            
            // Count matches
            int matches = 0;
            for (int interval : intervals) {
                if (std::find(tmplIntervals.begin(), tmplIntervals.end(), interval) 
                    != tmplIntervals.end()) {
                    matches++;
                }
            }
            
            float coverage = static_cast<float>(matches) / tmplIntervals.size();
            if (coverage > bestScore && coverage >= 0.7f) {
                bestScore = coverage;
                bestRoot = potentialRoot;
                bestQuality = tmpl.quality;
            }
        }
    }
    
    // If no quality match, default to major/minor based on 3rd
    if (bestQuality == ChordQuality::Unknown && pitchClasses.size() >= 2) {
        auto it = pitchClasses.begin();
        int root = *it;
        
        std::vector<int> intervals;
        for (int pc : pitchClasses) {
            intervals.push_back((pc - root + 12) % 12);
        }
        
        if (std::find(intervals.begin(), intervals.end(), 3) != intervals.end()) {
            bestQuality = ChordQuality::Minor;
        } else if (std::find(intervals.begin(), intervals.end(), 4) != intervals.end()) {
            bestQuality = ChordQuality::Major;
        } else {
            bestQuality = ChordQuality::Major;  // Default
        }
        bestRoot = root;
    }
    
    m_root = bestRoot;
    m_quality = bestQuality;
    m_bass = -1;
    m_notes = midiNotes;
}

std::optional<Chord> Chord::fromString(const std::string& chordStr) {
    return parseChordString(chordStr);
}

std::string Chord::name(bool useFlats) const {
    if (m_quality == ChordQuality::Unknown) {
        return "?";
    }
    
    std::string rootName = useFlats ? FLAT_NAMES[m_root % 12] : NOTE_NAMES[m_root % 12];
    std::string qualityStr = qualityToString(m_quality);
    std::string result = rootName + qualityStr;
    
    if (hasBass()) {
        std::string bassName = useFlats ? FLAT_NAMES[m_bass % 12] : NOTE_NAMES[m_bass % 12];
        result += "/" + bassName;
    }
    
    return result;
}

std::string Chord::rootName(bool useFlats) const {
    return useFlats ? FLAT_NAMES[m_root % 12] : NOTE_NAMES[m_root % 12];
}

std::vector<int> Chord::intervals() const {
    for (const auto& tmpl : getChordTemplates()) {
        if (tmpl.quality == m_quality) {
            return tmpl.intervals;
        }
    }
    return {0, 4, 7};  // Default major
}

bool Chord::hasInterval(int interval) const {
    auto ints = intervals();
    return std::find(ints.begin(), ints.end(), interval % 12) != ints.end();
}

std::vector<int> Chord::midiNotes(int octave) const {
    std::vector<int> result;
    int baseMidi = (octave + 1) * 12 + m_root;
    
    for (int interval : intervals()) {
        result.push_back(baseMidi + interval);
    }
    
    return result;
}

// ============================================================================
// Chord Parsing
// ============================================================================

// Flat to sharp conversion
static const std::map<std::string, std::string> FLAT_TO_SHARP = {
    {"Db", "C#"}, {"Eb", "D#"}, {"Fb", "E"}, {"Gb", "F#"},
    {"Ab", "G#"}, {"Bb", "A#"}, {"Cb", "B"}
};

std::optional<Chord> parseChordString(const std::string& chordStr) {
    if (chordStr.empty()) {
        return std::nullopt;
    }
    
    std::string str = chordStr;
    
    // Handle slash chords
    int bass = -1;
    size_t slashPos = str.find('/');
    if (slashPos != std::string::npos && slashPos < str.length() - 1) {
        std::string bassStr = str.substr(slashPos + 1);
        str = str.substr(0, slashPos);
        
        // Parse bass note
        if (!bassStr.empty()) {
            char bassRoot = std::toupper(bassStr[0]);
            if (bassRoot >= 'A' && bassRoot <= 'G') {
                int bassIdx = 0;
                for (size_t i = 0; i < 12; i++) {
                    if (NOTE_NAMES[i][0] == bassRoot) {
                        bassIdx = i;
                        break;
                    }
                }
                if (bassStr.length() > 1) {
                    if (bassStr[1] == '#') bassIdx = (bassIdx + 1) % 12;
                    else if (bassStr[1] == 'b') bassIdx = (bassIdx + 11) % 12;
                }
                bass = bassIdx;
            }
        }
    }
    
    // Extract root
    if (str.empty()) return std::nullopt;
    
    char rootChar = std::toupper(str[0]);
    if (rootChar < 'A' || rootChar > 'G') return std::nullopt;
    
    size_t rootLen = 1;
    int rootIdx = 0;
    
    // Find root in note names
    for (size_t i = 0; i < 12; i++) {
        if (NOTE_NAMES[i][0] == rootChar) {
            rootIdx = i;
            break;
        }
    }
    
    // Check for sharp/flat
    if (str.length() > 1) {
        if (str[1] == '#') {
            rootIdx = (rootIdx + 1) % 12;
            rootLen = 2;
        } else if (str[1] == 'b') {
            rootIdx = (rootIdx + 11) % 12;
            rootLen = 2;
        }
    }
    
    std::string remainder = str.substr(rootLen);
    
    // Parse quality
    ChordQuality quality = ChordQuality::Major;
    
    // Check for major7 first (before minor check)
    if (remainder.rfind("maj7", 0) == 0 || remainder.rfind("Maj7", 0) == 0 || 
        remainder.rfind("M7", 0) == 0) {
        quality = ChordQuality::Major7;
    }
    else if (remainder.rfind("maj", 0) == 0 || remainder.rfind("Maj", 0) == 0) {
        quality = ChordQuality::Major;
    }
    else if (remainder.rfind("min", 0) == 0 || remainder.rfind("m", 0) == 0 || 
             remainder[0] == '-') {
        // Check for min7
        if (remainder.find("7") != std::string::npos) {
            quality = ChordQuality::Minor7;
        } else {
            quality = ChordQuality::Minor;
        }
    }
    else if (remainder.rfind("dim", 0) == 0 || remainder[0] == 'o') {
        if (remainder.find("7") != std::string::npos) {
            quality = ChordQuality::Dim7;
        } else {
            quality = ChordQuality::Diminished;
        }
    }
    else if (remainder[0] == '+' || remainder.rfind("aug", 0) == 0) {
        quality = ChordQuality::Augmented;
    }
    else if (remainder.rfind("sus2", 0) == 0) {
        quality = ChordQuality::Sus2;
    }
    else if (remainder.rfind("sus4", 0) == 0 || remainder.rfind("sus", 0) == 0) {
        quality = ChordQuality::Sus4;
    }
    else if (remainder.rfind("7", 0) == 0) {
        quality = ChordQuality::Dominant7;
    }
    else if (remainder.rfind("6", 0) == 0) {
        quality = ChordQuality::Major6;
    }
    else if (remainder.rfind("add9", 0) == 0) {
        quality = ChordQuality::Add9;
    }
    
    return Chord(rootIdx, quality, bass);
}

std::vector<Chord> parseProgressionString(const std::string& progressionStr) {
    std::vector<Chord> result;
    
    // Split by common delimiters
    std::regex delimRegex("[-–—\\s|,]+");
    std::sregex_token_iterator it(progressionStr.begin(), progressionStr.end(), delimRegex, -1);
    std::sregex_token_iterator end;
    
    for (; it != end; ++it) {
        std::string chordStr = it->str();
        if (!chordStr.empty()) {
            auto chord = parseChordString(chordStr);
            if (chord) {
                result.push_back(*chord);
            }
        }
    }
    
    return result;
}

Chord detectChord(const std::vector<int>& midiNotes) {
    return Chord(midiNotes);
}

// ============================================================================
// Progression Implementation
// ============================================================================

Progression::Progression(const std::vector<Chord>& chords)
    : m_chords(chords) {
    if (!m_chords.empty()) {
        analyze();
    }
}

std::optional<Progression> Progression::fromString(const std::string& progressionStr) {
    auto chords = parseProgressionString(progressionStr);
    if (chords.empty()) {
        return std::nullopt;
    }
    return Progression(chords);
}

void Progression::addChord(const Chord& chord) {
    m_chords.push_back(chord);
    m_analyzed = false;
}

Key Progression::detectKey() const {
    if (m_chords.empty()) {
        return Key{0, Mode::Major};
    }
    
    // Weight first and last chords more heavily
    std::map<int, float> rootWeights;
    for (size_t i = 0; i < m_chords.size(); i++) {
        float weight = 1.0f;
        if (i == 0) weight = 2.0f;
        else if (i == m_chords.size() - 1) weight = 1.5f;
        
        int root = m_chords[i].root();
        rootWeights[root] += weight;
    }
    
    // Find most weighted root
    int likelyRoot = 0;
    float maxWeight = 0.0f;
    for (const auto& [root, weight] : rootWeights) {
        if (weight > maxWeight) {
            maxWeight = weight;
            likelyRoot = root;
        }
    }
    
    // Determine mode based on tonic chord quality
    Mode mode = Mode::Major;
    for (const auto& chord : m_chords) {
        if (chord.root() == likelyRoot) {
            if (chord.quality() == ChordQuality::Minor ||
                chord.quality() == ChordQuality::Minor7) {
                mode = Mode::Minor;
                break;
            }
        }
    }
    
    return Key{likelyRoot, mode};
}

void Progression::analyze() {
    m_key = detectKey();
    m_romanNumerals.clear();
    
    for (const auto& chord : m_chords) {
        m_romanNumerals.push_back(getRomanNumeral(chord));
    }
    
    m_analyzed = true;
}

std::string Progression::getRomanNumeral(const Chord& chord) const {
    int interval = (chord.root() - m_key.root + 12) % 12;
    
    // Roman numeral map
    static const std::map<int, std::string> numeralMap = {
        {0, "I"}, {1, "bII"}, {2, "II"}, {3, "bIII"}, {4, "III"},
        {5, "IV"}, {6, "#IV"}, {7, "V"}, {8, "bVI"}, {9, "VI"},
        {10, "bVII"}, {11, "VII"}
    };
    
    auto it = numeralMap.find(interval);
    std::string numeral = (it != numeralMap.end()) ? it->second : "?";
    
    // Make lowercase for minor/diminished
    if (chord.quality() == ChordQuality::Minor ||
        chord.quality() == ChordQuality::Minor7 ||
        chord.quality() == ChordQuality::Diminished ||
        chord.quality() == ChordQuality::Dim7 ||
        chord.quality() == ChordQuality::HalfDim7) {
        std::transform(numeral.begin(), numeral.end(), numeral.begin(), ::tolower);
    }
    
    // Add quality markers
    if (chord.quality() == ChordQuality::Diminished ||
        chord.quality() == ChordQuality::Dim7) {
        numeral += "°";
    } else if (chord.quality() == ChordQuality::Dominant7) {
        numeral += "7";
    } else if (chord.quality() == ChordQuality::Major7) {
        numeral += "M7";
    } else if (chord.quality() == ChordQuality::Minor7) {
        numeral += "7";
    } else if (chord.quality() == ChordQuality::Augmented) {
        numeral += "+";
    }
    
    return numeral;
}

std::map<std::string, std::string> Progression::identifyBorrowedChords() const {
    std::map<std::string, std::string> borrowed;
    
    if (m_key.mode != Mode::Major) {
        return borrowed;  // Only analyze borrowing in major keys for now
    }
    
    for (const auto& chord : m_chords) {
        int interval = (chord.root() - m_key.root + 12) % 12;
        
        // Common borrowed chord patterns
        if (interval == 3 && chord.quality() == ChordQuality::Major) {
            borrowed[chord.name()] = "parallel minor (bIII)";
        } else if (interval == 8 && chord.quality() == ChordQuality::Major) {
            borrowed[chord.name()] = "parallel minor (bVI)";
        } else if (interval == 10 && chord.quality() == ChordQuality::Major) {
            borrowed[chord.name()] = "mixolydian/parallel minor (bVII)";
        } else if (interval == 5 && chord.quality() == ChordQuality::Minor) {
            borrowed[chord.name()] = "parallel minor (iv)";
        }
    }
    
    return borrowed;
}

bool Progression::isDiatonic(const Chord& chord) const {
    int interval = (chord.root() - m_key.root + 12) % 12;
    auto scale = getScaleDegrees(m_key.mode);
    return std::find(scale.begin(), scale.end(), interval) != scale.end();
}

std::string Progression::toString() const {
    std::ostringstream oss;
    for (size_t i = 0; i < m_chords.size(); i++) {
        if (i > 0) oss << " - ";
        oss << m_chords[i].name();
    }
    return oss.str();
}

// ============================================================================
// HarmonyEngine Implementation
// ============================================================================

HarmonyEngine& HarmonyEngine::getInstance() {
    static HarmonyEngine instance;
    return instance;
}

Chord HarmonyEngine::detectChord(const std::vector<int>& midiNotes) const {
    return harmony::detectChord(midiNotes);
}

DiagnosisResult HarmonyEngine::diagnoseProgression(const std::string& progressionStr) const {
    DiagnosisResult result;
    
    auto chords = parseProgressionString(progressionStr);
    if (chords.empty()) {
        result.success = false;
        result.issues.push_back("Could not parse chord progression");
        result.suggestions.push_back("Check chord spelling");
        return result;
    }
    
    Progression prog(chords);
    result.detectedKey = prog.key();
    
    for (const auto& chord : chords) {
        result.chordNames.push_back(chord.name());
    }
    
    // Analyze each chord
    auto scale = getScaleDegrees(result.detectedKey.mode);
    
    for (size_t i = 0; i < chords.size(); i++) {
        const auto& chord = chords[i];
        int interval = (chord.root() - result.detectedKey.root + 12) % 12;
        
        // Check if root is diatonic
        if (std::find(scale.begin(), scale.end(), interval) == scale.end()) {
            std::string issue;
            if (interval == 3 && result.detectedKey.mode == Mode::Major) {
                issue = chord.name() + ": bIII (borrowed from parallel minor)";
                result.borrowedChords[chord.name()] = "parallel minor (bIII)";
            } else if (interval == 8 && result.detectedKey.mode == Mode::Major) {
                issue = chord.name() + ": bVI (borrowed from parallel minor)";
                result.borrowedChords[chord.name()] = "parallel minor (bVI)";
            } else if (interval == 10 && result.detectedKey.mode == Mode::Major) {
                issue = chord.name() + ": bVII (borrowed/mixolydian)";
                result.borrowedChords[chord.name()] = "mixolydian/parallel minor (bVII)";
            } else {
                issue = chord.name() + ": non-diatonic root (" + 
                        std::string(NOTE_NAMES[interval]) + " in " + 
                        result.detectedKey.toString() + ")";
            }
            result.issues.push_back(issue);
        }
        
        // Check voice leading
        if (i > 0) {
            const auto& prevChord = chords[i - 1];
            int rootMotion = (chord.root() - prevChord.root() + 12) % 12;
            if (rootMotion == 6) {  // Tritone motion
                result.suggestions.push_back(
                    "Tritone motion between " + prevChord.name() + " and " + 
                    chord.name() + " - can feel unstable");
            }
        }
    }
    
    // Check resolution
    const auto& lastChord = chords.back();
    int lastInterval = (lastChord.root() - result.detectedKey.root + 12) % 12;
    if (lastInterval != 0 && lastInterval != 7) {
        result.suggestions.push_back(
            "Progression ends on " + lastChord.name() + 
            " - consider resolving to " + std::string(NOTE_NAMES[result.detectedKey.root]));
    }
    
    // Check for V-I
    bool hasDominant = false;
    bool hasTonic = false;
    for (const auto& chord : chords) {
        int interval = (chord.root() - result.detectedKey.root + 12) % 12;
        if (interval == 7) hasDominant = true;
        if (interval == 0) hasTonic = true;
    }
    
    if (!hasDominant && hasTonic) {
        result.suggestions.push_back(
            "No dominant (V) chord - consider adding for stronger resolution");
    }
    
    return result;
}

Key HarmonyEngine::detectKey(const Progression& progression) const {
    return progression.detectKey();
}

Key HarmonyEngine::detectKey(const std::vector<Chord>& chords) const {
    Progression prog(chords);
    return prog.detectKey();
}

std::string HarmonyEngine::getRomanNumeral(const Chord& chord, const Key& key) const {
    Progression prog;
    prog.addChord(chord);
    // Manually set key (would need to expose this in Progression)
    return prog.getRomanNumeral(chord);
}

std::map<std::string, std::string> HarmonyEngine::identifyBorrowedChords(
    const Progression& progression) const {
    return progression.identifyBorrowedChords();
}

bool HarmonyEngine::isDiatonic(const Chord& chord, const Key& key) const {
    int interval = (chord.root() - key.root + 12) % 12;
    auto scale = getScaleDegrees(key.mode);
    return std::find(scale.begin(), scale.end(), interval) != scale.end();
}

int HarmonyEngine::getInterval(const Chord& chord, const Key& key) const {
    return (chord.root() - key.root + 12) % 12;
}

std::vector<ReharmSuggestion> HarmonyEngine::generateReharmonizations(
    const std::string& progressionStr,
    const std::string& style,
    int count) const {
    
    std::vector<ReharmSuggestion> suggestions;
    
    auto chords = parseProgressionString(progressionStr);
    if (chords.empty()) {
        return suggestions;
    }
    
    Progression prog(chords);
    Key key = prog.key();
    
    // Tritone substitution
    if (style == "jazz" || style == "all") {
        ReharmSuggestion tritone;
        tritone.technique = ReharmTechnique::TritoneSubstitution;
        tritone.mood = "chromatic, sophisticated";
        tritone.description = "Replace dominant chords with tritone substitutions";
        
        for (const auto& chord : chords) {
            int interval = (chord.root() - key.root + 12) % 12;
            if (interval == 7 && (chord.quality() == ChordQuality::Dominant7 ||
                                  chord.quality() == ChordQuality::Major)) {
                // Tritone sub
                int newRoot = (chord.root() + 6) % 12;
                tritone.chords.push_back(Chord(newRoot, ChordQuality::Dominant7));
            } else {
                tritone.chords.push_back(chord);
            }
        }
        suggestions.push_back(tritone);
    }
    
    // Borrowed chords from parallel
    if (style == "pop" || style == "all") {
        ReharmSuggestion borrowed;
        borrowed.technique = ReharmTechnique::BorrowedFromParallel;
        borrowed.mood = "bittersweet, nostalgic";
        borrowed.description = "Borrow chords from parallel minor";
        
        for (const auto& chord : chords) {
            int interval = (chord.root() - key.root + 12) % 12;
            if (interval == 5 && chord.quality() == ChordQuality::Major) {
                // IV -> iv
                borrowed.chords.push_back(Chord(chord.root(), ChordQuality::Minor));
            } else {
                borrowed.chords.push_back(chord);
            }
        }
        suggestions.push_back(borrowed);
    }
    
    // Sus chords
    {
        ReharmSuggestion sus;
        sus.technique = ReharmTechnique::SusChords;
        sus.mood = "open, unresolved";
        sus.description = "Replace some chords with sus variants";
        
        for (const auto& chord : chords) {
            if (chord.quality() == ChordQuality::Major) {
                sus.chords.push_back(Chord(chord.root(), ChordQuality::Sus4));
            } else if (chord.quality() == ChordQuality::Minor) {
                sus.chords.push_back(Chord(chord.root(), ChordQuality::Sus2));
            } else {
                sus.chords.push_back(chord);
            }
        }
        suggestions.push_back(sus);
    }
    
    // Limit to requested count
    if (suggestions.size() > static_cast<size_t>(count)) {
        suggestions.resize(count);
    }
    
    return suggestions;
}

} // namespace harmony
} // namespace iDAW
