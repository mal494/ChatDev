"""QA Engineer role for the agent cluster."""

from __future__ import annotations

from collections.abc import Callable


class QAAgent:
    def __init__(self, llm: Callable[[str], str]) -> None:
        self._llm = llm

    def run(self, filepath: str, code: str, error_message: str = "") -> str:
        return self._llm(
            "You are a QA Engineer. "
            "Run the code. If it fails, fix it. "
            "If it passes, say 'PASS' and nothing else.\n\n"
            f"File: {filepath}\nCode:\n{code}\nErrors:\n{error_message}"
        )
