"""CLI dispatch after M8 preflight (LLM); used with M9 run tracing."""

from __future__ import annotations

import logging
from argparse import Namespace

from articlebook.m6_qa import run_m6_contract_qa
from articlebook.pipeline import run_llm
from articlebook.shared.config import load_config_optional
from articlebook.shared.paths import project_root


def run_articlebook_cli_body(
    args: Namespace, log: logging.Logger
) -> tuple[bool, str | None, bool | None]:
    """Execute the LLM crew for the selected milestone.

    Returns ``(success, crew_result_text, qa_passed_or_none)``. May raise ``SystemExit``.
    """
    if load_config_optional() is None:
        raise SystemExit(
            "No LLM API key found for the configured provider. "
            "Set OPENAI_API_KEY (optionally OPENAI_API_KEY_2 / _3), or the three "
            "ARTICLEBOOK_*_KEY_SUFFIX variables from .env_example, or GOOGLE_API_KEY / "
            "GEMINI_API_KEY (and _2 / _3) for Google Gemini, "
            "and match ARTICLEBOOK_LLM_PROVIDER / config/models.yaml ``provider``."
        )
    log.info(
        "mode=llm milestone=%s topic=%s language=%s dry_run=%s",
        args.milestone,
        args.topic,
        args.language,
        args.dry_run,
    )
    result = run_llm(args.topic, args.language, milestone=args.milestone)
    print(result)
    qa_passed: bool | None = None
    if args.milestone == "m6":
        qa = run_m6_contract_qa(
            project_root(),
            log_prefix="m6_crew",
            allow_missing_pdf=args.m6_allow_missing_pdf,
        )
        qa_passed = qa.passed
        print(
            "\n--- M6 deterministic QA (post-crew) ---\n"
            f"PASS={qa.passed}  report=build/m6_qa_report.md"
        )
        if not qa.passed:
            raise SystemExit(1)
    return True, str(result), qa_passed
