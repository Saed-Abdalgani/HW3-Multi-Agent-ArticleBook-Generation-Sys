"""Thin CLI entrypoint for milestone M1."""

from __future__ import annotations

import argparse
import logging

from articlebook.pipeline import run_llm_m1, run_stub_m1, setup_logging
from articlebook.shared.config import load_config_optional


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-agent article/book generation (M1 crew).")
    parser.add_argument("--topic", required=True, help="Document topic")
    parser.add_argument(
        "--language",
        required=True,
        help="Primary language (e.g., English or Hebrew)",
    )
    parser.add_argument(
        "--stub",
        action="store_true",
        help="Offline deterministic run (no LLM) that still emits M1 placeholder artifacts.",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)
    log = logging.getLogger(__name__)

    if args.stub:
        log.info("mode=stub topic=%s language=%s", args.topic, args.language)
        run_stub_m1(args.topic, args.language)
        print("M1 stub pipeline completed.")
        return

    if load_config_optional() is None:
        raise SystemExit(
            "OPENAI_API_KEY is not set. Export it or pass --stub for offline placeholders."
        )
    log.info("mode=llm topic=%s language=%s", args.topic, args.language)
    result = run_llm_m1(args.topic, args.language)
    print(result)


if __name__ == "__main__":
    main()
