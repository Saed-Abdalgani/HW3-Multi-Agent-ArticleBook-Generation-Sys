"""CrewAI tasks for milestone M2 (content pipeline)."""

from __future__ import annotations

from crewai import Agent, Task

from articlebook.crew.task_overrides import resolve_task_strings

# Groq rejects tool payloads that omit the named parameter (bare ``[{...}]`` → ``tool_use_failed``).
_FILES_JSON_TOOL_RULE = (
    "**Tool call:** pass exactly one argument named **`files_json`** whose value is a **string** "
    "containing the whole JSON array (serialize the array as text; escape inner quotes per JSON). "
    "Do **not** supply only a bare JSON array as the tool arguments—Groq returns `tool_use_failed` "
    "unless the arguments are an object with a `files_json` string field matching the tool schema."
)

_WRITE_WS_SINGLE = (
    "To save one file, call **write_workspace_file** with **both** required string arguments: "
    "**relative_path** and **content** (full UTF-8 body). Do not use path wildcards or globs."
)


def build_m2_tasks(agents: dict[str, Agent], topic: str, language: str) -> list[Task]:
    """M2: research notes + `.bib`, outline with page budget, multi-file Markdown, QA."""
    shared = f"Topic: {topic}\nLanguage: {language}\n"

    rd, re = resolve_task_strings(
        "m2",
        "research",
        default_description=shared
        + "Read `prd.md` and `plan.md` via read_workspace_file. "
        "**Persist to disk:** call **write_workspace_files_batch** once with a JSON array of two "
        "objects, each with keys `relative_path` and `content`: one object for "
        "`content/research_notes.md` and one for `latex/references.bib`. "
        + _FILES_JSON_TOOL_RULE
        + " Do **not** pass a JSON array as the sole argument to `write_workspace_file` "
        "(that tool accepts only one path + one string). "
        "Write vetted sources (prefer real titles/years/URLs) in the research file and matching "
        "BibTeX keys for every citation you will reference. Follow research-methodology: "
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
        + _WRITE_WS_SINGLE
        + " Persist **relative_path** `content/outline.md` with **content** that is a chapter "
        "table with per-chapter **page estimate** and **word budget** (aim total ~15–20 pages at "
        "~250 words/page). Reserve one chapter row explicitly as the BiDi demonstration chapter. "
        "Include stable HTML comment anchors for FIG/GRAPH/TAB/EQ placeholders per "
        "document-structure.",
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
        + "Using the outline, **persist** these paths with **write_workspace_files_batch** as one "
        "JSON array of **seven** objects (each with **relative_path** and **content**): "
        "`content/chapter_01_scope.md`, `content/chapter_02_markdown_first.md`, "
        "`content/chapter_03_agents_and_crews.md`, `content/chapter_04_bidi_technical_note.md` "
        "(Hebrew+English LTR islands if language is Hebrew; otherwise include an RTL block quote "
        "demo), `content/chapter_05_latex_path.md`, `content/chapter_06_conclusion.md`, plus "
        "`content/REVIEW_GATE.md`. "
        + _FILES_JSON_TOOL_RULE
        + " "
        "Each of the six chapter files must be **750–1000 words** of substantive prose (not "
        "headings alone). Do **not** use meta-stubs such as 'This chapter will explore…' or "
        "'In this section we will…'; open with real technical content in the first paragraph. "
        "Combined chapters should still target roughly **15–20 PDF pages** (~250 words/page). "
        "Use pandoc-style markers [@bibkey] only for keys that exist in `latex/references.bib`, "
        "and remove any unused stub keys from that `.bib` if you replace it. Include asset anchors "
        "as HTML comments. "
        "REVIEW_GATE.md must state human approval is required before LaTeX conversion. "
        "Do not leave new chapter text only in the Final Answer—disk files must be updated.",
        default_expected_output="Six chapter markdown files + REVIEW_GATE.md on disk.",
        topic=topic,
        language=language,
    )
    writing = Task(description=wd, expected_output=we, agent=agents["writer"], context=[outline])

    qd, qe = resolve_task_strings(
        "m2",
        "qa",
        default_description=shared
        + "Verify files exist: `content/outline.md`, `content/research_notes.md`, "
        "`content/chapter_01_scope.md`, `content/chapter_02_markdown_first.md`, "
        "`content/chapter_03_agents_and_crews.md`, `content/chapter_04_bidi_technical_note.md`, "
        "`content/chapter_05_latex_path.md`, `content/chapter_06_conclusion.md`, "
        "`latex/references.bib`, `content/REVIEW_GATE.md`. "
        "Scan chapters for citation markers and confirm each key appears in references.bib. "
        + _WRITE_WS_SINGLE
        + " Save **relative_path** `build/m2_qa_report.md` with **content** as a markdown table: "
        "check, status, evidence.",
        default_expected_output="m2_qa_report.md with pass/fail per M2 contract.",
        topic=topic,
        language=language,
    )
    qa = Task(description=qd, expected_output=qe, agent=agents["qa"], context=[writing])
    return [research, outline, writing, qa]
