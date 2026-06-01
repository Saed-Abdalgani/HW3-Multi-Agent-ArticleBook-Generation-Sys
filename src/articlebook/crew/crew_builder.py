"""Assemble milestone crews (M1 full stack, M2 content, M3 figures, M4 LaTeX assembly)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from crewai import LLM, Crew, Process

from articlebook.crew.agents import build_agents
from articlebook.crew.crew_milestone_dispatch import Milestone, milestone_plan, ordered_agents
from articlebook.shared.paths import skills_root

__all__ = [
    "Milestone",
    "build_m1_crew",
    "build_m2_crew",
    "build_m3_crew",
    "build_m4_crew",
    "build_m5_crew",
    "build_m6_crew",
    "build_crew",
]


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


def build_m5_crew(
    llm: LLM,
    topic: str,
    language: str,
    *,
    task_callback: Callable[[Any], None] | None = None,
) -> Crew:
    """M5 crew: M4 pipeline with canonical multipass compile + QA on compile journal."""
    return build_crew(llm, topic, language, milestone="m5", task_callback=task_callback)


def build_m6_crew(
    llm: LLM,
    topic: str,
    language: str,
    *,
    task_callback: Callable[[Any], None] | None = None,
) -> Crew:
    """M6 crew: M5 pipeline + ``run_m6_contract_checks`` after canonical compile."""
    return build_crew(llm, topic, language, milestone="m6", task_callback=task_callback)


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
    keys, build_tasks = milestone_plan(milestone)
    task_list = build_tasks(agents, topic, language)
    payload: dict[str, object] = {
        "agents": ordered_agents(agents, keys),
        "tasks": task_list,
        "process": Process.sequential,
        "verbose": True,
        "memory": False,
        "skills": [str(skills_root() / "house-culture")],
    }
    if task_callback is not None:
        payload["task_callback"] = task_callback
    return Crew(**payload)
