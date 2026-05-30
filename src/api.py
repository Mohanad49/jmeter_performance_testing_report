from __future__ import annotations

from time import perf_counter

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.predictor import CarFeatures, predict_price

app = FastAPI(
    title="Car Price Prediction API",
    description="Small prediction endpoint designed for JMeter load and stress testing.",
    version="1.0.0",
)


class PredictionRequest(BaseModel):
    make: str = Field(..., examples=["Toyota"])
    model: str = Field(..., examples=["Corolla"])
    year: int = Field(..., ge=1980, le=2026, examples=[2020])
    mileage: int = Field(..., ge=0, le=1_000_000, examples=[65000])
    engine_size: float = Field(..., ge=0.6, le=8.0, examples=[1.6])
    transmission: str = Field(..., examples=["automatic"])
    fuel_type: str = Field(..., examples=["petrol"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict")
def predict(payload: PredictionRequest) -> dict[str, object]:
    started = perf_counter()
    features = CarFeatures(**payload.model_dump())
    prediction = predict_price(features)
    elapsed_ms = round((perf_counter() - started) * 1000, 3)
    return {
        "input": payload.model_dump(),
        "prediction": prediction,
        "processing_time_ms": elapsed_ms,
    }
