"""CrewAI agent definitions for milestone M1."""

from __future__ import annotations

from crewai import LLM, Agent

from articlebook.crew.agent_factory import build_agent
from articlebook.crew.workspace_tools import (
    assemble_latex_document,
    read_workspace_file,
    run_latex_canonical_compile,
    run_lualatex_once,
    run_m3_asset_generators,
    run_m6_contract_checks,
    run_matplotlib_stub,
    verify_m3_assets,
    write_workspace_file,
    write_workspace_files_batch,
)
from articlebook.rag.wiring import optional_rag_research_tools


def build_agents(llm: LLM) -> dict[str, Agent]:
    """Create ordered agents for M1/M2/M3 pipelines (skills + sandboxed tools)."""
    read_write = [write_workspace_file, write_workspace_files_batch, read_workspace_file]
    research_tools = read_write + optional_rag_research_tools()
    figure_tools = read_write + [
        run_matplotlib_stub,
        run_m3_asset_generators,
        verify_m3_assets,
        run_lualatex_once,
    ]
    compile_tools = [run_lualatex_once, run_latex_canonical_compile, read_workspace_file]
    qa_tools = read_write + [verify_m3_assets, run_m6_contract_checks]
    return {
        "research": build_agent(
            llm,
            "research",
            role="Research librarian",
            goal="Capture credible seed sources and constraints for the run topic.",
            backstory="You distrust uncited claims and prefer internal PRD/plan anchors.",
            tools=research_tools,
            skills=["research-methodology"],
        ),
        "architect": build_agent(
            llm,
            "architect",
            role="Outline architect",
            goal="Produce a chapter skeleton with page bands and asset hooks.",
            backstory="You translate fuzzy briefs into reviewable outlines.",
            tools=read_write,
            skills=["document-structure"],
        ),
        "writer": build_agent(
            llm,
            "writer",
            role="Markdown writer",
            goal=(
                "Produce full-length technical chapters (750–1000 words each) with asset "
                "anchors and valid citation markers."
            ),
            backstory=(
                "You write substantive prose—not meta-intros or stubs—and you pair structure "
                "skills with BiDi-aware drafting when Hebrew appears."
            ),
            tools=read_write,
            skills=["technical-writing", "bidi-hebrew"],
        ),
        "figure": build_agent(
            llm,
            "figure",
            role="Figure and graph specialist",
            goal="Execute whitelisted Matplotlib scripts and record figure metadata.",
            backstory=(
                "You never execute arbitrary Python—only approved scripts under scripts/: "
                "plot_stub_m1.py (M1), make_graph.py + make_image.py (M3). "
                "After generation you confirm binaries via verify_m3_assets before handing off."
            ),
            tools=figure_tools,
            skills=["figure-generation"],
        ),
        "latex": build_agent(
            llm,
            "latex",
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
            skills=["latex-authoring"],
        ),
        "compile": build_agent(
            llm,
            "compile",
            role="Compilation operator",
            goal=(
                "Run single-pass smoke when requested; otherwise execute the canonical "
                "LuaLaTeX/XeLaTeX + biber multipass driver and capture logs under build/."
            ),
            backstory=(
                "You treat logs as first-class artifacts: per-pass files plus a compile journal "
                "JSON for QA (M5)."
            ),
            tools=compile_tools,
            skills=["compilation"],
        ),
        "qa": build_agent(
            llm,
            "qa",
            role="QA reviewer",
            goal=(
                "Summarize artifact coverage, compile health, "
                "and M6 deterministic contract results."
            ),
            backstory=(
                "You enforce the FR-20 checklist; for M3 call verify_m3_assets; "
                "for M6 call run_m6_contract_checks after canonical compile."
            ),
            tools=qa_tools,
            skills=["qa-checklist"],
        ),
    }
