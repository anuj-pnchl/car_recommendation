"""Pydantic schemas for RAG chat (Step 7)."""

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for POST /api/chat."""

    message: str = Field(..., min_length=1, description="User question about cars")
    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="How many car documents to retrieve (1–10)",
    )


class ChatSource(BaseModel):
    """One retrieved car used as grounding context."""

    id: str
    metadata: dict[str, Any]
    distance: float | None = None


class ChatResponse(BaseModel):
    """Response for POST /api/chat."""

    query: str
    response: str
    retrieved_count: int
    sources: list[ChatSource]
    # Extracted structured constraints (helpful for debugging hybrid retrieval).
    filters: dict[str, Any] = Field(default_factory=dict)
