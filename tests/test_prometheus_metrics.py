"""Prometheus contract: evaluation counters and private-data-safe labels."""
from fastapi.testclient import TestClient
from llm_eval.api import create_app


def test_metrics_are_scrapeable_and_reflect_evaluations():
    client = TestClient(create_app("test-secret"))
    payload = {"cases": [{"id": "private-case-123", "prediction": "Paris",
                          "reference": "Paris", "latency_ms": 100}]}
    assert client.post("/v1/evaluate", json=payload).status_code == 401
    ok = client.post("/v1/evaluate", headers={"x-api-key": "test-secret"}, json=payload)
    assert ok.status_code == 200 and ok.json()["passed"]
    metrics = client.get("/metrics/")
    assert metrics.status_code == 200
    assert 'atlas_evaluation_batches_total{kind="answer",outcome="passed"}' in metrics.text
    assert 'atlas_evaluation_cases_total{kind="answer"}' in metrics.text
    assert "private-case-123" not in metrics.text
    assert "test-secret" not in metrics.text


def test_agent_telemetry_metrics_use_only_bounded_status():
    client = TestClient(create_app("test-secret"))
    payload = {"run_id": "sensitive-run-xyz", "tenant_hash": "sensitive-hash-xyz",
               "workflow": "test", "status": "completed", "duration_ms": 10,
               "cache_hit": True, "guardrail_blocked": False}
    response = client.post("/v1/telemetry/agent", headers={"x-api-key": "test-secret"}, json=payload)
    assert response.status_code == 202
    metrics = client.get("/metrics/").text
    assert 'atlas_agent_events_total{status="completed"}' in metrics
    assert "atlas_agent_cache_hits_total" in metrics
    assert "sensitive-run-xyz" not in metrics
    assert "sensitive-hash-xyz" not in metrics
