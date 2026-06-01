"""Factory helpers for building :class:`crewai.Agent` instances with YAML overlays."""

from __future__ import annotations

from crewai import LLM, Agent

from articlebook.crew.agent_overrides import merge_agent_fields
from articlebook.shared.paths import skills_root


def skill_path(folder: str) -> str:
    return str(skills_root() / folder)


def build_agent(
    llm: LLM,
    agent_id: str,
    *,
    tools: list,
    skills: list[str] | None = None,
    role: str,
    goal: str,
    backstory: str,
) -> Agent:
    base: dict = {
        "role": role,
        "goal": goal,
        "backstory": backstory,
        "tools": tools,
        "verbose": True,
    }
    if skills is not None:
        base["skills"] = list(skills)
    merged = merge_agent_fields(agent_id, base)
    skill_names = merged.pop("skills", None)
    resolved_skills = (
        [skill_path(str(name)) for name in skill_names] if isinstance(skill_names, list) else None
    )
    return Agent(
        llm=llm,
        role=str(merged["role"]),
        goal=str(merged["goal"]),
        backstory=str(merged["backstory"]),
        tools=merged["tools"],
        verbose=bool(merged.get("verbose", True)),
        skills=resolved_skills,
    )
