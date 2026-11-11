#!/usr/bin/env python3
"""
Resource Link Hub - REST API Backend
Pure Python using http.server (no external frameworks)
Port: 5000 | Storage: /var/lib/backend_data/links.json
"""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# ─── Configuration ────────────────────────────────────────────────────────────
PORT = 5000
DATA_DIR = "/var/lib/backend_data"
DATA_FILE = os.path.join(DATA_DIR, "links.json")

REQUIRED_FIELDS = {"title", "category", "url", "description"}
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def ensure_data_file():
    """Ensure the data directory and file exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)


def load_links() -> list:
    ensure_data_file()
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_links(links: list):
    ensure_data_file()
    with open(DATA_FILE, "w") as f:
        json.dump(links, f, indent=2, ensure_ascii=False)


# ─── Request Handler ──────────────────────────────────────────────────────────

class LinkHubHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Custom minimal logging
        print(f"[{self.log_date_time_string()}] {self.address_string()} - {format % args}")

    # ── Response Helpers ──────────────────────────────────────────────────────

    def _send_json(self, status: int, payload):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for key, value in CORS_HEADERS.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, message: str):
        self._send_json(status, {"error": message})

    def _read_json_body(self):
        """Read and parse JSON request body. Returns (data, error_msg)."""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return None, "Request body is empty"
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8")), None
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return None, f"Invalid JSON: {e}"

    # ── CORS Preflight ────────────────────────────────────────────────────────

    def do_OPTIONS(self):
        self.send_response(204)
        for key, value in CORS_HEADERS.items():
            self.send_header(key, value)
        self.end_headers()

    # ── GET /links ────────────────────────────────────────────────────────────

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/links":
            self._send_error(404, "Endpoint not found. Available: GET /links")
            return

        links = load_links()
        self._send_json(200, links)

    # ── POST /links ───────────────────────────────────────────────────────────

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/links":
            self._send_error(404, "Endpoint not found. Available: POST /links")
            return

        data, err = self._read_json_body()
        if err:
            self._send_error(400, err)
            return

        # Validate required fields
        missing = REQUIRED_FIELDS - set(data.keys())
        if missing:
            self._send_error(
                400,
                f"Missing required fields: {', '.join(sorted(missing))}. "
                f"Required: title, category, url, description"
            )
            return

        # Validate field values are non-empty strings
        empty_fields = [
            f for f in REQUIRED_FIELDS
            if not isinstance(data.get(f), str) or not data[f].strip()
        ]
        if empty_fields:
            self._send_error(
                400,
                f"Fields must be non-empty strings: {', '.join(sorted(empty_fields))}"
            )
            return

        # Build new link entry (only allowed fields)
        new_link = {
            "title": data["title"].strip(),
            "category": data["category"].strip(),
            "url": data["url"].strip(),
            "description": data["description"].strip(),
        }

        links = load_links()
        links.append(new_link)
        save_links(links)

        self._send_json(201, {"message": "Link added successfully", "link": new_link})

    # ── DELETE /links?index=X ─────────────────────────────────────────────────

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path != "/links":
            self._send_error(404, "Endpoint not found. Available: DELETE /links?index=X")
            return

        params = parse_qs(parsed.query)
        if "index" not in params:
            self._send_error(400, "Missing query parameter: index (e.g., DELETE /links?index=0)")
            return

        raw_index = params["index"][0]
        try:
            index = int(raw_index)
        except ValueError:
            self._send_error(400, f"Parameter 'index' must be an integer, got: '{raw_index}'")
            return

        links = load_links()

        if len(links) == 0:
            self._send_error(404, "No links found. The list is empty.")
            return

        if index < 0 or index >= len(links):
            self._send_error(
                404,
                f"Index {index} out of range. Valid range: 0 – {len(links) - 1}"
            )
            return

        removed = links.pop(index)
        save_links(links)

        self._send_json(200, {"message": "Link deleted successfully", "deleted": removed})


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ensure_data_file()
    server = HTTPServer(("0.0.0.0", PORT), LinkHubHandler)
    print(f"🚀 Resource Link Hub API running on http://0.0.0.0:{PORT}")
    print(f"   Data file: {DATA_FILE}")
    print("   Endpoints: GET /links | POST /links | DELETE /links?index=X")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⛔ Server stopped.")
        server.server_close()

