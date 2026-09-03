"""Workforce roles for ChatDev agent orchestration."""

from agents.admin import AdminAgent
from agents.architect import ArchitectAgent
from agents.coder import CoderAgent
from agents.developer import DeveloperAgent
from agents.executor import ExecutorAgent
from agents.integrator import IntegratorAgent
from agents.manager import ManagerAgent
from agents.planner import PlannerAgent
from agents.qa import QAAgent
from agents.tester import TesterAgent

__all__ = [
    "AdminAgent",
    "ArchitectAgent",
    "CoderAgent",
    "DeveloperAgent",
    "ExecutorAgent",
    "IntegratorAgent",
    "ManagerAgent",
    "PlannerAgent",
    "QAAgent",
    "TesterAgent",
]
