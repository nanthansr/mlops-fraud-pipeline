# MLOps Fraud Pipeline — Session Log

---

## Session 2026-02-27 18:22

**Goal**: Exploratory — understand the project and get the data pipeline working

**What we did**:
- Reviewed the project README — understood the 6-stage MLOps pipeline (train → serve → monitor → AIOps → alert)
- Analyzed `scripts/download_data.py` — traced the full flow: kaggle install check → credentials check → download → CSV validation
- Fixed a breaking bug in `download_data.py`: `kaggle` v2.0.0 renamed `KaggleApiExtended` to `KaggleApi`
- Installed `pandas` into `.venv` (was missing)
- Successfully downloaded the dataset: 284,807 rows, 492 fraud cases (0.173%), saved to `data/raw/creditcard.csv`
- Set up `SESSIONS.md` as a persistent session log with auto-captured pre-session state

**Files changed**:
- `scripts/download_data.py` — fixed `KaggleApiExtended` → `KaggleApi` import
- `SESSIONS.md` — created (this file)

**Decisions made**:
- Use `.venv/bin/python` for all script execution (venv is the project Python)
- Session log will auto-capture git state at every SESSION START

**Blockers**:
- `pandas` was not in the venv despite being in `requirements.txt` — may indicate venv was never fully initialized with `pip install -r requirements.txt`
- `scripts/devlog.py` is untracked — unknown purpose, not reviewed yet

**Next session**: Run `pip install -r requirements.txt` to fully initialize the venv, then move to `python src/model/train.py` (Stage 1)

**Interview Q**: The kaggle dataset has 0.17% fraud cases — what techniques would you use to handle this class imbalance during model training, and what evaluation metric would you prioritize over accuracy and why?

---

## Session 2026-02-27 19:00

**Goal**: Set up persistent session management tooling (devlog + custom slash commands)

**Work log**:
- Reviewed `scripts/devlog.py` — understood its open/close structure and `DEVLOG.md` dependency
- Created `.claude/commands/start.md` and `.claude/commands/stop.md` as custom slash commands
- Discovered `/stop` conflicts with a Claude Code built-in (triggers desktop handoff)
- Renamed commands to `/wakeup` and `/wrapup` to avoid all built-in collisions
- Created `DEVLOG.md` with today's first entry at `/wrapup`

**Files changed**:
- `.claude/commands/wakeup.md` — created (session start command)
- `.claude/commands/wrapup.md` — created (session end command)
- `DEVLOG.md` — created with first entry

**Decisions made**:
- `/wakeup` + `/wrapup` naming to avoid Claude Code built-in conflicts
- Dual-log approach: `SESSIONS.md` for structured pickup, `DEVLOG.md` for engineering journal/interview prep

**Blockers**:
- Venv not fully initialized — only `pandas` added manually; `pip install -r requirements.txt` not yet run

**Next session**: Run `pip install -r requirements.txt` to fully initialize the venv, then run `python src/model/train.py` to begin Stage 1 model training

**Interview Q**: What is the purpose of separating experiment tracking (MLflow) from serving metrics monitoring (Prometheus) — why not use one tool for both?

---

## Session 2026-03-02 13:00

**Pre-session state**:
- Branch: `main`
- Last commit: `3131505 Stage 1: project scaffold — fraud detection MLOps pipeline`
- Modified files: `scripts/download_data.py`
- Untracked files: `.claude/`, `DEVLOG.md`, `SESSIONS.md`, `scripts/devlog.py`

**Picked up from last session**: Run `pip install -r requirements.txt` to fully initialize the venv, then run `python src/model/train.py` to begin Stage 1 model training

**Goal**: Complete Stage 1 — train the model and get the FastAPI serving endpoint working

**Work log**:
- Verified dataset: `data/raw/creditcard.csv` — 144MB, 284,807 rows
- Installed missing deps: `xgboost`, `imbalanced-learn`, `fastapi`, `uvicorn`, `prometheus-fastapi-instrumentator`
- Fixed XGBoost load error: `libomp.dylib` missing — resolved with `brew install libomp`
- Ran `src/model/train.py` successfully — model trained in ~1s, saved to `models/model.joblib`
- Launched FastAPI with uvicorn (`src.api.main:app --reload`) — model loaded on startup
- Tested `/predict` endpoint with two cases: legit ($149.62 → 0.18% fraud) and known fraud pattern → 99.76% fraud

