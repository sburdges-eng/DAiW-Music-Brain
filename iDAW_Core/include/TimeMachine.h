/**
 * TimeMachine.h - iDAW v1.1 Auto-Save System
 *
 * Implements automatic project state versioning:
 * - Auto-saves to hidden .idaw_history/ Git repository
 * - Triggers on every 'Flip' between Side A and Side B
 * - Allows time-travel through project history
 * - Zero cloud connectivity - all local
 *
 * Philosophy: "Every creative moment is worth preserving."
 */

#pragma once

#include <JuceHeader.h>
#include <atomic>
#include <chrono>
#include <functional>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <ctime>
#include <filesystem>

namespace iDAW {

namespace fs = std::filesystem;

/**
 * Snapshot metadata
 */
struct TimeSnapshot {
    std::string id;              // Git commit hash (short)
    std::string timestamp;       // ISO 8601 format
    std::string description;     // Auto-generated or user description
    std::string triggerEvent;    // What caused the save (flip, confirm, manual)
    int sideAState;              // 0 = inactive, 1 = active
    int sideBState;
    float chaosValue;
    float complexityValue;
    std::string moodProfile;
    size_t fileSize;             // Size of saved state
};

/**
 * Time Machine Events
 */
enum class TimeMachineEvent {
    FLIP_TO_SIDE_A,
    FLIP_TO_SIDE_B,
    CONFIRM_OUTPUT,
    MANUAL_SAVE,
    AUTO_INTERVAL,
    BEFORE_DESTRUCTIVE_OP
};

/**
 * Project state serialization
 */
struct ProjectState {
    // Side A (Work) state
    struct {
        float tempo;
        int timeSignatureNum;
        int timeSignatureDenom;
        std::string key;
        std::vector<uint8_t> midiData;
    } sideA;

    // Side B (Dream) state
    struct {
        float chaos;
        float complexity;
        float grid;
        float gate;
        float swing;
        std::string promptText;
        std::string moodProfile;
        std::string lastAffect;
    } sideB;

    // Metadata
    std::string projectName;
    std::string lastModified;
    int version;

    /**
     * Serialize to JSON string
     */
    std::string toJson() const {
        std::ostringstream ss;
        ss << "{\n";
        ss << "  \"version\": " << version << ",\n";
        ss << "  \"projectName\": \"" << projectName << "\",\n";
        ss << "  \"lastModified\": \"" << lastModified << "\",\n";
        ss << "  \"sideA\": {\n";
        ss << "    \"tempo\": " << sideA.tempo << ",\n";
        ss << "    \"timeSignature\": \"" << sideA.timeSignatureNum << "/" << sideA.timeSignatureDenom << "\",\n";
        ss << "    \"key\": \"" << sideA.key << "\"\n";
        ss << "  },\n";
        ss << "  \"sideB\": {\n";
        ss << "    \"chaos\": " << sideB.chaos << ",\n";
        ss << "    \"complexity\": " << sideB.complexity << ",\n";
        ss << "    \"grid\": " << sideB.grid << ",\n";
        ss << "    \"gate\": " << sideB.gate << ",\n";
        ss << "    \"swing\": " << sideB.swing << ",\n";
        ss << "    \"promptText\": \"" << escapeJson(sideB.promptText) << "\",\n";
        ss << "    \"moodProfile\": \"" << sideB.moodProfile << "\",\n";
        ss << "    \"lastAffect\": \"" << sideB.lastAffect << "\"\n";
        ss << "  }\n";
        ss << "}\n";
        return ss.str();
    }

private:
    static std::string escapeJson(const std::string& s) {
        std::string result;
        for (char c : s) {
            switch (c) {
                case '"': result += "\\\""; break;
                case '\\': result += "\\\\"; break;
                case '\n': result += "\\n"; break;
                case '\r': result += "\\r"; break;
                case '\t': result += "\\t"; break;
                default: result += c;
            }
        }
        return result;
    }
};

/**
 * Time Machine - Auto-Save System
 *
 * Creates a hidden Git repository for project versioning:
 * - .idaw_history/
 *   ├── .git/
 *   ├── state.json
 *   ├── midi/
 *   │   └── [timestamped MIDI files]
 *   └── snapshots/
 *       └── [snapshot metadata]
 */
class TimeMachine {
public:
    // Configuration
    static constexpr int MAX_SNAPSHOTS = 1000;
    static constexpr int AUTO_SAVE_INTERVAL_SECONDS = 300;  // 5 minutes
    static constexpr const char* HISTORY_DIR = ".idaw_history";
    static constexpr const char* STATE_FILE = "state.json";

