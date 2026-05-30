"""Programmatic skill discovery (alternative to attaching paths on each Agent)."""

from __future__ import annotations

from pathlib import Path

from crewai.skills import discover_skills

from articlebook.shared.paths import skills_root


def list_discovered_skills(base: Path | None = None) -> list[str]:
    """Return skill names discovered under ``skills/`` (metadata-only scan)."""
    root = base or skills_root()
    skills = discover_skills(root)
    return sorted({s.name for s in skills})
