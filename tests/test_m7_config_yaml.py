"""M7 YAML config merge, overlays, and run stamp."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from articlebook.crew.agent_overrides import clear_agent_overlay_cache, merge_agent_fields
from articlebook.crew.task_overrides import clear_task_config_cache, resolve_task_strings
from articlebook.shared.config import load_config, load_models_document, write_resolved_run_stamp


def test_load_models_document_merges_defaults(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "models.yaml").write_text(
        yaml.safe_dump(
            {
                "version": "99",
                "model": "gpt-4o",
                "gatekeeper": {"retry_max_attempts": 2},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ARTICLEBOOK_CONFIG_DIR", str(cfg_dir))
    doc = load_models_document()
    assert doc["version"] == "99"
    assert doc["model"] == "gpt-4o"
    assert doc["gatekeeper"]["retry_max_attempts"] == 2
    assert doc["gatekeeper"]["instrumented"] is True


def test_write_resolved_run_stamp_writes_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "articlebook.shared.config.project_root",
        lambda: tmp_path,
    )
    cfg = {
        "provider": "openai",
        "model": "gpt-test",
        "temperature": 0.1,
        "seed": 3,
        "timeout": 9.0,
        "config_version": "1",
        "rag_enabled": False,
        "gatekeeper": {"instrumented": True},
    }
    path = write_resolved_run_stamp(cfg, milestone="m2")
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["model"] == "gpt-test"
    assert data["milestone"] == "m2"
    assert "api_key" not in data


def test_merge_agent_fields_overlay(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "agents.yaml").write_text(
        yaml.safe_dump(
            {
                "version": "1",
                "agents": {
                    "research": {
                        "role": "Patched role",
                        "skills": ["research-methodology", "house-culture"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ARTICLEBOOK_CONFIG_DIR", str(cfg_dir))
    clear_agent_overlay_cache()
    base = {
        "role": "Original",
        "goal": "G",
        "backstory": "B",
        "tools": [],
        "verbose": True,
        "skills": ["research-methodology"],
    }
    merged = merge_agent_fields("research", base)
    assert merged["role"] == "Patched role"
    assert merged["goal"] == "G"
    assert merged["skills"] == ["research-methodology", "house-culture"]


def test_resolve_task_strings_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "tasks.yaml").write_text(
        yaml.safe_dump(
            {
                "version": "1",
                "overrides": {
                    "m2": {
                        "research": {
                            "description": "Hello {topic} / {language}",
                            "expected_output": "OK {language}",
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ARTICLEBOOK_CONFIG_DIR", str(cfg_dir))
    clear_task_config_cache()
    d, e = resolve_task_strings(
        "m2",
        "research",
        default_description="DEF",
        default_expected_output="EXP",
        topic="T",
        language="L",
    )
    assert d == "Hello T / L"
    assert e == "OK L"


def test_load_config_env_overrides(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "models.yaml").write_text(
        yaml.safe_dump({"model": "from-yaml", "timeout_seconds": 5.0}),
        encoding="utf-8",
    )
    monkeypatch.setenv("ARTICLEBOOK_CONFIG_DIR", str(cfg_dir))
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("MODEL_NAME", "from-env")
    monkeypatch.setenv("ARTICLEBOOK_LLM_TIMEOUT_S", "77")
    cfg = load_config()
    assert cfg["model"] == "from-env"
    assert cfg["timeout"] == 77.0
