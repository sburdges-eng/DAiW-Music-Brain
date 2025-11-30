/**
 * @file Version.h
 * @brief iDAW Core Version Information
 *
 * Part of DAiW v1.0.0 Release
 */

#pragma once

#define IDAW_VERSION_MAJOR 1
#define IDAW_VERSION_MINOR 0
#define IDAW_VERSION_PATCH 0
#define IDAW_VERSION_STRING "1.0.0"

#define IDAW_PRODUCT_NAME "DAiW"
#define IDAW_COMPANY_NAME "DAiW Project"
#define IDAW_COPYRIGHT "Copyright (c) 2025 Sean Burdges"

// Build information
#define IDAW_BUILD_DATE __DATE__
#define IDAW_BUILD_TIME __TIME__

// Feature flags
#define IDAW_FEATURE_COMPREHENSIVE_ENGINE 1
#define IDAW_FEATURE_GROOVE_EXTRACTION 1
#define IDAW_FEATURE_CHORD_ANALYSIS 1
#define IDAW_FEATURE_INTENT_SCHEMA 1
#define IDAW_FEATURE_AI_ORCHESTRATOR 1
#define IDAW_FEATURE_PROPOSALS 1

// Component versions
#define IDAW_MUSIC_BRAIN_VERSION "1.0.0"
#define IDAW_MCP_WORKSTATION_VERSION "1.0.0"
#define IDAW_CPP_CORE_VERSION "1.0.0"

namespace idaw {

struct Version {
    static constexpr int major = IDAW_VERSION_MAJOR;
    static constexpr int minor = IDAW_VERSION_MINOR;
    static constexpr int patch = IDAW_VERSION_PATCH;

    static constexpr const char* string() {
        return IDAW_VERSION_STRING;
    }

    static constexpr const char* productName() {
        return IDAW_PRODUCT_NAME;
    }

    static constexpr const char* copyright() {
        return IDAW_COPYRIGHT;
    }
};

}  // namespace idaw
