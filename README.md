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
- Config wiring via `pydantic-settings`
- SQLAlchemy engine/session module scaffold

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

3. Run API:
```bash
uv run uvicorn app.main:app --reload
```

4. Run tests:
```bash
uv run pytest -q
```

5. Run integration tests (PostgreSQL):
```bash
KLUG_TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/klug_media_test uv run pytest -q tests/integration
```

6. Run legacy-source watch-event import script:
```bash
uv run python -m app.scripts.import_watch_events --input ./path/to/export.json --mode bootstrap
```

Dry run example:
```bash
uv run python -m app.scripts.import_watch_events --input ./path/to/export.csv --mode incremental --dry-run
```

Incremental resume example:
```bash
uv run python -m app.scripts.import_watch_events --input ./path/to/export.csv --mode incremental --resume-from-latest
```
