"""Subprocess helpers for LaTeX compile passes."""

from __future__ import annotations

import subprocess
from pathlib import Path


def run_cmd_capture_log(
    cmd: list[str],
    *,
    cwd: Path,
    log_path: Path,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(combined, encoding="utf-8", errors="replace")
    return proc


def tail_text(text: str, max_chars: int = 12000) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]
