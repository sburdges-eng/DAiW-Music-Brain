"""
Pipeline Module for AI Orchestrator.

Provides pipeline definition, stage management, and execution flow.

A Pipeline consists of multiple stages, each containing a processor.
Stages are executed sequentially, with each stage receiving the output
of the previous stage.

Usage:
    from music_brain.orchestrator import Pipeline, PipelineStage

    # Create pipeline
    pipeline = Pipeline("emotion_to_music")

    # Add stages
    pipeline.add_stage("intent", intent_processor)
    pipeline.add_stage("harmony", harmony_processor)
    pipeline.add_stage("groove", groove_processor)

    # Execute via orchestrator
    result = await orchestrator.execute(pipeline, input_data)
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

from music_brain.orchestrator.interfaces import (
    ProcessorInterface,
    ProcessorResult,
    ProcessorConfig,
    ExecutionContext,
)


class PipelineStatus(Enum):
    """Status of a pipeline execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StageResult:
    """
    Result from a single pipeline stage.

    Attributes:
        stage_name: Name of the stage
        processor_result: Result from the processor
        started_at: Stage start time
        completed_at: Stage completion time
        duration_ms: Stage execution time in milliseconds
    """
    stage_name: str
    processor_result: ProcessorResult
    started_at: str = ""
    completed_at: str = ""
    duration_ms: float = 0.0

    @property
    def success(self) -> bool:
        """Check if stage completed successfully."""
        return self.processor_result.success

    @property
    def data(self) -> Any:
        """Get stage output data."""
        return self.processor_result.data

    @property
    def error(self) -> Optional[str]:
        """Get stage error message."""
        return self.processor_result.error

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stage_name": self.stage_name,
            "processor_result": self.processor_result.to_dict(),
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
        }


@dataclass
class PipelineStage:
    """
    A single stage in a pipeline.

    Attributes:
        name: Stage name (unique within pipeline)
        processor: Processor to execute in this stage
        config: Stage configuration
        condition: Optional condition function to skip stage
        transform_input: Optional function to transform input before processing
        transform_output: Optional function to transform output after processing
    """
    name: str
    processor: ProcessorInterface
    config: ProcessorConfig = field(default_factory=lambda: ProcessorConfig(name=""))
    condition: Optional[Callable[[ExecutionContext], bool]] = None
    transform_input: Optional[Callable[[Any, ExecutionContext], Any]] = None
    transform_output: Optional[Callable[[ProcessorResult, ExecutionContext], ProcessorResult]] = None

    def __post_init__(self):
        if not self.config.name:
            self.config = ProcessorConfig(name=self.name)

    def should_execute(self, context: ExecutionContext) -> bool:
        """Check if this stage should execute based on condition."""
        if self.condition is None:
            return True
        return self.condition(context)


@dataclass
class PipelineDefinition:
    """
    Complete pipeline definition.

    Attributes:
        id: Unique pipeline identifier
        name: Human-readable pipeline name
        description: Pipeline description
        stages: Ordered list of stages
        created_at: Creation timestamp
        metadata: Pipeline metadata
    """
    id: str
    name: str
    description: str = ""
    stages: List[PipelineStage] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def stage_names(self) -> List[str]:
        """Get list of stage names in order."""
        return [stage.name for stage in self.stages]

    def get_stage(self, name: str) -> Optional[PipelineStage]:
        """Get stage by name."""
        for stage in self.stages:
            if stage.name == name:
                return stage
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "stages": [
                {
                    "name": stage.name,
                    "processor": stage.processor.__class__.__name__,
                    "config": stage.config.to_dict(),
                }
                for stage in self.stages
            ],
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


