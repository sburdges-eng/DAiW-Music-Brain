#!/usr/bin/env python3
"""
HTTP Server for MCP TODO

Provides a REST API for AI assistants that use HTTP-based function calling,
including ChatGPT plugins, Gemini, and other OpenAI-compatible APIs.

Run with:
    python -m mcp_todo.http_server --port 8080
"""

import json
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Any, Dict, Optional
import os

from .storage import TodoStorage


class TodoHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for TODO API."""

    storage: TodoStorage = None  # Will be set by server

    def _send_json(self, data: Dict[str, Any], status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _get_body(self) -> Dict[str, Any]:
        """Get JSON body from request."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        return json.loads(body)

    def _get_ai_source(self) -> str:
        """Detect AI source from headers."""
        user_agent = self.headers.get("User-Agent", "").lower()
        if "openai" in user_agent or "chatgpt" in user_agent:
            return "chatgpt"
        elif "gemini" in user_agent or "google" in user_agent:
            return "gemini"
        elif "anthropic" in user_agent or "claude" in user_agent:
            return "claude"
        elif "cursor" in user_agent:
            return "cursor"
        elif "copilot" in user_agent:
            return "copilot"
        return "http"

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Convert query params (lists) to single values
        params = {k: v[0] if len(v) == 1 else v for k, v in query.items()}

        if path == "/openapi.json" or path == "/openapi.yaml":
            # Serve OpenAPI spec
            spec_path = os.path.join(
                os.path.dirname(__file__),
                "configs",
                "openapi_spec.yaml"
            )
            if os.path.exists(spec_path):
                with open(spec_path) as f:
                    content = f.read()
                self.send_response(200)
                content_type = "application/json" if path.endswith(".json") else "text/yaml"
                self.send_header("Content-Type", content_type)
                self.end_headers()
                self.wfile.write(content.encode())
            else:
                self._send_json({"error": "OpenAPI spec not found"}, 404)

        elif path == "/.well-known/ai-plugin.json":
            # Serve ChatGPT plugin manifest
            manifest_path = os.path.join(
                os.path.dirname(__file__),
                "configs",
                "openai_plugin_manifest.json"
            )
            if os.path.exists(manifest_path):
                with open(manifest_path) as f:
                    manifest = json.load(f)
                self._send_json(manifest)
            else:
                self._send_json({"error": "Plugin manifest not found"}, 404)

        elif path == "/todos":
            # List TODOs
            todos = self.storage.list_all(
                project=params.get("project"),
                status=params.get("status"),
                priority=params.get("priority"),
                include_completed=params.get("include_completed", "true") == "true"
            )
            self._send_json({
                "success": True,
                "count": len(todos),
                "todos": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "status": t.status.value,
                        "priority": t.priority.value,
                        "tags": t.tags,
                        "project": t.project,
                    }
                    for t in todos
                ]
            })

        elif path.startswith("/todos/") and path.count("/") == 2:
            # Get single TODO
            todo_id = path.split("/")[2]

            if todo_id == "search":
                # Search endpoint
                query_str = params.get("q", "")
                todos = self.storage.search(query_str)
                self._send_json({
                    "success": True,
                    "count": len(todos),
                    "todos": [t.to_dict() for t in todos]
                })
            elif todo_id == "summary":
                # Summary endpoint
                summary = self.storage.get_summary(project=params.get("project"))
                self._send_json({
                    "success": True,
                    "summary": summary
                })
            else:
                # Get specific TODO
                todo = self.storage.get(todo_id)
                if todo:
                    self._send_json({
                        "success": True,
                        "todo": todo.to_dict()
                    })
                else:
                    self._send_json({
                        "success": False,
                        "error": f"TODO not found: {todo_id}"
                    }, 404)

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._get_body()
        ai_source = self._get_ai_source()

        if path == "/todos":
            # Create TODO
            if "title" not in body:
                self._send_json({
                    "success": False,
                    "error": "title is required"
                }, 400)
                return

            todo = self.storage.add(
                title=body["title"],
                description=body.get("description", ""),
                priority=body.get("priority", "medium"),
                tags=body.get("tags", []),
                project=body.get("project"),
                due_date=body.get("due_date"),
                context=body.get("context", ""),
                ai_source=ai_source,
            )
            self._send_json({
                "success": True,
                "message": f"Created TODO: {todo.title}",
                "todo": todo.to_dict()
            }, 201)

        elif path.endswith("/complete"):
            # Complete TODO
            todo_id = path.split("/")[2]
            todo = self.storage.complete(todo_id, ai_source=ai_source)
            if todo:
                self._send_json({
                    "success": True,
                    "message": f"Completed: {todo.title}",
                    "todo": todo.to_dict()
                })
            else:
                self._send_json({
                    "success": False,
                    "error": f"TODO not found: {todo_id}"
                }, 404)

        elif path.endswith("/start"):
            # Start TODO
            todo_id = path.split("/")[2]
            todo = self.storage.start(todo_id, ai_source=ai_source)
            if todo:
                self._send_json({
                    "success": True,
                    "message": f"Started: {todo.title}",
                    "todo": todo.to_dict()
                })
            else:
                self._send_json({
                    "success": False,
                    "error": f"TODO not found: {todo_id}"
                }, 404)

        elif path.endswith("/note"):
            # Add note
            todo_id = path.split("/")[2]
            note = body.get("note", "")
            todo = self.storage.get(todo_id)
            if todo:
                todo.add_note(note, ai_source=ai_source)
                self.storage.update(todo_id, notes=todo.notes)
                self._send_json({
                    "success": True,
                    "message": "Note added",
                    "todo": todo.to_dict()
                })
            else:
                self._send_json({
                    "success": False,
                    "error": f"TODO not found: {todo_id}"
                }, 404)

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_PATCH(self):
        """Handle PATCH requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._get_body()
        ai_source = self._get_ai_source()

        if path.startswith("/todos/"):
            todo_id = path.split("/")[2]
            todo = self.storage.update(todo_id, ai_source=ai_source, **body)
            if todo:
                self._send_json({
                    "success": True,
                    "message": f"Updated: {todo.title}",
                    "todo": todo.to_dict()
                })
            else:
                self._send_json({
                    "success": False,
                    "error": f"TODO not found: {todo_id}"
                }, 404)
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_DELETE(self):
        """Handle DELETE requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/todos/"):
            todo_id = path.split("/")[2]
            success = self.storage.delete(todo_id)
            if success:
                self._send_json({
                    "success": True,
                    "message": f"Deleted: {todo_id}"
                })
            else:
                self._send_json({
                    "success": False,
                    "error": f"TODO not found: {todo_id}"
                }, 404)
        else:
            self._send_json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        """Custom logging."""
        print(f"[HTTP] {args[0]}")


def run_server(port: int = 8080, storage_dir: Optional[str] = None):
    """Run the HTTP server."""
    TodoHTTPHandler.storage = TodoStorage(storage_dir)

    server = HTTPServer(("0.0.0.0", port), TodoHTTPHandler)
    print(f"MCP TODO HTTP Server running on http://localhost:{port}")
    print(f"  - OpenAPI spec: http://localhost:{port}/openapi.yaml")
    print(f"  - Plugin manifest: http://localhost:{port}/.well-known/ai-plugin.json")
    print(f"  - Storage: {TodoHTTPHandler.storage.storage_dir}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


def main():
    parser = argparse.ArgumentParser(description="MCP TODO HTTP Server")
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8080,
        help="Port to run the server on (default: 8080)"
    )
    parser.add_argument(
        "--storage-dir",
        help="Directory for TODO storage"
    )
    args = parser.parse_args()

    run_server(port=args.port, storage_dir=args.storage_dir)


if __name__ == "__main__":
    main()
