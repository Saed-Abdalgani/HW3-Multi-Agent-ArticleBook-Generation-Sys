"""Tests for bibliography contract alignment (M6 prep)."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from articlebook.bib_contract_align import (
    align_bib_with_tex_contract,
    merge_missing_stub_bib_entries,
)
from articlebook.m6_qa_parse import extract_cite_keys_from_tex, parse_bib_keys
from articlebook.m6_qa_parse import collect_tex_sources


def test_merge_missing_stub_bib_entries_appends_knuth(tmp_path: Path) -> None:
    latex = tmp_path / "latex"
    ch = latex / "chapters"
    ch.mkdir(parents=True)
    (latex / "main.tex").write_text("\\begin{document}\n\\end{document}\n", encoding="utf-8")
    (ch / "x.tex").write_text(r"\parencite{knuth1984texbook}", encoding="utf-8")
    (latex / "references.bib").write_text(
        "@article{khalidi2020,\n  author = {X},\n  title = {Y},\n  year = {2020}\n}\n",
        encoding="utf-8",
    )
    merged = merge_missing_stub_bib_entries(tmp_path)
    assert "knuth1984texbook" in merged
    bib = (latex / "references.bib").read_text(encoding="utf-8")
    assert "knuth1984texbook" in bib
    assert "khalidi2020" in bib
    keys = parse_bib_keys(bib)
    assert "knuth1984texbook" in keys and "khalidi2020" in keys


def test_align_normalizes_entry_type(tmp_path: Path) -> None:
    latex = tmp_path / "latex"
    ch = latex / "chapters"
    ch.mkdir(parents=True)
    (latex / "main.tex").write_text(
        "\\begin{document}\n\\backmatter\n\\end{document}\n", encoding="utf-8"
    )
    (ch / "c.tex").write_text(r"\parencite{khalidi2020}", encoding="utf-8")
    (latex / "references.bib").write_text(
        "@entry{rubenberg2020,\n  author = {R},\n  title = {T},\n  year = {2020}\n}\n",
        encoding="utf-8",
    )
    align_bib_with_tex_contract(tmp_path)
    bib = (latex / "references.bib").read_text(encoding="utf-8")
    assert "@misc{rubenberg2020" in bib
    bridge = ch / "_bib_orphan_bridge.tex"
    assert bridge.is_file()
    bridge_txt = bridge.read_text(encoding="utf-8")
    assert "rubenberg2020" in bridge_txt
    main_txt = (latex / "main.tex").read_text(encoding="utf-8")
    assert "\\input{chapters/_bib_orphan_bridge}" in main_txt
    blob = collect_tex_sources(latex)
    cites = extract_cite_keys_from_tex(blob)
    assert "khalidi2020" in cites


def test_cli_execution_returns_diag_on_m6_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    import argparse

    import articlebook.cli_execution as ce

    class QA:
        passed = False
        errors = ["bib:test_error"]

    monkeypatch.setattr(ce, "load_config_optional", lambda: {"api_key": "x"})
    monkeypatch.setattr(ce, "run_llm", lambda *a, **k: "crew_done")
    monkeypatch.setattr(ce, "run_m6_contract_qa", lambda *a, **k: QA())

    args = argparse.Namespace(
        milestone="m6",
        topic="t",
        language="English",
        dry_run=False,
        m6_allow_missing_pdf=True,
        m6_relax_page_count=False,
    )
    ok, _summary, qa_passed, diag = ce.run_articlebook_cli_body(
        args, logging.getLogger("test")
    )
    assert ok is False
    assert qa_passed is False
    assert diag is not None
    assert "bib:test_error" in diag
