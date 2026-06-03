"""M7 LLM API key resolution by provider."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from articlebook.shared.config import load_config


def test_load_config_google_provider_uses_google_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "models.yaml").write_text(
        yaml.safe_dump({"provider": "google", "model": "gemini/gemini-2.0-flash"}),
        encoding="utf-8",
    )
    monkeypatch.setenv("ARTICLEBOOK_CONFIG_DIR", str(cfg_dir))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "gsk_testkey012345678901234567890")
    cfg = load_config()
    assert cfg["provider"] == "google"
    assert cfg["api_key"] == "gsk_testkey012345678901234567890"
    assert "gemini" in cfg["model"]
