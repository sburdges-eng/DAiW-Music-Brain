/**
 * test_ring_buffer.cpp - Unit tests for Lock-Free Ring Buffer
 */

#include <gtest/gtest.h>
#include "MemoryManager.h"
#include <thread>
#include <atomic>
#include <vector>

using namespace iDAW;

// ============================================================================
// Ring Buffer Basic Tests
// ============================================================================

class RingBufferTest : public ::testing::Test {
protected:
    LockFreeRingBuffer<int, 16> buffer;
};

TEST_F(RingBufferTest, InitiallyEmpty) {
    EXPECT_TRUE(buffer.isEmpty());
    EXPECT_EQ(buffer.approximateSize(), 0);
}

TEST_F(RingBufferTest, PushPop) {
    EXPECT_TRUE(buffer.tryPush(42));
    
    EXPECT_FALSE(buffer.isEmpty());
    EXPECT_EQ(buffer.approximateSize(), 1);
    
    int value;
    EXPECT_TRUE(buffer.tryPop(value));
    EXPECT_EQ(value, 42);
    
    EXPECT_TRUE(buffer.isEmpty());
}

TEST_F(RingBufferTest, MultiplePushPop) {
    for (int i = 0; i < 10; i++) {
        EXPECT_TRUE(buffer.tryPush(i));
    }
    
    EXPECT_EQ(buffer.approximateSize(), 10);
    
    for (int i = 0; i < 10; i++) {
        int value;
        EXPECT_TRUE(buffer.tryPop(value));
        EXPECT_EQ(value, i);
    }
    
    EXPECT_TRUE(buffer.isEmpty());
}

TEST_F(RingBufferTest, FullBuffer) {
    // Fill buffer (capacity is 16, but one slot is always empty)
    for (int i = 0; i < 15; i++) {
        EXPECT_TRUE(buffer.tryPush(i));
    }
    
    // Should fail when full
    EXPECT_FALSE(buffer.tryPush(99));
}

TEST_F(RingBufferTest, EmptyPop) {
    int value;
    EXPECT_FALSE(buffer.tryPop(value));
}

TEST_F(RingBufferTest, WrapAround) {
    // Push and pop several times to wrap around
    for (int round = 0; round < 3; round++) {
        for (int i = 0; i < 10; i++) {
            EXPECT_TRUE(buffer.tryPush(i + round * 100));
        }
        
        for (int i = 0; i < 10; i++) {
            int value;
            EXPECT_TRUE(buffer.tryPop(value));
            EXPECT_EQ(value, i + round * 100);
        }
    }
    
    EXPECT_TRUE(buffer.isEmpty());
}

// ============================================================================
// MIDI Event Ring Buffer Tests
// ============================================================================

TEST(MidiBufferTest, BasicUsage) {
    LockFreeRingBuffer<MidiEvent, 256> midiBuffer;
    
    MidiEvent noteOn{0x90, 60, 100, 0};
    EXPECT_TRUE(midiBuffer.tryPush(noteOn));
    
    MidiEvent received;
    EXPECT_TRUE(midiBuffer.tryPop(received));
    
    EXPECT_EQ(received.status, 0x90);
    EXPECT_EQ(received.data1, 60);
    EXPECT_EQ(received.data2, 100);
    EXPECT_EQ(received.timestamp, 0);
}

TEST(MidiBufferTest, MultipleEvents) {
    LockFreeRingBuffer<MidiEvent, 256> midiBuffer;
    
    // Push multiple MIDI events
    std::vector<MidiEvent> events = {
        {0x90, 60, 100, 0},      // Note On C4
        {0x90, 64, 100, 0},      // Note On E4
        {0x90, 67, 100, 0},      // Note On G4
        {0x80, 60, 0, 480},      // Note Off C4
        {0x80, 64, 0, 480},      // Note Off E4
        {0x80, 67, 0, 480},      // Note Off G4
    };
    
    for (const auto& event : events) {
        EXPECT_TRUE(midiBuffer.tryPush(event));
    }
    
    // Pop and verify
    for (size_t i = 0; i < events.size(); i++) {
        MidiEvent received;
        EXPECT_TRUE(midiBuffer.tryPop(received));
        EXPECT_EQ(received.status, events[i].status);
        EXPECT_EQ(received.data1, events[i].data1);
        EXPECT_EQ(received.data2, events[i].data2);
        EXPECT_EQ(received.timestamp, events[i].timestamp);
    }
}

// ============================================================================
// Concurrent Access Tests
// ============================================================================

TEST(ConcurrentBufferTest, ProducerConsumer) {
    LockFreeRingBuffer<int, 1024> buffer;
    std::atomic<bool> done{false};
    std::atomic<int> consumedCount{0};
    
    const int numItems = 10000;
    
    // Consumer thread
    std::thread consumer([&]() {
        int lastValue = -1;
        while (!done.load() || !buffer.isEmpty()) {
            int value;
            if (buffer.tryPop(value)) {
                // Values should be in order
                EXPECT_GT(value, lastValue);
                lastValue = value;
                consumedCount++;
            }
        }
    });
    
    // Producer (main thread)
    for (int i = 0; i < numItems; i++) {
        while (!buffer.tryPush(i)) {
            // Buffer full, yield and retry
            std::this_thread::yield();
        }
    }
    
    done.store(true);
    consumer.join();
    
    EXPECT_EQ(consumedCount.load(), numItems);
}

TEST(ConcurrentBufferTest, MidiProducerConsumer) {
    LockFreeRingBuffer<MidiEvent, 4096> midiBuffer;
    std::atomic<bool> done{false};
    std::atomic<int> consumedCount{0};
    
    const int numEvents = 1000;
    
    // Consumer thread (simulates audio thread)
    std::thread consumer([&]() {
        while (!done.load() || !midiBuffer.isEmpty()) {
            MidiEvent event;
            if (midiBuffer.tryPop(event)) {
                consumedCount++;
            }
        }
    });
    
    // Producer (simulates UI/Python thread)
    for (int i = 0; i < numEvents; i++) {
        MidiEvent event{
            static_cast<uint8_t>(i % 2 == 0 ? 0x90 : 0x80),
            static_cast<uint8_t>(60 + (i % 12)),
            static_cast<uint8_t>(100),
            static_cast<uint32_t>(i * 100)
        };
        
        while (!midiBuffer.tryPush(event)) {
            std::this_thread::yield();
        }
    }
    
    done.store(true);
    consumer.join();
    
    EXPECT_EQ(consumedCount.load(), numEvents);
}
