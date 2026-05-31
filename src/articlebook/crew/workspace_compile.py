"""LuaLaTeX and Matplotlib stub subprocess helpers (no CrewAI)."""

from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from pathlib import Path

from articlebook.compile_multipass import prepare_miktex_path_on_windows

logger = logging.getLogger(__name__)


def compile_lualatex_once(root: Path, *, log_filename: str = "m1_lualatex_once.log") -> str:
    """Run one LuaLaTeX pass (shared by tool + offline stub)."""
    latex_dir = root / "latex"
    build_dir = root / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    prepare_miktex_path_on_windows()
    if not shutil.which("lualatex"):
        log_path = build_dir / log_filename
        msg = "lualatex not found on PATH; skipped smoke compile (install MiKTeX for M0/M5).\n"
        log_path.write_text(msg, encoding="utf-8")
        logger.warning("lualatex.missing log=%s", log_path.relative_to(root))
        return msg.strip()
    cmd = [
        "lualatex",
        "-interaction=nonstopmode",
        f"-output-directory={build_dir}",
        "main.tex",
    ]
    proc = subprocess.run(cmd, cwd=str(latex_dir), capture_output=True, text=True, check=False)
    log_path = build_dir / log_filename
    log_path.write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8", errors="replace")
    logger.info("lualatex.once rc=%s log=%s", proc.returncode, log_path.relative_to(root))
    rel = log_path.relative_to(root)
    return f"lualatex exit={proc.returncode}; log at {rel.as_posix()}"


def run_matplotlib_stub_script(root: Path) -> str:
    """Execute the whitelisted Matplotlib stub (shared by tool + offline stub)."""
    script = (root / "scripts" / "plot_stub_m1.py").resolve()
    if not script.is_file() or not str(script).startswith(str(root.resolve())):
        return "Stub script missing."
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    logger.info("matplotlib.stub rc=%s", proc.returncode)
    tail = (proc.stderr or proc.stdout or "")[-2000:]
    return f"exit={proc.returncode}\n{tail}"