    using SnapshotCallback = std::function<void(const TimeSnapshot&)>;

    TimeMachine(const std::string& projectPath = "")
        : m_projectPath(projectPath)
        , m_initialized(false)
        , m_snapshotCount(0)
    {
        if (!projectPath.empty()) {
            initialize(projectPath);
        }
    }

    /**
     * Initialize Time Machine for a project
     */
    bool initialize(const std::string& projectPath) {
        m_projectPath = projectPath;
        m_historyPath = fs::path(projectPath) / HISTORY_DIR;

        try {
            // Create history directory if it doesn't exist
            if (!fs::exists(m_historyPath)) {
                fs::create_directories(m_historyPath);
                fs::create_directories(m_historyPath / "midi");
                fs::create_directories(m_historyPath / "snapshots");

                // Initialize Git repository
                if (!initGitRepo()) {
                    return false;
                }

                // Create .gitignore in parent to hide history from main repo
                createGitIgnore();
            }

            // Load existing snapshots
            loadSnapshotHistory();

            m_initialized = true;
            return true;

        } catch (const std::exception& e) {
            m_lastError = e.what();
            return false;
        }
    }

    /**
     * Save current state (triggered on Flip or other events)
     */
    TimeSnapshot saveState(const ProjectState& state, TimeMachineEvent event) {
        if (!m_initialized) {
            return TimeSnapshot{};
        }

        TimeSnapshot snapshot;
        snapshot.timestamp = getCurrentTimestamp();
        snapshot.triggerEvent = eventToString(event);
        snapshot.chaosValue = state.sideB.chaos;
        snapshot.complexityValue = state.sideB.complexity;
        snapshot.moodProfile = state.sideB.moodProfile;
        snapshot.sideAState = (event == TimeMachineEvent::FLIP_TO_SIDE_A) ? 1 : 0;
        snapshot.sideBState = (event == TimeMachineEvent::FLIP_TO_SIDE_B) ? 1 : 0;

        try {
            // Write state to JSON file
            std::string stateJson = state.toJson();
            fs::path statePath = m_historyPath / STATE_FILE;

            std::ofstream stateFile(statePath);
            stateFile << stateJson;
            stateFile.close();

            snapshot.fileSize = stateJson.size();

            // Generate description
            snapshot.description = generateDescription(state, event);

            // Git commit
            std::string commitHash = gitCommit(snapshot.description);
            snapshot.id = commitHash.substr(0, 7);  // Short hash

            // Save snapshot metadata
            saveSnapshotMetadata(snapshot);

            m_snapshots.push_back(snapshot);
            m_snapshotCount++;

            // Notify callback
            if (m_snapshotCallback) {
                m_snapshotCallback(snapshot);
            }

            // Prune old snapshots if needed
            if (m_snapshots.size() > MAX_SNAPSHOTS) {
                pruneOldSnapshots();
            }

        } catch (const std::exception& e) {
            m_lastError = e.what();
        }

        return snapshot;
    }

    /**
     * Restore state from a snapshot
     */
    bool restoreState(const std::string& snapshotId) {
        if (!m_initialized) {
            return false;
        }

        try {
            // Git checkout the specific commit
            std::string command = "cd \"" + m_historyPath.string() +
                                  "\" && git checkout " + snapshotId + " -- " + STATE_FILE;
            int result = std::system(command.c_str());

            return result == 0;

        } catch (const std::exception& e) {
            m_lastError = e.what();
            return false;
        }
    }

    /**
     * Get snapshot history
     */
    std::vector<TimeSnapshot> getHistory(int limit = 50) const {
        if (limit <= 0 || limit > static_cast<int>(m_snapshots.size())) {
            return m_snapshots;
        }

        return std::vector<TimeSnapshot>(
            m_snapshots.end() - limit,
            m_snapshots.end()
        );
    }

