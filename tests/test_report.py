import pytest
from llm_eval.report import build_report
from llm_eval.advanced import Gate

def test_reproducible_report():
    cases=[{"id":"a","prediction":"Paris","reference":"Paris","latency_ms":100}]
    first=build_report(cases)
    assert first["passed"]
    assert first["dataset_sha256"] == build_report(cases)["dataset_sha256"]
    assert first["metrics"]["exact_match"] == 1

def test_gate_and_duplicates():
    cases=[{"id":"a","prediction":"London","reference":"Paris","latency_ms":5000}]
    report=build_report(cases,Gate(min_exact_match=1,max_p95_latency_ms=100))
    assert not report["passed"]
    assert len(report["failures"]) >= 2
    with pytest.raises(ValueError,match="Duplicate"):
        build_report(cases*2)
