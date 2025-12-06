/**
 * test_main.cpp - iDAW Core Test Suite Entry Point
 * 
 * Runs all stress tests and core module tests.
 * 
 * Build: cmake --build . --target idaw_tests
 * Run: ./idaw_tests
 */

#include "StressTestSuite.h"
#include "../include/HarmonyCore.h"
#include "../include/GrooveCore.h"
#include "../include/DiagnosticsCore.h"
#include "../include/OSCHandler.h"

#include <iostream>
#include <iomanip>
#include <vector>
#include <string>

using namespace iDAW;

// =============================================================================
// Test Framework
// =============================================================================

struct TestCase {
    std::string name;
    bool (*testFunc)();
};

int g_passCount = 0;
int g_failCount = 0;

#define TEST(name) { #name, test_##name }
#define ASSERT(cond) do { if (!(cond)) { std::cerr << "  FAIL: " << #cond << std::endl; return false; } } while(0)
#define ASSERT_EQ(a, b) do { if ((a) != (b)) { std::cerr << "  FAIL: " << #a << " != " << #b << std::endl; return false; } } while(0)
#define ASSERT_NEAR(a, b, tol) do { if (std::abs((a) - (b)) > (tol)) { std::cerr << "  FAIL: " << #a << " not near " << #b << std::endl; return false; } } while(0)

// =============================================================================
// Harmony Core Tests
// =============================================================================

bool test_HarmonyMidiToPitchClass() {
    ASSERT_EQ(Harmony::midiToPitchClass(60), 0);   // C4
    ASSERT_EQ(Harmony::midiToPitchClass(61), 1);   // C#4
    ASSERT_EQ(Harmony::midiToPitchClass(69), 9);   // A4
    ASSERT_EQ(Harmony::midiToPitchClass(72), 0);   // C5
    return true;
}

bool test_HarmonyChordDetection() {
    // C major chord: C4, E4, G4
    uint8_t cMajor[] = {60, 64, 67};
    Harmony::Chord chord = Harmony::detectChordFromNotes(cMajor, 3);
    
    ASSERT(chord.isValid());
    ASSERT_EQ(chord.root, 0);  // C
    ASSERT_EQ(chord.quality, Harmony::ChordQuality::Major);
    ASSERT(chord.confidence > 0.5f);
    
    return true;
}

bool test_HarmonyMinorChordDetection() {
    // A minor chord: A4, C5, E5
    uint8_t aMinor[] = {69, 72, 76};
    Harmony::Chord chord = Harmony::detectChordFromNotes(aMinor, 3);
    
    ASSERT(chord.isValid());
    ASSERT_EQ(chord.root, 9);  // A
    ASSERT_EQ(chord.quality, Harmony::ChordQuality::Minor);
    
    return true;
}

bool test_HarmonyDominant7Detection() {
    // G7 chord: G, B, D, F
    uint8_t g7[] = {55, 59, 62, 65};
    Harmony::Chord chord = Harmony::detectChordFromNotes(g7, 4);
    
    ASSERT(chord.isValid());
    ASSERT_EQ(chord.root, 7);  // G
    ASSERT_EQ(chord.quality, Harmony::ChordQuality::Dominant7);
    
    return true;
}

bool test_HarmonyKeyDetection() {
    // C major progression: C, F, G, C
    Harmony::Chord chords[4];
    chords[0].root = 0;  // C
    chords[0].quality = Harmony::ChordQuality::Major;
    chords[1].root = 5;  // F
    chords[1].quality = Harmony::ChordQuality::Major;
    chords[2].root = 7;  // G
    chords[2].quality = Harmony::ChordQuality::Major;
    chords[3].root = 0;  // C
    chords[3].quality = Harmony::ChordQuality::Major;
    
    Harmony::KeyResult key = Harmony::detectKey(chords, 4);
    
    ASSERT_EQ(key.keyRoot, 0);  // C
    ASSERT_EQ(key.mode, Harmony::Mode::Major);
    
    return true;
}

bool test_HarmonyRomanNumerals() {
    Harmony::Chord fMajor;
    fMajor.root = 5;  // F
    fMajor.quality = Harmony::ChordQuality::Major;
    
    Harmony::RomanNumeralResult rn = Harmony::getRomanNumeral(fMajor, 0, Harmony::Mode::Major);
    
    ASSERT_EQ(rn.numeral, "IV");
    ASSERT(rn.isDiatonic);
    
    return true;
}

