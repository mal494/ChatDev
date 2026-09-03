"""Deterministic planner-to-coder and multi-agent message routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


class Planner(Protocol):
    def run(self, task: str) -> str: ...


class Coder(Protocol):
    def run(self, task: str, plan: str) -> str: ...


@dataclass(frozen=True)
class WorkflowResult:
    task: str
    plan: str
    implementation: str
    metadata: dict[str, Any] | None = None


class MessageBus:
    """Run the planner first and pass its output to the coder, supporting extended agents."""

    def __init__(self, agents: Mapping[str, object]) -> None:
        try:
            self._planner: Planner = agents["planner"]  # type: ignore[assignment]
            self._coder: Coder = agents["coder"]  # type: ignore[assignment]
        except KeyError as exc:
            raise ValueError("MessageBus requires 'planner' and 'coder' agents.") from exc
        self._agents: dict[str, object] = dict(agents)

    def run(self, task: str) -> WorkflowResult:
        plan = self._planner.run(task)
        implementation = self._coder.run(task, plan)
        return WorkflowResult(task=task, plan=plan, implementation=implementation)

    def get_agent(self, name: str) -> object | None:
        return self._agents.get(name)
