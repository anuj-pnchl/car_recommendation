"""
ChromaDB status API (Step 5 — verification only).

GET /api/chroma/status
  Returns the car_documents collection name and document count.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.chroma import ChromaStatusResponse
from app.services.vector_store import COLLECTION_NAME, get_document_count

router = APIRouter(prefix="/api/chroma", tags=["chroma"])


@router.get("/status", response_model=ChromaStatusResponse)
def chroma_status():
    """Check that the local ChromaDB collection is reachable."""
    try:
        count = get_document_count()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to read ChromaDB status: {type(exc).__name__}",
        ) from None

    return ChromaStatusResponse(
        collection=COLLECTION_NAME,
        document_count=count,
    )
