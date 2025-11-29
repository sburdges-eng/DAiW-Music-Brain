"""
MCP Workstation - Debugging Protocol

Comprehensive logging, tracing, and debugging for multi-AI coordination.
"""

import logging
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from functools import wraps
from enum import Enum
from dataclasses import dataclass, field
import threading


class LogLevel(str, Enum):
    """Log severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DebugCategory(str, Enum):
    """Categories for debugging/tracing."""
    AI_COMMUNICATION = "ai_comm"
    PROPOSAL = "proposal"
    PHASE = "phase"
    TASK = "task"
    ORCHESTRATION = "orchestration"
    STORAGE = "storage"
    MCP = "mcp"
    PERFORMANCE = "performance"


@dataclass
class DebugEvent:
    """A single debug event."""
    timestamp: str
    level: LogLevel
    category: DebugCategory
    agent: Optional[str]
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    trace: Optional[str] = None
    duration_ms: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "level": self.level.value,
            "category": self.category.value,
            "agent": self.agent,
            "message": self.message,
            "data": self.data,
            "trace": self.trace,
            "duration_ms": self.duration_ms,
        }

    def __str__(self) -> str:
        agent_str = f"[{self.agent}]" if self.agent else ""
        return f"{self.timestamp} {self.level.value.upper():8} {self.category.value:12} {agent_str} {self.message}"


class DebugProtocol:
    """
    Central debugging and logging protocol for the workstation.

    Features:
    - Structured logging with categories
    - Performance tracing
    - AI communication tracking
    - Error capture with stack traces
    - Session playback for debugging
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.events: List[DebugEvent] = []
        self.max_events = 10000
        self.log_file: Optional[Path] = None
        self.console_output = True
        self.min_level = LogLevel.INFO
        self._file_handler = None

        # Performance tracking
        self._timers: Dict[str, float] = {}

        # Setup Python logging integration
        self._setup_logging()

    def _setup_logging(self):
        """Setup Python logging integration."""
        self.logger = logging.getLogger("mcp_workstation")
        self.logger.setLevel(logging.DEBUG)

        # Console handler
        if self.console_output:
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
            console.setFormatter(fmt)
            self.logger.addHandler(console)

    def set_log_file(self, path: str):
        """Set file for persistent logging."""
        self.log_file = Path(path)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Add file handler to logger
        if self._file_handler:
            self.logger.removeHandler(self._file_handler)

        self._file_handler = logging.FileHandler(str(self.log_file))
        self._file_handler.setLevel(logging.DEBUG)
        fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        self._file_handler.setFormatter(fmt)
        self.logger.addHandler(self._file_handler)

    def set_level(self, level: LogLevel):
        """Set minimum log level."""
        self.min_level = level
        py_level = getattr(logging, level.value.upper())
        self.logger.setLevel(py_level)

    def log(
        self,
        level: LogLevel,
        category: DebugCategory,
        message: str,
        agent: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        include_trace: bool = False,
        duration_ms: Optional[float] = None,
    ):
        """Log a debug event."""
        # Check level
        levels = list(LogLevel)
        if levels.index(level) < levels.index(self.min_level):
            return

        event = DebugEvent(
            timestamp=datetime.now().isoformat(),
            level=level,
            category=category,
            agent=agent,
            message=message,
            data=data or {},
            trace=traceback.format_exc() if include_trace else None,
            duration_ms=duration_ms,
        )

        # Store event
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]

        # Python logging
        py_level = getattr(logging, level.value.upper())
        self.logger.log(py_level, str(event))

        # Write to file if enabled
        if self.log_file:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(json.dumps(event.to_dict()) + "\n")
            except Exception:
                pass

    def debug(self, category: DebugCategory, message: str, **kwargs):
        """Log debug message."""
        self.log(LogLevel.DEBUG, category, message, **kwargs)

    def info(self, category: DebugCategory, message: str, **kwargs):
        """Log info message."""
        self.log(LogLevel.INFO, category, message, **kwargs)

    def warning(self, category: DebugCategory, message: str, **kwargs):
        """Log warning message."""
        self.log(LogLevel.WARNING, category, message, **kwargs)

    def error(self, category: DebugCategory, message: str, **kwargs):
        """Log error message."""
        kwargs.setdefault('include_trace', True)
        self.log(LogLevel.ERROR, category, message, **kwargs)

    def critical(self, category: DebugCategory, message: str, **kwargs):
        """Log critical message."""
        kwargs.setdefault('include_trace', True)
        self.log(LogLevel.CRITICAL, category, message, **kwargs)

    # Performance tracing
    def start_timer(self, name: str):
        """Start a performance timer."""
        import time
        self._timers[name] = time.perf_counter()

    def stop_timer(self, name: str, category: DebugCategory, message: str = "") -> float:
        """Stop timer and log duration."""
        import time
        if name not in self._timers:
            return 0.0

        duration_ms = (time.perf_counter() - self._timers[name]) * 1000
        del self._timers[name]

        self.log(
            LogLevel.DEBUG,
            category,
            message or f"Timer '{name}' completed",
            duration_ms=duration_ms,
        )
        return duration_ms

    # AI Communication tracking
    def log_ai_request(self, agent: str, request_type: str, data: Dict[str, Any]):
        """Log an AI request."""
        self.info(
            DebugCategory.AI_COMMUNICATION,
            f"Request to {agent}: {request_type}",
            agent=agent,
            data={"request_type": request_type, **data},
        )

    def log_ai_response(self, agent: str, response_type: str, data: Dict[str, Any]):
        """Log an AI response."""
        self.info(
            DebugCategory.AI_COMMUNICATION,
            f"Response from {agent}: {response_type}",
            agent=agent,
            data={"response_type": response_type, **data},
        )

    def log_ai_error(self, agent: str, error: str, details: Dict[str, Any] = None):
        """Log an AI error."""
        self.error(
            DebugCategory.AI_COMMUNICATION,
            f"Error from {agent}: {error}",
            agent=agent,
            data=details or {},
        )

    # Query methods
    def get_events(
        self,
        level: Optional[LogLevel] = None,
        category: Optional[DebugCategory] = None,
        agent: Optional[str] = None,
        limit: int = 100,
    ) -> List[DebugEvent]:
        """Get filtered events."""
        events = self.events

        if level:
            events = [e for e in events if e.level == level]
        if category:
            events = [e for e in events if e.category == category]
        if agent:
            events = [e for e in events if e.agent == agent]

        return events[-limit:]

    def get_errors(self, limit: int = 50) -> List[DebugEvent]:
        """Get recent errors."""
        return [e for e in self.events if e.level in (LogLevel.ERROR, LogLevel.CRITICAL)][-limit:]

    def get_ai_activity(self, agent: str, limit: int = 50) -> List[DebugEvent]:
        """Get recent activity for an AI agent."""
        return self.get_events(agent=agent, limit=limit)

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report from logged durations."""
        perf_events = [e for e in self.events if e.duration_ms is not None]

        if not perf_events:
            return {"message": "No performance data collected"}

        durations = [e.duration_ms for e in perf_events]
        return {
            "total_operations": len(perf_events),
            "total_time_ms": sum(durations),
            "avg_time_ms": sum(durations) / len(durations),
            "max_time_ms": max(durations),
            "min_time_ms": min(durations),
            "by_category": self._group_performance_by_category(perf_events),
        }

    def _group_performance_by_category(self, events: List[DebugEvent]) -> Dict[str, Dict]:
        """Group performance by category."""
        by_cat = {}
        for e in events:
            cat = e.category.value
            if cat not in by_cat:
                by_cat[cat] = {"count": 0, "total_ms": 0, "durations": []}
            by_cat[cat]["count"] += 1
            by_cat[cat]["total_ms"] += e.duration_ms
            by_cat[cat]["durations"].append(e.duration_ms)

        for cat, data in by_cat.items():
            data["avg_ms"] = data["total_ms"] / data["count"]
            del data["durations"]

        return by_cat

    def export_session(self, path: str):
        """Export all events to JSON for session replay."""
        with open(path, 'w') as f:
            json.dump([e.to_dict() for e in self.events], f, indent=2)

    def clear(self):
        """Clear all events."""
        self.events = []


# Global instance
_debug = None


def get_debug() -> DebugProtocol:
    """Get the global debug protocol instance."""
    global _debug
    if _debug is None:
        _debug = DebugProtocol()
    return _debug


# Decorator for function tracing
def trace(category: DebugCategory = DebugCategory.ORCHESTRATION):
    """Decorator to trace function execution."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            debug = get_debug()
            func_name = f"{func.__module__}.{func.__name__}"
            debug.start_timer(func_name)
            debug.debug(category, f"Entering {func_name}")

            try:
                result = func(*args, **kwargs)
                duration = debug.stop_timer(func_name, category, f"Completed {func_name}")
                return result
            except Exception as e:
                debug.error(category, f"Error in {func_name}: {e}")
                raise

        return wrapper
    return decorator


# Convenience functions
def log_debug(category: DebugCategory, message: str, **kwargs):
    get_debug().debug(category, message, **kwargs)


def log_info(category: DebugCategory, message: str, **kwargs):
    get_debug().info(category, message, **kwargs)


def log_warning(category: DebugCategory, message: str, **kwargs):
    get_debug().warning(category, message, **kwargs)


def log_error(category: DebugCategory, message: str, **kwargs):
    get_debug().error(category, message, **kwargs)
