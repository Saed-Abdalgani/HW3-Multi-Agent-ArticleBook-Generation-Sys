"""CrewAI ``LLM`` subclass with retries, rate spacing, and call instrumentation."""

from __future__ import annotations

import logging
import random
import threading
import time
from typing import Any, Self, cast

from crewai import LLM

from articlebook.shared.gatekeeper_policy import (
    estimate_cost_usd,
    is_llm_route_failover_error,
    is_transient_llm_error,
    pricing_for_model,
    provider_suggested_retry_delay_seconds,
    should_reset_llm_route_chain_on_transient,
    snapshot_usage,
    usage_delta,
)
from articlebook.shared.observability_llm import record_llm_fail, record_llm_ok

logger = logging.getLogger(__name__)

# CrewAI may set Anthropic-style keys on chat dicts; Groq rejects them (CrewAI #5886, LiteLLM Groq).
_LITELLM_MESSAGE_KEYS_STRICT_APIS_DROP = frozenset({"cache_breakpoint", "provider_specific_fields"})


def strip_provider_specific_message_keys(messages: Any) -> Any:
    """Shallow-copy ``messages`` without keys strict OpenAI-compatible APIs (e.g. Groq) reject."""
    if messages is None or isinstance(messages, str):
        return messages
    if not isinstance(messages, list):
        return messages
    out: list[Any] = []
    for item in messages:
        if isinstance(item, dict):
            out.append(
                {k: v for k, v in item.items() if k not in _LITELLM_MESSAGE_KEYS_STRICT_APIS_DROP}
            )
        else:
            out.append(item)
    return out


