"""
MLOps Project Daily Log — Auto-entry creator
──────────────────────────────────────────────
Run at the START of every session:
    python3 scripts/devlog.py

Creates today's entry in DEVLOG.md with:
- Yesterday's "blocked on" item as the opener
- Stage you're currently in
- Blanks to fill as you work

Run at the END of every session too:
    python3 scripts/devlog.py --close

Prompts you to fill in what you built and why,
then commits the log entry to git automatically.

Works on Mac and Windows. No external dependencies.
"""

import subprocess
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path

DEVLOG_PATH = Path(__file__).parent.parent / "DEVLOG.md"

STAGES = {
    1: "Stage 1 — Foundation (model + FastAPI + Docker)",
    2: "Stage 2 — CI/CD Pipeline (GitHub Actions → AWS ECR → ECS)",
    3: "Stage 3 — MLflow Experiment Tracking",
    4: "Stage 4 — Monitoring (Prometheus + Grafana)",
    5: "Stage 5 — AIOps Anomaly Detection Layer",
    6: "Stage 6 — Portfolio Polish",
}

# ── Update this as you move through stages ──
CURRENT_STAGE = 1


def get_today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_yesterday() -> str:
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def entry_exists_today(content: str) -> bool:
    return f"## {get_today()}" in content


def get_yesterday_blocked(content: str) -> str:
    """Pull the 'Blocked on' item from yesterday's entry."""
    yesterday = get_yesterday()
    pattern = rf"## {yesterday}.*?Blocked on[:\s]*\*\*([^\n]+)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return "Nothing blocked — clean start."


def get_git_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True
        )
        return result.stdout.strip() or "main"
    except Exception:
        return "main"


def get_last_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            capture_output=True, text=True
        )
        return result.stdout.strip() or "No commits yet"
    except Exception:
        return "No commits yet"


def create_entry(blocked_yesterday: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d %A")
    stage = STAGES.get(CURRENT_STAGE, f"Stage {CURRENT_STAGE}")
    branch = get_git_branch()
    last_commit = get_last_commit()

    return f"""## {today}
**Stage**: {stage}
**Branch**: `{branch}`
**Last commit**: {last_commit}

### 🔁 Picked up from yesterday
> {blocked_yesterday}

---

### ✅ What I built / did today
<!-- Be specific. Not "worked on the API" but "added /predict endpoint with Pydantic validation" -->
-
-
-

### 🧠 Decisions made and WHY
<!-- This is the most important section. Every decision you make here is an interview answer. -->
<!-- Format: Decision → Why → What I considered and rejected -->

**Decision**:
**Why**:
**Alternatives considered**:

---

### 💥 What broke
<!-- What error, what the error message was, how you fixed it -->
<!-- If not fixed: what you tried, what you'll try next -->

**Problem**:
**Error**:
**Fix / Status**:

---

### ❓ Blocked on
<!-- One specific thing. If nothing blocked you, write "Nothing — clean session." -->
**Blocked on**:

---

### ⏭ Next session
<!-- Exact next action. Not "continue Stage 1" but "write pytest for /predict endpoint" -->
**Next action**:
**Estimated time**:

---

"""


def commit_log(today: str):
    """Auto-commit the devlog entry to git."""
    try:
        subprocess.run(["git", "add", "DEVLOG.md"], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"devlog: {today} session notes"],
            check=True
        )
        print("✅ DEVLOG.md committed to git")
    except subprocess.CalledProcessError:
        print("⚠️  Git commit failed — commit manually: git add DEVLOG.md && git commit -m 'devlog'")


def open_in_editor():
    """Open DEVLOG.md in VS Code if available, otherwise print the path."""
    try:
        subprocess.run(["code", str(DEVLOG_PATH)], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"📝 Open manually: {DEVLOG_PATH}")


def main():
    closing_mode = "--close" in sys.argv

    if not DEVLOG_PATH.exists():
        print(f"❌ DEVLOG.md not found at {DEVLOG_PATH}")
        print("Make sure you're running this from the project root or scripts/ folder.")
        sys.exit(1)

    content = DEVLOG_PATH.read_text(encoding="utf-8")
    today = get_today()

    # ── CLOSING MODE: remind to fill in and commit ──
    if closing_mode:
        if not entry_exists_today(content):
            print("⚠️  No entry for today yet — run without --close first")
            sys.exit(1)

        print(f"""
📝 End of session checklist for {today}:

Before you close your laptop, make sure you filled in:
  ✅ What I built / did today  (specific, not vague)
  ✅ Decisions made and WHY    (interview gold — don't skip)
  ✅ What broke                (error + fix)
  ✅ Blocked on                (one specific thing)
  ✅ Next session              (exact next action)

Open DEVLOG.md now? Running: code DEVLOG.md
        """)

        open_in_editor()

        answer = input("Ready to commit? (y/n): ").strip().lower()
        if answer == "y":
            commit_log(today)
        else:
            print("Remember to commit before you switch machines.")
        return

    # ── OPENING MODE: create today's entry ──
    if entry_exists_today(content):
        print(f"""
✅ Today's devlog entry already exists ({today})

Open DEVLOG.md and keep filling it in as you work.
When done for the day: python3 scripts/devlog.py --close
        """)
        open_in_editor()
        return

    blocked_yesterday = get_yesterday_blocked(content)
    new_entry = create_entry(blocked_yesterday)

    # Insert after the header comment, newest entry at top
    insert_marker = "<!-- ENTRIES BELOW — newest at top -->\n"
    if insert_marker in content:
        updated = content.replace(
            insert_marker,
            insert_marker + "\n" + new_entry
        )
    else:
        updated = content + "\n" + new_entry

    DEVLOG_PATH.write_text(updated, encoding="utf-8")

    print(f"""
✅ Today's devlog entry created: {today}
   Stage: {STAGES.get(CURRENT_STAGE, f'Stage {CURRENT_STAGE}')}

🔁 Yesterday you were blocked on:
   {blocked_yesterday}

📝 Opening DEVLOG.md...
   Fill in sections AS YOU WORK — not all at the end.

When done: python3 scripts/devlog.py --close
    """)

    open_in_editor()


if __name__ == "__main__":
    main()