**Files changed**:
- `models/model.joblib` — created (trained XGBoost model, gitignored)
- `models/metrics.json` — created (ROC-AUC: 0.9747, PR-AUC: 0.8510, gitignored)
- `src/api/main.py` — replaced deprecated `@app.on_event("startup")` with `lifespan` handler
- `pytest.ini` — created with `pythonpath = .` so `pytest tests/ -v` works from any terminal
- `Dockerfile` + `docker-compose.yml` — updated (Dockerized Stage 1)
- `scripts/download_data.py` — kaggle v2 fix committed
- `.claude/commands/wakeup.md` + `wrapup.md` — session management commands committed
- `scripts/devlog.py` — committed

**Decisions made**:
- `scale_pos_weight=577` used to handle 577:1 class imbalance (XGBoost native approach over SMOTE)
- PR-AUC chosen as primary metric over ROC-AUC — more meaningful for imbalanced datasets
- `lifespan` handler over `@app.on_event` — future-proof FastAPI pattern
- Branch strategy: use feature branches from Stage 2 onwards (`stage-2-cicd` etc.) to demonstrate proper CI/CD workflow

**Blockers**:
- Venv still partially initialized — individual packages installed manually, `pip install -r requirements.txt` not run as a full init step

**Next session**: Create `stage-2-cicd` branch and begin GitHub Actions CI/CD pipeline (`.github/workflows/ci.yml`) — lint + test on push, then build and push Docker image to AWS ECR

**Interview Q**: Why is PR-AUC a better evaluation metric than ROC-AUC for a dataset with 0.17% fraud cases — what does each metric actually measure?

## Session 2026-03-04 HH:MM

**Pre-session state**:
- Branch: `main`
- Last commit: `1009a57 devlog: 2026-03-02 session notes final`
- Modified files: none
- Untracked files: none

**Picked up from last session**: Create `stage-2-cicd` branch and begin GitHub Actions CI/CD pipeline (`.github/workflows/ci.yml`) — lint + test on push, then build and push Docker image to AWS ECR

**Goal**: Stage 2 CI/CD — get GitHub Actions pipeline passing (test + build jobs)

**Work log**:
- Created `.github/workflows/ci-cd.yml` with `test` job (pytest) and `build` job (kaggle download → train → docker build)
- Fixed wrong dataset URL in ci-cd.yml
- Fixed `train.py` path (`src/model/train.py`)
- Pushed to `main` — both GitHub Actions jobs passing ✅
- ECR push job scaffolded and commented out (ready for AWS secrets)

**Files changed**:
- `.github/workflows/ci-cd.yml` — created (test + build jobs)
- `README.md` — added CI status badge

**Decisions made**:
- Train model inside CI `build` job so Docker image has a baked-in model
- ECR push job commented out (not deleted) — scaffold ready, pending AWS secrets
- Used `main` branch directly for Stage 2 (no feature branch needed at this scale)

**Blockers**:
- AWS credentials not configured — ECR push step is on hold until secrets added to GitHub repo settings

**Next session**: Configure AWS credentials (ECR repo + IAM user + GitHub secrets `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) and uncomment the ECR push job in ci-cd.yml

**Interview Q**: In your CI pipeline, why do you train the model inside the build job rather than committing the model file to git?

## Session 2026-03-06 HH:MM

**Pre-session state**:
- Branch: `main`
- Last commit: `28ffcb7 devlog: 2026-03-04 session notes`
- Modified files: none
- Untracked files: none

**Picked up from last session**: Configure AWS credentials (ECR repo + IAM user + GitHub secrets `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) and uncomment the ECR push job in ci-cd.yml

**Goal**: Stage 3 — provision AWS infrastructure, wire MLflow into the pipeline, complete full train→log→S3→registry loop

