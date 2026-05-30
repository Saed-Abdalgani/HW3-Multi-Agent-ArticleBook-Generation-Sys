"""Repository and working-directory path resolution."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Return the repository root (directory containing `skills/` and `latex/`)."""
    # shared/paths.py -> articlebook/shared -> articlebook -> src -> root
    return Path(__file__).resolve().parents[3]


def skills_root() -> Path:
    return project_root() / "skills"
