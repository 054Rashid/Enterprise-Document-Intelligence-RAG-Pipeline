"""Small adapter for optional LLM generation.

The retrieval layer stays independent from the LLM provider so the project can
be run and understood even without an API key.
"""

from typing import Iterable

import requests

from app.config import get_settings
from app.models import RetrievedChunk


def build_prompt(question: str, chunks: Iterable[RetrievedChunk]) -> str:
    """Create a simple context-first prompt from the retrieved chunks."""
    context = "\n\n".join(
        f"[Source: {c.document} | chunk {c.chunk_id} | score {c.score}]\n{c.text}"
        for c in chunks
    )
    return (
        "You are a helpful company knowledge assistant. Answer the question using only the supplied context. "
        "Do not invent facts. If the context is not enough, say that the answer is not available in the "
        "provided documents. Mention the source filename(s) when useful.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )


def generate_answer(question: str, chunks: list[RetrievedChunk]) -> tuple[str, str]:
    """Generate an answer with the selected provider, or return retrieval-only mode."""
    settings = get_settings()

    if settings.llm_provider.lower() == "openai":
        if not settings.openai_api_key or not settings.openai_model:
            return (
                "OpenAI mode is selected, but OPENAI_API_KEY or OPENAI_MODEL is missing.",
                "openai-misconfigured",
            )

        response = requests.post(
            f"{settings.openai_base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={
                "model": settings.openai_model,
                "temperature": 0.1,
                "messages": [
                    {"role": "system", "content": "Answer only from the supplied context."},
                    {"role": "user", "content": build_prompt(question, chunks)},
                ],
            },
            timeout=60,
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"].strip()
        return answer, "openai"

    if settings.llm_provider.lower() == "ollama":
        response = requests.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/generate",
            json={
                "model": settings.ollama_model,
                "prompt": build_prompt(question, chunks),
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["response"].strip(), "ollama"

    return (
        "Retrieval-only mode: no LLM provider is configured. Review the returned source chunks.",
        "retrieval-only",
    )
