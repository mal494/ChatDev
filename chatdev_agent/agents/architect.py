"""Software Architect role for the agent cluster."""

from __future__ import annotations

from collections.abc import Callable


class ArchitectAgent:
    def __init__(self, llm: Callable[[str], str]) -> None:
        self._llm = llm

    def run(self, task: str, requirements: str = "") -> str:
        return self._llm(
            "You are a Senior Software Architect. "
            "Task: Design the file structure for a Python project. "
            "Output ONLY a JSON object mapping filenames to instructions.\n\n"
            f"Task:\n{task}\n\nRequirements:\n{requirements}"
        )
