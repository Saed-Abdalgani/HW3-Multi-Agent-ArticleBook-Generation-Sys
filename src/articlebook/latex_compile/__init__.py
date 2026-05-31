"""Multipass LuaLaTeX/XeLaTeX + biber (M5). Public API re-exported from submodules."""

from articlebook.latex_compile.analysis import classify_compile_failure, needs_extra_engine_pass
from articlebook.latex_compile.canonical import compile_latex_canonical
from articlebook.latex_compile.env import (
    biber_available,
    engine_available,
    prepare_miktex_path_on_windows,
    resolve_latex_engine,
)
from articlebook.latex_compile.messages import compile_report_to_message
from articlebook.latex_compile.types import CompilePassRecord, CompileReport, LaTeXEngine

__all__ = [
    "CompilePassRecord",
    "CompileReport",
    "LaTeXEngine",
    "biber_available",
    "classify_compile_failure",
    "compile_latex_canonical",
    "compile_report_to_message",
    "engine_available",
    "needs_extra_engine_pass",
    "prepare_miktex_path_on_windows",
    "resolve_latex_engine",
]
