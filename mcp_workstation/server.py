"""
MCP Workstation - MCP Server

Exposes workstation functionality as MCP tools for AI assistants.
"""

import json
import sys
from typing import Any, Callable, Dict, List, Optional

from .models import AIAgent, ProposalCategory, ProposalStatus, PhaseStatus
from .orchestrator import get_workstation, Workstation
from .ai_specializations import TaskType
from .debug import log_info, log_error, DebugCategory


# =============================================================================
# MCP Tool Definitions
# =============================================================================

def get_mcp_tools() -> List[Dict[str, Any]]:
    """
    Get MCP tool definitions for the workstation.

    Returns a list of tool definitions compatible with the MCP protocol.
    """
    return [
        # Agent Management
        {
            "name": "workstation_register",
            "description": "Register an AI agent with the workstation. Call this first!",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "enum": ["claude", "chatgpt", "gemini", "github_copilot"],
                        "description": "The AI agent to register",
                    },
                },
                "required": ["agent"],
            },
        },
        {
            "name": "workstation_status",
            "description": "Get current workstation status and dashboard",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "workstation_capabilities",
            "description": "Get capabilities and strengths for an AI agent",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "enum": ["claude", "chatgpt", "gemini", "github_copilot"],
                    },
                },
                "required": ["agent"],
            },
        },

        # Proposal Operations
        {
            "name": "proposal_submit",
            "description": "Submit an improvement proposal (max 3 per agent)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "enum": ["claude", "chatgpt", "gemini", "github_copilot"],
                    },
                    "title": {
                        "type": "string",
                        "description": "Proposal title",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed proposal description",
                    },
                    "category": {
                        "type": "string",
                        "enum": [c.value for c in ProposalCategory],
                        "description": "Proposal category",
                    },
                    "priority": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10,
                        "description": "Priority 1-10 (10 highest)",
                    },
                    "estimated_effort": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "very_high"],
                    },
                    "phase_target": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 3,
                        "description": "Which iDAW phase (1-3)",
                    },
                    "implementation_notes": {
                        "type": "string",
                        "description": "Technical implementation notes",
                    },
                },
                "required": ["agent", "title", "description", "category"],
            },
        },
        {
            "name": "proposal_vote",
            "description": "Vote on a proposal (-1 reject, 0 neutral, 1 approve)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "enum": ["claude", "chatgpt", "gemini", "github_copilot"],
                    },
                    "proposal_id": {
                        "type": "string",
                        "description": "ID of the proposal to vote on",
                    },
                    "vote": {
                        "type": "integer",
                        "enum": [-1, 0, 1],
                        "description": "-1=reject, 0=neutral, 1=approve",
                    },
                    "comment": {
                        "type": "string",
                        "description": "Optional vote comment",
                    },
                },
                "required": ["agent", "proposal_id", "vote"],
            },
        },
        {
            "name": "proposal_list",
            "description": "List proposals (optionally filtered)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "enum": ["claude", "chatgpt", "gemini", "github_copilot"],
                        "description": "Filter by agent",
                    },
                    "status": {
                        "type": "string",
                        "enum": [s.value for s in ProposalStatus],
                        "description": "Filter by status",
                    },
                },
            },
        },
        {
            "name": "proposal_pending_votes",
            "description": "Get proposals waiting for your vote",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "enum": ["claude", "chatgpt", "gemini", "github_copilot"],
                    },
                },
                "required": ["agent"],
            },
        },

        # Phase Operations
        {
            "name": "phase_status",
            "description": "Get current phase status and tasks",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "phase_progress",
            "description": "Get formatted phase progress view",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "task_update",
            "description": "Update a task status",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "phase_id": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 3,
                    },
                    "task_id": {
                        "type": "string",
                    },
                    "status": {
                        "type": "string",
                        "enum": [s.value for s in PhaseStatus],
                    },
                    "progress": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                    },
                    "notes": {
                        "type": "string",
                    },
                },
                "required": ["phase_id", "task_id", "status"],
            },
        },
        {
            "name": "task_assign",
            "description": "Assign a task to an AI agent",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "phase_id": {
                        "type": "integer",
                    },
                    "task_id": {
                        "type": "string",
                    },
                    "agent": {
                        "type": "string",
                        "enum": ["claude", "chatgpt", "gemini", "github_copilot"],
                    },
                },
                "required": ["phase_id", "task_id", "agent"],
            },
        },

        # C++ Transition
        {
            "name": "cpp_plan",
            "description": "Get C++ transition plan and status",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "cpp_progress",
            "description": "Get formatted C++ transition progress",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "cpp_start_module",
            "description": "Start work on a C++ module",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "module_id": {
                        "type": "string",
                    },
                    "agent": {
                        "type": "string",
                        "enum": ["claude", "chatgpt", "gemini", "github_copilot"],
                    },
                },
                "required": ["module_id"],
            },
        },
        {
            "name": "cpp_update_module",
            "description": "Update C++ module progress",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "module_id": {
                        "type": "string",
                    },
                    "progress": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                    },
                    "status": {
                        "type": "string",
                        "enum": [s.value for s in PhaseStatus],
                    },
                },
                "required": ["module_id", "progress"],
            },
        },
        {
            "name": "cpp_cmake",
            "description": "Get CMake build plan",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },

        # Task Assignment
        {
            "name": "suggest_assignments",
            "description": "Get optimal AI assignments for tasks",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {
                                    "type": "string",
                                    "enum": [t.value for t in TaskType],
                                },
                            },
                            "required": ["name", "type"],
                        },
                    },
                },
                "required": ["tasks"],
            },
        },
        {
            "name": "workload",
            "description": "Get current workload for each AI agent",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },

        # Debug
        {
            "name": "debug_summary",
            "description": "Get debug and monitoring summary",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
    ]


