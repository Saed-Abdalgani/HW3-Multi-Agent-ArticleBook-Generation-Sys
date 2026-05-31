"""CrewAI agent definitions for milestone M1."""

from __future__ import annotations

from crewai import LLM, Agent

from articlebook.crew.workspace_tools import (
    assemble_latex_document,
    read_workspace_file,
    run_lualatex_once,
    run_m3_asset_generators,
    run_matplotlib_stub,
    verify_m3_assets,
    write_workspace_file,
)
from articlebook.shared.paths import skills_root


def _skill(folder: str) -> str:
    return str(skills_root() / folder)


def build_agents(llm: LLM) -> dict[str, Agent]:
    """Create ordered agents for M1/M2/M3 pipelines (skills + sandboxed tools)."""
    read_write = [write_workspace_file, read_workspace_file]
    figure_tools = read_write + [run_matplotlib_stub, run_m3_asset_generators, run_lualatex_once]
    compile_tools = [run_lualatex_once, read_workspace_file]
    qa_tools = read_write + [verify_m3_assets]

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
            goal="Execute whitelisted Matplotlib scripts and record figure metadata.",
            backstory=(
                "You never execute arbitrary Python—only approved scripts under scripts/: "
                "plot_stub_m1.py (M1), make_graph.py + make_image.py (M3)."
            ),
            tools=figure_tools,
            llm=llm,
            skills=[_skill("figure-generation")],
            verbose=True,
        ),
        "latex": Agent(
            role="LaTeX builder",
            goal=(
                "Convert Markdown to .tex, assemble main.tex, "
                "wire bibliography and preamble."
            ),
            backstory=(
                "You translate Markdown and anchors to compilable LaTeX "
                "using the assembly tool."
            ),
            tools=read_write + [assemble_latex_document],
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
            goal="Summarize artifact coverage and log health per milestone (M1/M2/M3).",
            backstory="You enforce the FR-20 checklist; for M3 you also call verify_m3_assets.",
            tools=qa_tools,
            llm=llm,
            skills=[_skill("qa-checklist")],
            verbose=True,
        ),
    }
