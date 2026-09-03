"""Expert Python Developer role for the agent cluster."""

from __future__ import annotations

from collections.abc import Callable


class DeveloperAgent:
    def __init__(self, llm: Callable[[str], str]) -> None:
        self._llm = llm

    def run(self, filename: str, instruction: str, context: str = "") -> str:
        return self._llm(
            "You are an Expert Python Developer. "
            "Write the code for the requested file. "
            "Output ONLY the code block. Do not converse.\n\n"
            f"File: {filename}\nInstruction: {instruction}\nContext:\n{context}"
        )
