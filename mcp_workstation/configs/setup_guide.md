# MCP Workstation Setup Guide

Multi-AI collaboration workstation for Claude, ChatGPT, Gemini, and GitHub Copilot.

## Quick Setup

### 1. Install the Package

```bash
cd /path/to/DAiW-Music-Brain
pip install -e .
```

### 2. Configure Your AI Assistant

#### Claude Desktop

Add to `~/.config/Claude/claude_desktop_config.json` (Linux) or equivalent:

```json
{
  "mcpServers": {
    "mcp-workstation": {
      "command": "python",
      "args": ["-m", "mcp_workstation.server"],
      "env": {
        "PYTHONPATH": "/path/to/DAiW-Music-Brain"
      }
    }
  }
}
```

#### Cursor / VS Code

Add to your workspace `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mcp-workstation": {
      "command": "python",
      "args": ["-m", "mcp_workstation.server"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

#### ChatGPT / Gemini

These use HTTP-based integration. Run the HTTP server:

```bash
# Start HTTP server on port 8765
python -c "
from mcp_workstation.orchestrator import get_workstation
from mcp_workstation.server import handle_tool_call
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length))
        result = handle_tool_call(data['tool'], data['arguments'])
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

HTTPServer(('localhost', 8765), Handler).serve_forever()
"
```

## CLI Usage

```bash
# Show dashboard
mcp-workstation status

# Register as an AI
mcp-workstation register claude

# Submit a proposal
mcp-workstation propose claude "Feature Title" "Description" feature_new

# Vote on proposal
mcp-workstation vote chatgpt PROP_ID 1

# Show phase progress
mcp-workstation phases

# Show C++ transition plan
mcp-workstation cpp

# Show AI specializations
mcp-workstation ai
```

## AI Specializations

Each AI is assigned tasks based on their strengths:

### Claude (Anthropic)
- **Best at**: Code analysis, system design, security review, complex reasoning
- **Recommended**: Architecture decisions, code review, technical docs

### ChatGPT (OpenAI)
- **Best at**: Code generation, brainstorming, explanations
- **Recommended**: Rapid prototyping, feature ideas, user docs

### Gemini (Google)
- **Best at**: Research, comparison analysis, testing
- **Recommended**: Performance analysis, test generation, research

### GitHub Copilot
- **Best at**: Code completion, inline suggestions, boilerplate
- **Recommended**: Implementation, refactoring, C++ development

## Proposal System

Each AI can submit up to **3 comprehensive improvement proposals**.

Proposals are voted on by all AIs:
- **+1**: Approve
- **0**: Neutral
- **-1**: Reject

Consensus is reached when majority votes align.

## iDAW Project Phases

### Phase 1: Core Systems (92% complete)
- CLI, groove system, intent schema
- Local AI agents, voice profiles
- MCP multi-AI workstation

### Phase 2: Expansion & Integration
- Full MCP tools
- Audio analysis
- Ableton integration
- Test suite

### Phase 3: C++ Transition
- Core DSP library
- VST3/AU plugins
- JUCE GUI
- Cross-platform builds

## Debug Protocol

The workstation includes comprehensive debugging:

```bash
# Show recent errors
mcp-workstation debug --errors

# Show performance report
mcp-workstation debug --performance
```

Logs are stored at: `~/.mcp_workstation/workstation_debug.log`
