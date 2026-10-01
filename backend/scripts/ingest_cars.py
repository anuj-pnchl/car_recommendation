"""
Ingest cars from data/cars.json into ChromaDB (Step 5).

Flow:
  cars.json → car_to_document() → Gemini embedding → ChromaDB upsert

Safe to run multiple times: uses stable car IDs + upsert (no duplicates).

Run from the backend folder (venv activated):

  python scripts/ingest_cars.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
CARS_FILE = PROJECT_ROOT / "data" / "cars.json"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.schemas.car import Car  # noqa: E402
from app.services.embeddings import car_to_document, generate_embedding  # noqa: E402
from app.services.vector_store import (  # noqa: E402
    get_document_count,
    upsert_car_document,
)


def load_cars() -> list[Car]:
    if not CARS_FILE.exists():
        raise FileNotFoundError(f"Car data not found: {CARS_FILE}")

    with CARS_FILE.open(encoding="utf-8") as file:
        raw = json.load(file)

    if not isinstance(raw, list):
        raise ValueError("cars.json must be a JSON array")

    return [Car.model_validate(item) for item in raw]


def car_metadata(car: Car) -> dict:
    """Structured fields useful later for filters / display."""
    return {
        "brand": car.brand,
        "model": car.model,
        "variant": car.variant,
        "body_type": car.body_type,
        "price": car.price,
        "fuel_type": car.fuel_type,
        "transmission": car.transmission,
        "seating_capacity": car.seating_capacity,
        "safety_rating": car.safety_rating,
    }


def main() -> None:
    print("Loading cars...")
    cars = load_cars()
    print(f"Found {len(cars)} cars.")
    print()

    for car in cars:
        print(f"Embedding: {car.brand} {car.model}")
        document = car_to_document(car)
        embedding = generate_embedding(document)
        upsert_car_document(
            car_id=str(car.id),
            document=document,
            embedding=embedding,
            metadata=car_metadata(car),
        )

    print()
    print("Ingestion completed.")
    print(f"Documents in collection: {get_document_count()}")


if __name__ == "__main__":
    main()
