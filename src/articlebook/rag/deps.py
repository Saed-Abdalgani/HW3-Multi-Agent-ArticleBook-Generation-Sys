"""Optional heavy imports for M9-OPT (skip when ``[rag]`` extra not installed)."""

from __future__ import annotations


def rag_stack_importable() -> bool:
    """Return True if Chroma client libraries are available."""
    try:
        import chromadb  # noqa: F401
    except ImportError:
        return False
    return True
