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
    parse_llm_routes_from_env,
    resolve_llm_api_key,
    resolve_llm_api_keys,
)
from articlebook.shared.config_yaml import load_models_document, rag_feature_enabled
from articlebook.shared.paths import project_root

# Load repo-root `.env` first so API keys resolve even when the shell cwd is not
# the project directory (plain `load_dotenv()` only searches the cwd by default).
_env_path = project_root() / ".env"
load_dotenv(_env_path)
load_dotenv()  # optional cwd `.env` for local overrides (does not override existing keys)

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
    routes = parse_llm_routes_from_env()
    if routes:
        # LiteLLM resolves the real upstream from each slot's ``model`` prefix (``openrouter/``,
        # ``groq/``, ``nvidia_nim/``, …). Keep YAML/env ``provider`` aligned with that path.
        provider = "openai"
        api_keys = [str(r["api_key"]) for r in routes]
        api_key = api_keys[0]
        model = str(routes[0]["model"])
        llm_routes = routes
    else:
        api_keys = resolve_llm_api_keys(provider)
        if not api_keys:
            raise ValueError(missing_llm_api_key_message(provider))
        api_key = api_keys[0]
        model = os.getenv("MODEL_NAME", str(doc.get("model", "gpt-4-turbo")))
        llm_routes: list[dict[str, str]] = []
    temperature = float(os.getenv("TEMPERATURE", str(doc.get("temperature", 0.7))))
    seed = int(os.getenv("SEED", str(doc.get("seed", 42))))
    timeout = float(
        os.getenv(
            "ARTICLEBOOK_LLM_TIMEOUT_S",
            str(doc.get("timeout_seconds", 120.0)),
        )
    )
    max_tokens_raw = os.getenv("ARTICLEBOOK_LLM_MAX_TOKENS", "").strip()
    if max_tokens_raw:
        max_tokens = int(max_tokens_raw)
    else:
        mt_doc = doc.get("max_tokens", doc.get("max_completion_tokens"))
        max_tokens = int(mt_doc) if mt_doc is not None else 8192
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
        "api_keys": api_keys,
        "model": model,
        "llm_routes": llm_routes,
        "temperature": temperature,
        "seed": seed,
        "provider": provider,
        "timeout": timeout,
        "max_tokens": max(256, min(max_tokens, 128_000)),
        "rag_enabled": rag_flag,
        "config_version": str(doc.get("version", "0")),
        "gatekeeper": gate,
        "pricing_per_million_tokens": doc.get("pricing_per_million_tokens") or {},
    }


def load_config_optional() -> dict[str, Any] | None:
    """Return config dict if the required API key for the active provider is set."""
    doc = load_models_document()
    provider = os.getenv("ARTICLEBOOK_LLM_PROVIDER", str(doc.get("provider", "openai")))
    if parse_llm_routes_from_env():
        return load_config()
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
        "llm_routes_slots": len(cfg.get("llm_routes") or []),
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
