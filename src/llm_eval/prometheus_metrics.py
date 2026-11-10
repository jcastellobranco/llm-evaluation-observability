"""Low-cardinality Prometheus metrics for local ATLAS evaluation/telemetry.

Never export case IDs, run IDs, tenant identifiers, prompts or text.
"""
from prometheus_client import Counter, Histogram, make_asgi_app

metrics_app = make_asgi_app()

EVALUATION_BATCHES = Counter(
    "atlas_evaluation_batches_total", "Evaluation requests by type and result",
    ["kind", "outcome"],
)
EVALUATION_CASES = Counter(
    "atlas_evaluation_cases_total", "Evaluation cases processed by type",
    ["kind"],
)
EVALUATION_DURATION = Histogram(
    "atlas_evaluation_request_duration_seconds", "Evaluation request duration",
    ["kind"],
)
AGENT_EVENTS = Counter(
    "atlas_agent_events_total", "Accepted agent telemetry events by outcome",
    ["status"],
)
AGENT_CACHE_HITS = Counter(
    "atlas_agent_cache_hits_total", "Agent telemetry events reporting a cache hit",
)
AGENT_GUARDRAIL_BLOCKS = Counter(
    "atlas_agent_guardrail_blocks_total", "Agent telemetry events reporting a guardrail block",
)


def record_evaluation(kind: str, passed: bool, cases: int, seconds: float) -> None:
    # kind is selected by the server, never supplied by a caller.
    EVALUATION_BATCHES.labels(kind=kind, outcome="passed" if passed else "failed").inc()
    EVALUATION_CASES.labels(kind=kind).inc(cases)
    EVALUATION_DURATION.labels(kind=kind).observe(seconds)


def record_agent(status: str, *, cache_hit: bool, guardrail_blocked: bool) -> None:
    # AgentEvent validates status against a finite enum before this call.
    AGENT_EVENTS.labels(status=status).inc()
    if cache_hit:
        AGENT_CACHE_HITS.inc()
    if guardrail_blocked:
        AGENT_GUARDRAIL_BLOCKS.inc()