class Pipeline:
    """
    Pipeline for orchestrating processing stages.

    A Pipeline defines a sequence of processing stages that transform
    input data through multiple processors.

    Usage:
        pipeline = Pipeline("emotion_to_music", "Generate music from emotion")

        # Add stages
        pipeline.add_stage("parse_emotion", emotion_parser)
        pipeline.add_stage("generate_harmony", harmony_generator)
        pipeline.add_stage("apply_groove", groove_applicator)

        # Add conditional stage
        pipeline.add_stage(
            "vocal_processing",
            vocal_processor,
            condition=lambda ctx: ctx.get_shared("has_vocals", False)
        )
    """

    def __init__(self, name: str, description: str = ""):
        self._definition = PipelineDefinition(
            id=f"pipeline_{uuid.uuid4().hex[:12]}",
            name=name,
            description=description,
        )
        self._status = PipelineStatus.PENDING

    @property
    def id(self) -> str:
        """Get pipeline ID."""
        return self._definition.id

    @property
    def name(self) -> str:
        """Get pipeline name."""
        return self._definition.name

    @property
    def description(self) -> str:
        """Get pipeline description."""
        return self._definition.description

    @property
    def stages(self) -> List[PipelineStage]:
        """Get pipeline stages."""
        return self._definition.stages

    @property
    def stage_names(self) -> List[str]:
        """Get list of stage names."""
        return self._definition.stage_names

    @property
    def status(self) -> PipelineStatus:
        """Get pipeline status."""
        return self._status

    @property
    def definition(self) -> PipelineDefinition:
        """Get pipeline definition."""
        return self._definition

    def add_stage(
        self,
        name: str,
        processor: ProcessorInterface,
        config: Optional[ProcessorConfig] = None,
        condition: Optional[Callable[[ExecutionContext], bool]] = None,
        transform_input: Optional[Callable[[Any, ExecutionContext], Any]] = None,
        transform_output: Optional[Callable[
            [ProcessorResult, ExecutionContext], ProcessorResult
        ]] = None,
    ) -> "Pipeline":
        """
        Add a processing stage to the pipeline.

        Args:
            name: Stage name (must be unique)
            processor: Processor to execute
            config: Optional stage configuration
            condition: Optional condition to skip stage
            transform_input: Optional input transformer
            transform_output: Optional output transformer

        Returns:
            Self for chaining
        """
        # Check for duplicate names
        if name in self.stage_names:
            raise ValueError(f"Stage with name '{name}' already exists")

        stage = PipelineStage(
            name=name,
            processor=processor,
            config=config or ProcessorConfig(name=name),
            condition=condition,
            transform_input=transform_input,
            transform_output=transform_output,
        )
        self._definition.stages.append(stage)
        return self

    def remove_stage(self, name: str) -> bool:
        """
        Remove a stage from the pipeline.

        Args:
            name: Stage name to remove

        Returns:
            True if stage was removed
        """
        for i, stage in enumerate(self._definition.stages):
            if stage.name == name:
                self._definition.stages.pop(i)
                return True
        return False

    def get_stage(self, name: str) -> Optional[PipelineStage]:
        """Get a stage by name."""
        return self._definition.get_stage(name)

    def insert_stage(
        self,
        index: int,
        name: str,
        processor: ProcessorInterface,
        config: Optional[ProcessorConfig] = None,
    ) -> "Pipeline":
        """
        Insert a stage at a specific position.

        Args:
            index: Position to insert at
            name: Stage name
            processor: Processor to execute
            config: Optional stage configuration

        Returns:
            Self for chaining
        """
        if name in self.stage_names:
            raise ValueError(f"Stage with name '{name}' already exists")

        stage = PipelineStage(
            name=name,
            processor=processor,
            config=config or ProcessorConfig(name=name),
        )
        self._definition.stages.insert(index, stage)
        return self

    def set_metadata(self, key: str, value: Any) -> "Pipeline":
        """Set pipeline metadata."""
        self._definition.metadata[key] = value
        return self

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get pipeline metadata."""
        return self._definition.metadata.get(key, default)

    def reset(self):
        """Reset pipeline status for reuse."""
        self._status = PipelineStatus.PENDING
        for stage in self.stages:
            stage.processor.reset()

    def validate(self) -> List[str]:
        """
        Validate pipeline configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not self.stages:
            errors.append("Pipeline has no stages")

        # Check for duplicate stage names
        names = set()
        for stage in self.stages:
            if stage.name in names:
                errors.append(f"Duplicate stage name: {stage.name}")
            names.add(stage.name)

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert pipeline to dictionary."""
        return self._definition.to_dict()

    def __repr__(self) -> str:
        return f"Pipeline(name='{self.name}', stages={len(self.stages)})"

    def __len__(self) -> int:
        return len(self.stages)

    def __iter__(self):
        return iter(self.stages)


class PipelineBuilder:
    """
    Builder for creating pipelines with a fluent interface.

    Usage:
        pipeline = (PipelineBuilder("my_pipeline")
            .description("Process emotional intent")
            .stage("parse", parser)
            .stage("generate", generator)
            .conditional_stage("enhance", enhancer, lambda ctx: ctx.get_shared("enhance"))
            .metadata("version", "1.0")
            .build())
    """

    def __init__(self, name: str):
        self._name = name
        self._description = ""
        self._stages: List[Dict[str, Any]] = []
        self._metadata: Dict[str, Any] = {}

    def description(self, desc: str) -> "PipelineBuilder":
        """Set pipeline description."""
        self._description = desc
        return self

    def stage(
        self,
        name: str,
        processor: ProcessorInterface,
        config: Optional[ProcessorConfig] = None,
    ) -> "PipelineBuilder":
        """Add a stage."""
        self._stages.append({
            "name": name,
            "processor": processor,
            "config": config,
            "condition": None,
        })
        return self

    def conditional_stage(
        self,
        name: str,
        processor: ProcessorInterface,
        condition: Callable[[ExecutionContext], bool],
        config: Optional[ProcessorConfig] = None,
    ) -> "PipelineBuilder":
        """Add a conditional stage."""
        self._stages.append({
            "name": name,
            "processor": processor,
            "config": config,
            "condition": condition,
        })
        return self

    def metadata(self, key: str, value: Any) -> "PipelineBuilder":
        """Set metadata."""
        self._metadata[key] = value
        return self

    def build(self) -> Pipeline:
        """Build the pipeline."""
        pipeline = Pipeline(self._name, self._description)

        for stage_def in self._stages:
            pipeline.add_stage(
                name=stage_def["name"],
                processor=stage_def["processor"],
                config=stage_def["config"],
                condition=stage_def["condition"],
            )

        for key, value in self._metadata.items():
            pipeline.set_metadata(key, value)

        return pipeline
