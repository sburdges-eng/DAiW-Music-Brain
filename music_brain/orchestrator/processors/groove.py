"""
Groove Processor for AI Orchestrator.

Processes groove patterns and applies timing/velocity
modifications based on emotional intent.

Usage:
    from music_brain.orchestrator.processors import GrooveProcessor

    processor = GrooveProcessor()
    result = await processor.process(groove_input, context)
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field

from music_brain.orchestrator.processors.base import BaseProcessor
from music_brain.orchestrator.interfaces import (
    ProcessorConfig,
    ProcessorResult,
    ExecutionContext,
)


@dataclass
class GrooveInput:
    """Input data for groove processing."""
    tempo: int = 120
    genre: str = "straight"
    emotion: str = "neutral"
    rule_to_break: Optional[str] = None
    swing_factor: float = 0.0
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GrooveOutput:
    """Output from groove processing."""
    pattern_name: str
    tempo_bpm: int
    swing_factor: float
    timing_offsets_16th: List[float]
    velocity_curve: List[int]
    rule_broken: Optional[str]
    rule_effect: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pattern_name": self.pattern_name,
            "tempo_bpm": self.tempo_bpm,
            "swing_factor": self.swing_factor,
            "timing_offsets_16th": self.timing_offsets_16th,
            "velocity_curve": self.velocity_curve,
            "rule_broken": self.rule_broken,
            "rule_effect": self.rule_effect,
        }


class GrooveProcessor(BaseProcessor):
    """
    Processor for generating and applying groove patterns.

    This processor integrates with the existing groove functionality
    in music_brain.groove and music_brain.session.intent_processor.

    Features:
    - Generate groove patterns from emotion/genre
    - Apply timing offsets for feel
    - Create velocity curves for dynamics
    - Support rule-breaking for emotional effect

    Usage:
        processor = GrooveProcessor()

        input_data = GrooveInput(
            tempo=90,
            genre="funk",
            emotion="grief",
            rule_to_break="RHYTHM_ConstantDisplacement"
        )

        result = await processor.process(input_data, context)
        if result.success:
            print(result.data.timing_offsets_16th)
    """

    def __init__(self, config: Optional[ProcessorConfig] = None):
        config = config or ProcessorConfig(name="groove")
        super().__init__(config)

    async def _validate_impl(self, input_data: Any) -> bool:
        """Validate groove input."""
        if isinstance(input_data, GrooveInput):
            return input_data.tempo > 0
        if isinstance(input_data, dict):
            return input_data.get("tempo", 120) > 0
        # Accept HarmonyOutput from previous stage - we'll get params from context
        if hasattr(input_data, 'chords'):
            return True
        return False

    async def _process_impl(
        self,
        input_data: Any,
        context: ExecutionContext,
    ) -> ProcessorResult:
        """
        Generate groove pattern based on input.

        Args:
            input_data: GrooveInput or dict with tempo/genre/emotion
            context: Execution context

        Returns:
            ProcessorResult with GrooveOutput
        """
        try:
            # Parse input - support multiple input formats
            if isinstance(input_data, dict):
                groove_input = GrooveInput(
                    tempo=input_data.get("tempo", 120),
                    genre=input_data.get("genre", "straight"),
                    emotion=input_data.get("emotion", "neutral"),
                    rule_to_break=input_data.get("rule_to_break"),
                    swing_factor=input_data.get("swing_factor", 0.0),
                    params=input_data.get("params", {}),
                )
            elif isinstance(input_data, GrooveInput):
                groove_input = input_data
            elif hasattr(input_data, 'chords'):
                # Input is from HarmonyProcessor - get params from context
                groove_input = GrooveInput(
                    tempo=context.get_shared("tempo", 120),
                    genre=context.get_shared("genre", "straight"),
                    emotion=context.get_shared("emotion", "neutral"),
                )
            else:
                return ProcessorResult(
                    success=False,
                    error=f"Invalid input type: {type(input_data).__name__}",
                )

            self._logger.debug(
                "Generating groove for %s at %d BPM",
                groove_input.genre,
                groove_input.tempo,
            )

            # Generate groove
            groove_output = await self._generate_groove(groove_input)

            # Store in shared context
            context.set_shared("groove", groove_output.to_dict())

            return ProcessorResult(
                success=True,
                data=groove_output,
                metadata={
                    "tempo": groove_input.tempo,
                    "genre": groove_input.genre,
                    "rule_broken": groove_output.rule_broken,
                },
            )

        except Exception as e:
            self._logger.error("Groove generation failed: %s", str(e))
            return ProcessorResult(
                success=False,
                error=f"Groove generation failed: {str(e)}",
            )

    async def _generate_groove(self, input_data: GrooveInput) -> GrooveOutput:
        """
        Generate groove using music_brain's groove tools.

        This is the integration point with existing functionality.
        """
        # Lazy import to avoid circular dependencies
        from music_brain.session.intent_processor import (
            generate_groove_constant_displacement,
            generate_groove_tempo_fluctuation,
            generate_groove_metric_modulation,
            generate_groove_dropped_beats,
        )

        rule = input_data.rule_to_break

        # Select generator based on rule
        if rule == "RHYTHM_ConstantDisplacement":
            groove = generate_groove_constant_displacement(input_data.tempo)
        elif rule == "RHYTHM_TempoFluctuation":
            groove = generate_groove_tempo_fluctuation(input_data.tempo)
        elif rule == "RHYTHM_MetricModulation":
            groove = generate_groove_metric_modulation(input_data.tempo)
        elif rule == "RHYTHM_DroppedBeats":
            groove = generate_groove_dropped_beats(input_data.tempo)
        else:
            # Default based on emotion
            emotion = input_data.emotion.lower()
            if emotion in ("anxiety", "tension", "unease"):
                groove = generate_groove_constant_displacement(input_data.tempo)
            elif emotion in ("intimacy", "vulnerability", "organic"):
                groove = generate_groove_tempo_fluctuation(input_data.tempo)
            else:
                groove = generate_groove_tempo_fluctuation(input_data.tempo)

        return GrooveOutput(
            pattern_name=groove.pattern_name,
            tempo_bpm=groove.tempo_bpm,
            swing_factor=groove.swing_factor,
            timing_offsets_16th=groove.timing_offsets_16th,
            velocity_curve=groove.velocity_curve,
            rule_broken=groove.rule_broken,
            rule_effect=groove.rule_effect,
        )
