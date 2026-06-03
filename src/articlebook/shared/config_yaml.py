"""YAML-backed model defaults and merge helpers (split from ``config`` for line budget)."""

from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from articlebook.shared.config_paths import config_dir


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
        "rag": {
            "enabled": False,
            "knowledge_dir": "knowledge",
            "chunk_size": 480,
            "chunk_overlap": 80,
            "top_k": 5,
            "persist_subdir": "rag_chroma",
        },
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


def rag_feature_enabled() -> bool:
    """True when M9-OPT local RAG is on (YAML ``rag.enabled`` or ``ARTICLEBOOK_RAG_ENABLED``)."""
    doc = load_models_document()
    rag_block = doc.get("rag") or {}
    flag = bool(rag_block.get("enabled", False))
    if os.getenv("ARTICLEBOOK_RAG_ENABLED", "").strip().casefold() in {"1", "true", "yes"}:
        flag = True
    return flag
