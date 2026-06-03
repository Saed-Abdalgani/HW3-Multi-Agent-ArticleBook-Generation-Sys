"""CrewAI tasks for milestone M2 (content pipeline)."""

from __future__ import annotations

from crewai import Agent, Task

from articlebook.crew.task_overrides import resolve_task_strings


def build_m2_tasks(agents: dict[str, Agent], topic: str, language: str) -> list[Task]:
    """M2: research notes + `.bib`, outline with page budget, multi-file Markdown, QA."""
    shared = f"Topic: {topic}\nLanguage: {language}\n"

    rd, re = resolve_task_strings(
        "m2",
        "research",
        default_description=shared
        + "Read `prd.md` and `plan.md` via read_workspace_file. Write `content/research_notes.md` "
        "with vetted sources (prefer real titles/years/URLs). Write `latex/references.bib` with "
        "matching BibTeX keys for every citation you will reference. Follow research-methodology: "
        "no orphan keys, no uncited entries.",
        default_expected_output="research_notes.md and references.bib saved; keys align.",
        topic=topic,
        language=language,
    )
    research = Task(description=rd, expected_output=re, agent=agents["research"])

    od, oe = resolve_task_strings(
        "m2",
        "outline",
        default_description=shared
        + "Write `content/outline.md`: chapter table with per-chapter **page estimate** and "
        "**word budget** (aim total ~15–20 pages at ~250 words/page). Reserve one chapter row "
        "explicitly as the BiDi demonstration chapter. Include stable HTML comment anchors for "
        "FIG/GRAPH/TAB/EQ placeholders per document-structure.",
        default_expected_output="outline.md with cumulative page budget within 15–20.",
        topic=topic,
        language=language,
    )
    outline = Task(
        description=od,
        expected_output=oe,
        agent=agents["architect"],
        context=[research],
    )

    wd, we = resolve_task_strings(
        "m2",
        "writing",
        default_description=shared
        + "Using the outline, write separate files: `content/chapter_01_scope.md`, "
        "`content/chapter_02_markdown_first.md`, `content/chapter_03_agents_and_crews.md`, "
        "`content/chapter_04_bidi_technical_note.md` (Hebrew+English LTR islands if language is "
        "Hebrew; otherwise include an RTL block quote demo), `content/chapter_05_latex_path.md`, "
        "`content/chapter_06_conclusion.md`. Use pandoc-style markers [@bibkey] that exist in "
        "`latex/references.bib`. Include asset anchors as HTML comments. "
        "Add `content/REVIEW_GATE.md` stating human approval is required before LaTeX conversion.",
        default_expected_output="Six chapter markdown files + REVIEW_GATE.md on disk.",
        topic=topic,
        language=language,
    )
    writing = Task(description=wd, expected_output=we, agent=agents["writer"], context=[outline])

    qd, qe = resolve_task_strings(
        "m2",
        "qa",
        default_description=shared
        + "Verify files exist: outline, research_notes, all chapter_*.md, "
        "references.bib, REVIEW_GATE. "
        "Scan chapters for citation markers and confirm each key appears in references.bib. "
        "Write `build/m2_qa_report.md` with a markdown table: check, status, evidence.",
        default_expected_output="m2_qa_report.md with pass/fail per M2 contract.",
        topic=topic,
        language=language,
    )
    qa = Task(description=qd, expected_output=qe, agent=agents["qa"], context=[writing])
    return [research, outline, writing, qa]
