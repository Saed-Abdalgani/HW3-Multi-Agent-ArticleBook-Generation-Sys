"""CrewAI tasks for milestone M2 (content pipeline)."""

from __future__ import annotations

from crewai import Agent, Task


def build_m2_tasks(agents: dict[str, Agent], topic: str, language: str) -> list[Task]:
    """M2: research notes + `.bib`, outline with page budget, multi-file Markdown, QA."""
    shared = f"Topic: {topic}\nLanguage: {language}\n"

    research = Task(
        description=shared
        + "Read `prd.md` and `plan.md` via read_workspace_file. Write `content/research_notes.md` "
        "with vetted sources (prefer real titles/years/URLs). Write `latex/references.bib` with "
        "matching BibTeX keys for every citation you will reference. Follow research-methodology: "
        "no orphan keys, no uncited entries.",
        expected_output="research_notes.md and references.bib saved; keys align.",
        agent=agents["research"],
    )
    outline = Task(
        description=shared
        + "Write `content/outline.md`: chapter table with per-chapter **page estimate** and "
        "**word budget** (aim total ~15–20 pages at ~250 words/page). Reserve one chapter row "
        "explicitly as the BiDi demonstration chapter. Include stable HTML comment anchors for "
        "FIG/GRAPH/TAB/EQ placeholders per document-structure.",
        expected_output="outline.md with cumulative page budget within 15–20.",
        agent=agents["architect"],
        context=[research],
    )
    writing = Task(
        description=shared
        + "Using the outline, write separate files: `content/chapter_01_scope.md`, "
        "`content/chapter_02_markdown_first.md`, `content/chapter_03_agents_and_crews.md`, "
        "`content/chapter_04_bidi_technical_note.md` (Hebrew+English LTR islands if language is "
        "Hebrew; otherwise include an RTL block quote demo), `content/chapter_05_latex_path.md`, "
        "`content/chapter_06_conclusion.md`. Use pandoc-style markers [@bibkey] that exist in "
        "`latex/references.bib`. Include asset anchors as HTML comments. "
        "Add `content/REVIEW_GATE.md` stating human approval is required before LaTeX conversion.",
        expected_output="Six chapter markdown files + REVIEW_GATE.md on disk.",
        agent=agents["writer"],
        context=[outline],
    )
    qa = Task(
        description=shared
        + "Verify files exist: outline, research_notes, all chapter_*.md, "
        "references.bib, REVIEW_GATE. "
        "Scan chapters for citation markers and confirm each key appears in references.bib. "
        "Write `build/m2_qa_report.md` with a markdown table: check, status, evidence.",
        expected_output="m2_qa_report.md with pass/fail per M2 contract.",
        agent=agents["qa"],
        context=[writing],
    )
    return [research, outline, writing, qa]
