"""Token/cost heuristics and transient-error classification for the gatekeeper (M7)."""

from __future__ import annotations

from typing import Any

from crewai import LLM


def snapshot_usage(llm: LLM) -> dict[str, int]:
    raw = getattr(llm, "_token_usage", None)
    if not isinstance(raw, dict):
        return {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}
    return {
        "total_tokens": int(raw.get("total_tokens", 0)),
        "prompt_tokens": int(raw.get("prompt_tokens", 0)),
        "completion_tokens": int(raw.get("completion_tokens", 0)),
    }


def usage_delta(before: dict[str, int], after: dict[str, int]) -> dict[str, int]:
    return {k: max(0, after[k] - before[k]) for k in before}


def pricing_for_model(cfg: dict[str, Any], model: str) -> dict[str, float]:
    table = cfg.get("pricing_per_million_tokens") or {}
    if model in table and isinstance(table[model], dict):
        row = table[model]
        return {
            "input": float(row.get("input", 0.0)),
            "output": float(row.get("output", 0.0)),
        }
    default = table.get("default") or {}
    return {
        "input": float(default.get("input", 0.0)),
        "output": float(default.get("output", 0.0)),
    }


def estimate_cost_usd(delta: dict[str, int], pricing: dict[str, float]) -> float:
    """Rough cost from token deltas and per-million USD rates (logging only)."""
    p = delta.get("prompt_tokens", 0)
    c = delta.get("completion_tokens", 0)
    return (p * pricing["input"] + c * pricing["output"]) / 1_000_000.0


def is_transient_llm_error(exc: BaseException) -> bool:
    """Heuristic: retry only for likely-transient provider/network failures."""
    name = type(exc).__name__
    transient_names = {
        "RateLimitError",
        "InternalServerError",
        "APITimeoutError",
        "APIConnectionError",
        "APIError",
        "Timeout",
        "ReadTimeout",
        "ConnectTimeout",
        "ConnectError",
    }
    if name in transient_names:
        return True
    msg = str(exc).lower()
    needles = ("timeout", "rate limit", "429", "503", "502", "temporarily unavailable", "overloaded")
    return any(n in msg for n in needles)
