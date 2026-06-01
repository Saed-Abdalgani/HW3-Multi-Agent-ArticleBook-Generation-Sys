"""Load optional task description overrides from ``config/tasks.yaml`` (M7)."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

import yaml

from articlebook.shared.config_paths import config_dir

log = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_task_config_raw() -> dict[str, Any]:
    path = config_dir() / "tasks.yaml"
    if not path.is_file():
        return {"version": "0", "overrides": {}}
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        log.warning("tasks.yaml root must be a mapping; ignoring")
        return {"version": "0", "overrides": {}}
    return data


def clear_task_config_cache() -> None:
    """Test helper: reset :func:`load_task_config_raw` LRU cache."""
    load_task_config_raw.cache_clear()


def resolve_task_strings(
    milestone: str,
    task_key: str,
    *,
    default_description: str,
    default_expected_output: str,
    topic: str,
    language: str,
) -> tuple[str, str]:
    """Return description + expected_output, substituting ``{topic}`` / ``{language}``."""
    raw = load_task_config_raw()
    overrides = raw.get("overrides") or {}
    m = overrides.get(milestone) or {}
    entry = m.get(task_key) or {}
    desc = entry.get("description", default_description)
    exp = entry.get("expected_output", default_expected_output)
    ctx = {"topic": topic, "language": language}

    def _fmt(s: str) -> str:
        try:
            return s.format(**ctx)
        except (KeyError, ValueError):
            return s

    return _fmt(desc), _fmt(exp)