bool test_HarmonyBorrowedChord() {
    // Bbm in F major context (iv borrowed from parallel minor)
    Harmony::Chord bbMinor;
    bbMinor.root = 10;  // Bb
    bbMinor.quality = Harmony::ChordQuality::Minor;
    
    Harmony::RomanNumeralResult rn = Harmony::getRomanNumeral(bbMinor, 5, Harmony::Mode::Major);
    
    ASSERT(!rn.isDiatonic);  // Bb minor is not diatonic to F major
    
    return true;
}

// =============================================================================
// Groove Core Tests
// =============================================================================

bool test_GrooveSwingCalculation() {
    Groove::NoteEvent events[4];
    events[0].startTick = 0;
    events[0].velocity = 100;
    events[1].startTick = 240;   // 8th note (straight)
    events[1].velocity = 80;
    events[2].startTick = 480;
    events[2].velocity = 100;
    events[3].startTick = 720;   // 8th note (straight)
    events[3].velocity = 80;
    
    float swing = Groove::calculateSwing(events, 4, 480);
    
    // Straight timing should have ~0 swing
    ASSERT_NEAR(swing, 0.0f, 0.15f);
    
    return true;
}

bool test_GrooveTimingDeviation() {
    int16_t deviation = Groove::calculateTimingDeviation(485, 480, 16);
    
    // 485 is 5 ticks after a 16th note grid at 480 PPQ
    // Grid is at 480 * 4 / 16 = 120 ticks
    // Nearest grid to 485 is 480
    ASSERT_EQ(deviation, 5);
    
    return true;
}

bool test_GrooveTemplateExtraction() {
    Groove::NoteEvent events[4];
    events[0] = {36, 100, 0, 0, 480, 0, false, false};
    events[1] = {38, 80, 0, 480, 480, 0, false, false};
    events[2] = {36, 95, 0, 960, 480, 0, false, false};
    events[3] = {38, 85, 0, 1440, 480, 0, false, false};
    
    Groove::GrooveTemplate tmpl = Groove::extractGroove(events, 4, 480, 120.0f, 16);
    
    ASSERT_EQ(tmpl.eventCount, 4);
    ASSERT_EQ(tmpl.ppq, 480);
    ASSERT_NEAR(tmpl.tempoBpm, 120.0f, 0.01f);
    ASSERT(tmpl.velocityStats.min <= tmpl.velocityStats.max);
    
    return true;
}

bool test_GrooveGenreParams() {
    Groove::GenreGrooveParams funk = Groove::getGenreGrooveParams(Groove::GenreGroove::Funk);
    
    ASSERT(funk.swingFactor > 0.0f);
    ASSERT(funk.swingFactor < 0.2f);
    ASSERT(funk.velocityVariation > 0.0f);
    
    Groove::GenreGrooveParams straight = Groove::getGenreGrooveParams(Groove::GenreGroove::Straight);
    ASSERT_NEAR(straight.swingFactor, 0.0f, 0.01f);
    
    return true;
}

bool test_GrooveHumanize() {
    Groove::NoteEvent events[4];
    for (int i = 0; i < 4; ++i) {
        events[i].startTick = i * 480;
        events[i].velocity = 100;
        events[i].pitch = 36;
    }
    
    // Store original values
    uint32_t origTicks[4];
    uint8_t origVels[4];
    for (int i = 0; i < 4; ++i) {
        origTicks[i] = events[i].startTick;
        origVels[i] = events[i].velocity;
    }
    
    Groove::humanize(events, 4, 15, 10, 42);
    
    // At least some values should have changed
    bool tickChanged = false;
    bool velChanged = false;
    for (int i = 0; i < 4; ++i) {
        if (events[i].startTick != origTicks[i]) tickChanged = true;
        if (events[i].velocity != origVels[i]) velChanged = true;
    }
    
    ASSERT(tickChanged || velChanged);
    
    return true;
}

// =============================================================================
// Diagnostics Core Tests
// =============================================================================

bool test_DiagnosticsNoteNameParsing() {
    ASSERT_EQ(Diagnostics::noteNameToPitchClass("C"), 0);
    ASSERT_EQ(Diagnostics::noteNameToPitchClass("C#"), 1);
    ASSERT_EQ(Diagnostics::noteNameToPitchClass("Db"), 1);
    ASSERT_EQ(Diagnostics::noteNameToPitchClass("A"), 9);
    ASSERT_EQ(Diagnostics::noteNameToPitchClass("Bb"), 10);
    
    return true;
}

