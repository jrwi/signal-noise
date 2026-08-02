# PROGRESS

Running log. Newest entries at top.

---

## 2026-08-01 — Session 1: the repo exists now

**Context.** Project went quiet after 2026-03-15 — work got hectic, then a layoff. Returning to it as a learning project first, portfolio second.

**Shipped**
- `git init` + baseline commit `88cb86b`. Four months of work now has a history. `.env`, `.cache`, and unrelated scratch files stay out via `.gitignore`.
- Rewrote `CLAUDE.md` / `AGENTS.md` from "demanding coach on a 12–16 week clock" to guide mode: learning-first, 3–5 things per session, nothing ships half-built.
- This file.

**Repo state at restart**
- ~330 lines of Python. SDK skeleton only.
- Working: Spotify client (40 lines), Postgres client (67), DynamoDB client (55), Alembic initial migration, local Terraform for DynamoDB, docker-compose.
- Empty: `tests/`, `data_generators/`, `airflow/`. No Spark, no dbt, no S3, no Kafka.
- **Known mess:** three competing Track models — `models/track.py`, `models/track_v1.py`, `models/spotify_track.py`. Unresolved.
- Tests are scattered: some in `signal_noise_sdk/tests/`, some sitting inside `signal_noise_sdk/storage/`.

**Slipped**
- Both March commitments (PROGRESS.md, phase-1 slice definition) went unmet for four months. Cause was life, not scope. Closed now.

**Learned**
- Nothing technical yet. Session was housekeeping.

**Next session opens with**
- Collapse the three Track models into one, and write down why that one won.

**Parking lot**
- Move all tests under a single `tests/` tree.
- Decide whether DynamoDB stays in the design at all, or was a detour.
- `data_generators/` is empty — synthetic play-event generator needed before any streaming work.
