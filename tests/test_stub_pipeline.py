from __future__ import annotations

from articlebook.m4_chapters import discover_chapter_md
from articlebook.pipeline_stubs import (
    run_stub_m1,
    run_stub_m2,
    run_stub_m3,
    run_stub_m4,
    run_stub_m5,
)
from articlebook.shared.paths import project_root
from articlebook.skills_inventory import list_discovered_skills


def test_stub_m1_writes_core_artifacts() -> None:
    run_stub_m1(topic="stub-topic", language="English")
    root = project_root()
    assert (root / "content" / "m1_research_notes.md").is_file()
    assert (root / "build" / "m1_qa_report.md").is_file()


def test_stub_m2_writes_outline_chapters_and_bib() -> None:
    run_stub_m2(topic="Multi-Agent Publishing", language="Hebrew")
    root = project_root()
    assert (root / "content" / "outline.md").is_file()
    assert (root / "content" / "research_notes.md").is_file()
    assert (root / "content" / "chapter_04_bidi_technical_note.md").is_file()
    assert (root / "latex" / "references.bib").is_file()
    bib = (root / "latex" / "references.bib").read_text(encoding="utf-8")
    assert "knuth1984texbook" in bib
    bidi = (root / "content" / "chapter_04_bidi_technical_note.md").read_text(encoding="utf-8")
    assert "CrewAI" in bidi or "crewai" in bidi.lower()
    assert (root / "build" / "m2_stub_manifest.md").is_file()


def test_stub_m3_runs_after_m2_artifacts() -> None:
    run_stub_m3(topic="Figures QA", language="Hebrew")
    root = project_root()
    assert (root / "content" / "outline.md").is_file()
    assert (root / "figures" / "m3_manifest.txt").is_file()


def test_stub_m4_assembles_main_tex() -> None:
    run_stub_m4(topic="LaTeX Assembly", language="English")
    root = project_root()
    main = (root / "latex" / "main.tex").read_text(encoding="utf-8")
    assert "biblatex" in main
    assert "cleveref" in main
    assert "fancyhdr" in main
    assert "printbibliography" in main
    md_chapters = discover_chapter_md(root)
    assert md_chapters, "expected markdown chapters after stub m4"
    assert (root / "latex" / "chapters" / f"{md_chapters[0].stem}.tex").is_file()
    assert "\\input{chapters/m3_fr9_showcase}" in main
    assert (root / "build" / "m4_stub_manifest.md").is_file()
    manifest = (root / "build" / "m4_stub_manifest.md").read_text(encoding="utf-8")
    assert "engine=" in manifest and "journal=" in manifest
    assert (root / "build" / "m4_compile_journal.json").is_file()


def test_stub_m5_writes_m5_manifest() -> None:
    run_stub_m5(topic="M5 Compile", language="English")
    root = project_root()
    assert (root / "build" / "m5_stub_manifest.md").is_file()
    assert (root / "build" / "m5_compile_journal.json").is_file()


def test_stub_m4_chapter_md_count_matches_generated_tex() -> None:
    """M6.4 proxy: one assembled TeX per Markdown chapter (outline-driven structure)."""
    run_stub_m4(topic="Hierarchy check", language="English")
    root = project_root()
    md_chapters = discover_chapter_md(root)
    tex_chapters = sorted((root / "latex" / "chapters").glob("chapter_*.tex"))
    assert len(tex_chapters) == len(md_chapters)


def test_discover_skills_names() -> None:
    names = list_discovered_skills()
    for expected in (
        "technical-writing",
        "bidi-hebrew",
        "latex-authoring",
        "figure-generation",
        "qa-checklist",
        "research-methodology",
        "document-structure",
        "house-culture",
        "local-rag",
        "security-review",
    ):
        assert expected in names
