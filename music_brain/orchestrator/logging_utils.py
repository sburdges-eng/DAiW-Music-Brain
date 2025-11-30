"""
Logging Utilities for AI Orchestrator.

Provides detailed logging infrastructure for:
- Pipeline execution monitoring
- Stage-by-stage progress tracking
- Debug information for troubleshooting
- Performance metrics

Usage:
    from music_brain.orchestrator.logging_utils import get_logger, LogLevel

    logger = get_logger("my_pipeline")
    logger.info("Starting pipeline execution")
    logger.debug("Processing stage: harmony_generation", extra={"stage": "harmony"})
"""

import logging
import sys
import time
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path


class LogLevel(Enum):
    """Log levels for orchestrator logging."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


@dataclass
class LogEntry:
    """Structured log entry for pipeline execution."""
    timestamp: str
    level: str
    message: str
    logger_name: str
    pipeline_id: Optional[str] = None
    stage_name: Optional[str] = None
    execution_id: Optional[str] = None
    duration_ms: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


class LogFormatter(logging.Formatter):
    """Custom formatter for orchestrator logs with pipeline context."""

    DEFAULT_FORMAT = (
        "%(asctime)s | %(levelname)-8s | %(name)s | "
        "%(pipeline_id)s | %(stage_name)s | %(message)s"
    )
    DEBUG_FORMAT = (
        "%(asctime)s | %(levelname)-8s | %(name)s | "
        "[%(filename)s:%(lineno)d] | %(pipeline_id)s | %(stage_name)s | %(message)s"
    )

    def __init__(self, debug_mode: bool = False):
        fmt = self.DEBUG_FORMAT if debug_mode else self.DEFAULT_FORMAT
        super().__init__(fmt, datefmt="%Y-%m-%d %H:%M:%S")
        self.debug_mode = debug_mode

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with pipeline context."""
        # Add default values for custom fields if not present
        if not hasattr(record, 'pipeline_id'):
            record.pipeline_id = '-'
        if not hasattr(record, 'stage_name'):
            record.stage_name = '-'

        return super().format(record)


