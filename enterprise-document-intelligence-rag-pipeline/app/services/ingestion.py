from hashlib import sha256
from pathlib import Path

from pypdf import PdfReader

from app.config import get_settings
from app.database import get_connection
from app.services.chunking import chunk_text
from app.services.embeddings import embed_texts

SUPPORTED_SUFFIXES = {".txt", ".pdf"}


def read_document(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def ingest_directory(directory: str) -> dict:
    root = Path(directory)
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Directory does not exist: {directory}")

    files = sorted(p for p in root.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES)
    documents = 0
    chunks_total = 0

    with get_connection() as conn:
        for path in files:
            raw = read_document(path)
            chunks = chunk_text(raw, get_settings().chunk_size, get_settings().chunk_overlap)
            if not chunks:
                continue

            content_hash = sha256(raw.encode("utf-8")).hexdigest()
            row = conn.execute(
                """
                INSERT INTO documents(filename, content_hash)
                VALUES (%s, %s)
                ON CONFLICT(filename) DO UPDATE SET content_hash=EXCLUDED.content_hash
                RETURNING id
                """,
                (path.name, content_hash),
            ).fetchone()
            document_id = row["id"]
            conn.execute("DELETE FROM document_chunks WHERE document_id = %s", (document_id,))

            vectors = embed_texts(chunks)
            for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
                conn.execute(
                    """
                    INSERT INTO document_chunks(document_id, chunk_index, content, embedding)
                    VALUES (%s, %s, %s, %s::vector)
                    """,
                    (document_id, idx, chunk, str(vector)),
                )
            documents += 1
            chunks_total += len(chunks)

    return {"documents_ingested": documents, "chunks_created": chunks_total}
