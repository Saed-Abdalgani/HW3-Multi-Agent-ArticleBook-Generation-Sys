"""Shared LaTeX / M3 steps for M4–M6 stub pipelines."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from articlebook.compile_multipass import compile_latex_canonical, compile_report_to_message
from articlebook.inputs import RunInputs
from articlebook.m2_stub import write_m2_stub_artifacts
from articlebook.m3_assets import run_m3_python_generators, write_m3_stub_manifest
from articlebook.m4_assembly import assemble_latex_project


def write_m3_figure_manifest(fig_dir: Path) -> None:
    manifest_lines = ["figures/graph.pdf", "figures/image.png"]
    fig_dir.mkdir(parents=True, exist_ok=True)
    (fig_dir / "m3_manifest.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")


def stub_latex_through_m5_driver(
    root: Path,
    inputs: RunInputs,
    *,
    log_prefix: str,
    manifest_writer: Callable[[Path, RunInputs, list[str], str], None],
) -> None:
    """M2 + M3 + M4 assembly + canonical multipass compile (``compile_latex_canonical``)."""
    write_m2_stub_artifacts(root, inputs)
    gen_log = run_m3_python_generators(root)
    write_m3_stub_manifest(root, inputs, gen_log)
    (root / "figures").mkdir(parents=True, exist_ok=True)
    write_m3_figure_manifest(root / "figures")
    stems = assemble_latex_project(root, inputs)
    report = compile_latex_canonical(root, log_prefix=log_prefix)
    manifest_writer(root, inputs, stems, compile_report_to_message(report))
