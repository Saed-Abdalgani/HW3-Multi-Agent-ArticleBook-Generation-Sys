from __future__ import annotations

from articlebook.pipeline import run_stub_m1
from articlebook.shared.paths import project_root
from articlebook.skills_inventory import list_discovered_skills


def test_stub_m1_writes_core_artifacts() -> None:
    run_stub_m1(topic="stub-topic", language="English")
    root = project_root()
    assert (root / "content" / "m1_research_notes.md").is_file()
    assert (root / "build" / "m1_qa_report.md").is_file()


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
