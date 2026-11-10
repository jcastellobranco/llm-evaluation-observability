"""Offline contracts for Grafana-managed ATLAS alert rules."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1] / "observability"
ALERTS = ROOT / "grafana/provisioning/alerting/atlas-alerts.yml"

EXPECTED = {
    "atlas-worker-queue-backlog": (10, "5m", "warning"),
    "atlas-worker-failure-rate": (0.20, "3m", "critical"),
    "atlas-rag-search-p95": (2, "5m", "warning"),
    "atlas-target-down": (0.5, "2m", "critical"),
}


def rules_by_uid():
    doc = yaml.safe_load(ALERTS.read_text())
    assert doc["apiVersion"] == 1
    assert len(doc["groups"]) == 1
    group = doc["groups"][0]
    assert group["orgId"] == 1
    assert group["folder"] == "general"
    assert group["interval"] == "1m"
    return {rule["uid"]: rule for rule in group["rules"]}


def test_all_rules_have_valid_query_and_threshold_contracts():
    rules = rules_by_uid()
    assert set(rules) == set(EXPECTED)
    for uid, (threshold, pending, severity) in EXPECTED.items():
        rule = rules[uid]
        assert rule["condition"] == "B"
        assert rule["for"] == pending
        assert rule["noDataState"] == "OK"
        assert rule["execErrState"] == "Error"
        assert rule["isPaused"] is False
        assert rule["labels"]["platform"] == "atlas"
        assert rule["labels"]["severity"] == severity
        assert rule["annotations"]["runbook_url"].endswith("docs/ATLAS_ALERTS.md")
        query, comparator = rule["data"]
        assert query["refId"] == "A"
        assert query["datasourceUid"] == "atlas-prometheus"
        assert query["model"]["instant"] is True
        assert query["model"]["range"] is False
        assert comparator["refId"] == "B"
        assert comparator["datasourceUid"] == "__expr__"
        assert comparator["model"]["type"] == "threshold"
        assert comparator["model"]["expression"] == "A"
        evaluator = comparator["model"]["conditions"][0]["evaluator"]
        assert evaluator["type"] == "gt"
        assert evaluator["params"] == [threshold]


def test_failure_rate_excludes_retries_and_requires_sample_size():
    expr = rules_by_uid()["atlas-worker-failure-rate"]["data"][0]["model"]["expr"]
    assert 'outcome="failed"' in expr
    assert 'outcome=~"failed|completed"' in expr
    assert ">= 5" in expr
    assert "retrying" not in expr
    assert "[10m]" in expr


def test_rag_p95_requires_minimum_search_volume():
    expr = rules_by_uid()["atlas-rag-search-p95"]["data"][0]["model"]["expr"]
    assert "histogram_quantile(0.95" in expr
    assert "atlas_rag_search_duration_seconds_bucket[5m]" in expr
    assert "atlas_rag_search_duration_seconds_count[5m]" in expr
    assert ">= 10" in expr


def test_queue_and_availability_use_fixed_metric_labels():
    rules = rules_by_uid()
    assert rules["atlas-worker-queue-backlog"]["data"][0]["model"]["expr"] == (
        'sum(atlas_worker_queue_jobs{status="queued"}) or vector(0)'
    )
    assert rules["atlas-target-down"]["data"][0]["model"]["expr"] == (
        '1 - up{job=~"atlas-rag|atlas-worker"}'
    )
    for rule in rules.values():
        query = rule["data"][0]["model"]["expr"]
        for forbidden in ("tenant_id", "document_id", "prompt", "api_key"):
            assert forbidden not in query
