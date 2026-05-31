"""Assemble milestone crews (M1 full stack, M2 content, M3 figures, M4 LaTeX assembly)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from crewai import LLM, Crew, Process

from articlebook.crew.agents import build_agents
from articlebook.crew.tasks import build_m1_tasks, build_m2_tasks, build_m3_tasks, build_m4_tasks
from articlebook.shared.paths import skills_root

Milestone = Literal["m1", "m2", "m3", "m4"]


def build_m1_crew(
    llm: LLM,
    topic: str,
    language: str,
    *,
    task_callback: Callable[[Any], None] | None = None,
) -> Crew:
    """Backward-compatible alias for the full M1 sequential crew."""
    return build_crew(llm, topic, language, milestone="m1", task_callback=task_callback)


def build_m2_crew(
    llm: LLM,
    topic: str,
    language: str,
    *,
    task_callback: Callable[[Any], None] | None = None,
) -> Crew:
    """M2 crew: research → outline → multi-chapter Markdown → QA (no compile)."""
    return build_crew(llm, topic, language, milestone="m2", task_callback=task_callback)


def build_m3_crew(
    llm: LLM,
    topic: str,
    language: str,
    *,
    task_callback: Callable[[Any], None] | None = None,
) -> Crew:
    """M3 crew: M2 pipeline + figure generators + extended QA (FR-9)."""
    return build_crew(llm, topic, language, milestone="m3", task_callback=task_callback)


def build_m4_crew(
    llm: LLM,
    topic: str,
    language: str,
    *,
    task_callback: Callable[[Any], None] | None = None,
) -> Crew:
    """M4 crew: M3 pipeline + LaTeX assembly + one compile + QA."""
    return build_crew(llm, topic, language, milestone="m4", task_callback=task_callback)


def build_crew(
    llm: LLM,
    topic: str,
    language: str,
    *,
    milestone: Milestone = "m2",
    task_callback: Callable[[Any], None] | None = None,
) -> Crew:
    """Create the sequential crew with crew-level house culture plus per-agent skills."""
    agents = build_agents(llm)
    if milestone == "m1":
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
    elif milestone == "m4":
        tasks = build_m4_tasks(agents, topic, language)
        ordered_agents = [
            agents["research"],
            agents["architect"],
            agents["writer"],
            agents["figure"],
            agents["latex"],
            agents["compile"],
            agents["qa"],
        ]
    elif milestone == "m3":
        tasks = build_m3_tasks(agents, topic, language)
        ordered_agents = [
            agents["research"],
            agents["architect"],
            agents["writer"],
            agents["figure"],
            agents["qa"],
        ]
    else:
        tasks = build_m2_tasks(agents, topic, language)
        ordered_agents = [
            agents["research"],
            agents["architect"],
            agents["writer"],
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
