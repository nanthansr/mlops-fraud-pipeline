# MLOps Fraud Pipeline — Dev Log

> Engineering journal. Fill in AS YOU WORK, not all at the end.
> Run `/wakeup` at session start, `/wrapup` at session end.

<!-- ENTRIES BELOW — newest at top -->

## 2026-03-06 Friday
**Stage**: Stage 2 — CI/CD (GitHub Actions → AWS ECR → ECS)
**Branch**: `main`
**Last commit**: 28ffcb7 devlog: 2026-03-04 session notes

### Picked up from last session
> Configure AWS credentials (create ECR repo + IAM user + add GitHub secrets `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`) and uncomment the ECR push job in ci-cd.yml

---

### What I built / did today
- Reordered project stages: MLflow (Stage 3) before ECR/ECS deploy (Stage 2b)
- Updated README to reflect new stage order with rationale

### Decisions made and WHY
**Decision**: Do MLflow (Stage 3) before ECR/ECS deploy (Stage 2b)
**Why**: Deploying to ECS without a model registry means shipping an unversioned, untracked model. MLflow registry lets CI pull a known, approved model version — which is what "preventing a bad model from deploying" actually means in production.
**Alternatives considered**: ECR/ECS first — rejected because the CI pipeline would need to be rebuilt anyway once MLflow is added; doing it in the right order avoids rework

---

### What broke
**Problem**:
**Error**:
**Fix / Status**:

---

### Blocked on
**Blocked on**:

---

### Next session
**Next action**:

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

