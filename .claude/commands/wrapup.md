You are the session assistant for this MLOps project. When this command is run, do the following steps in order:

## 1. Gather session evidence

Run these in parallel:
- `git status` and `git diff --stat HEAD`
- `git log --oneline -5`
- Read the current session's entry in `SESSIONS.md` (the last `## Session` block) to recall the goal and any work log notes

## 2. Update SESSIONS.md

Find the last `## Session` block in `SESSIONS.md` (the one that was opened by `/start` today) and fill in the placeholder fields:

- **Goal**: use whatever the user said they were working on at the start, or infer from the conversation
- **Work log**: bullet-point summary of everything done this session (infer from conversation history and git diff)
- **Files changed**: list all files touched (from git status + diff)
- **Decisions made**: any architecture, tool, or approach decisions made during the session
- **Blockers**: unresolved errors, open questions, or things that slowed progress
- **Next session**: one specific, concrete next action (not vague — e.g. "write pytest for /predict endpoint" not "continue Stage 1")
- **Interview Q**: one question the user should be able to answer based on today's work

## 3. Update DEVLOG.md

Find today's entry in `DEVLOG.md` and fill in the sections that are still blank:

- **What I built / did today**: bullet list of concrete things built or done
- **Decisions made and WHY**: any decisions from the session
- **What broke**: any errors encountered and how they were fixed (or current status)
- **Blocked on**: the single most important blocker, or "Nothing — clean session."
- **Next session → Next action**: the exact same next action written in SESSIONS.md

## 4. Commit session logs

Stage and commit `SESSIONS.md` and `DEVLOG.md`:

```
git add SESSIONS.md DEVLOG.md
git commit -m "devlog: [YYYY-MM-DD] session notes"
```

Report the commit hash. Then ask the user: "Push to remote? (yes/no)" — if yes, run `git push`. If no, skip.

## 5. Print a closing summary

Output this to the user:

```
── SESSION STOP [date] [time] ───────────────────────

WHAT WE DID
  [3-5 bullet points of concrete work done]

FILES TOUCHED
  [list]

NEXT SESSION
  → [exact next action]

INTERVIEW Q
  [the question]

SESSIONS.md and DEVLOG.md updated and committed.
Push status: [pushed / skipped]
─────────────────────────────────────────────────────
```
