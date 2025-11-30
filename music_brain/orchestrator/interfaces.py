"""
Abstract Interfaces for AI Orchestrator Processing Modules.

Provides base classes and contracts for:
- Processor implementations
- Configuration management
- Result handling

All processing modules should implement ProcessorInterface.

Usage:
    from music_brain.orchestrator.interfaces import ProcessorInterface, ProcessorResult

    class HarmonyProcessor(ProcessorInterface):
        async def process(self, input_data, context):
            # Process harmony generation
            return ProcessorResult(success=True, data=harmony_data)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Generic


class ProcessorStatus(Enum):
    """Status of a processor execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ProcessorConfig:
    """
    Configuration for a processor.

    Attributes:
        name: Processor name
        enabled: Whether the processor is active
        timeout_seconds: Maximum execution time
        retry_count: Number of retries on failure
        params: Processor-specific parameters
    """
    name: str
    enabled: bool = True
    timeout_seconds: float = 30.0
    retry_count: int = 0
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
            "params": self.params,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessorConfig":
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            enabled=data.get("enabled", True),
            timeout_seconds=data.get("timeout_seconds", 30.0),
            retry_count=data.get("retry_count", 0),
            params=data.get("params", {}),
        )


@dataclass
class ProcessorResult:
    """
    Result from a processor execution.

    Attributes:
        success: Whether processing succeeded
        data: Output data from processor
        error: Error message if failed
        metadata: Additional execution metadata
        duration_ms: Execution time in milliseconds
    """
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "duration_ms": self.duration_ms,
        }


# Type variable for input/output types
T_Input = TypeVar("T_Input")
T_Output = TypeVar("T_Output")


class ProcessorInterface(ABC, Generic[T_Input, T_Output]):
    """
    Abstract base class for all processing modules.

    Processors are the building blocks of AI pipelines. Each processor:
    - Receives input data and execution context
    - Performs a specific transformation or analysis
    - Returns a ProcessorResult with output data

    Example implementation:
        class HarmonyProcessor(ProcessorInterface[IntentData, ChordProgression]):
            async def process(self, input_data, context):
                # Generate harmony from intent
                harmony = self._generate_harmony(input_data)
                return ProcessorResult(success=True, data=harmony)

            async def validate_input(self, input_data):
                return isinstance(input_data, IntentData)
    """

    def __init__(self, config: Optional[ProcessorConfig] = None):
        self.config = config or ProcessorConfig(name=self.__class__.__name__)
        self._status = ProcessorStatus.PENDING
        self._last_result: Optional[ProcessorResult] = None

    @property
    def name(self) -> str:
        """Get processor name."""
        return self.config.name

    @property
    def status(self) -> ProcessorStatus:
        """Get current processor status."""
        return self._status

    @property
    def last_result(self) -> Optional[ProcessorResult]:
        """Get the last execution result."""
        return self._last_result

    @abstractmethod
    async def process(
        self,
        input_data: T_Input,
        context: "ExecutionContext",
    ) -> ProcessorResult:
        """
        Process input data and return result.

        Args:
            input_data: Input data to process
            context: Execution context with pipeline state

        Returns:
            ProcessorResult with output data or error
        """
        pass

    async def validate_input(self, input_data: T_Input) -> bool:
        """
        Validate input data before processing.

        Override in subclasses for specific validation.

        Args:
            input_data: Input data to validate

        Returns:
            True if input is valid
        """
        return True

    async def pre_process(
        self,
        input_data: T_Input,
        context: "ExecutionContext",
    ) -> T_Input:
        """
        Pre-processing hook called before main processing.

        Override in subclasses for input transformation.

        Args:
            input_data: Input data
            context: Execution context

        Returns:
            Transformed input data
        """
        return input_data

    async def post_process(
        self,
        result: ProcessorResult,
        context: "ExecutionContext",
    ) -> ProcessorResult:
        """
        Post-processing hook called after main processing.

        Override in subclasses for result transformation.

        Args:
            result: Processing result
            context: Execution context

        Returns:
            Transformed result
        """
        return result

    async def on_error(
        self,
        error: Exception,
        context: "ExecutionContext",
    ) -> Optional[ProcessorResult]:
        """
        Error handler called when processing fails.

        Override in subclasses for custom error handling.

        Args:
            error: Exception that occurred
            context: Execution context

        Returns:
            Optional fallback result, or None to propagate error
        """
        return None

    def reset(self):
        """Reset processor state for reuse."""
        self._status = ProcessorStatus.PENDING
        self._last_result = None


