"""Write ``latex/chapters/*.tex`` from ``content/chapter_*.md``."""

from __future__ import annotations

from pathlib import Path

from articlebook.inputs import RunInputs
from articlebook.m4_constants import CHAPTER_MD_GLOB
from articlebook.m4_md_to_tex import chapter_label_from_stem, markdown_chapter_to_tex


def discover_chapter_md(root: Path) -> list[Path]:
    content = root / "content"
    paths = sorted(content.glob(CHAPTER_MD_GLOB))
    return [p for p in paths if p.is_file()]


def write_chapter_tex_files(root: Path, inputs: RunInputs) -> list[str]:
    """Emit ``latex/chapters/<stem>.tex`` for each ``content/chapter_*.md``."""
    latex_ch = root / "latex" / "chapters"
    latex_ch.mkdir(parents=True, exist_ok=True)
    stems: list[str] = []
    for md_path in discover_chapter_md(root):
        stem = md_path.stem
        rtl = inputs.text_direction == "rtl" and "bidi" in stem.lower()
        tex = markdown_chapter_to_tex(
            md_path.read_text(encoding="utf-8"),
            chapter_label=chapter_label_from_stem(stem),
            rtl_heavy=rtl,
        )
        out_path = latex_ch / f"{stem}.tex"
        out_path.write_text(
            "% Auto-generated from Markdown (M4). Regenerate via pipeline.\n"
            f"% source: content/{md_path.name}\n\n" + tex,
            encoding="utf-8",
        )
        stems.append(stem)
    return stems
