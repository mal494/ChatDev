"""Software Tester role for the agent cluster."""

from __future__ import annotations

from collections.abc import Callable


class TesterAgent:
    def __init__(self, llm: Callable[[str], str]) -> None:
        self._llm = llm

    def run(self, code_or_filepath: str, test_output: str = "") -> str:
        return self._llm(
            "You are a Software Tester. "
            "Your sole responsibility is to run the built software and judge if it works. "
            "Return PASS or FAIL with a short reason.\n\n"
            f"Target: {code_or_filepath}\nExecution Output:\n{test_output}"
        )
