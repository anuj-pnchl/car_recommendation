"""
RAG chat API (Steps 7 + 10).

POST /api/chat
  Hybrid retrieve (structured filters + Chroma semantic search),
  then ask Gemini to answer using only that retrieved context.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse, ChatSource
from app.services.embeddings import EmbeddingError
from app.services.gemini import GeminiConfigError
from app.services.rag import RagError, generate_rag_answer
from app.services.retrieval import RetrievalError

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat_rag(payload: ChatRequest):
    """
    Grounded car recommendation using hybrid RAG.

    Example:
      { "message": "Suggest a petrol automatic SUV under 15 lakh", "top_k": 5 }
    """
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message must not be empty.")

    try:
        result = generate_rag_answer(query=message, top_k=payload.top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    except GeminiConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from None
    except EmbeddingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from None
    except RetrievalError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from None
    except RagError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from None

    return ChatResponse(
        query=result["query"],
        response=result["response"],
        retrieved_count=result["retrieved_count"],
        sources=[ChatSource(**source) for source in result["sources"]],
        filters=result.get("filters") or {},
    )
