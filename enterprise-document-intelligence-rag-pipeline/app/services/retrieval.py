"""Semantic search over document chunks stored in PostgreSQL."""

from app.database import get_connection
from app.models import RetrievedChunk
from app.services.embeddings import embed_query


def search(query: str, top_k: int = 5) -> list[RetrievedChunk]:
    """Return the document chunks most similar to a user question."""
    vector = embed_query(query)

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT d.filename,
                   c.id AS chunk_id,
                   c.content,
                   1 - (c.embedding <=> %s::vector) AS score
            FROM document_chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s
            """,
            (str(vector), str(vector), top_k),
        ).fetchall()

    return [
        RetrievedChunk(
            document=row["filename"],
            chunk_id=row["chunk_id"],
            score=round(float(row["score"]), 4),
            text=row["content"],
        )
        for row in rows
    ]
