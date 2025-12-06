cmake_minimum_required(VERSION 3.14)

# Test executable
add_executable(memory_pool_test
    memory_pool_test.cpp
)

target_link_libraries(memory_pool_test
    PRIVATE
        daiw_core
        Threads::Threads
)

add_test(NAME MemoryPoolTest COMMAND memory_pool_test)
