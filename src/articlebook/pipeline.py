"""High-level runners: stub vs LLM, milestones M1–M4."""

from __future__ import annotations

import logging
from typing import Literal

from articlebook.crew.crew_builder import build_crew
from articlebook.crew.workspace_tools import bind_workspace_root, reset_workspace_root
from articlebook.inputs import log_resolved_run_config, validate_topic_language
from articlebook.pipeline_stubs import run_stub_m1, run_stub_m2, run_stub_m3, run_stub_m4
from articlebook.shared.config import load_config
from articlebook.shared.gatekeeper import create_llm
from articlebook.shared.paths import project_root

Milestone = Literal["m1", "m2", "m3", "m4"]

__all__ = [
    "Milestone",
    "setup_logging",
    "run_stub_m1",
    "run_stub_m2",
    "run_stub_m3",
    "run_stub_m4",
    "run_llm",
    "run_llm_m1",
    "run_llm_m2",
    "run_llm_m3",
    "run_llm_m4",
]


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def run_llm(topic: str, language: str, milestone: Milestone = "m2") -> str:
    """Execute CrewAI crew (requires OPENAI_API_KEY). Milestone: m1 | m2 | m3 | m4."""
    inputs = validate_topic_language(topic, language)
    root = project_root()
    token = bind_workspace_root(root)
    log = logging.getLogger(__name__)
    try:
        cfg = load_config()
        llm = create_llm(cfg)
        log_resolved_run_config(inputs, mode="llm", milestone=milestone)

        def _task_cb(output: object) -> None:
            log.info("crew.task.done snippet=%s", str(output)[:400].replace("\n", " "))

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
        return str(result)
    finally:
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
