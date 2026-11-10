"""Citation integrity API regression tests."""
from fastapi.testclient import TestClient
from llm_eval.api import create_app


def test_citation_gate_accepts_allowed_required_ids():
    client = TestClient(create_app(api_key="test-secret"))
    response = client.post("/v1/evaluate/citations", headers={"x-api-key": "test-secret"}, json={
        "cases": [{"id": "case-1", "cited_ids": ["doc-1"], "allowed_ids": ["doc-1"], "required_ids": ["doc-1"]}]
    })
    assert response.status_code == 200
    assert response.json()["passed"] is True


def test_citation_gate_rejects_unsupported_and_missing_ids():
    client = TestClient(create_app(api_key="test-secret"))
    response = client.post("/v1/evaluate/citations", headers={"x-api-key": "test-secret"}, json={
        "cases": [{"id": "case-2", "cited_ids": ["foreign"], "allowed_ids": ["doc-1"], "required_ids": ["doc-1"]}]
    })
    assert response.status_code == 200
    assert response.json()["passed"] is False
    assert response.json()["cases"][0]["unsupported_ids"] == ["foreign"]
    assert response.json()["cases"][0]["missing_ids"] == ["doc-1"]


def test_citation_gate_requires_auth():
    client = TestClient(create_app(api_key="test-secret"))
    assert client.post("/v1/evaluate/citations", json={"cases": [{"id": "case-1"}]}).status_code == 401
