"""Backward-compatible config shim for legacy imports."""

from articlebook.shared.config import load_config as get_config

__all__ = ["get_config"]
