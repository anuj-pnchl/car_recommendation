"""
Car data service.

Reads cars from data/cars.json and applies simple structured filters.
No database — the JSON file is the source of truth for this step.
"""

import json
from pathlib import Path

from fastapi import HTTPException

from app.schemas.car import Car

# Project root is three levels above this file:
#   services/ -> app/ -> backend/ -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CARS_FILE = PROJECT_ROOT / "data" / "cars.json"


def load_cars() -> list[Car]:
    """
    Load and validate all cars from the JSON file.

    Raises HTTPException if the file is missing or invalid,
    so the API returns a clean error instead of a stack trace.
    """
    if not CARS_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Car data file not found at: {CARS_FILE}",
        )

    try:
        with CARS_FILE.open(encoding="utf-8") as file:
            raw_data = json.load(file)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Car data file is not valid JSON.",
        )
    except OSError:
        raise HTTPException(
            status_code=500,
            detail="Unable to read car data file.",
        )

    if not isinstance(raw_data, list):
        raise HTTPException(
            status_code=500,
            detail="Car data file must contain a JSON array of cars.",
        )

    try:
        return [Car.model_validate(item) for item in raw_data]
    except Exception:
        # Keep the message beginner-friendly; avoid leaking internals.
        raise HTTPException(
            status_code=500,
            detail="Car data file has invalid car records.",
        )


def filter_cars(
    cars: list[Car],
    body_type: str | None = None,
    fuel_type: str | None = None,
    transmission: str | None = None,
    max_price: int | None = None,
    body_types: list[str] | None = None,
    transmissions: list[str] | None = None,
    seating_capacity_min: int | None = None,
    min_safety_rating: int | None = None,
) -> list[Car]:
    """
    Apply simple filters on structured fields.

    Matching for text filters is case-insensitive.
    Multiple filters are combined with AND logic.
    """
    results = cars

    if body_types:
        allowed = {value.strip().lower() for value in body_types if value}
        results = [c for c in results if c.body_type.lower() in allowed]
    elif body_type:
        needle = body_type.strip().lower()
        results = [c for c in results if c.body_type.lower() == needle]

    if fuel_type:
        needle = fuel_type.strip().lower()
        results = [c for c in results if c.fuel_type.lower() == needle]

    if transmissions:
        allowed = {value.strip().lower() for value in transmissions if value}
        results = [c for c in results if c.transmission.lower() in allowed]
    elif transmission:
        needle = transmission.strip().lower()
        results = [c for c in results if c.transmission.lower() == needle]

    if max_price is not None:
        results = [c for c in results if c.price <= max_price]

    if seating_capacity_min is not None:
        results = [
            c for c in results if c.seating_capacity >= seating_capacity_min
        ]

    if min_safety_rating is not None:
        results = [c for c in results if c.safety_rating >= min_safety_rating]

    return results
