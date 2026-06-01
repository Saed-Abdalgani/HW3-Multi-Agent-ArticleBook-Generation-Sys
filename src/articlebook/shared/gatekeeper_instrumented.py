"""CrewAI ``LLM`` subclass with retries, rate spacing, and call instrumentation."""

from __future__ import annotations

import logging
import random
import threading
import time
from typing import Any

from crewai import LLM

from articlebook.shared.gatekeeper_policy import (
    estimate_cost_usd,
    is_transient_llm_error,
    pricing_for_model,
    snapshot_usage,
    usage_delta,
)

logger = logging.getLogger(__name__)


class InstrumentedLLM(LLM):
    """CrewAI ``LLM`` with retries, soft rate limiting, and structured call logging."""

    def __init__(
        self,
        *,
        gk_retry_max: int = 4,
        gk_base_delay_s: float = 0.8,
        gk_max_delay_s: float = 30.0,
        gk_min_interval_s: float = 0.0,
        gk_cost_config: dict[str, Any] | None = None,
        **llm_kwargs: Any,
    ) -> None:
        super().__init__(**llm_kwargs)
        self._gk_retry_max = max(1, int(gk_retry_max))
        self._gk_base_delay_s = float(gk_base_delay_s)
        self._gk_max_delay_s = float(gk_max_delay_s)
        self._gk_min_interval_s = max(0.0, float(gk_min_interval_s))
        self._gk_cost_config = gk_cost_config or {}
        self._gk_lock = threading.Lock()
        self._gk_last_call_start = 0.0

    def call(self, *args: Any, **kwargs: Any) -> Any:
        self._gk_rate_limit_wait()
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
                if attempt >= self._gk_retry_max or not is_transient_llm_error(exc):
                    logger.error(
                        "Gatekeeper: LLM call failed attempt=%s/%s err=%s: %s",
                        attempt,
                        self._gk_retry_max,
                        type(exc).__name__,
                        exc,
                    )
                    raise
                delay = min(
                    self._gk_max_delay_s,
                    self._gk_base_delay_s * (2 ** (attempt - 1)) + random.random() * 0.15,
                )
                logger.warning(
                    "Gatekeeper: transient LLM error %s (attempt %s/%s); sleeping %.2fs",
                    type(exc).__name__,
                    attempt,
                    self._gk_retry_max,
                    delay,
                )
                time.sleep(delay)
                continue

            dt = time.perf_counter() - t0
            after = snapshot_usage(self)
            delta = usage_delta(before, after)
            est = estimate_cost_usd(delta, pricing)
            from_agent = kwargs.get("from_agent")
            agent_name = getattr(from_agent, "role", None) if from_agent is not None else None
            logger.info(
                "Gatekeeper: LLM ok attempt=%s latency_s=%.3f agent=%s token_delta=%s est_cost_usd=%.6f",
                attempt,
                dt,
                agent_name,
                delta,
                est,
            )
            return result

        assert last_exc is not None
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
