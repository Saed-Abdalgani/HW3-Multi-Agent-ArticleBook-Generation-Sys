from __future__ import annotations

from pathlib import Path

from articlebook.m3_assets import verify_m3_figure_assets
from articlebook.pipeline import run_stub_m3
from articlebook.shared.paths import project_root


def test_verify_m3_figure_assets_happy_tmp(tmp_path: Path) -> None:
    (tmp_path / "figures").mkdir(parents=True)
    (tmp_path / "figures" / "graph.pdf").write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    (tmp_path / "figures" / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0" * 64)
    latex = tmp_path / "latex" / "chapters"
    latex.mkdir(parents=True)
    (latex / "m3_fr9_showcase.tex").write_text(
        "\\includegraphics{../figures/graph.pdf}\n"
        "\\includegraphics{../figures/image.png}\n",
        encoding="utf-8",
    )
    ok, issues = verify_m3_figure_assets(tmp_path)
    assert ok
    assert issues == []


def test_verify_m3_figure_assets_detects_missing(tmp_path: Path) -> None:
    (tmp_path / "figures").mkdir(parents=True)
    (tmp_path / "figures" / "graph.pdf").write_bytes(b"x")
    latex = tmp_path / "latex" / "chapters"
    latex.mkdir(parents=True)
    (latex / "m3_fr9_showcase.tex").write_text(
        "\\includegraphics{../figures/graph.pdf}\n"
        "\\includegraphics{../figures/missing.png}\n",
        encoding="utf-8",
    )
    ok, issues = verify_m3_figure_assets(tmp_path)
    assert not ok
    assert any("missing:figures/image.png" in i for i in issues)
    assert any("missing_graphics" in i for i in issues)


def test_stub_m3_writes_m2_plus_figures() -> None:
    run_stub_m3(topic="M3 Stub Topic", language="English")
    root = project_root()
    assert (root / "figures" / "graph.pdf").is_file()
    assert (root / "figures" / "image.png").is_file()
    assert (root / "figures" / "graph.pdf").stat().st_size > 100
    assert (root / "figures" / "image.png").stat().st_size > 100
    assert (root / "build" / "m3_stub_manifest.md").is_file()
    ok, _ = verify_m3_figure_assets(root)
    assert ok
