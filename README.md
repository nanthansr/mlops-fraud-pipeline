# MLOps CI/CD Pipeline — Credit Card Fraud Detection

![CI](https://github.com/nanthansr/mlops-fraud-pipeline/actions/workflows/ci-cd.yml/badge.svg)

> End-to-end MLOps pipeline: train → serve → monitor → detect anomalies → alert

## What This Is

A production-grade MLOps pipeline built on credit card fraud detection.
Demonstrates the full stack an MLOps engineer is expected to own:
model training, FastAPI serving, Docker containerization, GitHub Actions CI/CD,
MLflow experiment tracking, Prometheus + Grafana monitoring, and an AIOps anomaly detection layer.

Built cross-platform — runs identically on Mac and Windows via Docker.

## Stack

| Layer | Technology |
|-------|-----------|
| Model | scikit-learn / XGBoost — fraud classification (imbalanced dataset) |
| API | FastAPI + Uvicorn |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions → AWS ECR → AWS ECS |
| Experiment Tracking | MLflow |
| Monitoring | Prometheus + Grafana |
| Cloud | AWS (ECR, ECS, CloudWatch) |
| Language | Python 3.11 |

## Project Stages

- [ ] **Stage 1** — Foundation: model + FastAPI + Docker (local)
- [ ] **Stage 2** — CI/CD: GitHub Actions → AWS ECR → ECS deploy
- [ ] **Stage 3** — MLflow: experiment tracking + model registry
- [ ] **Stage 4** — Monitoring: Prometheus metrics + Grafana dashboard
- [ ] **Stage 5** — AIOps: anomaly detection on build times + model drift alerts
- [ ] **Stage 6** — Polish: clean README, architecture diagram, demo video, LinkedIn post

## Running Locally

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
docker compose run app pytest tests/ -v
```

## Architecture

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

## Dataset

**Credit Card Fraud Detection** — Kaggle
- 284,807 transactions, 492 fraudulent (0.17% — highly imbalanced)
- Features: V1–V28 (PCA-transformed), Amount, Time
- Target: Class (0 = legitimate, 1 = fraud)
- Key challenge: imbalanced classes — requires SMOTE or class weighting

Download: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

## Interview Talking Points (fill in as you build)

- Why XGBoost over logistic regression for this problem?
- How did you handle class imbalance?
- What happens if model accuracy drops in production?
- How does your CI/CD pipeline prevent a bad model from deploying?
- What metrics are you monitoring and why those specifically?

## Author

Nanthan Srikumar · [LinkedIn](https://www.linkedin.com/in/nanthan-sr/) · [GitHub](https://github.com/nanthansr)
