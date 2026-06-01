"""Lightweight validation for agent-visible text between pipeline stages (M7)."""

from __future__ import annotations

from typing import Any


def validate_agent_text_output(
    text: Any,
    *,
    stage: str = "agent",
    min_chars: int = 1,
    max_chars: int = 1_000_000,
) -> str:
    """Return stripped text or raise if the payload is unusable for downstream tasks.

    Intended for tool summaries / task outputs that should be non-empty strings.
    """
    if not isinstance(text, str):
        msg = f"{stage}: expected str output, got {type(text).__name__}"
        raise TypeError(msg)
    s = text.strip()
    if len(s) < min_chars:
        msg = f"{stage}: output empty after strip (min_chars={min_chars})"
        raise ValueError(msg)
    if len(s) > max_chars:
        msg = f"{stage}: output exceeds max_chars={max_chars}"
        raise ValueError(msg)
    return s


def validate_agent_text_output_lenient(text: Any, *, stage: str = "agent") -> str | None:
    """Same as :func:`validate_agent_text_output` but returns ``None`` on failure (log-only)."""
    try:
        return validate_agent_text_output(text, stage=stage)
    except (TypeError, ValueError):
        return None
