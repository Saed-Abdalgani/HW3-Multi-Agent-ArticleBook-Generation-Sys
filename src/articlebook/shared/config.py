"""Load application configuration from YAML + environment (M7)."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from articlebook.shared.config_credentials import (
    missing_llm_api_key_message,
    resolve_llm_api_key,
)
from articlebook.shared.config_yaml import load_models_document, rag_feature_enabled
from articlebook.shared.paths import project_root

load_dotenv()

log = logging.getLogger(__name__)

__all__ = [
    "load_config",
    "load_config_optional",
    "load_models_document",
    "rag_feature_enabled",
    "write_resolved_run_stamp",
]


def load_config() -> dict[str, Any]:
    """Return model/runtime settings and API key for LLM construction (M7)."""
    doc = load_models_document()
    provider = os.getenv("ARTICLEBOOK_LLM_PROVIDER", str(doc.get("provider", "openai")))
    api_key = resolve_llm_api_key(provider)
    if not api_key:
        raise ValueError(missing_llm_api_key_message(provider))
    temperature = float(os.getenv("TEMPERATURE", str(doc.get("temperature", 0.7))))
    seed = int(os.getenv("SEED", str(doc.get("seed", 42))))
    model = os.getenv("MODEL_NAME", str(doc.get("model", "gpt-4-turbo")))
    timeout = float(
        os.getenv(
            "ARTICLEBOOK_LLM_TIMEOUT_S",
            str(doc.get("timeout_seconds", 120.0)),
        )
    )
    rag_flag = rag_feature_enabled()

    gate = dict(doc.get("gatekeeper") or {})
    g_env_attempts = os.getenv("ARTICLEBOOK_GK_RETRY_MAX")
    if g_env_attempts:
        gate["retry_max_attempts"] = int(g_env_attempts)
    g_env_interval = os.getenv("ARTICLEBOOK_GK_MIN_INTERVAL_S")
    if g_env_interval is not None:
        gate["rate_limit_min_interval_s"] = float(g_env_interval)

    return {
        "api_key": api_key,
        "model": model,
        "temperature": temperature,
        "seed": seed,
        "provider": provider,
        "timeout": timeout,
        "rag_enabled": rag_flag,
        "config_version": str(doc.get("version", "0")),
        "gatekeeper": gate,
        "pricing_per_million_tokens": doc.get("pricing_per_million_tokens") or {},
    }


def load_config_optional() -> dict[str, Any] | None:
    """Return config dict if the required API key for the active provider is set."""
    doc = load_models_document()
    provider = os.getenv("ARTICLEBOOK_LLM_PROVIDER", str(doc.get("provider", "openai")))
    if resolve_llm_api_key(provider) is None:
        return None
    return load_config()


def write_resolved_run_stamp(cfg: dict[str, Any], *, milestone: str) -> Path:
    """Write redacted resolved config next to artifacts (under ``build/``)."""
    root = project_root()
    build = root / "build"
    build.mkdir(parents=True, exist_ok=True)
    path = build / "resolved_run_config.json"
    payload = {
        "milestone": milestone,
        "provider": cfg.get("provider"),
        "model": cfg.get("model"),
        "temperature": cfg.get("temperature"),
        "seed": cfg.get("seed"),
        "timeout_s": cfg.get("timeout"),
        "config_version": cfg.get("config_version"),
        "rag_enabled": cfg.get("rag_enabled"),
        "gatekeeper": {k: v for k, v in (cfg.get("gatekeeper") or {}).items() if "secret" not in k},
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    log.info("run.stamp written path=%s", path)
    return path
