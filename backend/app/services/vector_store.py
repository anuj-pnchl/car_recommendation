"""
ChromaDB vector store (Step 5).

Stores car documents + Gemini embeddings in a local persistent database.

Flow (this step):
  cars.json → car_to_document() → Gemini embedding → ChromaDB

Data is saved under:
  backend/chroma_db/

Semantic search is implemented in retrieval.py (Step 6).
RAG chat answer generation is NOT implemented here yet.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

# backend/ is two levels above this file: services/ → app/ → backend/
BACKEND_DIR = Path(__file__).resolve().parents[2]
CHROMA_PATH = BACKEND_DIR / "chroma_db"
COLLECTION_NAME = "car_documents"


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Open (or create) the local persistent ChromaDB client.

    Files are written under backend/chroma_db/ so data survives restarts.
    """
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_PATH))


def get_car_collection() -> Collection:
    """
    Get or create the car_documents collection.

    We use cosine space because Gemini embeddings are compared with
    cosine similarity (same idea as Step 4).
    """
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def get_document_count() -> int:
    """How many car documents are currently stored."""
    return get_car_collection().count()


def upsert_car_document(
    *,
    car_id: str,
    document: str,
    embedding: list[float],
    metadata: dict[str, Any],
) -> None:
    """
    Insert or update one car document.

    Using upsert + stable car IDs makes ingestion safe to re-run
    without creating duplicates.
    """
    collection = get_car_collection()
    collection.upsert(
        ids=[car_id],
        documents=[document],
        embeddings=[embedding],
        metadatas=[metadata],
    )


def get_documents_by_ids(ids: list[str]) -> dict[str, Any]:
    """Fetch stored documents by their Chroma IDs (car IDs as strings)."""
    collection = get_car_collection()
    return collection.get(
        ids=ids,
        include=["documents", "metadatas"],
    )
