"""Pytest fixtures shared across tests."""

from __future__ import annotations

import pytest

from articlebook.crew.agent_overrides import clear_agent_overlay_cache
from articlebook.crew.task_overrides import clear_task_config_cache


@pytest.fixture(autouse=True)
def _reset_m7_yaml_caches() -> None:
    """M7 YAML loaders use LRU caches; reset so tmp_path configs apply per test."""
    clear_agent_overlay_cache()
    clear_task_config_cache()
    yield
    clear_agent_overlay_cache()
    clear_task_config_cache()
