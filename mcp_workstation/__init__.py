"""
MCP Multi-AI Workstation

Orchestrates collaboration between Claude, ChatGPT, Gemini, and GitHub Copilot
for the iDAW project development.

Features:
- Multi-AI proposal system (3 improvements per AI)
- Phase management for iDAW development
- C++ transition planning
- Shared task coordination
- Debugging protocol
- AI specialization-based task assignment

Usage:
    from mcp_workstation import Workstation, AIAgent, Proposal

    ws = Workstation()
    ws.register_agent(AIAgent.CLAUDE)
    ws.submit_proposal(
        AIAgent.CLAUDE,
        "Improvement title",
        "Description",
        ProposalCategory.ARCHITECTURE
    )
    ws.advance_phase()

MCP Server:
    # Run as stdio server
    python -m mcp_workstation.server

    # Or use the entry point
    mcp-workstation
"""

from .models import (
    AIAgent,
    ProposalStatus,
    ProposalCategory,
    PhaseStatus,
    Proposal,
    Phase,
    PhaseTask,
    WorkstationState,
)

from .orchestrator import (
    Workstation,
    get_workstation,
    shutdown_workstation,
)

from .proposals import (
    ProposalManager,
    ProposalVote,
    format_proposal,
    format_proposal_list,
    get_proposal_template,
)

from .phases import (
    PhaseManager,
    IDAW_PHASES,
    format_phase_progress,
    get_next_actions,
)

from .cpp_planner import (
    CppTransitionPlanner,
    CppModule,
    CppTask,
    CppPriority,
    PortingStrategy,
    IDAW_CPP_MODULES,
    format_cpp_plan,
)

from .debug import (
    DebugProtocol,
    DebugCategory,
    DebugEvent,
    LogLevel,
    get_debug,
    trace,
    log_debug,
    log_info,
    log_warning,
    log_error,
)

from .ai_specializations import (
    AICapabilities,
    TaskType,
    AI_CAPABILITIES,
    get_capabilities,
    get_best_agent_for_task,
    get_best_agents_for_task,
    get_agents_for_category,
    suggest_task_assignment,
    get_collaboration_strategy,
    print_ai_summary,
    get_task_assignment_summary,
)

from .server import (
    get_mcp_tools,
    handle_tool_call,
    run_server,
)

__all__ = [
    # Models
    "AIAgent",
    "ProposalStatus",
    "ProposalCategory",
    "PhaseStatus",
    "Proposal",
    "Phase",
    "PhaseTask",
    "WorkstationState",

    # Orchestrator
    "Workstation",
    "get_workstation",
    "shutdown_workstation",

    # Proposals
    "ProposalManager",
    "ProposalVote",
    "format_proposal",
    "format_proposal_list",
    "get_proposal_template",

    # Phases
    "PhaseManager",
    "IDAW_PHASES",
    "format_phase_progress",
    "get_next_actions",

    # C++ Planner
    "CppTransitionPlanner",
    "CppModule",
    "CppTask",
    "CppPriority",
    "PortingStrategy",
    "IDAW_CPP_MODULES",
    "format_cpp_plan",

    # Debug
    "DebugProtocol",
    "DebugCategory",
    "DebugEvent",
    "LogLevel",
    "get_debug",
    "trace",
    "log_debug",
    "log_info",
    "log_warning",
    "log_error",

    # AI Specializations
    "AICapabilities",
    "TaskType",
    "AI_CAPABILITIES",
    "get_capabilities",
    "get_best_agent_for_task",
    "get_best_agents_for_task",
    "get_agents_for_category",
    "suggest_task_assignment",
    "get_collaboration_strategy",
    "print_ai_summary",
    "get_task_assignment_summary",

    # Server
    "get_mcp_tools",
    "handle_tool_call",
    "run_server",
]

__version__ = "1.0.0"
__author__ = "DAiW"


# =============================================================================
# Quick Test
# =============================================================================

def _test():
    """Quick test of the workstation."""
    print("MCP Workstation - Quick Test")
    print("=" * 50)

    # Initialize workstation
    ws = get_workstation()

    # Register Claude
    ws.register_agent(AIAgent.CLAUDE)

    # Show dashboard
    print(ws.get_dashboard())

    # Show AI specializations
    print("\nAI Specializations:")
    print_ai_summary()

    # Show C++ plan
    print("\n" + ws.get_cpp_progress())


if __name__ == "__main__":
    _test()
