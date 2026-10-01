"""
Pydantic schemas for ChromaDB status (Step 5).
"""

from pydantic import BaseModel


class ChromaStatusResponse(BaseModel):
    """Response for GET /api/chroma/status."""

    collection: str
    document_count: int
