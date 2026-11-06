# LLM Evaluation & Observability

Reproducible evaluation baselines for generated answers and document retrieval.

## What works

- Authenticated FastAPI `POST /v1/evaluate` computes exact match, token F1, p95 latency, and configurable pass/fail release gates.
- Authenticated `POST /v1/evaluate/retrieval` computes Recall@K, MRR@K and Precision@K from labeled relevant/retrieved IDs.
- Standalone deterministic reports with stable SHA-256 input dataset identifiers.
- JSONL event support in the core library, Dockerfile, unit tests, GitHub Actions.

## Run

```bash
pip install -e '.[dev]'
export EVAL_API_KEY=replace-with-local-secret
uvicorn llm_eval.api:create_app --factory --port 8000
pytest -q
```

See [Evaluation protocol](docs/EVALUATION_PROTOCOL.md). The sibling inference platform can call this API when an RAG job includes a reference answer.

## Boundaries

These are transparent lexical and ranking metrics, **not** a validated hallucination/factuality judge. Precision and recall require a curated relevance dataset. p95 from tiny batches is not statistically stable. Model tracing, cost monitoring and online observability dashboards are future work. Not production-ready.
