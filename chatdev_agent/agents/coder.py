"""Implementation role for the standalone agent cluster."""

from collections.abc import Callable


class CoderAgent:
    def __init__(self, llm: Callable[[str], str]) -> None:
        self._llm = llm

    def run(self, task: str, plan: str) -> str:
        return self._llm(
            "You are the coding agent. Produce a concise implementation response "
            "that follows this plan.\n\n"
            f"Task:\n{task}\n\nPlan:\n{plan}"
        )
