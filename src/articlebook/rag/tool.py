"""CrewAI tool: retrieve cited snippets from local ``knowledge/`` (M9-OPT)."""

from __future__ import annotations

import json

from crewai.tools import tool

from articlebook.crew.workspace_sandbox import _root
from articlebook.rag.chroma_service import query_as_json
from articlebook.rag.deps import rag_stack_importable
from articlebook.shared.config import rag_feature_enabled


@tool("retrieve_knowledge_snippets")
def retrieve_knowledge_snippets(query: str) -> str:
    """Top-k local snippets with ``source_id`` = ``bib_key`` for [@source_id] cites (M6)."""
    if not rag_feature_enabled():
        return json.dumps(
            {"snippets": [], "claims": [], "info": "rag.disabled"},
            ensure_ascii=False,
        )
    if not rag_stack_importable():
        return json.dumps(
            {
                "snippets": [],
                "claims": [],
                "error": "missing_optional_deps",
                "hint": "uv sync --extra rag",
            },
            ensure_ascii=False,
        )
    root = _root()
    return query_as_json(root, query.strip() or "*")