bool test_DiagnosticsChordParsing() {
    Diagnostics::ParsedChord am = Diagnostics::parseChordString("Am");
    ASSERT(am.isValid());
    ASSERT_EQ(am.rootNum, 9);  // A
    ASSERT_EQ(am.quality, Harmony::ChordQuality::Minor);
    
    Diagnostics::ParsedChord cmaj7 = Diagnostics::parseChordString("Cmaj7");
    ASSERT(cmaj7.isValid());
    ASSERT_EQ(cmaj7.rootNum, 0);  // C
    ASSERT_EQ(cmaj7.quality, Harmony::ChordQuality::Major7);
    
    Diagnostics::ParsedChord g7 = Diagnostics::parseChordString("G7");
    ASSERT(g7.isValid());
    ASSERT_EQ(g7.rootNum, 7);  // G
    ASSERT_EQ(g7.quality, Harmony::ChordQuality::Dominant7);
    
    return true;
}

bool test_DiagnosticsProgressionParsing() {
    Diagnostics::ParsedChord chords[8];
    size_t count = Diagnostics::parseProgressionString("F-C-Am-Dm", chords, 8);
    
    ASSERT_EQ(count, 4);
    ASSERT_EQ(chords[0].rootNum, 5);  // F
    ASSERT_EQ(chords[1].rootNum, 0);  // C
    ASSERT_EQ(chords[2].rootNum, 9);  // A
    ASSERT_EQ(chords[3].rootNum, 2);  // D
    
    return true;
}

bool test_DiagnosticsProgressionDiagnosis() {
    Diagnostics::ProgressionDiagnosis diag = Diagnostics::diagnoseProgression("F-C-Am-Dm");
    
    ASSERT_EQ(diag.chordCount, 4);
    ASSERT(diag.keyConfidence > 0.0f);
    
    return true;
}

bool test_DiagnosticsBorrowedChordDetection() {
    // F-C-Bbm-F should detect Bbm as borrowed
    Diagnostics::ProgressionDiagnosis diag = Diagnostics::diagnoseProgression("F-C-Bbm-F");
    
    // Should have some issues or borrowed chord count > 0
    ASSERT(diag.issueCount > 0 || diag.borrowedChordCount > 0);
    
    return true;
}

// =============================================================================
// OSC Handler Tests
// =============================================================================

bool test_OSCMessageCreation() {
    OSC::Message msg;
    msg.setAddress("/test/address");
    msg.setFloat(0.75f);
    
    ASSERT(msg.isValid());
    ASSERT_EQ(msg.getAddress(), "/test/address");
    ASSERT_NEAR(msg.getFloat(), 0.75f, 0.0001f);
    
    return true;
}

bool test_OSCMessageQueue() {
    OSC::MessageQueue queue;
    
    ASSERT(queue.isEmpty());
    
    OSC::Message msg1;
    msg1.setAddress("/test/1");
    msg1.setFloat(1.0f);
    
    ASSERT(queue.tryPush(msg1));
    ASSERT(!queue.isEmpty());
    
    OSC::Message msg2;
    ASSERT(queue.tryPop(msg2));
    ASSERT(queue.isEmpty());
    ASSERT_EQ(msg2.getAddress(), "/test/1");
    ASSERT_NEAR(msg2.getFloat(), 1.0f, 0.0001f);
    
    return true;
}

bool test_OSCHandlerSendMethods() {
    OSC::OSCHandler handler;
    OSC::OSCHandler::Config config;
    handler.initialize(config);
    
    ASSERT(handler.isInitialized());
    ASSERT(handler.sendFloat("/test/float", 0.5f));
    ASSERT(handler.sendInt("/test/int", 42));
    ASSERT(handler.sendChaos(0.7f));
    ASSERT(handler.sendTempo(120.0f));
    
    // Verify messages were queued
    ASSERT(!handler.isOutgoingEmpty());
    
    return true;
}

bool test_OSCMIDIMessage() {
    OSC::Message msg;
    msg.setAddress(std::string(OSC::Address::MIDI_NOTE));
    msg.setMIDI(0, 0x90, 60, 100);  // Note on, C4, velocity 100
    
    ASSERT(msg.isValid());
    ASSERT_EQ(msg.data[0], 0);    // Port
    ASSERT_EQ(msg.data[1], 0x90); // Status
    ASSERT_EQ(msg.data[2], 60);   // Note
    ASSERT_EQ(msg.data[3], 100);  // Velocity
    
    return true;
}

