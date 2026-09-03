"""Unit tests for the workforce roles, portable config, and admin diagnostics."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure offline deterministic mode for testing
os.environ["CHATDEV_BACKEND"] = "offline"

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT))

from admin_boss import run_admin_diagnosis
from agent import Agent
from agents import (
    AdminAgent,
    ArchitectAgent,
    CoderAgent,
    DeveloperAgent,
    ExecutorAgent,
    IntegratorAgent,
    ManagerAgent,
    PlannerAgent,
    QAAgent,
    TesterAgent,
)
import config
from orchestrator import Orchestrator
from utils import extract_code_block, extract_json_safe


class ConfigAndThemeTests(unittest.TestCase):
    def test_theme_constants_defined(self) -> None:
        self.assertEqual(config.GREEN_CODE, "#00FF41")
        self.assertEqual(config.BG_COLOR, "#0D0D0D")
        self.assertEqual(config.TERMINAL_FONT, ("Courier New", 12))

    def test_portable_paths_created(self) -> None:
        self.assertTrue(os.path.exists(config.BASE_DIR))
        self.assertTrue(config.REPO_PATH.startswith(config.BASE_DIR))
        self.assertTrue(config.MEMORY_FILE.startswith(config.BASE_DIR))

    def test_workforce_prompts_present(self) -> None:
        expected_roles = [
            "manager",
            "architect",
            "developer",
            "executor",
            "tester",
            "qa",
            "integrator",
            "admin",
        ]
        for role in expected_roles:
            self.assertIn(role, config.ROLE_SYSTEM_PROMPTS)


class WorkforceAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.llm = config._offline_llm

    def test_manager_agent(self) -> None:
        agent = ManagerAgent(self.llm)
        out = agent.run("Build a weather app")
        self.assertIn("Requirements", out)

    def test_architect_agent(self) -> None:
        agent = ArchitectAgent(self.llm)
        out = agent.run("Build a weather app")
        data = extract_json_safe(out)
        self.assertIsInstance(data, dict)
        self.assertIn("src/main.py", data)

    def test_developer_agent(self) -> None:
        agent = DeveloperAgent(self.llm)
        out = agent.run("src/main.py", "Create entry point")
        code = extract_code_block(out)
        self.assertTrue(len(code) > 0)

    def test_executor_agent(self) -> None:
        agent = ExecutorAgent(self.llm)
        out = agent.run("step 1", "do step 1")
        self.assertTrue(len(out) > 0)

    def test_tester_agent(self) -> None:
        agent = TesterAgent(self.llm)
        out = agent.run("src/main.py", "all good")
        self.assertIn("PASS", out)

    def test_qa_agent(self) -> None:
        agent = QAAgent(self.llm)
        out = agent.run("src/main.py", "print(1)")
        self.assertEqual(out, "PASS")

    def test_integrator_agent(self) -> None:
        agent = IntegratorAgent(self.llm)
        out = agent.run("import requests")
        self.assertTrue("requests" in out or len(out) > 0)

    def test_admin_agent(self) -> None:
        agent = AdminAgent(self.llm)
        out = agent.run("OK", "no errors")
        self.assertIn("Admin diagnostic", out)


class UnifiedAgentClassTests(unittest.TestCase):
    def test_agent_think_with_llm(self) -> None:
        agent = Agent("admin", llm=lambda p: "custom admin response")
        response = agent.think("diagnose this")
        self.assertEqual(response, "custom admin response")

    def test_agent_fallback_on_unreachable_api(self) -> None:
        # Invalid api_base should gracefully fallback to configured offline LLM
        agent = Agent("qa", config={"api_base": "http://127.0.0.1:9999/v1"})
        response = agent.think("check status")
        self.assertEqual(response, "PASS")


class OrchestratorAndAdminBossTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_admin_diagnose_executes(self) -> None:
        report = run_admin_diagnosis()
        self.assertTrue(len(report) > 0)
        self.assertTrue("Admin diagnostic" in report or "Detected failures" in report)

    def test_run_full_cycle(self) -> None:
        orch = Orchestrator(llm=config._offline_llm)
        result = orch.run_full_cycle("Simple Calculator", target_dir=self.temp_dir)
        self.assertEqual(result["task"], "Simple Calculator")
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "requirements.md")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "requirements.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "README.md")))
