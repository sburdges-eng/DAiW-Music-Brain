/**
 * @file test_memory.cpp
 * @brief Tests for memory management utilities
 */

#include <catch2/catch_all.hpp>
#include "daiw/memory.hpp"

TEST_CASE("MemoryPool basic operations", "[memory]") {
    daiw::MemoryPool pool(64, 10);

    SECTION("Initial state") {
        REQUIRE(pool.totalBlocks() == 10);
        REQUIRE(pool.availableBlocks() == 10);
        REQUIRE(pool.blockSize() == 64);
    }

    SECTION("Allocation and deallocation") {
        void* ptr1 = pool.allocate();
        REQUIRE(ptr1 != nullptr);
        REQUIRE(pool.availableBlocks() == 9);

        void* ptr2 = pool.allocate();
        REQUIRE(ptr2 != nullptr);
        REQUIRE(pool.availableBlocks() == 8);

        pool.deallocate(ptr1);
        REQUIRE(pool.availableBlocks() == 9);
    }

    SECTION("Contains check") {
        void* ptr = pool.allocate();
        REQUIRE(pool.contains(ptr));

        int stackVar;
        REQUIRE_FALSE(pool.contains(&stackVar));
    }
}

TEST_CASE("RingBuffer operations", "[memory]") {
    daiw::RingBuffer<int, 16> buffer;

    SECTION("Empty buffer") {
        REQUIRE(buffer.empty());
        REQUIRE(buffer.size() == 0);
    }

    SECTION("Push and pop") {
        REQUIRE(buffer.push(42));
        REQUIRE_FALSE(buffer.empty());
        REQUIRE(buffer.size() == 1);

        int value;
        REQUIRE(buffer.pop(value));
        REQUIRE(value == 42);
        REQUIRE(buffer.empty());
    }

    SECTION("Full buffer") {
        for (int i = 0; i < 15; ++i) {
            REQUIRE(buffer.push(i));
        }
        REQUIRE_FALSE(buffer.push(99));  // Should fail, buffer full
    }
}
