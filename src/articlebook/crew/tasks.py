"""Sequential tasks for milestone M1 (artifacts + logging hooks)."""

from __future__ import annotations

from crewai import Agent, Task


def build_m1_tasks(agents: dict[str, Agent], topic: str, language: str) -> list[Task]:
    """Return tasks wired in pipeline order with shared kickoff inputs."""
    shared = f"Topic: {topic}\nLanguage: {language}\n"

    research = Task(
        description=shared
        + "Skim `prd.md` via read_workspace_file, then write `content/m1_research_notes.md` "
        "summarizing scope, risks, and 3 placeholder BibTeX keys aligned to research-methodology.",
        expected_output="Confirmation that m1_research_notes.md exists with YAML-ish headings.",
        agent=agents["research"],
    )
    outline = Task(
        description=shared
        + "Using the research notes context, write `content/m1_outline.md` with chapter titles, "
        "page bands, explicit BiDi chapter flag, and asset hooks per document-structure.",
        expected_output="Outline markdown saved at content/m1_outline.md.",
        agent=agents["architect"],
        context=[research],
    )
    writing = Task(
        description=shared
        + "From the outline, write `content/m1_chapter_draft.md` with two short sections and "
        "HTML/Markdown anchors for figures, tables, and equations per technical-writing and "
        "bidi-hebrew skills.",
        expected_output="Draft markdown saved at content/m1_chapter_draft.md.",
        agent=agents["writer"],
        context=[outline],
    )
    figures = Task(
        description=shared
        + "Call run_matplotlib_stub, then write `figures/m1_manifest.txt` listing outputs "
        "and intended final filenames (diagram/image/graph/table/equation placeholders).",
        expected_output="Stub graph executed and manifest written under figures/.",
        agent=agents["figure"],
        context=[writing],
    )
    latex = Task(
        description=shared
        + "Write `latex/chapters/m1_stub_chapter.tex` that inputs the chapter narrative as "
        "commented text plus includegraphics placeholders referencing "
        "`../figures/m1_stub_graph.pdf`.",
        expected_output="TeX stub saved under latex/chapters/.",
        agent=agents["latex"],
        context=[figures],
    )
    compile_ = Task(
        description=shared
        + "Run run_lualatex_once once, then read `build/m1_lualatex_once.log` if present and "
        "summarize errors/warnings in plain language.",
        expected_output="LuaLaTeX smoke pass executed with log captured.",
        agent=agents["compile"],
        context=[latex],
    )
    qa = Task(
        description=shared
        + "Read prior artifacts (notes, outline, draft, manifest, tex stub, LaTeX log) and write "
        "`build/m1_qa_report.md` with a checklist table: item, status, evidence path.",
        expected_output="QA markdown saved at build/m1_qa_report.md.",
        agent=agents["qa"],
        context=[compile_],
    )
    return [research, outline, writing, figures, latex, compile_, qa]
