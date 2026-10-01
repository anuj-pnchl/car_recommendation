"""Pydantic schemas for the embedding learning/test endpoint."""

from pydantic import BaseModel, Field


class EmbeddingRequest(BaseModel):
    """Request body for POST /api/embeddings."""

    text: str = Field(..., min_length=1, description="Text to convert into an embedding")


class EmbeddingResponse(BaseModel):
    """
    Response for POST /api/embeddings.

    Only a short preview of the vector is returned (not the full list).
    Dimension is computed dynamically as len(embedding).
    """

    dimension: int
    embedding_preview: list[float]
    model: str
