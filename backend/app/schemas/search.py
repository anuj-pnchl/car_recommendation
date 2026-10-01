"""Pydantic schemas for semantic search (Step 6)."""

from typing import Any

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request body for POST /api/search."""

    query: str = Field(..., min_length=1, description="Natural-language car question")
    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of similar car documents to return (1–10)",
    )


class SearchResultItem(BaseModel):
    """One retrieved car document from ChromaDB."""

    id: str
    document: str
    metadata: dict[str, Any]
    distance: float | None = None


class SearchResponse(BaseModel):
    """Response for POST /api/search."""

    query: str
    count: int
    results: list[SearchResultItem]
