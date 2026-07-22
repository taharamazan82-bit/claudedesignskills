#!/usr/bin/env python3
"""
Alfred launcher — starts backend + frontend together, cross-platform, stdlib-only.

This is the "one command, no manual steps" entry point. On Windows the Alfred.bat
wrapper just calls this. It:
  1. ensures .env exists (runs setup.py logic if needed),
  2. starts the FastAPI backend (uvicorn) on :8000,
  3. starts the Vite dev server (npm run dev) on :5173,
  4. streams both, and shuts both down cleanly on Ctrl+C.

Usage:
    python3 start.py                # start everything
    python3 start.py --backend-only # just the API (for tool/CLI testing)
"""

import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def ensure_env():
    env = ROOT / ".env"
    if not env.exists():
        subprocess.run([sys.executable, str(ROOT / "setup.py")], check=False)


def start_backend():
    # Prefer the venv uvicorn if present, else module form.
    cmd = [sys.executable, "-m", "uvicorn", "app:app",
           "--host", "127.0.0.1", "--port", "8000"]
    return subprocess.Popen(cmd, cwd=str(ROOT / "backend"))


def start_frontend():
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm:
        print("[warn] npm not found — frontend not started. Install Node.js.")
        return None
    fe = ROOT / "frontend"
    if not (fe / "node_modules").exists():
        print("[setup] installing frontend deps (first run only)…")
        subprocess.run([npm, "install", "--no-audit", "--no-fund"], cwd=str(fe))
    return subprocess.Popen([npm, "run", "dev"], cwd=str(fe))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Start Alfred.")
    parser.add_argument("--backend-only", action="store_true")
    args = parser.parse_args(argv)

    ensure_env()
    procs = []
    try:
        print("[alfred] starting backend on http://127.0.0.1:8000 …")
        procs.append(start_backend())
        if not args.backend_only:
            time.sleep(1.0)
            fe = start_frontend()
            if fe:
                procs.append(fe)
                print("[alfred] UI will be at http://127.0.0.1:5173")
        print("[alfred] running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
            for p in procs:
                if p.poll() is not None:
                    raise SystemExit("[alfred] a process exited; shutting down.")
    except (KeyboardInterrupt, SystemExit) as e:
        print("\n" + str(e) if str(e) else "\n[alfred] stopping…")
    finally:
        for p in procs:
            try:
                if os.name == "nt":
                    p.terminate()
                else:
                    p.send_signal(signal.SIGTERM)
            except Exception:
                pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
