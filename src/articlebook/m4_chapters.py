"""Write ``latex/chapters/*.tex`` from ``content/chapter_*.md``."""

from __future__ import annotations

from pathlib import Path

from articlebook.inputs import RunInputs
from articlebook.m4_constants import CHAPTER_MD_GLOB
from articlebook.m4_md_to_tex import chapter_label_from_stem, markdown_chapter_to_tex

# Writer crew (M2+) emits these; stub / course templates use ``chapter_01_scope``-style names.
_TOPIC_CHAPTER_NAMES = tuple(f"chapter_{i}.md" for i in range(1, 7))
_BIDI_TEMPLATE = "chapter_04_bidi_technical_note.md"


def discover_chapter_md(root: Path) -> list[Path]:
    """Markdown sources to turn into ``latex/chapters/chapter_*.tex`` and ``\\input`` order.

    When **all six** topic files ``content/chapter_1.md`` … ``chapter_6.md`` exist, use those
    (PRD: coherent book on the topic), then append ``chapter_04_bidi_technical_note.md`` when
    present (FR-13 BiDi demo chapter from the course template). Otherwise keep lexicographic
    ``chapter_*.md`` (stub ``chapter_01_scope`` … ``chapter_06_conclusion`` layout).
    """
    content = root / "content"
    if not content.is_dir():
        return []
    topic_paths: list[Path] = []
    for name in _TOPIC_CHAPTER_NAMES:
        p = content / name
        if not p.is_file():
            topic_paths.clear()
            break
        topic_paths.append(p)
    if len(topic_paths) == 6:
        bidi = content / _BIDI_TEMPLATE
        if bidi.is_file():
            topic_paths.append(bidi)
        return topic_paths
    paths = sorted(content.glob(CHAPTER_MD_GLOB))
    return [p for p in paths if p.is_file()]


def write_chapter_tex_files(root: Path, inputs: RunInputs) -> list[str]:
    """Emit ``latex/chapters/<stem>.tex`` for each ``content/chapter_*.md``."""
    latex_ch = root / "latex" / "chapters"
    latex_ch.mkdir(parents=True, exist_ok=True)
    discovered = discover_chapter_md(root)
    stems_preview = [p.stem for p in discovered]
    stem_set = set(stems_preview)
    # Remove stale ``chapter_*.tex`` from a prior layout (e.g. template + topic) so PDF/QA
    # match the current discover set.
    for tex_path in latex_ch.glob("chapter_*.tex"):
        if tex_path.stem not in stem_set:
            tex_path.unlink(missing_ok=True)
    stems: list[str] = []
    for md_path in discovered:
        stem = md_path.stem
        rtl = inputs.text_direction == "rtl" and "bidi" in stem.lower()
        tex = markdown_chapter_to_tex(
            md_path.read_text(encoding="utf-8"),
            chapter_label=chapter_label_from_stem(stem),
            rtl_heavy=rtl,
        )
        if "bidi" in stem.lower() and inputs.text_direction == "ltr":
            tex += (
                "\n\n% M6 BiDi heuristic: explicit English environment (polyglossia).\n"
                "\\begin{english}\n"
                "English technical labels and citations in this chapter remain LTR.\n"
                "\\end{english}\n"
            )
        out_path = latex_ch / f"{stem}.tex"
        out_path.write_text(
            "% Auto-generated from Markdown (M4). Regenerate via pipeline.\n"
            f"% source: content/{md_path.name}\n\n" + tex,
            encoding="utf-8",
        )
        stems.append(stem)
    return stems
