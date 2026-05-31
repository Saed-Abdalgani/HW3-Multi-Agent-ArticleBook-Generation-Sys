"""Compile journal JSON and failure artifacts."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from articlebook.latex_compile.analysis import classify_compile_failure
from articlebook.latex_compile.cmd import tail_text
from articlebook.latex_compile.types import CompileReport


def write_compile_journal(build_dir: Path, log_prefix: str, report: CompileReport) -> None:
    payload = {
        "ok": report.ok,
        "engine": report.engine,
        "pdf_exists": report.pdf_exists,
        "failure_pass": report.failure_pass,
        "error_class": report.error_class,
        "needs_rerun_after_last": report.needs_rerun_after_last,
        "passes": [
            {
                "name": p.name,
                "command": p.command,
                "cwd": p.cwd,
                "returncode": p.returncode,
                "log": p.log_relative,
            }
            for p in report.passes
        ],
        "unresolved_log_lines_sample": report.unresolved_log_lines[:20],
    }
    path = build_dir / f"{log_prefix}_compile_journal.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    report.journal_relative = f"build/{log_prefix}_compile_journal.json"


def finalize_compile_failure(
    report: CompileReport,
    build_dir: Path,
    log_prefix: str,
    proc: subprocess.CompletedProcess[str],
    pass_name: str,
) -> CompileReport:
    report.ok = False
    report.failure_pass = pass_name
    excerpt = tail_text((proc.stderr or "") + "\n" + (proc.stdout or ""))
    report.failure_excerpt = excerpt
    report.error_class = classify_compile_failure(proc.stderr or "", proc.stdout or "")
    (build_dir / f"{log_prefix}_failure.txt").write_text(
        f"pass={pass_name}\nclass={report.error_class}\n\n{excerpt}",
        encoding="utf-8",
    )
    report.pdf_exists = (build_dir / "main.pdf").is_file()
    write_compile_journal(build_dir, log_prefix, report)
    return report
