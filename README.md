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
- One-time Trakt import workflow

## Local Development (Contributor/Personal Use)

1. Create environment:
```bash
uv venv --python 3.12
```

2. Install dependencies:
```bash
uv sync
```

3. Configure optional API auth:
```bash
export KLUG_API_KEY=replace-with-long-random-value
export KLUG_API_AUTH_MODE=write
```

`KLUG_API_AUTH_MODE` options:
- `disabled`: no API key checks
- `write`: require `X-API-Key` on write methods (`POST/PUT/PATCH/DELETE`)
- `all`: require `X-API-Key` on all routed endpoints

If `KLUG_API_KEY` is unset, requests are allowed (local dev convenience).

4. Run API:
```bash
uv run uvicorn app.main:app --reload
```

5. Run tests:
```bash
uv run pytest -q
```

6. Run integration tests (PostgreSQL):
```bash
KLUG_TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/klug_media_test uv run pytest -q tests/integration
```

7. Run legacy-source watch-event import script:
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
