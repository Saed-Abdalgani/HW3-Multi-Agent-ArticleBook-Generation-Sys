"""Sandboxed file and subprocess tools bound to the project workspace."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
from contextvars import ContextVar, Token
from pathlib import Path

from crewai.tools import tool

logger = logging.getLogger(__name__)

_ALLOWED_PREFIXES = ("content/", "latex/", "figures/", "build/", "scripts/")
_ROOT_READABLE = frozenset(
    {"prd.md", "plan.md", "todo.md", "README.md", "SYSTEM_PROMPT.md", "PROMPTS.md"}
)
_workspace_root: ContextVar[Path | None] = ContextVar("articlebook_workspace_root", default=None)


def bind_workspace_root(root: Path) -> Token:
    """Bind the workspace root for tool execution (call from the crew runner thread)."""
    return _workspace_root.set(root.resolve())


def reset_workspace_root(token: Token) -> None:
    _workspace_root.reset(token)


def _root() -> Path:
    r = _workspace_root.get()
    if r is None:
        msg = "Workspace root is not bound; call bind_workspace_root() before running tools."
        raise RuntimeError(msg)
    return r


def _validate_relative(relative_path: str) -> Path:
    raw = Path(relative_path).as_posix().lstrip("./")
    if not raw or ".." in Path(raw).parts or Path(raw).is_absolute():
        raise ValueError("Invalid relative path.")
    if not any(raw.startswith(p) for p in _ALLOWED_PREFIXES):
        allowed = ", ".join(_ALLOWED_PREFIXES)
        raise ValueError(f"Path must start with one of: {allowed}")
    return Path(raw)


def _validate_relative_read(relative_path: str) -> Path:
    raw = Path(relative_path).as_posix().lstrip("./")
    if not raw or ".." in Path(raw).parts or Path(raw).is_absolute():
        raise ValueError("Invalid relative path.")
    if raw in _ROOT_READABLE:
        return Path(raw)
    if not any(raw.startswith(p) for p in _ALLOWED_PREFIXES):
        allowed = ", ".join(_ALLOWED_PREFIXES) + f", or one of {sorted(_ROOT_READABLE)}"
        raise ValueError(f"Path not allowed for read: {allowed}")
    return Path(raw)


def _ensure_under_root(root: Path, target: Path) -> Path:
    resolved = (root / target).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("Resolved path escapes project root.")
    return resolved


@tool("write_workspace_file")
def write_workspace_file(relative_path: str, content: str) -> str:
    """Write UTF-8 text under content/, latex/, figures/, build/, or scripts/ (relative to repo)."""
    root = _root()
    rel = _validate_relative(relative_path)
    dest = _ensure_under_root(root, rel)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    msg = f"Wrote {dest.relative_to(root)} ({len(content)} chars)."
    logger.info(
        "artifact.write path=%s bytes=%s",
        dest.relative_to(root),
        len(content.encode("utf-8")),
    )
    return msg


@tool("read_workspace_file")
def read_workspace_file(relative_path: str) -> str:
    """Read a UTF-8 text file from allowed project subfolders."""
    root = _root()
    rel = _validate_relative_read(relative_path)
    src = (root / rel).resolve()
    if not src.is_relative_to(root.resolve()):
        raise ValueError("Invalid read target.")
    if not src.is_file():
        return f"Missing file: {src.relative_to(root)}"
    text = src.read_text(encoding="utf-8")
    logger.info("artifact.read path=%s chars=%s", src.relative_to(root), len(text))
    return text


def compile_lualatex_once(root: Path) -> str:
    """Run one LuaLaTeX pass (shared by tool + offline stub)."""
    latex_dir = root / "latex"
    build_dir = root / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    if os.name == "nt" and not shutil.which("lualatex"):
        miktex = os.path.expandvars(r"%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64")
        if os.path.isdir(miktex):
            os.environ["PATH"] = miktex + os.pathsep + os.environ.get("PATH", "")
    if not shutil.which("lualatex"):
        log_path = build_dir / "m1_lualatex_once.log"
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
    log_path = build_dir / "m1_lualatex_once.log"
    log_path.write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8", errors="replace")
    logger.info("lualatex.once rc=%s log=%s", proc.returncode, log_path.relative_to(root))
    return f"lualatex exit={proc.returncode}; log at build/m1_lualatex_once.log"


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


@tool("run_matplotlib_stub")
def run_matplotlib_stub(reason: str = "run") -> str:
    """Run the whitelisted stub script `scripts/plot_stub_m1.py` to emit a vector figure."""
    return run_matplotlib_stub_script(_root())


@tool("run_lualatex_once")
def run_lualatex_once(reason: str = "run") -> str:
    """One LuaLaTeX pass on latex/main.tex into build/ (M1 smoke; full passes in M5)."""
    return compile_lualatex_once(_root())


def workspace_tools() -> list:
    """Tools shared across agents (bound root via bind_workspace_root)."""
    return [
        write_workspace_file,
        read_workspace_file,
        run_matplotlib_stub,
        run_lualatex_once,
    ]
