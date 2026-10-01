"""
Semantic + hybrid retrieval from ChromaDB.

Semantic search (Step 6):
  User question → Gemini embedding → ChromaDB nearest cars

Hybrid search (Step 10):
  User question
    → extract structured constraints (budget, fuel, …)
    → filter cars.json candidates (hard constraints)
    → semantic retrieve only among those candidates
"""

from __future__ import annotations

from typing import Any

from app.services.cars import filter_cars, load_cars
from app.services.embeddings import EmbeddingError, generate_embedding
from app.services.query_parser import QueryConstraints, parse_query_constraints
from app.services.vector_store import get_car_collection, get_document_count


class RetrievalError(Exception):
    """Raised when ChromaDB search fails."""


def search_cars(
    query: str,
    top_k: int = 5,
    allowed_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Find the most relevant car documents for a natural-language question.

    Args:
        query: User question, e.g. "Suggest a family SUV under 15 lakh"
        top_k: How many results to return (caller should already validate range)
        allowed_ids: Optional set of car IDs (as strings). When set, only these
            cars can appear in the result (used by hybrid retrieval).

    Returns:
        A list of dicts with id, document, metadata, and distance.
        Lower distance ≈ more similar (Chroma cosine space).
    """
    cleaned = (query or "").strip()
    if not cleaned:
        raise ValueError("Query must not be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    # If the collection is empty, return no results instead of failing.
    total = get_document_count()
    if total == 0:
        return []

    # When hard-filtering by ID, fetch a wider ranked list so candidates
    # near the bottom of a small top_k window are not missed.
    if allowed_ids is not None:
        if not allowed_ids:
            return []
        n_results = total
    else:
        n_results = min(top_k, total)

    # 1) Convert the question into the same embedding space as stored cars.
    try:
        query_embedding = generate_embedding(cleaned)
    except EmbeddingError:
        raise

    # 2) Ask Chroma for the nearest stored car vectors.
    try:
        collection = get_car_collection()
        raw = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:
        raise RetrievalError(
            f"ChromaDB query failed: {type(exc).__name__}"
        ) from None

    ids = (raw.get("ids") or [[]])[0]
    documents = (raw.get("documents") or [[]])[0]
    metadatas = (raw.get("metadatas") or [[]])[0]
    distances = (raw.get("distances") or [[]])[0]

    results: list[dict[str, Any]] = []
    for index, doc_id in enumerate(ids):
        if allowed_ids is not None and str(doc_id) not in allowed_ids:
            continue
        results.append(
            {
                "id": doc_id,
                "document": documents[index] if index < len(documents) else "",
                "metadata": metadatas[index] if index < len(metadatas) else {},
                "distance": distances[index] if index < len(distances) else None,
            }
        )
        if len(results) >= top_k:
            break

    return results


def hybrid_search_cars(
    query: str,
    top_k: int = 5,
) -> tuple[list[dict[str, Any]], QueryConstraints]:
    """
    Hybrid retrieval: structured filters first, then semantic ranking.

    Explicit constraints from the question (price, fuel, transmission, …)
    always take priority. Semantic search only ranks cars that already
    satisfy those constraints.
    """
    cleaned = (query or "").strip()
    constraints = parse_query_constraints(cleaned)

    allowed_ids: set[str] | None = None
    if constraints.has_hard_filters():
        cars = load_cars()
        candidates = filter_cars(
            cars,
            max_price=constraints.max_price,
            fuel_type=constraints.fuel_type,
            body_types=constraints.body_types or None,
            transmissions=constraints.transmissions or None,
            seating_capacity_min=constraints.seating_capacity_min,
            min_safety_rating=constraints.min_safety_rating,
        )
        if not candidates:
            # Hard constraints matched nothing — do not fall back to unrelated cars.
            return [], constraints
        allowed_ids = {str(car.id) for car in candidates}

    results = search_cars(query=cleaned, top_k=top_k, allowed_ids=allowed_ids)
    return results, constraints
