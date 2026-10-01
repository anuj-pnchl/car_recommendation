"""
Embeddings API (Step 4 — learning/testing only).

POST /api/embeddings
  Converts text → embedding vector preview.
  Does NOT store vectors and does NOT perform search.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.embeddings import EmbeddingRequest, EmbeddingResponse
from app.services.embeddings import EmbeddingError, generate_embedding
from app.services.gemini import GeminiConfigError, get_embedding_model

router = APIRouter(prefix="/api", tags=["embeddings"])

# How many numbers to show in the preview (full vector can be thousands long).
PREVIEW_LENGTH = 5


@router.post("/embeddings", response_model=EmbeddingResponse)
def create_embedding(payload: EmbeddingRequest):
    """
    Generate an embedding for the given text and return a small preview.

    Example request:
      { "text": "I need a comfortable family SUV" }
    """
    try:
        vector = generate_embedding(payload.text)
    except GeminiConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from None
    except EmbeddingError as exc:
        message = str(exc)
        status = 400 if "empty" in message.lower() else 502
        raise HTTPException(status_code=status, detail=message) from None

    return EmbeddingResponse(
        dimension=len(vector),
        embedding_preview=[float(v) for v in vector[:PREVIEW_LENGTH]],
        model=get_embedding_model(),
    )
