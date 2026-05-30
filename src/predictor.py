from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CarFeatures:
    """Input features used by the lightweight demo predictor.

    The point of this project is JMeter performance testing. The predictor is
    intentionally deterministic and fast so the test isolates API/runtime
    behavior rather than ML training time.
    """

    make: str
    model: str
    year: int
    mileage: int
    engine_size: float
    transmission: str
    fuel_type: str


MAKE_BASE_PRICE = {
    "toyota": 23_000,
    "honda": 22_000,
    "bmw": 46_000,
    "mercedes": 52_000,
    "hyundai": 19_000,
    "kia": 18_000,
    "ford": 25_000,
    "chevrolet": 24_000,
}

FUEL_ADJUSTMENT = {
    "petrol": 0,
    "diesel": 1_500,
    "hybrid": 3_500,
    "electric": 8_000,
}

TRANSMISSION_ADJUSTMENT = {
    "manual": -1_200,
    "automatic": 1_400,
}


def predict_price(features: CarFeatures) -> dict[str, float | int | str]:
    """Return a deterministic estimated price and a confidence band.

    This is a production-shaped stand-in for a persisted ML model. Replace this
    function with a joblib/scikit-learn model call when the trained artifact is
    available.
    """

    current_year = 2026
    make = features.make.strip().lower()
    fuel_type = features.fuel_type.strip().lower()
    transmission = features.transmission.strip().lower()

    base_price = MAKE_BASE_PRICE.get(make, 21_000)
    age = max(current_year - features.year, 0)
    age_depreciation = min(age * 0.055, 0.72)
    mileage_depreciation = min(features.mileage / 250_000 * 0.38, 0.52)
    engine_adjustment = max(features.engine_size - 1.6, -0.8) * 2_200

    estimated = (
        base_price * (1 - age_depreciation) * (1 - mileage_depreciation)
        + FUEL_ADJUSTMENT.get(fuel_type, 0)
        + TRANSMISSION_ADJUSTMENT.get(transmission, 0)
        + engine_adjustment
    )

    estimated = max(round(estimated, 2), 1_000.00)
    band = round(estimated * 0.08, 2)

    return {
        "currency": "USD",
        "estimated_price": estimated,
        "lower_bound": round(estimated - band, 2),
        "upper_bound": round(estimated + band, 2),
        "model_version": "demo-rf-compatible-v1",
    }
