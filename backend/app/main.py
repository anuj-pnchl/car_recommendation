"""
FastAPI application entry point.

Step 1: health check
Step 2: cars endpoint (data/cars.json)
Step 4: embeddings learning endpoint
Step 5: ChromaDB status (ingestion via scripts)
Step 6: semantic search (retrieve car docs)
Step 7: RAG chat answer (retrieve + Gemini grounded answer)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.cars import router as cars_router
from app.api.chat import router as chat_router
from app.api.chroma import router as chroma_router
from app.api.embeddings import router as embeddings_router
from app.api.search import router as search_router
from app.schemas import HealthResponse

app = FastAPI(
    title="Car Recommendation RAG API",
    description="Backend for a beginner-friendly Car Recommendation RAG Chatbot",
    version="0.7.0",
)

# CORS lets the React app (localhost:5173) call this API (localhost:8000).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cars_router)
app.include_router(embeddings_router)
app.include_router(chroma_router)
app.include_router(search_router)
app.include_router(chat_router)


@app.get("/api/health", response_model=HealthResponse)
def health_check():
    """Simple health endpoint used by the React 'Check Backend' button."""
    return HealthResponse(
        status="ok",
        message="Car Recommendation RAG API is running",
    )
