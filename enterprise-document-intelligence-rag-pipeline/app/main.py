from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.config import get_settings
from app.database import init_db
from app.schemas import IngestRequest, QueryRequest, SearchRequest
from app.services.ingestion import ingest_directory
from app.services.llm import generate_answer
from app.services.retrieval import search


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=get_settings().app_name,
    version="1.0.0",
    description="A small learning project for document search and RAG.",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": get_settings().app_name}


@app.post("/api/ingest")
def ingest(request: IngestRequest) -> dict:
    try:
        return ingest_directory(request.directory)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/search")
def semantic_search(request: SearchRequest) -> dict:
    try:
        results = search(request.query, request.top_k)
        return {
            "query": request.query,
            "results": [r.__dict__ for r in results],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/query")
def rag_query(request: QueryRequest) -> dict:
    try:
        results = search(request.query, request.top_k)
        answer, provider = generate_answer(request.query, results)
        return {
            "query": request.query,
            "answer": answer,
            "provider": provider,
            "sources": [
                {"document": r.document, "chunk_id": r.chunk_id, "score": r.score}
                for r in results
            ],
            "retrieved_context": [r.__dict__ for r in results],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
