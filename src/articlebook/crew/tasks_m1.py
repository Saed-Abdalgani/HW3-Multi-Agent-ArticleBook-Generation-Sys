"""CrewAI tasks for milestone M1 (full stack)."""

from __future__ import annotations

from crewai import Agent, Task

# LLM tool-calling: always name tools and required parameters explicitly (M6 contract).
_WS = (
    "Use **write_workspace_file** with **both** required string arguments: **relative_path** "
    "(repo-relative path) and **content** (full UTF-8 body). Omitting either fails validation."
)


def build_m1_tasks(agents: dict[str, Agent], topic: str, language: str) -> list[Task]:
    """Return tasks wired in pipeline order with shared kickoff inputs."""
    shared = f"Topic: {topic}\nLanguage: {language}\n"

    research = Task(
        description=shared
        + "Skim `prd.md` via read_workspace_file, then "
        + _WS
        + " Save **relative_path** `content/m1_research_notes.md` with **content** summarizing "
        "scope, risks, and 3 placeholder BibTeX keys aligned to research-methodology.",
        expected_output="Confirmation that m1_research_notes.md exists with YAML-ish headings.",
        agent=agents["research"],
    )
    outline = Task(
        description=shared
        + "Using the research notes context, "
        + _WS
        + " Save **relative_path** `content/m1_outline.md` with **content** containing chapter "
        "titles, page bands, explicit BiDi chapter flag, and asset hooks per document-structure.",
        expected_output="Outline markdown saved at content/m1_outline.md.",
        agent=agents["architect"],
        context=[research],
    )
    writing = Task(
        description=shared
        + "From the outline, "
        + _WS
        + " Save **relative_path** `content/m1_chapter_draft.md` with **content** containing two "
        "short sections and HTML/Markdown anchors for figures, tables, and equations per "
        "technical-writing and bidi-hebrew skills.",
        expected_output="Draft markdown saved at content/m1_chapter_draft.md.",
        agent=agents["writer"],
        context=[outline],
    )
    figures = Task(
        description=shared
        + "Call **run_matplotlib_stub** (optional **reason** string as the only argument). "
        + _WS
        + " Save **relative_path** `figures/m1_manifest.txt` with **content** listing outputs "
        "and intended final filenames (diagram/image/graph/table/equation placeholders).",
        expected_output="Stub graph executed and manifest written under figures/.",
        agent=agents["figure"],
        context=[writing],
    )
    latex = Task(
        description=shared
        + _WS
        + " Save **relative_path** `latex/chapters/m1_stub_chapter.tex` with **content** that "
        "inputs the chapter narrative as commented text plus includegraphics placeholders "
        "referencing `../figures/m1_stub_graph.pdf`.",
        expected_output="TeX stub saved under latex/chapters/.",
        agent=agents["latex"],
        context=[figures],
    )
    compile_ = Task(
        description=shared
        + "Call **run_lualatex_once** with **reason** (first argument, e.g. `m1_smoke`) and "
        "**log_filename** (second argument) exactly `m1_lualatex_once.log`. "
        "Then read `build/m1_lualatex_once.log` via read_workspace_file if present and "
        "summarize errors/warnings in plain language.",
        expected_output="LuaLaTeX smoke pass executed with log captured.",
        agent=agents["compile"],
        context=[latex],
    )
    qa = Task(
        description=shared
        + "Read prior artifacts (notes, outline, draft, manifest, tex stub, LaTeX log). "
        + _WS
        + " Save **relative_path** `build/m1_qa_report.md` with **content** containing a "
        "checklist table: item, status, evidence path.",
        expected_output="QA markdown saved at build/m1_qa_report.md.",
        agent=agents["qa"],
        context=[compile_],
    )
    return [research, outline, writing, figures, latex, compile_, qa]
