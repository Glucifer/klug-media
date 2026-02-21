# PROJECT_CONTEXT.md

Purpose: quick rehydration file after context compaction so work can resume with correct project state and workflow assumptions.

## High-Level Architecture
- Backend: FastAPI app (`app/main.py`) with routers mounted under `/api/v1`.
- Layers:
  - `app/api/`: thin HTTP endpoints
  - `app/services/`: business logic
  - `app/repositories/`: data access/query helpers
  - `app/db/models/`: SQLAlchemy ORM entities
  - `app/schemas/`: Pydantic request/response models
- DB: PostgreSQL via SQLAlchemy 2.x, migrations via Alembic.
- Frontend: minimal server-served page at `/` using static assets in `app/web/`:
  - `app/web/index.html`
  - `app/web/styles.css`
  - `app/web/app.js`

## What Exists
- Core API + health endpoint (`GET /api/v1/health`).
- Session auth endpoints:
  - `POST /api/v1/session/login`
  - `DELETE /api/v1/session/logout`
  - `GET /api/v1/session/me`
- API key auth mode support via settings (`disabled`, `write`, `all`).
- Domain endpoints:
  - users
  - media items
  - watch events
  - shows + show progress
  - import batches + import errors
  - watch-event import endpoint(s)
- Legacy-source import script:
  - `python -m app.scripts.import_watch_events`
  - supports dry run + incremental resume
- Backfill script:
  - `python -m app.scripts.backfill_episode_shows`
- Tests:
  - unit tests + API tests in `tests/`
  - integration tests in `tests/integration/`
- Frontend smoke page supports login/logout/session check, show list, show detail, and progress table.

## What Is Not Implemented Yet (or only partial)
- Production-grade frontend UI (current page is intentionally minimal).
- Full watch-history browsing UI/API slice with richer filtering/pagination UX.
- Planned external sync integrations (metadata/webhooks/automation connectors) are not fully implemented.
- Hardening items likely still needed over time: broader integration coverage, stricter operational docs, and deployment polish.

## Naming Conventions and Guardrails
- Do not use the forbidden external service name in code identifiers/docs.
- Prefer `klug` for internal naming where applicable.
- Keep architecture boring and layered: API -> services -> repositories.
- Return schema DTOs from APIs, not raw ORM models.
- Keep timezone-aware UTC timestamps.
- Prefer UUID primary keys unless schema requires otherwise.

## Things Explicitly Avoided
- Introducing alternative frameworks/toolchains not in project standards.
- Destructive DB actions unless explicitly requested.
- Editing files in `/db` backup artifacts unless explicitly requested.
- Logging secrets.
- Broad/opaque exception handling.

## Working Agreements With User
- Commit workflow:
  - stage changes
  - run tests/checks as appropriate
  - run `git status` before commit
  - attempt commit when user requests commit
  - run `git status` after commit attempt so hook failures can be pasted verbatim
  - show `git log -1 --oneline` after successful commit
  - never run `git push` (user handles push)
- If pre-commit/hooks fail, report exact failure and wait for user-provided output if needed.

## Rehydration Checklist After Context Compaction
1. Read `AGENTS.md`.
2. Read this file (`PROJECT_CONTEXT.md`).
3. Check current branch and working tree:
   - `git status --short`
   - `git log -1 --oneline`
4. Confirm latest app surface quickly:
   - `README.md`
   - `app/main.py`
   - `app/api/`
   - `app/web/`
5. Before edits, restate planned files and run a small verification loop (`ruff`, `pytest`, or targeted smoke run).

## Canonical Dev Commands
- Run API: `uv run uvicorn app.main:app --reload`
- Run tests: `uv run pytest -q`
- Run lint: `uv run ruff check app tests`
- Legacy import:
  - `uv run python -m app.scripts.import_watch_events ...`
- Backfill:
  - `uv run python -m app.scripts.backfill_episode_shows --dry-run`

## Notes to Keep Updated
- Update this file whenever:
  - new endpoint groups are added
  - auth behavior changes
  - scripts/import behavior changes
  - workflow agreements with user change
