"""Load application configuration from YAML + environment (M7)."""

from __future__ import annotations

import json
import logging
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from articlebook.shared.config_paths import config_dir
from articlebook.shared.paths import project_root

load_dotenv()

log = logging.getLogger(__name__)


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for k, v in overlay.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = deepcopy(v)
    return out


def _load_yaml(name: str) -> dict[str, Any]:
    path: Path = config_dir() / name
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data if isinstance(data, dict) else {}


def _default_models_dict() -> dict[str, Any]:
    return {
        "version": "0",
        "provider": "openai",
        "model": "gpt-4-turbo",
        "temperature": 0.7,
        "seed": 42,
        "timeout_seconds": 120.0,
        "rag": {"enabled": False},
        "gatekeeper": {
            "instrumented": True,
            "retry_max_attempts": 4,
            "retry_base_delay_s": 0.8,
            "retry_max_delay_s": 30.0,
            "rate_limit_min_interval_s": 0.0,
        },
        "pricing_per_million_tokens": {
            "default": {"input": 0.0, "output": 0.0},
        },
    }


def load_models_document() -> dict[str, Any]:
    """Return merged ``models`` settings (YAML + sane defaults)."""
    merged = _default_models_dict()
    merged = _deep_merge(merged, _load_yaml("models.yaml"))
    return merged


def load_config() -> dict[str, Any]:
    """Return model/runtime settings and API key for LLM construction (M7)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        msg = "OPENAI_API_KEY is required for LLM crew runs (use --stub for offline placeholders)."
        raise ValueError(msg)
    doc = load_models_document()
    temperature = float(os.getenv("TEMPERATURE", str(doc.get("temperature", 0.7))))
    seed = int(os.getenv("SEED", str(doc.get("seed", 42))))
    model = os.getenv("MODEL_NAME", str(doc.get("model", "gpt-4-turbo")))
    provider = os.getenv("ARTICLEBOOK_LLM_PROVIDER", str(doc.get("provider", "openai")))
    timeout = float(
        os.getenv(
            "ARTICLEBOOK_LLM_TIMEOUT_S",
            str(doc.get("timeout_seconds", 120.0)),
        )
    )
    rag_enabled = doc.get("rag") or {}
    rag_flag = bool(rag_enabled.get("enabled", False))
    if os.getenv("ARTICLEBOOK_RAG_ENABLED", "").strip().casefold() in {"1", "true", "yes"}:
        rag_flag = True

    gate = dict(doc.get("gatekeeper") or {})
    g_env_attempts = os.getenv("ARTICLEBOOK_GK_RETRY_MAX")
    if g_env_attempts:
        gate["retry_max_attempts"] = int(g_env_attempts)
    g_env_interval = os.getenv("ARTICLEBOOK_GK_MIN_INTERVAL_S")
    if g_env_interval is not None:
        gate["rate_limit_min_interval_s"] = float(g_env_interval)

    cfg: dict[str, Any] = {
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
    return cfg


def load_config_optional() -> dict[str, Any] | None:
    """Return config dict if API key is set, else None."""
    if not os.getenv("OPENAI_API_KEY"):
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
