"""Single entry for LLM construction (retries, timing, usage — M7 gatekeeper)."""

from __future__ import annotations

import logging
from typing import Any

from crewai import LLM

from articlebook.shared.gatekeeper_instrumented import InstrumentedLLM
from articlebook.shared.gatekeeper_policy import estimate_cost_usd, is_transient_llm_error

logger = logging.getLogger(__name__)

__all__ = ["InstrumentedLLM", "create_llm", "estimate_cost_usd", "is_transient_llm_error"]


def create_llm(config: dict[str, Any]) -> LLM:
    """Build the CrewAI LLM from validated configuration (no secret logging)."""
    model = str(config["model"])
    temperature = float(config["temperature"])
    seed = int(config.get("seed", 42))
    api_key = str(config["api_key"])
    api_keys = list(config.get("api_keys") or [api_key])
    llm_routes = list(config.get("llm_routes") or [])
    timeout = config.get("timeout")
    provider = str(config.get("provider", "openai"))
    gate = dict(config.get("gatekeeper") or {})
    if len(llm_routes) > 1:
        # Each LLM call starts at slot 1; give enough attempts for throttles + failover across slots.
        n = len(llm_routes)
        gate["retry_max_attempts"] = max(int(gate.get("retry_max_attempts", 4)), 4 + n * 2)
        models_only = ", ".join(str(r.get("model", "")) for r in llm_routes)
        logger.info(
            "Gatekeeper: creating LLM with %s-route failover (order=%s); retry_max_attempts=%s",
            n,
            models_only,
            gate["retry_max_attempts"],
        )
    logger.info(
        "Gatekeeper: creating LLM provider=%s model=%s temperature=%s seed=%s timeout=%s",
        provider,
        model,
        temperature,
        seed,
        timeout,
    )
    llm_kwargs: dict[str, Any] = {
        "model": model,
        "temperature": temperature,
        "seed": seed,
        "api_key": api_key,
    }
    if timeout is not None:
        llm_kwargs["timeout"] = float(timeout)
    mt = config.get("max_tokens")
    if mt is not None:
        llm_kwargs["max_tokens"] = int(mt)

    if not gate.get("instrumented", True):
        return LLM(**llm_kwargs)

    return InstrumentedLLM(
        gk_retry_max=int(gate.get("retry_max_attempts", 4)),
        gk_base_delay_s=float(gate.get("retry_base_delay_s", 0.8)),
        gk_max_delay_s=float(gate.get("retry_max_delay_s", 30.0)),
        gk_min_interval_s=float(gate.get("rate_limit_min_interval_s", 0.0)),
        gk_cost_config=config,
        gk_api_keys=api_keys,
        gk_llm_routes=llm_routes if len(llm_routes) > 1 else None,
        **llm_kwargs,
    )
