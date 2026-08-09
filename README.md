# Load Testing a Prediction API with JMeter

[![API Tests](https://github.com/Mohanad49/jmeter_performance_testing_report/actions/workflows/api-tests.yml/badge.svg)](https://github.com/Mohanad49/jmeter_performance_testing_report/actions/workflows/api-tests.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A performance engagement against a car-price prediction service: an Apache JMeter test
plan driving a FastAPI `/predict` endpoint under concurrent load, plus a report generator
that turns the raw `.jtl` output into latency percentiles, error rates and findings.

**[Read the sample report →](reports/performance_summary.md)**

## Two decisions worth stating up front

**JMeter points at the API, not at the Streamlit page.** Streamlit is here as the
user-facing app, and it would have been the more impressive-looking thing to load-test.
It would also have produced numbers about Streamlit's websocket session handling rather
than about prediction latency, and a percentile that mixes framework overhead with the
thing under test cannot be acted on. Test the layer whose latency you intend to change.

**The predictor is deliberately trivial.** `src/predictor.py` is a deterministic pricing
function, not a trained model. A real model would make every latency figure a statement
about inference cost on whatever machine ran it, and would drown the signal this project
exists to produce: how the *service* behaves under concurrency. The tradeoff is stated
rather than hidden — these numbers describe a fast endpoint under load, and the report
says so.

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

## Acceptance criteria, and what the sample run did against them

Thresholds are written down before the run, not after. A criterion chosen once the
numbers are in is not a criterion, it is a description.

| Metric | Target | Sample run (50 users, 120 s) | |
| --- | ---: | ---: | --- |
| Error rate | < 1% | 0.48% (14 / 2,920) | pass |
| P95 latency | < 500 ms | 119.3 ms | pass |
| P99 latency | < 1000 ms | 354.0 ms | pass |
| Sustained 5xx | 0 | 14 total — 5×500, 9×503 | **investigate** |

The last row is the interesting one, and it is why an average is not a result. Mean
latency was 75 ms and P95 was comfortable, but P99 sat at 354 ms and the maximum touched
793 ms — so roughly one request in a hundred took five times the average, and fourteen
did not complete at all. A dashboard showing the mean would have called this clean.

The 5xx responses are not "acceptable at this volume" until someone has looked at them.
`reports/performance_summary.md` records that as an open finding rather than rounding it
off, along with what the next run needs to answer it: server-side CPU and memory
monitoring, and the same plan re-run at 50 / 100 / 200 users to find where the service
actually saturates.