**Work log**:
- Provisioned S3 bucket `mlops-fraud-pipeline-artifacts-nanthan` in `us-east-2` for MLflow artifacts
- Set up OIDC identity provider on AWS — GitHub Actions authenticates via short-lived STS tokens, no stored keys
- Created IAM role `mlops-github-actions-role` with least-privilege inline policy scoped to specific bucket + 3 actions only (GetObject, PutObject, ListBucket) — removed broad S3FullAccess
- Installed AWS CLI, configured local credentials via `mlops-local-dev` IAM user
- Added GitHub secrets: `AWS_ROLE_ARN`, `AWS_REGION`
- Reordered stages: MLflow (Stage 3) before ECR/ECS (Stage 2b) — right architectural order
- Updated `ci-cd.yml`: `permissions: id-token: write` for OIDC, fixed hardcoded `us-east-1` → `${{ secrets.AWS_REGION }}`, Stage 2b commented block updated to `role-to-assume` pattern + `@champion` alias comment
- Updated `docker-compose.yml`: MLflow uses S3 as artifact backend, boto3 installed in container, `~/.aws` mounted, upgraded image to v3.10.1
- Updated `train.py`: MLflow experiment tracking added (params + metrics), model registered as `fraud-detector`, tracking URI via `os.getenv()`, Stage 2b backend store limitation noted in comment
- Fixed MLflow version mismatch (local 3.10.1 vs Docker 2.13.0) — aligned both to 3.10.1
- Ran full loop: `train.py` → MLflow logged run → artifact stored in S3 → model registered as `fraud-detector@champion` ✅
- CI confirmed passing after all changes
- Created `RAWLOG.md` (personal diary, all sessions backfilled) and `CLAUDE.md` (ground rules)

**Files changed**:
- `.github/workflows/ci-cd.yml` — OIDC auth, region secret fix, Stage 2b block updated
- `docker-compose.yml` — MLflow S3 artifact backend, boto3, `~/.aws` mount, v3.10.1
- `src/model/train.py` — MLflow tracking + registration, env var URI, Stage 2b note
- `requirements.txt` — MLflow pinned to 3.10.1
- `README.md` — stages reordered, Stage 1 + 2a marked complete
- `RAWLOG.md` — created
- `CLAUDE.md` — created

**Decisions made**:
- OIDC over IAM access keys — no long-lived credentials, STS issues temporary creds per job
- Least-privilege S3 policy — scoped to specific bucket and 3 actions, not S3FullAccess
- MLflow aliases (`@champion`) over deprecated Staging/Production stages — removed in MLflow 2.13.0+
- Backend store stays local for now — will move to EC2-hosted MLflow in Stage 2b (noted in code)
- Tracking URI via `os.getenv()` — CI can override via secret without code changes
- MLflow before ECR/ECS — registry must exist before CI can deploy a versioned model

**Blockers**:
- MLflow backend store is local (`./mlruns`) — CI cannot query the registry until it's moved to a shared location (EC2-hosted MLflow or S3-backed store). Known Stage 2b problem, noted in code.

**Next session**: Begin Stage 2b — host MLflow tracking server on EC2 (or move backend store to shared location) so CI can query the registry, then uncomment and wire up the ECR push job in ci-cd.yml

**Interview Q**: MLflow 3.x removed Staging/Production stages — what replaced them, and how do you reference the champion model version in code?

## Session 2026-03-10 HH:MM

**Pre-session state**:
- Branch: `main`
- Last commit: `e4e30b7 devlog: 2026-03-06 full session notes — AWS infra + MLflow Stage 3`
- Modified files: none
- Untracked files: `AWSCLIV2.pkg`

**Picked up from last session**: Begin Stage 2b — host MLflow tracking server on EC2 (or move backend store to shared location) so CI can query the registry, then uncomment and wire up the ECR push job in ci-cd.yml

**Goal**: Spin up EC2-hosted MLflow tracking server so GitHub Actions CI can query the fraud-detector@champion model registry

