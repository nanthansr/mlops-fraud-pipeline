# Raw Dev Diary — Nandy's MLOps Project

> Honest, casual notes. What I worked on, what broke, what I figured out.
> Updated automatically every session.

---

## 2026-02-27 (Session 1)

**What I worked on:**
First session — just explored the project and tried to download the Kaggle dataset.

**What broke or confused me:**
The download script crashed immediately. Turned out `kaggle` v2.0 renamed a class and nobody told the script. Also `pandas` wasn't even installed in the venv despite being in requirements.txt — classic, venv was never actually initialized properly.

**What I figured out or decided:**
Fixed the Kaggle import (`KaggleApiExtended` → `KaggleApi`), pip installed pandas manually, got the dataset downloaded — 284k rows, 492 fraud cases (0.17%). Tiny fraction of fraud, that's going to matter later.

**Interesting tool or concept I used:**
Kaggle CLI — you can download datasets straight from terminal with `kaggle datasets download`. Needs a `~/.kaggle/kaggle.json` credentials file to work.

---

## 2026-02-27 (Session 2)

**What I worked on:**
Set up session management — wanted a way to pick up where I left off across conversations.

**What broke or confused me:**
Named the command `/stop` and it opened Claude Desktop instead of running my command. Apparently Claude Code has built-in commands and `/stop` conflicts with one of them. Annoying but easy fix.

**What I figured out or decided:**
Renamed to `/wakeup` and `/wrapup` — unique enough to not clash with anything. Also set up two log files: `SESSIONS.md` for quick pickup state, `DEVLOG.md` as a proper engineering journal. Different purposes, both useful.

**Interesting tool or concept I used:**
Claude Code custom slash commands — you can drop a `.md` file in `.claude/commands/` and it becomes a `/commandname` you can run in any session. The file is literally just the instructions for what Claude should do.

---

## 2026-03-02

**What I worked on:**
Stage 1 — trained the fraud model, got FastAPI running, tested the `/predict` endpoint, wrote tests, and Dockerized the whole thing.

**What broke or confused me:**
XGBoost wouldn't load on Mac — cryptic error about `libomp.dylib` missing. Turns out XGBoost needs OpenMP which doesn't come with macOS. `brew install libomp` fixed it. Also pytest kept throwing `ModuleNotFoundError: No module named 'src'` — fixed by adding a `pytest.ini` with `pythonpath = .` so it knows where to look.

**What I figured out or decided:**
Used `scale_pos_weight=577` to handle the 577:1 class imbalance natively in XGBoost — simpler than SMOTE and no synthetic data. Also switched to PR-AUC as the main metric instead of ROC-AUC because ROC-AUC is misleading on super imbalanced datasets (a model that predicts everything as legit scores 0.97 ROC-AUC — that's useless).

**Interesting tool or concept I used:**
FastAPI `lifespan` context manager — the modern way to run startup/shutdown logic. The old `@app.on_event("startup")` is deprecated. Small change, same result, cleaner code.

---

## 2026-03-04

**What I worked on:**
Stage 2 CI/CD — set up GitHub Actions to automatically run tests and build the Docker image on every push.

**What broke or confused me:**
Two issues in the YAML. First, Kaggle 403'd — forgot I needed to accept the dataset terms on the website before the API would let me download it. Second, the dataset slug in the YAML was wrong (`creditcard-fraud-detection` vs the actual `mlg-ulb/creditcardfraud`). Also had `python train.py` instead of `python src/model/train.py` — it's not in the root.

**What I figured out or decided:**
Both jobs are green now — `test` runs pytest, `build` downloads data, retrains the model, and builds the Docker image. ECR push is scaffolded but commented out until I wire up AWS secrets. Left it in rather than deleting it — easier to uncomment than rewrite.

**Interesting tool or concept I used:**
GitHub Actions secrets — you store sensitive stuff like `KAGGLE_KEY` in the repo settings and reference them in YAML as `${{ secrets.KAGGLE_KEY }}`. Never touches the code, never ends up in git history.

---

## 2026-03-06

**What I worked on:**
Big AWS setup day + wired MLflow into the full pipeline. Provisioned S3, set up OIDC auth for GitHub Actions, created the IAM role, then updated ci-cd.yml, docker-compose, and train.py. Ran the full loop end to end — trained model, saw the run in MLflow UI, confirmed artifact path points to S3, promoted to `@champion`.

**What broke or confused me:**
MLflow version mismatch — local venv had 3.10.1, Docker image was 2.13.0. The new `log_model` in 3.x calls a `/logged-models` API endpoint that doesn't exist on the 2.x server. Got a 404 and a cryptic traceback. Fixed by upgrading the Docker image to match local. Also: almost did ECR/ECS before MLflow — would've shipped an unversioned model and had to redo the CI pipeline later.

**What I figured out or decided:**
OIDC is the right way to auth GitHub Actions with AWS — no stored keys, short-lived tokens per job. Also figured out MLflow's two storage layers: `--backend-store-uri` for run metadata (stays local), `--default-artifact-root` for model files (goes to S3). MLflow 3.x dropped Staging/Production stages — now use aliases. `@champion` is the new Production.

**Interesting tool or concept I used:**
IAM least-privilege — instead of giving the role S3FullAccess, scoped it to exactly 3 actions (GetObject, PutObject, ListBucket) on exactly one bucket. If the role ever gets compromised, blast radius is minimal.

---
