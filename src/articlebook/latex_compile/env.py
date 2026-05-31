"""PATH probing and engine selection for LaTeX tooling."""

from __future__ import annotations

import os
import shutil

from articlebook.latex_compile.types import LaTeXEngine


def prepare_miktex_path_on_windows() -> None:
    """Prepend default MiKTeX user bin when engines are missing (Windows)."""
    if os.name != "nt":
        return
    if shutil.which("lualatex") or shutil.which("xelatex"):
        return
    miktex = os.path.expandvars(r"%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64")
    if os.path.isdir(miktex):
        os.environ["PATH"] = miktex + os.pathsep + os.environ.get("PATH", "")


def resolve_latex_engine() -> LaTeXEngine:
    """Engine from ``ARTICLEBOOK_LATEX_ENGINE`` (``lualatex`` | ``xelatex``)."""
    raw = os.getenv("ARTICLEBOOK_LATEX_ENGINE", "lualatex").strip().lower()
    if raw in ("xelatex", "xe"):
        return "xelatex"
    return "lualatex"


def engine_available(engine: LaTeXEngine) -> bool:
    prepare_miktex_path_on_windows()
    return shutil.which(engine) is not None


def biber_available() -> bool:
    prepare_miktex_path_on_windows()
    return shutil.which("biber") is not None
