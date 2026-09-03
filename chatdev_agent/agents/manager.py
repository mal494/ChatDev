"""Product Manager role for the agent cluster."""

from __future__ import annotations

from collections.abc import Callable


class ManagerAgent:
    def __init__(self, llm: Callable[[str], str]) -> None:
        self._llm = llm

    def run(self, task: str) -> str:
        return self._llm(
            "You are a Senior Product Manager. "
            "Break down the user request into a detailed 'requirements.md'. "
            "Output Markdown only.\n\n"
            f"Task:\n{task}"
        )
