"""Dry-run short-circuit for deterministic stub pipelines (M8)."""

from __future__ import annotations

import logging

from articlebook.shared.security_context import dry_run_active


def skip_stub_disk_writes(log: logging.Logger, milestone: str) -> bool:
    """Return True when this stub run must not touch the workspace."""
    if dry_run_active():
        log.info("stub.%s dry-run: skipping disk writes", milestone)
        return True
    return False
