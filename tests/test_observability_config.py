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
    assert "metrics_path: /metrics/" in config
    assert "localhost" not in config
