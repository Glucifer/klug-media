# AGENTS.md — Klug Media (Codex Instructions)

You are an AI coding agent working in this repository. Follow these rules strictly.

## 1) Project goal
Build a self-hosted media tracking app (“Klug Media”) with a Python backend.
Optimize for correctness, maintainability, and incremental delivery.

## 2) Authoritative tech stack
- Python: 3.12+
- Web framework: FastAPI
- Server: uvicorn
- Dependency manager: uv
- Database: PostgreSQL
- ORM: SQLAlchemy 2.x (2.0 style)
- Migrations: Alembic
- Data validation / settings: Pydantic v2 + pydantic-settings
- HTTP client: httpx
- Testing: pytest (add pytest-asyncio only if needed)

Do NOT introduce alternative frameworks/tools (e.g., Django, Prisma, Tortoise, asyncpg-only, etc.)
unless explicitly asked.

## 3) Naming + repo boundaries
- Do NOT use the word “trakt” anywhere in code, identifiers, packages, or docs.
- Prefer “klug” for internal identifiers (schemas, app names, env vars).
- Treat `/db` as read-only unless explicitly instructed.
  - The schema backup file in `/db` is a source artifact. Do not edit/format/rename it.

## 4) Coding standards
- Be explicit and readable. Avoid cleverness.
- Use type hints everywhere for public functions and important internals.
- Keep modules small and focused.
- Avoid broad exception catches; handle expected failure modes cleanly.
- Log useful context; do not log secrets.

### Formatting & linting
- If the repo includes ruff/black/etc., follow it.
- Otherwise: keep formatting clean and consistent; do not reformat unrelated files.

## 5) Architecture conventions (preferred layout)
Keep the backend modular and boring (boring is good):

- `app/main.py` — FastAPI app factory + router mounting
- `app/api/` — routers (thin endpoints only)
- `app/core/` — settings, logging, constants, utilities
- `app/db/`
  - `session.py` (engine + sessionmaker)
  - `models/` (SQLAlchemy ORM models)
  - `migrations/` (Alembic)
- `app/schemas/` — Pydantic v2 request/response DTOs
- `app/services/` — business logic (imports/sync/jobs), no FastAPI dependency
- `app/repositories/` — optional: DB query layer if it helps keep services clean

Rules:
- Endpoints call services.
- Services call repositories/DB helpers.
- DB models are not returned directly from API responses; map to Pydantic schemas.

## 6) Database rules
- PostgreSQL is the source of truth; prefer constraints in the DB (FKs, unique, checks).
- Use timezone-aware timestamps in UTC.
- Prefer UUID primary keys unless the existing schema dictates otherwise.
- For SQLAlchemy 2.x:
  - Use `Mapped[]` typing and `mapped_column()`
  - Use `select()` + session.execute patterns
- Avoid implicit autocommit behavior; use explicit transactions.

## 7) Agent safety + workflow rules
- Before large edits: summarize the plan and list files to change.
- Keep diffs small:
  - If a change is > ~300 lines, split into steps/commits.
- Never delete data, drop tables, or do destructive migrations unless explicitly instructed.
- When running commands, state exactly what you ran and why.
- Prefer tests or a quick “smoke run” for verification.

## 8) Definition of done
A task is “done” only when:
- The app runs locally with documented commands, OR tests pass for that unit.
- New endpoints have minimal request/response Pydantic models.
- Errors are handled cleanly (no raw stack traces to users).
- New config values are documented (README or `.env.example`).
- Provide a short summary + how to verify.

## 9) Local dev commands (uv)
Assume a `.venv` in the repo root.

- Create venv:
  - `uv venv`
- Install deps (if requirements exist):
  - `uv pip install -r requirements.txt`
- Add a dependency:
  - `uv pip install <package>`
  - (then update requirements via `uv pip freeze > requirements.txt` if this repo uses requirements files)
- Run API:
  - `uv run uvicorn app.main:app --reload`
- Tests:
  - `uv run pytest -q`

If the repo uses `pyproject.toml` + locked deps, follow that instead of requirements.txt.

## 10) Communication style
- Be concise and specific.
- If something is ambiguous, make a reasonable assumption and state it.
- For each new file: give a one-line purpose explanation.
