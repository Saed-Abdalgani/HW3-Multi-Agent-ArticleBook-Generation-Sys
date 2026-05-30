"""Single entry for LLM construction (retries/backpressure expand here)."""

from __future__ import annotations

import logging
from typing import Any

from crewai import LLM

logger = logging.getLogger(__name__)


def create_llm(config: dict[str, Any]) -> LLM:
    """Build the CrewAI LLM from validated configuration (no secret logging)."""
    model = str(config["model"])
    temperature = float(config["temperature"])
    seed = int(config.get("seed", 42))
    api_key = str(config["api_key"])
    logger.info(
        "Gatekeeper: creating LLM model=%s temperature=%s seed=%s",
        model,
        temperature,
        seed,
    )
    return LLM(
        model=model,
        temperature=temperature,
        seed=seed,
        api_key=api_key,
    )
