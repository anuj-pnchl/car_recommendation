"""
Learning script: generate embeddings and compare meanings with cosine similarity.

Run from the backend folder (with venv activated):

  python scripts/test_embeddings.py

What this demonstrates:
  1. Text → Gemini embedding model → vector of numbers
  2. Similar sentences tend to have higher cosine similarity
  3. Different sentences tend to have lower cosine similarity

No ChromaDB / vector search / RAG here — that comes in a later step.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `from app...` when running as a script from backend/
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.embeddings import (  # noqa: E402
    car_to_document,
    cosine_similarity,
    generate_embedding,
)
from app.services.gemini import get_embedding_model  # noqa: E402


PREVIEW_LENGTH = 10

EXAMPLE_TEXTS = [
    "I need a family car",
    "I need a comfortable SUV for highway travel",
    "I want a fast sports car",
    "I need a fuel efficient car for city driving",
]

SIMILARITY_PAIRS = [
    ("I need a family car", "I need a car for my family"),
    ("I need a family car", "I want a sports car"),
]


def print_embedding(text: str, vector: list[float]) -> None:
    preview = [round(v, 6) for v in vector[:PREVIEW_LENGTH]]
    print("Text:")
    print(text)
    print()
    print("Embedding dimension:")
    print(len(vector))
    print()
    print(f"First {PREVIEW_LENGTH} values:")
    print(preview)
    print("-" * 60)


def main() -> None:
    print("=" * 60)
    print("Step 4 — Gemini Embeddings Demo")
    print(f"Model: {get_embedding_model()}")
    print("=" * 60)
    print()

    # --- Part 1: generate and inspect embeddings ---
    print("Part 1: Generate embeddings for example texts")
    print()
    for text in EXAMPLE_TEXTS:
        vector = generate_embedding(text)
        print_embedding(text, vector)

    # --- Part 2: cosine similarity experiment ---
    print()
    print("=" * 60)
    print("Similarity experiment:")
    print("Higher cosine similarity ≈ closer meaning")
    print("=" * 60)
    print()

    for text_a, text_b in SIMILARITY_PAIRS:
        emb_a = generate_embedding(text_a)
        emb_b = generate_embedding(text_b)
        score = cosine_similarity(emb_a, emb_b)

        print("Text A:")
        print(text_a)
        print()
        print("Text B:")
        print(text_b)
        print()
        print("Cosine similarity:")
        print(f"{score:.4f}")
        print()
        print("---")
        print()

    # --- Part 3: preview car_to_document (no embedding of full dataset) ---
    print("=" * 60)
    print("car_to_document() helper preview (not embedding all cars yet)")
    print("=" * 60)
    sample_car = {
        "id": 1,
        "brand": "Tata",
        "model": "Nexon",
        "variant": "Creative+",
        "body_type": "Compact SUV",
        "price": 1450000,
        "fuel_type": "Petrol",
        "transmission": "Automatic",
        "mileage": 17.0,
        "seating_capacity": 5,
        "engine": "1199 cc",
        "power": "118 bhp",
        "torque": "170 Nm",
        "boot_space": 382,
        "safety_rating": 5,
        "safety_features": ["6 Airbags", "ABS", "ESC", "Hill Hold Control"],
        "features": [
            "Touchscreen Infotainment",
            "Apple CarPlay",
            "Android Auto",
            "Cruise Control",
        ],
        "suitable_for": ["Family", "City Driving", "Highway Driving"],
        "description": "A compact SUV suitable for city and family use.",
    }
    document = car_to_document(sample_car)
    print(document)
    print()
    print("Done. Next step will store embeddings in ChromaDB for vector search.")


if __name__ == "__main__":
    main()
