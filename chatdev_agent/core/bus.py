"""Deterministic planner-to-coder message routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol


class Planner(Protocol):
    def run(self, task: str) -> str: ...


class Coder(Protocol):
    def run(self, task: str, plan: str) -> str: ...


@dataclass(frozen=True)
class WorkflowResult:
    task: str
    plan: str
    implementation: str


class MessageBus:
    """Run the planner first and pass its output to the coder."""

    def __init__(self, agents: Mapping[str, object]) -> None:
        try:
            self._planner: Planner = agents["planner"]  # type: ignore[assignment]
            self._coder: Coder = agents["coder"]  # type: ignore[assignment]
        except KeyError as exc:
            raise ValueError("MessageBus requires 'planner' and 'coder' agents.") from exc

    def run(self, task: str) -> WorkflowResult:
        plan = self._planner.run(task)
        implementation = self._coder.run(task, plan)
        return WorkflowResult(task=task, plan=plan, implementation=implementation)
