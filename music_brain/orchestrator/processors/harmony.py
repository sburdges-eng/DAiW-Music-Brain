"""
Harmony Processor for AI Orchestrator.

Processes harmonic intent and generates chord progressions
based on emotional requirements.

Usage:
    from music_brain.orchestrator.processors import HarmonyProcessor

    processor = HarmonyProcessor()
    result = await processor.process(intent_data, context)
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass

from music_brain.orchestrator.processors.base import BaseProcessor
from music_brain.orchestrator.interfaces import (
    ProcessorConfig,
    ProcessorResult,
    ExecutionContext,
)


@dataclass
class HarmonyInput:
    """Input data for harmony processing."""
    emotion: str
    key: str = "C"
    mode: str = "major"
    progression_length: int = 4
    rule_to_break: Optional[str] = None
    params: Dict[str, Any] = None

    def __post_init__(self):
        if self.params is None:
            self.params = {}


@dataclass
class HarmonyOutput:
    """Output from harmony processing."""
    chords: List[str]
    roman_numerals: List[str]
    key: str
    mode: str
    rule_broken: Optional[str]
    emotional_arc: List[str]
    voice_leading_notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chords": self.chords,
            "roman_numerals": self.roman_numerals,
            "key": self.key,
            "mode": self.mode,
            "rule_broken": self.rule_broken,
            "emotional_arc": self.emotional_arc,
            "voice_leading_notes": self.voice_leading_notes,
        }


class HarmonyProcessor(BaseProcessor):
    """
    Processor for generating harmonic content based on emotional intent.

    This processor integrates with the existing harmony generation
    functionality in music_brain.session.intent_processor.

    Features:
    - Generate chord progressions from emotion
    - Apply rule-breaking for emotional effect
    - Consider modal interchange and borrowed chords
    - Provide voice leading suggestions

    Usage:
        processor = HarmonyProcessor()

        input_data = HarmonyInput(
            emotion="grief",
            key="F",
            mode="major",
            rule_to_break="HARMONY_ModalInterchange"
        )

        result = await processor.process(input_data, context)
        if result.success:
            print(result.data.chords)  # ['F', 'C', 'Dm', 'Bbm']
    """

    def __init__(self, config: Optional[ProcessorConfig] = None):
        config = config or ProcessorConfig(name="harmony")
        super().__init__(config)

    async def _validate_impl(self, input_data: Any) -> bool:
        """Validate harmony input."""
        if isinstance(input_data, HarmonyInput):
            return bool(input_data.emotion)
        if isinstance(input_data, dict):
            return "emotion" in input_data
        # Accept IntentOutput from previous stage - we'll get emotion from context
        if hasattr(input_data, 'intent'):
            return True
        return False

    async def _process_impl(
        self,
        input_data: Any,
        context: ExecutionContext,
    ) -> ProcessorResult:
        """
        Generate harmonic content based on input.

        Args:
            input_data: HarmonyInput or dict with emotion/key/mode
            context: Execution context

        Returns:
            ProcessorResult with HarmonyOutput
        """
        try:
            # Parse input - support multiple input formats
            if isinstance(input_data, dict):
                harmony_input = HarmonyInput(
                    emotion=input_data.get("emotion", "neutral"),
                    key=input_data.get("key", "C"),
                    mode=input_data.get("mode", "major"),
                    progression_length=input_data.get("progression_length", 4),
                    rule_to_break=input_data.get("rule_to_break"),
                    params=input_data.get("params", {}),
                )
            elif isinstance(input_data, HarmonyInput):
                harmony_input = input_data
            elif hasattr(input_data, 'intent'):
                # Input is from IntentProcessor - get params from context
                harmony_input = HarmonyInput(
                    emotion=context.get_shared("emotion", "neutral"),
                    key=context.get_shared("key", "C"),
                    mode=context.get_shared("mode", "major"),
                    rule_to_break=input_data.intent.get("phase_2", {}).get(
                        "technical_rule_to_break"
                    ),
                )
            else:
                return ProcessorResult(
                    success=False,
                    error=f"Invalid input type: {type(input_data).__name__}",
                )

            self._logger.debug(
                "Generating harmony for emotion: %s in %s %s",
                harmony_input.emotion,
                harmony_input.key,
                harmony_input.mode,
            )

            # Generate harmony using existing functionality
            harmony_output = await self._generate_harmony(harmony_input)

            # Store in shared context for other processors
            context.set_shared("harmony", harmony_output.to_dict())

            return ProcessorResult(
                success=True,
                data=harmony_output,
                metadata={
                    "emotion": harmony_input.emotion,
                    "key": harmony_input.key,
                    "mode": harmony_input.mode,
                    "rule_broken": harmony_output.rule_broken,
                },
            )

        except Exception as e:
            self._logger.error("Harmony generation failed: %s", str(e))
            return ProcessorResult(
                success=False,
                error=f"Harmony generation failed: {str(e)}",
            )

    async def _generate_harmony(self, input_data: HarmonyInput) -> HarmonyOutput:
        """
        Generate harmony using music_brain's harmony tools.

        This is the integration point with existing functionality.
        """
        # Lazy import to avoid circular dependencies
        from music_brain.session.intent_processor import (
            generate_progression_modal_interchange,
            generate_progression_avoid_tonic,
            generate_progression_parallel_motion,
            generate_progression_unresolved_dissonance,
        )

        rule = input_data.rule_to_break

        # Select generator based on rule
        if rule == "HARMONY_ModalInterchange":
            prog = generate_progression_modal_interchange(
                input_data.key, input_data.mode
            )
        elif rule == "HARMONY_AvoidTonicResolution":
            prog = generate_progression_avoid_tonic(
                input_data.key, input_data.mode
            )
        elif rule == "HARMONY_ParallelMotion":
            prog = generate_progression_parallel_motion(
                input_data.key, input_data.mode
            )
        elif rule == "HARMONY_UnresolvedDissonance":
            prog = generate_progression_unresolved_dissonance(
                input_data.key, input_data.mode
            )
        else:
            # Default based on emotion
            emotion = input_data.emotion.lower()
            if emotion in ("grief", "longing", "nostalgia"):
                prog = generate_progression_modal_interchange(
                    input_data.key, input_data.mode
                )
            elif emotion in ("defiance", "anger", "rage"):
                prog = generate_progression_parallel_motion(
                    input_data.key, input_data.mode
                )
            else:
                prog = generate_progression_modal_interchange(
                    input_data.key, input_data.mode
                )

        return HarmonyOutput(
            chords=prog.chords,
            roman_numerals=prog.roman_numerals,
            key=prog.key,
            mode=prog.mode,
            rule_broken=prog.rule_broken,
            emotional_arc=prog.emotional_arc,
            voice_leading_notes=prog.voice_leading_notes,
        )
