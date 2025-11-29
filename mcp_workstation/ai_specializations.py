"""
MCP Workstation - AI Specializations

Defines what each AI assistant excels at, ensuring optimal task assignment.
Based on real-world capabilities and strengths of each AI system.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Optional
from .models import AIAgent, ProposalCategory


class TaskType(str, Enum):
    """Types of tasks that can be assigned."""
    # Code Tasks
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    CODE_REFACTORING = "code_refactoring"
    BUG_FIXING = "bug_fixing"
    TESTING = "testing"

    # Architecture
    SYSTEM_DESIGN = "system_design"
    API_DESIGN = "api_design"
    DATABASE_DESIGN = "database_design"

    # Documentation
    DOCUMENTATION = "documentation"
    TECHNICAL_WRITING = "technical_writing"
    CODE_COMMENTS = "code_comments"

    # Analysis
    CODE_ANALYSIS = "code_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    SECURITY_ANALYSIS = "security_analysis"

    # Audio/Music Specific
    DSP_ALGORITHM = "dsp_algorithm"
    AUDIO_PROCESSING = "audio_processing"
    MIDI_HANDLING = "midi_handling"
    MUSIC_THEORY = "music_theory"

    # C++ Specific
    CPP_DEVELOPMENT = "cpp_development"
    MEMORY_OPTIMIZATION = "memory_optimization"
    LOW_LEVEL_OPTIMIZATION = "low_level_optimization"

    # Multi-file Operations
    MULTI_FILE_REFACTOR = "multi_file_refactor"
    PROJECT_SCAFFOLDING = "project_scaffolding"

    # Research
    RESEARCH = "research"
    COMPARISON_ANALYSIS = "comparison_analysis"

    # Creative
    BRAINSTORMING = "brainstorming"
    PROBLEM_SOLVING = "problem_solving"


@dataclass
class AICapabilities:
    """Capabilities and strengths of an AI agent."""
    agent: AIAgent
    display_name: str
    description: str

    # Core strengths (0.0 - 1.0 proficiency)
    strengths: Dict[TaskType, float] = field(default_factory=dict)

    # Best-suited proposal categories
    proposal_categories: List[ProposalCategory] = field(default_factory=list)

    # Languages this AI excels at
    best_languages: List[str] = field(default_factory=list)

    # Special abilities
    special_abilities: List[str] = field(default_factory=list)

    # Limitations to be aware of
    limitations: List[str] = field(default_factory=list)

    # Recommended use cases
    recommended_for: List[str] = field(default_factory=list)

    def get_strength(self, task_type: TaskType) -> float:
        """Get proficiency for a task type (0.0 - 1.0)."""
        return self.strengths.get(task_type, 0.5)

    def is_strong_at(self, task_type: TaskType, threshold: float = 0.7) -> bool:
        """Check if agent is particularly strong at a task type."""
        return self.get_strength(task_type) >= threshold


# =============================================================================
# AI Agent Capability Definitions
# =============================================================================

CLAUDE_CAPABILITIES = AICapabilities(
    agent=AIAgent.CLAUDE,
    display_name="Claude (Anthropic)",
    description="Excels at complex reasoning, code analysis, and nuanced understanding. "
                "Strong at following detailed instructions and maintaining context.",

    strengths={
        # Very Strong (0.9+)
        TaskType.CODE_ANALYSIS: 0.95,
        TaskType.CODE_REVIEW: 0.95,
        TaskType.SYSTEM_DESIGN: 0.95,
        TaskType.TECHNICAL_WRITING: 0.95,
        TaskType.PROBLEM_SOLVING: 0.95,

        # Strong (0.8-0.9)
        TaskType.CODE_GENERATION: 0.90,
        TaskType.CODE_REFACTORING: 0.90,
        TaskType.API_DESIGN: 0.90,
        TaskType.DOCUMENTATION: 0.90,
        TaskType.SECURITY_ANALYSIS: 0.90,
        TaskType.RESEARCH: 0.85,
        TaskType.BUG_FIXING: 0.85,

        # Good (0.7-0.8)
        TaskType.DSP_ALGORITHM: 0.80,
        TaskType.AUDIO_PROCESSING: 0.80,
        TaskType.CPP_DEVELOPMENT: 0.80,
        TaskType.MULTI_FILE_REFACTOR: 0.75,
        TaskType.MUSIC_THEORY: 0.75,

        # Moderate
        TaskType.PERFORMANCE_ANALYSIS: 0.70,
        TaskType.MEMORY_OPTIMIZATION: 0.70,
        TaskType.LOW_LEVEL_OPTIMIZATION: 0.65,
    },

    proposal_categories=[
        ProposalCategory.ARCHITECTURE,
        ProposalCategory.CODE_QUALITY,
        ProposalCategory.RELIABILITY,
        ProposalCategory.DOCUMENTATION,
        ProposalCategory.AI_COLLABORATION,
        ProposalCategory.DSP_ALGORITHM,
    ],

    best_languages=["Python", "TypeScript", "Rust", "C++", "Go"],

    special_abilities=[
        "Long context understanding (200K+ tokens)",
        "Complex multi-step reasoning",
        "Detailed code explanations",
        "Security vulnerability analysis",
        "Maintaining conversation context",
        "Following nuanced instructions",
    ],

    limitations=[
        "Cannot execute code directly",
        "Knowledge cutoff date applies",
        "Cannot access external URLs without tools",
    ],

    recommended_for=[
        "Complex architecture decisions",
        "Code review and analysis",
        "Technical documentation",
        "Security audits",
        "Multi-file refactoring planning",
        "API design and review",
    ],
)


CHATGPT_CAPABILITIES = AICapabilities(
    agent=AIAgent.CHATGPT,
    display_name="ChatGPT (OpenAI)",
    description="Versatile AI with strong coding abilities and broad knowledge. "
                "Excellent at explaining concepts and iterative development.",

    strengths={
        # Very Strong (0.9+)
        TaskType.CODE_GENERATION: 0.92,
        TaskType.BRAINSTORMING: 0.90,
        TaskType.DOCUMENTATION: 0.90,
        TaskType.PROBLEM_SOLVING: 0.90,

        # Strong (0.8-0.9)
        TaskType.CODE_REVIEW: 0.85,
        TaskType.TECHNICAL_WRITING: 0.85,
        TaskType.API_DESIGN: 0.85,
        TaskType.RESEARCH: 0.85,
        TaskType.BUG_FIXING: 0.85,
        TaskType.TESTING: 0.80,

        # Good (0.7-0.8)
        TaskType.SYSTEM_DESIGN: 0.80,
        TaskType.CODE_REFACTORING: 0.80,
        TaskType.CODE_ANALYSIS: 0.75,
        TaskType.MUSIC_THEORY: 0.80,
        TaskType.DSP_ALGORITHM: 0.75,

        # Moderate
        TaskType.CPP_DEVELOPMENT: 0.75,
        TaskType.AUDIO_PROCESSING: 0.70,
        TaskType.SECURITY_ANALYSIS: 0.70,
        TaskType.PERFORMANCE_ANALYSIS: 0.65,
    },

    proposal_categories=[
        ProposalCategory.FEATURE_NEW,
        ProposalCategory.FEATURE_ENHANCEMENT,
        ProposalCategory.USER_EXPERIENCE,
        ProposalCategory.DOCUMENTATION,
        ProposalCategory.TESTING,
    ],

    best_languages=["Python", "JavaScript", "TypeScript", "C#", "Java"],

    special_abilities=[
        "Code interpreter execution",
        "Web browsing capability",
        "Image generation (DALL-E)",
        "Plugin ecosystem",
        "Voice conversation mode",
    ],

    limitations=[
        "Shorter context window than Claude",
        "May be overly verbose",
        "Can hallucinate API details",
    ],

    recommended_for=[
        "Rapid prototyping",
        "Feature brainstorming",
        "User-facing documentation",
        "Test case generation",
        "Interactive development",
        "Explaining concepts",
    ],
)


GEMINI_CAPABILITIES = AICapabilities(
    agent=AIAgent.GEMINI,
    display_name="Gemini (Google)",
    description="Strong at code generation with Google-ecosystem integration. "
                "Excellent multimodal capabilities and research access.",

    strengths={
        # Very Strong (0.9+)
        TaskType.CODE_GENERATION: 0.90,
        TaskType.RESEARCH: 0.95,
        TaskType.COMPARISON_ANALYSIS: 0.90,

        # Strong (0.8-0.9)
        TaskType.DOCUMENTATION: 0.85,
        TaskType.CODE_ANALYSIS: 0.85,
        TaskType.SYSTEM_DESIGN: 0.80,
        TaskType.API_DESIGN: 0.80,
        TaskType.TESTING: 0.85,

        # Good (0.7-0.8)
        TaskType.CODE_REVIEW: 0.75,
        TaskType.BUG_FIXING: 0.80,
        TaskType.TECHNICAL_WRITING: 0.75,
        TaskType.DATABASE_DESIGN: 0.80,
        TaskType.PERFORMANCE_ANALYSIS: 0.80,

        # Moderate
        TaskType.DSP_ALGORITHM: 0.70,
        TaskType.AUDIO_PROCESSING: 0.65,
        TaskType.CPP_DEVELOPMENT: 0.70,
        TaskType.MUSIC_THEORY: 0.65,
    },

    proposal_categories=[
        ProposalCategory.PERFORMANCE,
        ProposalCategory.TESTING,
        ProposalCategory.BUILD_SYSTEM,
        ProposalCategory.TOOL_INTEGRATION,
    ],

    best_languages=["Python", "JavaScript", "Java", "Kotlin", "Go"],

    special_abilities=[
        "Google Search integration",
        "Very long context (1M+ tokens)",
        "Multimodal understanding",
        "Code execution in sandbox",
        "Integration with Google Cloud",
    ],

    limitations=[
        "Less nuanced instruction following",
        "May prioritize Google technologies",
        "Can be overly cautious",
    ],

    recommended_for=[
        "Research and comparison tasks",
        "Performance optimization",
        "Test generation",
        "Google Cloud integration",
        "Large codebase analysis",
        "Database design",
    ],
)


GITHUB_COPILOT_CAPABILITIES = AICapabilities(
    agent=AIAgent.GITHUB_COPILOT,
    display_name="GitHub Copilot",
    description="Specialized code completion and generation AI. "
                "Deeply integrated with IDE and GitHub ecosystem.",

    strengths={
        # Very Strong (0.9+)
        TaskType.CODE_GENERATION: 0.95,
        TaskType.CODE_COMMENTS: 0.90,
        TaskType.BUG_FIXING: 0.90,

        # Strong (0.8-0.9)
        TaskType.CODE_REFACTORING: 0.88,
        TaskType.TESTING: 0.88,
        TaskType.PROJECT_SCAFFOLDING: 0.85,
        TaskType.MULTI_FILE_REFACTOR: 0.85,

        # Good (0.7-0.8)
        TaskType.CODE_REVIEW: 0.75,
        TaskType.CODE_ANALYSIS: 0.75,
        TaskType.API_DESIGN: 0.70,
        TaskType.CPP_DEVELOPMENT: 0.85,
        TaskType.LOW_LEVEL_OPTIMIZATION: 0.80,

        # Moderate
        TaskType.SYSTEM_DESIGN: 0.60,
        TaskType.DOCUMENTATION: 0.65,
        TaskType.DSP_ALGORITHM: 0.70,
        TaskType.AUDIO_PROCESSING: 0.65,
        TaskType.RESEARCH: 0.50,
    },

    proposal_categories=[
        ProposalCategory.CODE_QUALITY,
        ProposalCategory.TESTING,
        ProposalCategory.CPP_PORT,
        ProposalCategory.CPP_OPTIMIZATION,
        ProposalCategory.BUILD_SYSTEM,
    ],

    best_languages=["Python", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust"],

    special_abilities=[
        "Real-time code completion",
        "IDE integration (VS Code, JetBrains)",
        "GitHub repository context",
        "Multi-file awareness in IDE",
        "Instant suggestions while typing",
        "CLI mode for terminal",
    ],

    limitations=[
        "Requires IDE context for best results",
        "Less effective for high-level discussions",
        "Cannot explain reasoning as well",
        "Shorter response length",
    ],

    recommended_for=[
        "Inline code completion",
        "Boilerplate generation",
        "Test writing",
        "Quick bug fixes",
        "C++ development",
        "Multi-file refactoring (in IDE)",
        "Code pattern completion",
    ],
)


# =============================================================================
# AI Specialization Registry
# =============================================================================

AI_CAPABILITIES: Dict[AIAgent, AICapabilities] = {
    AIAgent.CLAUDE: CLAUDE_CAPABILITIES,
    AIAgent.CHATGPT: CHATGPT_CAPABILITIES,
    AIAgent.GEMINI: GEMINI_CAPABILITIES,
    AIAgent.GITHUB_COPILOT: GITHUB_COPILOT_CAPABILITIES,
}


def get_capabilities(agent: AIAgent) -> AICapabilities:
    """Get capabilities for an AI agent."""
    return AI_CAPABILITIES.get(agent, CLAUDE_CAPABILITIES)


def get_best_agent_for_task(task_type: TaskType) -> AIAgent:
    """Get the best AI agent for a specific task type."""
    best_agent = AIAgent.CLAUDE
    best_strength = 0.0

    for agent, caps in AI_CAPABILITIES.items():
        strength = caps.get_strength(task_type)
        if strength > best_strength:
            best_strength = strength
            best_agent = agent

    return best_agent


def get_best_agents_for_task(task_type: TaskType, top_n: int = 2) -> List[tuple]:
    """Get the top N agents for a task type with their strengths."""
    rankings = []
    for agent, caps in AI_CAPABILITIES.items():
        strength = caps.get_strength(task_type)
        rankings.append((agent, strength))

    rankings.sort(key=lambda x: x[1], reverse=True)
    return rankings[:top_n]


def get_agents_for_category(category: ProposalCategory) -> List[AIAgent]:
    """Get agents best suited for a proposal category."""
    suitable = []
    for agent, caps in AI_CAPABILITIES.items():
        if category in caps.proposal_categories:
            suitable.append(agent)
    return suitable


def suggest_task_assignment(
    tasks: List[tuple],  # List of (task_name, task_type)
) -> Dict[str, AIAgent]:
    """
    Suggest optimal task assignments across available AI agents.

    Returns a dict of {task_name: suggested_agent}
    """
    assignments = {}
    agent_load = {agent: 0 for agent in AIAgent}

    # Sort tasks by specificity (more specific tasks first)
    sorted_tasks = sorted(tasks, key=lambda t: AI_CAPABILITIES[
        get_best_agent_for_task(t[1])
    ].get_strength(t[1]), reverse=True)

    for task_name, task_type in sorted_tasks:
        # Get rankings
        rankings = get_best_agents_for_task(task_type, top_n=4)

        # Consider load balancing
        for agent, strength in rankings:
            if agent_load[agent] < 3 or strength > 0.85:
                assignments[task_name] = agent
                agent_load[agent] += 1
                break
        else:
            # Fallback to best regardless of load
            assignments[task_name] = rankings[0][0]

    return assignments


def get_collaboration_strategy(task_type: TaskType) -> Dict[str, Any]:
    """
    Get a collaboration strategy for complex tasks.

    Suggests how multiple AIs can work together on a task.
    """
    rankings = get_best_agents_for_task(task_type, top_n=4)

    strategy = {
        "task_type": task_type.value,
        "primary_agent": rankings[0][0].value,
        "primary_strength": rankings[0][1],
        "roles": {},
    }

    # Assign roles based on strengths
    if task_type in (TaskType.SYSTEM_DESIGN, TaskType.API_DESIGN):
        strategy["roles"] = {
            "architect": AIAgent.CLAUDE.value,
            "implementer": AIAgent.GITHUB_COPILOT.value,
            "reviewer": AIAgent.CHATGPT.value,
            "researcher": AIAgent.GEMINI.value,
        }
    elif task_type in (TaskType.CODE_GENERATION, TaskType.CODE_REFACTORING):
        strategy["roles"] = {
            "generator": AIAgent.GITHUB_COPILOT.value,
            "reviewer": AIAgent.CLAUDE.value,
            "tester": AIAgent.GEMINI.value,
            "documenter": AIAgent.CHATGPT.value,
        }
    elif task_type in (TaskType.CPP_DEVELOPMENT, TaskType.LOW_LEVEL_OPTIMIZATION):
        strategy["roles"] = {
            "implementer": AIAgent.GITHUB_COPILOT.value,
            "optimizer": AIAgent.CLAUDE.value,
            "analyzer": AIAgent.GEMINI.value,
            "documenter": AIAgent.CHATGPT.value,
        }
    elif task_type in (TaskType.DSP_ALGORITHM, TaskType.AUDIO_PROCESSING):
        strategy["roles"] = {
            "algorithm_designer": AIAgent.CLAUDE.value,
            "implementer": AIAgent.GITHUB_COPILOT.value,
            "tester": AIAgent.GEMINI.value,
            "explainer": AIAgent.CHATGPT.value,
        }
    else:
        # Default strategy
        strategy["roles"] = {
            "primary": rankings[0][0].value,
            "secondary": rankings[1][0].value if len(rankings) > 1 else rankings[0][0].value,
            "reviewer": AIAgent.CLAUDE.value,
        }

    return strategy


# =============================================================================
# Summary Functions
# =============================================================================

def print_ai_summary():
    """Print a summary of all AI capabilities."""
    for agent, caps in AI_CAPABILITIES.items():
        print(f"\n{'='*60}")
        print(f"{caps.display_name}")
        print(f"{'='*60}")
        print(f"\n{caps.description}\n")

        print("Top Strengths:")
        sorted_strengths = sorted(
            caps.strengths.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        for task_type, strength in sorted_strengths:
            bar = "█" * int(strength * 10)
            print(f"  {task_type.value:25} {bar} {strength:.0%}")

        print(f"\nBest Languages: {', '.join(caps.best_languages[:5])}")
        print(f"Special: {', '.join(caps.special_abilities[:3])}")


def get_task_assignment_summary(tasks: List[tuple]) -> str:
    """Get a formatted summary of task assignments."""
    assignments = suggest_task_assignment(tasks)

    lines = ["Task Assignment Summary", "=" * 40]
    by_agent = {}
    for task_name, agent in assignments.items():
        if agent not in by_agent:
            by_agent[agent] = []
        by_agent[agent].append(task_name)

    for agent in AIAgent:
        if agent in by_agent:
            lines.append(f"\n{AI_CAPABILITIES[agent].display_name}:")
            for task in by_agent[agent]:
                lines.append(f"  • {task}")

    return "\n".join(lines)
