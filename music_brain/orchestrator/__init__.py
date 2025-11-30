"""
AI Orchestrator Module - Central coordination for DAiW Music Brain AI pipelines.

This module provides the foundational architecture for:
- AI pipeline orchestration and execution
- Processing module management
- Workflow logging and monitoring
- Interface layers for external integrations

Phase 1 Infrastructure:
- Pipeline execution with stage management
- Abstract processor interfaces
- Detailed logging for debugging
- Event-driven callbacks

Usage:
    from music_brain.orchestrator import AIOrchestrator, Pipeline

    # Create orchestrator
    orchestrator = AIOrchestrator()

    # Define pipeline
    pipeline = Pipeline("emotion_to_harmony")
    pipeline.add_stage("intent_processing", intent_processor)
    pipeline.add_stage("harmony_generation", harmony_processor)

    # Execute
    result = await orchestrator.execute(pipeline, input_data)
"""

from music_brain.orchestrator.orchestrator import (
    AIOrchestrator,
    OrchestratorConfig,
    ExecutionContext,
    ExecutionResult,
)
from music_brain.orchestrator.pipeline import (
    Pipeline,
    PipelineStage,
    StageResult,
    PipelineStatus,
)
from music_brain.orchestrator.interfaces import (
    ProcessorInterface,
    ProcessorConfig,
    ProcessorResult,
)
from music_brain.orchestrator.logging_utils import (
    OrchestratorLogger,
    LogLevel,
    LogFormatter,
    get_logger,
)

__all__ = [
    # Core Orchestrator
    "AIOrchestrator",
    "OrchestratorConfig",
    "ExecutionContext",
    "ExecutionResult",
    # Pipeline
    "Pipeline",
    "PipelineStage",
    "StageResult",
    "PipelineStatus",
    # Interfaces
    "ProcessorInterface",
    "ProcessorConfig",
    "ProcessorResult",
    # Logging
    "OrchestratorLogger",
    "LogLevel",
    "LogFormatter",
    "get_logger",
]

__version__ = "0.1.0"
__author__ = "DAiW"
