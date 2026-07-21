#!/usr/bin/env python3
"""
Alfred backend — thin FastAPI transport between the UI and the Python tools.

Design boundary (per plan): the backend is a thin controller. Single-step,
low-latency work (chat/STT/TTS) calls local tools DIRECTLY via the allowlist
dispatcher (run_tool.py); it does NOT go through n8n. Multi-step / scheduled
work (research chains, video->upload, stat tracking) is what n8n owns.

Secrets stay server-side: the browser talks to this backend, the backend holds
the keys (loaded from .env). Keys are never sent to the frontend.

Run:
    pip install -r requirements.txt
    uvicorn app:app --host 127.0.0.1 --port 8000
"""

import json
import os
import subprocess
import sys

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ALFRED_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN_TOOL = os.path.join(ALFRED_ROOT, "tools", "run_tool.py")

app = FastAPI(title="Alfred backend", version="0.1.0")

# Localhost-only UI; CORS kept tight.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_dotenv():
    """Minimal .env loader (stdlib) so keys reach the tool subprocess."""
    path = os.path.join(ALFRED_ROOT, ".env")
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()


def ask_alfred(prompt: str, system: str | None = None) -> dict:
    """Call the LLM router through the allowlist dispatcher and parse its JSON."""
    argv = [sys.executable, RUN_TOOL, "llm_router", "--prompt", prompt, "--json"]
    if system:
        argv += ["--system", system]
    proc = subprocess.run(argv, capture_output=True, text=True)
    try:
        return json.loads(proc.stdout)
    except ValueError:
        return {"ok": False, "error": "router_unparseable", "detail": proc.stderr}


class ChatIn(BaseModel):
    prompt: str
    system: str | None = None


@app.get("/api/health")
def health():
    return {"ok": True, "service": "alfred-backend", "version": "0.1.0"}


@app.post("/api/chat")
def chat(body: ChatIn):
    return ask_alfred(body.prompt, body.system)


@app.websocket("/ws")
async def ws(sock: WebSocket):
    """Realtime channel for the avatar: emits state (thinking/speaking)."""
    await sock.accept()
    try:
        while True:
            msg = json.loads(await sock.receive_text())
            await sock.send_json({"type": "state", "value": "thinking"})
            result = ask_alfred(msg.get("prompt", ""), msg.get("system"))
            await sock.send_json({"type": "state", "value": "speaking"})
            await sock.send_json({"type": "reply", "result": result})
            await sock.send_json({"type": "state", "value": "idle"})
    except WebSocketDisconnect:
        pass