**Work log**:
- Launched EC2 `mlops_mlflow_server` (us-east-2, t3.micro → t3.small after OOM)
- Security group: port 22 (own IP), port 5000 (0.0.0.0/0)
- Installed MLflow on EC2 as systemd service
- Switched to hotspot — lab WiFi blocks port 5000
- train.py hit EC2 MLflow, logged run salty-wasp-147, registered fraud-detector in registry ✅
- t3.micro OOM-killed MLflow on model-versions/create (500 errors) — upgraded to t3.small
- SSH to t3.small now unresponsive — suspected stale SSH IP rule in security group

**Files changed**: none — all work was AWS console + EC2 setup
**Decisions made**: SQLite backend (not RDS), port 5000 open to 0.0.0.0/0, t3.small over t3.micro
**Blockers**: SSH to EC2 (3.15.26.187) timing out — security group SSH rule likely has stale IP from lab WiFi
**Next session**: Fix SSH → assign Elastic IP → confirm MLflow on t3.small → re-run train.py → set @champion alias → MLFLOW_TRACKING_URI secret → create ECR repo → fetch_model.py → uncomment build-and-push in ci-cd.yml
**Interview Q**: Your MLflow tracking server is on EC2 with port 5000 open to 0.0.0.0/0 — what are the risks and what would you do differently in a real production setup?

## Session 2026-03-13 19:14

**Pre-session state**:
- Branch: `main`
- Last commit: `66d16ca devlog: 2026-03-10 session notes — Stage 2b EC2 MLflow setup (blocked on SSH)`
- Modified files: none
- Untracked files: `AWSCLIV2.pkg`

**Picked up from last session**: Fix SSH → assign Elastic IP → confirm MLflow on t3.small → re-run train.py → set @champion alias → MLFLOW_TRACKING_URI secret → create ECR repo → fetch_model.py → uncomment build-and-push in ci-cd.yml

**Goal**: Complete Stage 2b — fix SSH blocker, wire ECR build-and-push to MLflow registry, verify full CI loop

**Work log**:
- Fixed EC2 SSH — SG SSH rule updated (temp 0.0.0.0/0 → tightened back)
- Elastic IP 3.15.26.187 assigned to EC2
- MLflow systemd service confirmed healthy on t3.small after reboot
- train.py re-run → EC2 MLflow tracking, artifacts in S3 ✅
- fraud-detector@champion alias set in MLflow registry ✅
- MLFLOW_TRACKING_URI + ECR_REPOSITORY_URI added to GitHub Secrets
- ECR repo mlops-fraud-pipeline created in us-east-2
- IAM role ECR + S3 permissions confirmed
- scripts/fetch_model.py written — mlflow.xgboost.load_model + joblib.dump (not download_artifacts)
- ci-cd.yml: old blind-retrain build job removed, build-and-push job activated
- Full CI loop verified: push → tests → fetch @champion → docker build → ECR push ✅

**Files changed**: `scripts/fetch_model.py` (new), `.github/workflows/ci-cd.yml`, `DEVLOG.md`, `SESSIONS.md`
**Decisions made**: mlflow.xgboost.load_model over download_artifacts (FastAPI needs joblib not MLflow dir); removed blind-retrain job; explicit boto3 install in CI; image tagged with github.sha
**Blockers**: None — Stage 2b complete
**Next session**: ECS deployment — pull image from ECR, run as Fargate service, expose /predict publicly, wire health checks
**Interview Q**: CI now fetches a registered model from MLflow instead of retraining — what are the tradeoffs of baking the model into the Docker image at build time vs loading it at container startup from S3/MLflow?

## Session 2026-03-20 06:11

**Pre-session state**:
- Branch: `main`
- Last commit: `8fb816d devlog: 2026-03-13 session notes — Stage 2b complete`
- Modified files: none
- Untracked files: `AWSCLIV2.pkg`

**Picked up from last session**: ECS deployment — pull image from ECR, run as Fargate service, expose /predict publicly, wire health checks

**Goal**: Complete ECS deployment — get /predict live on Fargate

