"""Load application configuration from environment (no secrets in logs)."""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def load_config() -> dict[str, Any]:
    """Return model/runtime settings and API key for LLM construction."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        msg = "OPENAI_API_KEY is required for LLM crew runs (use --stub for offline placeholders)."
        raise ValueError(msg)
    return {
        "api_key": api_key,
        "model": os.getenv("MODEL_NAME", "gpt-4-turbo"),
        "temperature": float(os.getenv("TEMPERATURE", "0.7")),
        "seed": int(os.getenv("SEED", "42")),
    }


def load_config_optional() -> dict[str, Any] | None:
    """Return config dict if API key is set, else None."""
    if not os.getenv("OPENAI_API_KEY"):
        return None
    return load_config()
