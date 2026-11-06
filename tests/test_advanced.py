from llm_eval.advanced import summarize, check_gate
def test_regression_gate():
    result=summarize([{"exact_match":True,"token_f1":1.0,"latency_ms":100},{"exact_match":False,"token_f1":0.5,"latency_ms":200}])
    assert result["count"]==2
    passed, failures=check_gate(result)
    assert not passed and failures
