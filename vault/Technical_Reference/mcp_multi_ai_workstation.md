# MCP Multi-AI Workstation

> A collaborative system where Claude, ChatGPT, Gemini, and GitHub Copilot work together on DAiW development.

## Overview

The MCP (Model Context Protocol) Multi-AI Workstation enables multiple AI assistants to collaborate on music production software development. Each AI brings specialized strengths to different aspects of the project.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   MCP Workstation                        │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ Claude  │  │ ChatGPT │  │ Gemini  │  │ Copilot │    │
│  │         │  │         │  │         │  │         │    │
│  │ Emotion │  │ UX/Flow │  │ Theory  │  │  Code   │    │
│  │ Intent  │  │ Teaching│  │ Analysis│  │  Impl   │    │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘    │
│       │            │            │            │          │
│       └────────────┴─────┬──────┴────────────┘          │
│                          │                               │
│              ┌───────────▼───────────┐                  │
│              │    Orchestrator       │                  │
│              │  - Task Assignment    │                  │
│              │  - Proposal Voting    │                  │
│              │  - Phase Management   │                  │
│              └───────────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

## AI Specializations

### Claude
- **Strengths**: Emotional depth, intent analysis, vulnerability exploration
- **Domains**: Core wound work, shadow work, inner child healing
- **Therapy Questions**: 125 (emotional/vulnerability/inner work)

### ChatGPT
- **Strengths**: User experience, teaching, relationship dynamics
- **Domains**: Coping mechanisms, boundaries, forgiveness
- **Therapy Questions**: 125 (relationships/coping/identity)

### Gemini
- **Strengths**: Music theory, harmonic analysis, technical accuracy
- **Domains**: Harmony, melody, voice leading, key detection
- **Musician Questions**: 125 (harmony/theory/analysis)

### GitHub Copilot
- **Strengths**: Code implementation, production techniques, technical systems
- **Domains**: Arrangement, rhythm, sound design, mixing
- **Musician Questions**: 125 (production/arrangement/technical)

## Proposal System

Each AI submits up to 3 proposals per phase. The user votes on proposals:
- **Y** = Approve
- **N** = Reject

Approved proposals are assigned to AIs based on their specializations.

## The Three Phases (iDAW)

### Phase 1: Core Systems (92% complete)
- Intent schema and interrogation
- Groove extraction and application
- Chord analysis and diagnosis
- Rule-breaking framework

### Phase 2: Expansion & Integration
- Multi-AI collaboration tools
- Advanced humanization
- Audio fingerprinting
- Benchmark systems

### Phase 3: C++ Professional DAW
- Real-time audio safety
- JUCE plugin framework
- SIMD-optimized DSP
- Lock-free data structures

## Usage

### CLI Commands
```bash
# Check workstation status
python -m mcp_workstation.cli status

# Register an AI
python -m mcp_workstation.cli register claude

# Submit a proposal
python -m mcp_workstation.cli propose claude "Feature Name" "Description"

# Vote on proposals
python -m mcp_workstation.cli vote

# View C++ transition plan
python -m mcp_workstation.cli cpp status
```

### MCP Server
```bash
# Start the MCP server
python -m mcp_workstation.server
```

## Files

| File | Purpose |
|------|---------|
| `mcp_workstation/models.py` | Data models (AIAgent, Proposal, Phase) |
| `mcp_workstation/orchestrator.py` | Central coordination |
| `mcp_workstation/proposals.py` | Proposal management |
| `mcp_workstation/phases.py` | Phase tracking |
| `mcp_workstation/ai_specializations.py` | AI capability mapping |
| `mcp_workstation/cpp_planner.py` | C++ transition planning |
| `mcp_workstation/server.py` | MCP server (20+ tools) |
| `mcp_workstation/cli.py` | Command-line interface |

## Related

- [[song_intent_schema]] - The emotional intent framework
- [[question_bank]] - 500+ branching questions
- [[cpp_foundation]] - C++ real-time audio architecture
