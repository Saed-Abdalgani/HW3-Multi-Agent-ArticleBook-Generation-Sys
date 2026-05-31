"""High-level runners: stub vs LLM, milestones M1 (full) and M2 (content)."""

from __future__ import annotations

import logging
from typing import Literal

from articlebook.crew.crew_builder import build_crew
from articlebook.crew.workspace_tools import (
    bind_workspace_root,
    compile_lualatex_once,
    reset_workspace_root,
    run_matplotlib_stub_script,
)
from articlebook.inputs import log_resolved_run_config, validate_topic_language
from articlebook.m2_stub import write_m2_stub_artifacts
from articlebook.shared.config import load_config
from articlebook.shared.gatekeeper import create_llm
from articlebook.shared.paths import project_root

Milestone = Literal["m1", "m2"]


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def run_stub_m1(topic: str, language: str) -> None:
    """Deterministic M1 placeholder pipeline (no LLM) for CI and smoke tests."""
    inputs = validate_topic_language(topic, language)
    root = project_root()
    log = logging.getLogger(__name__)
    log_resolved_run_config(inputs, mode="stub", milestone="m1")
    token = bind_workspace_root(root)
    try:
        (root / "content" / "m1_research_notes.md").write_text(
            f"# M1 research (stub)\nTopic: {inputs.topic}\nLanguage: {inputs.language}\n",
            encoding="utf-8",
        )
        (root / "content" / "m1_outline.md").write_text(
            "# Outline (stub)\n- Ch1 intro (3p)\n- Ch2 BiDi demo (3p)\n", encoding="utf-8"
        )
        (root / "content" / "m1_chapter_draft.md").write_text(
            "# Draft (stub)\n<!-- FIG:stub -->\n", encoding="utf-8"
        )
        run_matplotlib_stub_script(root)
        (root / "figures" / "m1_manifest.txt").write_text("m1_stub_graph.pdf\n", encoding="utf-8")
        tex = (
            "% stub chapter\n"
            "\\begin{center}\n"
            "\\includegraphics[width=0.5\\linewidth]{../figures/m1_stub_graph.pdf}\n"
            "\\end{center}\n"
        )
        (root / "latex" / "chapters" / "m1_stub_chapter.tex").write_text(tex, encoding="utf-8")
        compile_lualatex_once(root)
        log_path = root / "build" / "m1_lualatex_once.log"
        log_text = (
            log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""
        )
        (root / "build" / "m1_qa_report.md").write_text(
            "# M1 QA (stub)\n|check|status|\n|---|---|\n|artifacts|ok|\n"
            f"|lualatex log chars|{len(log_text)}|\n",
            encoding="utf-8",
        )
        log.info("stub.m1 complete root=%s", root)
    finally:
        reset_workspace_root(token)


def run_stub_m2(topic: str, language: str) -> None:
    """Deterministic M2 content pipeline: outline, chapters, BiDi note, `.bib` (no compile)."""
    inputs = validate_topic_language(topic, language)
    root = project_root()
    log = logging.getLogger(__name__)
    log_resolved_run_config(inputs, mode="stub", milestone="m2")
    token = bind_workspace_root(root)
    try:
        write_m2_stub_artifacts(root, inputs)
        log.info("stub.m2 complete root=%s", root)
    finally:
        reset_workspace_root(token)


def run_llm(topic: str, language: str, milestone: Milestone = "m2") -> str:
    """Execute CrewAI crew (requires OPENAI_API_KEY). Default milestone is M2 content pipeline."""
    inputs = validate_topic_language(topic, language)
    root = project_root()
    token = bind_workspace_root(root)
    log = logging.getLogger(__name__)
    try:
        cfg = load_config()
        llm = create_llm(cfg)
        log_resolved_run_config(inputs, mode="llm", milestone=milestone)

        def _task_cb(output: object) -> None:
            log.info("crew.task.done snippet=%s", str(output)[:400].replace("\n", " "))

        crew = build_crew(
            llm, inputs.topic, inputs.language, milestone=milestone, task_callback=_task_cb
        )
        log.info(
            "crew.kickoff.start topic=%s language=%s milestone=%s",
            topic,
            language,
            milestone,
        )
        result = crew.kickoff(inputs={"topic": inputs.topic, "language": inputs.language})
        log.info("crew.kickoff.done")
        return str(result)
    finally:
        reset_workspace_root(token)


def run_llm_m1(topic: str, language: str) -> str:
    """Backward-compatible entry: full M1 crew."""
    return run_llm(topic, language, milestone="m1")


def run_llm_m2(topic: str, language: str) -> str:
    """M2 content pipeline via LLM agents."""
    return run_llm(topic, language, milestone="m2")
