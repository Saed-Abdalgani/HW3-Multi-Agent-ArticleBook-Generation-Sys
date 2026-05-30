from __future__ import annotations

import yaml

from articlebook.shared.paths import skills_root


def _frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        raise AssertionError("missing front matter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise AssertionError("malformed front matter")
    return yaml.safe_load(parts[1]) or {}


def test_all_skills_parse() -> None:
    root = skills_root()
    for skill_dir in sorted(root.iterdir()):
        if not skill_dir.is_dir():
            continue
        md = skill_dir / "SKILL.md"
        if not md.is_file():
            continue
        data = _frontmatter(md.read_text(encoding="utf-8"))
        assert data.get("name"), f"{md} missing name"
        assert data.get("description"), f"{md} missing description"
        assert "metadata" in data, f"{md} missing metadata block"
