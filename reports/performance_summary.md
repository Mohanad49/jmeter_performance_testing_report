# JMeter Performance Testing Report

## Scenario

Sample run: 50 users, 30s ramp-up, 120s duration

## Executive Summary

The `/predict` endpoint was tested using concurrent virtual users with JSON payloads representing different car records. The objective was to measure throughput, latency percentiles, and stability under sustained load.

## Key Metrics

| Metric | Value |
| --- | ---: |
| Total requests | 2920 |
| Failed requests | 14 |
| Error rate | 0.48% |
| Test duration | 120.02 s |
| Throughput | 24.33 req/s |
| Min latency | 8.0 ms |
| Average latency | 75.31 ms |
| P50 latency | 64.0 ms |
| P90 latency | 92.0 ms |
| P95 latency | 119.3 ms |
| P99 latency | 354.0 ms |
| Max latency | 793.0 ms |

## Response Codes

| Code | Count |
| --- | ---: |
| 200 | 2906 |
| 500 | 5 |
| 503 | 9 |

## Bottleneck Findings

- Error rate is 0.48%, which is acceptable for this demo scenario.
- P95 latency is 119.3 ms, which is healthy for this lightweight API.
- P99 latency is 354.0 ms versus average 75.31 ms, so tail latency exists even if the average looks fine.
- Max latency reached 793.0 ms, which suggests occasional spikes. Re-test with CPU and memory monitoring enabled.

## Recommendations

1. Keep testing the API endpoint directly instead of the Streamlit UI; UI testing gives noisy numbers and hides backend bottlenecks.
2. Re-run the same test with 50, 100, and 200 users to identify the saturation point.
3. Add server-side monitoring for CPU, memory, worker count, and inference time so the report explains why latency changes.
4. For a real ML artifact, load the model once at startup. Do not reload it per request.
5. Define an acceptance threshold before testing, for example: error rate below 1%, P95 latency below 500 ms, and no sustained 5xx responses.
