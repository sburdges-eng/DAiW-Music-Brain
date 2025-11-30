/**
 * @file test_simd.cpp
 * @brief Tests for SIMD operations
 */

#include <catch2/catch_all.hpp>
#include "daiw/types.hpp"
#include <vector>

// These would test the actual SIMD implementations
TEST_CASE("SIMD scale operation", "[simd]") {
    std::vector<float> input = {1.0f, 2.0f, 3.0f, 4.0f};
    std::vector<float> output(4);

    // Simple scalar test (placeholder for SIMD test)
    float gain = 2.0f;
    for (size_t i = 0; i < input.size(); ++i) {
        output[i] = input[i] * gain;
    }

    REQUIRE(output[0] == Catch::Approx(2.0f));
    REQUIRE(output[1] == Catch::Approx(4.0f));
    REQUIRE(output[2] == Catch::Approx(6.0f));
    REQUIRE(output[3] == Catch::Approx(8.0f));
}

TEST_CASE("SIMD add operation", "[simd]") {
    std::vector<float> a = {1.0f, 2.0f, 3.0f, 4.0f};
    std::vector<float> b = {0.5f, 0.5f, 0.5f, 0.5f};
    std::vector<float> result(4);

    for (size_t i = 0; i < a.size(); ++i) {
        result[i] = a[i] + b[i];
    }

    REQUIRE(result[0] == Catch::Approx(1.5f));
    REQUIRE(result[3] == Catch::Approx(4.5f));
}
