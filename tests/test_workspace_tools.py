from __future__ import annotations

from pathlib import Path

import pytest

from articlebook.crew.workspace_tools import (
    bind_workspace_root,
    read_workspace_file,
    reset_workspace_root,
    write_workspace_file,
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


def test_read_whitelisted_root_docs() -> None:
    root = project_root()
    token = bind_workspace_root(root)
    try:
        text = read_workspace_file.run(relative_path="plan.md")  # type: ignore[attr-defined]
        assert "Phase M1" in text or "M1" in text
        assert "untrusted" in text.lower()
    finally:
        reset_workspace_root(token)
