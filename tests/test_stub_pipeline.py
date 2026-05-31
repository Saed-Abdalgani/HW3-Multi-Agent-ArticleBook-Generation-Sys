from __future__ import annotations

from articlebook.pipeline import run_stub_m1, run_stub_m2
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
    ):
        assert expected in names
