"""Datatypes for the multipass LaTeX + biber driver."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

LaTeXEngine = Literal["lualatex", "xelatex"]


@dataclass
class CompilePassRecord:
    """One subprocess step in the build journal."""

    name: str
    command: list[str]
    cwd: str
    returncode: int
    log_relative: str


@dataclass
class CompileReport:
    """Outcome of :func:`articlebook.latex_compile.canonical.compile_latex_canonical`."""

    ok: bool
    engine: LaTeXEngine
    pdf_exists: bool
    passes: list[CompilePassRecord] = field(default_factory=list)
    failure_pass: str | None = None
    failure_excerpt: str | None = None
    error_class: str | None = None
    needs_rerun_after_last: bool = False
    unresolved_log_lines: list[str] = field(default_factory=list)
    journal_relative: str = "build/m5_compile_journal.json"
