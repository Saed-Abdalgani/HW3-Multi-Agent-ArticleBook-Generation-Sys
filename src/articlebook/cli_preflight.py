"""M8 CLI preflight: topic validation, overwrite warning, paid-run confirmation, context tokens."""

from __future__ import annotations

from argparse import Namespace
from contextvars import Token
from pathlib import Path

from articlebook.inputs import validate_topic_language
from articlebook.shared.security import (
    ensure_overwrite_artifacts_confirmed,
    ensure_paid_llm_confirmed,
)
from articlebook.shared.security_context import (
    reset_allow_workspace_overwrites,
    reset_dry_run,
    set_allow_workspace_overwrites,
    set_dry_run,
)


def run_cli_security_preflight(args: Namespace, root: Path) -> tuple[Token, Token]:
    """Validate inputs, interactive gates, then bind dry-run + overwrite permission."""
    validate_topic_language(args.topic, args.language)
    ensure_overwrite_artifacts_confirmed(
        root, assume_yes=args.yes, dry_run=args.dry_run
    )
    if not args.stub:
        ensure_paid_llm_confirmed(assume_yes=args.yes)
    t_dry = set_dry_run(args.dry_run)
    t_allow = set_allow_workspace_overwrites(True)
    return t_dry, t_allow


def reset_cli_security_tokens(t_dry: Token, t_allow: Token) -> None:
    reset_dry_run(t_dry)
    reset_allow_workspace_overwrites(t_allow)
