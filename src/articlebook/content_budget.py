"""Post-crew Markdown shaping so LaTeX/PDF stays near the M6 page band (15–20).

Crew agents sometimes finish with a ``Final Answer`` but never call write tools; stale
``content/chapter_*.md`` (especially stub-era repetition) can push ``build/main.pdf`` past
the contract. This module collapses obvious duplicate blocks and caps per-chapter words,
then :func:`articlebook.m4_assembly.assemble_latex_project` can be re-run safely.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from articlebook.m4_constants import CHAPTER_MD_GLOB


def _collapse_consecutive_duplicate_lines(markdown: str) -> str:
    """Drop consecutive duplicate non-empty lines (stub chapters often repeat one paragraph)."""
    lines = markdown.splitlines()
    out: list[str] = []
    prev_non_empty: str | None = None
    for line in lines:
        st = line.strip()
        if st and st == prev_non_empty:
            continue
        out.append(line)
        prev_non_empty = st if st else None
    return "\n".join(out)


def _collapse_consecutive_duplicate_blocks(markdown: str) -> str:
    """Drop consecutive duplicate non-empty paragraphs (double-newline separated)."""
    parts = re.split(r"\n\n+", markdown)
    out: list[str] = []
    last_sig: str | None = None
    for block in parts:
        sig = block.strip()
        if sig and sig == last_sig:
            continue
        out.append(block)
        last_sig = sig if sig else None
    body = "\n\n".join(out).strip()
    return body + "\n" if body else markdown


def _truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    clipped = " ".join(words[:max_words]).rstrip()
    return clipped + "\n\n_(Editorial note: chapter trimmed automatically to satisfy PDF page budget.)_\n"


def normalize_chapter_markdown_for_pdf_budget(markdown: str, *, max_words: int) -> str:
    """Collapse duplicate stub lines/blocks, then hard-cap word count."""
    step1 = _collapse_consecutive_duplicate_lines(markdown)
    collapsed = _collapse_consecutive_duplicate_blocks(step1)
    return _truncate_words(collapsed, max_words)


def max_words_per_chapter_from_env(default: int = 1000) -> int:
    raw = os.getenv("ARTICLEBOOK_MAX_WORDS_PER_CHAPTER", "").strip()
    if not raw:
        return default
    try:
        n = int(raw)
        return max(200, min(n, 5000))
    except ValueError:
        return default


def apply_chapter_markdown_pdf_budgets(root: Path, *, max_words: int | None = None) -> list[str]:
    """Rewrite ``content/chapter_*.md`` files in place when trimming applies.

    Returns relative POSIX paths that were modified (empty if none).
    """
    cap = max_words if max_words is not None else max_words_per_chapter_from_env()
    content = root / "content"
    if not content.is_dir():
        return []
    touched: list[str] = []
    for path in sorted(content.glob(CHAPTER_MD_GLOB)):
        if not path.is_file():
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        new = normalize_chapter_markdown_for_pdf_budget(raw, max_words=cap)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            touched.append(path.relative_to(root).as_posix())
    return touched


__all__ = [
    "apply_chapter_markdown_pdf_budgets",
    "max_words_per_chapter_from_env",
    "normalize_chapter_markdown_for_pdf_budget",
]
