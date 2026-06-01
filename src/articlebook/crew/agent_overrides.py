"""Load optional agent field overrides from ``config/agents.yaml`` (M7)."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

import yaml

from articlebook.shared.config_paths import config_dir

log = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_agent_overlay() -> dict[str, dict[str, Any]]:
    path = config_dir() / "agents.yaml"
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        log.warning("agents.yaml root must be a mapping; ignoring")
        return {}
    agents = data.get("agents")
    if agents is None:
        return {}
    if not isinstance(agents, dict):
        log.warning("agents.yaml `agents` must be a mapping; ignoring")
        return {}
    return agents


def clear_agent_overlay_cache() -> None:
    load_agent_overlay.cache_clear()


def merge_agent_fields(agent_id: str, base: dict[str, Any]) -> dict[str, Any]:
    """Overlay YAML-defined role/goal/backstory/skills onto ``base`` Agent kwargs."""
    overlay = load_agent_overlay().get(agent_id)
    if not overlay:
        return dict(base)
    merged = dict(base)
    for key in ("role", "goal", "backstory"):
        if key in overlay and overlay[key] is not None:
            merged[key] = str(overlay[key]).strip()
    if "skills" in overlay and overlay["skills"] is not None:
        skills = overlay["skills"]
        if not isinstance(skills, list):
            log.warning("agents.yaml %s.skills must be a list; ignoring", agent_id)
        else:
            merged["skills"] = skills
    return merged
