/**
 * @file logging.cpp
 * @brief Logging utilities for DAiW
 */

#include <iostream>
#include <string>
#include <cstdarg>

namespace daiw {

enum class LogLevel {
    Debug,
    Info,
    Warning,
    Error
};

class Logger {
public:
    static Logger& instance() {
        static Logger logger;
        return logger;
    }

    void setLevel(LogLevel level) { level_ = level; }
    LogLevel getLevel() const { return level_; }

    void log(LogLevel level, const char* message) {
        if (level >= level_) {
            const char* prefix = "";
            switch (level) {
                case LogLevel::Debug:   prefix = "[DEBUG] "; break;
                case LogLevel::Info:    prefix = "[INFO]  "; break;
                case LogLevel::Warning: prefix = "[WARN]  "; break;
                case LogLevel::Error:   prefix = "[ERROR] "; break;
            }
            std::cerr << prefix << message << std::endl;
        }
    }

private:
    Logger() = default;
    LogLevel level_ = LogLevel::Info;
};

void logDebug(const char* message) {
    Logger::instance().log(LogLevel::Debug, message);
}

void logInfo(const char* message) {
    Logger::instance().log(LogLevel::Info, message);
}

void logWarning(const char* message) {
    Logger::instance().log(LogLevel::Warning, message);
}

void logError(const char* message) {
    Logger::instance().log(LogLevel::Error, message);
}

}  // namespace daiw
