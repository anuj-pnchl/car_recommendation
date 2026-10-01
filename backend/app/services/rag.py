"""
RAG answer generation with hybrid retrieval.

Flow:
  User question
    → parse structured constraints (budget, fuel, …)
    → filter cars.json candidates
    → semantic retrieve among candidates (ChromaDB)
    → build grounded context
    → Gemini recommendation
"""

from __future__ import annotations

from typing import Any

from google.genai import errors as genai_errors

from app.services.embeddings import EmbeddingError
from app.services.gemini import GeminiConfigError, get_chat_model, get_gemini_client
from app.services.query_parser import QueryConstraints
from app.services.retrieval import RetrievalError, hybrid_search_cars


class RagError(Exception):
    """Raised when Gemini answer generation fails."""


NO_MATCH_MESSAGE = (
    "I couldn't find a car in the available dataset that matches all of "
    "those requirements. Try relaxing one of the constraints (for example "
    "budget, fuel type, or body type), or ask without that filter."
)


def _format_price_inr(price: Any) -> str:
    """Turn an INR integer into a short readable string when possible."""
    try:
        value = int(price)
    except (TypeError, ValueError):
        return str(price)
    lakhs = value / 100000
    if lakhs >= 1:
        # e.g. 1450000 → "14.5 lakh (₹14,50,000)"
        return f"{lakhs:.2f}".rstrip("0").rstrip(".") + f" lakh (₹{value:,})"
    return f"₹{value:,}"


def _format_constraints_for_prompt(constraints: QueryConstraints) -> str:
    """Human-readable summary of extracted filters for the Gemini prompt."""
    public = constraints.to_public_dict()
    if not public:
        return "None detected (use semantic relevance only)."

    lines: list[str] = []
    if "max_price" in public:
        lines.append(f"- Maximum price: {_format_price_inr(public['max_price'])}")
    if "fuel_type" in public:
        lines.append(f"- Fuel type: {public['fuel_type']}")
    if public.get("transmissions"):
        lines.append(f"- Transmission (one of): {', '.join(public['transmissions'])}")
    if public.get("body_types"):
        lines.append(f"- Body type (one of): {', '.join(public['body_types'])}")
    if "seating_capacity_min" in public:
        lines.append(f"- Minimum seating: {public['seating_capacity_min']}")
    if "min_safety_rating" in public:
        lines.append(f"- Minimum safety rating: {public['min_safety_rating']}")
    return "\n".join(lines)


def build_context(results: list[dict[str, Any]]) -> str:
    """
    Turn retrieved Chroma matches into readable text for the Gemini prompt.

    Uses only document text + metadata already stored in ChromaDB.
    """
    blocks: list[str] = []

    for index, item in enumerate(results, start=1):
        meta = item.get("metadata") or {}
        document = (item.get("document") or "").strip()
        car_id = item.get("id", "")

        lines = [
            f"Car {index} (id: {car_id}):",
            f"Brand: {meta.get('brand', 'N/A')}",
            f"Model: {meta.get('model', 'N/A')}",
            f"Variant: {meta.get('variant', 'N/A')}",
            f"Body Type: {meta.get('body_type', 'N/A')}",
            f"Price: {_format_price_inr(meta.get('price', 'N/A'))}",
            f"Fuel: {meta.get('fuel_type', 'N/A')}",
            f"Transmission: {meta.get('transmission', 'N/A')}",
            f"Seating Capacity: {meta.get('seating_capacity', 'N/A')}",
            f"Safety Rating: {meta.get('safety_rating', 'N/A')}",
        ]
        if document:
            lines.append(f"Description: {document}")

        blocks.append("\n".join(lines))

    return "\n\n".join(blocks)


