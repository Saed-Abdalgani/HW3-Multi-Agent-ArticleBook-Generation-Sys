"""Workspace root binding and path validation for crew tools."""

from __future__ import annotations

from contextvars import ContextVar, Token
from pathlib import Path

_ALLOWED_PREFIXES = ("content/", "latex/", "figures/", "build/", "scripts/")
_ROOT_READABLE = frozenset(
    {"prd.md", "plan.md", "todo.md", "README.md", "SYSTEM_PROMPT.md", "PROMPTS.md"}
)
_workspace_root: ContextVar[Path | None] = ContextVar("articlebook_workspace_root", default=None)


def bind_workspace_root(root: Path) -> Token:
    """Bind the workspace root for tool execution (call from the crew runner thread)."""
    return _workspace_root.set(root.resolve())


def reset_workspace_root(token: Token) -> None:
    _workspace_root.reset(token)


def _root() -> Path:
    r = _workspace_root.get()
    if r is None:
        msg = "Workspace root is not bound; call bind_workspace_root() before running tools."
        raise RuntimeError(msg)
    return r


def _validate_relative(relative_path: str) -> Path:
    raw = Path(relative_path).as_posix().lstrip("./")
    if not raw or ".." in Path(raw).parts or Path(raw).is_absolute():
        raise ValueError("Invalid relative path.")
    if not any(raw.startswith(p) for p in _ALLOWED_PREFIXES):
        allowed = ", ".join(_ALLOWED_PREFIXES)
        raise ValueError(f"Path must start with one of: {allowed}")
    return Path(raw)


def _validate_relative_read(relative_path: str) -> Path:
    raw = Path(relative_path).as_posix().lstrip("./")
    if not raw or ".." in Path(raw).parts or Path(raw).is_absolute():
        raise ValueError("Invalid relative path.")
    if raw in _ROOT_READABLE:
        return Path(raw)
    if not any(raw.startswith(p) for p in _ALLOWED_PREFIXES):
        allowed = ", ".join(_ALLOWED_PREFIXES) + f", or one of {sorted(_ROOT_READABLE)}"
        raise ValueError(f"Path not allowed for read: {allowed}")
    return Path(raw)


def _ensure_under_root(root: Path, target: Path) -> Path:
    resolved = (root / target).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("Resolved path escapes project root.")
    return resolved
