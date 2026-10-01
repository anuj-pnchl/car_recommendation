"""
Cars API routes.

GET /api/cars — list cars from data/cars.json with optional filters.
"""

from fastapi import APIRouter, Query

from app.schemas.car import CarsResponse
from app.services.cars import filter_cars, load_cars

router = APIRouter(prefix="/api", tags=["cars"])


@router.get("/cars", response_model=CarsResponse)
def get_cars(
    body_type: str | None = Query(
        default=None,
        description="Filter by body type, e.g. SUV, Hatchback",
    ),
    fuel_type: str | None = Query(
        default=None,
        description="Filter by fuel type, e.g. Petrol, Diesel",
    ),
    transmission: str | None = Query(
        default=None,
        description="Filter by transmission, e.g. Automatic, Manual",
    ),
    max_price: int | None = Query(
        default=None,
        ge=0,
        description="Only include cars with price <= this value (INR)",
    ),
):
    """
    Return cars from the JSON dataset.

    Example:
      /api/cars?body_type=SUV&fuel_type=Petrol&max_price=1500000
    """
    cars = load_cars()
    filtered = filter_cars(
        cars,
        body_type=body_type,
        fuel_type=fuel_type,
        transmission=transmission,
        max_price=max_price,
    )
    return CarsResponse(count=len(filtered), cars=filtered)
