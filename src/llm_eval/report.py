"""Deterministic evaluation reports for regression review."""
import hashlib
import json
from datetime import datetime, timezone
from .advanced import Gate, summarize, check_gate
from .core import token_f1

def build_report(cases: list[dict], gate: Gate = Gate()) -> dict:
    if not cases:
        raise ValueError("At least one evaluation case is required")
    ids = [str(case["id"]) for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate case IDs are not allowed")
    events=[]
    for case in cases:
        pred, ref = str(case["prediction"]), str(case["reference"])
        latency = float(case["latency_ms"])
        if not 0 <= latency <= 3600000:
            raise ValueError("Invalid latency")
        events.append({"exact_match": pred.strip().casefold()==ref.strip().casefold(),
                       "token_f1":token_f1(pred,ref), "latency_ms":latency})
    metrics=summarize(events)
    passed, failures=check_gate(metrics,gate)
    canonical=json.dumps(cases,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return {"schema_version":1,"dataset_sha256":hashlib.sha256(canonical.encode()).hexdigest(),
            "passed":passed,"failures":failures,"metrics":metrics,
            "cases":[{"id":case["id"],**event} for case,event in zip(cases,events)]}
