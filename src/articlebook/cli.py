"""Thin CLI entrypoint for milestones M1–M4 (stub + LLM)."""

from __future__ import annotations

import argparse
import logging

from articlebook.pipeline import (
    run_llm,
    run_stub_m1,
    run_stub_m2,
    run_stub_m3,
    run_stub_m4,
    setup_logging,
)
from articlebook.shared.config import load_config_optional


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
        choices=("m1", "m2", "m3", "m4"),
        default="m2",
        help="m1=full smoke; m2=content; m3=M2+figures; m4=M3+LaTeX assembly+compile. Default: m2.",
    )
    parser.add_argument(
        "--stub",
        action="store_true",
        help="Offline deterministic run (no LLM). Milestone selects stub profile.",
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
        else:
            run_stub_m4(args.topic, args.language)
            print("M4 stub pipeline completed.")
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


if __name__ == "__main__":
    main()
