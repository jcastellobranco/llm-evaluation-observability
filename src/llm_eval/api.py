"""Evaluation service with authenticated requests and deterministic baseline metrics."""
import hmac
import os
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from .core import token_f1
from .retrieval import evaluate_retrieval
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

class CitationCase(BaseModel):
    id: str = Field(min_length=1, max_length=128)
    cited_ids: list[str] = Field(default_factory=list, max_length=100)
    allowed_ids: list[str] = Field(default_factory=list, max_length=100)
    required_ids: list[str] = Field(default_factory=list, max_length=100)

class CitationRequest(BaseModel):
    cases: list[CitationCase] = Field(min_length=1, max_length=1000)

class RetrievalCase(BaseModel):
    retrieved_ids: list[str] = Field(max_length=100)
    relevant_ids: list[str] = Field(min_length=1, max_length=100)

class RetrievalRequest(BaseModel):
    cases: list[RetrievalCase] = Field(min_length=1, max_length=1000)
    k: int = Field(default=5, ge=1, le=100)

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
    @app.post("/v1/evaluate/citations")
    def evaluate_citations(body: CitationRequest, _: None = Depends(authorize)):
        """Deterministic citation allowlist/coverage gate; not a factuality judge."""
        results = []
        for case in body.cases:
            cited = set(case.cited_ids)
            allowed = set(case.allowed_ids)
            required = set(case.required_ids)
            unsupported = sorted(cited - allowed)
            missing = sorted(required - cited)
            results.append({"id": case.id, "passed": not unsupported and not missing,
                            "unsupported_ids": unsupported, "missing_ids": missing})
        return {"passed": all(item["passed"] for item in results), "cases": results}

    @app.post("/v1/evaluate/retrieval")
    def evaluate_ranked_retrieval(body: RetrievalRequest, _: None = Depends(authorize)):
        try:
            return evaluate_retrieval([case.model_dump() for case in body.cases], k=body.k)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
    return app
