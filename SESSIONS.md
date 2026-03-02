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
