/**
 * memory_pool_test.cpp - Tests for the lock-free MemoryPool
 *
 * Tests basic functionality and thread safety of the MemoryPool class.
 */

#include "daiw/memory.hpp"
#include <atomic>
#include <cassert>
#include <iostream>
#include <mutex>
#include <set>
#include <thread>
#include <vector>

using namespace daiw;

void test_basic_allocation() {
    std::cout << "Testing basic allocation..." << std::endl;

    constexpr size_t blockSize = 64;
    constexpr size_t numBlocks = 10;

    MemoryPool pool(blockSize, numBlocks);

    // Check initial state
    assert(pool.totalBlocks() == numBlocks);
    assert(pool.blockSize() == blockSize);
    assert(pool.freeCount() == numBlocks);

    // Allocate all blocks
    std::vector<void*> ptrs;
    for (size_t i = 0; i < numBlocks; ++i) {
        void* ptr = pool.allocate();
        assert(ptr != nullptr);
        assert(pool.contains(ptr));
        ptrs.push_back(ptr);
    }

    // All blocks should be allocated
    assert(pool.freeCount() == 0);

    // Next allocation should fail
    void* extra = pool.allocate();
    assert(extra == nullptr);

    // Free all blocks
    for (void* ptr : ptrs) {
        pool.deallocate(ptr);
    }

    // All blocks should be free again
    assert(pool.freeCount() == numBlocks);

    std::cout << "Basic allocation test passed!" << std::endl;
}

void test_contains() {
    std::cout << "Testing contains()..." << std::endl;

    constexpr size_t blockSize = 64;
    constexpr size_t numBlocks = 5;

    MemoryPool pool(blockSize, numBlocks);

    // Allocate a block
    void* ptr = pool.allocate();
    assert(ptr != nullptr);
    assert(pool.contains(ptr));

    // Test that nullptr is not contained
    assert(!pool.contains(nullptr));

    // Test that an external pointer is not contained
    char external[64];
    assert(!pool.contains(external));

    // Test that misaligned pointer is not contained
    char* misaligned = static_cast<char*>(ptr) + 1;
    assert(!pool.contains(misaligned));

    pool.deallocate(ptr);

    std::cout << "Contains test passed!" << std::endl;
}

void test_concurrent_allocation() {
    std::cout << "Testing concurrent allocation..." << std::endl;

    constexpr size_t blockSize = 64;
    constexpr size_t numBlocks = 1000;
    constexpr size_t numThreads = 4;
    constexpr size_t opsPerThread = 10000;
    // Deallocate every N iterations to keep the pool from being exhausted
    // while still testing concurrent alloc/dealloc behavior
    constexpr size_t deallocateFrequency = 3;

    MemoryPool pool(blockSize, numBlocks);

    std::atomic<size_t> successfulAllocs{0};
    std::atomic<size_t> failedAllocs{0};
    std::atomic<bool> startFlag{false};

    auto workerFunc = [&]() {
        // Wait for start signal
        while (!startFlag.load(std::memory_order_acquire)) {
            std::this_thread::yield();
        }

        std::vector<void*> myPtrs;
        for (size_t i = 0; i < opsPerThread; ++i) {
            // Try to allocate
            void* ptr = pool.allocate();
            if (ptr != nullptr) {
                successfulAllocs.fetch_add(1, std::memory_order_relaxed);
                myPtrs.push_back(ptr);
            } else {
                failedAllocs.fetch_add(1, std::memory_order_relaxed);
            }

            // Occasionally deallocate some to test concurrent dealloc
            if (!myPtrs.empty() && (i % deallocateFrequency == 0)) {
                pool.deallocate(myPtrs.back());
                myPtrs.pop_back();
            }
        }

        // Deallocate remaining
        for (void* ptr : myPtrs) {
            pool.deallocate(ptr);
        }
    };

    // Create worker threads
    std::vector<std::thread> threads;
    for (size_t i = 0; i < numThreads; ++i) {
        threads.emplace_back(workerFunc);
    }

    // Start all threads simultaneously
    startFlag.store(true, std::memory_order_release);

    // Wait for all threads to finish
    for (auto& t : threads) {
        t.join();
    }

    // All blocks should be returned
    assert(pool.freeCount() == numBlocks);

    std::cout << "Concurrent allocation test passed!" << std::endl;
    std::cout << "  Successful allocs: " << successfulAllocs.load() << std::endl;
    std::cout << "  Failed allocs: " << failedAllocs.load() << std::endl;
}

void test_no_double_allocation() {
    std::cout << "Testing no double allocation (race condition fix)..." << std::endl;

    constexpr size_t blockSize = 64;
    constexpr size_t numBlocks = 1000;
    constexpr size_t numThreads = 8;
    // Number of trials to run - higher values increase confidence in race-freedom
    constexpr int numTrials = 50;

    // Run the test multiple times to increase chance of catching races
    for (int trial = 0; trial < numTrials; ++trial) {
        // Create a fresh pool for each trial
        MemoryPool pool(blockSize, numBlocks);

        std::atomic<bool> startFlag{false};
        std::atomic<bool> failure{false};
        std::mutex allPtrsMutex;
        std::set<void*> allPtrs;
        std::vector<std::vector<void*>> threadPtrs(numThreads);

        auto workerFunc = [&](size_t threadIdx) {
            // Wait for start signal
            while (!startFlag.load(std::memory_order_acquire)) {
                std::this_thread::yield();
            }

            std::vector<void*>& myPtrs = threadPtrs[threadIdx];

            // Allocate as many blocks as possible
            while (true) {
                void* ptr = pool.allocate();
                if (ptr == nullptr) {
                    break;  // Pool exhausted
                }
                myPtrs.push_back(ptr);
            }
        };

        std::vector<std::thread> threads;
        for (size_t i = 0; i < numThreads; ++i) {
            threads.emplace_back(workerFunc, i);
        }

        // Start all threads simultaneously
        startFlag.store(true, std::memory_order_release);

        for (auto& t : threads) {
            t.join();
        }

        // After all threads finish, check for duplicates
        size_t totalAllocated = 0;
        for (size_t i = 0; i < numThreads; ++i) {
            for (void* ptr : threadPtrs[i]) {
                if (allPtrs.count(ptr) > 0) {
                    // Found duplicate - this indicates a race condition!
                    std::cerr << "Trial " << trial << ": Duplicate pointer found!" << std::endl;
                    failure.store(true, std::memory_order_relaxed);
                }
                allPtrs.insert(ptr);
                totalAllocated++;
            }
        }

        if (failure.load()) {
            assert(false && "Race condition detected: duplicate allocation!");
        }

        // Verify we allocated exactly numBlocks
        if (totalAllocated != numBlocks) {
            std::cerr << "Trial " << trial << ": Expected " << numBlocks
                      << " allocations, got " << totalAllocated << std::endl;
            assert(false);
        }

        // Return all blocks for the next trial (pool is destroyed anyway)
        for (size_t i = 0; i < numThreads; ++i) {
            for (void* ptr : threadPtrs[i]) {
                pool.deallocate(ptr);
            }
        }
    }

    std::cout << "No double allocation test passed!" << std::endl;
}

int main() {
    std::cout << "=== MemoryPool Tests ===" << std::endl;

    test_basic_allocation();
    test_contains();
    test_concurrent_allocation();
    test_no_double_allocation();

    std::cout << std::endl;
    std::cout << "All tests passed!" << std::endl;
    return 0;
}
