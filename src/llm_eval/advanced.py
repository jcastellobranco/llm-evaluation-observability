"""Reproducible regression gates and JSONL event aggregation."""
from dataclasses import dataclass
from statistics import mean
from typing import Iterable

@dataclass(frozen=True)
class Gate:
    min_exact_match: float = 0.8
    min_token_f1: float = 0.75
    max_p95_latency_ms: float = 2000

def percentile(values: list[float], p: float) -> float:
    if not values or not 0 <= p <= 100:
        raise ValueError("Expected nonempty values and percentile 0..100")
    ordered = sorted(values)
    index = (len(ordered)-1) * p/100
    low = int(index)
    high = min(low+1, len(ordered)-1)
    return ordered[low] + (ordered[high]-ordered[low]) * (index-low)

def summarize(events: Iterable[dict]) -> dict:
    rows = list(events)
    if not rows:
        raise ValueError("No evaluation events")
    return {
        "count": len(rows),
        "exact_match": mean(float(x["exact_match"]) for x in rows),
        "token_f1": mean(float(x["token_f1"]) for x in rows),
        "p95_latency_ms": percentile([float(x["latency_ms"]) for x in rows], 95),
    }

def check_gate(summary: dict, gate: Gate = Gate()) -> tuple[bool, list[str]]:
    failures = []
    for field, minimum in [("exact_match", gate.min_exact_match), ("token_f1", gate.min_token_f1)]:
        if summary[field] < minimum:
            failures.append(f"{field} below {minimum}")
    if summary["p95_latency_ms"] > gate.max_p95_latency_ms:
        failures.append("p95 latency above threshold")
    return not failures, failures
