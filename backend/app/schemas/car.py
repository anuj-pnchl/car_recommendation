"""
Pydantic models for car data.

These models mirror the fields in data/cars.json so FastAPI can
validate and document the API responses.
"""

from pydantic import BaseModel, Field


class Car(BaseModel):
    """One car from the JSON dataset."""

    # --- Structured fields (good for exact filters later) ---
    id: int
    brand: str
    model: str
    variant: str
    body_type: str
    price: int = Field(description="Approximate price in INR (demo data)")
    fuel_type: str
    transmission: str
    mileage: float
    seating_capacity: int
    engine: str
    power: str
    torque: str
    boot_space: int
    safety_rating: int

    # --- Descriptive fields (useful later for semantic / RAG search) ---
    safety_features: list[str]
    features: list[str]
    suitable_for: list[str]
    description: str


class CarsResponse(BaseModel):
    """Response shape for GET /api/cars."""

    count: int
    cars: list[Car]
