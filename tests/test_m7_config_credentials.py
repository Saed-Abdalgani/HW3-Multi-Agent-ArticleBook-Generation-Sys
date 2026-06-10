"""M7 LLM API key resolution by provider."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from articlebook.shared.config import load_config
from articlebook.shared.config_credentials import parse_llm_routes_from_env, resolve_llm_api_keys


@pytest.fixture(autouse=True)
def _clear_llm_route_shortcuts(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "ARTICLEBOOK_OPENROUTER_KEY_SUFFIX",
        "ARTICLEBOOK_GROQ_KEY_SUFFIX",
        "ARTICLEBOOK_NVIDIA_KEY_SUFFIX",
        "ARTICLEBOOK_ROUTE_MODELS",
    ):
        monkeypatch.delenv(key, raising=False)


def test_resolve_llm_api_keys_openai_order_and_dedupe(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARTICLEBOOK_LLM_ROUTES", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY_3", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-a")
    monkeypatch.setenv("OPENAI_API_KEY_2", "sk-b")
    monkeypatch.setenv("OPENAI_API_KEY_3", "sk-c")
    assert resolve_llm_api_keys("openai") == ["sk-a", "sk-b", "sk-c"]
    monkeypatch.setenv("OPENAI_API_KEY_2", "sk-a")
    assert resolve_llm_api_keys("openai") == ["sk-a", "sk-c"]


def test_load_config_includes_api_keys(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "models.yaml").write_text(
        yaml.safe_dump({"provider": "openai", "model": "gpt-4-turbo"}),
        encoding="utf-8",
    )
    monkeypatch.setenv("ARTICLEBOOK_CONFIG_DIR", str(cfg_dir))
    monkeypatch.delenv("ARTICLEBOOK_LLM_PROVIDER", raising=False)
    monkeypatch.setenv("ARTICLEBOOK_LLM_ROUTES", "")
    monkeypatch.delenv("OPENAI_API_KEY_3", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.delenv("ARTICLEBOOK_LLM_MAX_TOKENS", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "primary")
    monkeypatch.setenv("OPENAI_API_KEY_2", "backup")
    cfg = load_config()
    assert cfg["api_key"] == "primary"
    assert cfg["api_keys"] == ["primary", "backup"]
    assert cfg["max_tokens"] == 8192


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
    monkeypatch.setenv("ARTICLEBOOK_LLM_ROUTES", "")
    monkeypatch.delenv("ARTICLEBOOK_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "gsk_testkey012345678901234567890")
    monkeypatch.setenv("GOOGLE_API_KEY_2", "gsk_secondkey012345678901234567")
    cfg = load_config()
    assert cfg["provider"] == "google"
    assert cfg["api_key"] == "gsk_testkey012345678901234567890"
    assert cfg["api_keys"][0] == "gsk_testkey012345678901234567890"
    assert cfg["api_keys"][1] == "gsk_secondkey012345678901234567"
    assert "gemini" in cfg["model"]


def test_parse_llm_routes_from_env_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARTICLEBOOK_LLM_ROUTES", raising=False)
    monkeypatch.setenv(
        "ARTICLEBOOK_LLM_ROUTES",
        " sk-or-1|openrouter/openai/gpt-4o ; gsk-2|groq/llama-3.3-70b-versatile ",
    )
    r = parse_llm_routes_from_env()
    assert r == [
        {"api_key": "sk-or-1", "model": "openrouter/openai/gpt-4o"},
        {"api_key": "gsk-2", "model": "groq/llama-3.3-70b-versatile"},
    ]
    assert resolve_llm_api_keys("google") == ["sk-or-1", "gsk-2"]


def test_load_config_llm_routes_overrides_model(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "models.yaml").write_text(
        yaml.safe_dump({"provider": "openai", "model": "gpt-4-turbo"}),
        encoding="utf-8",
    )
    monkeypatch.setenv("ARTICLEBOOK_CONFIG_DIR", str(cfg_dir))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ARTICLEBOOK_LLM_PROVIDER", raising=False)
    monkeypatch.setenv("MODEL_NAME", "ignored-when-routes")
    monkeypatch.setenv("ARTICLEBOOK_LLM_ROUTES", "aa|m-a;bb|m-b")
    cfg = load_config()
    assert cfg["provider"] == "openai"
    assert cfg["model"] == "m-a"
    assert cfg["llm_routes"][1]["model"] == "m-b"
    assert len(cfg["llm_routes"]) == 2


def test_parse_llm_routes_invalid_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARTICLEBOOK_LLM_ROUTES", "no-pipe-segment")
    with pytest.raises(ValueError, match="ARTICLEBOOK_LLM_ROUTES"):
        parse_llm_routes_from_env()


def test_key_suffixes_build_default_routes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARTICLEBOOK_LLM_ROUTES", raising=False)
    monkeypatch.setenv("ARTICLEBOOK_OPENROUTER_KEY_SUFFIX", "orx")
    monkeypatch.setenv("ARTICLEBOOK_GROQ_KEY_SUFFIX", "gqy")
    monkeypatch.setenv("ARTICLEBOOK_NVIDIA_KEY_SUFFIX", "nvz")
    r = parse_llm_routes_from_env()
    assert r is not None
    assert r[0]["api_key"] == "gsk_gqy"
    assert r[0]["model"] == "groq/llama-3.3-70b-versatile"
    assert r[1]["api_key"] == "sk-or-v1-orx"
    assert r[1]["model"] == "openrouter/openai/gpt-4o-mini"
    assert r[2]["api_key"] == "gsk_gqy"
    assert r[2]["model"] == "groq/meta-llama/llama-4-scout-17b-16e-instruct"


def test_key_suffixes_accept_prefixed_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARTICLEBOOK_LLM_ROUTES", raising=False)
    monkeypatch.setenv("ARTICLEBOOK_OPENROUTER_KEY_SUFFIX", "sk-or-v1-already")
    monkeypatch.setenv("ARTICLEBOOK_GROQ_KEY_SUFFIX", "gsk_already")
    monkeypatch.setenv("ARTICLEBOOK_NVIDIA_KEY_SUFFIX", "nvapi-already")
    r = parse_llm_routes_from_env()
    assert r is not None
    assert r[0]["api_key"] == "gsk_already"
    assert r[1]["api_key"] == "sk-or-v1-already"
    assert r[2]["api_key"] == "gsk_already"


def test_route_models_must_have_three_parts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARTICLEBOOK_LLM_ROUTES", raising=False)
    monkeypatch.setenv("ARTICLEBOOK_OPENROUTER_KEY_SUFFIX", "a")
    monkeypatch.setenv("ARTICLEBOOK_GROQ_KEY_SUFFIX", "b")
    monkeypatch.setenv("ARTICLEBOOK_NVIDIA_KEY_SUFFIX", "c")
    monkeypatch.setenv("ARTICLEBOOK_ROUTE_MODELS", "only-one")
    with pytest.raises(ValueError, match="ARTICLEBOOK_ROUTE_MODELS"):
        parse_llm_routes_from_env()


def test_route_models_slot3_nvidia_uses_nvidia_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARTICLEBOOK_LLM_ROUTES", raising=False)
    monkeypatch.setenv("ARTICLEBOOK_OPENROUTER_KEY_SUFFIX", "orx")
    monkeypatch.setenv("ARTICLEBOOK_GROQ_KEY_SUFFIX", "gqy")
    monkeypatch.setenv("ARTICLEBOOK_NVIDIA_KEY_SUFFIX", "nvz")
    monkeypatch.setenv(
        "ARTICLEBOOK_ROUTE_MODELS",
        "groq/llama-3.3-70b-versatile;openrouter/openai/gpt-4o-mini;nvidia_nim/meta/llama-3.1-70b-instruct",
    )
    r = parse_llm_routes_from_env()
    assert r is not None
    assert r[2]["api_key"] == "nvapi-nvz"
    assert r[2]["model"].startswith("nvidia_nim/")


def test_load_config_max_tokens_from_yaml(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "models.yaml").write_text(
        yaml.safe_dump({"provider": "openai", "model": "gpt-4-turbo", "max_tokens": 6000}),
        encoding="utf-8",
    )
    monkeypatch.setenv("ARTICLEBOOK_CONFIG_DIR", str(cfg_dir))
    monkeypatch.delenv("ARTICLEBOOK_LLM_MAX_TOKENS", raising=False)
    monkeypatch.setenv("ARTICLEBOOK_LLM_ROUTES", "")
    monkeypatch.delenv("ARTICLEBOOK_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "primary")
    cfg = load_config()
    assert cfg["max_tokens"] == 6000


def test_llm_routes_explicit_wins_over_suffixes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARTICLEBOOK_LLM_ROUTES", "full|m1;full2|m2")
    monkeypatch.setenv("ARTICLEBOOK_OPENROUTER_KEY_SUFFIX", "ignored")
    monkeypatch.setenv("ARTICLEBOOK_GROQ_KEY_SUFFIX", "ignored")
    monkeypatch.setenv("ARTICLEBOOK_NVIDIA_KEY_SUFFIX", "ignored")
    r = parse_llm_routes_from_env()
    assert len(r or []) == 2
