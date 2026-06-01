"""Map milestone codes to ordered agent keys and task builder callables."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from crewai import Agent, Task

from articlebook.crew.tasks import (
    build_m1_tasks,
    build_m2_tasks,
    build_m3_tasks,
    build_m4_tasks,
    build_m5_tasks,
    build_m6_tasks,
)

Milestone = Literal["m1", "m2", "m3", "m4", "m5", "m6"]

_AGENT_ORDER_FULL = (
    "research",
    "architect",
    "writer",
    "figure",
    "latex",
    "compile",
    "qa",
)
_AGENT_ORDER_M3 = ("research", "architect", "writer", "figure", "qa")
_AGENT_ORDER_M2 = ("research", "architect", "writer", "qa")


def milestone_plan(
    milestone: Milestone,
) -> tuple[tuple[str, ...], Callable[[dict[str, Agent], str, str], list[Task]]]:
    """Return (ordered agent dict keys, task list builder)."""
    if milestone == "m1":
        return _AGENT_ORDER_FULL, build_m1_tasks
    if milestone == "m5":
        return _AGENT_ORDER_FULL, build_m5_tasks
    if milestone == "m6":
        return _AGENT_ORDER_FULL, build_m6_tasks
    if milestone == "m4":
        return _AGENT_ORDER_FULL, build_m4_tasks
    if milestone == "m3":
        return _AGENT_ORDER_M3, build_m3_tasks
    return _AGENT_ORDER_M2, build_m2_tasks


def ordered_agents(agents: dict[str, Agent], keys: tuple[str, ...]) -> list[Agent]:
    return [agents[k] for k in keys]
