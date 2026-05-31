"""Sequential tasks for milestones M1 (full crew), M2 (content), M3 (figures + QA)."""

from __future__ import annotations

from crewai import Agent, Task


def build_m3_tasks(agents: dict[str, Agent], topic: str, language: str) -> list[Task]:
    """M2 content pipeline plus M3 figure generators and extended QA (FR-9)."""
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
    figures = Task(
        description=shared
        + "Call **run_m3_asset_generators** once to emit `figures/graph.pdf` and `figures/image.png`. "
        "Then write `figures/m3_manifest.txt` listing those files with one path per line. "
        "If generation fails, capture stderr in the manifest and stop.",
        expected_output="M3 binaries on disk + figures/m3_manifest.txt.",
        agent=agents["figure"],
        context=[writing],
    )
    qa = Task(
        description=shared
        + "Call **verify_m3_assets** and record the verbatim result. Verify M2 files exist: "
        "outline, research_notes, all chapter_*.md, references.bib, REVIEW_GATE. "
        "Read `latex/chapters/m3_fr9_showcase.tex` and confirm labels "
        "`fig:pipeline`, `fig:cover-art`, `fig:latency`, `tab:requirements`, `eq:normalized` appear. "
        "Write `build/m3_qa_report.md` with markdown tables for M2 checks and M3 checks "
        "(check, status, evidence).",
        expected_output="m3_qa_report.md with M2+M3 contract rows.",
        agent=agents["qa"],
        context=[figures],
    )
    return [research, outline, writing, figures, qa]


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
