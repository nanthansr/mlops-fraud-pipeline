# differentiation report

## what this repository does that many similar repos do not
- It links model lifecycle and serving lifecycle end to end: model training and registration in MLflow, CI fetching the registry champion model, then container deployment flow.
- It includes both request-time and batch-time observability: Prometheus counters/histograms for live serving and Evidently drift checks pushed via Pushgateway.
- It has incident simulation scripts that exercise monitoring and alert rules instead of only showing static dashboards.
- It preserves prediction records as one object per request in S3 partitioned by date, enabling replay and drift analysis workflows.

## gaps a hiring manager could notice
- API lacks a compact machine-readable health summary endpoint for status pages or external monitors.
- Some external integrations were configured via hardcoded values instead of environment variables.
- External calls in a few scripts had limited failure handling, reducing operational robustness.
- Documentation needed clearer architecture narrative and decision tradeoff framing for interviews.

## chosen technical addition under 150 lines
- Addition: GET /metrics/summary endpoint in the FastAPI service.
- Why this differentiates: it exposes key model-health signals in one JSON payload for uptime robots, status pages, and simple runbooks.
- Scope: small and realistic - in-memory prediction counters plus last prediction timestamp, no behavior change to inference path.
- Estimated files touched: src/api/main.py and tests/test_api.py.
