"""Embedding helpers.

The model is cached so it is loaded once per application process instead of once per request.
"""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import get_settings


@lru_cache
def get_model() -> SentenceTransformer:
    return SentenceTransformer(get_settings().embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Convert a list of texts into normalized embedding vectors."""
    if not texts:
        return []
    vectors = get_model().encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return vectors.tolist()


def embed_query(query: str) -> list[float]:
    """Create an embedding for one user question."""
    return embed_texts([query])[0]