    /**
     * Get snapshot by ID
     */
    TimeSnapshot getSnapshot(const std::string& id) const {
        for (const auto& snapshot : m_snapshots) {
            if (snapshot.id == id) {
                return snapshot;
            }
        }
        return TimeSnapshot{};
    }

    /**
     * Set callback for snapshot events
     */
    void setSnapshotCallback(SnapshotCallback callback) {
        m_snapshotCallback = std::move(callback);
    }

    /**
     * Get last error message
     */
    std::string getLastError() const {
        return m_lastError;
    }

    /**
     * Get snapshot count
     */
    int getSnapshotCount() const noexcept {
        return m_snapshotCount;
    }

    /**
     * Check if initialized
     */
    bool isInitialized() const noexcept {
        return m_initialized;
    }

    /**
     * Get history path
     */
    std::string getHistoryPath() const {
        return m_historyPath.string();
    }

private:
    /**
     * Initialize Git repository
     */
    bool initGitRepo() {
        std::string command = "cd \"" + m_historyPath.string() +
                              "\" && git init --quiet";
        int result = std::system(command.c_str());

        if (result != 0) {
            m_lastError = "Failed to initialize Git repository";
            return false;
        }

        // Configure Git for this repo
        command = "cd \"" + m_historyPath.string() +
                  "\" && git config user.email \"idaw@local\" && " +
                  "git config user.name \"iDAW Time Machine\"";
        std::system(command.c_str());

        // Initial commit
        std::ofstream readme(m_historyPath / "README.md");
        readme << "# iDAW Time Machine History\n\n";
        readme << "This directory contains automatic project snapshots.\n";
        readme << "Do not modify manually.\n";
        readme.close();

        command = "cd \"" + m_historyPath.string() +
                  "\" && git add . && git commit -m \"Initialize Time Machine\" --quiet";
        std::system(command.c_str());

        return true;
    }

    /**
     * Create .gitignore in parent project to hide history
     */
    void createGitIgnore() {
        fs::path gitignorePath = fs::path(m_projectPath) / ".gitignore";

        // Check if .gitignore exists and if it already has our entry
        if (fs::exists(gitignorePath)) {
            std::ifstream existing(gitignorePath);
            std::string content((std::istreambuf_iterator<char>(existing)),
                                 std::istreambuf_iterator<char>());
            if (content.find(HISTORY_DIR) != std::string::npos) {
                return;  // Already has entry
            }
            existing.close();
        }

        // Append our entry
        std::ofstream gitignore(gitignorePath, std::ios::app);
        gitignore << "\n# iDAW Time Machine (local history)\n";
        gitignore << HISTORY_DIR << "/\n";
        gitignore.close();
    }

    /**
     * Git commit current state
     */
    std::string gitCommit(const std::string& message) {
        std::string command = "cd \"" + m_historyPath.string() +
                              "\" && git add -A && git commit -m \"" +
                              message + "\" --quiet";
        std::system(command.c_str());

        // Get commit hash
        command = "cd \"" + m_historyPath.string() +
                  "\" && git rev-parse HEAD";

        std::array<char, 128> buffer;
        std::string result;

        FILE* pipe = popen(command.c_str(), "r");
        if (pipe) {
            while (fgets(buffer.data(), buffer.size(), pipe) != nullptr) {
                result += buffer.data();
            }
            pclose(pipe);
        }

        // Trim whitespace
        result.erase(result.find_last_not_of(" \n\r\t") + 1);
        return result;
    }

    /**
     * Save snapshot metadata
     */
    void saveSnapshotMetadata(const TimeSnapshot& snapshot) {
        fs::path metaPath = m_historyPath / "snapshots" / (snapshot.id + ".json");

        std::ofstream metaFile(metaPath);
        metaFile << "{\n";
        metaFile << "  \"id\": \"" << snapshot.id << "\",\n";
        metaFile << "  \"timestamp\": \"" << snapshot.timestamp << "\",\n";
        metaFile << "  \"description\": \"" << snapshot.description << "\",\n";
        metaFile << "  \"triggerEvent\": \"" << snapshot.triggerEvent << "\",\n";
        metaFile << "  \"chaosValue\": " << snapshot.chaosValue << ",\n";
        metaFile << "  \"complexityValue\": " << snapshot.complexityValue << ",\n";
        metaFile << "  \"moodProfile\": \"" << snapshot.moodProfile << "\",\n";
        metaFile << "  \"fileSize\": " << snapshot.fileSize << "\n";
        metaFile << "}\n";
        metaFile.close();
    }

