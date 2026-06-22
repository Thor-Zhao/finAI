#!/usr/bin/env python3
"""n8n bridge: receives HTTP trigger → runs auto-publish script"""

import http.server
import json
import subprocess
import urllib.parse
import threading

PORT = 9999
TOKEN = "n8n-bridge-secret-2026"
SCRIPT = "/home/thor/finAI-website/auto-publish.py"

# Track running executions
_current_exec = None

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/health":
            self.send_json({"status": "ok"})
        elif path == "/status":
            self.send_json({"running": _current_exec is not None})
        else:
            self.send_error(404)

    def do_POST(self):
        global _current_exec
        path = urllib.parse.urlparse(self.path).path
        if path != "/trigger":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {}
        if data.get("token") != TOKEN:
            self.send_json({"error": "invalid token"}, 403)
            return

        if _current_exec:
            self.send_json({"error": "already running"}, 409)
            return

        # Run async
        def run():
            global _current_exec
            _current_exec = "running"
            try:
                result = subprocess.run(
                    ["python3", SCRIPT],
                    capture_output=True, text=True, timeout=600,
                    cwd="/home/thor/finAI-website"
                )
                _current_exec = "done" if result.returncode == 0 else f"failed({result.returncode})"
            except subprocess.TimeoutExpired:
                _current_exec = "timeout"
            except Exception as e:
                _current_exec = f"error({e})"

        t = threading.Thread(target=run, daemon=True)
        t.start()

        self.send_json({"status": "started", "message": "publishing in background"})

    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass  # quiet

print(f"n8n bridge listening on :{PORT}")
httpd = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
httpd.serve_forever()
