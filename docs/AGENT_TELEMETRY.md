# Agent runtime telemetry (development implementation)

Authenticated endpoints:
- `POST /v1/telemetry/agent` accepts strictly typed, redacted execution events with `x-api-key: $EVAL_API_KEY`.
- `GET /v1/telemetry/agent/summary` returns total runs, failures, guardrail blocks, cache hits, LLM/tool calls, input/output tokens, estimated USD cost and mean duration.

Only aggregated operational fields are accepted. Do **not** send prompts, retrieved evidence, tool arguments, API keys, user identifiers or raw tenant IDs. The `tenant_hash` is a pseudonym, not anonymization.

Storage is an in-process, bounded deque of up to 10,000 events. It resets on restart and does not aggregate across replicas. This is suitable for local demonstrations, **not** production monitoring, billing, audit retention or durable cost accounting. Token/cost fields are accepted only when supplied by a trusted caller; the service does not calculate provider prices.

The sibling multi-agent service sends a minimal event subset using `ATLAS_EVAL_TELEMETRY_URL` (HTTPS) and `ATLAS_EVAL_TELEMETRY_KEY`, both optional. Configure credentials in a secret manager. Deploy both matching branches before enabling integration.
