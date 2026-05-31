"""Canonical engine → biber → engine ×N multipass orchestration."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from articlebook.latex_compile.analysis import (
    classify_compile_failure,
    collect_unresolved_markers,
    needs_extra_engine_pass,
)
from articlebook.latex_compile.cmd import tail_text
from articlebook.latex_compile.env import engine_available, prepare_miktex_path_on_windows, resolve_latex_engine
from articlebook.latex_compile.journal import finalize_compile_failure, write_compile_journal
from articlebook.latex_compile.runner import PassRunner
from articlebook.latex_compile.types import CompileReport, LaTeXEngine

logger = logging.getLogger(__name__)


def compile_latex_canonical(
    root: Path,
    *,
    log_prefix: str = "m5",
    engine: LaTeXEngine | None = None,
    max_rerun_rounds: int = 4,
) -> CompileReport:
    """Run plan.md §4 sequence: engine → biber → engine ×2+ until stable (capped).

    Invokes the engine from ``latex/`` with ``-output-directory`` pointing at
    ``build/`` so ``.aux`` / ``.bcf`` / ``main.pdf`` land in ``build/``.
    """
    chosen = engine or resolve_latex_engine()
    latex_dir = root / "latex"
    build_dir = root / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    prepare_miktex_path_on_windows()

    report = CompileReport(ok=False, engine=chosen, pdf_exists=False, passes=[])

    if not latex_dir.is_dir() or not (latex_dir / "main.tex").is_file():
        excerpt = "latex/main.tex missing"
        report.failure_pass = "preflight"
        report.failure_excerpt = excerpt
        report.error_class = "missing_file"
        (build_dir / f"{log_prefix}_failure.txt").write_text(excerpt, encoding="utf-8")
        write_compile_journal(build_dir, log_prefix, report)
        return report

    if not engine_available(chosen):
        msg = (
            f"{chosen} not found on PATH; skipped compile (install MiKTeX). "
            "Set ARTICLEBOOK_LATEX_ENGINE=xelatex to try XeLaTeX.\n"
        )
        log_path = build_dir / f"{log_prefix}_skip.log"
        log_path.write_text(msg, encoding="utf-8")
        logger.warning("%s.missing log=%s", chosen, log_path.relative_to(root))
        report.failure_pass = "preflight"
        report.failure_excerpt = msg.strip()
        report.error_class = "missing_engine"
        write_compile_journal(build_dir, log_prefix, report)
        return report

    runner = PassRunner(root, latex_dir, build_dir, log_prefix, chosen, report)

    p1 = runner.run_engine("initial")
    if p1.returncode != 0:
        return finalize_compile_failure(report, build_dir, log_prefix, p1, "engine_initial")

    b = runner.run_biber()
    if b.returncode != 0:
        report.error_class = classify_compile_failure(b.stderr, b.stdout)
        excerpt = tail_text((b.stderr or "") + "\n" + (b.stdout or ""))
        (build_dir / f"{log_prefix}_biber_warning_excerpt.txt").write_text(
            excerpt, encoding="utf-8"
        )

    for tag in ("post_biber_1", "post_biber_2"):
        pr = runner.run_engine(tag)
        if pr.returncode != 0:
            return finalize_compile_failure(report, build_dir, log_prefix, pr, tag)

    log_file = build_dir / "main.log"
    for round_i in range(max_rerun_rounds):
        log_text = log_file.read_text(encoding="utf-8", errors="replace") if log_file.is_file() else ""
        report.needs_rerun_after_last = needs_extra_engine_pass(log_text)
        report.unresolved_log_lines = collect_unresolved_markers(log_text)
        if not report.needs_rerun_after_last:
            break
        pr = runner.run_engine(f"stabilize_{round_i + 1}")
        if pr.returncode != 0:
            return finalize_compile_failure(
                report, build_dir, log_prefix, pr, f"stabilize_{round_i + 1}"
            )

    report.pdf_exists = (build_dir / "main.pdf").is_file()
    log_text = log_file.read_text(encoding="utf-8", errors="replace") if log_file.is_file() else ""
    report.needs_rerun_after_last = needs_extra_engine_pass(log_text)
    report.unresolved_log_lines = collect_unresolved_markers(log_text)

    still_bad = report.needs_rerun_after_last or bool(
        re.search(r"There were undefined citations|undefined references", log_text, re.I)
    )
    all_passes_ok = all(p.returncode == 0 for p in report.passes)
    report.ok = report.pdf_exists and all_passes_ok and not still_bad
    if not report.ok and report.failure_pass is None:
        report.failure_pass = "post_pass_scan"
        report.failure_excerpt = tail_text(log_text)
        report.error_class = "unresolved_refs_or_rerun" if still_bad else "missing_pdf"

    write_compile_journal(build_dir, log_prefix, report)
    return report
