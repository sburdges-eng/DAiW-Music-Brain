# CompilerWarnings.cmake
# Sets up strict compiler warnings for code quality

function(set_target_warnings target)
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        target_compile_options(${target} PRIVATE
            -Wall
            -Wextra
            -Wpedantic
            -Wshadow
            -Wnon-virtual-dtor
            -Wold-style-cast
            -Wcast-align
            -Wunused
            -Woverloaded-virtual
            -Wconversion
            -Wsign-conversion
            -Wnull-dereference
            -Wdouble-promotion
            -Wformat=2
            -Wimplicit-fallthrough
        )

        if(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
            target_compile_options(${target} PRIVATE
                -Wmisleading-indentation
                -Wduplicated-cond
                -Wduplicated-branches
                -Wlogical-op
                -Wuseless-cast
            )
        endif()

    elseif(MSVC)
        target_compile_options(${target} PRIVATE
            /W4
            /permissive-
            /w14640    # thread unsafe static member initialization
            /w14826    # conversion from 'type1' to 'type2' is sign-extended
            /w14928    # illegal copy-initialization
        )
    endif()
endfunction()
