"""
Intent Processor for AI Orchestrator.

Processes song intent through the three-phase interrogation model
to generate complete musical parameters.

Usage:
    from music_brain.orchestrator.processors import IntentProcessor

    processor = IntentProcessor()
    result = await processor.process(intent_data, context)
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field

from music_brain.orchestrator.processors.base import BaseProcessor
from music_brain.orchestrator.interfaces import (
    ProcessorConfig,
    ProcessorResult,
    ExecutionContext,
)


@dataclass
class IntentInput:
    """
    Input data for intent processing.

    Supports the three-phase intent model:
    - Phase 0: Core wound/desire
    - Phase 1: Emotional intent
    - Phase 2: Technical constraints
    """
    # Phase 0: Core
    core_event: str = ""
    core_resistance: str = ""
    core_longing: str = ""
    core_stakes: str = ""
    core_transformation: str = ""

    # Phase 1: Emotional
    mood_primary: str = ""
    mood_secondary_tension: float = 0.5
    vulnerability_scale: str = "Medium"
    narrative_arc: str = ""
    imagery_texture: str = ""

    # Phase 2: Technical
    technical_genre: str = ""
    technical_key: str = "C"
    technical_mode: str = "major"
    technical_tempo_range: tuple = (80, 120)
    technical_rule_to_break: str = ""
    rule_breaking_justification: str = ""

    # Meta
    title: str = ""
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "phase_0": {
                "core_event": self.core_event,
                "core_resistance": self.core_resistance,
                "core_longing": self.core_longing,
                "core_stakes": self.core_stakes,
                "core_transformation": self.core_transformation,
            },
            "phase_1": {
                "mood_primary": self.mood_primary,
                "mood_secondary_tension": self.mood_secondary_tension,
                "vulnerability_scale": self.vulnerability_scale,
                "narrative_arc": self.narrative_arc,
                "imagery_texture": self.imagery_texture,
            },
            "phase_2": {
                "technical_genre": self.technical_genre,
                "technical_key": self.technical_key,
                "technical_mode": self.technical_mode,
                "technical_tempo_range": list(self.technical_tempo_range),
                "technical_rule_to_break": self.technical_rule_to_break,
                "rule_breaking_justification": self.rule_breaking_justification,
            },
            "title": self.title,
        }


@dataclass
class IntentOutput:
    """Output from intent processing."""
    # Validated intent
    intent: Dict[str, Any]

    # Generated parameters
    suggested_key: str
    suggested_mode: str
    suggested_tempo: int
    suggested_rules: list
    emotional_palette: Dict[str, Any]

    # Validation
    is_valid: bool
    validation_issues: list

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "intent": self.intent,
            "suggested_key": self.suggested_key,
            "suggested_mode": self.suggested_mode,
            "suggested_tempo": self.suggested_tempo,
            "suggested_rules": self.suggested_rules,
            "emotional_palette": self.emotional_palette,
            "is_valid": self.is_valid,
            "validation_issues": self.validation_issues,
        }


class IntentProcessor(BaseProcessor):
    """
    Processor for validating and enhancing song intent.

    This processor:
    - Validates the three-phase intent schema
    - Suggests missing parameters based on emotion
    - Generates emotional-to-musical mappings
    - Provides rule-breaking suggestions

    The output is used by downstream processors (harmony, groove, etc.)
    to generate appropriate musical content.

    Usage:
        processor = IntentProcessor()

        input_data = IntentInput(
            mood_primary="grief",
            core_event="Loss of a relationship",
            technical_key="F",
            technical_mode="major",
        )

        result = await processor.process(input_data, context)
        if result.success:
            print(result.data.suggested_rules)
    """

    def __init__(self, config: Optional[ProcessorConfig] = None):
        config = config or ProcessorConfig(name="intent")
        super().__init__(config)

    async def _validate_impl(self, input_data: Any) -> bool:
        """Validate intent input - very permissive, will fill in gaps."""
        if isinstance(input_data, IntentInput):
            # At minimum need some emotional direction
            return bool(
                input_data.mood_primary
                or input_data.core_longing
                or input_data.core_event
            )
        if isinstance(input_data, dict):
            return bool(
                input_data.get("mood_primary")
                or input_data.get("core_longing")
                or input_data.get("core_event")
                or input_data.get("emotion")
            )
        return False

    async def _process_impl(
        self,
        input_data: Any,
        context: ExecutionContext,
    ) -> ProcessorResult:
        """
        Process and validate intent data.

        Args:
            input_data: IntentInput or dict with intent fields
            context: Execution context

        Returns:
            ProcessorResult with IntentOutput
        """
        try:
            # Parse input
            if isinstance(input_data, dict):
                intent_input = self._parse_dict_to_intent(input_data)
            elif isinstance(input_data, IntentInput):
                intent_input = input_data
            else:
                return ProcessorResult(
                    success=False,
                    error=f"Invalid input type: {type(input_data).__name__}",
                )

            self._logger.debug(
                "Processing intent: %s (mood: %s)",
                intent_input.title or "untitled",
                intent_input.mood_primary,
            )

            # Process intent
            intent_output = await self._process_intent(intent_input)

            # Store in shared context for downstream processors
            context.set_shared("intent", intent_output.to_dict())
            context.set_shared("emotion", intent_input.mood_primary)
            context.set_shared("key", intent_output.suggested_key)
            context.set_shared("mode", intent_output.suggested_mode)
            context.set_shared("tempo", intent_output.suggested_tempo)

            return ProcessorResult(
                success=True,
                data=intent_output,
                metadata={
                    "mood_primary": intent_input.mood_primary,
                    "is_valid": intent_output.is_valid,
                    "issues_count": len(intent_output.validation_issues),
                },
            )

        except Exception as e:
            self._logger.error("Intent processing failed: %s", str(e))
            return ProcessorResult(
                success=False,
                error=f"Intent processing failed: {str(e)}",
            )

    def _parse_dict_to_intent(self, data: Dict[str, Any]) -> IntentInput:
        """Parse dictionary to IntentInput."""
        # Handle flat or nested structure
        phase_0 = data.get("phase_0", data.get("song_root", {}))
        phase_1 = data.get("phase_1", data.get("song_intent", {}))
        phase_2 = data.get("phase_2", data.get("technical_constraints", {}))

        # Extract fields, supporting both nested and flat
        tempo_range = (
            phase_2.get("technical_tempo_range")
            or data.get("technical_tempo_range")
            or (80, 120)
        )
        if isinstance(tempo_range, list):
            tempo_range = tuple(tempo_range)

        return IntentInput(
            # Phase 0
            core_event=phase_0.get("core_event", data.get("core_event", "")),
            core_resistance=phase_0.get("core_resistance", data.get("core_resistance", "")),
            core_longing=phase_0.get("core_longing", data.get("core_longing", "")),
            core_stakes=phase_0.get("core_stakes", data.get("core_stakes", "")),
            core_transformation=phase_0.get(
                "core_transformation", data.get("core_transformation", "")
            ),
            # Phase 1
            mood_primary=phase_1.get(
                "mood_primary",
                data.get("mood_primary", data.get("emotion", "")),
            ),
            mood_secondary_tension=phase_1.get(
                "mood_secondary_tension", data.get("mood_secondary_tension", 0.5)
            ),
            vulnerability_scale=phase_1.get(
                "vulnerability_scale", data.get("vulnerability_scale", "Medium")
            ),
            narrative_arc=phase_1.get("narrative_arc", data.get("narrative_arc", "")),
            imagery_texture=phase_1.get("imagery_texture", data.get("imagery_texture", "")),
            # Phase 2
            technical_genre=phase_2.get("technical_genre", data.get("genre", "")),
            technical_key=phase_2.get("technical_key", data.get("key", "C")),
            technical_mode=phase_2.get("technical_mode", data.get("mode", "major")),
            technical_tempo_range=tempo_range,
            technical_rule_to_break=phase_2.get(
                "technical_rule_to_break", data.get("rule_to_break", "")
            ),
            rule_breaking_justification=phase_2.get(
                "rule_breaking_justification", data.get("rule_justification", "")
            ),
            # Meta
            title=data.get("title", ""),
            params=data.get("params", {}),
        )

    async def _process_intent(self, input_data: IntentInput) -> IntentOutput:
        """
        Process intent using music_brain's intent tools.

        This is the integration point with existing functionality.
        """
        # Lazy imports
        from music_brain.session.intent_schema import (
            validate_intent,
            suggest_rule_break,
            get_affect_mapping,
            CompleteSongIntent,
            SongRoot,
            SongIntent,
            TechnicalConstraints,
        )

        # Build CompleteSongIntent for validation
        complete_intent = CompleteSongIntent(
            title=input_data.title,
            song_root=SongRoot(
                core_event=input_data.core_event,
                core_resistance=input_data.core_resistance,
                core_longing=input_data.core_longing,
                core_stakes=input_data.core_stakes,
                core_transformation=input_data.core_transformation,
            ),
            song_intent=SongIntent(
                mood_primary=input_data.mood_primary,
                mood_secondary_tension=input_data.mood_secondary_tension,
                vulnerability_scale=input_data.vulnerability_scale,
                narrative_arc=input_data.narrative_arc,
                imagery_texture=input_data.imagery_texture,
            ),
            technical_constraints=TechnicalConstraints(
                technical_genre=input_data.technical_genre,
                technical_key=input_data.technical_key,
                technical_mode=input_data.technical_mode,
                technical_tempo_range=input_data.technical_tempo_range,
                technical_rule_to_break=input_data.technical_rule_to_break,
                rule_breaking_justification=input_data.rule_breaking_justification,
            ),
        )

        # Validate
        validation_issues = validate_intent(complete_intent)

        # Get affect mapping for emotional parameters
        affect_mapping = get_affect_mapping(input_data.mood_primary) or {}

        # Suggest key/mode/tempo based on emotion
        suggested_key = input_data.technical_key or "C"
        suggested_mode = input_data.technical_mode or "major"

        if affect_mapping:
            modes = affect_mapping.get("modes", [])
            if modes:
                suggested_mode = modes[0].lower()
            tempo_range = affect_mapping.get("tempo_range", (80, 120))
            suggested_tempo = sum(tempo_range) // 2
        else:
            suggested_tempo = sum(input_data.technical_tempo_range) // 2

        # Suggest rule breaks
        suggested_rules = suggest_rule_break(input_data.mood_primary)

        return IntentOutput(
            intent=input_data.to_dict(),
            suggested_key=suggested_key,
            suggested_mode=suggested_mode,
            suggested_tempo=suggested_tempo,
            suggested_rules=suggested_rules,
            emotional_palette=affect_mapping,
            is_valid=len(validation_issues) == 0,
            validation_issues=validation_issues,
        )
