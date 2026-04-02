# MLOps Fraud Detection Pipeline

![CI](https://github.com/nanthansr/mlops-fraud-pipeline/actions/workflows/ci-cd.yml/badge.svg)

This repository implements a full fraud detection MLOps system around the ULB credit card dataset, from model training and MLflow registry promotion to FastAPI inference, Prometheus and Grafana observability, drift checks with Evidently, and incident-driven alerting; the focus is production behavior under monitoring and deployment constraints, not just model score reporting.

## Architecture

[View interactive architecture diagram](https://nanthansr.github.io/mlops-fraud-pipeline/architecture.html)

```
[Kaggle Dataset] → [Feature Engineering] → [XGBoost Model]
                                                  ↓
                                          [MLflow Registry]
                                                  ↓
                                [FastAPI Prediction Service]
                                          ↓           ↓
                              [GitHub Actions]    [Prometheus]
                                    ↓                 ↓
                             [AWS ECR/ECS]      [Grafana Dashboard]
                                                       ↓
                                           [AIOps Anomaly Detector]
                                                       ↓
                                              [Slack/Email Alert]
```

- Kaggle dataset: fixed public benchmark with extreme class imbalance (0.17% fraud) keeps evaluation and threshold logic grounded in a reproducible baseline.
- Feature engineering: Time is dropped and Amount is scaled to match PCA feature ranges so serving-time distributions stay aligned with training assumptions.
- XGBoost model: class weighting via scale_pos_weight handles 577:1 imbalance without synthetic oversampling drift.
- MLflow registry: CI fetches a named champion model version instead of retraining blindly during every deploy.
- FastAPI service: low-latency online inference exposes both prediction APIs and machine metrics from one deployable unit.
- GitHub Actions: test-first pipeline blocks image push when API behavior regresses.
- AWS ECR and ECS: immutable image builds and managed runtime make rollback and redeploy deterministic.
- Prometheus and Grafana: request, fraud-rate, confidence, and drift metrics are observable in one dashboard.
- AIOps anomaly layer: batch drift checks complement request metrics to catch silent input-distribution failures.
- Alert channel: SMTP route from Grafana turns threshold breaches into on-call signals.

## Stack

| Layer | Technology | Why not X |
|-------|------------|-----------|
| Model | XGBoost with scale_pos_weight | Logistic regression was rejected because non-linear feature interaction is important in anonymized PCA space and recall collapses under extreme imbalance. |
| API | FastAPI + Uvicorn | Flask was rejected because strict request typing and automatic OpenAPI schema were required for predictable MLOps handoff. |
| Drift detection | Evidently DataDriftPreset | Custom drift logic was rejected to avoid under-tested statistical code and inconsistent thresholds across features. |
| Experiment tracking | MLflow 3.x registry + aliases | Local-only artifact files were rejected because promotion and rollback need explicit version metadata. |
| Monitoring | Prometheus + Grafana + Pushgateway | CloudWatch-only monitoring was rejected for this stack because request, model, and batch drift metrics needed one query language and one dashboard surface. |
| Deployment | Docker Compose local, AWS ECS/Fargate target | EC2-backed ECS was rejected to avoid instance patching and scaling overhead for a service-oriented inference workload. |
| Language | Python 3.11 | Older Python releases were rejected due to dependency compatibility for modern FastAPI, MLflow, and Evidently versions. |

## Monitoring and alerting

Grafana alert rules are provisioned from docker/grafana/provisioning/alerting.

| Rule | Condition | Threshold reasoning |
|------|-----------|---------------------|
| Fraud Rate Spike | rate(fraud_predictions_total{result="fraud"}[5m]) / ignoring(result) rate(prediction_requests_total[5m]) > 0.005 | Baseline fraud prevalence in this dataset is 0.17%; 0.5% is roughly 3x baseline, high enough to avoid noise and low enough to catch degradation early. |
| Data Drift Warning | drift_share_of_drifted_columns > 0.5 | If over half of features drift together, the issue is usually upstream data change rather than random variance, so alerting should be immediate. |

Both rules route to fraud-pipeline-email through SMTP.

## Running locally

```bash
# Clone and enter
git clone https://github.com/nanthansr/mlops-fraud-pipeline
cd mlops-fraud-pipeline

# Download data (requires Kaggle API key)
python scripts/download_data.py

# Train model
python src/model/train.py

# Start full stack (API + Prometheus + Grafana)
docker compose up --build

# API docs
open http://localhost:8000/docs

# Grafana dashboard
open http://localhost:3000  # admin / admin

# Run tests
pytest tests/ -v
```

### Simulating incidents

```bash
python scripts/simulate_incident.py --incident fraud_spike
python scripts/simulate_incident.py --incident distribution_shift
```

Expected output patterns:
- fraud_spike: prints a high observed fraud rate, typically far above the 0.5% alert threshold.
- distribution_shift: prints Amount range 5000 to 15000 and V1 to V5 shift +5.0, then drift checks should report high drift share.

## Key engineering decisions

- Decision: Pull champion model from MLflow registry in CI before image build | Why: deploys a reviewed model artifact, not an ad-hoc retrain | Rejected: train-on-every-push build job.
- Decision: Use PR-AUC as primary training metric | Why: positive class is 0.17% so ROC-AUC can hide poor fraud precision/recall tradeoff | Rejected: accuracy-only and ROC-AUC-only reporting.
- Decision: One S3 object per prediction under date partition | Why: S3 has no safe append semantics and partitioned objects support replay and drift jobs | Rejected: append-in-place file updates.
- Decision: Push batch drift metrics via Pushgateway | Why: drift job is short-lived and Prometheus cannot scrape a process after exit | Rejected: long-running fake exporter just for batch jobs.
- Decision: Alert on fraud rate at 0.5% | Why: this is about 3x baseline 0.17% and reduces normal variance noise | Rejected: ultra-low thresholds that page on normal fluctuation.
- Decision: Drift alert threshold above 50% drifted columns | Why: broad cross-feature shift usually indicates upstream data quality issue | Rejected: single-feature drift paging.
- Decision: Keep inference path stable and add JSON health summary endpoint | Why: integrates with external status tooling without changing predict semantics | Rejected: heavy refactor of serving flow.

## Interview Q and A

1. Why PR-AUC over ROC-AUC for this dataset?
PR-AUC tracks precision-recall behavior on the minority fraud class directly, which is the operational objective when only 0.17% of transactions are fraud.

2. Why one S3 object per prediction instead of appending?
S3 object append is not atomic and concurrent writes are unsafe; one object per request with date partitioning is reliable and query-friendly.

3. Why Pushgateway for drift metrics?
Drift detection runs as a batch script and exits, so Pushgateway holds last computed values for Prometheus scraping.

4. How does CI/CD prevent a bad model from deploying?
Tests must pass before image push, and deploy artifact is fetched from MLflow champion alias rather than retraining an unknown candidate on each commit.

5. What would you change first for real production?
Move from SMTP-only alerting to incident routing with escalation policy and add authenticated model governance controls around promotion and rollback.

## Dataset

Credit Card Fraud Detection on Kaggle:
- 284,807 transactions with 492 fraud cases.
- Features V1 to V28 plus Amount and Time.
- Target class: 0 legit, 1 fraud.

Dataset link: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

## Author

Nanthan Srikumar · [LinkedIn](https://www.linkedin.com/in/nanthan-sr/) · [GitHub](https://github.com/nanthansr)