# =============================================================================
# Tool Handlers
# =============================================================================

def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle an MCP tool call.

    Returns the result as a dictionary.
    """
    ws = get_workstation()

    try:
        # Agent Management
        if name == "workstation_register":
            agent = AIAgent(arguments["agent"])
            ws.register_agent(agent)
            return {
                "success": True,
                "message": f"Agent {agent.display_name} registered",
                "capabilities": ws.get_agent_capabilities(agent),
            }

        elif name == "workstation_status":
            return {
                "dashboard": ws.get_dashboard(),
                "status": ws.get_status(),
            }

        elif name == "workstation_capabilities":
            agent = AIAgent(arguments["agent"])
            return ws.get_agent_capabilities(agent)

        # Proposals
        elif name == "proposal_submit":
            result = ws.submit_proposal(
                agent=AIAgent(arguments["agent"]),
                title=arguments["title"],
                description=arguments["description"],
                category=ProposalCategory(arguments["category"]),
                priority=arguments.get("priority", 5),
                estimated_effort=arguments.get("estimated_effort", "medium"),
                phase_target=arguments.get("phase_target", 1),
                implementation_notes=arguments.get("implementation_notes", ""),
            )
            if result:
                return {"success": True, "proposal": result}
            return {"success": False, "error": "Failed to submit proposal (limit reached?)"}

        elif name == "proposal_vote":
            result = ws.vote_on_proposal(
                agent=AIAgent(arguments["agent"]),
                proposal_id=arguments["proposal_id"],
                vote=arguments["vote"],
                comment=arguments.get("comment", ""),
            )
            return {"success": result}

        elif name == "proposal_list":
            all_proposals = ws.get_all_proposals()

            # Apply filters
            proposals = all_proposals["proposals"]
            if "agent" in arguments:
                proposals = [p for p in proposals if p["agent"] == arguments["agent"]]
            if "status" in arguments:
                proposals = [p for p in proposals if p["status"] == arguments["status"]]

            return {
                "proposals": proposals,
                "summary": all_proposals["summary"],
            }

        elif name == "proposal_pending_votes":
            agent = AIAgent(arguments["agent"])
            data = ws.get_proposals_for_agent(agent)
            return {
                "pending_votes": data["pending_votes"],
                "slots_remaining": data["slots_remaining"],
            }

        # Phases
        elif name == "phase_status":
            return ws.get_current_phase()

        elif name == "phase_progress":
            return {"progress": ws.get_phase_progress()}

        elif name == "task_update":
            ws.update_task(
                phase_id=arguments["phase_id"],
                task_id=arguments["task_id"],
                status=arguments["status"],
                progress=arguments.get("progress"),
                notes=arguments.get("notes"),
            )
            return {"success": True}

        elif name == "task_assign":
            ws.assign_task_to_agent(
                phase_id=arguments["phase_id"],
                task_id=arguments["task_id"],
                agent=AIAgent(arguments["agent"]),
            )
            return {"success": True}

        # C++ Transition
        elif name == "cpp_plan":
            return ws.get_cpp_plan()

        elif name == "cpp_progress":
            return {"progress": ws.get_cpp_progress()}

        elif name == "cpp_start_module":
            agent = AIAgent(arguments["agent"]) if "agent" in arguments else None
            ws.start_cpp_module(arguments["module_id"], agent)
            return {"success": True}

        elif name == "cpp_update_module":
            ws.update_cpp_module(
                module_id=arguments["module_id"],
                progress=arguments["progress"],
                status=arguments.get("status"),
            )
            return {"success": True}

        elif name == "cpp_cmake":
            return {"cmake": ws.get_cmake_plan()}

        # Task Assignment
        elif name == "suggest_assignments":
            tasks = [(t["name"], TaskType(t["type"])) for t in arguments["tasks"]]
            return {"assignments": ws.suggest_assignments(tasks)}

        elif name == "workload":
            return {"workload": ws.get_agent_workload()}

        # Debug
        elif name == "debug_summary":
            return ws.get_debug_summary()

        else:
            return {"error": f"Unknown tool: {name}"}

    except Exception as e:
        log_error(DebugCategory.MCP, f"Tool error: {name}: {e}")
        return {"error": str(e)}


# =============================================================================
# MCP Server (stdio transport)
# =============================================================================

def run_server():
    """
    Run the MCP server using stdio transport.

    This implements the MCP protocol for tool invocation.
    """
    log_info(DebugCategory.MCP, "MCP Workstation server starting")

    tools = get_mcp_tools()

    while True:
        try:
            # Read JSON-RPC request from stdin
            line = sys.stdin.readline()
            if not line:
                break

            request = json.loads(line)
            method = request.get("method", "")
            params = request.get("params", {})
            req_id = request.get("id")

            response = {"jsonrpc": "2.0", "id": req_id}

            if method == "initialize":
                response["result"] = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                    },
                    "serverInfo": {
                        "name": "mcp-workstation",
                        "version": "1.0.0",
                    },
                }

            elif method == "tools/list":
                response["result"] = {"tools": tools}

            elif method == "tools/call":
                tool_name = params.get("name", "")
                tool_args = params.get("arguments", {})
                result = handle_tool_call(tool_name, tool_args)
                response["result"] = {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2),
                        }
                    ],
                }

            elif method == "notifications/initialized":
                # No response needed for notifications
                continue

            else:
                response["error"] = {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                }

            # Write response to stdout
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except json.JSONDecodeError as e:
            log_error(DebugCategory.MCP, f"JSON decode error: {e}")
        except Exception as e:
            log_error(DebugCategory.MCP, f"Server error: {e}")


if __name__ == "__main__":
    run_server()
