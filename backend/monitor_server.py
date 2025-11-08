"""
Real-Time Backend Monitor Server
Serves live logs via Server-Sent Events (SSE)
"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
from pathlib import Path
import re
from datetime import datetime

app = FastAPI(title="Heimdall Monitor")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_FILE = "/tmp/backend_test.log"


def parse_log_line(line: str) -> dict:
    """Parse a log line and categorize it"""

    # Mission-related logs
    if "🚁" in line or "Received mission" in line:
        return {"type": "mission", "message": line.strip()}

    # WebSocket logs
    if "WebSocket" in line or "ws/" in line:
        return {"type": "websocket", "message": line.strip()}

    # HTTP requests
    if "POST" in line or "GET" in line:
        if "/mission/execute" in line:
            return {"type": "mission", "message": line.strip()}
        return {"type": "request", "message": line.strip()}

    # Errors
    if "ERROR" in line or "error" in line.lower() or "❌" in line:
        return {"type": "error", "message": line.strip()}

    # Info
    return {"type": "info", "message": line.strip()}


async def log_streamer():
    """Stream log file in real-time"""

    # Read existing logs first
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            # Read last 50 lines
            lines = f.readlines()
            for line in lines[-50:]:
                if line.strip():
                    log_data = parse_log_line(line)
                    yield f"data: {log_data}\n\n"

    # Now watch for new lines
    last_position = 0
    if os.path.exists(LOG_FILE):
        last_position = os.path.getsize(LOG_FILE)

    while True:
        await asyncio.sleep(0.5)  # Check every 500ms

        if not os.path.exists(LOG_FILE):
            continue

        current_size = os.path.getsize(LOG_FILE)

        if current_size > last_position:
            with open(LOG_FILE, 'r') as f:
                f.seek(last_position)
                new_lines = f.readlines()

                for line in new_lines:
                    if line.strip():
                        log_data = parse_log_line(line)
                        import json
                        yield f"data: {json.dumps(log_data)}\n\n"

                last_position = f.tell()
        elif current_size < last_position:
            # Log file was truncated
            last_position = 0


@app.get("/logs/stream")
async def stream_logs():
    """SSE endpoint for live logs"""
    return StreamingResponse(
        log_streamer(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/", response_class=HTMLResponse)
async def monitor_page():
    """Serve the monitoring page"""
    html_path = Path(__file__).parent / "monitor_live.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    return HTMLResponse(content="<h1>Monitor page not found</h1>")


if __name__ == "__main__":
    import uvicorn
    print("=" * 80)
    print("🖥️  Heimdall Real-Time Monitor")
    print("=" * 80)
    print(f"Monitoring: {LOG_FILE}")
    print("Server: http://localhost:8001")
    print("=" * 80)
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="warning")
