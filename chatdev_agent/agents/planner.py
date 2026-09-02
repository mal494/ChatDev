"""Planning role for the standalone agent cluster."""

from collections.abc import Callable


class PlannerAgent:
    def __init__(self, llm: Callable[[str], str]) -> None:
        self._llm = llm

    def run(self, task: str) -> str:
        return self._llm(
            "You are the planning agent. Create a concise implementation plan "
            "with three practical steps.\n\nTask:\n"
            f"{task}"
        )
