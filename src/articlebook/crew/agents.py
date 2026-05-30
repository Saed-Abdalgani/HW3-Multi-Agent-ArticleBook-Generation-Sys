"""CrewAI agent definitions for milestone M1."""

from __future__ import annotations

from crewai import LLM, Agent

from articlebook.crew.workspace_tools import (
    read_workspace_file,
    run_lualatex_once,
    run_matplotlib_stub,
    write_workspace_file,
)
from articlebook.shared.paths import skills_root


def _skill(folder: str) -> str:
    return str(skills_root() / folder)


def build_agents(llm: LLM) -> dict[str, Agent]:
    """Create ordered agents for the M1 pipeline (skills + sandboxed tools)."""
    read_write = [write_workspace_file, read_workspace_file]
    all_tools = read_write + [run_matplotlib_stub, run_lualatex_once]
    compile_tools = [run_lualatex_once, read_workspace_file]

    return {
        "research": Agent(
            role="Research librarian",
            goal="Capture credible seed sources and constraints for the run topic.",
            backstory="You distrust uncited claims and prefer internal PRD/plan anchors.",
            tools=read_write,
            llm=llm,
            skills=[_skill("research-methodology")],
            verbose=True,
        ),
        "architect": Agent(
            role="Outline architect",
            goal="Produce a chapter skeleton with page bands and asset hooks.",
            backstory="You translate fuzzy briefs into reviewable outlines.",
            tools=read_write,
            llm=llm,
            skills=[_skill("document-structure")],
            verbose=True,
        ),
        "writer": Agent(
            role="Markdown writer",
            goal="Draft placeholder chapter text with anchors for assets and citations.",
            backstory="You pair structure skills with BiDi-aware drafting when Hebrew appears.",
            tools=read_write,
            llm=llm,
            skills=[_skill("technical-writing"), _skill("bidi-hebrew")],
            verbose=True,
        ),
        "figure": Agent(
            role="Figure and graph specialist",
            goal="Execute the whitelisted Matplotlib stub and record figure metadata.",
            backstory="You never execute arbitrary Python—only the approved stub script.",
            tools=all_tools,
            llm=llm,
            skills=[_skill("figure-generation")],
            verbose=True,
        ),
        "latex": Agent(
            role="LaTeX builder",
            goal="Emit a minimal chapter stub referencing assets under figures/.",
            backstory="You translate Markdown anchors to TeX inputs without losing labels.",
            tools=read_write,
            llm=llm,
            skills=[_skill("latex-authoring")],
            verbose=True,
        ),
        "compile": Agent(
            role="Compilation operator",
            goal="Run a single LuaLaTeX smoke pass and capture logs under build/.",
            backstory="You treat logs as first-class artifacts for downstream QA.",
            tools=compile_tools,
            llm=llm,
            verbose=True,
        ),
        "qa": Agent(
            role="QA reviewer",
            goal="Summarize artifact coverage and log health for milestone M1.",
            backstory="You enforce the FR-20 checklist at placeholder depth.",
            tools=read_write,
            llm=llm,
            skills=[_skill("qa-checklist")],
            verbose=True,
        ),
    }