class JsonLogFormatter(logging.Formatter):
    """JSON formatter for structured logging output."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=record.levelname,
            message=record.getMessage(),
            logger_name=record.name,
            pipeline_id=getattr(record, 'pipeline_id', None),
            stage_name=getattr(record, 'stage_name', None),
            execution_id=getattr(record, 'execution_id', None),
            duration_ms=getattr(record, 'duration_ms', None),
            extra=getattr(record, 'extra_data', {}),
        )
        return entry.to_json()


class OrchestratorLogger:
    """
    Enhanced logger for AI orchestrator with pipeline context.

    Provides:
    - Contextual logging with pipeline/stage info
    - Performance timing
    - Structured output (text or JSON)
    - Log history for debugging

    Usage:
        logger = OrchestratorLogger("my_pipeline")
        logger.set_context(pipeline_id="pipe_123", stage_name="harmony")
        logger.info("Processing input data")

        with logger.timed_operation("chord_analysis"):
            # ... do work ...
            pass
    """

    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        json_output: bool = False,
        debug_mode: bool = False,
        log_file: Optional[Path] = None,
    ):
        self.name = name
        self._logger = logging.getLogger(f"daiw.orchestrator.{name}")
        self._logger.setLevel(level.value)

        # Context for pipeline/stage tracking
        self._context: Dict[str, Any] = {}

        # Log history for debugging
        self._history: List[LogEntry] = []
        self._max_history = 1000

        # Timing stack for nested operations
        self._timing_stack: List[Dict[str, Any]] = []

        # Setup handlers
        self._setup_handlers(json_output, debug_mode, log_file)

    def _setup_handlers(
        self,
        json_output: bool,
        debug_mode: bool,
        log_file: Optional[Path],
    ):
        """Configure logging handlers."""
        # Remove existing handlers
        self._logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        if json_output:
            console_handler.setFormatter(JsonLogFormatter())
        else:
            console_handler.setFormatter(LogFormatter(debug_mode=debug_mode))
        self._logger.addHandler(console_handler)

        # File handler (if specified)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(JsonLogFormatter())  # Always JSON for files
            self._logger.addHandler(file_handler)

    def set_context(self, **kwargs):
        """Set context values that will be included in all log messages."""
        self._context.update(kwargs)

    def clear_context(self):
        """Clear all context values."""
        self._context.clear()

    def _log(
        self,
        level: int,
        message: str,
        *args,
        exc_info: bool = False,
        **kwargs,
    ):
        """Internal log method with context injection."""
        # Merge context with kwargs
        extra = {**self._context, **kwargs}

        # Create log record extras
        extra_fields = {
            k: v for k, v in extra.items()
            if k not in ('pipeline_id', 'stage_name', 'execution_id', 'duration_ms')
        }
        record_extras = {
            'pipeline_id': extra.get('pipeline_id', '-'),
            'stage_name': extra.get('stage_name', '-'),
            'execution_id': extra.get('execution_id'),
            'duration_ms': extra.get('duration_ms'),
            'extra_data': extra_fields,
        }

        # Log the message
        self._logger.log(level, message, *args, extra=record_extras, exc_info=exc_info)

        # Store in history
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=logging.getLevelName(level),
            message=message % args if args else message,
            logger_name=self.name,
            pipeline_id=record_extras.get('pipeline_id'),
            stage_name=record_extras.get('stage_name'),
            execution_id=record_extras.get('execution_id'),
            duration_ms=record_extras.get('duration_ms'),
            extra=extra_fields,
        )
        self._history.append(entry)
        if len(self._history) > self._max_history:
            self._history.pop(0)

    def debug(self, message: str, *args, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log info message."""
        self._log(logging.INFO, message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, message, *args, **kwargs)

    def error(self, message: str, *args, exc_info: bool = True, **kwargs):
        """Log error message with optional exception info."""
        self._log(logging.ERROR, message, *args, exc_info=exc_info, **kwargs)

    def critical(self, message: str, *args, exc_info: bool = True, **kwargs):
        """Log critical message with optional exception info."""
        self._log(logging.CRITICAL, message, *args, exc_info=exc_info, **kwargs)

    def stage_start(self, stage_name: str, **kwargs):
        """Log the start of a pipeline stage."""
        self.set_context(stage_name=stage_name)
        self.info("Stage started: %s", stage_name, **kwargs)

    def stage_complete(self, stage_name: str, duration_ms: float, **kwargs):
        """Log the completion of a pipeline stage."""
        self.info(
            "Stage completed: %s (%.2f ms)",
            stage_name, duration_ms,
            duration_ms=duration_ms,
            **kwargs,
        )

    def stage_failed(self, stage_name: str, error: Exception, **kwargs):
        """Log a stage failure."""
        self.error(
            "Stage failed: %s - %s",
            stage_name, str(error),
            stage_name=stage_name,
            exc_info=True,
            **kwargs,
        )

    def pipeline_start(self, pipeline_id: str, **kwargs):
        """Log the start of a pipeline execution."""
        self.set_context(pipeline_id=pipeline_id)
        self.info("Pipeline started: %s", pipeline_id, **kwargs)

    def pipeline_complete(self, pipeline_id: str, duration_ms: float, **kwargs):
        """Log the completion of a pipeline."""
        self.info(
            "Pipeline completed: %s (%.2f ms)",
            pipeline_id, duration_ms,
            duration_ms=duration_ms,
            **kwargs,
        )

    def pipeline_failed(self, pipeline_id: str, error: Exception, **kwargs):
        """Log a pipeline failure."""
        self.error(
            "Pipeline failed: %s - %s",
            pipeline_id, str(error),
            exc_info=True,
            **kwargs,
        )

    class TimedOperation:
        """Context manager for timing operations."""

        def __init__(self, logger: 'OrchestratorLogger', operation_name: str):
            self.logger = logger
            self.operation_name = operation_name
            self.start_time: float = 0
            self.duration_ms: float = 0

        def __enter__(self):
            self.start_time = time.perf_counter()
            self.logger.debug("Starting operation: %s", self.operation_name)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.duration_ms = (time.perf_counter() - self.start_time) * 1000
            if exc_type is None:
                self.logger.debug(
                    "Completed operation: %s (%.2f ms)",
                    self.operation_name, self.duration_ms,
                    duration_ms=self.duration_ms,
                )
            else:
                self.logger.error(
                    "Failed operation: %s (%.2f ms) - %s",
                    self.operation_name, self.duration_ms, exc_val,
                    duration_ms=self.duration_ms,
                )
            return False  # Don't suppress exceptions

    def timed_operation(self, operation_name: str) -> TimedOperation:
        """Create a timed operation context manager."""
        return self.TimedOperation(self, operation_name)

    def get_history(
        self,
        level: Optional[LogLevel] = None,
        limit: int = 100,
    ) -> List[LogEntry]:
        """Get log history, optionally filtered by level."""
        history = self._history[-limit:]
        if level:
            history = [
                entry for entry in history
                if entry.level == level.name
            ]
        return history

    def export_history(self, filepath: Path):
        """Export log history to JSON file."""
        with open(filepath, 'w') as f:
            json.dump([entry.to_dict() for entry in self._history], f, indent=2)


# Global logger registry
_loggers: Dict[str, OrchestratorLogger] = {}


def get_logger(
    name: str,
    level: LogLevel = LogLevel.INFO,
    json_output: bool = False,
    debug_mode: bool = False,
) -> OrchestratorLogger:
    """
    Get or create an orchestrator logger.

    Args:
        name: Logger name (unique identifier)
        level: Minimum log level
        json_output: Use JSON formatting
        debug_mode: Include debug info (file/line)

    Returns:
        OrchestratorLogger instance
    """
    if name not in _loggers:
        _loggers[name] = OrchestratorLogger(
            name=name,
            level=level,
            json_output=json_output,
            debug_mode=debug_mode,
        )
    return _loggers[name]


def configure_global_logging(
    level: LogLevel = LogLevel.INFO,
    json_output: bool = False,
    debug_mode: bool = False,
):
    """Configure global logging settings for all orchestrator loggers."""
    root_logger = logging.getLogger("daiw.orchestrator")
    root_logger.setLevel(level.value)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add console handler
    handler = logging.StreamHandler(sys.stdout)
    if json_output:
        handler.setFormatter(JsonLogFormatter())
    else:
        handler.setFormatter(LogFormatter(debug_mode=debug_mode))
    root_logger.addHandler(handler)
