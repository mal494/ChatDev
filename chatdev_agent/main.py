"""Command-line entry point for ChatDev agent demonstration and orchestration."""

from __future__ import annotations

import argparse
import sys

# Configure UTF-8 stdout if available to prevent Windows cp1252 charmap errors
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from pathlib import Path

# Ensure chatdev_agent and project root directories are in sys.path
_CURRENT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CURRENT_DIR.parent
for _path in [str(_CURRENT_DIR), str(_PROJECT_ROOT)]:
    if _path not in sys.path:
        sys.path.insert(0, _path)

from admin_boss import run_admin_diagnosis
from agents.coder import CoderAgent
from agents.planner import PlannerAgent
from config import BackendConfigurationError, log, make_llm
from core.bus import MessageBus
from orchestrator import Orchestrator


def build_cluster() -> MessageBus:
    """Create the small planner-to-coder agent pipeline."""
    llm = make_llm()
    bus = MessageBus({"planner": PlannerAgent(llm), "coder": CoderAgent(llm)})
    log("Cluster initialized.")
    return bus


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run ChatDev agent orchestration, full workforce cycles, or diagnostics."
    )
    parser.add_argument(
        "task",
        nargs="?",
        default=None,
        help="The development task for the agent cluster.",
    )
    parser.add_argument(
        "--diagnose",
        "--admin",
        action="store_true",
        help="Run Admin Boss system diagnostics.",
    )
    parser.add_argument(
        "--mode",
        choices=["compact", "full"],
        default="compact",
        help="Execution mode: 'compact' (planner + coder) or 'full' (complete workforce cycle).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.diagnose:
        print("========================================")
        print("   ADMIN BOSS - SYSTEM DIAGNOSTICS      ")
        print("========================================")
        report = run_admin_diagnosis()
        print("\n[+] ADMIN REPORT:\n" + "-" * 60)
        print(report)
        print("-" * 60)
        return 0

    if not args.task:
        print("Error: task argument is required when not running --diagnose.", file=sys.stderr)
        return 1

    try:
        if args.mode == "full":
            orchestrator = Orchestrator(llm=make_llm())
            result = orchestrator.run_full_cycle(args.task)
            print(f"Task: {result['task']}\nOutput Directory: {result['output_dir']}\nFiles Created: {result['files']}")
            return 0

        result = build_cluster().run(args.task)
    except BackendConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    print(f"Task: {result.task}\n\nPlan:\n{result.plan}\n\nImplementation:\n{result.implementation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
