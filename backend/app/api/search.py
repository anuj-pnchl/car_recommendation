"""
Semantic search API (Step 6).

POST /api/search
  Embed the user question with Gemini, query ChromaDB, return top car docs.

Does NOT generate a Gemini chat answer — that is a later step.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem
from app.services.embeddings import EmbeddingError
from app.services.gemini import GeminiConfigError
from app.services.retrieval import RetrievalError, search_cars

router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search_car_documents(payload: SearchRequest):
    """
    Retrieve the most relevant car documents for a question.

    Example:
      { "query": "Suggest a family SUV under 15 lakh", "top_k": 5 }
    """
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    try:
        matches = search_cars(query=query, top_k=payload.top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    except GeminiConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from None
    except EmbeddingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from None
    except RetrievalError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from None

    results = [SearchResultItem(**item) for item in matches]
    return SearchResponse(query=query, count=len(results), results=results)
