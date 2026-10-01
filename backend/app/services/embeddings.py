"""
Embedding service (Step 4).

An embedding converts text into a list of numbers (a vector) that
captures the *meaning* of the text — not just the exact words.

Why this matters for RAG / semantic search:
  Similar meaning  → vectors tend to point in a similar direction
  Different meaning → vectors tend to be less similar

Used by Step 5 to store vectors in ChromaDB and by Step 6 for query embeddings.
RAG chat answer generation comes in a later step.
"""

from __future__ import annotations

import math
from typing import Sequence

from google.genai import errors as genai_errors

from app.schemas.car import Car
from app.services.gemini import get_embedding_model, get_gemini_client


class EmbeddingError(Exception):
    """Raised when embedding generation fails (API converts this to HTTP errors)."""


def generate_embedding(text: str) -> list[float]:
    """
    Convert a text string into an embedding vector using Gemini.

    Steps:
      1. Validate the input text.
      2. Call the Gemini embedding model via the google-genai SDK.
      3. Return the list of floats (the embedding vector).

    The vector length (dimension) depends on the model — do not hardcode it.
    """
    cleaned = (text or "").strip()
    if not cleaned:
        raise EmbeddingError("Text must not be empty.")

    client = get_gemini_client()
    model = get_embedding_model()

    try:
        # Official google-genai API:
        #   client.models.embed_content(model=..., contents=...)
        result = client.models.embed_content(
            model=model,
            contents=cleaned,
        )
    except genai_errors.ClientError as exc:
        raise EmbeddingError(f"Gemini embedding request failed: {exc}") from None
    except EmbeddingError:
        raise
    except Exception as exc:
        # Avoid leaking secrets; keep a short, useful message.
        raise EmbeddingError(
            f"Unable to generate embedding: {type(exc).__name__}"
        ) from None

    # Response shape: result.embeddings[0].values → list[float]
    if not result.embeddings or result.embeddings[0].values is None:
        raise EmbeddingError("Gemini returned an empty embedding.")

    return list(result.embeddings[0].values)


def cosine_similarity(vector_a: Sequence[float], vector_b: Sequence[float]) -> float:
    """
    Measure how similar two embedding vectors are.

    Cosine similarity =
        dot(A, B) / (||A|| * ||B||)

    Meaning:
      - Result is between -1 and 1 for typical embeddings (often ~0 to 1 for text).
      - Closer to 1  → more similar meaning.
      - Closer to 0  → less related meaning.

    Pure Python (no heavy ML framework) so beginners can see the math.
    """
    if len(vector_a) != len(vector_b):
        raise ValueError("Vectors must have the same dimension.")
    if not vector_a:
        raise ValueError("Vectors must not be empty.")

    dot = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)


def car_to_document(car: Car | dict) -> str:
    """
    Convert one car into a plain-text document for future embedding / RAG.

    Structured fields become readable sentences. Descriptive fields
    (features, suitable_for, description) add semantic meaning.

    Used by scripts/ingest_cars.py to build text before Gemini embedding.
    """
    if isinstance(car, dict):
        car = Car.model_validate(car)

    features = ", ".join(car.features) if car.features else "N/A"
    safety_features = (
        ", ".join(car.safety_features) if car.safety_features else "N/A"
    )
    suitable = ", ".join(car.suitable_for) if car.suitable_for else "N/A"

    return (
        f"{car.brand} {car.model} {car.variant} is a {car.body_type}. "
        f"It uses {car.fuel_type} fuel and has a {car.transmission} transmission. "
        f"Approximate price is {car.price} INR. "
        f"It seats {car.seating_capacity} people and has a mileage of {car.mileage} km/l. "
        f"Engine: {car.engine}, power: {car.power}, torque: {car.torque}. "
        f"Boot space is {car.boot_space} litres. "
        f"It has a {car.safety_rating}-star safety rating. "
        f"Safety features include {safety_features}. "
        f"It is suitable for {suitable}. "
        f"Features include {features}. "
        f"{car.description}"
    )
