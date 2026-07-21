#!/usr/bin/env python3
"""
Tests for llm_router — stdlib unittest, provider calls are MOCKED.

Per plan Eng review E5: tests must never burn free-tier quota, so every network
path is stubbed. Run with:  python3 -m unittest discover -s alfred/tools/tests
or directly:  ./test_llm_router.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import llm_router  # noqa: E402


class RoutingLogicTest(unittest.TestCase):
    def setUp(self):
        # Clean provider env so tests are deterministic.
        for spec in llm_router.PROVIDERS.values():
            os.environ.pop(spec["key_env"], None)
        os.environ.pop("ALFRED_PROVIDER_ORDER", None)

    def test_classify(self):
        self.assertEqual(llm_router._classify(200), "ok")
        self.assertEqual(llm_router._classify(429), "next")
        self.assertEqual(llm_router._classify(503), "next")
        self.assertEqual(llm_router._classify(401), "next")
        self.assertEqual(llm_router._classify(400), "stop")

    def test_falls_back_to_second_provider(self):
        os.environ["GROQ_API_KEY"] = "x"
        os.environ["GEMINI_API_KEY"] = "y"

        def fake_call(name, messages, **kw):
            if name == "groq":
                return {"action": "next", "reason": "HTTP 429"}
            return {"action": "ok", "text": "hi from gemini", "model": "gemini-2.0-flash"}

        orig = llm_router.call_provider
        llm_router.call_provider = fake_call
        try:
            res = llm_router.route("hello")
        finally:
            llm_router.call_provider = orig

        self.assertTrue(res["ok"])
        self.assertEqual(res["provider"], "gemini")
        self.assertEqual(res["text"], "hi from gemini")

    def test_malformed_request_stops(self):
        os.environ["GROQ_API_KEY"] = "x"

        def fake_call(name, messages, **kw):
            return {"action": "stop", "reason": "HTTP 400"}

        orig = llm_router.call_provider
        llm_router.call_provider = fake_call
        try:
            res = llm_router.route("hello")
        finally:
            llm_router.call_provider = orig

        self.assertFalse(res["ok"])
        self.assertEqual(res["error"], "malformed_request")
        self.assertEqual(res["exit"], 3)

    def test_no_keys_fails_cleanly(self):
        res = llm_router.route("hello")
        self.assertFalse(res["ok"])
        self.assertEqual(res["error"], "all_providers_failed")
        self.assertEqual(res["exit"], 2)

    def test_dry_run_makes_no_call(self):
        os.environ["GROQ_API_KEY"] = "x"

        def boom(*a, **k):
            raise AssertionError("network call must not happen in dry-run")

        orig = llm_router.call_provider
        llm_router.call_provider = boom
        try:
            res = llm_router.route("hello", dry_run=True)
        finally:
            llm_router.call_provider = orig

        self.assertTrue(res["ok"])
        self.assertTrue(res["dry_run"])
        self.assertEqual(res["provider"], "groq")

    def test_provider_order_env_override(self):
        os.environ["ALFRED_PROVIDER_ORDER"] = "openrouter,groq"
        self.assertEqual(llm_router.provider_order(), ["openrouter", "groq"])


if __name__ == "__main__":
    unittest.main()
