#!/usr/bin/env python3
"""
Alfred tool dispatcher — the ONLY entry point the AI is allowed to call.

Security model (per plan Eng review E2 + user requirement "no injection risk"):
  - The AI never produces shell commands. It picks a tool NAME from a closed
    allowlist and passes structured arguments. This file validates both.
  - Tools are invoked with subprocess using a LIST of arguments (never a shell
    string), so there is no shell interpolation and no command-injection surface.
  - Everything runs on localhost; no tool here opens a network listener.
  - Unknown tool names, or arguments failing validation, are rejected outright.

Add a new capability by registering it in ALLOWLIST — nothing else can run.

Usage:
    ./run_tool.py --list
    ./run_tool.py llm_router --prompt "merhaba" --json
    ./run_tool.py --json llm_router --prompt "merhaba"     # wrap output as JSON

Exit codes:
    0  tool ran (its own exit code is reported in --json mode)
    4  usage error / tool not in allowlist / invalid argument
"""

import argparse
import json
import os
import subprocess
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))

# Closed allowlist. Each tool maps to its script plus the flags it accepts.
# "flags" are passed through verbatim (validated to be in the set); "values"
# flags take exactly one following argument.
ALLOWLIST = {
    "llm_router": {
        "script": "llm_router.py",
        "value_flags": {"--prompt", "--system", "--provider", "--timeout"},
        "bool_flags": {"--json", "--dry-run", "--list"},
        # --prompt is passed positionally to llm_router (its first positional arg)
        "positional_from": "--prompt",
    },
}


def build_argv(tool, spec, extra):
    """Translate validated flags into a safe argv list for the target script."""
    argv = [sys.executable, os.path.join(TOOLS_DIR, spec["script"])]
    i = 0
    positional = None
    while i < len(extra):
        tok = extra[i]
        if tok in spec.get("bool_flags", set()):
            argv.append(tok)
            i += 1
        elif tok in spec.get("value_flags", set()):
            if i + 1 >= len(extra):
                raise ValueError("flag %s expects a value" % tok)
            val = extra[i + 1]
            if tok == spec.get("positional_from"):
                positional = val
            else:
                argv.extend([tok, val])
            i += 2
        else:
            raise ValueError("argument %r not permitted for tool %r" % (tok, tool))
    if positional is not None:
        argv.append(positional)
    return argv


def main(argv=None):
    parser = argparse.ArgumentParser(description="Alfred allowlist tool dispatcher.")
    parser.add_argument("--list", action="store_true", help="list allowed tools")
    parser.add_argument("--json", action="store_true",
                        help="wrap the tool result in a JSON envelope")
    parser.add_argument("tool", nargs="?", help="tool name from the allowlist")
    parser.add_argument("args", nargs=argparse.REMAINDER,
                        help="validated flags for the tool")
    args = parser.parse_args(argv)

    if args.list:
        print(json.dumps({"tools": sorted(ALLOWLIST)}, indent=2))
        return 0

    if not args.tool:
        parser.error("a tool name is required (or use --list)")

    if args.tool not in ALLOWLIST:
        sys.stderr.write(
            "refused: %r is not in the allowlist.\n  fix: register it in "
            "ALLOWLIST or use --list to see permitted tools.\n" % args.tool)
        return 4

    spec = ALLOWLIST[args.tool]
    try:
        target_argv = build_argv(args.tool, spec, args.args)
    except ValueError as e:
        sys.stderr.write("refused: %s\n" % e)
        return 4

    # No shell — list argv only. This is the injection-proof boundary.
    proc = subprocess.run(target_argv, capture_output=True, text=True)

    if args.json:
        print(json.dumps({
            "tool": args.tool, "exit": proc.returncode,
            "stdout": proc.stdout, "stderr": proc.stderr,
        }, ensure_ascii=False, indent=2))
    else:
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
