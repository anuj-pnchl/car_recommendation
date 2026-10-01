# Backend — Car Recommendation RAG API

FastAPI backend for the Car Recommendation RAG Chatbot learning project.

## Current functionality

### Step 1–2

- `GET /api/health`
- `GET /api/cars` (+ filters)

### Step 4–6

- `POST /api/embeddings`
- ChromaDB under `backend/chroma_db/` (`car_documents`)
- `GET /api/chroma/status`
- `POST /api/search` — semantic retrieval

### Step 7

- `POST /api/chat` — RAG answer (retrieve + Gemini grounded generation)
- `app/services/rag.py` — context building + prompt + generation

## Setup

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

## Run API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## RAG chat

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Suggest a family SUV under 15 lakh","top_k":5}'
```

Flow:

1. Embed the user message (Gemini).
2. Retrieve top cars from ChromaDB.
3. Build a text context from those cars.
4. Ask Gemini to answer **only** from that context.
5. Return `{ response, sources, ... }`.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | Backend-only Gemini key |
| `GEMINI_EMBEDDING_MODEL` | Embedding model (default `gemini-embedding-001`) |
| `GEMINI_CHAT_MODEL` | Chat model (default `gemini-flash-lite-latest`) |

## Folder overview

| Path | Purpose |
|------|---------|
| `app/api/chat.py` | `POST /api/chat` |
| `app/services/rag.py` | RAG pipeline |
| `app/services/retrieval.py` | Semantic search |
| `app/services/vector_store.py` | ChromaDB helpers |
| `app/services/embeddings.py` | Gemini embeddings |
| `app/services/gemini.py` | Shared Gemini client |
