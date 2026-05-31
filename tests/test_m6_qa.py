"""Tests for M6 deterministic QA (citation/bib parsing and contract runner)."""

from __future__ import annotations

from pathlib import Path

from articlebook.m6_qa import (
    extract_cite_keys_from_tex,
    parse_bib_keys,
    run_m6_contract_qa,
)
from articlebook.pipeline import run_stub_m6
from articlebook.shared.paths import project_root


def test_parse_bib_keys_basic() -> None:
    bib = "@book{knuth1984texbook,\n  author = {Knuth},\n}\n@misc{x2024,\n title={t},\n}\n"
    keys = parse_bib_keys(bib)
    assert keys == {"knuth1984texbook", "x2024"}


def test_extract_cite_keys_parencite_mult() -> None:
    tex = r"Intro \parencite{a,b} and \textcite{c}."
    assert extract_cite_keys_from_tex(tex) == {"a", "b", "c"}


def test_run_m6_contract_qa_detects_missing_bib_key(tmp_path: Path) -> None:
    root = tmp_path
    (root / "latex").mkdir(parents=True)
    (root / "latex" / "main.tex").write_text(
        "\\begin{document}\\parencite{missing}\\end{document}", encoding="utf-8"
    )
    (root / "latex" / "references.bib").write_text("@book{a,\n author={A},\n}\n", encoding="utf-8")
    (root / "content").mkdir()
    (root / "content" / "chapter_04_bidi_technical_note.md").write_text(
        "# BiDi\n\nעברית\n", encoding="utf-8"
    )
    (root / "build").mkdir()
    r = run_m6_contract_qa(root, allow_missing_pdf=True)
    assert any("bib:cite_key_missing_in_bib:missing" in e for e in r.errors)


def test_stub_m6_smoke_with_relaxed_pdf() -> None:
    """CI-friendly: static checks + QA reports without requiring MiKTeX."""
    ok = run_stub_m6("M6 smoke", language="English", allow_missing_pdf=True)
    root = project_root()
    assert (root / "build" / "m6_qa_report.md").is_file()
    assert (root / "build" / "m6_stub_manifest.md").is_file()
    assert isinstance(ok, bool)
