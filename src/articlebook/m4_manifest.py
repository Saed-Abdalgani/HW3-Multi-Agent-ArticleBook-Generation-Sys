"""M4 stub run manifest under ``build/``."""

from __future__ import annotations

from pathlib import Path

from articlebook.inputs import RunInputs


def write_m4_stub_manifest(
    root: Path,
    inputs: RunInputs,
    stems: list[str],
    compile_msg: str,
    *,
    manifest_filename: str = "m4_stub_manifest.md",
    compile_section_title: str = "## Canonical multi-pass compile (M5 driver)",
) -> None:
    build = root / "build"
    build.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        [
            "# Stub manifest (LaTeX assembly + compile)",
            "",
            f"- topic: {inputs.topic}",
            f"- language: {inputs.language}",
            f"- text_direction: {inputs.text_direction}",
            "",
            "## Generated TeX",
            "",
            "- `latex/main.tex`",
            *[f"- `latex/chapters/{s}.tex`" for s in stems],
            "- `latex/chapters/m3_fr9_showcase.tex` (M3 FR-9, included)",
            "",
            compile_section_title,
            "",
            "Per-pass logs and `*_compile_journal.json` live under `build/`.",
            "",
            "```text",
            compile_msg.strip()[:6000],
            "```",
            "",
        ]
    )
    (build / manifest_filename).write_text(body, encoding="utf-8")


def write_m5_stub_manifest(
    root: Path, inputs: RunInputs, stems: list[str], compile_msg: str
) -> None:
    """M5 milestone record (same tree as M4 stub; distinct manifest filename)."""
    write_m4_stub_manifest(
        root,
        inputs,
        stems,
        compile_msg,
        manifest_filename="m5_stub_manifest.md",
        compile_section_title="## M5 exit — canonical compile + biber + stabilization",
    )
