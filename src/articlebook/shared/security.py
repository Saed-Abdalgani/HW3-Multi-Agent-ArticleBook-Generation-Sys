"""M8 security facade: re-export heuristics, read guards, and CLI gates."""

from __future__ import annotations

from articlebook.shared.security_context import (
    allow_workspace_overwrites_active,
    dry_run_active,
    reset_allow_workspace_overwrites,
    reset_dry_run,
    set_allow_workspace_overwrites,
    set_dry_run,
)
from articlebook.shared.security_gates import (
    ensure_overwrite_artifacts_confirmed,
    ensure_paid_llm_confirmed,
)
from articlebook.shared.security_heuristics import (
    UNTRUSTED_FILE_READ_NOTICE,
    assert_topic_and_language_safe,
    guard_file_read_payload,
    tool_facing_string_has_denylisted_patterns,
)

__all__ = [
    "UNTRUSTED_FILE_READ_NOTICE",
    "allow_workspace_overwrites_active",
    "assert_topic_and_language_safe",
    "dry_run_active",
    "ensure_overwrite_artifacts_confirmed",
    "ensure_paid_llm_confirmed",
    "guard_file_read_payload",
    "reset_allow_workspace_overwrites",
    "reset_dry_run",
    "set_allow_workspace_overwrites",
    "set_dry_run",
    "tool_facing_string_has_denylisted_patterns",
]
