"""Thin CLI entrypoint for milestones M1–M6 (stub + LLM)."""

from __future__ import annotations

import argparse
import logging

from articlebook.m6_qa import run_m6_contract_qa
from articlebook.pipeline import (
    run_llm,
    run_stub_m1,
    run_stub_m2,
    run_stub_m3,
    run_stub_m4,
    run_stub_m5,
    run_stub_m6,
    setup_logging,
)
from articlebook.shared.config import load_config_optional
from articlebook.shared.paths import project_root


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Multi-agent article/book generation (CrewAI + LaTeX, HW3)."
    )
    parser.add_argument("--topic", required=True, help="Document topic")
    parser.add_argument(
        "--language",
        required=True,
        help="Primary language (e.g., English or Hebrew)",
    )
    parser.add_argument(
        "--milestone",
        choices=("m1", "m2", "m3", "m4", "m5", "m6"),
        default="m2",
        help="m1=full smoke; m2=content; m3=M2+figures; m4=M3+LaTeX+compile; "
        "m5=M4+canonical multipass (biber); m6=M5+deterministic QA contract. Default: m2.",
    )
    parser.add_argument(
        "--stub",
        action="store_true",
        help="Offline deterministic run (no LLM). Milestone selects stub profile.",
    )
    parser.add_argument(
        "--m6-allow-missing-pdf",
        action="store_true",
        help=(
            "For m6: relax PDF / missing-engine compile journal so static checks run "
            "without MiKTeX."
        ),
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)
    log = logging.getLogger(__name__)

    if args.stub:
        log.info(
            "mode=stub milestone=%s topic=%s language=%s",
            args.milestone,
            args.topic,
            args.language,
        )
        if args.milestone == "m1":
            run_stub_m1(args.topic, args.language)
            print("M1 stub pipeline completed.")
        elif args.milestone == "m2":
            run_stub_m2(args.topic, args.language)
            print("M2 stub content pipeline completed.")
        elif args.milestone == "m3":
            run_stub_m3(args.topic, args.language)
            print("M3 stub pipeline completed.")
        elif args.milestone == "m4":
            run_stub_m4(args.topic, args.language)
            print("M4 stub pipeline completed.")
        elif args.milestone == "m5":
            run_stub_m5(args.topic, args.language)
            print("M5 stub pipeline completed.")
        else:
            ok = run_stub_m6(
                args.topic, args.language, allow_missing_pdf=args.m6_allow_missing_pdf
            )
            print(
                "M6 stub pipeline completed. "
                f"Deterministic QA: {'PASS' if ok else 'FAIL'} — see build/m6_qa_report.md"
            )
            if not ok:
                raise SystemExit(1)
        return

    if load_config_optional() is None:
        raise SystemExit(
            "OPENAI_API_KEY is not set. Export it or pass --stub for offline placeholders."
        )
    log.info(
        "mode=llm milestone=%s topic=%s language=%s",
        args.milestone,
        args.topic,
        args.language,
    )
    result = run_llm(args.topic, args.language, milestone=args.milestone)
    print(result)
    if args.milestone == "m6":
        qa = run_m6_contract_qa(
            project_root(),
            log_prefix="m6_crew",
            allow_missing_pdf=args.m6_allow_missing_pdf,
        )
        print(
            "\n--- M6 deterministic QA (post-crew) ---\n"
            f"PASS={qa.passed}  report=build/m6_qa_report.md"
        )
        if not qa.passed:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
