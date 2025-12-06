"""
Multi-AI Intent-to-Code Pipeline

4-stage AI pipeline that transforms emotional intent into working code:
1. Claude: Intent Analysis
2. Gemini: Research & Options
3. ChatGPT: Implementation Plan
4. Copilot: Code Generation

Proposal: Claude - Multi-AI Intent-to-Code Pipeline
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime
import json


class PipelineStage(str, Enum):
    """Stages of the intent-to-code pipeline."""
    INTENT_ANALYSIS = "intent_analysis"       # Claude
    RESEARCH = "research"                      # Gemini
    IMPLEMENTATION_PLAN = "implementation"     # ChatGPT
    CODE_GENERATION = "code_generation"        # Copilot


class AIRole(str, Enum):
    """AI roles in the pipeline."""
    CLAUDE = "claude"
    GEMINI = "gemini"
    CHATGPT = "chatgpt"
    COPILOT = "copilot"


# Stage to AI mapping
STAGE_AI_MAP = {
    PipelineStage.INTENT_ANALYSIS: AIRole.CLAUDE,
    PipelineStage.RESEARCH: AIRole.GEMINI,
    PipelineStage.IMPLEMENTATION_PLAN: AIRole.CHATGPT,
    PipelineStage.CODE_GENERATION: AIRole.COPILOT,
}


@dataclass
class IntentAnalysisResult:
    """Output from Stage 1: Intent Analysis (Claude)."""
    # Extracted intent
    core_emotion: str
    secondary_emotions: List[str]
    narrative_arc: str
    vulnerability_level: str

    # Rule-breaking analysis
    rule_breaks_justified: List[Dict[str, str]]  # [{rule, justification}]
    rule_breaks_unjustified: List[str]  # Rules suggested without justification

    # Technical implications
    suggested_key: Optional[str] = None
    suggested_mode: Optional[str] = None
    suggested_tempo_range: Optional[tuple] = None

    # Confidence and notes
    confidence: float = 0.0
    analysis_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "core_emotion": self.core_emotion,
            "secondary_emotions": self.secondary_emotions,
            "narrative_arc": self.narrative_arc,
            "vulnerability_level": self.vulnerability_level,
            "rule_breaks_justified": self.rule_breaks_justified,
            "rule_breaks_unjustified": self.rule_breaks_unjustified,
            "suggested_key": self.suggested_key,
            "suggested_mode": self.suggested_mode,
            "suggested_tempo_range": self.suggested_tempo_range,
            "confidence": self.confidence,
            "analysis_notes": self.analysis_notes,
        }


@dataclass
class ResearchResult:
    """Output from Stage 2: Research & Options (Gemini)."""
    # Reference tracks
    reference_tracks: List[Dict[str, str]]  # [{title, artist, why_relevant}]

    # Technical options
    progression_options: List[Dict[str, Any]]  # Chord progressions with tradeoffs
    groove_options: List[Dict[str, Any]]       # Genre templates with tradeoffs
    production_options: List[Dict[str, Any]]   # Production techniques

    # Research findings
    similar_implementations: List[str]
    potential_challenges: List[str]
    recommended_approach: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference_tracks": self.reference_tracks,
            "progression_options": self.progression_options,
            "groove_options": self.groove_options,
            "production_options": self.production_options,
            "similar_implementations": self.similar_implementations,
            "potential_challenges": self.potential_challenges,
            "recommended_approach": self.recommended_approach,
        }


@dataclass
class ImplementationPlan:
    """Output from Stage 3: Implementation Plan (ChatGPT)."""
    # High-level steps
    phases: List[Dict[str, Any]]  # [{name, description, tasks}]

    # Detailed tasks
    tasks: List[Dict[str, Any]]  # [{id, description, dependencies, estimated_complexity}]

    # Test cases
    test_cases: List[Dict[str, str]]  # [{description, expected_outcome}]

    # Risk mitigation
    risks: List[Dict[str, str]]  # [{risk, mitigation}]

    # Timeline estimate
    estimated_complexity: str  # low, medium, high, very_high

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phases": self.phases,
            "tasks": self.tasks,
            "test_cases": self.test_cases,
            "risks": self.risks,
            "estimated_complexity": self.estimated_complexity,
        }


@dataclass
class CodeGenerationResult:
    """Output from Stage 4: Code Generation (Copilot)."""
    # Generated code
    files: Dict[str, str]  # {filename: content}

    # Code metadata
    entry_point: str
    dependencies: List[str]

    # Tests
    test_files: Dict[str, str]  # {test_filename: content}

    # Documentation
    usage_example: str
    api_documentation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "files": self.files,
            "entry_point": self.entry_point,
            "dependencies": self.dependencies,
            "test_files": self.test_files,
            "usage_example": self.usage_example,
            "api_documentation": self.api_documentation,
        }


@dataclass
class PipelineState:
    """Complete state of a pipeline execution."""
    id: str
    created_at: str

    # Input
    raw_intent: Dict[str, Any]

    # Stage results
    intent_analysis: Optional[IntentAnalysisResult] = None
    research: Optional[ResearchResult] = None
    implementation_plan: Optional[ImplementationPlan] = None
    code_generation: Optional[CodeGenerationResult] = None

    # Progress
    current_stage: PipelineStage = PipelineStage.INTENT_ANALYSIS
    completed_stages: List[PipelineStage] = field(default_factory=list)
    failed_stage: Optional[PipelineStage] = None
    error_message: Optional[str] = None

    def is_complete(self) -> bool:
        return len(self.completed_stages) == 4

    def progress_percent(self) -> float:
        return len(self.completed_stages) / 4 * 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "raw_intent": self.raw_intent,
            "intent_analysis": self.intent_analysis.to_dict() if self.intent_analysis else None,
            "research": self.research.to_dict() if self.research else None,
            "implementation_plan": self.implementation_plan.to_dict() if self.implementation_plan else None,
            "code_generation": self.code_generation.to_dict() if self.code_generation else None,
            "current_stage": self.current_stage.value,
            "completed_stages": [s.value for s in self.completed_stages],
            "failed_stage": self.failed_stage.value if self.failed_stage else None,
            "error_message": self.error_message,
        }


class IntentToCodePipeline:
    """
    Orchestrates the 4-stage AI pipeline.

    Each stage can be executed by different AI models or run locally.
    """

    def __init__(self):
        self.states: Dict[str, PipelineState] = {}
        self._stage_handlers: Dict[PipelineStage, Callable] = {}

        # Register default handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default stage handlers (local implementations)."""
        self._stage_handlers[PipelineStage.INTENT_ANALYSIS] = self._analyze_intent_local
        self._stage_handlers[PipelineStage.RESEARCH] = self._research_local
        self._stage_handlers[PipelineStage.IMPLEMENTATION_PLAN] = self._plan_local
        self._stage_handlers[PipelineStage.CODE_GENERATION] = self._generate_code_local

    def register_handler(self, stage: PipelineStage, handler: Callable):
        """Register a custom handler for a stage (e.g., API call to AI)."""
        self._stage_handlers[stage] = handler

    def create_pipeline(self, intent: Dict[str, Any]) -> str:
        """
        Create a new pipeline from intent.

        Args:
            intent: Song intent dictionary (from intent schema)

        Returns:
            Pipeline ID
        """
        import uuid

        pipeline_id = str(uuid.uuid4())[:8]
        state = PipelineState(
            id=pipeline_id,
            created_at=datetime.now().isoformat(),
            raw_intent=intent,
        )
        self.states[pipeline_id] = state

        return pipeline_id

    def execute_stage(self, pipeline_id: str, stage: PipelineStage) -> bool:
        """
        Execute a single stage of the pipeline.

        Args:
            pipeline_id: Pipeline to execute
            stage: Stage to execute

        Returns:
            True if successful
        """
        state = self.states.get(pipeline_id)
        if not state:
            return False

        handler = self._stage_handlers.get(stage)
        if not handler:
            state.error_message = f"No handler for stage: {stage.value}"
            state.failed_stage = stage
            return False

        try:
            state.current_stage = stage
            result = handler(state)

            # Store result
            if stage == PipelineStage.INTENT_ANALYSIS:
                state.intent_analysis = result
            elif stage == PipelineStage.RESEARCH:
                state.research = result
            elif stage == PipelineStage.IMPLEMENTATION_PLAN:
                state.implementation_plan = result
            elif stage == PipelineStage.CODE_GENERATION:
                state.code_generation = result

            state.completed_stages.append(stage)
            return True

        except Exception as e:
            state.error_message = str(e)
            state.failed_stage = stage
            return False

    def execute_all(self, pipeline_id: str) -> bool:
        """Execute all stages in sequence."""
        stages = [
            PipelineStage.INTENT_ANALYSIS,
            PipelineStage.RESEARCH,
            PipelineStage.IMPLEMENTATION_PLAN,
            PipelineStage.CODE_GENERATION,
        ]

        for stage in stages:
            if not self.execute_stage(pipeline_id, stage):
                return False

        return True

    def get_state(self, pipeline_id: str) -> Optional[PipelineState]:
        """Get pipeline state."""
        return self.states.get(pipeline_id)

    # =========================================================================
    # Default Local Handlers
    # =========================================================================

    def _analyze_intent_local(self, state: PipelineState) -> IntentAnalysisResult:
        """Local intent analysis (Claude's role)."""
        intent = state.raw_intent

        # Extract from Phase 0 (root)
        root = intent.get("root", {})
        core_emotion = root.get("core_event", "unknown")

        # Extract from Phase 1 (intent)
        phase1 = intent.get("intent", {})
        mood = phase1.get("mood_primary", "neutral")
        vulnerability = phase1.get("vulnerability_scale", "medium")
        arc = phase1.get("narrative_arc", "linear")

        # Extract from Phase 2 (technical)
        phase2 = intent.get("technical", {})
        rule_break = phase2.get("rule_to_break")
        justification = phase2.get("rule_breaking_justification", "")

        # Build result
        result = IntentAnalysisResult(
            core_emotion=core_emotion,
            secondary_emotions=[mood] if mood != core_emotion else [],
            narrative_arc=arc,
            vulnerability_level=vulnerability,
            rule_breaks_justified=[
                {"rule": rule_break, "justification": justification}
            ] if rule_break and justification else [],
            rule_breaks_unjustified=[rule_break] if rule_break and not justification else [],
            suggested_key=phase2.get("key"),
            suggested_mode=phase2.get("mode"),
            confidence=0.8 if justification else 0.5,
            analysis_notes="Local analysis - for full analysis, use Claude API",
        )

        return result

    def _research_local(self, state: PipelineState) -> ResearchResult:
        """Local research (Gemini's role)."""
        analysis = state.intent_analysis

        # Suggest based on emotion
        emotion_progressions = {
            "grief": [
                {"name": "i - VI - III - VII", "emotion": "melancholic", "tradeoff": "Common but effective"},
            ],
            "anger": [
                {"name": "i - VII - VI - VII", "emotion": "driving", "tradeoff": "Can feel aggressive"},
            ],
            "joy": [
                {"name": "I - V - vi - IV", "emotion": "uplifting", "tradeoff": "Very common"},
            ],
        }

        core = analysis.core_emotion.lower() if analysis else "neutral"
        progressions = emotion_progressions.get(core, [
            {"name": "I - IV - V - I", "emotion": "neutral", "tradeoff": "Safe choice"},
        ])

        return ResearchResult(
            reference_tracks=[
                {"title": "Example Track", "artist": "Example Artist", "why_relevant": "Similar emotional content"},
            ],
            progression_options=progressions,
            groove_options=[
                {"name": "straight_8ths", "feel": "neutral", "tradeoff": "Safe but may lack groove"},
            ],
            production_options=[
                {"technique": "room_reverb", "effect": "space", "tradeoff": "Can muddy the mix"},
            ],
            similar_implementations=["Check existing groove templates"],
            potential_challenges=["Balancing emotion with technical execution"],
            recommended_approach="Start with the chord progression, then add groove",
        )

    def _plan_local(self, state: PipelineState) -> ImplementationPlan:
        """Local implementation planning (ChatGPT's role)."""
        research = state.research

        return ImplementationPlan(
            phases=[
                {
                    "name": "Foundation",
                    "description": "Set up harmonic and rhythmic foundation",
                    "tasks": ["task_1", "task_2"],
                },
                {
                    "name": "Development",
                    "description": "Add arrangement and production elements",
                    "tasks": ["task_3", "task_4"],
                },
                {
                    "name": "Polish",
                    "description": "Fine-tune and test",
                    "tasks": ["task_5"],
                },
            ],
            tasks=[
                {"id": "task_1", "description": "Create chord progression", "dependencies": [], "complexity": "low"},
                {"id": "task_2", "description": "Apply groove template", "dependencies": ["task_1"], "complexity": "low"},
                {"id": "task_3", "description": "Add rule-breaking elements", "dependencies": ["task_2"], "complexity": "medium"},
                {"id": "task_4", "description": "Production processing", "dependencies": ["task_3"], "complexity": "medium"},
                {"id": "task_5", "description": "Test and iterate", "dependencies": ["task_4"], "complexity": "low"},
            ],
            test_cases=[
                {"description": "Emotional impact test", "expected_outcome": "Evokes intended emotion"},
                {"description": "Technical validity test", "expected_outcome": "No unintended dissonance"},
            ],
            risks=[
                {"risk": "Rule-breaking goes too far", "mitigation": "A/B test with and without"},
            ],
            estimated_complexity="medium",
        )

    def _generate_code_local(self, state: PipelineState) -> CodeGenerationResult:
        """Local code generation (Copilot's role)."""
        plan = state.implementation_plan
        analysis = state.intent_analysis

        # Generate simple code based on analysis
        code = f'''"""
Generated from Intent Pipeline
Emotion: {analysis.core_emotion if analysis else 'unknown'}
"""

from music_brain.structure.chord import ChordProgression
from music_brain.groove.templates import get_template

# Create progression
progression = ChordProgression.from_string("Am - F - C - G")

# Apply groove
groove = get_template("pop_ballad")

# Output
print(f"Progression: {{progression}}")
print(f"Groove: {{groove.name}}")
'''

        test_code = '''"""Tests for generated code."""
import pytest

def test_progression_exists():
    """Test that progression was created."""
    assert True  # Placeholder

def test_groove_applied():
    """Test that groove was applied."""
    assert True  # Placeholder
'''

        return CodeGenerationResult(
            files={"generated_song.py": code},
            entry_point="generated_song.py",
            dependencies=["music_brain"],
            test_files={"test_generated.py": test_code},
            usage_example="python generated_song.py",
            api_documentation="See inline comments in generated code.",
        )

    # =========================================================================
    # Visualization
    # =========================================================================

    def format_progress(self, pipeline_id: str) -> str:
        """Format pipeline progress for display."""
        state = self.states.get(pipeline_id)
        if not state:
            return "Pipeline not found"

        stages = [
            ("1. Intent Analysis (Claude)", PipelineStage.INTENT_ANALYSIS),
            ("2. Research (Gemini)", PipelineStage.RESEARCH),
            ("3. Implementation Plan (ChatGPT)", PipelineStage.IMPLEMENTATION_PLAN),
            ("4. Code Generation (Copilot)", PipelineStage.CODE_GENERATION),
        ]

        lines = [
            "=" * 50,
            "INTENT-TO-CODE PIPELINE",
            "=" * 50,
            f"ID: {state.id}",
            f"Progress: {state.progress_percent():.0f}%",
            "",
        ]

        for name, stage in stages:
            if stage in state.completed_stages:
                icon = "✓"
            elif stage == state.current_stage:
                icon = "◐"
            elif stage == state.failed_stage:
                icon = "✗"
            else:
                icon = "○"

            lines.append(f"  {icon} {name}")

        if state.error_message:
            lines.extend(["", f"Error: {state.error_message}"])

        return "\n".join(lines)


# =============================================================================
# Convenience Functions
# =============================================================================

_pipeline: Optional[IntentToCodePipeline] = None


def get_pipeline() -> IntentToCodePipeline:
    """Get the global pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = IntentToCodePipeline()
    return _pipeline


def run_intent_pipeline(intent: Dict[str, Any]) -> PipelineState:
    """Run the full intent-to-code pipeline."""
    pipeline = get_pipeline()
    pipeline_id = pipeline.create_pipeline(intent)
    pipeline.execute_all(pipeline_id)
    return pipeline.get_state(pipeline_id)
