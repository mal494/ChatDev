"""One-shot command-line entry point for the ChatDev agent demo."""

from __future__ import annotations

import argparse
import sys

from agents.planner import PlannerAgent
from agents.coder import CoderAgent
from config import BackendConfigurationError, log, make_llm
from core.bus import MessageBus


def build_cluster() -> MessageBus:
    """Create the small planner-to-coder agent pipeline."""
    llm = make_llm()
    bus = MessageBus({"planner": PlannerAgent(llm), "coder": CoderAgent(llm)})
    log("Cluster initialized.")
    return bus


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a compact ChatDev planner/coder demonstration."
    )
    parser.add_argument("task", help="The development task for the agent cluster.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = build_cluster().run(args.task)
    except BackendConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    print(f"Task: {result.task}\n\nPlan:\n{result.plan}\n\nImplementation:\n{result.implementation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
