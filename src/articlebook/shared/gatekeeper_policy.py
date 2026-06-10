"""Token/cost heuristics and transient-error classification for the gatekeeper (M7)."""

from __future__ import annotations

import re
from typing import Any

from crewai import LLM

# Groq JSON / prose: ``Please try again in 10.402s`` (TPM/RPM rolling window).
_GROQ_TRY_AGAIN_IN_SECONDS = re.compile(
    r"try\s+again\s+in\s+(\d+(?:\.\d+)?)\s*s\b",
    re.IGNORECASE,
)


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


def _credit_or_quota_exhaustion_message(msg: str) -> bool:
    """Billing / prepaid credits exhausted — fail over to another route; same-slot backoff is useless."""
    m = msg.casefold()
    if "402" in m:
        return True
    needles = (
        "more credits",
        "fewer max_tokens",
        "can only afford",
        "insufficient credits",
        "not enough credits",
        "payment required",
        "credit balance",
        "requires more credits",
    )
    return any(n in m for n in needles)


def _provider_throttle_or_quota_message(msg: str) -> bool:
    """HTTP / body hints that another API key or route should be tried (throttle or billing)."""
    if _credit_or_quota_exhaustion_message(msg):
        return True
    m = msg.casefold()
    if "429" in m:
        return True
    needles = (
        "rate limit",
        "ratelimit",
        "too many requests",
        "resource exhausted",
        "quota exceeded",
        "requests per min",
        "tpm",
        "rpm",
    )
    return any(n in m for n in needles)


def is_rate_limit_llm_error(exc: BaseException) -> bool:
    """True when failing over to the next route/key is appropriate (429, throttles, out of credits)."""
    name = type(exc).__name__
    if name in {"RateLimitError"}:
        return True
    return _provider_throttle_or_quota_message(str(exc))


def is_llm_route_failover_error(exc: BaseException) -> bool:
    """True when the next configured ``key|model`` route should be tried.

    Includes throttles/credits (:func:`is_rate_limit_llm_error`) and Groq-style
    ``tool_use_failed`` (model emitted tool XML / invalid tool args that other
    providers accept via OpenAI-compatible tool_calls), and NVIDIA NIM
    **single-tool-only** rejections when CrewAI issues parallel tool calls.
    """
    if is_rate_limit_llm_error(exc):
        return True
    msg = str(exc).casefold()
    if "tool_use_failed" in msg:
        return True
    if "failed to call a function" in msg:
        return True
    if "single tool" in msg:
        return True
    return False


def provider_suggested_retry_delay_seconds(exc: BaseException) -> float | None:
    """Lower bound for backoff when the provider names a wait (e.g. Groq TPM).

    Returns ``None`` if no hint is found. Values are clamped to a sane range.
    """
    m = _GROQ_TRY_AGAIN_IN_SECONDS.search(str(exc))
    if not m:
        return None
    try:
        sec = float(m.group(1))
    except ValueError:
        return None
    if sec <= 0.0 or sec > 3600.0:
        return None
    # Slightly above the stated window so the rolling TPM bucket has cleared.
    return sec + 0.35


def should_reset_llm_route_chain_on_transient(exc: BaseException) -> bool:
    """After a transient error, restart from route slot 0 (not last slot).

    Groq may reject an oversized request on low-TPM models (e.g. ``llama-3.1-8b-instant``)
    with ``RateLimitError`` / ``request too large`` while a larger TPM route (slot 1)
    recovers after backoff. **Do not** use this for generic 429/503 on the last slot —
    that would ping-pong forever (see ``test_instrumented_llm_transient_retry_keeps_current_route``).
    """
    m = str(exc).casefold()
    return "request too large" in m or "reduce your message size" in m


def is_transient_llm_error(exc: BaseException) -> bool:
    """Heuristic: retry only for likely-transient provider/network failures."""
    msg_all = str(exc)
    # Credit exhaustion: either the next route handles it, or the call should fail without useless backoff.
    if _credit_or_quota_exhaustion_message(msg_all):
        return False
    # Groq tool_use_failed: retry/backoff on the same slot does not fix bad tool XML — failover or fail.
    mlow = msg_all.casefold()
    if "tool_use_failed" in mlow or "failed to call a function" in mlow:
        return False
    if "single tool" in mlow:
        return False
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
    msg = msg_all.lower()
    needles = (
        "timeout",
        "rate limit",
        "429",
        "503",
        "502",
        "temporarily unavailable",
        "overloaded",
    )
    return any(n in msg for n in needles)
