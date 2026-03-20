# MLOps Fraud Pipeline — Dev Log

> Engineering journal. Fill in AS YOU WORK, not all at the end.
> Run `/wakeup` at session start, `/wrapup` at session end.

<!-- ENTRIES BELOW — newest at top -->

## 2026-03-20 Friday
**Stage**: Stage 4 — Monitoring (Prometheus + Grafana)
**Branch**: `main`
**Last commit**: 8fb816d devlog: 2026-03-13 session notes — Stage 2b complete

### Picked up from last session
> ECS deployment — pull image from ECR, run as Fargate service, expose /predict publicly, wire health checks

---

### What I built / did today
- Created ECS cluster `mlops-fraud-pipeline` (Fargate)
- Wrote task definition `mlops-fraud-pipeline` — 0.25 vCPU, 0.5GB RAM, port 8000
- Deployed service `fraud-detection-service` — running on public IP 18.220.17.19
- Verified `/predict` endpoint live and returning correct predictions

### Decisions made and WHY
**Decision**:
**Why**:
**Alternatives considered**:

---

### What broke
**Problem**:
**Error**:
**Fix / Status**:

---

### Blocked on
**Blocked on**: Nothing — Stage 2b fully complete including ECS.

---

### Next session
**Next action**: Stage 4 — wire Prometheus scraping to FastAPI /metrics, set up Grafana dashboard

---

## 2026-03-13 Friday
**Stage**: Stage 2b — COMPLETE
**Branch**: `main`
**Last commit**: 4e0d3f7 ci: activate Stage 2b — ECR build-and-push wired to MLflow registry

### Picked up from last session
> Fix SSH (update security group SSH rule to current IP, or use EC2 Instance Connect from browser as fallback) → assign Elastic IP → confirm MLflow running on t3.small → re-run train.py → set @champion alias → add MLFLOW_TRACKING_URI to GitHub Secrets → create ECR repo → write fetch_model.py → uncomment build-and-push in ci-cd.yml

---

### What I built / did today
- Fixed EC2 SSH — updated security group SSH rule (temporarily 0.0.0.0/0 to unblock, then tightened)
- Assigned Elastic IP 3.15.26.187 to EC2 — stable address, no more IP drift
- Confirmed MLflow systemd service running and healthy on t3.small after reboot
- Re-ran train.py with MLFLOW_TRACKING_URI → EC2 — clean run, artifacts in S3
- Set `fraud-detector@champion` alias in MLflow registry on EC2
- Added `MLFLOW_TRACKING_URI` + `ECR_REPOSITORY_URI` to GitHub Secrets
- Created ECR repository `mlops-fraud-pipeline` in us-east-2
- Confirmed IAM role `mlops-github-actions-role` has ECR + S3 access
- Wrote `scripts/fetch_model.py` — loads `@champion` via `mlflow.xgboost.load_model`, re-serializes as `models/model.joblib` for FastAPI
- Removed old blind-retrain `build` job from ci-cd.yml, activated `build-and-push` job
- Verified full CI loop: push → tests → fetch champion → docker build → push to ECR ✅

### Decisions made and WHY
**Decision**: `mlflow.xgboost.load_model` + `joblib.dump` in fetch_model.py instead of `download_artifacts`
**Why**: `download_artifacts` dumps the raw MLflow artifact directory (MLmodel, model.xgb, conda files) — main.py expects `joblib.load("models/model.joblib")`. Loading via the XGBoost flavor and re-serializing gives FastAPI exactly what it needs.
**Alternatives considered**: Change main.py to load from MLflow directly — more invasive, breaks local dev workflow

**Decision**: Removed blind-retrain `build` job entirely
**Why**: CI was downloading Kaggle data and retraining on every push — expensive, non-deterministic, and bypasses the registry. Champion model lives in MLflow; CI should fetch it, not recreate it.
**Alternatives considered**: Keep both jobs — unnecessary duplication

