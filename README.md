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

## ATLAS local observability (Grafana + Prometheus)

This repository **owns** the Prometheus scrape configuration, Grafana datasource
provisioning, and ATLAS overview dashboard under `observability/`. The sibling
`ai-inference-platform` repository owns the Docker Compose orchestration.

Clone/update both repositories as siblings, then in `ai-inference-platform`:

```bash
make init                 # generates a local Grafana admin password in untracked .env
make config-observability
make up-observability     # app + RAG + evaluation + agents + Redis + monitoring
make ps-observability
```

- Grafana: http://127.0.0.1:3000 (username `admin` unless `GRAFANA_ADMIN_USER` is set)
- Prometheus: http://127.0.0.1:9090/targets
- Dashboard: **ATLAS / ATLAS · Local observability** (automatically provisioned)
- To view the generated Grafana password locally, inspect
  `GRAFANA_ADMIN_PASSWORD` in the inference repository's untracked `.env`.
- Grafana/Prometheus are bound to localhost, not publicly exposed.
- `/metrics/` is scrapeable from the private Compose network without the
  evaluation API key; **do not publish the evaluation service or metrics port**.
- Prometheus keeps seven days of data in a persistent Docker volume. Neither
  `make down-observability` nor normal restarts delete volumes.

The dashboard includes API throughput/latency, evaluation batch outcomes and
agent telemetry *when events arrive*. Evaluation service metrics include only
bounded kind/outcome/status labels; no prompts, run IDs, tenant hashes, or
secrets. Agent telemetry delivery from the agent service is currently optional
and disabled in the default HTTP-only local setup, so its chart can be empty.
RAG and worker-specific Prometheus instrumentation are not yet included.

Grafana's admin password is applied when its database volume is first created;
changing `.env` alone does not reset an existing Grafana account. This is a
local development dashboard, not a production monitoring deployment.

## Boundaries

These are transparent lexical and ranking metrics, **not** a validated hallucination/factuality judge. Precision and recall require a curated relevance dataset. p95 from tiny batches is not statistically stable. Distributed tracing and production-grade cost monitoring remain future work; local Prometheus/Grafana dashboards are available. Not production-ready.
