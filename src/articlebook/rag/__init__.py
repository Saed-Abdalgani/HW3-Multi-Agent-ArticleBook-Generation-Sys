"""M9-OPT optional local RAG (ADR-003); disabled unless ``rag.enabled`` and ``[rag]`` extras."""

from articlebook.rag.wiring import optional_rag_research_tools

__all__ = ["optional_rag_research_tools"]