**Work log**:
- Created ECS cluster `mlops-fraud-pipeline` (Fargate)
- Task definition `mlops-fraud-pipeline` — 0.25 vCPU, 0.5GB, port 8000
- Deployed service `fraud-detection-service` — public IP 18.220.17.19
- Verified /predict live and returning correct predictions ✅

**Files changed**: none — all AWS console work
**Decisions made**: Fargate (serverless containers, no EC2 management); 0.25 vCPU / 0.5GB (minimum viable for inference)
**Blockers**: None — Stage 2b fully complete
**Next session**: Stage 4 — wire Prometheus scraping to FastAPI /metrics, set up Grafana dashboard
**Interview Q**: Your ECS task has 0.25 vCPU and 0.5GB RAM — how would you decide when to scale up, and what metrics would you watch?

## Session 2026-03-22 22:33

**Pre-session state**:
- Branch: `main`
- Last commit: `348d1af devlog: update 2026-03-13 entry — Stage 2b fully complete incl. ECS`
- Modified files: none
- Untracked files: `AWSCLIV2.pkg`

**Picked up from last session**: Stage 4 — wire Prometheus to scrape metrics from FastAPI, build Grafana dashboard showing prediction rate, fraud rate, latency

**Goal**: Stage 4 — wire Prometheus custom metrics, S3 prediction logging, Evidently drift detection, Grafana dashboard

**Work log**:
- Added evidently==0.7.20, prometheus-client, boto3 to requirements.txt (fixed numpy pin conflict and stale package versions along the way)
- Created src/api/monitoring.py — fraud_predictions_total Counter (labelled fraud/legit), prediction_probability Histogram, prediction_requests_total Counter
- Updated src/api/main.py — custom metrics updated on every /predict call; each prediction logged to S3 at prediction-logs/date=YYYY-MM-DD/<uuid>.jsonl in a background thread
- Created scripts/generate_reference.py — stratified 5000-row sample from creditcard.csv, saved to data/processed/reference.csv
- Updated .gitignore to commit reference.csv
- Added pushgateway service to docker-compose.yml (port 9091), added scrape job with honor_labels: true to docker/prometheus.yml
- Created scripts/drift_check.py — reads today's S3 partition, runs Evidently DataDriftPreset vs reference.csv, pushes drift_dataset_drift_detected and drift_share_of_drifted_columns to Pushgateway. Supports --date flag.
- Created Grafana provisioning: datasources/prometheus.yaml, dashboards/dashboards.yaml, dashboards/fraud-monitoring.json (5-panel dashboard)
- Mounted ./docker/grafana/provisioning into grafana service
- Fixed evidently 0.7.x API (module paths, Snapshot return, dict structure)
- Fixed S3 credentials in container by mounting ~/.aws into app service
- Verified: Prometheus targets UP, fraud_predictions_total visible, 20 predictions logged to S3, drift check processes predictions, Grafana dashboard auto-loads

**Files changed**: `requirements.txt`, `src/api/main.py`, `src/api/monitoring.py` (new), `scripts/generate_reference.py` (new), `scripts/drift_check.py` (new), `data/processed/reference.csv` (new), `.gitignore`, `docker-compose.yml`, `docker/prometheus.yml`, `docker/grafana/provisioning/datasources/prometheus.yaml` (new), `docker/grafana/provisioning/dashboards/dashboards.yaml` (new), `docker/grafana/provisioning/dashboards/fraud-monitoring.json` (new)
**Decisions made**: S3 over CSV/SQLite for prediction logs (production-correct); one object per prediction with uuid key (no native S3 append, Hive partitioning for Athena); Pushgateway for drift metrics (batch job can't be scraped after exit); honor_labels: true to preserve pushed job labels; reference.csv committed (stable 5000-row snapshot); background thread for S3 write (keeps /predict latency clean)
**Blockers**: None — Stage 4 complete
**Next session**: Stage 5 — Grafana alerting rules on fraud rate spike and drift threshold breach, Slack or email alert routing, incident simulation write-up
**Interview Q**: Your drift check script pushes metrics to a Pushgateway instead of exposing a /metrics endpoint — why, and what are the tradeoffs of the Pushgateway pattern?
