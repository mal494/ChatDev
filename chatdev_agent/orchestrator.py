"""Orchestrator: Coordinates multi-agent workforce and executes diagnostics and builds."""

from __future__ import annotations

import json
import os
import sys
import time
from collections.abc import Callable
from typing import Any

import requests

from agent import Agent
from config import BASE_DIR, LOGS_DIR, REPO_PATH, log, make_llm
from utils import (
    extract_code_block,
    extract_json_safe,
    log_event,
    read_file,
    run_python_script,
    save_file,
)


class Orchestrator:
    """Coordinates the AI workforce for end-to-end software development and diagnosis."""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        llm: Callable[[str], str] | None = None,
    ) -> None:
        self.config = config or {}
        self.llm = llm
        self.base_dir = self.config.get("base_dir", BASE_DIR)
        self.logs_dir = self.config.get("logs_dir", LOGS_DIR)

        # Initialize the AI Workforce
        self.pm = Agent("manager", self.config, llm=self.llm)
        self.arch = Agent("architect", self.config, llm=self.llm)
        self.dev = Agent("developer", self.config, llm=self.llm)
        self.executor = Agent("executor", self.config, llm=self.llm)
        self.tester = Agent("tester", self.config, llm=self.llm)
        self.qa = Agent("qa", self.config, llm=self.llm)
        self.integrator = Agent("integrator", self.config, llm=self.llm)
        self.admin = Agent("admin", self.config, llm=self.llm)

    def log(self, message: str, source: str = "SYSTEM") -> None:
        log_event(f"[{source}] {message}", "INFO")

    def wait_for_brain(self, max_retries: int = 2, retry_delay: float = 0.5) -> bool:
        """Polls the AI server health endpoint."""
        api_base = self.pm.api_base
        base_url = api_base.replace("/v1", "").replace("/chat/completions", "")
        health_url = base_url.rstrip("/") + "/health"

        for _ in range(max_retries):
            try:
                response = requests.get(health_url, timeout=1)
                if response.status_code == 200:
                    return True
            except Exception:
                pass
            time.sleep(retry_delay)
        return False

    def _collect_log_snippets(self, limit: int = 5, max_chars: int = 2000) -> str:
        """Read recent log files and format tail snippets."""
        if not os.path.exists(self.logs_dir):
            return "No logs directory found."

        log_files = [
            os.path.join(self.logs_dir, f)
            for f in os.listdir(self.logs_dir)
            if f.lower().endswith((".txt", ".log"))
        ]
        if not log_files:
            return "No logs found."

        log_files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        snippets: list[str] = []
        for path in log_files[:limit]:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()[-max_chars:]
                snippets.append(f"--- {os.path.basename(path)} ---\n{content}")
            except Exception as e:
                snippets.append(f"--- {os.path.basename(path)} ---\nError reading log: {e}")

        return "\n\n".join(snippets)

    def admin_diagnose(self) -> str:
        """Diagnose agent health by analyzing logs and system health."""
        brain_ok = self.wait_for_brain()
        log_snippets = self._collect_log_snippets()

        context = f"""
Brain health: {'OK' if brain_ok else 'UNRESPONSIVE'}
Recent Logs:
{log_snippets}
"""
        prompt = "Diagnose failing agents and recommend fixes."
        report = self.admin.think(prompt, context=context)

        # If HTTP failed and offline mode did not produce a report, supply clear fallback
        if not report or report.startswith("ERROR"):
            return (
                "Admin diagnostic fallback:\n"
                "1) Detected failures or risks: AI server unreachable; agents cannot call /v1/chat/completions.\n"
                "2) Likely root causes: local model server not running, still loading, or port blocked.\n"
                "3) Recommended actions: start local model server, verify CHATDEV_BACKEND configuration, check logs.\n\n"
                f"Recent Logs:\n{log_snippets}"
            )
        return report

    def run_qa_check(self, filepath: str, code_content: str) -> bool:
        """Runs the code. If it fails, asks Developer to fix it."""
        self.log(f"Running QA on {os.path.basename(filepath)}...", "QA_AGENT")
        result = run_python_script(filepath)

        if result["success"]:
            self.log("PASS. Code executed successfully.", "QA_AGENT")
            return True

        self.log(f"FAILED. Error: {result['stderr'][:200]}...", "QA_AGENT")
        self.log("Requesting hot-fix from Developer...", "QA_AGENT")

        fix_prompt = f"""
The code you wrote for '{os.path.basename(filepath)}' failed to run.
ERROR MESSAGE:
{result['stderr']}
ORIGINAL CODE:
{code_content}
Fix the error and output the FULL, CORRECTED code block.
"""
        fixed_code_text = self.dev.think(fix_prompt, context="Fixing execution error")
        clean_fixed_code = extract_code_block(fixed_code_text)
        if clean_fixed_code:
            save_file(filepath, clean_fixed_code)
            self.log(f"Applied fix to {os.path.basename(filepath)}.", "QA_AGENT")
        return False

    def run_full_cycle(self, task: str, target_dir: str | None = None) -> dict[str, Any]:
        """Execute the full product development workflow: PM -> Arch -> Dev -> QA -> Integrator."""
        out_dir = target_dir or os.path.join(REPO_PATH, "generated_app")
        os.makedirs(out_dir, exist_ok=True)

        self.log(f"Starting full development cycle for: {task}", "ORCHESTRATOR")

        # 1. Product Manager generates requirements
        reqs = self.pm.think(f"Generate requirements for: {task}")
        save_file(os.path.join(out_dir, "requirements.md"), reqs)

        # 2. Architect designs project structure
        arch_output = self.arch.think(
            "Design file structure in JSON mapping filenames to instructions.",
            context=reqs,
        )
        file_map = extract_json_safe(arch_output)
        if not file_map or not isinstance(file_map, dict):
            file_map = {"src/main.py": f"Main CLI application for: {task}"}

        # 3. Developer implements each file
        created_files: list[str] = []
        for rel_path, instructions in file_map.items():
            dest_file = os.path.join(out_dir, rel_path)
            code_response = self.dev.think(
                f"Write code for {rel_path}: {instructions}",
                context=reqs,
            )
            clean_code = extract_code_block(code_response)
            if not clean_code:
                clean_code = f'# Code for {rel_path}\nprint("Running {task}")\n'
            save_file(dest_file, clean_code)
            created_files.append(dest_file)

        # 4. QA check on entry point
        entry_point = os.path.join(out_dir, "src", "main.py")
        if os.path.exists(entry_point):
            content = read_file(entry_point) or ""
            self.run_qa_check(entry_point, content)

        # 5. Integrator generates requirements.txt and README.md
        context_files = "\n".join(
            f"File: {f}\n{read_file(f)}" for f in created_files[:3]
        )
        reqs_txt = self.integrator.think(
            "Output requirements.txt with only external dependencies.",
            context=context_files,
        )
        save_file(os.path.join(out_dir, "requirements.txt"), reqs_txt.strip())

        readme_md = self.integrator.think(
            "Output README.md with Installation and Run instructions.",
            context=f"Task: {task}\nFiles: {list(file_map.keys())}",
        )
        save_file(os.path.join(out_dir, "README.md"), readme_md)

        self.log("Workflow completed successfully.", "ORCHESTRATOR")
        return {
            "task": task,
            "output_dir": out_dir,
            "files": list(file_map.keys()),
            "requirements": reqs,
        }
