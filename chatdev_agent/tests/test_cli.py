"""Focused tests for the standalone agent demonstration."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT))

from config import BackendConfigurationError, make_llm
from core.bus import MessageBus


class RecordingPlanner:
    def __init__(self, events: list[tuple[str, str]]) -> None:
        self.events = events

    def run(self, task: str) -> str:
        self.events.append(("planner", task))
        return "the plan"


class RecordingCoder:
    def __init__(self, events: list[tuple[str, str, str]]) -> None:
        self.events = events

    def run(self, task: str, plan: str) -> str:
        self.events.append(("coder", task, plan))
        return "the implementation"


class ConfigTests(unittest.TestCase):
    def test_offline_is_default_and_needs_no_network(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            response = make_llm()("Create a concise implementation plan\n\nTask:\nDemo")
        self.assertIn("Demo", response)

    def test_invalid_backend_has_actionable_error(self) -> None:
        with patch.dict(os.environ, {"CHATDEV_BACKEND": "invalid"}, clear=True):
            with self.assertRaisesRegex(BackendConfigurationError, "Unsupported"):
                make_llm()


class MessageBusTests(unittest.TestCase):
    def test_planner_runs_before_coder_and_passes_its_plan(self) -> None:
        events: list[tuple[object, ...]] = []
        bus = MessageBus({"planner": RecordingPlanner(events), "coder": RecordingCoder(events)})

        result = bus.run("build a demo")

        self.assertEqual(events, [("planner", "build a demo"), ("coder", "build a demo", "the plan")])
        self.assertEqual(result.implementation, "the implementation")
