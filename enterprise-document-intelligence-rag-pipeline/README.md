# Enterprise Document Intelligence & RAG Pipeline

A beginner-friendly Retrieval-Augmented Generation (RAG) project that I built to understand how an AI assistant can answer questions from a small set of company documents.

The project takes PDF/TXT files, cleans and splits the text into smaller chunks, creates embeddings with a Sentence Transformer model, stores those embeddings in PostgreSQL with `pgvector`, finds the most relevant chunks for a question, and optionally sends that context to an LLM through a simple FastAPI API.

> **Project level:** Fresher / learning project. This is a practical prototype, not a claim of production-scale enterprise infrastructure.

## Why I built this

I wanted one project that connects the topics I was learning separately:

- Python and SQL
- Data cleaning and preprocessing
- NLP and embeddings
- Semantic search
- RAG and LLMs
- REST APIs
- PostgreSQL
- Docker
- Basic testing and GitHub Actions

The goal was to understand the full flow instead of only calling an LLM API from a notebook.

## What the project does

Suppose the `data/documents/` folder contains simple company policies such as an employee handbook, IT support policy, and procurement policy.

A user can ask:

> **"What should I do if my company laptop stops working?"**

The application does not send all documents to the LLM. It first searches the stored document chunks and returns the most relevant ones. Those chunks are then used as context for the answer.

```text
PDF / TXT files
      |
      v
Read + clean text
      |
      v
Split into overlapping chunks
      |
      v
Create embeddings
      |
      v
PostgreSQL + pgvector
      |
      v
Semantic similarity search
      |
      v
Relevant context
      |
      v
Optional LLM answer
      |
      v
FastAPI response
```

## Tech stack

| Area | Tool |
|---|---|
| Language | Python |
| API | FastAPI |
| Database | PostgreSQL |
| Vector search | pgvector |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Documents | PDF / TXT |
| LLM option | OpenAI-compatible API or Ollama |
| Containerization | Docker / Docker Compose |
| Testing | pytest |
| CI | GitHub Actions |

## Repository structure

```text
enterprise-rag-pipeline/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── services/
│       ├── __init__.py
│       ├── chunking.py
│       ├── embeddings.py
│       ├── ingestion.py
│       ├── llm.py
│       └── retrieval.py
├── data/
│   └── documents/
│       ├── employee_handbook.txt
│       ├── it_support_policy.txt
│       ├── procurement_policy.txt
│       └── sample_policy.txt
├── docs/
│   └── sample_questions.md
├── scripts/
│   └── ingest_documents.py
├── tests/
│   ├── test_chunking.py
│   ├── test_health.py
│   └── test_retrieval.py
├── .github/workflows/ci.yml
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── LICENSE
├── Makefile
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/enterprise-rag-pipeline.git
cd enterprise-rag-pipeline
```

### 2. Create the environment file

```bash
# Windows PowerShell
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

The default configuration uses **retrieval-only mode**, so you can first learn the search part without needing an LLM API key.

### 3. Start PostgreSQL

The easiest option is Docker:

```bash
docker compose up -d db
```

### 4. Create a Python environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 5. Ingest the sample documents

```bash
python scripts/ingest_documents.py
```

The script:

1. Reads PDF/TXT files from `data/documents/`.
2. Cleans extra whitespace.
3. Splits long text into overlapping chunks.
4. Creates one embedding per chunk.
5. Saves the documents, chunks, and vectors in PostgreSQL.

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

FastAPI will show the interactive Swagger UI.

## Try the project

### Health check

```bash
curl http://127.0.0.1:8000/health
```

### Semantic search

```bash
curl -X POST http://127.0.0.1:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"How do I report a laptop problem?","top_k":5}'
```

This endpoint is useful for understanding the RAG retrieval step because it shows the matching document, chunk, similarity score, and text.

### RAG question answering

```bash
curl -X POST http://127.0.0.1:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"How do I report a laptop problem?","top_k":5}'
```

Without an LLM provider, the API returns the retrieved context so you can inspect what the search layer found.

## Optional: connect an LLM

### OpenAI-compatible provider

Add values to `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=your_model
```

The code uses a small OpenAI-compatible `/chat/completions` request, so the base URL can also point to another compatible provider.

### Ollama

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2:3b
```

Run the selected Ollama model locally before using `/api/query` in Ollama mode.

## Design decisions I made

### Why chunk the text?

Long documents are harder to search directly. Smaller overlapping chunks make it easier to retrieve the part of a document that is relevant to the question.

### Why embeddings?

Keyword search can miss related wording. Embeddings let the project compare the meaning of the question with the meaning of the stored chunks.

### Why PostgreSQL + pgvector?

I wanted the project to use SQL for the application data while also learning how vector data can be stored and searched in the same database.

### Why FastAPI?

It gave me a simple way to turn the Python pipeline into an API that another application could call.

## What I learned

This project helped me understand the difference between:

- **Data ingestion** – getting raw documents into the pipeline.
- **Chunking** – breaking text into searchable pieces.
- **Embeddings** – converting text into numerical vectors.
- **Retrieval** – selecting the most similar chunks for a question.
- **RAG** – giving those retrieved chunks to an LLM as context before generating an answer.

I also got practical experience with environment variables, Docker Compose, SQL table design, API schemas, error handling, and basic automated tests.

## Limitations

This is intentionally a small learning project. It currently has a simple chunking strategy, a basic similarity search, a small sample document set, and no authentication or advanced evaluation framework.

Those limitations are deliberate: the project shows that I understand the core pipeline and gives me a clear base for improving it later.

## Possible next steps

- Add a small web interface for uploading documents and asking questions.
- Add metadata filters such as department or document type.
- Compare different embedding models.
- Add retrieval metrics and a small evaluation dataset.
- Add a background job for larger document collections.
- Add authentication and rate limiting before using it in a real service.

## How I would explain it in an interview

> "I built a small RAG application to understand the complete path from raw company documents to an AI answer. I used Python to ingest and clean PDF/TXT files, chunked the text, generated embeddings with Sentence Transformers, stored them in PostgreSQL using pgvector, and used similarity search to retrieve relevant chunks. FastAPI exposes the workflow as an API, and an optional LLM uses the retrieved text as context. The main thing I learned was how the data pipeline and retrieval layer fit together before the LLM step."

## License

MIT
