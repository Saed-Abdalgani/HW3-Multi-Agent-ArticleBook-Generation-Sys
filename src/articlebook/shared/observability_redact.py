"""Redact secrets and trim strings for M9 run reports and logs."""

from __future__ import annotations

import re
from typing import Final

_SK_RE: Final[re.Pattern[str]] = re.compile(r"sk-[A-Za-z0-9]{10,}", re.IGNORECASE)
_BEARER_RE: Final[re.Pattern[str]] = re.compile(
    r"bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE
)
_KEY_ASSIGN_RE: Final[re.Pattern[str]] = re.compile(
    r"(?i)(api[_-]?key|openai[_-]?api[_-]?key|authorization)\s*[:=]\s*(\S+)"
)


def redact_for_report(text: str, *, max_chars: int = 4000) -> str:
    """Remove common secret patterns and cap length for JSON/markdown artifacts."""
    s = str(text)
    s = _SK_RE.sub("[REDACTED_SK]", s)
    s = _BEARER_RE.sub("Bearer [REDACTED]", s)
    s = _KEY_ASSIGN_RE.sub(lambda m: f"{m.group(1)}=[REDACTED]", s)
    if len(s) > max_chars:
        return s[:max_chars] + "\n… [truncated]"
    return s
