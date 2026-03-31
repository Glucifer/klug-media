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

Phase 1 backend scaffolding is in progress.
The repository currently includes:

- FastAPI app entrypoint
- Versioned API prefix (`/api/v1`)
- Health endpoint (`GET /api/v1/health`)
- Import endpoints (`/api/v1/imports/*`)
- Users, media items, watch events, and shows endpoints
- Config wiring via `pydantic-settings`
- SQLAlchemy engine/session module
- Alembic migrations through `0004_align_show_progress_view_with_backup`

## Architecture Direction

- `app/main.py` for app factory and router mounting
- `app/api/` for thin endpoints
- `app/services/` for business logic
- `app/db/` for database session and models
- `app/schemas/` for request/response DTOs

## Planned Integrations

- TMDB metadata sync
- Jellyfin webhook sync
- Radarr/Sonarr import
- One-time external watch-history export import workflow

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

3. Configure optional API auth (PowerShell):
```powershell
$env:KLUG_API_KEY="replace-with-long-random-value"
$env:KLUG_API_AUTH_MODE="write"
$env:KLUG_SESSION_PASSWORD="replace-with-login-password"
$env:KLUG_SESSION_SECRET="replace-with-session-signing-secret"
$env:KLUG_IMPORT_UPLOAD_MAX_MB="25"
$env:KLUG_SCROBBLE_MIN_PROGRESS_PERCENT="90"
$env:KLUG_SCROBBLE_MIN_COMPLETION_RATIO="0.90"
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

4. Run API:
```bash
uv run uvicorn app.main:app --reload
```

5. Run tests:
```bash
uv run pytest -q
```

6. Run integration tests (PostgreSQL, PowerShell):
```powershell
$env:KLUG_TEST_DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/klug_media_test"
uv run pytest -q tests/integration
```

7. Run legacy export watch-event import script:
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

8. Backfill episode `show_id` links for older data:
```bash
uv run python -m app.scripts.backfill_episode_shows --dry-run
```

Write mode example:
```bash
uv run python -m app.scripts.backfill_episode_shows
```

## API Smoke Checks

With server running on `http://127.0.0.1:8000`:

```bash
curl http://127.0.0.1:8000/api/v1/health
curl -X POST http://127.0.0.1:8000/api/v1/session/login -H "Content-Type: application/json" -d '{"password":"<session-password>"}'
curl http://127.0.0.1:8000/api/v1/shows
curl http://127.0.0.1:8000/api/v1/shows/progress
curl "http://127.0.0.1:8000/api/v1/shows/progress?user_id=<your-user-uuid>"
curl http://127.0.0.1:8000/api/v1/shows/<show-uuid>
curl "http://127.0.0.1:8000/api/v1/shows/<show-uuid>?user_id=<your-user-uuid>"
curl -X POST http://127.0.0.1:8000/api/v1/users -H "Content-Type: application/json" -H "X-API-Key: <your-api-key>" -d '{"username":"alice"}'
```

Interactive docs:

```text
http://127.0.0.1:8000/docs
```

Minimal frontend page:

```text
http://127.0.0.1:8000/
```

The page uses:
- `POST /api/v1/session/login`
- `GET /api/v1/session/me`
- `DELETE /api/v1/session/logout`
- `GET /api/v1/shows`
- `GET /api/v1/shows/{show_id}`
