"""Resolve LLM API keys from environment by provider (OpenAI vs Google Gemini)."""

from __future__ import annotations

import os


def _norm_provider(provider: str) -> str:
    return str(provider or "openai").strip().casefold()


def resolve_llm_api_key(provider: str) -> str | None:
    """Return the API key for ``provider``, or None if unset."""
    p = _norm_provider(provider)
    if p in {"google", "gemini", "google_genai", "vertex_ai", "vertex"}:
        return (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("ARTICLEBOOK_API_KEY")
        )
    if p in {"openai", "azure", "anthropic"}:
        return os.getenv("OPENAI_API_KEY") or os.getenv("ARTICLEBOOK_API_KEY")
    return (
        os.getenv("OPENAI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("ARTICLEBOOK_API_KEY")
    )


def missing_llm_api_key_message(provider: str) -> str:
    p = _norm_provider(provider)
    if p in {"google", "gemini", "google_genai", "vertex_ai", "vertex"}:
        return (
            "GOOGLE_API_KEY (or GEMINI_API_KEY) is required for Google/Gemini runs. "
            "Set it in the environment or .env (never commit secrets)."
        )
    return (
        "OPENAI_API_KEY is required for OpenAI-compatible runs. "
        "Set it in the environment or .env (never commit secrets)."
    )
