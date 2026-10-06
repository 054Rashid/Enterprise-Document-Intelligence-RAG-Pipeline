"""Small text-cleaning and chunking helpers used by the ingestion pipeline."""


def normalize_text(text: str) -> str:
    """Collapse repeated whitespace so document chunks are easier to work with."""
    return " ".join(text.split()).strip()


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """Split cleaned text into overlapping character-based chunks.

    Character chunking is intentionally simple here. It makes the project easy to
    understand for a first RAG implementation and leaves room for later experiments
    with token-based or sentence-aware chunking.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    cleaned = normalize_text(text)
    if not cleaned:
        return []

    chunks = []
    start = 0
    step = chunk_size - overlap
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(cleaned):
            break
        start += step
    return chunks
