# Klug Media

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

## Local Development

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
