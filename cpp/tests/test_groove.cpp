/**
 * @file test_groove.cpp
 * @brief Tests for groove module
 */

#include <catch2/catch_all.hpp>
#include "daiw/types.hpp"

TEST_CASE("GrooveSettings defaults", "[groove]") {
    daiw::GrooveSettings settings;

    REQUIRE(settings.swing == 0.0f);
    REQUIRE(settings.pushPull == 0.0f);
    REQUIRE(settings.humanization == 0.0f);
    REQUIRE(settings.velocityVar == 0.0f);
}

TEST_CASE("NoteEvent operations", "[groove]") {
    daiw::NoteEvent note;
    note.pitch = 60;
    note.velocity = 100;
    note.startTick = 480;
    note.durationTicks = 240;

    REQUIRE(note.endTick() == 720);
}

TEST_CASE("Groove settings ranges", "[groove]") {
    daiw::GrooveSettings settings;

    SECTION("Swing range") {
        settings.swing = 0.5f;
        REQUIRE(settings.swing >= 0.0f);
        REQUIRE(settings.swing <= 1.0f);
    }

    SECTION("Push/pull range") {
        settings.pushPull = -0.5f;
        REQUIRE(settings.pushPull >= -1.0f);
        REQUIRE(settings.pushPull <= 1.0f);
    }
}
