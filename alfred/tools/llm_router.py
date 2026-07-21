#!/usr/bin/env python3
"""
Alfred LLM Router — free-tier provider routing with automatic fallback.

The "brain" of Alfred, built on the "Python does the work, AI only supervises"
principle. This script is fully standalone: it runs from the CLI without any AI
in the loop, and uses ONLY the Python 3 standard library (no pip install needed),
which keeps the zero-touch install promise intact.

Providers are OpenAI-compatible chat-completion endpoints, tried in order until
one succeeds. Keys are read from the environment (never hardcoded). Missing-key
providers are skipped automatically.

Retry taxonomy (per plan Eng review E3):
    success              -> return immediately
    429 / 5xx / network  -> transient, try the next provider
    401 / 403 / 404      -> provider misconfigured, skip it, try the next
    other 4xx (400/422)  -> malformed request, stop and report (won't self-heal)

Usage:
    ./llm_router.py "Merhaba Alfred"                 # ask, human-readable output
    ./llm_router.py --json "özetle: ..."             # machine output for n8n/backend
    ./llm_router.py --dry-run "test"                 # no network, show routing plan
    ./llm_router.py --provider groq "sadece groq"    # force one provider
    ./llm_router.py --system "Sen Alfred'sin." "sel" # set a system prompt
    ./llm_router.py --list                           # show configured providers

Environment variables (set via .env, never committed):
    GROQ_API_KEY, GROQ_MODEL           (default model: llama-3.3-70b-versatile)
    GEMINI_API_KEY, GEMINI_MODEL       (default model: gemini-2.0-flash)
    OPENROUTER_API_KEY, OPENROUTER_MODEL (default: meta-llama/llama-3.3-70b-instruct:free)
    ALFRED_PROVIDER_ORDER              (comma list, e.g. "groq,gemini,openrouter")

Exit codes:
    0  success
    2  no provider succeeded (all transient failures / no keys)
    3  malformed request (non-retryable 4xx)
    4  usage / argument error
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

# Provider registry. Every entry is an OpenAI-compatible /chat/completions API,
# so a single request path serves all of them. base_url has no trailing slash.
PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "model_env": "GROQ_MODEL",
        "default_model": "llama-3.3-70b-versatile",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "key_env": "GEMINI_API_KEY",
        "model_env": "GEMINI_MODEL",
        "default_model": "gemini-2.0-flash",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "key_env": "OPENROUTER_API_KEY",
        "model_env": "OPENROUTER_MODEL",
        "default_model": "meta-llama/llama-3.3-70b-instruct:free",
    },
}

DEFAULT_ORDER = ["groq", "gemini", "openrouter"]


def provider_order():
    """Return the configured provider order, honoring ALFRED_PROVIDER_ORDER."""
    raw = os.environ.get("ALFRED_PROVIDER_ORDER", "").strip()
    if raw:
        order = [p.strip() for p in raw.split(",") if p.strip() in PROVIDERS]
        if order:
            return order
    return list(DEFAULT_ORDER)


def has_key(name):
    return bool(os.environ.get(PROVIDERS[name]["key_env"], "").strip())


def model_for(name):
    spec = PROVIDERS[name]
    return os.environ.get(spec["model_env"], "").strip() or spec["default_model"]


def _classify(status):
    """Map an HTTP status to a routing action: 'next', 'stop', or 'ok'."""
    if status == 200:
        return "ok"
    if status == 429 or 500 <= status < 600:
        return "next"  # transient — try the next provider
    if status in (401, 403, 404):
        return "next"  # this provider is misconfigured — skip it
    return "stop"  # other 4xx: malformed request, won't self-heal


def call_provider(name, messages, timeout=30, max_tokens=1024, temperature=0.6):
    """
    Call one provider. Returns a dict:
        {"action": "ok",   "text": str, "model": str}
        {"action": "next", "reason": str}
        {"action": "stop", "reason": str}
    Never raises for network/HTTP issues — those become 'next'/'stop'.
    """
    spec = PROVIDERS[name]
    key = os.environ.get(spec["key_env"], "").strip()
    if not key:
        return {"action": "next", "reason": "no API key set"}

    url = spec["base_url"] + "/chat/completions"
    payload = json.dumps({
        "model": model_for(name),
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", "Bearer " + key)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        text = body["choices"][0]["message"]["content"]
        return {"action": "ok", "text": text, "model": model_for(name)}
    except urllib.error.HTTPError as e:
        action = _classify(e.code)
        return {"action": action, "reason": "HTTP %d" % e.code}
    except urllib.error.URLError as e:
        return {"action": "next", "reason": "network: %s" % e.reason}
    except (KeyError, IndexError, ValueError) as e:
        return {"action": "next", "reason": "bad response shape: %s" % e}
    except Exception as e:  # last-resort guard so the router never crashes
        return {"action": "next", "reason": "unexpected: %s" % e}


def route(prompt, system=None, force=None, dry_run=False, timeout=30):
    """
    Try providers in order until one succeeds. Returns a result dict with an
    'attempts' trail so callers can see exactly what happened.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    order = [force] if force else provider_order()
    attempts = []

    for name in order:
        if name not in PROVIDERS:
            attempts.append({"provider": name, "result": "unknown provider"})
            continue

        if dry_run:
            configured = has_key(name)
            attempts.append({
                "provider": name,
                "result": "would-call" if configured else "skip (no key)",
                "model": model_for(name),
            })
            if configured or force:
                return {
                    "ok": True, "provider": name, "model": model_for(name),
                    "text": "[dry-run] would ask %s (%s)" % (name, model_for(name)),
                    "attempts": attempts, "dry_run": True,
                }
            continue

        res = call_provider(name, messages, timeout=timeout)
        attempts.append({"provider": name, "result": res["action"],
                         "reason": res.get("reason", "")})

        if res["action"] == "ok":
            return {"ok": True, "provider": name, "model": res["model"],
                    "text": res["text"], "attempts": attempts}
        if res["action"] == "stop":
            return {"ok": False, "error": "malformed_request",
                    "detail": res.get("reason", ""), "attempts": attempts,
                    "exit": 3}
        # 'next' — keep going, small backoff between providers
        time.sleep(0.2)

    return {"ok": False, "error": "all_providers_failed",
            "detail": "no provider succeeded (check keys/quota)",
            "attempts": attempts, "exit": 2}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Alfred LLM router with free-tier provider fallback.")
    parser.add_argument("prompt", nargs="?", help="the user prompt")
    parser.add_argument("--system", help="optional system prompt")
    parser.add_argument("--provider", choices=list(PROVIDERS),
                        help="force a single provider")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    parser.add_argument("--dry-run", action="store_true",
                        help="no network calls; show the routing plan")
    parser.add_argument("--timeout", type=int, default=30,
                        help="per-provider timeout in seconds (default 30)")
    parser.add_argument("--list", action="store_true",
                        help="list configured providers and exit")
    args = parser.parse_args(argv)

    if args.list:
        out = [{"provider": n, "configured": has_key(n), "model": model_for(n)}
               for n in provider_order()]
        print(json.dumps({"providers": out}, ensure_ascii=False, indent=2))
        return 0

    if not args.prompt:
        parser.error("a prompt is required (or use --list)")

    result = route(args.prompt, system=args.system, force=args.provider,
                   dry_run=args.dry_run, timeout=args.timeout)

    if args.json:
        printable = {k: v for k, v in result.items() if k != "exit"}
        print(json.dumps(printable, ensure_ascii=False, indent=2))
    else:
        if result["ok"]:
            print(result["text"])
        else:
            # problem + cause + fix (per DX convention X2)
            sys.stderr.write(
                "Alfred router failed: %s\n  cause: %s\n"
                "  fix: check that at least one provider key is set in .env "
                "and within its free-tier quota.\n"
                % (result["error"], result.get("detail", "")))

    return 0 if result["ok"] else result.get("exit", 2)


if __name__ == "__main__":
    sys.exit(main())
