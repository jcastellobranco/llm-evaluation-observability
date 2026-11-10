# ATLAS local alerting (Grafana 11.6)

The local Grafana instance evaluates four provisioned **Grafana-managed** rules
every minute. They are visible in **Alerting → Alert rules** under the built-in
General folder with the `platform=atlas` label. No cloud account or
Alertmanager container is required.

| Rule | Trigger | Pending period | Severity |
| --- | --- | --- | --- |
| Worker queue backlog | More than **10** jobs in `queued` | **5 min** | warning |
| Worker terminal failure rate | More than **20%** `failed / (failed + completed)` over 10 min, with **at least 5** finished jobs | **3 min** | critical |
| RAG search p95 | Search p95 greater than **2 seconds** over 5 min, with **at least 10** searches | **5 min** | warning |
| RAG/worker unavailable | Prometheus `up == 0` for either target | **2 min** | critical |

The `retrying` outcome does **not** count as a terminal failure. The failure
ratio uses Prometheus counter increases, so a worker restart does not create
a false spike. The RAG alert measures **retrieval only**, not total end-to-end
generation latency. These are initial development thresholds, not SLOs.

Grafana uses `noDataState: OK` for the workload-dependent rules: idle
services do not produce false alerts. The target-down rule checks scrape
availability. Grafana query errors use `execErrState: Error` and are visible
as rule evaluation errors.

## Notifications: one-time local configuration

**Provisioning rules is not the same as configuring outbound delivery.**
Grafana evaluates and displays alerts automatically, but to receive a message
outside Grafana, you must configure a destination:

1. Open http://127.0.0.1:3000 and sign in.
2. Go to **Alerting → Contact points → Add contact point**. Choose email
   (requires working Grafana SMTP), Discord, Slack, or a private webhook.
   Store destination tokens in Grafana locally; never commit them to Git.
3. Use **Test** on the contact point to verify delivery.
4. In **Alerting → Notification policies**, route `platform=atlas` to the
   contact point. Optionally split `severity=critical` from `warning`.
5. Leave grouping and repeat intervals conservative to avoid notification
   storms (e.g., group by `alertname`, `component`; repeat every 4h).

Grafana's built-in default contact point may not deliver anything if SMTP
is not configured. Do **not** assume messages are being sent just because
rules are firing. The contact point and notification policy are intentionally
managed through the local Grafana UI and persisted in `atlas_grafana_data`.
They are not overwritten by these provisioned rules.

## Troubleshooting

- **Queue backlog:** check **ATLAS · RAG & Worker** and
  `{platform="atlas",service="worker"}` in Loki. Look for slow jobs,
  stuck external services and worker availability.
- **Failure rate:** inspect sanitized `worker_job_error` events in Loki,
  and check job state and retry settings without exposing prompt contents.
- **RAG p95:** inspect the RAG search p95 and embedding panels, pgvector
  database load, and `{platform="atlas",service="rag"}` logs.
- **Target unavailable:** check http://127.0.0.1:9090/targets and
  `make ps-observability` / `make logs-observability`.
- **No rules appear:** update both `llm-evaluation-observability` and
  `ai-inference-platform` on `main`, then run
  `make up-observability`. The Compose overlay must mount the sibling
  `observability/grafana/provisioning/alerting` directory.

Provisioned alert rules are **file-managed**; edit
`observability/grafana/provisioning/alerting/atlas-alerts.yml` in Git and
restart Grafana to change their thresholds. Changes in the UI to
file-provisioned rules are not persistent. Use Grafana's rule evaluation
history and preview to verify behavior; no live alert triggering is performed
by CI.