    /**
     * Load snapshot history from disk
     */
    void loadSnapshotHistory() {
        fs::path snapshotsDir = m_historyPath / "snapshots";

        if (!fs::exists(snapshotsDir)) {
            return;
        }

        for (const auto& entry : fs::directory_iterator(snapshotsDir)) {
            if (entry.path().extension() == ".json") {
                // Parse snapshot metadata (simplified)
                TimeSnapshot snapshot;
                snapshot.id = entry.path().stem().string();
                m_snapshots.push_back(snapshot);
            }
        }

        m_snapshotCount = static_cast<int>(m_snapshots.size());
    }

    /**
     * Prune old snapshots to stay under limit
     */
    void pruneOldSnapshots() {
        // Keep every 10th snapshot for history, remove others
        while (m_snapshots.size() > MAX_SNAPSHOTS) {
            // Remove oldest non-milestone snapshot
            for (auto it = m_snapshots.begin(); it != m_snapshots.end(); ++it) {
                size_t index = std::distance(m_snapshots.begin(), it);
                if (index % 10 != 0) {
                    m_snapshots.erase(it);
                    break;
                }
            }
        }
    }

    /**
     * Generate description for snapshot
     */
    std::string generateDescription(const ProjectState& state, TimeMachineEvent event) {
        std::ostringstream ss;

        switch (event) {
            case TimeMachineEvent::FLIP_TO_SIDE_A:
                ss << "Flip to Work Mode";
                break;
            case TimeMachineEvent::FLIP_TO_SIDE_B:
                ss << "Flip to Dream Mode";
                break;
            case TimeMachineEvent::CONFIRM_OUTPUT:
                ss << "Confirmed output";
                break;
            case TimeMachineEvent::MANUAL_SAVE:
                ss << "Manual save";
                break;
            case TimeMachineEvent::AUTO_INTERVAL:
                ss << "Auto-save";
                break;
            case TimeMachineEvent::BEFORE_DESTRUCTIVE_OP:
                ss << "Pre-operation backup";
                break;
        }

        if (!state.sideB.moodProfile.empty()) {
            ss << " [" << state.sideB.moodProfile << "]";
        }

        ss << " C:" << static_cast<int>(state.sideB.chaos * 100) << "%";
        ss << " X:" << static_cast<int>(state.sideB.complexity * 100) << "%";

        return ss.str();
    }

    /**
     * Convert event to string
     */
    static std::string eventToString(TimeMachineEvent event) {
        switch (event) {
            case TimeMachineEvent::FLIP_TO_SIDE_A: return "flip_to_a";
            case TimeMachineEvent::FLIP_TO_SIDE_B: return "flip_to_b";
            case TimeMachineEvent::CONFIRM_OUTPUT: return "confirm";
            case TimeMachineEvent::MANUAL_SAVE: return "manual";
            case TimeMachineEvent::AUTO_INTERVAL: return "auto";
            case TimeMachineEvent::BEFORE_DESTRUCTIVE_OP: return "backup";
            default: return "unknown";
        }
    }

    /**
     * Get current timestamp in ISO 8601 format
     */
    static std::string getCurrentTimestamp() {
        auto now = std::chrono::system_clock::now();
        auto time = std::chrono::system_clock::to_time_t(now);
        std::tm tm = *std::localtime(&time);

        std::ostringstream ss;
        ss << std::put_time(&tm, "%Y-%m-%dT%H:%M:%S");
        return ss.str();
    }

    // State
    std::string m_projectPath;
    fs::path m_historyPath;
    bool m_initialized;
    int m_snapshotCount;
    std::string m_lastError;

    std::vector<TimeSnapshot> m_snapshots;
    SnapshotCallback m_snapshotCallback;
};

} // namespace iDAW
