"""Hook InstrumentedLLM into the M9 run buffer (no heavy imports in gatekeeper)."""

from __future__ import annotations

from typing import Any

from articlebook.shared.observability_buffer import trace_get


def record_llm_ok(
    *,
    attempt: int,
    max_attempts: int,
    latency_s: float,
    agent_name: str | None,
    token_delta: dict[str, Any],
    est_cost_usd: float,
) -> None:
    buf = trace_get()
    if buf is None:
        return
    buf.append_llm_event(
        {
            "ok": True,
            "attempt": attempt,
            "max_attempts": max_attempts,
            "latency_s": round(latency_s, 4),
            "agent": agent_name,
            "token_delta": token_delta,
            "est_cost_usd": round(est_cost_usd, 8),
        }
    )


def record_llm_fail(
    *,
    attempt: int,
    max_attempts: int,
    error_type: str,
    message: str,
) -> None:
    buf = trace_get()
    if buf is None:
        return
    buf.append_llm_event(
        {
            "ok": False,
            "attempt": attempt,
            "max_attempts": max_attempts,
            "error_type": error_type,
            "message": (message or "")[:500],
        }
    )
