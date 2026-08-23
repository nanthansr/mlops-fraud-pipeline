# Migrating the fraud API to Hugging Face Spaces

**Status: scoped, not built.** Written 2026-08-04.

## Why

The API currently runs on Nanthan's Oracle VPS at
`https://yieldai-n8n.duckdns.org/fraud-api/`, behind nginx basic auth added
2026-08-04 after a security audit found it publicly reachable, unauthenticated,
and running as root.

Basic auth stops anonymous abuse but does not fix the actual problem: **the demo
shares a machine with Hermes (which holds live OpenRouter, Telegram, Groq and
Notion tokens) and production n8n.** A compromise of the demo is a compromise of
everything. You cannot fix co-location with authentication.

Moving it to a Space fixes three things at once:

- **Isolation.** Nothing of Nanthan's is on that machine.
- **The link becomes a credential.** `huggingface.co/spaces/<user>/fraud-detection`
  reads as an ML engineer's work. `yieldai-n8n.duckdns.org/fraud-api/` reads as a
  hobby VPS, and he is job hunting.
- **The password goes away.** Public is fine once nothing valuable is co-located.

Verified 2026-08-04: HF Spaces **CPU Basic is free** - 2 vCPU, 16 GB RAM, no time
limit, no sleep. The model is 309 KB and inference is a single sklearn/xgboost
call, so free CPU is not a compromise here, it is correctly sized.

## Approach: Docker Space, not Gradio

HF Spaces supports Gradio, Streamlit, Static, and Docker SDKs. **Use Docker.**

Gradio would mean rewriting the frontend and throwing away `demo/index.html` -
1283 lines with presets, styling, and links to his GitHub and LinkedIn. It would
also hide the FastAPI surface, and the API *is* the portfolio point: this is an
MLOps pipeline project, not a model demo. The Swagger page at `/docs` is itself
an artifact worth showing for a backend or MLOps role.

Docker Space reuses the existing `Dockerfile` nearly as-is.

## Changes needed

### 1. `README.md` with HF frontmatter

Spaces are configured by YAML frontmatter in the repo's `README.md`:

```yaml
---
title: Credit Card Fraud Detection
emoji: 💳
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---
```

`app_port` matters - see gotcha 1.

### 2. Split requirements

`requirements.txt` currently installs the training stack into the serving image.
Confirmed by grep: **`mlflow` and `evidently` are not imported anywhere under
`src/api/`** - they are training-only. `mlflow` alone pulls a large dependency
tree and dominates build time.

Create `requirements-serve.txt`:

```
fastapi==0.135.1
uvicorn==0.41.0
pydantic==2.12.5
scikit-learn==1.8.0
xgboost==3.2.0
pandas==2.2.2
numpy>=2.0
joblib==1.5.3
prometheus-fastapi-instrumentator==7.1.0
prometheus-client
```

Dropped: `mlflow`, `evidently`, `boto3`, `kaggle`, `pytest`, `httpx`,
`imbalanced-learn`. See gotcha 2 about the last one.

### 3. Make the `boto3` import lazy

`src/api/main.py:9` imports `boto3` at module level, but it is only used inside
`_log_to_s3()` (line 193), which is gated behind `PREDICTION_LOG_BUCKET` being
set. Move the import inside that function so the dependency can be dropped.
One line moved, no behavior change.

### 4. Dockerfile

- `EXPOSE 7860` and `--port 7860` instead of 8000.
- `COPY requirements-serve.txt` instead of `requirements.txt`.
- Add a non-root user. HF Spaces runs containers as uid 1000; declaring it
  explicitly avoids permission surprises and is the fix for the "running as root"
  finding that started this.
- Drop the `pytest`/dev leftovers.

### 5. Model file

`models/model.joblib` is 309 KB - commit it directly. Git LFS is unnecessary
under 10 MB.

### 6. Point the demo at its own origin

`demo/index.html` uses a configurable `API_BASE` (line ~1194). On a Space the
demo and the API are the same origin, so `API_BASE` should be `''` (relative).
Confirm it is not hardcoded to the duckdns host.

## Two gotchas that will bite

### 1. `/` must serve the demo, not JSON

HF embeds the Space in an iframe pointing at `/`. Right now
`src/api/main.py:132` returns a JSON blob at `/`, so the Space would render as
raw JSON and look broken to exactly the people this is meant to impress.

Fix: redirect `/` to `/demo/`, and move the current JSON response to `/info`.
Small change, but skipping it makes the whole migration pointless.

### 2. Unpickling may need `imbalanced-learn` or `xgboost`

`joblib.load()` needs the classes inside the pickle to be importable. If
`train.py` saved a pipeline containing an imblearn step (SMOTE and similar are
common on this dataset), dropping `imbalanced-learn` breaks model loading **at
runtime, not at build time** - the container starts fine and every prediction
fails.

Do not assume. Build the slim image locally and confirm the model loads and
`/predict` returns a real score before pushing. If it needs imblearn, add it
back - it is small.

## Decisions for Nanthan

1. **Keep `/metrics` (Prometheus) on the Space?** It is a genuine MLOps signal
   for a hiring manager. It is also a public endpoint exposing request counts.
   Harmless, but his call.
2. **What happens to the VPS copy once the Space is live?** Recommended: stop the
   container, remove the `location /fraud-api/` block from nginx, delete the
   htpasswd file. Leaving it running keeps the blast-radius problem for no
   benefit.
3. **Space visibility:** public. A private Space defeats the purpose.

## Verification

1. Slim image builds locally, `docker run -p 7860:7860`, `/health` returns 200.
2. `POST /predict` with a known-fraud sample from the demo presets returns a
   sensible probability - this is the real test that the dependency slimming did
   not break unpickling.
3. `/` redirects to the demo and the page renders.
4. Push to the Space; the build log completes and the iframe shows the demo.
5. Demo's predict button works against the Space's own origin (no CORS error in
   the browser console).
6. Only then: tear down the VPS copy and revert the nginx change.

## Effort

About an hour. Roughly 60 changed lines across `Dockerfile`,
`requirements-serve.txt`, `README.md`, and two small edits in
`src/api/main.py`. The bulk of the time is the local build-and-verify loop in
step 2, which is the step worth not rushing.
