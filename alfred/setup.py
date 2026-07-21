#!/usr/bin/env python3
"""
Alfred zero-touch bootstrap.

Goal (per plan "Zero-touch" principle): one command gets everything ready with
no manual wiring. This script is stdlib-only and cross-platform (targets Windows,
runs anywhere). It is safe to re-run — every step is idempotent.

What it does:
  1. Create .env from .env.example if missing (you only paste one Groq key later).
  2. Make all tools/*.py executable.
  3. Preflight: check python / node+npx / ffmpeg and report what's missing.
  4. Print the exact next step (start backend / n8n) — no guesswork.

It does NOT install system packages or start long-running services; the launcher
(install.ps1 / Alfred.bat) does that. This keeps setup fast and side-effect-light.

Usage:
    python3 setup.py            # run all checks and scaffold .env
    python3 setup.py --json     # machine-readable report
"""

import argparse
import json
import os
import shutil
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def ensure_env():
    env, example = ROOT / ".env", ROOT / ".env.example"
    if env.exists():
        return "exists"
    if example.exists():
        shutil.copyfile(example, env)
        return "created"
    return "missing-example"


def make_tools_executable():
    changed = []
    tools = ROOT / "tools"
    for py in list(tools.glob("*.py")) + list((tools / "tests").glob("*.py")):
        mode = py.stat().st_mode
        py.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        changed.append(py.name)
    return changed


def preflight():
    checks = {}
    checks["python"] = sys.version.split()[0]
    checks["node"] = _ver(shutil.which("node"))
    checks["npx"] = bool(shutil.which("npx"))
    checks["ffmpeg"] = bool(shutil.which("ffmpeg"))
    return checks


def _ver(path):
    return bool(path)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Alfred zero-touch bootstrap.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = {
        "env": ensure_env(),
        "tools_executable": make_tools_executable(),
        "preflight": preflight(),
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print("Alfred bootstrap")
    print("  .env:", report["env"],
          "(paste your free Groq key into .env — that's the only manual step)")
    pf = report["preflight"]
    print("  python:", pf["python"])
    for name in ("node", "npx", "ffmpeg"):
        ok = pf[name]
        mark = "ok" if ok else "MISSING"
        print("  %-7s %s" % (name + ":", mark))
    missing = [n for n in ("node", "ffmpeg") if not pf[n]]
    print()
    if missing:
        print("Install missing prerequisites, then re-run:", ", ".join(missing))
    print("Next: start the brain    ->  python3 tools/llm_router.py --dry-run \"test\"")
    print("      start the backend  ->  cd backend && pip install -r requirements.txt "
          "&& uvicorn app:app --port 8000")
    return 0


if __name__ == "__main__":
    sys.exit(main())
