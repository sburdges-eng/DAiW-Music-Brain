/**
 * @file test_harmony.cpp
 * @brief Tests for harmony module
 */

#include <catch2/catch_all.hpp>
#include "daiw/types.hpp"

TEST_CASE("TimeSignature operations", "[harmony]") {
    daiw::TimeSignature ts;
    ts.numerator = 4;
    ts.denominator = 4;

    REQUIRE(ts.beatsPerBar() == 4.0f);
    REQUIRE(ts.ticksPerBar(480) == 1920.0f);
}

TEST_CASE("TimeSignature 3/4", "[harmony]") {
    daiw::TimeSignature ts;
    ts.numerator = 3;
    ts.denominator = 4;

    REQUIRE(ts.beatsPerBar() == 3.0f);
    REQUIRE(ts.ticksPerBar(480) == 1440.0f);
}

TEST_CASE("Tempo calculations", "[harmony]") {
    daiw::Tempo tempo;
    tempo.bpm = 120.0f;

    SECTION("Samples per beat at 48kHz") {
        float spb = tempo.samplesPerBeat(48000);
        REQUIRE(spb == Catch::Approx(24000.0f));
    }

    SECTION("Milliseconds per beat") {
        float mpb = tempo.msPerBeat();
        REQUIRE(mpb == Catch::Approx(500.0f));
    }
}
