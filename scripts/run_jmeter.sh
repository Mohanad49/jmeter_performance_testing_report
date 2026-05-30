#!/usr/bin/env bash
set -euo pipefail

mkdir -p sample_results reports

JMETER_BIN="${JMETER_BIN:-jmeter}"
THREADS="${THREADS:-50}"
RAMP_UP="${RAMP_UP:-30}"
DURATION="${DURATION:-120}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

"$JMETER_BIN" -n \
  -t jmeter/car_price_prediction_load_test.jmx \
  -Jhost="$HOST" \
  -Jport="$PORT" \
  -Jthreads="$THREADS" \
  -Jramp_up="$RAMP_UP" \
  -Jduration="$DURATION" \
  -l sample_results/jmeter_results.jtl \
  -e -o reports/html-dashboard

python scripts/generate_report.py \
  --input sample_results/jmeter_results.jtl \
  --output reports/performance_summary.md \
  --scenario "${THREADS} users, ${RAMP_UP}s ramp-up, ${DURATION}s duration"
