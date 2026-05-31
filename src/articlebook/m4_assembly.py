"""M4 LaTeX assembly: orchestrate Markdown → .tex and ``main.tex``."""

from __future__ import annotations

from pathlib import Path

from articlebook.inputs import RunInputs
from articlebook.m4_chapters import write_chapter_tex_files
from articlebook.m4_main_tex import write_main_tex
from articlebook.m4_manifest import write_m4_stub_manifest
from articlebook.m4_md_to_tex import _convert_markdown_line, markdown_chapter_to_tex

__all__ = [
    "assemble_latex_project",
    "write_m4_stub_manifest",
    "markdown_chapter_to_tex",
    "_convert_markdown_line",
]


def assemble_latex_project(root: Path, inputs: RunInputs) -> list[str]:
    """Convert Markdown chapters, write ``main.tex``, return chapter stems."""
    stems = write_chapter_tex_files(root, inputs)
    if not stems:
        msg = "No content/chapter_*.md files found; run M2 stub or writer first."
        raise FileNotFoundError(msg)
    write_main_tex(root, inputs, stems)
    return stems
