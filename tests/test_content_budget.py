from __future__ import annotations

from pathlib import Path

from articlebook.content_budget import (
    apply_chapter_markdown_pdf_budgets,
    normalize_chapter_markdown_for_pdf_budget,
)


def test_duplicate_lines_collapse() -> None:
    body = "A\n" + ("Same line.\n" * 8) + "\nTail."
    out = normalize_chapter_markdown_for_pdf_budget(body, max_words=500)
    assert out.count("Same line.") == 1


def test_word_cap_inserts_note() -> None:
    words = " ".join(f"w{i}" for i in range(600))
    out = normalize_chapter_markdown_for_pdf_budget(words, max_words=50)
    assert "w49" in out
    assert "w50" not in out
    assert "PDF page budget" in out


def test_apply_chapter_markdown_pdf_budgets_writes(tmp_path: Path) -> None:
    (tmp_path / "content").mkdir()
    dup = "# T\n\n" + ("para.\n\n" * 5) + "end."
    (tmp_path / "content" / "chapter_01_scope.md").write_text(dup, encoding="utf-8")
    touched = apply_chapter_markdown_pdf_budgets(tmp_path, max_words=500)
    assert "content/chapter_01_scope.md" in touched
    new = (tmp_path / "content" / "chapter_01_scope.md").read_text(encoding="utf-8")
    assert new.count("para.") <= 2
