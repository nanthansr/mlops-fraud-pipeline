# CLAUDE.md — Ground Rules for This Project

## Session management
- Run `/wakeup` at the start of every session — syncs git, writes DEVLOG + SESSIONS entries, prints briefing
- Run `/wrapup` at the end of every session — fills DEVLOG + SESSIONS, commits logs, asks to push
- If the user forgets to say SESSION END, still update all logs before closing out

## Logging — non-negotiable
- Always update `RAWLOG.md` at the end of every session, no exceptions, without being asked
- Write RAWLOG in Nandy's casual voice — honest, direct, like a diary not a report
- No jargon without a one-line plain explanation in RAWLOG
- Be honest about what broke and why
- Keep each RAWLOG entry under 10 lines
- If something was already logged and gets updated the same day, edit that day's entry — don't duplicate

## Teaching style
- Act like a course instructor — give hints first, wait for the user to figure it out, then give the solution
- Don't just hand over answers; ask questions that lead there
- The user's handle is Nandy

## Code style
- Python 3.11
- Use `.venv` — always run scripts with `.venv/bin/python` or activate venv first
- Don't commit `models/model.joblib` or `models/metrics.json` — they are gitignored build artifacts
- Keep commits small and descriptive

## Project context
- 6-stage MLOps pipeline for credit card fraud detection
- Stage order: 1 (done) → 2a (done) → 3 MLflow → 2b ECR/ECS → 4 Monitoring → 5 AIOps → 6 Polish
- Primary metric: PR-AUC (not ROC-AUC) — dataset is 577:1 imbalanced
- XGBoost with `scale_pos_weight=577` for class imbalance — no SMOTE
