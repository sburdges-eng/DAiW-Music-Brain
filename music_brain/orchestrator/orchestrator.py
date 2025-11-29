"""
AI Orchestrator - Central coordination for DAiW Music Brain AI pipelines.

The AIOrchestrator is the main entry point for executing AI pipelines.
It manages:
- Pipeline execution with stage management
- Execution context and state
- Error handling and recovery
- Callback notifications
- Detailed logging

Usage:
    from music_brain.orchestrator import AIOrchestrator, Pipeline

    # Create orchestrator
    orchestrator = AIOrchestrator()

    # Execute pipeline
    result = await orchestrator.execute(pipeline, input_data)

    # Or with context manager
    async with AIOrchestrator() as orchestrator:
        result = await orchestrator.execute(pipeline, input_data)
"""

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable

from music_brain.orchestrator.logging_utils import (
    OrchestratorLogger,
    LogLevel,
    get_logger,
)
from music_brain.orchestrator.interfaces import (
    ProcessorInterface,
    ProcessorResult,
    ProcessorStatus,
    ExecutionContext,
    CallbackInterface,
    DefaultCallback,
)
from music_brain.orchestrator.pipeline import (
    Pipeline,
    PipelineStage,
    PipelineStatus,
    StageResult,
)


@dataclass
class OrchestratorConfig:
    """
    Configuration for the AI Orchestrator.

    Attributes:
        default_timeout: Default timeout for stage execution (seconds)
        max_retries: Maximum retry attempts for failed stages
        enable_logging: Enable detailed logging
        log_level: Logging level
        json_logging: Use JSON format for logs
        debug_mode: Enable debug output
        parallel_stages: Allow parallel stage execution (experimental)
    """
    default_timeout: float = 30.0
    max_retries: int = 1
    enable_logging: bool = True
    log_level: LogLevel = LogLevel.INFO
    json_logging: bool = False
    debug_mode: bool = False
    parallel_stages: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "default_timeout": self.default_timeout,
            "max_retries": self.max_retries,
            "enable_logging": self.enable_logging,
            "log_level": self.log_level.name,
            "json_logging": self.json_logging,
            "debug_mode": self.debug_mode,
            "parallel_stages": self.parallel_stages,
        }


@dataclass
class ExecutionResult:
    """
    Result from a complete pipeline execution.

    Attributes:
        execution_id: Unique identifier for this execution
        pipeline_id: ID of the executed pipeline
        success: Whether execution completed successfully
        final_output: Output from the last stage
        stage_results: Results from all stages
        error: Error message if failed
        started_at: Execution start timestamp
        completed_at: Execution completion timestamp
        duration_ms: Total execution time in milliseconds
        context: Final execution context
    """
    execution_id: str
    pipeline_id: str
    success: bool
    final_output: Any = None
    stage_results: Dict[str, StageResult] = field(default_factory=dict)
    error: Optional[str] = None
    started_at: str = ""
    completed_at: str = ""
    duration_ms: float = 0.0
    context: Optional[ExecutionContext] = None

    def get_stage_output(self, stage_name: str) -> Any:
        """Get output from a specific stage."""
        result = self.stage_results.get(stage_name)
        return result.data if result else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "pipeline_id": self.pipeline_id,
            "success": self.success,
            "final_output": self.final_output,
            "stage_results": {
                name: result.to_dict()
                for name, result in self.stage_results.items()
            },
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
        }


