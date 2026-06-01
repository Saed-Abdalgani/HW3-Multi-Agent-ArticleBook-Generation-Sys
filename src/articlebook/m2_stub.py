"""Deterministic M2 content artifacts (outline, chapters, bibliography) for stub runs."""

from __future__ import annotations

from pathlib import Path

from articlebook.inputs import RunInputs
from articlebook.m2_stub_bib import bibtex_corpus
from articlebook.m2_stub_chapter_copy import chapter_bidi, chapter_body, research_md, review_gate
from articlebook.m2_stub_constants import PAGE_TARGET_HI, PAGE_TARGET_LO
from articlebook.m2_stub_outline import outline_md


def write_m2_stub_artifacts(root: Path, inputs: RunInputs) -> None:
    """Emit M2 stub artifacts: outline, research notes, chapters, `.bib`, review gate."""
    content = root / "content"
    latex = root / "latex"
    build = root / "build"
    for d in (content, latex, build):
        d.mkdir(parents=True, exist_ok=True)

    rtl = inputs.text_direction == "rtl"
    direction_label = "rtl" if rtl else "ltr"

    (content / "outline.md").write_text(
        outline_md(inputs.topic, inputs.language, direction_label), encoding="utf-8"
    )
    (content / "research_notes.md").write_text(
        research_md(inputs.topic, inputs.language), encoding="utf-8"
    )
    (latex / "references.bib").write_text(bibtex_corpus(), encoding="utf-8")
    (content / "REVIEW_GATE.md").write_text(review_gate(), encoding="utf-8")

    chapters = [
        ("chapter_01_scope.md", "Scope, audience, definitions", 1300, "[@knuth1984texbook]."),
        (
            "chapter_02_markdown_first.md",
            "Markdown-first authoring",
            1300,
            "[@markdownguide2024].",
        ),
        (
            "chapter_03_agents_and_crews.md",
            "Agents, crews, and task ordering",
            1700,
            "[@crewai2024docs; @short2024llm].",
        ),
        ("chapter_05_latex_path.md", "From Markdown to LaTeX", 750, "[@lamport1994latex]."),
        ("chapter_06_conclusion.md", "Conclusion and next steps", 750, ""),
    ]
    for fname, title, words, cite in chapters:
        hint = f"Citations: {cite}" if cite else "Summary only; citations already established."
        text = chapter_body(inputs.topic, title, words, hint)
        (content / fname).write_text(text, encoding="utf-8")

    (content / "chapter_04_bidi_technical_note.md").write_text(
        chapter_bidi(inputs.topic, inputs.language, rtl), encoding="utf-8"
    )

    manifest = [
        "# M2 stub manifest",
        "",
        f"- topic: {inputs.topic}",
        f"- language: {inputs.language}",
        f"- text_direction: {direction_label}",
        "",
        "## Files",
        "",
        "- `content/outline.md`",
        "- `content/research_notes.md`",
        "- `content/REVIEW_GATE.md`",
        "- `content/chapter_01_scope.md` … `chapter_06_conclusion.md`",
        "- `latex/references.bib`",
        "",
        f"## Page estimate: ~{5+5+6+4+3+3} pages (target {PAGE_TARGET_LO}–{PAGE_TARGET_HI})",
        "",
    ]
    (build / "m2_stub_manifest.md").write_text("\n".join(manifest), encoding="utf-8")
