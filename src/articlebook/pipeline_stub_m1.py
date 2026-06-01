"""Deterministic M1 stub pipeline (isolated to keep ``pipeline_stubs`` small)."""

from __future__ import annotations

import logging

from articlebook.crew.workspace_tools import (
    bind_workspace_root,
    compile_lualatex_once,
    reset_workspace_root,
    run_matplotlib_stub_script,
)
from articlebook.inputs import log_resolved_run_config, validate_topic_language
from articlebook.shared.paths import project_root
from articlebook.shared.security_context import dry_run_active


def run_stub_m1(topic: str, language: str) -> None:
    """Deterministic M1 placeholder pipeline (no LLM) for CI and smoke tests."""
    inputs = validate_topic_language(topic, language)
    root = project_root()
    log = logging.getLogger(__name__)
    log_resolved_run_config(inputs, mode="stub", milestone="m1")
    if dry_run_active():
        log.info("stub.m1 dry-run: skipping disk writes")
        return
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
