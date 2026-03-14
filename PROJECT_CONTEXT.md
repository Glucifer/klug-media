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
  - watch-event import endpoint(s), including upload route
- Import upload endpoint:
  - `POST /api/v1/imports/watch-events/legacy-source/upload`
  - accepts JSON/CSV multipart uploads
  - supports `input_schema`, `mode`, `dry_run`, `resume_from_latest`
  - enforces max size via `KLUG_IMPORT_UPLOAD_MAX_MB` (default 25 MB)
- Kodi playback ingestion endpoints:
  - `POST /api/v1/webhooks/kodi/events`
  - `POST /api/v1/webhooks/kodi/scrobble`
  - `GET /api/v1/playback-events`
  - raw-ish playback events are now persisted before watch-event decisions are made
  - current decision engine creates watch events for explicit `scrobble` events and high-progress `stop` events
  - playback-event visibility is available through a filtered read API for debugging collector input and scrobble decisions
- Legacy export import script:
  - `python -m app.scripts.import_watch_events`
  - supports dry run + incremental resume
- Backfill script:
  - `python -m app.scripts.backfill_episode_shows`
- Tests:
  - unit tests + API tests in `tests/`
  - integration tests in `tests/integration/`
- Import integration coverage exists for upload dry-run path.
- Frontend page (`/`) now includes:
  - session login/logout and auth status
  - ops strip (API health, auth mode, session state, last refresh)
  - watch history table with pagination/filtering
  - import runner (file upload + mode/dry-run/resume options)
  - cursor visibility (`cursor_before`, `cursor_after`, local last cursor)
  - import batch history with status filter (persisted)
  - import batch detail panel
  - import error drilldown + JSON export
  - import batch detail JSON copy action
  - “reuse settings” from prior import batches

## What Is Not Implemented Yet (or only partial)
- Production-grade frontend UI (current page is intentionally minimal).
- Full watch-history browsing UX polish (sorting/search/column customization, richer metadata views).
- Planned external sync integrations (metadata/webhooks/automation connectors) are not fully implemented.
- Scrobbler pipeline is only partially implemented: Kodi/Node-RED ingestion now exists, but richer session/resume handling and additional playback sources still need work.
- Hardening items likely still needed over time: broader integration coverage, stricter operational docs, and deployment polish.

## Naming Conventions and Guardrails
- Do not use the forbidden external service name in app/internal identifiers, package names, or internal architecture docs.
- Exception: the external service name may be used when describing import compatibility with an external export/source format.
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
- This file can include short current-status notes that help resume work after context loss, but avoid stale tool-specific assumptions when possible.
- Commit workflow:
  - stage changes
  - run tests/checks as appropriate
  - run `git status` before commit
  - attempt commit when user requests commit
  - run `git status` after commit attempt so hook failures can be pasted verbatim
  - show `git log -1 --oneline` after successful commit
- If pre-commit/hooks fail, report exact failure and wait for user-provided output if needed.

## Current Working Context
- Development environment is Windows-native using the Codex desktop app and `uv`.
- Prefer guidance that remains valid across sessions; update temporary goal notes when they materially change.
- If adding temporary session notes here, keep them short and remove or refresh them once they become stale.

## 🛠 Status Dashboard
- [x] Backend Core (FastAPI)
- [x] Auth (Session-based)
- [/] Import Logic (Watch-events - 80% complete)
- [ ] Production UI (Minimal state)
- [ ] External Metadata Sync (Planned)

## Canonical Dev Commands
- Run API: `uv run uvicorn app.main:app --reload`
- Run tests: `uv run pytest -q`
- Run lint: `uv run ruff check app tests`
- Run integration tests (PowerShell): `$env:KLUG_TEST_DATABASE_URL="..."; uv run pytest -q tests/integration`
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
