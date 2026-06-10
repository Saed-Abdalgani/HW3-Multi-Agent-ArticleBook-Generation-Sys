"""CrewAI tasks for milestone M3 (figures + QA)."""

from __future__ import annotations

from crewai import Agent, Task

from articlebook.crew.tasks_m2 import _FILES_JSON_TOOL_RULE, _WRITE_WS_SINGLE


def build_m3_tasks(agents: dict[str, Agent], topic: str, language: str) -> list[Task]:
    """M2 content pipeline plus M3 figure generators and extended QA (FR-9)."""
    shared = f"Topic: {topic}\nLanguage: {language}\n"

    research = Task(
        description=shared
        + "Read `prd.md` and `plan.md` via read_workspace_file. "
        "**Persist to disk:** call **write_workspace_files_batch** once with a JSON array of two "
        "objects (`relative_path` + `content`) for `content/research_notes.md` and "
        "`latex/references.bib`. "
        + _FILES_JSON_TOOL_RULE
        + " Do **not** pass a JSON array to `write_workspace_file` alone. "
        "Write vetted sources (prefer real titles/years/URLs) and matching BibTeX keys for every "
        "citation you will reference. Follow research-methodology: no orphan keys, no uncited "
        "entries.",
        expected_output="research_notes.md and references.bib saved; keys align.",
        agent=agents["research"],
    )
    outline = Task(
        description=shared
        + _WRITE_WS_SINGLE
        + " Persist **relative_path** `content/outline.md` with **content** that is a chapter "
        "table with per-chapter **page estimate** and **word budget** (aim total ~15–20 pages at "
        "~250 words/page). Reserve one chapter row explicitly as the BiDi demonstration chapter. "
        "Include stable HTML comment anchors for FIG/GRAPH/TAB/EQ placeholders per "
        "document-structure.",
        expected_output="outline.md with cumulative page budget within 15–20.",
        agent=agents["architect"],
        context=[research],
    )
    writing = Task(
        description=shared
        + "Using the outline, **persist** with **write_workspace_files_batch** one JSON array of "
        "**seven** objects (each with **relative_path** and **content**): "
        "`content/chapter_01_scope.md`, `content/chapter_02_markdown_first.md`, "
        "`content/chapter_03_agents_and_crews.md`, `content/chapter_04_bidi_technical_note.md`, "
        "`content/chapter_05_latex_path.md`, `content/chapter_06_conclusion.md`, plus "
        "`content/REVIEW_GATE.md`. "
        + _FILES_JSON_TOOL_RULE
        + " "
        "Each chapter must be **750–1000 words** of substantive prose; do **not** use meta-stubs "
        "such as 'This chapter will explore…'. Avoid many `##` headings (each becomes a LaTeX "
        "section). Use [@bibkey] only for keys in `latex/references.bib`; drop unused stub keys "
        "if you replace the bibliography. Include asset anchors as HTML comments. "
        "REVIEW_GATE.md must require human approval before LaTeX conversion. "
        "Do not leave chapter bodies only in the Final Answer.",
        expected_output="Six chapter markdown files + REVIEW_GATE.md on disk.",
        agent=agents["writer"],
        context=[outline],
    )
    figures = Task(
        description=shared
        + "Call **run_m3_asset_generators** once (optional **reason** string). "
        "Immediately call **verify_m3_assets**; the reply must be exactly `M3 asset check: OK` "
        "(non‑empty `figures/graph.pdf` and `figures/image.png`). If not OK, re-run "
        "**run_m3_asset_generators**, then **verify_m3_assets** again; repeat until OK or you "
        "document irrecoverable failure. "
        + _WRITE_WS_SINGLE
        + " Save **relative_path** `figures/m3_manifest.txt` with **content** listing "
        "`figures/graph.pdf` and `figures/image.png` (one path per line). "
        "If generation fails irrecoverably, put stderr in the manifest **content** and stop.",
        expected_output="M3 binaries on disk + figures/m3_manifest.txt.",
        agent=agents["figure"],
        context=[writing],
    )
    qa = Task(
        description=shared
        + "Call **verify_m3_assets** and record the verbatim result. Verify M2 files exist: "
        "`content/chapter_01_scope.md`, `content/chapter_02_markdown_first.md`, "
        "`content/chapter_03_agents_and_crews.md`, `content/chapter_04_bidi_technical_note.md`, "
        "`content/chapter_05_latex_path.md`, `content/chapter_06_conclusion.md`, "
        "Read `latex/chapters/m3_fr9_showcase.tex` and confirm labels "
        "`fig:pipeline`, `fig:cover-art`, `fig:latency`, `tab:requirements`, "
        "`eq:normalized` appear. "
        + _WRITE_WS_SINGLE
        + " Save **relative_path** `build/m3_qa_report.md` with **content** as markdown tables "
        "for M2 checks and M3 checks (check, status, evidence).",
        expected_output="m3_qa_report.md with M2+M3 contract rows.",
        agent=agents["qa"],
        context=[figures],
    )
    return [research, outline, writing, figures, qa]
