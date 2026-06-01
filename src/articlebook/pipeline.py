"""High-level runners: stub vs LLM, milestones M1–M6."""

from __future__ import annotations

import logging
from typing import Literal

from articlebook.crew.crew_builder import build_crew
from articlebook.crew.workspace_tools import bind_workspace_root, reset_workspace_root
from articlebook.inputs import log_resolved_run_config, validate_topic_language
from articlebook.pipeline_stubs import (
    run_stub_m1,
    run_stub_m2,
    run_stub_m3,
    run_stub_m4,
    run_stub_m5,
    run_stub_m6,
)
from articlebook.shared.config import load_config, write_resolved_run_stamp
from articlebook.shared.gatekeeper import create_llm
from articlebook.shared.observability import append_task_output_if_tracing, log_json_event
from articlebook.shared.output_validate import validate_agent_text_output_lenient
from articlebook.shared.paths import project_root
from articlebook.shared.security_context import (
    reset_allow_workspace_overwrites,
    set_allow_workspace_overwrites,
)

Milestone = Literal["m1", "m2", "m3", "m4", "m5", "m6"]

__all__ = [
    "Milestone",
    "setup_logging",
    "run_stub_m1",
    "run_stub_m2",
    "run_stub_m3",
    "run_stub_m4",
    "run_stub_m5",
    "run_stub_m6",
    "run_llm",
    "run_llm_m1",
    "run_llm_m2",
    "run_llm_m3",
    "run_llm_m4",
    "run_llm_m5",
    "run_llm_m6",
]


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def run_llm(topic: str, language: str, milestone: Milestone = "m2") -> str:
    """Execute CrewAI crew (requires OPENAI_API_KEY). Milestone: m1 | m2 | m3 | m4 | m5 | m6."""
    inputs = validate_topic_language(topic, language)
    root = project_root()
    token = bind_workspace_root(root)
    owr_tok = set_allow_workspace_overwrites(True)
    log = logging.getLogger(__name__)
    try:
        cfg = load_config()
        write_resolved_run_stamp(cfg, milestone=milestone)
        llm = create_llm(cfg)
        log_resolved_run_config(
            inputs,
            mode="llm",
            milestone=milestone,
            provider=str(cfg.get("provider")),
            model=str(cfg.get("model")),
            seed=int(cfg.get("seed", 42)),
            config_version=str(cfg.get("config_version", "")),
        )

        def _task_cb(output: object) -> None:
            text = str(output)
            append_task_output_if_tracing(text)
            snippet = text[:400].replace("\n", " ")
            log.info("crew.task.done snippet=%s", snippet)
            log_json_event(log, "crew_task_done", chars=len(text))
            if validate_agent_text_output_lenient(text, stage="crew.task") is None:
                log.warning("crew.task.output failed lenient validation (empty or invalid)")

        crew = build_crew(
            llm, inputs.topic, inputs.language, milestone=milestone, task_callback=_task_cb
        )
        log.info(
            "crew.kickoff.start topic=%s language=%s milestone=%s",
            topic,
            language,
            milestone,
        )
        result = crew.kickoff(inputs={"topic": inputs.topic, "language": inputs.language})
        log.info("crew.kickoff.done")
        usage_fn = getattr(llm, "get_token_usage_summary", None)
        if callable(usage_fn):
            log.info("crew.llm.token_usage_summary=%s", usage_fn())
        return str(result)
    finally:
        reset_allow_workspace_overwrites(owr_tok)
        reset_workspace_root(token)


def run_llm_m1(topic: str, language: str) -> str:
    """Backward-compatible entry: full M1 crew."""
    return run_llm(topic, language, milestone="m1")


def run_llm_m2(topic: str, language: str) -> str:
    """M2 content pipeline via LLM agents."""
    return run_llm(topic, language, milestone="m2")


def run_llm_m3(topic: str, language: str) -> str:
    """M3 pipeline via LLM agents (M2 + figure generators + QA)."""
    return run_llm(topic, language, milestone="m3")


def run_llm_m4(topic: str, language: str) -> str:
    """M4 pipeline via LLM agents (M3 + LaTeX assembly + compile + QA)."""
    return run_llm(topic, language, milestone="m4")


def run_llm_m5(topic: str, language: str) -> str:
    """M5 pipeline via LLM agents (M4 + canonical multipass compile + QA)."""
    return run_llm(topic, language, milestone="m5")


def run_llm_m6(topic: str, language: str) -> str:
    """M6 pipeline: M5 + deterministic contract QA tool (``run_m6_contract_checks``)."""
    return run_llm(topic, language, milestone="m6")
