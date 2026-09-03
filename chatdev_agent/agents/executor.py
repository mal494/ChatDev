"""Execution & Implementation Engineer role for the agent cluster."""

from __future__ import annotations

from collections.abc import Callable


class ExecutorAgent:
    def __init__(self, llm: Callable[[str], str]) -> None:
        self._llm = llm

    def run(self, plan: str, instruction: str) -> str:
        return self._llm(
            "You are an Execution & Implementation Engineer. "
            "ONLY implement the provided plan or file instructions. "
            "Do not change requirements or architecture. "
            "Output ONLY the code block, with no commentary.\n\n"
            f"Plan:\n{plan}\n\nInstruction:\n{instruction}"
        )
