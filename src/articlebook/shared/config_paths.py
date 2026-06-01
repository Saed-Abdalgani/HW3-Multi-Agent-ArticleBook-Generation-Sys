"""Resolve the directory holding ``models.yaml`` / ``agents.yaml`` / ``tasks.yaml``."""

from __future__ import annotations

import os
from pathlib import Path

from articlebook.shared.paths import project_root


def config_dir() -> Path:
    """Return ``ARTICLEBOOK_CONFIG_DIR`` or ``<repo>/config``."""
    env = os.environ.get("ARTICLEBOOK_CONFIG_DIR")
    if env:
        return Path(env).expanduser().resolve()
    return project_root() / "config"
