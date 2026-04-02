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
  - stop-event thresholds are configurable with `KLUG_SCROBBLE_MIN_PROGRESS_PERCENT` and `KLUG_SCROBBLE_MIN_COMPLETION_RATIO`
  - playback-event visibility is available through a filtered read API for debugging collector input and scrobble decisions
  - a first Node-RED collector flow now exists in the live `Kodi Scrobbler` tab and is exported in `docs/node_red/kodi_scrobbler_flow.json`
- Metadata enrichment:
  - TMDB-first enrichment queue is now modeled on `media_item`
  - operator endpoints exist under `/api/v1/metadata-enrichment/*`
  - enrichment is ID-first and uses TMDB `/find` for Kodi-style `imdb_id` and `tvdb_id` resolution
  - raw provider payloads are cached in `app.tmdb_metadata_cache`
  - queue behavior is now operator-focused: `Process Pending` only handles `pending` rows, failed/skipped rows require explicit retry
  - `metadata_updated_at` now represents successful metadata writes only, while `enrichment_attempted_at` tracks all attempts
  - operator responses now include normalized failure codes and suggested next actions
- Watch-event corrections:
  - `watch_event` now supports lightweight correction metadata (`updated_*`) and soft delete fields (`is_deleted`, `deleted_*`)
  - correction endpoints now exist under `/api/v1/watch-events/{watch_id}/delete|restore|correct`
  - rough manual watch entry now exists under `POST /api/v1/watch-events/manual`
  - v1 manual movie entry resolves by TMDB movie id
  - v1 manual episode entry resolves by TMDB show id + season + episode; an optional TMDB episode id can be supplied as a validation check, but TMDB does not support episode-detail lookup by episode id alone
  - default watch history and show-progress reads now exclude soft-deleted watch events
  - completed, unrated watch events can now be listed and rated through `/api/v1/watch-events/unrated` and `/api/v1/watch-events/{watch_id}/rate`
  - watch-specific version and runtime overrides can now be set manually through `/api/v1/watch-events/{watch_id}/version`
- Horrorfest overlay:
  - Horrorfest is now modeled as a dedicated annual overlay on top of canonical `watch_event` rows
  - yearly windows are configured through `app.horrorfest_year`
  - qualifying completed movie watches now auto-create ordered `app.horrorfest_entry` rows for live, import, and manual watch creation paths
  - operator endpoints now exist under `/api/v1/horrorfest/*` for year config, listing, include/remove/restore, and manual reordering
  - watch-event list responses now expose `horrorfest_year`, `horrorfest_watch_order`, and `is_horrorfest_watch`
  - legacy import rows can now carry optional `horrorfest_year` and `horrorfest_watch_order` values so historical annual order can be preserved during import
- Dashboard stats:
  - query-backed stats endpoints now exist under `/api/v1/stats/*`
  - first endpoints are `summary`, `monthly`, and `horrorfest`
  - summary stats now cover active/completed watches, rewatches, movies vs episodes, total watch time, average rating, and unrated backlog
  - monthly stats are grouped by each watch's user-local year/month rather than UTC
  - Horrorfest annual stats summarize active `horrorfest_entry` rows without creating a separate analytics store
- Legacy export import script:
  - `python -m app.scripts.import_watch_events`
  - supports dry run + incremental resume
  - legacy JSON imports still treat naive timestamps as UTC, but flat CSV uploads/imports now interpret naive `watched_at` values in the target user's timezone before normalizing to UTC
- Preserved Horrorfest overlay import script:
  - `python -m app.scripts.import_horrorfest`
  - applies legacy Horrorfest year/order plus preserved rating/version metadata onto already-imported canonical `watch_event` rows
  - matches imported watches primarily by preserved `trakt_log_id` stored as `watch_event.source_event_id`, with TMDB/local-date fallback only when needed
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
  - watch history detail/editor panel for safe corrections and restore
  - watch history version/runtime override controls for per-watch movie cuts
  - recently watched, unrated queue with 1-10 rating actions
  - Horrorfest year configuration and ordered entry operator panel
  - compact stats section with summary cards, monthly rollups, and Horrorfest annual summaries
  - import runner (file upload + mode/dry-run/resume options)
  - manual watch add form for off-Kodi viewing
  - cursor visibility (`cursor_before`, `cursor_after`, local last cursor)
  - import batch history with status filter (persisted)
  - import batch detail panel
  - import error drilldown + JSON export
  - import batch detail JSON copy action
  - “reuse settings” from prior import batches
  - scrobble activity operator view
  - metadata enrichment operator queue with process/retry actions

## What Is Not Implemented Yet (or only partial)
- Production-grade frontend UI (current page is intentionally minimal).
- Full watch-history browsing UX polish (sorting/search/column customization, richer metadata views).
- Planned external sync integrations (metadata/webhooks/automation connectors) are not fully implemented.
- Metadata enrichment exists in a first operator-focused form, but there is not yet a polished end-user metadata UI.
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
- Local network topology for current dev setup:
  - Klug API runs on the Windows host at `172.20.1.10`
  - PostgreSQL, Home Assistant, and Node-RED run on `172.20.1.20`
  - Preferred dev bind/port for Klug is `0.0.0.0:8010` so container-hosted services can reach it without colliding with an existing service on port `8000`
- Node-RED collector notes:
  - Flow tab: `Kodi Scrobbler`
  - The current flow reads flow env vars first, then falls back to Node-RED global values for:
    - `KLUG_API_BASE_URL` (for current dev setup, use `http://172.20.1.10:8010`)
    - `KLUG_API_KEY`
    - `KLUG_USER_ID`
  - The current collector listens to `media_player.kodi` state changes and also polls lightweight progress every 5 minutes while Kodi is playing.
  - Live verification now succeeds end to end: Kodi play/stop events persist to `playback_event`, high-progress stop events create `watch_event`, and external IDs such as `tvdb_id` are promoted from Kodi payloads for later enrichment.
  - The deployed flow uses a native Node-RED `http request` node for delivery to Klug rather than `fetch` inside a function node.

## 🛠 Status Dashboard
- [x] Backend Core (FastAPI)
- [x] Auth (Session-based)
- [/] Import Logic (Watch-events - 80% complete)
- [ ] Production UI (Minimal state)
- [/] External Metadata Sync (TMDB-first operator queue in place)

## Canonical Dev Commands
- Run API: `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8010`
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

