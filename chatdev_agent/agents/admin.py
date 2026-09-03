"""Admin Boss role for failure analysis and system health diagnostics."""

from __future__ import annotations

from collections.abc import Callable


class AdminAgent:
    def __init__(self, llm: Callable[[str], str]) -> None:
        self._llm = llm

    def run(self, health_status: str, log_snippets: str) -> str:
        return self._llm(
            "You are the Admin Boss Agent. Your job is to monitor other agents and diagnose failures. "
            "Analyze logs, recent errors, and system health signals. Return a concise report with:\n"
            "1) Detected failures or risks,\n"
            "2) Likely root causes,\n"
            "3) Recommended actions.\n\n"
            f"Brain health: {health_status}\nRecent Logs:\n{log_snippets}"
        )
