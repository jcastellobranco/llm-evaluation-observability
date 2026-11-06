"""Evaluation service with authenticated requests and deterministic baseline metrics."""
import hmac
import os
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from .core import token_f1
from .advanced import Gate, summarize, check_gate

class Case(BaseModel):
    id: str = Field(min_length=1, max_length=128)
    prediction: str = Field(max_length=16000)
    reference: str = Field(max_length=16000)
    latency_ms: float = Field(ge=0, le=3600000)

class EvaluateRequest(BaseModel):
    cases: list[Case] = Field(min_length=1, max_length=1000)
    min_exact_match: float = Field(default=0.8, ge=0, le=1)
    min_token_f1: float = Field(default=0.75, ge=0, le=1)
    max_p95_latency_ms: float = Field(default=2000, gt=0)

def create_app(api_key: str | None = None) -> FastAPI:
    secret = api_key if api_key is not None else os.getenv("EVAL_API_KEY", "")
    if not secret:
        raise RuntimeError("EVAL_API_KEY is required")
    app = FastAPI(title="LLM Evaluation Platform", version="0.3.0")
    def authorize(x_api_key: str | None = Header(default=None)):
        if not x_api_key or not hmac.compare_digest(x_api_key, secret):
            raise HTTPException(401, "Invalid API key")
    @app.get("/health")
    def health():
        return {"status":"ok"}
    @app.post("/v1/evaluate")
    def evaluate(body: EvaluateRequest, _: None = Depends(authorize)):
        events = [{
            "exact_match": case.prediction.strip().casefold() == case.reference.strip().casefold(),
            "token_f1": token_f1(case.prediction, case.reference),
            "latency_ms": case.latency_ms,
        } for case in body.cases]
        metrics = summarize(events)
        passed, failures = check_gate(metrics, Gate(body.min_exact_match, body.min_token_f1, body.max_p95_latency_ms))
        return {"passed": passed, "failures": failures, "metrics": metrics, "cases": [{"id": c.id, **event} for c,event in zip(body.cases,events)]}
    return app
