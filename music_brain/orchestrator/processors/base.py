"""
Base Processor for AI Orchestrator.

Provides concrete implementations of ProcessorInterface with
common functionality for music processing pipelines.

Usage:
    from music_brain.orchestrator.processors import BaseProcessor

    class MyProcessor(BaseProcessor):
        async def _process_impl(self, input_data, context):
            # Custom processing logic
            result = do_something(input_data)
            return ProcessorResult(success=True, data=result)
"""

from typing import Any, Dict, Optional
from abc import abstractmethod

from music_brain.orchestrator.interfaces import (
    ProcessorInterface,
    ProcessorConfig,
    ProcessorResult,
    ExecutionContext,
    ProcessorStatus,
)
from music_brain.orchestrator.logging_utils import get_logger, OrchestratorLogger


class BaseProcessor(ProcessorInterface):
    """
    Base class for all processing modules.

    Provides:
    - Logging integration
    - Common validation patterns
    - Error handling helpers
    - Metrics collection

    Subclasses should override:
    - _process_impl: Main processing logic
    - _validate_impl: Input validation (optional)

    Example:
        class MyProcessor(BaseProcessor):
            async def _process_impl(self, input_data, context):
                # Process input_data
                output = transform(input_data)
                return ProcessorResult(success=True, data=output)
    """

    def __init__(self, config: Optional[ProcessorConfig] = None):
        super().__init__(config)
        self._logger: OrchestratorLogger = get_logger(f"processor.{self.name}")
        self._processed_count = 0
        self._error_count = 0

    @abstractmethod
    async def _process_impl(
        self,
        input_data: Any,
        context: ExecutionContext,
    ) -> ProcessorResult:
        """
        Implement main processing logic.

        Args:
            input_data: Input data to process
            context: Execution context

        Returns:
            ProcessorResult with output data
        """
        pass

    async def _validate_impl(self, input_data: Any) -> bool:
        """
        Implement input validation logic.

        Override in subclasses for specific validation.

        Args:
            input_data: Input data to validate

        Returns:
            True if valid
        """
        return True

    async def process(
        self,
        input_data: Any,
        context: ExecutionContext,
    ) -> ProcessorResult:
        """
        Process input data with logging and error handling.

        Args:
            input_data: Input data to process
            context: Execution context

        Returns:
            ProcessorResult with output data or error
        """
        self._status = ProcessorStatus.RUNNING
        self._logger.debug(
            "Processing input: %s",
            type(input_data).__name__,
            stage_name=context.stage_name,
        )

        try:
            result = await self._process_impl(input_data, context)
            self._processed_count += 1

            if result.success:
                self._logger.debug(
                    "Processing successful: %s",
                    type(result.data).__name__,
                    stage_name=context.stage_name,
                )
                self._status = ProcessorStatus.COMPLETED
            else:
                self._logger.warning(
                    "Processing failed: %s",
                    result.error,
                    stage_name=context.stage_name,
                )
                self._error_count += 1
                self._status = ProcessorStatus.FAILED

            self._last_result = result
            return result

        except Exception as e:
            self._error_count += 1
            self._status = ProcessorStatus.FAILED
            self._logger.error(
                "Processing exception: %s",
                str(e),
                stage_name=context.stage_name,
                exc_info=True,
            )
            result = ProcessorResult(
                success=False,
                error=str(e),
                metadata={"exception_type": type(e).__name__},
            )
            self._last_result = result
            return result

    async def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data.

        Args:
            input_data: Input data to validate

        Returns:
            True if valid
        """
        if input_data is None:
            self._logger.warning("Input data is None")
            return False
        return await self._validate_impl(input_data)

    def get_metrics(self) -> Dict[str, Any]:
        """Get processor metrics."""
        return {
            "name": self.name,
            "processed_count": self._processed_count,
            "error_count": self._error_count,
            "success_rate": (
                self._processed_count - self._error_count
            ) / max(self._processed_count, 1),
            "status": self._status.value,
        }

    def reset(self):
        """Reset processor state."""
        super().reset()
        self._processed_count = 0
        self._error_count = 0


class PassthroughProcessor(BaseProcessor):
    """
    A simple processor that passes input through unchanged.

    Useful for testing pipelines or as a placeholder.
    """

    async def _process_impl(
        self,
        input_data: Any,
        context: ExecutionContext,
    ) -> ProcessorResult:
        """Pass input through unchanged."""
        return ProcessorResult(
            success=True,
            data=input_data,
            metadata={"passthrough": True},
        )


class TransformProcessor(BaseProcessor):
    """
    A processor that applies a transformation function.

    Usage:
        processor = TransformProcessor(
            transform_fn=lambda x, ctx: {"processed": x},
            name="my_transform"
        )
    """

    def __init__(
        self,
        transform_fn,
        name: str = "transform",
        config: Optional[ProcessorConfig] = None,
    ):
        config = config or ProcessorConfig(name=name)
        super().__init__(config)
        self._transform_fn = transform_fn

    async def _process_impl(
        self,
        input_data: Any,
        context: ExecutionContext,
    ) -> ProcessorResult:
        """Apply transformation function."""
        try:
            result = self._transform_fn(input_data, context)
            return ProcessorResult(success=True, data=result)
        except Exception as e:
            return ProcessorResult(success=False, error=str(e))