def build_rag_prompt(
    query: str,
    context: str,
    constraints: QueryConstraints,
) -> str:
    """Grounded prompt: answer only from the retrieved car context."""
    filters_text = _format_constraints_for_prompt(constraints)
    return f"""You are a car recommendation assistant for a learning demo dataset of Indian-market cars.

The cars below were retrieved from the application's dataset using hybrid retrieval
(structured filters + semantic search). They already satisfy any explicit constraints
that could be extracted from the user's question.

Answer the user's question using ONLY the car information provided in the context below.

Rules:
- Respect the user's explicit constraints listed below. Do not recommend a car that
  violates them (the context should already be filtered).
- Do not invent prices, specifications, mileage, safety ratings, features, or other facts.
- Do not use general world knowledge about cars outside this context.
- Do not recommend cars that are not listed in the context.
- If the context is empty or no car fits, clearly say that no matching car was found
  in the available dataset.
- You may explain trade-offs between the matching cars (price, fuel, seating, etc.).
- Keep the recommendation clear, helpful, and concise.

Explicit constraints extracted from the question:
{filters_text}

Retrieved car information:
{context}

User question:
{query}
"""


def _call_gemini(prompt: str) -> str:
    """Send the grounded prompt to Gemini and return plain text."""
    from google.genai import types

    client = get_gemini_client()
    model = get_chat_model()

    try:
        result = client.models.generate_content(
            model=model,
            contents=prompt,
            # Disable AFC — we only need plain text answers for RAG.
            config=types.GenerateContentConfig(
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            ),
        )
    except genai_errors.APIError as exc:
        # Covers ClientError (4xx) and ServerError (5xx) from google-genai.
        message = str(exc)
        status = getattr(exc, "code", None) or getattr(exc, "status_code", None)
        if (
            status == 429
            or "429" in message
            or "RESOURCE_EXHAUSTED" in message
            or "quota" in message.lower()
        ):
            raise RagError(
                "Gemini free-tier quota/rate limit reached for this chat model. "
                "Wait a minute and try again, or set GEMINI_CHAT_MODEL="
                "gemini-flash-lite-latest in backend/.env"
            ) from None
        if status in (500, 502, 503) or type(exc).__name__ == "ServerError":
            raise RagError(
                "Gemini is temporarily unavailable. Please try again in a moment."
            ) from None
        raise RagError(f"Gemini chat request failed: {exc}") from None
    except GeminiConfigError:
        raise
    except Exception as exc:
        name = type(exc).__name__
        if name == "ServerError":
            raise RagError(
                "Gemini is temporarily unavailable. Please try again in a moment."
            ) from None
        raise RagError(f"Unable to generate answer: {name}") from None

    text = (getattr(result, "text", None) or "").strip()
    if not text:
        raise RagError("Gemini returned an empty answer.")
    return text


def generate_rag_answer(query: str, top_k: int = 5) -> dict[str, Any]:
    """
    Full hybrid RAG pipeline for one user question.

    Returns:
      {
        "query": ...,
        "response": ...,
        "retrieved_count": ...,
        "sources": [ {id, metadata, distance}, ... ],
        "filters": { ... }   # extracted constraints (for debugging)
      }
    """
    cleaned = (query or "").strip()
    if not cleaned:
        raise ValueError("Message must not be empty.")

    # 1) Hybrid retrieve: structured filters + semantic ranking.
    try:
        results, constraints = hybrid_search_cars(query=cleaned, top_k=top_k)
    except (ValueError, EmbeddingError, RetrievalError):
        raise

    filters = constraints.to_public_dict()

    sources = [
        {
            "id": item.get("id"),
            "metadata": item.get("metadata") or {},
            "distance": item.get("distance"),
        }
        for item in results
    ]

    # 2) No matching candidates → do not invent unrelated recommendations.
    if not results:
        if constraints.has_hard_filters():
            response = NO_MATCH_MESSAGE
        else:
            response = (
                "I could not find any matching cars in the available dataset. "
                "Please try a different question, or make sure car documents "
                "have been ingested into ChromaDB."
            )
        return {
            "query": cleaned,
            "response": response,
            "retrieved_count": 0,
            "sources": [],
            "filters": filters,
        }

    # 3) Build context and ask Gemini for a grounded answer.
    context = build_context(results)
    prompt = build_rag_prompt(cleaned, context, constraints)
    answer = _call_gemini(prompt)

    return {
        "query": cleaned,
        "response": answer,
        "retrieved_count": len(results),
        "sources": sources,
        "filters": filters,
    }
