"""Guarded workspace read/write (M8): dry-run, overwrite policy, untrusted file reads."""

from __future__ import annotations

import logging
from pathlib import Path

from articlebook.crew.workspace_sandbox import (
    _ensure_under_root,
    _root,
    _validate_relative,
    _validate_relative_read,
)
from articlebook.shared.security import (
    UNTRUSTED_FILE_READ_NOTICE,
    allow_workspace_overwrites_active,
    dry_run_active,
    guard_file_read_payload,
)
from articlebook.shared.security_heuristics import tool_facing_string_has_denylisted_patterns

logger = logging.getLogger(__name__)


def _write_needs_explicit_overwrite(rel: Path) -> bool:
    s = rel.as_posix()
    return not s.startswith("build/")


def guarded_write_workspace_file(relative_path: str, content: str) -> str:
    """Write UTF-8 text with M8 dry-run and overwrite controls."""
    root = _root()
    rel = _validate_relative(relative_path)
    deny = tool_facing_string_has_denylisted_patterns(content)
    if deny:
        raise ValueError(
            "write_workspace_file: content matches denylisted patterns: " + ", ".join(deny)
        )
    dest = _ensure_under_root(root, rel)
    if dry_run_active():
        exists = " (would overwrite existing)" if dest.is_file() else ""
        return (
            f"DRY-RUN: would write {dest.relative_to(root)}{exists} "
            f"({len(content)} chars). No bytes written."
        )
    if (
        dest.is_file()
        and _write_needs_explicit_overwrite(rel)
        and not allow_workspace_overwrites_active()
    ):
        raise ValueError(
            f"Refusing to overwrite {dest.relative_to(root)} without operator approval. "
            "Re-run with --yes after reviewing existing artifacts, or delete the file first."
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    msg = f"Wrote {dest.relative_to(root)} ({len(content)} chars)."
    logger.info(
        "artifact.write path=%s bytes=%s",
        dest.relative_to(root),
        len(content.encode("utf-8")),
    )
    return msg


def guarded_read_workspace_file(relative_path: str) -> str:
    """Read UTF-8 text with traversal checks and M8 read hardening."""
    root = _root()
    rel = _validate_relative_read(relative_path)
    src = (root / rel).resolve()
    if not src.is_relative_to(root.resolve()):
        raise ValueError("Invalid read target.")
    if not src.is_file():
        return f"Missing file: {src.relative_to(root)}"
    text = src.read_text(encoding="utf-8")
    rel_pos = rel.as_posix()
    safe = guard_file_read_payload(text, relative_path=rel_pos)
    logger.info("artifact.read path=%s chars=%s", src.relative_to(root), len(text))
    return f"{safe}\n\n{UNTRUSTED_FILE_READ_NOTICE}"
