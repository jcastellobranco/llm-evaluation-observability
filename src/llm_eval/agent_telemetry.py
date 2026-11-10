"""Bounded, in-process agent telemetry aggregates; no raw prompts or tool arguments.

For single-instance development only; production requires durable event storage.
"""
from collections import deque
from statistics import mean
from threading import Lock

_EVENTS = deque(maxlen=10000)
_LOCK = Lock()

def record(event: dict) -> None:
    # Strict allowlist: no prompt, response, secret, document or tool arguments.
    allowed = {"run_id", "tenant_hash", "workflow", "status", "duration_ms",
               "llm_calls", "tool_calls", "input_tokens", "output_tokens",
               "cache_hit", "guardrail_blocked", "estimated_cost_usd"}
    if set(event) - allowed:
        raise ValueError("Unsupported telemetry fields")
    if len(str(event)) > 2048:
        raise ValueError("Telemetry event too large")
    with _LOCK:
        _EVENTS.append(dict(event))

def aggregate() -> dict:
    with _LOCK:
        events = list(_EVENTS)
    return {
        "runs": len(events),
        "failed_runs": sum(e.get("status") == "failed" for e in events),
        "guardrail_blocks": sum(bool(e.get("guardrail_blocked")) for e in events),
        "cache_hits": sum(bool(e.get("cache_hit")) for e in events),
        "llm_calls": sum(int(e.get("llm_calls", 0)) for e in events),
        "tool_calls": sum(int(e.get("tool_calls", 0)) for e in events),
        "input_tokens": sum(int(e.get("input_tokens", 0)) for e in events),
        "output_tokens": sum(int(e.get("output_tokens", 0)) for e in events),
        "estimated_cost_usd": round(sum(float(e.get("estimated_cost_usd", 0)) for e in events), 6),
        "mean_duration_ms": round(mean(float(e.get("duration_ms", 0)) for e in events), 2) if events else 0,
        "storage": "process-memory",
    }
