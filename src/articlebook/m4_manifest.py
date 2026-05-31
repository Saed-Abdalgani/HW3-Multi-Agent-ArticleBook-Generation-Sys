"""M4 stub run manifest under ``build/``."""

from __future__ import annotations

from pathlib import Path

from articlebook.inputs import RunInputs


def write_m4_stub_manifest(
    root: Path, inputs: RunInputs, stems: list[str], compile_msg: str
) -> None:
    build = root / "build"
    build.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        [
            "# M4 stub manifest (LaTeX assembly)",
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
            "## One-pass compile (M4 exit; full passes in M5)",
            "",
            "```text",
            compile_msg.strip()[:6000],
            "```",
            "",
        ]
    )
    (build / "m4_stub_manifest.md").write_text(body, encoding="utf-8")
