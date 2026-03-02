You are the session assistant for this MLOps project. When this command is run, do the following steps in order:

## 1. Sync with remote

Run `git pull` to fetch and merge any remote changes. Report the result (up to date, fast-forwarded, or conflicts). If there are merge conflicts, stop and tell the user — do not proceed until resolved.

## 3. Capture current state

Run these in parallel:
- `git status` and `git log --oneline -5`
- Read `SESSIONS.md` — extract the last session's **Next session** and **Blockers** fields
- Read `DEVLOG.md` — extract the most recent entry's **Next action** and **Blocked on** fields
- Read `README.md` — identify which stage checkboxes are completed vs pending
- List files in `src/`, `scripts/`, `data/` to understand current codebase state

## 4. Write today's DEVLOG.md entry

Read the current `DEVLOG.md`. If there is no entry for today's date yet, prepend a new entry using this exact template (fill in real values from git and from the previous entry):

```
## YYYY-MM-DD Weekday
**Stage**: [current stage from README checkboxes]
**Branch**: `[current branch]`
**Last commit**: [last commit oneline]

### Picked up from last session
> [the "Next action" from previous DEVLOG entry, or "Clean start." if none]

---

### What I built / did today
-

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
**Blocked on**:

---

### Next session
**Next action**:

---

```

Insert the new entry immediately after the line `<!-- ENTRIES BELOW — newest at top -->` if that marker exists, otherwise prepend after the file header.

## 5. Append a new session entry to SESSIONS.md

Append the following to `SESSIONS.md` (fill in real values):

```
## Session YYYY-MM-DD HH:MM

**Pre-session state**:
- Branch: `[branch]`
- Last commit: `[last commit]`
- Modified files: [list or "none"]
- Untracked files: [list or "none"]

**Picked up from last session**: [Next session line from previous SESSIONS.md entry, or "First session."]

**Goal**: [to be filled by user]

**Work log**:
<!-- appended during session -->

**Files changed**: <!-- filled at /stop -->
**Decisions made**: <!-- filled at /stop -->
**Blockers**: <!-- filled at /stop -->
**Next session**: <!-- filled at /stop -->
**Interview Q**: <!-- filled at /stop -->
```

## 6. Print a briefing to the user

Output a clean, concise briefing in this format:

```
── SESSION START [date] [time] ──────────────────────

LAST SESSION
  Worked on : [summary from last SESSIONS.md entry]
  Ended at  : [date/time of last session]
  Blocked on: [blocker from last session]

PICK UP FROM
  [exact Next session / Next action line]

CODEBASE STATE
  Branch     : [branch]
  Last commit: [commit]
  Stage      : [current stage]
  Data       : [whether creditcard.csv exists in data/raw/]

─────────────────────────────────────────────────────
What are you working on today?
```

Then wait for the user's response and note their goal.
