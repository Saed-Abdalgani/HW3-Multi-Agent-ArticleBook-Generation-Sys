"""Assemble the milestone M1 crew (sequential process + shared skills)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from crewai import LLM, Crew, Process

from articlebook.crew.agents import build_agents
from articlebook.crew.tasks import build_m1_tasks
from articlebook.shared.paths import skills_root


def build_m1_crew(
    llm: LLM,
    topic: str,
    language: str,
    *,
    task_callback: Callable[[Any], None] | None = None,
) -> Crew:
    """Create the sequential crew with crew-level house culture plus per-agent skills."""
    agents = build_agents(llm)
    tasks = build_m1_tasks(agents, topic, language)
    ordered_agents = [
        agents["research"],
        agents["architect"],
        agents["writer"],
        agents["figure"],
        agents["latex"],
        agents["compile"],
        agents["qa"],
    ]
    payload: dict[str, object] = {
        "agents": ordered_agents,
        "tasks": tasks,
        "process": Process.sequential,
        "verbose": True,
        "memory": False,
        "skills": [str(skills_root() / "house-culture")],
    }
    if task_callback is not None:
        payload["task_callback"] = task_callback
    return Crew(**payload)
