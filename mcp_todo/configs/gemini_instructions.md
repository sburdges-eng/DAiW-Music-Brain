# Using MCP TODO with Google Gemini

## Option 1: Google AI Studio with Function Calling

In Google AI Studio or when using the Gemini API, you can integrate MCP TODO by defining these function declarations:

```python
import google.generativeai as genai

# Define TODO functions for Gemini
todo_functions = [
    {
        "name": "todo_add",
        "description": "Add a new TODO task",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task title"},
                "description": {"type": "string", "description": "Task description"},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                "tags": {"type": "array", "items": {"type": "string"}},
                "project": {"type": "string"},
                "due_date": {"type": "string", "description": "Due date (YYYY-MM-DD)"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "todo_list",
        "description": "List all TODO tasks with optional filters",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked", "cancelled"]},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                "project": {"type": "string"}
            }
        }
    },
    {
        "name": "todo_complete",
        "description": "Mark a TODO as completed",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "TODO ID to complete"}
            },
            "required": ["id"]
        }
    },
    {
        "name": "todo_start",
        "description": "Mark a TODO as in progress",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "TODO ID to start"}
            },
            "required": ["id"]
        }
    },
    {
        "name": "todo_delete",
        "description": "Delete a TODO",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "TODO ID to delete"}
            },
            "required": ["id"]
        }
    },
    {
        "name": "todo_search",
        "description": "Search TODOs by text",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "todo_summary",
        "description": "Get TODO statistics",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]

# Create the model with TODO tools
model = genai.GenerativeModel(
    model_name="gemini-pro",
    tools=todo_functions
)
```

## Option 2: Integration Script

Use this Python script to bridge Gemini and MCP TODO:

```python
#!/usr/bin/env python3
"""
Gemini + MCP TODO Integration
"""

import google.generativeai as genai
import sys
sys.path.insert(0, '/path/to/DAiW-Music-Brain')

from mcp_todo.storage import TodoStorage

# Initialize storage
storage = TodoStorage()

def handle_function_call(function_call):
    """Handle function calls from Gemini."""
    name = function_call.name
    args = dict(function_call.args)

    if name == "todo_add":
        todo = storage.add(
            title=args["title"],
            description=args.get("description", ""),
            priority=args.get("priority", "medium"),
            tags=args.get("tags", []),
            project=args.get("project"),
            due_date=args.get("due_date"),
            ai_source="gemini"
        )
        return f"Created TODO: {todo.title} (ID: {todo.id})"

    elif name == "todo_list":
        todos = storage.list_all(
            status=args.get("status"),
            priority=args.get("priority"),
            project=args.get("project")
        )
        return "\n".join(str(t) for t in todos) or "No TODOs found"

    elif name == "todo_complete":
        todo = storage.complete(args["id"], ai_source="gemini")
        return f"Completed: {todo.title}" if todo else "TODO not found"

    elif name == "todo_start":
        todo = storage.start(args["id"], ai_source="gemini")
        return f"Started: {todo.title}" if todo else "TODO not found"

    elif name == "todo_delete":
        success = storage.delete(args["id"])
        return "Deleted" if success else "TODO not found"

    elif name == "todo_search":
        todos = storage.search(args["query"])
        return "\n".join(str(t) for t in todos) or "No matches found"

    elif name == "todo_summary":
        summary = storage.get_summary()
        return f"Total: {summary['total']}, Pending: {summary['pending']}, In Progress: {summary['in_progress']}, Completed: {summary['completed']}"

# Configure Gemini
genai.configure(api_key="YOUR_API_KEY")

# Create chat with tools
model = genai.GenerativeModel(
    model_name="gemini-pro",
    tools=todo_functions
)
chat = model.start_chat()

# Example usage
response = chat.send_message("Add a task to review the code")
if response.candidates[0].content.parts[0].function_call:
    result = handle_function_call(
        response.candidates[0].content.parts[0].function_call
    )
    print(result)
```

## Option 3: HTTP API Bridge

For Gemini integrations that prefer HTTP, run the HTTP server:

```bash
python -m mcp_todo.http_server --port 8080
```

Then use Gemini's HTTP function calling to connect to `http://localhost:8080`.

## Shared Storage

All AI assistants share the same TODO storage at `~/.mcp_todo/todos.json`, so tasks created in Gemini appear in Claude, ChatGPT, and Cursor!