// =============================================================================
// Test Runner
// =============================================================================

std::vector<TestCase> g_tests = {
    // Harmony Core
    TEST(HarmonyMidiToPitchClass),
    TEST(HarmonyChordDetection),
    TEST(HarmonyMinorChordDetection),
    TEST(HarmonyDominant7Detection),
    TEST(HarmonyKeyDetection),
    TEST(HarmonyRomanNumerals),
    TEST(HarmonyBorrowedChord),
    
    // Groove Core
    TEST(GrooveSwingCalculation),
    TEST(GrooveTimingDeviation),
    TEST(GrooveTemplateExtraction),
    TEST(GrooveGenreParams),
    TEST(GrooveHumanize),
    
    // Diagnostics Core
    TEST(DiagnosticsNoteNameParsing),
    TEST(DiagnosticsChordParsing),
    TEST(DiagnosticsProgressionParsing),
    TEST(DiagnosticsProgressionDiagnosis),
    TEST(DiagnosticsBorrowedChordDetection),
    
    // OSC Handler
    TEST(OSCMessageCreation),
    TEST(OSCMessageQueue),
    TEST(OSCHandlerSendMethods),
    TEST(OSCMIDIMessage),
};

void runTests() {
    std::cout << "\n╔══════════════════════════════════════════════════════════════╗\n";
    std::cout << "║                   iDAW Core Unit Tests                        ║\n";
    std::cout << "╚══════════════════════════════════════════════════════════════╝\n\n";
    
    for (const auto& test : g_tests) {
        std::cout << "  " << std::left << std::setw(40) << test.name << " ";
        
        bool passed = false;
        try {
            passed = test.testFunc();
        } catch (const std::exception& e) {
            std::cerr << "EXCEPTION: " << e.what() << std::endl;
        } catch (...) {
            std::cerr << "UNKNOWN EXCEPTION" << std::endl;
        }
        
        if (passed) {
            std::cout << "\033[32m✓ PASS\033[0m\n";
            g_passCount++;
        } else {
            std::cout << "\033[31m✗ FAIL\033[0m\n";
            g_failCount++;
        }
    }
}

void runStressTests() {
    std::cout << "\n╔══════════════════════════════════════════════════════════════╗\n";
    std::cout << "║                   iDAW Stress Tests                          ║\n";
    std::cout << "╚══════════════════════════════════════════════════════════════╝\n\n";
    
    auto results = StressTest::runAllTests();
    
    for (const auto& result : results) {
        std::cout << "  Test " << std::setw(2) << result.testNumber << ": ";
        std::cout << std::left << std::setw(25) << result.testName << " ";
        
        if (result.passed) {
            std::cout << "\033[32m✓ PASS\033[0m";
            g_passCount++;
        } else {
            std::cout << "\033[31m✗ FAIL\033[0m";
            g_failCount++;
        }
        
        std::cout << " (" << std::fixed << std::setprecision(2) << result.durationMs << "ms)\n";
    }
}

int main(int argc, char* argv[]) {
    std::cout << "\n";
    std::cout << "     ██╗██████╗  █████╗ ██╗    ██╗\n";
    std::cout << "     ██║██╔══██╗██╔══██╗██║    ██║\n";
    std::cout << "     ██║██║  ██║███████║██║ █╗ ██║\n";
    std::cout << "     ██║██║  ██║██╔══██║██║███╗██║\n";
    std::cout << "     ██║██████╔╝██║  ██║╚███╔███╔╝\n";
    std::cout << "     ╚═╝╚═════╝ ╚═╝  ╚═╝ ╚══╝╚══╝\n";
    std::cout << "\n     C++ Core Test Suite v1.0.0\n\n";
    
    // Run unit tests
    runTests();
    
    // Run stress tests
    runStressTests();
    
    // Summary
    std::cout << "\n╔══════════════════════════════════════════════════════════════╗\n";
    std::cout << "║                        Summary                               ║\n";
    std::cout << "╠══════════════════════════════════════════════════════════════╣\n";
    std::cout << "║  Total: " << std::setw(3) << (g_passCount + g_failCount);
    std::cout << "    Pass: \033[32m" << std::setw(3) << g_passCount << "\033[0m";
    std::cout << "    Fail: \033[31m" << std::setw(3) << g_failCount << "\033[0m";
    std::cout << "                  ║\n";
    std::cout << "╚══════════════════════════════════════════════════════════════╝\n\n";
    
    return g_failCount > 0 ? 1 : 0;
}