class AIOrchestrator:
    """
    Central orchestration hub for AI pipelines.

    The AIOrchestrator coordinates the execution of processing pipelines,
    managing stage execution, context propagation, and error handling.

    Features:
    - Sequential pipeline execution with stage management
    - Execution context with shared state
    - Detailed logging and monitoring
    - Error handling with retries
    - Callback support for event notification
    - Async/await support

    Usage:
        # Create orchestrator
        config = OrchestratorConfig(log_level=LogLevel.DEBUG)
        orchestrator = AIOrchestrator(config)

        # Create pipeline
        pipeline = Pipeline("emotion_to_music")
        pipeline.add_stage("intent", intent_processor)
        pipeline.add_stage("harmony", harmony_processor)

        # Execute
        result = await orchestrator.execute(pipeline, {"emotion": "grief"})

        if result.success:
            print(f"Generated: {result.final_output}")
        else:
            print(f"Failed: {result.error}")
    """

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()

        # Logger
        self._logger = get_logger(
            "orchestrator",
            level=self.config.log_level if self.config.enable_logging else LogLevel.WARNING,
            json_output=self.config.json_logging,
            debug_mode=self.config.debug_mode,
        )

        # Callbacks
        self._callbacks: List[CallbackInterface] = [DefaultCallback()]

        # Execution history
        self._execution_history: List[ExecutionResult] = []
        self._max_history = 100

        # State
        self._running_executions: Dict[str, ExecutionContext] = {}

    def add_callback(self, callback: CallbackInterface):
        """Add a callback for pipeline events."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: CallbackInterface):
        """Remove a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    async def execute(
        self,
        pipeline: Pipeline,
        input_data: Any,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        """
        Execute a pipeline with input data.

        Args:
            pipeline: Pipeline to execute
            input_data: Initial input data for first stage
            initial_context: Optional initial shared context

        Returns:
            ExecutionResult with final output or error
        """
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"
        start_time = time.perf_counter()
        started_at = datetime.now().isoformat()

        # Create execution context
        context = ExecutionContext(
            execution_id=execution_id,
            pipeline_id=pipeline.id,
            shared_data=initial_context or {},
            started_at=started_at,
        )
        self._running_executions[execution_id] = context

        # Set logger context
        self._logger.set_context(
            pipeline_id=pipeline.id,
            execution_id=execution_id,
        )

        # Log pipeline start
        self._logger.pipeline_start(
            pipeline.id,
            stages=len(pipeline.stages),
            stage_names=pipeline.stage_names,
        )

        # Notify callbacks
        await self._notify_pipeline_start(pipeline.id, context)

        # Validate pipeline
        validation_errors = pipeline.validate()
        if validation_errors:
            error = f"Pipeline validation failed: {validation_errors}"
            self._logger.error(error)
            result = ExecutionResult(
                execution_id=execution_id,
                pipeline_id=pipeline.id,
                success=False,
                error=error,
                started_at=started_at,
                completed_at=datetime.now().isoformat(),
                duration_ms=(time.perf_counter() - start_time) * 1000,
                context=context,
            )
            await self._notify_pipeline_error(pipeline.id, context, ValueError(error))
            return result

        # Execute stages
        stage_results: Dict[str, StageResult] = {}
        current_data = input_data
        success = True
        error_message = None

        for idx, stage in enumerate(pipeline.stages):
            context.stage_name = stage.name
            context.stage_index = idx

            # Check condition
            if not stage.should_execute(context):
                self._logger.info(
                    "Skipping stage: %s (condition not met)",
                    stage.name,
                )
                continue

            # Execute stage
            stage_result = await self._execute_stage(
                stage,
                current_data,
                context,
            )

            # Store result
            stage_results[stage.name] = stage_result
            context.stage_results[stage.name] = stage_result.processor_result

            if stage_result.success:
                current_data = stage_result.data
            else:
                success = False
                error_message = f"Stage '{stage.name}' failed: {stage_result.error}"
                self._logger.pipeline_failed(pipeline.id, Exception(error_message))
                await self._notify_pipeline_error(
                    pipeline.id, context, Exception(error_message)
                )
                break

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000
        completed_at = datetime.now().isoformat()

        # Create result
        result = ExecutionResult(
            execution_id=execution_id,
            pipeline_id=pipeline.id,
            success=success,
            final_output=current_data if success else None,
            stage_results=stage_results,
            error=error_message,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            context=context,
        )

        # Log completion
        if success:
            self._logger.pipeline_complete(pipeline.id, duration_ms)
            await self._notify_pipeline_complete(pipeline.id, context, duration_ms)

        # Store in history
        self._execution_history.append(result)
        if len(self._execution_history) > self._max_history:
            self._execution_history.pop(0)

        # Cleanup
        del self._running_executions[execution_id]
        self._logger.clear_context()

        return result

    async def _execute_stage(
        self,
        stage: PipelineStage,
        input_data: Any,
        context: ExecutionContext,
    ) -> StageResult:
        """Execute a single pipeline stage."""
        start_time = time.perf_counter()
        started_at = datetime.now().isoformat()

        self._logger.stage_start(stage.name)
        await self._notify_stage_start(stage.name, context)

        # Transform input if needed
        if stage.transform_input:
            try:
                input_data = stage.transform_input(input_data, context)
            except Exception as e:
                self._logger.error("Input transformation failed: %s", str(e))

        # Validate input
        try:
            is_valid = await stage.processor.validate_input(input_data)
            if not is_valid:
                raise ValueError(f"Invalid input for stage '{stage.name}'")
        except Exception as e:
            self._logger.error("Input validation failed: %s", str(e))
            return StageResult(
                stage_name=stage.name,
                processor_result=ProcessorResult(
                    success=False,
                    error=f"Input validation failed: {str(e)}",
                ),
                started_at=started_at,
                completed_at=datetime.now().isoformat(),
                duration_ms=(time.perf_counter() - start_time) * 1000,
            )

        # Execute processor with retries
        retries = stage.config.retry_count or self.config.max_retries
        timeout = stage.config.timeout_seconds or self.config.default_timeout

        last_error = None
        for attempt in range(retries + 1):
            try:
                if attempt > 0:
                    self._logger.info(
                        "Retrying stage: %s (attempt %d/%d)",
                        stage.name, attempt + 1, retries + 1,
                    )

                # Pre-process
                processed_input = await stage.processor.pre_process(input_data, context)

                # Execute with timeout
                processor_result = await asyncio.wait_for(
                    stage.processor.process(processed_input, context),
                    timeout=timeout,
                )

                # Post-process
                processor_result = await stage.processor.post_process(
                    processor_result, context
                )

                # Transform output if needed
                if stage.transform_output:
                    try:
                        processor_result = stage.transform_output(processor_result, context)
                    except Exception as e:
                        self._logger.warning("Output transformation failed: %s", str(e))

                # Calculate duration
                duration_ms = (time.perf_counter() - start_time) * 1000

                # Log and notify
                self._logger.stage_complete(stage.name, duration_ms)
                await self._notify_stage_complete(
                    stage.name, context, processor_result, duration_ms
                )

                return StageResult(
                    stage_name=stage.name,
                    processor_result=processor_result,
                    started_at=started_at,
                    completed_at=datetime.now().isoformat(),
                    duration_ms=duration_ms,
                )

            except asyncio.TimeoutError:
                last_error = f"Stage '{stage.name}' timed out after {timeout}s"
                self._logger.warning(last_error)
            except Exception as e:
                last_error = str(e)
                self._logger.error("Stage '%s' failed: %s", stage.name, last_error)

                # Try error handler
                fallback = await stage.processor.on_error(e, context)
                if fallback:
                    return StageResult(
                        stage_name=stage.name,
                        processor_result=fallback,
                        started_at=started_at,
                        completed_at=datetime.now().isoformat(),
                        duration_ms=(time.perf_counter() - start_time) * 1000,
                    )

        # All retries failed
        duration_ms = (time.perf_counter() - start_time) * 1000
        self._logger.stage_failed(stage.name, Exception(last_error or "Unknown error"))
        await self._notify_stage_error(stage.name, context, Exception(last_error or "Unknown error"))

        return StageResult(
            stage_name=stage.name,
            processor_result=ProcessorResult(
                success=False,
                error=last_error,
            ),
            started_at=started_at,
            completed_at=datetime.now().isoformat(),
            duration_ms=duration_ms,
        )

    # Callback notification methods

    async def _notify_pipeline_start(self, pipeline_id: str, context: ExecutionContext):
        """Notify callbacks of pipeline start."""
        for callback in self._callbacks:
            try:
                await callback.on_pipeline_start(pipeline_id, context)
            except Exception as e:
                self._logger.debug("Callback error: %s", str(e))

    async def _notify_pipeline_complete(
        self,
        pipeline_id: str,
        context: ExecutionContext,
        duration_ms: float,
    ):
        """Notify callbacks of pipeline completion."""
        for callback in self._callbacks:
            try:
                await callback.on_pipeline_complete(pipeline_id, context, duration_ms)
            except Exception as e:
                self._logger.debug("Callback error: %s", str(e))

    async def _notify_pipeline_error(
        self,
        pipeline_id: str,
        context: ExecutionContext,
        error: Exception,
    ):
        """Notify callbacks of pipeline error."""
        for callback in self._callbacks:
            try:
                await callback.on_pipeline_error(pipeline_id, context, error)
            except Exception as e:
                self._logger.debug("Callback error: %s", str(e))

    async def _notify_stage_start(self, stage_name: str, context: ExecutionContext):
        """Notify callbacks of stage start."""
        for callback in self._callbacks:
            try:
                await callback.on_stage_start(stage_name, context)
            except Exception as e:
                self._logger.debug("Callback error: %s", str(e))

    async def _notify_stage_complete(
        self,
        stage_name: str,
        context: ExecutionContext,
        result: ProcessorResult,
        duration_ms: float,
    ):
        """Notify callbacks of stage completion."""
        for callback in self._callbacks:
            try:
                await callback.on_stage_complete(stage_name, context, result, duration_ms)
            except Exception as e:
                self._logger.debug("Callback error: %s", str(e))

    async def _notify_stage_error(
        self,
        stage_name: str,
        context: ExecutionContext,
        error: Exception,
    ):
        """Notify callbacks of stage error."""
        for callback in self._callbacks:
            try:
                await callback.on_stage_error(stage_name, context, error)
            except Exception as e:
                self._logger.debug("Callback error: %s", str(e))

    # Utility methods

    def get_execution_history(
        self,
        pipeline_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[ExecutionResult]:
        """Get execution history, optionally filtered by pipeline."""
        history = self._execution_history[-limit:]
        if pipeline_id:
            history = [r for r in history if r.pipeline_id == pipeline_id]
        return history

    def get_running_executions(self) -> Dict[str, ExecutionContext]:
        """Get currently running executions."""
        return dict(self._running_executions)

    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a running execution.

        Note: This is a best-effort cancellation. Processors may not
        respond immediately to cancellation requests.

        Args:
            execution_id: ID of execution to cancel

        Returns:
            True if execution was found and cancelled
        """
        if execution_id in self._running_executions:
            self._logger.warning("Cancelling execution: %s", execution_id)
            # In a full implementation, we would track and cancel the async task
            return True
        return False

    # Context manager support

    async def __aenter__(self) -> "AIOrchestrator":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup any running executions
        pass

    def __repr__(self) -> str:
        return (
            f"AIOrchestrator(running={len(self._running_executions)}, "
            f"history={len(self._execution_history)})"
        )
