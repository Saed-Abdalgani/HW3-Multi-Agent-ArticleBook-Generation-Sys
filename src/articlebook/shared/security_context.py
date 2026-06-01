"""M8 execution context: dry-run (no writes) and overwrite permission (crew tools)."""

from __future__ import annotations

from contextvars import ContextVar, Token

_dry_run: ContextVar[bool] = ContextVar("articlebook_dry_run", default=False)
_allow_workspace_overwrites: ContextVar[bool] = ContextVar(
    "articlebook_allow_workspace_overwrites", default=False
)


def dry_run_active() -> bool:
    return _dry_run.get()


def allow_workspace_overwrites_active() -> bool:
    return _allow_workspace_overwrites.get()


def set_dry_run(value: bool) -> Token:
    return _dry_run.set(bool(value))


def set_allow_workspace_overwrites(value: bool) -> Token:
    return _allow_workspace_overwrites.set(bool(value))


def reset_dry_run(token: Token) -> None:
    _dry_run.reset(token)


def reset_allow_workspace_overwrites(token: Token) -> None:
    _allow_workspace_overwrites.reset(token)
