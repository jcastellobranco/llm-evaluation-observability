# Reproducible LLM evaluation protocol

This project evaluates supplied predictions against references, reports exact match, token-level F1 and P95 latency, and applies configurable release gates. The deterministic report builder includes a SHA-256 digest of canonical input cases, allowing identical evaluation datasets to be compared across runs.

## Recommended experiment metadata

Record dataset revision, model name and version, prompt template revision, decoding parameters, inference provider, seed (when supported), hardware profile, and evaluation implementation commit SHA.

## Interpretation

Exact match and token F1 are lexical measures. They do not establish correctness, factuality, safety, bias or citation faithfulness. Small sample P95 values are unstable. Release gates are illustrative until thresholds are calibrated against real representative datasets.

## Planned extensions

- Groundedness and citation precision for RAG outputs
- Provider and prompt comparisons with confidence intervals
- Structured experiment history and downloadable JSON reports
- Traces, OpenTelemetry metrics and model-level cost accounting
