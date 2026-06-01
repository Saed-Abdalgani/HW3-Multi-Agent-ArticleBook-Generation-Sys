"""Attach optional RAG tools to the Research agent (ADR-003)."""

from __future__ import annotations

import logging

from articlebook.rag.deps import rag_stack_importable
from articlebook.rag.tool import retrieve_knowledge_snippets
from articlebook.shared.config import rag_feature_enabled

log = logging.getLogger(__name__)


def optional_rag_research_tools() -> list:
    """Return ``[retrieve_knowledge_snippets]`` when RAG is enabled and deps exist."""
    if not rag_feature_enabled():
        return []
    if not rag_stack_importable():
        log.warning(
            "rag.enabled is true but optional RAG deps are missing; "
            "install with: uv sync --extra rag"
        )
        return []
    return [retrieve_knowledge_snippets]
