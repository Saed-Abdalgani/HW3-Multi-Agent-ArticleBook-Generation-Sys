from __future__ import annotations

from pathlib import Path

import pytest

from articlebook.crew.workspace_tools import (
    bind_workspace_root,
    read_workspace_file,
    reset_workspace_root,
    write_workspace_file,
    write_workspace_files_batch,
)
from articlebook.shared.paths import project_root


def test_project_root_contains_skills() -> None:
    root = project_root()
    assert (root / "skills").is_dir()
    assert (root / "latex" / "main.tex").is_file()


def test_workspace_tools_reject_traversal(tmp_path: Path) -> None:
    token = bind_workspace_root(tmp_path)
    try:
        (tmp_path / "content").mkdir(parents=True, exist_ok=True)
        with pytest.raises(ValueError):
            write_workspace_file.run(  # type: ignore[attr-defined]
                relative_path="content/../../secret.txt", content="nope"
            )
    finally:
        reset_workspace_root(token)


def test_write_workspace_files_batch(tmp_path: Path) -> None:
    token = bind_workspace_root(tmp_path)
    try:
        (tmp_path / "content").mkdir(parents=True, exist_ok=True)
        payload = (
            '[{"relative_path": "content/a.md", "content": "# A"},'
            '{"relative_path": "content/b.md", "content": "# B"}]'
        )
        msg = write_workspace_files_batch.run(files_json=payload)  # type: ignore[attr-defined]
        assert "Wrote" in msg
        assert (tmp_path / "content" / "a.md").read_text(encoding="utf-8") == "# A"
        assert (tmp_path / "content" / "b.md").read_text(encoding="utf-8") == "# B"
    finally:
        reset_workspace_root(token)


def test_write_rejects_build_compiler_artifacts(tmp_path: Path) -> None:
    token = bind_workspace_root(tmp_path)
    try:
        (tmp_path / "build").mkdir()
        for rel in (
            "build/main.tex",
            "build/main.pdf",
            "build/main.bbl",
            "build/m6_crew_pass01_lualatex.log",
        ):
            with pytest.raises(ValueError, match="Refusing"):
                write_workspace_file.run(relative_path=rel, content="x")  # type: ignore[attr-defined]
        (tmp_path / "build" / "m6_qa_report.md").write_text("old", encoding="utf-8")
        out = write_workspace_file.run(  # type: ignore[attr-defined]
            relative_path="build/m6_qa_report.md", content="# ok\n"
        )
        assert "Wrote" in out
    finally:
        reset_workspace_root(token)
    root = project_root()
    token = bind_workspace_root(root)
    try:
        text = read_workspace_file.run(relative_path="plan.md")  # type: ignore[attr-defined]
        assert "Phase M1" in text or "M1" in text
        assert "untrusted" in text.lower()
    finally:
        reset_workspace_root(token)
