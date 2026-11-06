from fastapi.testclient import TestClient
from llm_eval.api import create_app

def test_evaluation_gate():
    client = TestClient(create_app("secret"))
    payload = {"cases":[{"id":"one","prediction":"Paris","reference":"Paris","latency_ms":100}]}
    assert client.post("/v1/evaluate",json=payload).status_code==401
    response = client.post("/v1/evaluate",headers={"x-api-key":"secret"},json=payload)
    assert response.status_code==200
    assert response.json()["passed"] is True
    assert response.json()["metrics"]["exact_match"] == 1
    payload["cases"][0]["prediction"]="London"
    failed = client.post("/v1/evaluate",headers={"x-api-key":"secret"},json=payload)
    assert failed.json()["passed"] is False
