"""
Pydantic schemas (request/response models).
"""

from pydantic import BaseModel

from app.schemas.car import Car, CarsResponse
from app.schemas.chat import ChatRequest, ChatResponse, ChatSource
from app.schemas.chroma import ChromaStatusResponse
from app.schemas.embeddings import EmbeddingRequest, EmbeddingResponse
from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem

__all__ = [
    "HealthResponse",
    "Car",
    "CarsResponse",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "ChromaStatusResponse",
    "SearchRequest",
    "SearchResponse",
    "SearchResultItem",
    "ChatRequest",
    "ChatResponse",
    "ChatSource",
]


class HealthResponse(BaseModel):
    """Response shape for GET /api/health."""

    status: str
    message: str