@dataclass
class ExecutionContext:
    """
    Context passed to processors during pipeline execution.

    Provides:
    - Access to pipeline state and results from previous stages
    - Shared data between processors
    - Execution metadata

    Attributes:
        execution_id: Unique identifier for this execution
        pipeline_id: Identifier of the executing pipeline
        stage_name: Current stage name
        stage_index: Index of current stage in pipeline
        stage_results: Results from completed stages
        shared_data: Shared state between processors
        metadata: Execution metadata
        started_at: Execution start time
    """
    execution_id: str
    pipeline_id: str
    stage_name: str = ""
    stage_index: int = 0
    stage_results: Dict[str, ProcessorResult] = field(default_factory=dict)
    shared_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_stage_result(self, stage_name: str) -> Optional[ProcessorResult]:
        """Get result from a completed stage."""
        return self.stage_results.get(stage_name)

    def get_stage_data(self, stage_name: str) -> Any:
        """Get output data from a completed stage."""
        result = self.get_stage_result(stage_name)
        return result.data if result and result.success else None

    def set_shared(self, key: str, value: Any):
        """Set a shared value accessible by all processors."""
        self.shared_data[key] = value

    def get_shared(self, key: str, default: Any = None) -> Any:
        """Get a shared value."""
        return self.shared_data.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "pipeline_id": self.pipeline_id,
            "stage_name": self.stage_name,
            "stage_index": self.stage_index,
            "stage_results": {
                name: result.to_dict()
                for name, result in self.stage_results.items()
            },
            "shared_data": self.shared_data,
            "metadata": self.metadata,
            "started_at": self.started_at,
        }


class CallbackInterface(ABC):
    """
    Interface for pipeline execution callbacks.

    Implement to receive notifications about pipeline events.
    """

    @abstractmethod
    async def on_pipeline_start(
        self,
        pipeline_id: str,
        context: ExecutionContext,
    ):
        """Called when pipeline execution starts."""
        pass

    @abstractmethod
    async def on_pipeline_complete(
        self,
        pipeline_id: str,
        context: ExecutionContext,
        duration_ms: float,
    ):
        """Called when pipeline execution completes successfully."""
        pass

    @abstractmethod
    async def on_pipeline_error(
        self,
        pipeline_id: str,
        context: ExecutionContext,
        error: Exception,
    ):
        """Called when pipeline execution fails."""
        pass

    @abstractmethod
    async def on_stage_start(
        self,
        stage_name: str,
        context: ExecutionContext,
    ):
        """Called when a stage starts processing."""
        pass

    @abstractmethod
    async def on_stage_complete(
        self,
        stage_name: str,
        context: ExecutionContext,
        result: ProcessorResult,
        duration_ms: float,
    ):
        """Called when a stage completes processing."""
        pass

    @abstractmethod
    async def on_stage_error(
        self,
        stage_name: str,
        context: ExecutionContext,
        error: Exception,
    ):
        """Called when a stage fails."""
        pass


class DefaultCallback(CallbackInterface):
    """Default no-op callback implementation."""

    async def on_pipeline_start(self, pipeline_id, context):
        pass

    async def on_pipeline_complete(self, pipeline_id, context, duration_ms):
        pass

    async def on_pipeline_error(self, pipeline_id, context, error):
        pass

    async def on_stage_start(self, stage_name, context):
        pass

    async def on_stage_complete(self, stage_name, context, result, duration_ms):
        pass

    async def on_stage_error(self, stage_name, context, error):
        pass
