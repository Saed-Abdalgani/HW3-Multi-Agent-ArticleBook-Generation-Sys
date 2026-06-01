"""Fixed-size text splitter with overlap (M9-OPT)."""


def chunk_text(text: str, *, chunk_size: int, overlap: int) -> list[str]:
    """Split ``text`` into overlapping windows (``overlap`` < ``chunk_size``)."""
    if chunk_size <= 0:
        return []
    step = max(1, chunk_size - max(0, overlap))
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        out.append(text[i : i + chunk_size])
        i += step
    return out
