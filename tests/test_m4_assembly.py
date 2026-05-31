from __future__ import annotations

from pathlib import Path

from articlebook.inputs import validate_topic_language
from articlebook.m4_assembly import _convert_markdown_line, markdown_chapter_to_tex
from articlebook.m4_main_tex import write_main_tex


def test_pandoc_cite_to_parencite() -> None:
    assert "\\parencite{a,b}" in _convert_markdown_line("See [@a; @b] for details.")


def test_markdown_chapter_heading_and_label() -> None:
    md = "# Hello World\n\nBody.\n"
    tex = markdown_chapter_to_tex(
        md, chapter_label="ch:test", rtl_heavy=False
    )
    assert "\\chapter{Hello World}" in tex
    assert "\\label{ch:test}" in tex
    assert "Body" in tex


def test_bold_and_code_not_double_escaped() -> None:
    """Regression: \\textbf/\\texttt must not be re-escaped into literal text."""
    tex = _convert_markdown_line("Use **bold** and `code/here` now.")
    assert "\\textbf{bold}" in tex
    assert "\\texttt{code/here}" in tex
    assert "\\textbackslash" not in tex


def test_rtl_heavy_wraps_code_as_ltr_island() -> None:
    """Inline code becomes an explicit LTR island under RTL layout (FR-13)."""
    rtl = _convert_markdown_line("term `CrewAI` here", rtl_heavy=True)
    assert "\\textenglish{\\texttt{CrewAI}}" in rtl
    ltr = _convert_markdown_line("term `CrewAI` here", rtl_heavy=False)
    assert "\\texttt{CrewAI}" in ltr
    assert "\\textenglish" not in ltr


def test_main_tex_rtl_for_hebrew(tmp_path: Path) -> None:
    """FR-14: Hebrew drives a full RTL document; English stays LTR default."""
    (tmp_path / "latex").mkdir(parents=True)
    he = validate_topic_language("Topic", "Hebrew")
    write_main_tex(tmp_path, he, ["chapter_01_scope"])
    he_tex = (tmp_path / "latex" / "main.tex").read_text(encoding="utf-8")
    assert "\\setdefaultlanguage{hebrew}" in he_tex
    assert "\\setotherlanguage{english}" in he_tex

    en = validate_topic_language("Topic", "English")
    write_main_tex(tmp_path, en, ["chapter_01_scope"])
    en_tex = (tmp_path / "latex" / "main.tex").read_text(encoding="utf-8")
    assert "\\setdefaultlanguage{english}" in en_tex
    assert "\\setotherlanguage{hebrew}" in en_tex
