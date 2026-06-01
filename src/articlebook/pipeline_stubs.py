"""Deterministic stub runners (M1–M6) for ``articlebook.pipeline``."""

from __future__ import annotations

import logging

from articlebook.crew.workspace_tools import bind_workspace_root, reset_workspace_root
from articlebook.inputs import log_resolved_run_config, validate_topic_language
from articlebook.m2_stub import write_m2_stub_artifacts
from articlebook.m3_assets import run_m3_python_generators, write_m3_stub_manifest
from articlebook.m4_manifest import (
    write_m4_stub_manifest,
    write_m5_stub_manifest,
    write_m6_stub_manifest,
)
from articlebook.m6_qa import run_m6_contract_qa
from articlebook.pipeline_stub_latex import stub_latex_through_m5_driver, write_m3_figure_manifest
from articlebook.pipeline_stub_m1 import run_stub_m1
from articlebook.shared.paths import project_root


def run_stub_m2(topic: str, language: str) -> None:
    """Deterministic M2 content pipeline: outline, chapters, BiDi note, `.bib` (no compile)."""
    inputs = validate_topic_language(topic, language)
    root = project_root()
    log = logging.getLogger(__name__)
    log_resolved_run_config(inputs, mode="stub", milestone="m2")
    token = bind_workspace_root(root)
    try:
        write_m2_stub_artifacts(root, inputs)
        log.info("stub.m2 complete root=%s", root)
    finally:
        reset_workspace_root(token)


def run_stub_m3(topic: str, language: str) -> None:
    """Deterministic M2 + M3: Markdown draft, `.bib`, Matplotlib assets, M3 manifest."""
    inputs = validate_topic_language(topic, language)
    root = project_root()
    log = logging.getLogger(__name__)
    log_resolved_run_config(inputs, mode="stub", milestone="m3")
    token = bind_workspace_root(root)
    try:
        write_m2_stub_artifacts(root, inputs)
        gen_log = run_m3_python_generators(root)
        write_m3_stub_manifest(root, inputs, gen_log)
        (root / "figures").mkdir(parents=True, exist_ok=True)
        write_m3_figure_manifest(root / "figures")
        log.info("stub.m3 complete root=%s", root)
    finally:
        reset_workspace_root(token)


def run_stub_m4(topic: str, language: str) -> None:
    """Deterministic M2 + M3 + M4: Markdown, assets, LaTeX assembly, multipass compile."""
    inputs = validate_topic_language(topic, language)
    root = project_root()
    log = logging.getLogger(__name__)
    log_resolved_run_config(inputs, mode="stub", milestone="m4")
    token = bind_workspace_root(root)
    try:
        stub_latex_through_m5_driver(
            root, inputs, log_prefix="m4", manifest_writer=write_m4_stub_manifest
        )
        log.info("stub.m4 complete root=%s", root)
    finally:
        reset_workspace_root(token)


def run_stub_m5(topic: str, language: str) -> None:
    """Same tree as M4 stub; records ``m5_stub_manifest.md`` (M5 sign-off trail)."""
    inputs = validate_topic_language(topic, language)
    root = project_root()
    log = logging.getLogger(__name__)
    log_resolved_run_config(inputs, mode="stub", milestone="m5")
    token = bind_workspace_root(root)
    try:
        stub_latex_through_m5_driver(
            root, inputs, log_prefix="m5", manifest_writer=write_m5_stub_manifest
        )
        log.info("stub.m5 complete root=%s", root)
    finally:
        reset_workspace_root(token)


def run_stub_m6(topic: str, language: str, *, allow_missing_pdf: bool = False) -> bool:
    """M5 stub tree plus deterministic M6 contract QA; returns whether QA passed."""
    inputs = validate_topic_language(topic, language)
    root = project_root()
    log = logging.getLogger(__name__)
    log_resolved_run_config(inputs, mode="stub", milestone="m6")
    token = bind_workspace_root(root)
    try:
        stub_latex_through_m5_driver(
            root, inputs, log_prefix="m5", manifest_writer=write_m5_stub_manifest
        )
        qa = run_m6_contract_qa(root, log_prefix="m5", allow_missing_pdf=allow_missing_pdf)
        write_m6_stub_manifest(root, inputs, qa.passed)
        log.info("stub.m6 complete root=%s qa_passed=%s", root, qa.passed)
        return qa.passed
    finally:
        reset_workspace_root(token)


__all__ = [
    "run_stub_m1",
    "run_stub_m2",
    "run_stub_m3",
    "run_stub_m4",
    "run_stub_m5",
    "run_stub_m6",
]
