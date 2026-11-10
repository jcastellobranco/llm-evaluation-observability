from fastapi.testclient import TestClient
from llm_eval.api import create_app

def test_retrieval_gate_pass():
    client = TestClient(create_app(api_key="secret"))
    r = client.post("/v1/evaluate/retrieval", headers={"x-api-key":"secret"}, json={"cases":[{"retrieved_ids":["a","b"],"relevant_ids":["a"]}],"k":2,"min_recall_at_k":1,"min_mrr_at_k":1,"min_precision_at_k":0.5})
    assert r.status_code == 200
    assert r.json()["passed"] is True

def test_retrieval_gate_fail():
    client = TestClient(create_app(api_key="secret"))
    r = client.post("/v1/evaluate/retrieval", headers={"x-api-key":"secret"}, json={"cases":[{"retrieved_ids":["wrong","a"],"relevant_ids":["a"]}],"k":2,"min_mrr_at_k":0.75})
    assert r.status_code == 200
    assert r.json()["passed"] is False

def test_retrieval_gate_auth():
    client = TestClient(create_app(api_key="secret"))
    assert client.post("/v1/evaluate/retrieval",json={"cases":[{"retrieved_ids":["a"],"relevant_ids":["a"]}]}).status_code == 401
