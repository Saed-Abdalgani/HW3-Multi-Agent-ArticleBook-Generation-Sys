"""Sandboxed file and subprocess tools bound to the project workspace."""

from __future__ import annotations

from crewai.tools import tool

from articlebook.compile_multipass import compile_latex_canonical, compile_report_to_message
from articlebook.crew.workspace_compile import compile_lualatex_once, run_matplotlib_stub_script
from articlebook.crew.workspace_io_security import (
    guarded_read_workspace_file,
    guarded_write_workspace_file,
)
from articlebook.crew.workspace_m6_reply import m6_contract_tool_reply
from articlebook.crew.workspace_sandbox import (
    bind_workspace_root,
    reset_workspace_root,
)
from articlebook.inputs import validate_topic_language
from articlebook.m3_assets import run_m3_python_generators, verify_m3_figure_assets
from articlebook.m4_assembly import assemble_latex_project
from articlebook.m6_qa import run_m6_contract_qa

__all__ = [
    "bind_workspace_root",
    "reset_workspace_root",
    "compile_lualatex_once",
    "run_matplotlib_stub_script",
    "write_workspace_file",
    "read_workspace_file",
    "run_matplotlib_stub",
    "run_m3_asset_generators",
    "verify_m3_assets",
    "assemble_latex_document",
    "run_lualatex_once",
    "run_latex_canonical_compile",
    "run_m6_contract_checks",
    "workspace_tools",
]


@tool("write_workspace_file")
def write_workspace_file(relative_path: str, content: str) -> str:
    """Write UTF-8 text under content/, latex/, figures/, build/, or scripts/ (relative to repo)."""
    return guarded_write_workspace_file(relative_path, content)


@tool("read_workspace_file")
def read_workspace_file(relative_path: str) -> str:
    """Read a UTF-8 text file from allowed project subfolders."""
    return guarded_read_workspace_file(relative_path)


@tool("run_matplotlib_stub")
def run_matplotlib_stub(reason: str = "run") -> str:
    """Run the whitelisted stub script `scripts/plot_stub_m1.py` to emit a vector figure."""
    from articlebook.crew.workspace_sandbox import _root

    return run_matplotlib_stub_script(_root())


@tool("run_m3_asset_generators")
def run_m3_asset_generators(reason: str = "run") -> str:
    """Run `scripts/make_graph.py` and `scripts/make_image.py` (M3 FR-9 binaries)."""
    from articlebook.crew.workspace_sandbox import _root

    return run_m3_python_generators(_root())


@tool("verify_m3_assets")
def verify_m3_assets(reason: str = "check") -> str:
    """Pre-build check: graph.pdf, image.png, and includegraphics targets from M3 TeX."""
    from articlebook.crew.workspace_sandbox import _root

    ok, issues = verify_m3_figure_assets(_root())
    if ok:
        return "M3 asset check: OK"
    return "M3 asset check: FAIL — " + "; ".join(issues)


@tool("assemble_latex_document")
def assemble_latex_document(topic: str, language: str) -> str:
    """M4: Markdown chapters → ``latex/chapters/*.tex`` and regenerate ``main.tex``."""
    from articlebook.crew.workspace_sandbox import _root

    root = _root()
    inputs = validate_topic_language(topic, language)
    stems = assemble_latex_project(root, inputs)
    return f"Assembled LaTeX ({len(stems)} chapters + M3 showcase): " + ", ".join(stems)


@tool("run_lualatex_once")
def run_lualatex_once(reason: str = "run", log_filename: str = "m1_lualatex_once.log") -> str:
    """One LuaLaTeX pass on latex/main.tex into build/ (M1 smoke; M4 may pass log_filename)."""
    from articlebook.crew.workspace_sandbox import _root

    return compile_lualatex_once(_root(), log_filename=log_filename)


@tool("run_latex_canonical_compile")
def run_latex_canonical_compile(reason: str = "run", log_prefix: str = "m5_crew") -> str:
    """M5: LuaLaTeX/XeLaTeX + biber + extra passes until stable (plan.md §4)."""
    from articlebook.crew.workspace_sandbox import _root

    report = compile_latex_canonical(_root(), log_prefix=log_prefix)
    return compile_report_to_message(report)


@tool("run_m6_contract_checks")
def run_m6_contract_checks(reason: str = "qa", log_prefix: str = "m6_crew") -> str:
    """M6: deterministic FR-20 / prd §9 checks; writes ``build/m6_qa_report.{md,json}``."""
    from articlebook.crew.workspace_sandbox import _root

    root = _root()
    report = run_m6_contract_qa(root, log_prefix=log_prefix)
    return m6_contract_tool_reply(report, log_prefix)


def workspace_tools() -> list:
    """Tools shared across agents (bound root via bind_workspace_root)."""
    return [
        write_workspace_file,
        read_workspace_file,
        run_matplotlib_stub,
        run_m3_asset_generators,
        verify_m3_assets,
        assemble_latex_document,
        run_lualatex_once,
        run_latex_canonical_compile,
        run_m6_contract_checks,
    ]
