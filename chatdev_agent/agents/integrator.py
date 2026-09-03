"""DevOps Release Engineer role for the agent cluster."""

from __future__ import annotations

from collections.abc import Callable


class IntegratorAgent:
    def __init__(self, llm: Callable[[str], str]) -> None:
        self._llm = llm

    def run(self, code_files: str) -> str:
        return self._llm(
            "You are a DevOps Release Engineer. "
            "Task 1: Output a 'requirements.txt' file. "
            "RULES: "
            "- Read the code imports. "
            "- Output ONLY the library names. "
            "- If no external libraries are used, output NOTHING. "
            "- DO NOT include comments or formatting.\n\n"
            "Task 2: Output a 'README.md'. "
            "RULES: "
            "- Include 'Installation' and 'Run' sections.\n\n"
            f"Code Context:\n{code_files}"
        )
