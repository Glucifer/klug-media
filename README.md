# Klug Media

![Status: Personal Use Only](https://img.shields.io/badge/Status-Personal_Use_Only-red)
![Maintenance: Experimental](https://img.shields.io/badge/Maintenance-Experimental-orange)

> [!WARNING]
> **This is a personal hobby project, not a consumer product.**
>
> Klug Media is built specifically for my local home server environment (Unraid, PostgreSQL, Node-RED). It is currently under active, messy development. I am sharing the code for transparency and inspiration, but I do **not** provide support, installation guides, or guarantees that it will work for anyone else.
>
> **Non-goal:** this is not a supported drop-in replacement for any third-party tracking service.
> There are no releases, no migration guarantees, and no backward-compatibility promise.

Klug Media is a self-hosted media tracking and analytics platform.
The goal is complete ownership of watch history, metadata, analytics, and integrations.

## Current Stack

- Python 3.12+
- FastAPI + uvicorn
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- Pydantic v2 + pydantic-settings
- httpx
- pytest

## Project Status

Klug Media is now at a personal-use `v1` milestone.
The current system is usable for day-to-day tracking without direct database edits, with the intentionally minimal dashboard acting as the operator UI.

Core v1 workflows now include:

- full watch-history import from legacy JSON/CSV exports
- one-time Jellyfin collection snapshot import for owned movies/shows/episodes
- live Kodi scrobbling through Node-RED/Home Assistant
- manual watch entry for off-Kodi viewing
- TMDB-first metadata enrichment
- ratings and per-watch version/runtime overrides
- Horrorfest yearly overlay management
- manual watch correction and soft delete/restore
- basic dashboard stats, recent history, and operator troubleshooting views

The repository currently includes:

- FastAPI app entrypoint
- Versioned API prefix (`/api/v1`)
- Health endpoint (`GET /api/v1/health`)
- Import endpoints (`/api/v1/imports/*`)
- Collection browse endpoints (`/api/v1/collection/*`)
- Users, media items, watch events, and shows endpoints
- Manual watch entry endpoint for off-Kodi viewing
- Horrorfest year/entry endpoints for annual challenge tracking
- Stats endpoints for dashboard summaries and monthly/Horrorfest rollups
- Config wiring via `pydantic-settings`
- SQLAlchemy engine/session module
- Alembic migrations through `0014_add_collection_entry_table`

## Architecture Direction

- `app/main.py` for app factory and router mounting
- `app/api/` for thin endpoints
- `app/services/` for business logic
- `app/db/` for database session and models
- `app/schemas/` for request/response DTOs

## Planned / Post-v1 Integrations

- TMDB metadata sync
- Jellyfin webhook sync
- Radarr/Sonarr import
- One-time external watch-history export import workflow
- Horrorfest annual watch tracking and stats

## Naming Note

Internal app code, identifiers, and docs should use `klug` naming rather than third-party service branding.
An exception is allowed when documenting or handling one-time import of an external export format, where the external service name may be mentioned descriptively.

## Local Development (Contributor/Personal Use)

1. Create environment:
```bash
uv venv --python 3.12
```

2. Install dependencies:
```bash
uv sync
```

3. Copy `.env.example` to `.env` and replace `DATABASE_URL` with your real database host, user, password, and database name before starting the app.

4. Configure optional API auth (PowerShell):
```powershell
$env:KLUG_API_KEY="replace-with-long-random-value"
$env:KLUG_API_AUTH_MODE="write"
$env:KLUG_SESSION_PASSWORD="replace-with-login-password"
$env:KLUG_SESSION_SECRET="replace-with-session-signing-secret"
$env:KLUG_IMPORT_UPLOAD_MAX_MB="25"
$env:KLUG_SCROBBLE_MIN_PROGRESS_PERCENT="90"
$env:KLUG_SCROBBLE_MIN_COMPLETION_RATIO="0.90"
$env:KLUG_WATCH_COLLISION_WINDOW_SECONDS="300"
$env:KLUG_TMDB_API_KEY="replace-with-tmdb-api-key"
$env:KLUG_METADATA_ENRICHMENT_ENABLED="true"
$env:KLUG_METADATA_CACHE_TTL_HOURS="168"
$env:KLUG_JELLYFIN_BASE_URL="http://jellyfin-host:8096"
$env:KLUG_JELLYFIN_API_KEY="replace-with-jellyfin-api-key"
$env:KLUG_JELLYFIN_TIMEOUT_SECONDS="15"
```

`KLUG_API_AUTH_MODE` options:
- `disabled`: no API key checks
- `write`: require `X-API-Key` on write methods (`POST/PUT/PATCH/DELETE`)
- `all`: require `X-API-Key` on all routed endpoints

In `APP_ENV=dev`, if `KLUG_API_KEY` is unset and no session secret/password is configured, requests are allowed (local dev convenience).
In `APP_ENV=prod`, write requests fail closed and require a valid `X-API-Key` even if a session cookie is present.

Session auth endpoints:
- `POST /api/v1/session/login` with `{ "password": "<KLUG_SESSION_PASSWORD>" }`
- `DELETE /api/v1/session/logout`
- `GET /api/v1/session/me`

When logged in, a signed `klug_session` cookie can satisfy API auth checks (API key remains supported for scripts/admin usage).

Scrobbler threshold options:
- `KLUG_SCROBBLE_MIN_PROGRESS_PERCENT`: progress percent required for stop-event scrobbling when progress data is present
- `KLUG_SCROBBLE_MIN_COMPLETION_RATIO`: watched/total ratio required for stop-event scrobbling when duration data is used
- `KLUG_WATCH_COLLISION_WINDOW_SECONDS`: conservative matching window used to deduplicate import/live watch collisions into one final `watch_event`

Metadata enrichment options:
- `KLUG_TMDB_API_KEY`: TMDB API key used for async metadata enrichment and external-id lookups
- `KLUG_METADATA_ENRICHMENT_ENABLED`: enables the operator-driven TMDB enrichment queue
- `KLUG_METADATA_CACHE_TTL_HOURS`: cache lifetime for TMDB payloads stored in `app.tmdb_metadata_cache`

Jellyfin collection import options:
- `KLUG_JELLYFIN_BASE_URL`: Jellyfin server base URL used for collection snapshot reads
- `KLUG_JELLYFIN_API_KEY`: Jellyfin API key with read access to libraries and items
- `KLUG_JELLYFIN_TIMEOUT_SECONDS`: HTTP timeout for Jellyfin snapshot requests

5. Run API:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
```

In the previous Windows-native environment, Klug ran on the Windows host at `172.20.1.10:8010`.
That allowed Docker-hosted services on `172.20.1.20` such as Node-RED and Home Assistant to reach the API over the LAN.
For WSL or Dockerized deployment, replace these host examples with the container/host address exposed in that environment.

If Windows reserves `8010` after an OS update and you hit `WinError 10013`, run on `8210` instead:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8210
```

If you change the port, update the Node-RED/Home Assistant target URL to match.

6. Run tests:
```bash
uv run pytest -q
```

7. Run integration tests (PostgreSQL, PowerShell):
```powershell
$env:KLUG_TEST_DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/klug_media_test"
uv run pytest -q tests/integration
```

8. Run legacy export watch-event import script:
```bash
uv run python -m app.scripts.import_watch_events --input ./path/to/export.json --input-schema legacy_backup --user-id <your-user-uuid> --mode bootstrap
```

Dry run example:
```bash
uv run python -m app.scripts.import_watch_events --input ./path/to/export.csv --input-schema legacy_backup --user-id <your-user-uuid> --mode incremental --dry-run
```

Incremental resume example:
```bash
uv run python -m app.scripts.import_watch_events --input ./path/to/export.csv --input-schema legacy_backup --user-id <your-user-uuid> --mode incremental --resume-from-latest --error-report ./import_errors.json
```

9. Import preserved Horrorfest overlay data after canonical watch history is already imported:
```bash
uv run python -m app.scripts.import_horrorfest --input ./v_horrorfest_trakt_preserve_export.csv --user-id <your-user-uuid>
```

Dry run example:
```bash
uv run python -m app.scripts.import_horrorfest --input ./v_horrorfest_trakt_preserve_export.csv --user-id <your-user-uuid> --dry-run
```

Dry run with unmatched-row report:
```bash
uv run python -m app.scripts.import_horrorfest --input ./v_horrorfest_trakt_preserve_export.csv --user-id <your-user-uuid> --dry-run --error-report ./horrorfest_unmatched.json
```

10. Backfill episode `show_id` links for older data:
```bash
uv run python -m app.scripts.backfill_episode_shows --dry-run
```

Write mode example:
```bash
uv run python -m app.scripts.backfill_episode_shows
```

11. Run a Jellyfin collection snapshot import after configuring Jellyfin env vars:
```bash
curl -X POST http://172.20.1.10:8010/api/v1/imports/collection/jellyfin -H "Content-Type: application/json" -H "X-API-Key: <your-api-key>" -d '{"dry_run":true}'
```

Real import example:
```bash
curl -X POST http://172.20.1.10:8010/api/v1/imports/collection/jellyfin -H "Content-Type: application/json" -H "X-API-Key: <your-api-key>" -d '{}'
```

## API Smoke Checks

With the server running, replace the base URL below with the address for your current WSL/Docker environment:

```bash
curl http://172.20.1.10:8010/api/v1/health
curl -X POST http://172.20.1.10:8010/api/v1/session/login -H "Content-Type: application/json" -d '{"password":"<session-password>"}'
curl http://172.20.1.10:8010/api/v1/shows
curl http://172.20.1.10:8010/api/v1/collection/movies
curl http://172.20.1.10:8010/api/v1/collection/shows
curl http://172.20.1.10:8010/api/v1/collection/episodes
curl http://172.20.1.10:8010/api/v1/shows/progress
curl "http://172.20.1.10:8010/api/v1/shows/progress?user_id=<your-user-uuid>"
curl http://172.20.1.10:8010/api/v1/shows/<show-uuid>
curl "http://172.20.1.10:8010/api/v1/shows/<show-uuid>?user_id=<your-user-uuid>"
curl -X POST http://172.20.1.10:8010/api/v1/users -H "Content-Type: application/json" -H "X-API-Key: <your-api-key>" -d '{"username":"alice"}'
```

Interactive docs:

```text
http://172.20.1.10:8010/docs
```

Minimal frontend page:

```text
http://172.20.1.10:8010/
```

The page uses:
- `POST /api/v1/session/login`
- `GET /api/v1/session/me`
- `DELETE /api/v1/session/logout`
- `GET /api/v1/shows`
- `GET /api/v1/shows/{show_id}`
- `GET /api/v1/horrorfest/years`
- `GET /api/v1/horrorfest/years/{year}/entries`
- `GET /api/v1/stats/summary`
- `GET /api/v1/stats/monthly`
- `GET /api/v1/stats/horrorfest`
- `POST /api/v1/watch-events/manual`

## Manual Watch Entry

V1 manual entry is intentionally rough but usable from the existing dashboard or API:

- movies: supply a TMDB movie id
- episodes: supply a TMDB show id plus season and episode numbers
- optional TMDB episode id can be included as a validation check

Episode note: TMDB does not provide episode-detail lookup by episode id alone, so Klug uses the canonical local episode identity of `show_tmdb_id + season + episode`.

## Jellyfin Collection Import

Collection import is intentionally separate from watch history.

- Jellyfin is treated as the owned-library source of truth for movies, shows, and episodes
- Klug ignores Jellyfin watched flags, play counts, resume state, and other user playback fields
- snapshot reruns mark no-longer-present entries as missing instead of deleting them
- current collection browse lives under `/api/v1/collection/*`

Recommended cutover:

1. Run a dry-run collection import.
2. Run the real collection import.
3. Verify `/api/v1/collection/movies`, `/api/v1/collection/shows`, and `/api/v1/collection/episodes`.
4. Disable the Jellyfin plugin that writes external watch-state changes back into Jellyfin.

## V1 Notes

This `v1` milestone is focused on operational correctness, importability, and long-term personal use rather than polished browsing UX.

Current expectations:

- the dashboard is an operator/admin surface, not a consumer-ready frontend
- manual corrections are expected for some legacy-history edge cases
- Horrorfest imports may require curation of old historical rows where the original source data was incomplete or wrong
- TMDB enrichment is intentionally ID-first and avoids fuzzy title matching wherever possible
