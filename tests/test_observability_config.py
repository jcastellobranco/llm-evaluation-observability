"""Offline contract checks for the local ATLAS observability assets."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "observability"


def test_grafana_dashboard_and_datasource_provisioning():
    dashboard = json.loads((ROOT / "grafana/provisioning/dashboards/json/atlas-overview.json").read_text())
    assert dashboard["uid"] == "atlas-local-overview"
    assert len(dashboard["panels"]) >= 6
    assert all(panel["datasource"]["uid"] == "atlas-prometheus" for panel in dashboard["panels"])
    datasource = (ROOT / "grafana/provisioning/datasources/prometheus.yml").read_text()
    assert "uid: atlas-prometheus" in datasource
    assert "http://prometheus:9090" in datasource
    provider = (ROOT / "grafana/provisioning/dashboards/provider.yml").read_text()
    assert "/etc/grafana/provisioning/dashboards/json" in provider


def test_prometheus_scrapes_only_private_service_metrics():
    config = (ROOT / "prometheus.yml").read_text()
    assert "backend:8000" in config
    assert "evaluation:8000" in config
    assert "rag:8000" in config
    assert "worker:9101" in config
    assert "metrics_path: /metrics/" in config
    assert "localhost" not in config


def test_rag_worker_and_log_dashboards_are_provisioned():
    dashboard_dir = ROOT / "grafana/provisioning/dashboards/json"
    rag_worker = json.loads((dashboard_dir / "atlas-rag-worker.json").read_text())
    assert rag_worker["uid"] == "atlas-rag-worker"
    assert len(rag_worker["panels"]) >= 10
    assert all(p["datasource"]["uid"] == "atlas-prometheus" for p in rag_worker["panels"])
    logs = json.loads((dashboard_dir / "atlas-container-logs.json").read_text())
    assert logs["uid"] == "atlas-container-logs"
    assert any(p["type"] == "logs" for p in logs["panels"])
    assert all(p["datasource"]["uid"] == "atlas-loki" for p in logs["panels"])
    assert "service" in logs["templating"]["list"][0]["name"]


def test_loki_alloy_configs_are_private_and_bounded():
    loki = (ROOT / "loki.yml").read_text()
    alloy = (ROOT / "alloy.alloy").read_text()
    datasource = (ROOT / "grafana/provisioning/datasources/loki.yml").read_text()
    assert "retention_period: 168h" in loki
    assert "http://loki:3100" in datasource
    assert "uid: atlas-loki" in datasource
    assert 'host = "tcp://docker-proxy:2375"' in alloy
    assert 'target_label = "service"' in alloy
    assert 'action = "keep"' in alloy
    assert "/var/run/docker.sock" not in alloy
