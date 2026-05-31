from __future__ import annotations

from articlebook.compile_multipass import classify_compile_failure, needs_extra_engine_pass


def test_needs_extra_engine_pass_detects_rerun() -> None:
    assert needs_extra_engine_pass("Rerun to get cross-references right")
    assert needs_extra_engine_pass("Package biblatex Warning: Please (re)run Biber")
    assert not needs_extra_engine_pass("Output written on main.pdf")


def test_classify_failure_latex_error() -> None:
    assert (
        classify_compile_failure("! LaTeX Error: undefined control sequence.", "")
        == "latex_error"
    )


def test_classify_failure_missing_file() -> None:
    assert classify_compile_failure("error: file not found", "") == "missing_file"