**Decision**: `pip install mlflow boto3` explicitly in build-and-push job
**Why**: boto3 is not in requirements.txt (it's a CI/AWS concern, not a runtime dep). Fresh runner has nothing — can't assume.
**Alternatives considered**: Add boto3 to requirements.txt — pollutes the runtime image with a dep only needed in CI

**Decision**: Image tagged with `github.sha`
**Why**: Full traceability — every ECR image maps back to an exact commit. Makes rollbacks and incident investigation unambiguous.
**Alternatives considered**: `latest` tag — loses traceability, unsafe for prod

---

### What broke
**Problem**: `fetch_model.py` initial draft used `mlflow.artifacts.download_artifacts`
**Error**: Would have dumped MLflow artifact dir to disk — main.py can't joblib.load that
**Fix / Status**: Rewrote to use `mlflow.xgboost.load_model` + `joblib.dump` ✅

---

### Blocked on
**Blocked on**: Nothing — Stage 2b complete. Next is ECS deployment (Stage 2b continued).

---

### Next session
**Next action**: ECS deployment — pull image from ECR, run as Fargate service, expose /predict publicly, wire health checks

---

## 2026-03-10 Tuesday
**Stage**: Stage 2b / Stage 3 — MLflow backend + ECR/ECS deploy
**Branch**: `main`
**Last commit**: e4e30b7 devlog: 2026-03-06 full session notes — AWS infra + MLflow Stage 3

### Picked up from last session
> Promote `fraud-detector` to `@champion` alias in MLflow UI if not done, then begin Stage 2b — move MLflow backend store to shared location and uncomment ECR push job in ci-cd.yml

---

### What I built / did today
- Launched EC2 instance `mlops_mlflow_server` (us-east-2, t3.micro → upgraded to t3.small)
- Configured security group: port 22 (my IP), port 5000 (0.0.0.0/0)
- Installed MLflow on EC2 as a systemd service
- Pointed `train.py` at EC2 tracking URI — successfully logged run `salty-wasp-147` and registered `fraud-detector` in EC2 MLflow registry
- Discovered lab WiFi blocks non-standard ports — had to switch to hotspot to reach port 5000

### Decisions made and WHY
**Decision**: SQLite backend store on EC2 (not RDS)
**Why**: RDS adds cost and complexity that's unnecessary at this scope. SQLite is fine for a single-writer portfolio project.
**Alternatives considered**: RDS PostgreSQL — deferred, overkill here

**Decision**: Port 5000 open to 0.0.0.0/0
**Why**: GitHub Actions IPs are a large, changing range — restricting by IP isn't practical for CI. Accepted tradeoff for portfolio project, will document in README.
**Alternatives considered**: Restrict to GitHub IP ranges — impractical, ranges change

**Decision**: Upgraded to t3.small (2GB RAM)
**Why**: t3.micro OOM-killed MLflow — 570MB idle left zero headroom for the server process. t3.small is the minimum viable size.
**Alternatives considered**: Stay on t3.micro — model registration was 500-erroring, not viable

---

### What broke
**Problem**: t3.micro OOM — MLflow server crashed with 500 errors on `model-versions/create`
**Error**: 500 Internal Server Error from MLflow registry endpoint during `train.py` model registration
**Fix / Status**: Upgraded to t3.small. SSH now unresponsive on new instance — not yet resolved.

**Problem**: SSH timing out on t3.small after instance type change
**Error**: Connection timeout to 3.15.26.187:22
**Fix / Status**: Suspected cause — security group SSH rule still has lab WiFi IP, now on hotspot. To investigate tomorrow.

---

### Blocked on
**Blocked on**: SSH to EC2 (3.15.26.187) timing out — likely security group SSH rule has stale IP. Blocked on fixing this before any further EC2/MLflow/ECR work can proceed.

---

### Next session
**Next action**: Fix SSH (update security group SSH rule to current IP, or use EC2 Instance Connect from browser as fallback) → assign Elastic IP → confirm MLflow running on t3.small → re-run train.py → set @champion alias → add MLFLOW_TRACKING_URI to GitHub Secrets → create ECR repo → write fetch_model.py → uncomment build-and-push in ci-cd.yml

---

## 2026-03-06 Friday
**Stage**: Stage 2 — CI/CD (GitHub Actions → AWS ECR → ECS)
**Branch**: `main`
**Last commit**: 28ffcb7 devlog: 2026-03-04 session notes

### Picked up from last session
> Configure AWS credentials (create ECR repo + IAM user + add GitHub secrets `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`) and uncomment the ECR push job in ci-cd.yml

---

### What I built / did today
- Provisioned S3 bucket `mlops-fraud-pipeline-artifacts-nanthan` (us-east-2) for MLflow artifact storage
- Set up OIDC on AWS — GitHub Actions authenticates via short-lived STS tokens, no stored access keys
- Created IAM role `mlops-github-actions-role` with least-privilege inline S3 policy (3 actions, specific bucket only)
- Installed AWS CLI, configured local credentials via `mlops-local-dev` IAM user
- Added GitHub secrets: `AWS_ROLE_ARN`, `AWS_REGION`
- Reordered stages: MLflow (Stage 3) before ECR/ECS deploy (Stage 2b)
- Updated `ci-cd.yml`: OIDC permissions, region secret fix, Stage 2b block uses `role-to-assume` + `@champion` alias comment
- Updated `docker-compose.yml`: MLflow → S3 artifact backend, boto3, `~/.aws` mount, upgraded to v3.10.1
- Updated `train.py`: MLflow experiment tracking (params + metrics), model registered as `fraud-detector`, tracking URI via env var, Stage 2b backend store limitation noted
- Fixed MLflow version mismatch: local 3.10.1 vs Docker 2.13.0 — aligned both to 3.10.1
- Ran full loop: train → MLflow logs run → artifact in S3 → registered as `fraud-detector@champion` ✅
- CI passing after all changes

### Decisions made and WHY
**Decision**: OIDC over IAM access keys for CI auth
**Why**: Access keys are long-lived — if leaked, exposure until manually revoked. OIDC tokens are issued per job by GitHub, verified by AWS STS, and expire when the job ends. Nothing stored anywhere.
**Alternatives considered**: IAM access keys stored as GitHub secrets — rejected, permanent exposure risk

**Decision**: Least-privilege S3 policy (not S3FullAccess)
**Why**: IAM best practice — grant only what's needed. Role only needs GetObject, PutObject, ListBucket on this specific bucket. S3FullAccess would allow deleting any bucket, reading any object across the account.
**Alternatives considered**: S3FullAccess — faster to set up, rejected as a security anti-pattern

**Decision**: MLflow 3.x alias `@champion` over Staging/Production stages
**Why**: MLflow removed the old stage system in 2.13.0. Aliases are more flexible — you can have multiple (champion, challenger, rollback) and they're not limited to a fixed workflow.
**Alternatives considered**: Old `Production` stage string — no longer exists in MLflow 3.x

**Decision**: Backend store stays local for now
**Why**: Moving it to a shared location (EC2-hosted MLflow or RDS) is a bigger infrastructure step. For Stage 3 local dev, local backend is fine — artifact storage (the important part for CI) is already on S3.
**Alternatives considered**: Move backend to S3-backed SQLite now — deferred to Stage 2b

---

### What broke
**Problem**:
**Error**:
**Fix / Status**:

---

### Blocked on
**Blocked on**: MLflow backend store is local — CI cannot query the model registry until it's moved to a shared location (S3-backed or hosted). Known Stage 2b problem, noted in code.

---

### Next session
**Next action**: Promote `fraud-detector` to `@champion` alias in MLflow UI if not done, then begin Stage 2b — move MLflow backend store to shared location and uncomment ECR push job in ci-cd.yml

---

## 2026-03-04 Wednesday
**Stage**: Stage 2 — CI/CD (GitHub Actions → AWS ECR → ECS)
**Branch**: `main`
**Last commit**: dd52d92 fixed path for train.py

### Picked up from last session
> Create `stage-2-cicd` branch and build `.github/workflows/ci.yml` — lint + test on push, then build and push Docker image to AWS ECR

---

### What I built / did today
- Created `.github/workflows/ci-cd.yml` with two jobs: `test` (pytest) and `build` (download dataset → train model → docker build)
- Fixed dataset download URL in ci-cd.yml
- Fixed path issue for `train.py` in CI
- Pushed to `main` — GitHub Actions ran and both `test` and `build` jobs passed ✅
- ECR push job scaffolded but commented out (ready for when AWS credentials are configured)

### Decisions made and WHY
**Decision**: Run dataset download + model training inside the CI `build` job
**Why**: Docker image needs a trained model baked in; can't build a functional image without running train.py first
**Alternatives considered**: Pre-baked model artifact in repo — rejected (model file is gitignored; large binary files don't belong in git)

**Decision**: Keep ECR push job commented out rather than deleting it
**Why**: Scaffold is ready; just needs AWS secrets wired up. Commenting preserves intent without breaking the working pipeline.
**Alternatives considered**: Separate branch for ECR work — unnecessary; the commented block is clear enough

---

### What broke
**Problem**: Dataset download step used wrong URL format in ci-cd.yml
**Error**: Kaggle download failed in CI
**Fix / Status**: Fixed — corrected dataset path in `kaggle datasets download` command

**Problem**: `train.py` path incorrect in CI
**Error**: `python train.py` not found
**Fix / Status**: Fixed — changed to `python src/model/train.py`

---

### Blocked on
**Blocked on**: AWS credentials not yet configured — ECR push step is commented out until secrets are added to GitHub repo settings

---

### Next session
**Next action**: Configure AWS credentials (create ECR repo + IAM user + add GitHub secrets `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`) and uncomment the ECR push job in ci-cd.yml

---

## 2026-03-02 Monday
**Stage**: Stage 1 — Foundation (model + FastAPI + Docker)
**Branch**: `main`
**Last commit**: 3131505 Stage 1: project scaffold — fraud detection MLOps pipeline

### Picked up from last session
> Run `pip install -r requirements.txt` to fully initialize the venv, then run `python src/model/train.py` to begin Stage 1 model training.

---

### What I built / did today
- Verified dataset exists: `data/raw/creditcard.csv` (144MB, 284,807 rows)
- Installed missing venv deps: `xgboost`, `imbalanced-learn`, `fastapi`, `uvicorn`, `prometheus-fastapi-instrumentator`, `pytest`, `httpx`
- Fixed `libomp.dylib` missing error blocking XGBoost on macOS — `brew install libomp`
- Ran `src/model/train.py` — XGBoost model trained successfully in ~1s (ROC-AUC: 0.9747, PR-AUC: 0.8510)
- Launched FastAPI server via `uvicorn src.api.main:app --reload`
- Tested `/predict` endpoint manually: legit → 0.18% fraud; fraud pattern → 99.76%
- Ran `pytest tests/ -v` — 5/5 passed
- Fixed `pytest tests/ -v` `ModuleNotFoundError` — added `pytest.ini` with `pythonpath = .`
- Fixed deprecated `@app.on_event("startup")` — replaced with `lifespan` async context manager
- Dockerized Stage 1 (done in separate terminal)
- Committed and pushed all Stage 1 work to `main` (commit `8bab044`)

### Decisions made and WHY
**Decision**: Use `scale_pos_weight=577` (XGBoost native) over SMOTE for class imbalance
**Why**: Avoids synthetic data generation overhead; XGBoost handles it natively at the loss function level; faster and simpler
**Alternatives considered**: SMOTE (commented out in train.py) — adds training time and complexity; class_weight in sklearn — not applicable to XGBoost

**Decision**: PR-AUC as primary metric over ROC-AUC
**Why**: ROC-AUC is optimistic on imbalanced datasets because it factors in true negatives (99.83% of data). PR-AUC focuses on the minority class (fraud) — a model that predicts all-legit scores 0.9747 ROC-AUC but fails at actual fraud detection
**Alternatives considered**: F1-score — useful but threshold-dependent; PR-AUC is threshold-agnostic

---

### What broke
**Problem**: XGBoost failed to load on macOS
**Error**: `XGBoostError: Library not loaded: @rpath/libomp.dylib`
**Fix / Status**: Fixed — `brew install libomp` installs the OpenMP runtime XGBoost requires on macOS

**Problem**: `use_label_encoder` parameter deprecated
**Error**: `UserWarning: Parameters: { "use_label_encoder" } are not used`
**Fix / Status**: Non-breaking warning — can remove the param from `train.py` in a cleanup pass

---

### Blocked on
**Blocked on**: Nothing — Stage 1 fully complete and pushed.

---

### Next session
**Next action**: Create `stage-2-cicd` branch and build `.github/workflows/ci.yml` — lint + test on push, then build and push Docker image to AWS ECR

---

## 2026-02-27 Friday
**Stage**: Stage 1 — Foundation (model + FastAPI + Docker)
**Branch**: `main`
**Last commit**: 3131505 Stage 1: project scaffold — fraud detection MLOps pipeline

### Picked up from last session
> First session — clean start.

---

### What I built / did today
- Explored project structure and README — understood all 6 stages
- Analyzed `scripts/download_data.py` end-to-end
- Fixed kaggle v2.0.0 breaking change: `KaggleApiExtended` → `KaggleApi`
- Installed `pandas` into `.venv` (was missing despite being in requirements.txt)
- Successfully downloaded dataset to `data/raw/creditcard.csv` (284,807 rows, 492 fraud)
- Reviewed `scripts/devlog.py` — understood its open/close session structure
- Created `.claude/commands/wakeup.md` and `.claude/commands/wrapup.md` — custom slash commands for session management
- Renamed from `/start`+`/stop` to `/wakeup`+`/wrapup` after `/stop` conflicted with a Claude Code built-in

### Decisions made and WHY
**Decision**: Use `/wakeup` and `/wrapup` instead of `/start` and `/stop`
**Why**: `/stop` triggered Claude Code's `/desktop` handoff command — likely prefix-matched. Unique names avoid any built-in collisions.
**Alternatives considered**: `/session-start` / `/session-end` — rejected as too verbose

**Decision**: `SESSIONS.md` + `DEVLOG.md` as dual persistent logs
**Why**: `SESSIONS.md` is structured for quick session pickup; `DEVLOG.md` is the engineering journal with decisions/blockers for interview prep. They serve different purposes.
**Alternatives considered**: Single file — rejected because mixing session state with engineering notes makes both harder to scan

---

### What broke
**Problem**: `download_data.py` failed on import
**Error**: `ImportError: cannot import name 'KaggleApiExtended'`
**Fix / Status**: Fixed — `kaggle` v2.0.0 renamed class to `KaggleApi`. Updated import and instantiation.

**Problem**: `pandas` not installed in venv
**Error**: `ModuleNotFoundError: No module named 'pandas'`
**Fix / Status**: Fixed — `pip install pandas`. Root cause: venv was never initialized with `pip install -r requirements.txt`

---

### Blocked on
**Blocked on**: Nothing — clean session. Venv not fully initialized (only pandas added manually so far).

---

### Next session
**Next action**: Run `pip install -r requirements.txt` to fully initialize the venv, then run `python src/model/train.py` to begin Stage 1 model training.

---

