"""M6: PDF heuristics, secret scan, FR-9 / structure / BiDi surface checks."""

from __future__ import annotations

import re
from pathlib import Path

_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"OPENAI_API_KEY\s*=\s*['\"]?[^\s'\"]+"),
    re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*"),
)


def scan_build_for_secrets(build_dir: Path) -> list[str]:
    hits: list[str] = []
    if not build_dir.is_dir():
        return hits
    for path in sorted(build_dir.glob("*.log")) + sorted(build_dir.glob("*.json")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for rx in _SECRET_PATTERNS:
            if rx.search(text):
                hits.append(f"possible_secret:{path.name}")
                break
    return hits


def pdf_page_count(pdf_path: Path) -> int | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    try:
        reader = PdfReader(str(pdf_path))
        return len(reader.pages)
    except Exception:
        return None


def pdf_text_has_double_question(pdf_path: Path) -> bool | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    try:
        reader = PdfReader(str(pdf_path))
        chunks: list[str] = []
        for page in reader.pages[: min(30, len(reader.pages))]:
            t = page.extract_text() or ""
            chunks.append(t)
        return "??" in "\n".join(chunks)
    except Exception:
        return None


def fr9_source_checks(tex_blob: str, *, showcase_file_exists: bool) -> list[str]:
    issues: list[str] = []
    if not showcase_file_exists:
        issues.append("fr9:missing_m3_fr9_showcase.tex")
    if "\\begin{tikzpicture}" not in tex_blob and "\\tikz" not in tex_blob:
        issues.append("fr9:missing_tikz_diagram")
    if "\\includegraphics" not in tex_blob:
        issues.append("fr9:missing_includegraphics")
    if "\\begin{tabular}" not in tex_blob and "\\begin{tabularx}" not in tex_blob:
        issues.append("fr9:missing_tabular")
    if "\\begin{equation}" not in tex_blob and "\\begin{align}" not in tex_blob:
        issues.append("fr9:missing_amsmath_environment")
    return issues


def front_matter_list_checks(main_tex: str) -> list[str]:
    issues: list[str] = []
    if "\\listoffigures" not in main_tex:
        issues.append("structure:missing_listoffigures")
    if "\\listoftables" not in main_tex:
        issues.append("structure:missing_listoftables")
    return issues


def main_tex_structure_checks(main_tex: str) -> list[str]:
    issues: list[str] = []
    required = (
        ("\\begin{titlepage}", "structure:missing_titlepage"),
        ("\\tableofcontents", "structure:missing_toc"),
        ("\\pagestyle{fancy}", "structure:missing_fancyhdr_pagestyle"),
        ("\\printbibliography", "structure:missing_printbibliography"),
        ("\\usepackage{hyperref}", "structure:missing_hyperref"),
        ("polyglossia", "structure:missing_polyglossia"),
    )
    for needle, code in required:
        if needle not in main_tex:
            issues.append(code)
    if "hebrew" not in main_tex.lower():
        issues.append("bidi:hebrew_language_not_declared_in_main")
    return issues


def bidi_heuristic(tex_blob: str, content_dir: Path) -> list[str]:
    warns: list[str] = []
    bidi_md = content_dir / "chapter_04_bidi_technical_note.md"
    if not bidi_md.is_file():
        warns.append("bidi:missing_chapter_04_bidi_md")
    else:
        body = bidi_md.read_text(encoding="utf-8", errors="replace")
        if "עברית" not in body and "RTL" not in body and "rtl" not in body.lower():
            warns.append("bidi:chapter_04_lacks_expected_rtl_markers")
    if "\\textenglish" not in tex_blob and "\\begin{english}" not in tex_blob:
        warns.append("bidi:no_explicit_ltr_island_macro_found")
    return warns


__all__ = [
    "bidi_heuristic",
    "fr9_source_checks",
    "front_matter_list_checks",
    "main_tex_structure_checks",
    "pdf_page_count",
    "pdf_text_has_double_question",
    "scan_build_for_secrets",
]
