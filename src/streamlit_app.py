from __future__ import annotations

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="Car Price Predictor", page_icon="🚗")
st.title("Car Price Prediction Demo")
st.caption("Streamlit UI backed by a FastAPI prediction endpoint for JMeter performance testing.")

with st.form("prediction_form"):
    make = st.selectbox("Make", ["Toyota", "Honda", "BMW", "Mercedes", "Hyundai", "Kia", "Ford", "Chevrolet"])
    model = st.text_input("Model", value="Corolla")
    year = st.slider("Year", min_value=1980, max_value=2026, value=2020)
    mileage = st.number_input("Mileage", min_value=0, max_value=1_000_000, value=65000, step=5000)
    engine_size = st.number_input("Engine size", min_value=0.6, max_value=8.0, value=1.6, step=0.1)
    transmission = st.selectbox("Transmission", ["automatic", "manual"])
    fuel_type = st.selectbox("Fuel type", ["petrol", "diesel", "hybrid", "electric"])
    submitted = st.form_submit_button("Predict")

if submitted:
    payload = {
        "make": make,
        "model": model,
        "year": int(year),
        "mileage": int(mileage),
        "engine_size": float(engine_size),
        "transmission": transmission,
        "fuel_type": fuel_type,
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        prediction = data["prediction"]
        st.metric("Estimated Price", f"{prediction['estimated_price']:,.2f} {prediction['currency']}")
        st.write("Confidence band:", f"{prediction['lower_bound']:,.2f} - {prediction['upper_bound']:,.2f}")
        st.caption(f"API processing time: {data['processing_time_ms']} ms")
    except requests.RequestException as exc:
        st.error(f"Prediction API request failed: {exc}")
        st.info("Start the API first: python -m uvicorn src.api:app --reload")
