"""
Simple natural-language constraint extraction (hybrid retrieval).

This is NOT a full NLP system. It only looks for obvious keywords such as
petrol/diesel, automatic/manual, SUV/sedan, and "under X lakh".
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field


@dataclass
class QueryConstraints:
    """Structured filters extracted from a user question."""

    max_price: int | None = None
    fuel_type: str | None = None
    # When set, car.transmission must be one of these values.
    transmissions: list[str] = field(default_factory=list)
    # When set, car.body_type must be one of these values.
    body_types: list[str] = field(default_factory=list)
    seating_capacity_min: int | None = None
    min_safety_rating: int | None = None

    def has_hard_filters(self) -> bool:
        """True when at least one explicit structured constraint was found."""
        return any(
            [
                self.max_price is not None,
                self.fuel_type is not None,
                bool(self.transmissions),
                bool(self.body_types),
                self.seating_capacity_min is not None,
                self.min_safety_rating is not None,
            ]
        )

    def to_public_dict(self) -> dict:
        """Compact dict for API debugging (omit empty fields)."""
        data = asdict(self)
        return {key: value for key, value in data.items() if value not in (None, [], "")}


# Canonical values matching data/cars.json
_FUEL_ALIASES = {
    "petrol": "Petrol",
    "diesel": "Diesel",
    "cng": "CNG",
    "electric": "Electric",
    "ev": "Electric",
}

# "automatic" in user language → any non-manual gearbox in our dataset
_AUTOMATIC_GROUP = ["Automatic", "AMT", "CVT", "DCT", "e-CVT"]


def _extract_max_price(text: str) -> int | None:
    """
    Parse budgets like:
      under 15 lakh / below 12 lakhs / up to 10 lakh / 15 lakh budget
    Returns price in INR (lakh * 100000).
    """
    patterns = [
        r"(?:under|below|upto|up to|less than)\s+(\d+(?:\.\d+)?)\s*lakh",
        r"(\d+(?:\.\d+)?)\s*lakh(?:s)?\s+(?:budget|or less|max|maximum)",
        r"budget\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*lakh",
        r"(?:under|below|upto|up to)\s+₹?\s*(\d+(?:\.\d+)?)\s*lakh",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            lakhs = float(match.group(1))
            return int(lakhs * 100000)
    return None


def _extract_fuel(text: str) -> str | None:
    for alias, canonical in _FUEL_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", text, flags=re.IGNORECASE):
            return canonical
    return None


def _extract_transmissions(text: str) -> list[str]:
    if re.search(r"\bmanual\b", text, flags=re.IGNORECASE):
        return ["Manual"]
    if re.search(r"\b(automatic|auto|amt|cvt|dct)\b", text, flags=re.IGNORECASE):
        return list(_AUTOMATIC_GROUP)
    return []


def _extract_body_types(text: str) -> list[str]:
    # More specific phrases first.
    if re.search(r"\bcompact\s+suv\b", text, flags=re.IGNORECASE):
        return ["Compact SUV"]
    if re.search(r"\bhatchback\b", text, flags=re.IGNORECASE):
        return ["Hatchback"]
    if re.search(r"\bsedan\b", text, flags=re.IGNORECASE):
        return ["Sedan"]
    if re.search(r"\bmpv\b", text, flags=re.IGNORECASE):
        return ["MPV"]
    if re.search(r"\bsuv\b", text, flags=re.IGNORECASE):
        # In this dataset, users saying "SUV" usually accept Compact SUV too.
        return ["SUV", "Compact SUV"]
    return []


def _extract_seating_min(text: str) -> int | None:
    patterns = [
        r"family\s+of\s+(\d+)",
        r"(\d+)\s*(?:people|persons|seater|seaters|seats)",
        r"seats?\s+(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    # Soft family phrase without a number → at least 5 seats.
    if re.search(r"\bfamily\b", text, flags=re.IGNORECASE):
        return 5
    return None


def _extract_min_safety(text: str) -> int | None:
    if re.search(r"\b(safe|safety|safest)\b", text, flags=re.IGNORECASE):
        return 4
    return None


def parse_query_constraints(query: str) -> QueryConstraints:
    """
    Extract obvious structured constraints from a natural-language question.

    Returns an empty-constraint object when nothing clear is found
    (pure semantic search will be used).
    """
    text = (query or "").strip().lower()
    if not text:
        return QueryConstraints()

    return QueryConstraints(
        max_price=_extract_max_price(text),
        fuel_type=_extract_fuel(text),
        transmissions=_extract_transmissions(text),
        body_types=_extract_body_types(text),
        seating_capacity_min=_extract_seating_min(text),
        min_safety_rating=_extract_min_safety(text),
    )
