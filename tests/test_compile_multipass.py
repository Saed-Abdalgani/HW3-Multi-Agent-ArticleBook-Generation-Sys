from __future__ import annotations

from pathlib import Path

from articlebook.compile_multipass import classify_compile_failure, needs_extra_engine_pass
from articlebook.latex_compile.runner import copy_bib_files_latex_to_build


def test_needs_extra_engine_pass_detects_rerun() -> None:
    assert needs_extra_engine_pass("Rerun to get cross-references right")
    assert needs_extra_engine_pass("Package biblatex Warning: Please (re)run Biber")
    assert not needs_extra_engine_pass("Output written on main.pdf")


def test_classify_failure_latex_error() -> None:
    assert (
        classify_compile_failure("! LaTeX Error: something obscure.", "")
        == "latex_error"
    )
    assert (
        classify_compile_failure("! LaTeX Error: undefined control sequence.", "")
        == "undefined_control_sequence"
    )


def test_classify_failure_missing_file() -> None:
    assert classify_compile_failure("error: file not found", "") == "missing_file"


def test_copy_bib_files_latex_to_build(tmp_path: Path) -> None:
    latex = tmp_path / "latex"
    build = tmp_path / "build"
    latex.mkdir()
    (latex / "references.bib").write_text(
        "@book{x, author={X}, title={Y}, year={2000}}\n", encoding="utf-8"
    )
    (latex / "extra.bib").write_text(
        "@book{z, author={Z}, title={W}, year={2001}}\n", encoding="utf-8"
    )
    copy_bib_files_latex_to_build(latex, build)
    assert (build / "references.bib").read_text(encoding="utf-8").startswith("@book{x")
    assert (build / "extra.bib").read_text(encoding="utf-8").startswith("@book{z")
