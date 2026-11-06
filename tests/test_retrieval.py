import pytest
from llm_eval.retrieval import evaluate_retrieval

def test_recall_mrr_precision():
    data=[
        {"retrieved_ids":["bad","relevant-a","relevant-b"],
         "relevant_ids":["relevant-a","relevant-b"]},
        {"retrieved_ids":["irrelevant","miss"],"relevant_ids":["target"]},
    ]
    report=evaluate_retrieval(data,k=2)
    assert report["queries"]==2
    assert report["recall_at_k"]==0.25
    assert report["mrr_at_k"]==0.25
    assert report["precision_at_k"]==0.25

def test_invalid_benchmarks():
    with pytest.raises(ValueError):
        evaluate_retrieval([])
    with pytest.raises(ValueError):
        evaluate_retrieval([{"retrieved_ids":[],"relevant_ids":[]}])
    with pytest.raises(ValueError,match="Duplicate"):
        evaluate_retrieval([{"retrieved_ids":["a","a"],"relevant_ids":["a"]}])

def test_missing_relevant_returns_zero():
    results=evaluate_retrieval([{"retrieved_ids":["a"],"relevant_ids":["b"]}],k=5)
    assert results["mrr_at_k"]==0
    assert results["recall_at_k"]==0
