from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _load_jmeter_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"JMeter results file not found: {path}")

    df = pd.read_csv(path)
    required = {"timeStamp", "elapsed", "label", "responseCode", "success"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required JMeter columns: {', '.join(sorted(missing))}")

    df["timeStamp"] = pd.to_numeric(df["timeStamp"], errors="coerce")
    df["elapsed"] = pd.to_numeric(df["elapsed"], errors="coerce")
    df = df.dropna(subset=["timeStamp", "elapsed"])
    df["success"] = df["success"].astype(str).str.lower().isin(["true", "1", "yes"])
    return df


def _percentile(series: pd.Series, percentile: float) -> float:
    return round(float(series.quantile(percentile / 100)), 2)


def analyze(df: pd.DataFrame) -> dict[str, object]:
    total = len(df)
    failed = int((~df["success"]).sum())
    start_ms = int(df["timeStamp"].min())
    end_ms = int(df["timeStamp"].max())
    duration_seconds = max((end_ms - start_ms) / 1000, 1)
    throughput = total / duration_seconds

    response_codes = (
        df["responseCode"].astype(str).value_counts().sort_index().to_dict()
    )

    return {
        "total_requests": total,
        "failed_requests": failed,
        "error_rate_percent": round((failed / total * 100) if total else 0, 2),
        "duration_seconds": round(duration_seconds, 2),
        "throughput_rps": round(throughput, 2),
        "min_ms": round(float(df["elapsed"].min()), 2),
        "avg_ms": round(float(df["elapsed"].mean()), 2),
        "p50_ms": _percentile(df["elapsed"], 50),
        "p90_ms": _percentile(df["elapsed"], 90),
        "p95_ms": _percentile(df["elapsed"], 95),
        "p99_ms": _percentile(df["elapsed"], 99),
        "max_ms": round(float(df["elapsed"].max()), 2),
        "response_codes": response_codes,
    }


def _bottleneck_notes(metrics: dict[str, object]) -> list[str]:
    notes: list[str] = []
    error_rate = float(metrics["error_rate_percent"])
    p95 = float(metrics["p95_ms"])
    p99 = float(metrics["p99_ms"])
    avg = float(metrics["avg_ms"])
    max_ms = float(metrics["max_ms"])

    if error_rate > 1:
        notes.append(
            f"Error rate is {error_rate}%, which is too high for a prediction endpoint. Inspect non-200 response codes and server logs first."
        )
    else:
        notes.append(
            f"Error rate is {error_rate}%, which is acceptable for this demo scenario."
        )

    if p95 > 500:
        notes.append(
            f"P95 latency is {p95} ms. That is a bottleneck signal; profile model inference, request parsing, and worker count."
        )
    elif p95 > 250:
        notes.append(
            f"P95 latency is {p95} ms. This is usable, but it may degrade under a higher ramp-up or larger model artifact."
        )
    else:
        notes.append(f"P95 latency is {p95} ms, which is healthy for this lightweight API.")

    if p99 > avg * 3:
        notes.append(
            f"P99 latency is {p99} ms versus average {avg} ms, so tail latency exists even if the average looks fine."
        )

    if max_ms > p99 * 1.5:
        notes.append(
            f"Max latency reached {max_ms} ms, which suggests occasional spikes. Re-test with CPU and memory monitoring enabled."
        )

    return notes


def render_markdown(metrics: dict[str, object], scenario: str) -> str:
    response_codes = metrics["response_codes"]
    codes_md = "\n".join(f"| {code} | {count} |" for code, count in response_codes.items())
    notes_md = "\n".join(f"- {note}" for note in _bottleneck_notes(metrics))

    return f"""# JMeter Performance Testing Report

## Scenario

{scenario}

## Executive Summary

The `/predict` endpoint was tested using concurrent virtual users with JSON payloads representing different car records. The objective was to measure throughput, latency percentiles, and stability under sustained load.

## Key Metrics

| Metric | Value |
| --- | ---: |
| Total requests | {metrics['total_requests']} |
| Failed requests | {metrics['failed_requests']} |
| Error rate | {metrics['error_rate_percent']}% |
| Test duration | {metrics['duration_seconds']} s |
| Throughput | {metrics['throughput_rps']} req/s |
| Min latency | {metrics['min_ms']} ms |
| Average latency | {metrics['avg_ms']} ms |
| P50 latency | {metrics['p50_ms']} ms |
| P90 latency | {metrics['p90_ms']} ms |
| P95 latency | {metrics['p95_ms']} ms |
| P99 latency | {metrics['p99_ms']} ms |
| Max latency | {metrics['max_ms']} ms |

## Response Codes

| Code | Count |
| --- | ---: |
{codes_md}

## Bottleneck Findings

{notes_md}

## Recommendations

1. Keep testing the API endpoint directly instead of the Streamlit UI; UI testing gives noisy numbers and hides backend bottlenecks.
2. Re-run the same test with 50, 100, and 200 users to identify the saturation point.
3. Add server-side monitoring for CPU, memory, worker count, and inference time so the report explains why latency changes.
4. For a real ML artifact, load the model once at startup. Do not reload it per request.
5. Define an acceptance threshold before testing, for example: error rate below 1%, P95 latency below 500 ms, and no sustained 5xx responses.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Markdown report from JMeter JTL CSV results.")
    parser.add_argument("--input", required=True, help="Path to JMeter JTL/CSV results file.")
    parser.add_argument("--output", required=True, help="Path to write the Markdown report.")
    parser.add_argument("--scenario", default="50 users, 30s ramp-up, 120s duration")
    args = parser.parse_args()

    df = _load_jmeter_csv(Path(args.input))
    metrics = analyze(df)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown(metrics, args.scenario), encoding="utf-8")
    print(f"Report written to {output}")


if __name__ == "__main__":
    main()