class InstrumentedLLM(LLM):
    """CrewAI ``LLM`` with retries, soft rate limiting, and structured call logging."""

    def __new__(cls, model: str, is_litellm: bool = False, **kwargs: Any) -> Self:
        """CrewAI's ``LLM.__new__`` returns native provider classes (e.g. ``OpenAICompletion``),
        which drops this subclass and ignores ``InstrumentedLLM.call``. Forcing
        ``is_litellm=True`` keeps construction on ``InstrumentedLLM`` so gatekeeper logic runs
        (requires ``litellm`` — declared in ``pyproject.toml``).
        """
        if cls is InstrumentedLLM:
            merged = dict(kwargs)
            merged["is_litellm"] = True
            return cast(Self, LLM.__new__(cls, model, **merged))
        return cast(Self, LLM.__new__(cls, model, is_litellm=is_litellm, **kwargs))

    def __init__(
        self,
        *,
        gk_retry_max: int = 4,
        gk_base_delay_s: float = 0.8,
        gk_max_delay_s: float = 30.0,
        gk_min_interval_s: float = 0.0,
        gk_cost_config: dict[str, Any] | None = None,
        gk_api_keys: list[str] | None = None,
        gk_llm_routes: list[dict[str, str]] | None = None,
        **llm_kwargs: Any,
    ) -> None:
        llm_kwargs = dict(llm_kwargs)
        llm_kwargs.setdefault("is_litellm", True)
        super().__init__(**llm_kwargs)
        self._gk_retry_max = max(1, int(gk_retry_max))
        self._gk_base_delay_s = float(gk_base_delay_s)
        self._gk_max_delay_s = float(gk_max_delay_s)
        self._gk_min_interval_s = max(0.0, float(gk_min_interval_s))
        self._gk_cost_config = gk_cost_config or {}
        self._gk_lock = threading.Lock()
        self._gk_last_call_start = 0.0
        self._gk_routes: list[tuple[str, str]] | None = None
        if gk_llm_routes and len(gk_llm_routes) > 1:
            built: list[tuple[str, str]] = []
            for row in gk_llm_routes:
                k = str(row.get("api_key", "")).strip()
                m = str(row.get("model", "")).strip()
                if k and m:
                    built.append((k, m))
            if len(built) > 1:
                self._gk_routes = built
        raw_keys = list(gk_api_keys) if gk_api_keys else []
        cleaned = [str(k).strip() for k in raw_keys if str(k).strip()]
        if not cleaned:
            ak = llm_kwargs.get("api_key")
            if ak:
                cleaned = [str(ak).strip()]
        self._gk_api_keys = cleaned
        self._gk_key_index = 0

    def _gk_slot_count(self) -> int:
        if self._gk_routes:
            return len(self._gk_routes)
        return len(self._gk_api_keys)

    def _gk_set_active_slot(self, index: int) -> None:
        if self._gk_routes:
            self._gk_key_index = max(0, min(int(index), len(self._gk_routes) - 1))
            key, model = self._gk_routes[self._gk_key_index]
            setattr(self, "api_key", key)
            setattr(self, "model", model)
            return
        self._gk_set_active_key(index)

    def _gk_set_active_key(self, index: int) -> None:
        if not self._gk_api_keys:
            return
        self._gk_key_index = max(0, min(int(index), len(self._gk_api_keys) - 1))
        key = self._gk_api_keys[self._gk_key_index]
        setattr(self, "api_key", key)

    def call(self, *args: Any, **kwargs: Any) -> Any:
        self._gk_rate_limit_wait()
        self._gk_set_active_slot(0)
        # Groq rejects ``cache_breakpoint`` / ``provider_specific_fields`` on message dicts (CrewAI #5886).
        args_list = list(args)
        if args_list:
            args_list[0] = strip_provider_specific_message_keys(args_list[0])
            args = tuple(args_list)
        elif "messages" in kwargs:
            kwargs = {**kwargs, "messages": strip_provider_specific_message_keys(kwargs["messages"])}
        pricing = pricing_for_model(self._gk_cost_config, str(self.model))
        attempt = 0
        last_exc: BaseException | None = None
        while attempt < self._gk_retry_max:
            attempt += 1
            before = snapshot_usage(self)
            t0 = time.perf_counter()
            try:
                result = super().call(*args, **kwargs)
            except BaseException as exc:
                last_exc = exc
                n_slots = self._gk_slot_count()
                if (
                    n_slots > 1
                    and is_llm_route_failover_error(exc)
                    and self._gk_key_index < n_slots - 1
                ):
                    prev_idx = self._gk_key_index
                    prev_model = str(getattr(self, "model", ""))
                    self._gk_set_active_slot(self._gk_key_index + 1)
                    logger.warning(
                        "Gatekeeper: LLM route failover %s/%s -> %s/%s (from model=%r to model=%r) "
                        "after %s: %s",
                        prev_idx + 1,
                        n_slots,
                        self._gk_key_index + 1,
                        n_slots,
                        prev_model,
                        str(getattr(self, "model", "")),
                        type(exc).__name__,
                        exc,
                    )
                    attempt -= 1
                    continue
                if attempt >= self._gk_retry_max or not is_transient_llm_error(exc):
                    logger.error(
                        "Gatekeeper: LLM call failed attempt=%s/%s err=%s: %s",
                        attempt,
                        self._gk_retry_max,
                        type(exc).__name__,
                        exc,
                    )
                    record_llm_fail(
                        attempt=attempt,
                        max_attempts=self._gk_retry_max,
                        error_type=type(exc).__name__,
                        message=str(exc),
                    )
                    raise
                base = self._gk_base_delay_s * (2 ** (attempt - 1)) + random.random() * 0.15
                suggested = provider_suggested_retry_delay_seconds(exc)
                if suggested is not None:
                    # Honor Groq/OpenRouter-style "try again in Ns" even when N > ``gk_max_delay_s``.
                    cap = min(600.0, max(self._gk_max_delay_s, suggested))
                    delay = min(cap, max(base, suggested))
                else:
                    delay = min(self._gk_max_delay_s, base)
                logger.warning(
                    "Gatekeeper: transient LLM error %s (attempt %s/%s); sleeping %.2fs"
                    "%s",
                    type(exc).__name__,
                    attempt,
                    self._gk_retry_max,
                    delay,
                    f" (provider hint {suggested:.2f}s)" if suggested is not None else "",
                )
                time.sleep(delay)
                if not self._gk_routes:
                    self._gk_set_active_slot(0)
                elif (
                    self._gk_slot_count() > 1
                    and should_reset_llm_route_chain_on_transient(exc)
                ):
                    self._gk_set_active_slot(0)
                continue

            dt = time.perf_counter() - t0
            after = snapshot_usage(self)
            delta = usage_delta(before, after)
            est = estimate_cost_usd(delta, pricing)
            from_agent = kwargs.get("from_agent")
            agent_name = getattr(from_agent, "role", None) if from_agent is not None else None
            logger.info(
                "Gatekeeper: LLM ok attempt=%s latency_s=%.3f agent=%s token_delta=%s "
                "est_cost_usd=%.6f",
                attempt,
                dt,
                agent_name,
                delta,
                est,
            )
            record_llm_ok(
                attempt=attempt,
                max_attempts=self._gk_retry_max,
                latency_s=dt,
                agent_name=agent_name,
                token_delta=delta,
                est_cost_usd=est,
            )
            return result

        assert last_exc is not None
        record_llm_fail(
            attempt=self._gk_retry_max,
            max_attempts=self._gk_retry_max,
            error_type=type(last_exc).__name__,
            message=str(last_exc),
        )
        raise last_exc

    def _gk_rate_limit_wait(self) -> None:
        if self._gk_min_interval_s <= 0:
            return
        with self._gk_lock:
            now = time.monotonic()
            if self._gk_last_call_start > 0.0:
                wait = self._gk_min_interval_s - (now - self._gk_last_call_start)
                if wait > 0:
                    time.sleep(wait)
            self._gk_last_call_start = time.monotonic()
