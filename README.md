# JMeter Performance Testing Report
[![API Tests](https://github.com/Mohanad49/jmeter_performance_testing_report/actions/workflows/api-tests.yml/badge.svg)](https://github.com/Mohanad49/jmeter_performance_testing_report/actions/workflows/api-tests.yml)

This repo implements the third project from the resume: **JMeter Performance Testing Report | Apache JMeter, Streamlit, Python**.

The implementation is intentionally practical: JMeter targets a FastAPI `/predict` endpoint, while Streamlit acts as the UI. Testing the Streamlit page itself with JMeter would produce noisy UI/framework numbers and would not isolate prediction latency. For a credible QA portfolio, test the API directly and use Streamlit as the user-facing app.

## What is included

- FastAPI prediction service: `src/api.py`
- Streamlit UI: `src/streamlit_app.py`
- Deterministic demo predictor: `src/predictor.py`
- JMeter test plan: `jmeter/car_price_prediction_load_test.jmx`
- Payload dataset for virtual users: `jmeter/payloads.csv`
- JMeter execution scripts: `scripts/run_jmeter.sh` and `scripts/run_jmeter.bat`
- Python report generator: `scripts/generate_report.py`
- Sample JMeter results: `sample_results/jmeter_sample_results.csv`
- Generated sample report: `reports/performance_summary.md`
- API tests: `tests/test_api.py`

## Project architecture

```text
Streamlit UI  --->  FastAPI /predict endpoint  --->  Predictor function
                       ^
                       |
                    JMeter
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Run the API

```bash
python -m uvicorn src.api:app --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Prediction request:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"make":"Toyota","model":"Corolla","year":2020,"mileage":65000,"engine_size":1.6,"transmission":"automatic","fuel_type":"petrol"}'
```

## Run the Streamlit UI

In a second terminal, after starting the API:

```bash
streamlit run src/streamlit_app.py
```

## Run the JMeter test

Install Apache JMeter and make sure `jmeter` is available in your terminal path.

Linux/macOS:

```bash
THREADS=50 RAMP_UP=30 DURATION=120 ./scripts/run_jmeter.sh
```

Windows:

```bat
set THREADS=50
set RAMP_UP=30
set DURATION=120
scripts\\run_jmeter.bat
```

The test writes:

- raw JMeter results to `sample_results/jmeter_results.jtl`
- HTML dashboard to `reports/html-dashboard/`
- Markdown summary to `reports/performance_summary.md`

## Generate a report from an existing JMeter results file

```bash
python scripts/generate_report.py \
  --input sample_results/jmeter_sample_results.csv \
  --output reports/performance_summary.md \
  --scenario "Sample run: 50 users, 30s ramp-up, 120s duration"
```

## Suggested performance acceptance criteria

| Metric | Target |
| --- | ---: |
| Error rate | < 1% |
| P95 latency | < 500 ms |
| P99 latency | < 1000 ms |
| Sustained 5xx errors | 0 |

