"""Shim: stable imports for ``articlebook.compile_multipass``.

Implementation lives in ``articlebook.latex_compile``.
"""

from articlebook.latex_compile import (
    CompilePassRecord,
    CompileReport,
    LaTeXEngine,
    biber_available,
    classify_compile_failure,
    compile_latex_canonical,
    compile_report_to_message,
    engine_available,
    needs_extra_engine_pass,
    prepare_miktex_path_on_windows,
    resolve_latex_engine,
)

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
