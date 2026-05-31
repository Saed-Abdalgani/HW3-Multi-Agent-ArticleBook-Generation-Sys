"""Deterministic stub runners (M1–M4) for ``articlebook.pipeline``."""

from __future__ import annotations

import logging
from pathlib import Path

from articlebook.crew.workspace_tools import (
    bind_workspace_root,
    compile_lualatex_once,
    reset_workspace_root,
    run_matplotlib_stub_script,
)
from articlebook.inputs import log_resolved_run_config, validate_topic_language
from articlebook.m2_stub import write_m2_stub_artifacts
from articlebook.m3_assets import run_m3_python_generators, write_m3_stub_manifest
from articlebook.m4_assembly import assemble_latex_project, write_m4_stub_manifest
from articlebook.shared.paths import project_root


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


def _write_m3_figure_manifest(fig_dir: Path) -> None:
    manifest_lines = ["figures/graph.pdf", "figures/image.png"]
    fig_dir.mkdir(parents=True, exist_ok=True)
    (fig_dir / "m3_manifest.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")


def run_stub_m3(topic: str, language: str) -> None:
    """Deterministic M2 + M3: Markdown draft, `.bib`, Matplotlib assets, M3 manifest."""
    inputs = validate_topic_language(topic, language)
    root = project_root()
    log = logging.getLogger(__name__)
    log_resolved_run_config(inputs, mode="stub", milestone="m3")
    token = bind_workspace_root(root)
    try:
        write_m2_stub_artifacts(root, inputs)
        gen_log = run_m3_python_generators(root)
        write_m3_stub_manifest(root, inputs, gen_log)
        (root / "figures").mkdir(parents=True, exist_ok=True)
        _write_m3_figure_manifest(root / "figures")
        log.info("stub.m3 complete root=%s", root)
    finally:
        reset_workspace_root(token)


def run_stub_m4(topic: str, language: str) -> None:
    """Deterministic M2 + M3 + M4: Markdown, assets, LaTeX assembly, one LuaLaTeX pass."""
    inputs = validate_topic_language(topic, language)
    root = project_root()
    log = logging.getLogger(__name__)
    log_resolved_run_config(inputs, mode="stub", milestone="m4")
    token = bind_workspace_root(root)
    try:
        write_m2_stub_artifacts(root, inputs)
        gen_log = run_m3_python_generators(root)
        write_m3_stub_manifest(root, inputs, gen_log)
        (root / "figures").mkdir(parents=True, exist_ok=True)
        _write_m3_figure_manifest(root / "figures")
        stems = assemble_latex_project(root, inputs)
        compile_msg = compile_lualatex_once(root, log_filename="m4_lualatex_once.log")
        write_m4_stub_manifest(root, inputs, stems, compile_msg)
        log.info("stub.m4 complete root=%s", root)
    finally:
        reset_workspace_root(token)
