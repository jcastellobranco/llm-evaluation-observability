from fastapi.testclient import TestClient
from llm_eval.api import create_app

def test_retrieval_endpoint_requires_api_key():
    client=TestClient(create_app("secret"))
    payload={"cases":[{"retrieved_ids":["x","target"],
                       "relevant_ids":["target"]}],"k":2}
    assert client.post("/v1/evaluate/retrieval",json=payload).status_code==401
    result=client.post("/v1/evaluate/retrieval",headers={"x-api-key":"secret"},json=payload)
    assert result.status_code==200, result.text
    assert result.json()["recall_at_k"]==1
    assert result.json()["mrr_at_k"]==0.5

def test_duplicate_retrieval_ids_rejected():
    client=TestClient(create_app("secret"))
    result=client.post("/v1/evaluate/retrieval",headers={"x-api-key":"secret"},
        json={"cases":[{"retrieved_ids":["x","x"],"relevant_ids":["x"]}]})
    assert result.status_code==422
