# Incident simulation

This document records two synthetic incidents run against the fraud detection pipeline to validate the monitoring and alerting stack.

---

## Incident 1: Fraud rate spike

**Simulated on**: 2026-03-25
**Script**: `scripts/simulate_incident.py --incident fraud_spike`

### What was simulated

50 transactions with feature values strongly associated with fraud were sent to the `/predict` endpoint. The script uses these exact ranges from `scripts/simulate_incident.py`: V1 and V3 in -5.0 to -3.0, V4 and V11 in +3.0 to +5.0, V10 in -5.0 to -3.0, V14 in -7.0 to -4.0, and Amount in 1.0 to 300.0. All 50 were classified as fraud (100% fraud rate), well above the 0.5% alert threshold.

### Features manipulated

The ULB credit card dataset's V-features are PCA components - their original meaning is anonymised, but their correlation with fraud is well-documented. V14, V1, and V3 are among the highest-importance fraud-separating components in this dataset family, so the simulation pushes them hardest:

| Feature | Direction | Reason |
|---------|-----------|--------|
| V14 | Strongly negative (−4 to −7) | Highest single-feature importance for fraud in the dataset |
| V1, V3 | Strongly negative (−3 to −5) | Strong negative correlation with fraud label |
| V4, V11 | Strongly positive (+3 to +5) | Strong positive correlation with fraud label |
| V10 | Strongly negative (−3 to −5) | Significant fraud predictor |

These values were chosen to emulate a high-risk region of feature space and push the XGBoost model past its normal decision boundary.

### What the monitoring stack detected

- `fraud_predictions_total{result="fraud"}` incremented to 50 in Prometheus within seconds of the simulation
- The Grafana "Fraud Rate Spike" alert rule evaluated `rate(fraud_predictions_total{result="fraud"}[5m]) / rate(prediction_requests_total[1m])` and entered Pending state (1-minute hold before firing)

### Alert

**Rule**: Fraud Rate Spike
**Threshold**: fraud rate > 0.5% over a 5-minute window
**Contact point**: fraud-pipeline-email → `<your-email>` (configured in `.env`)

### What a real on-call engineer would do

1. Check the current model version in the MLflow registry — confirm which version is deployed as `@champion`
2. Inspect the raw prediction logs in S3 (`prediction-logs/date=YYYY-MM-DD/`) to determine whether the spike is from a single source IP, merchant, or transaction pattern
3. If the spike is model-driven (not a real fraud wave), roll back the `@champion` alias to the previous registered version and redeploy via CI
4. If the spike is legitimate, escalate to the fraud operations team with the S3 logs as evidence

---

## Incident 2: Distribution shift

**Simulated on**: 2026-03-25
**Script**: `scripts/simulate_incident.py --incident distribution_shift`

### What was simulated

50 transactions were sent with `Amount` values 100x above normal (5,000-15,000 vs. a training baseline around 50) and V1-V5 shifted by +5.0 outside the training distribution. This mirrors a data pipeline error such as currency conversion mistakes or feature scaling regressions.

### What Evidently detected

`scripts/drift_check.py` read the day's 100 S3 prediction logs (50 fraud spike + 50 distribution shift) and ran an `DataDriftPreset` comparison against the 5,000-row training reference sample.

Result: **drift detected on 100% of input features**.

Metrics pushed to Pushgateway:
- `drift_dataset_drift_detected = 1`
- `drift_share_of_drifted_columns = 1.0`

### What the drift alert means operationally

The model is receiving inputs it was never trained on. In production this does not necessarily mean predictions are wrong today — XGBoost will still return a value — but confidence in those predictions is low and model performance metrics are no longer reliable. Silent degradation is the risk: the model may appear healthy by Prometheus metrics while accuracy has collapsed.

### Alert

**Rule**: Data Drift Warning
**Threshold**: share of drifted columns > 50%
**Contact point**: fraud-pipeline-email → `<your-email>` (configured in `.env`)

### Remediation steps

1. Identify the upstream change — compare the drifted feature distributions in S3 against historical logs to pinpoint when the shift began
2. If it is a pipeline bug (currency error, schema change), fix the upstream feed and backfill the affected prediction window
3. Re-run `scripts/generate_reference.py` and `scripts/drift_check.py` after the fix to confirm drift metrics return to zero
4. If the distribution shift reflects a genuine change in transaction behaviour (new market, new product), schedule a model retrain on recent data and register a new `@champion` in MLflow
