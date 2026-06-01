"""CLI dispatch after M8 preflight (stub vs LLM); used with M9 run tracing."""

from __future__ import annotations

import logging
from argparse import Namespace

from articlebook.m6_qa import run_m6_contract_qa
from articlebook.pipeline import (
    run_llm,
    run_stub_m1,
    run_stub_m2,
    run_stub_m3,
    run_stub_m4,
    run_stub_m5,
    run_stub_m6,
)
from articlebook.shared.config import load_config_optional
from articlebook.shared.paths import project_root


def run_articlebook_cli_body(
    args: Namespace, log: logging.Logger
) -> tuple[bool, str | None, bool | None]:
    """Execute stub or LLM path.

    Returns ``(success, crew_result_text, qa_passed_or_none)``. May raise ``SystemExit``.
    """
    if args.stub:
        log.info(
            "mode=stub milestone=%s topic=%s language=%s dry_run=%s",
            args.milestone,
            args.topic,
            args.language,
            args.dry_run,
        )
        if args.milestone == "m1":
            run_stub_m1(args.topic, args.language)
            print("M1 stub pipeline completed.")
            return True, None, None
        if args.milestone == "m2":
            run_stub_m2(args.topic, args.language)
            print("M2 stub content pipeline completed.")
            return True, None, None
        if args.milestone == "m3":
            run_stub_m3(args.topic, args.language)
            print("M3 stub pipeline completed.")
            return True, None, None
        if args.milestone == "m4":
            run_stub_m4(args.topic, args.language)
            print("M4 stub pipeline completed.")
            return True, None, None
        if args.milestone == "m5":
            run_stub_m5(args.topic, args.language)
            print("M5 stub pipeline completed.")
            return True, None, None
        ok = run_stub_m6(args.topic, args.language, allow_missing_pdf=args.m6_allow_missing_pdf)
        if args.dry_run:
            print("M6 stub dry-run completed (skipped writes and QA).")
            return True, None, None
        print(
            "M6 stub pipeline completed. "
            f"Deterministic QA: {'PASS' if ok else 'FAIL'} — see build/m6_qa_report.md"
        )
        if not ok:
            raise SystemExit(1)
        return True, None, ok

    if load_config_optional() is None:
        raise SystemExit(
            "OPENAI_API_KEY is not set. Export it or pass --stub for offline placeholders."
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
