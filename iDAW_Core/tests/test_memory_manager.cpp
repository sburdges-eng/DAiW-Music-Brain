/**
 * test_memory_manager.cpp - Unit tests for Memory Manager
 */

#include <gtest/gtest.h>
#include "MemoryManager.h"
#include <thread>

using namespace iDAW;

// ============================================================================
// Memory Manager Tests
// ============================================================================

class MemoryManagerTest : public ::testing::Test {
protected:
    MemoryManager& manager = MemoryManager::getInstance();
};

TEST_F(MemoryManagerTest, Singleton) {
    MemoryManager& m1 = MemoryManager::getInstance();
    MemoryManager& m2 = MemoryManager::getInstance();
    
    EXPECT_EQ(&m1, &m2);
}

TEST_F(MemoryManagerTest, SideAAllocator) {
    SideAAllocator& sideA = manager.getSideA();
    
    // Should be able to allocate
    void* ptr = sideA.allocate(1024);
    EXPECT_NE(ptr, nullptr);
    
    // Bytes used should increase
    EXPECT_GE(sideA.getBytesUsed(), 1024);
    
    // Usage percent should be valid
    EXPECT_GE(sideA.getUsagePercent(), 0.0f);
    EXPECT_LE(sideA.getUsagePercent(), 100.0f);
}

TEST_F(MemoryManagerTest, SideBAllocator) {
    SideBAllocator& sideB = manager.getSideB();
    
    // Should be able to allocate
    void* ptr = sideB.allocate(1024);
    EXPECT_NE(ptr, nullptr);
    
    // Should be able to deallocate
    sideB.deallocate(ptr, 1024);
}

TEST_F(MemoryManagerTest, SideBAllocator_MultiplAllocations) {
    SideBAllocator& sideB = manager.getSideB();
    
    std::vector<void*> ptrs;
    for (int i = 0; i < 10; i++) {
        void* ptr = sideB.allocate(1024);
        EXPECT_NE(ptr, nullptr);
        ptrs.push_back(ptr);
    }
    
    // Deallocate all
    for (void* ptr : ptrs) {
        sideB.deallocate(ptr, 1024);
    }
}

TEST_F(MemoryManagerTest, AudioThreadRegistration) {
    // Initially, current thread is not audio thread
    // (unless running in audio context)
    
    // After registration, current thread should be audio thread
    manager.registerAudioThread();
    EXPECT_TRUE(manager.isAudioThread());
}

TEST_F(MemoryManagerTest, SideACanAllocate) {
    SideAAllocator& sideA = manager.getSideA();
    
    // Should be able to allocate reasonable amounts
    EXPECT_TRUE(sideA.canAllocate(1024 * 1024));  // 1MB
}

TEST_F(MemoryManagerTest, SideABytesRemaining) {
    SideAAllocator& sideA = manager.getSideA();
    
    size_t remaining = sideA.getBytesRemaining();
    EXPECT_GT(remaining, 0);
    
    // Total should be used + remaining
    size_t total = sideA.getBytesUsed() + sideA.getBytesRemaining();
    EXPECT_EQ(total, MemoryConfig::SIDE_A_SIZE);
}

// ============================================================================
// SideBPtr RAII Tests
// ============================================================================

TEST(SideBPtrTest, BasicUsage) {
    SideBPtr<int> ptr(10);
    
    EXPECT_NE(ptr.get(), nullptr);
    
    // Write to elements
    for (int i = 0; i < 10; i++) {
        ptr[i] = i * 2;
    }
    
    // Read back
    for (int i = 0; i < 10; i++) {
        EXPECT_EQ(ptr[i], i * 2);
    }
    
    // Destructor will deallocate
}

TEST(SideBPtrTest, MoveSemantics) {
    SideBPtr<int> ptr1(5);
    EXPECT_NE(ptr1.get(), nullptr);
    
    int* rawPtr = ptr1.get();
    
    SideBPtr<int> ptr2 = std::move(ptr1);
    
    // ptr2 should have the pointer
    EXPECT_EQ(ptr2.get(), rawPtr);
    
    // ptr1 should be null
    EXPECT_EQ(ptr1.get(), nullptr);
}

TEST(SideBPtrTest, DefaultConstructor) {
    SideBPtr<int> ptr;
    EXPECT_EQ(ptr.get(), nullptr);
}
