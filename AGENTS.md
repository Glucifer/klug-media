# AGENTS.md — Klug Media (Codex Instructions)

You are an AI coding agent working in this repository. Follow these rules strictly.

## 1) Goals and scope
- Build a self-hosted media tracking app ("Klug Media") with a Python backend.
- Prioritize correctness, maintainability, and small incremental commits.
- Default to implementing the smallest working slice, then iterate.

## 2) Tech stack (authoritative)
- Language: Python 3.12+
- Web framework: FastAPI
- ASGI server: uvicorn
- Database: PostgreSQL
- ORM: SQLAlchemy 2.x (typed) OR SQLModel (pick one and stick to it)
- Migrations: Alembic
- Validation/settings: Pydantic v2 + pydantic-settings
- HTTP client: httpx
- Testing: pytest (+ pytest-asyncio if needed)

If the repo already contains tooling choices (poetry/uv/pip-tools/ruff/etc.), match the repo.
Do NOT introduce alternative stacks unless explicitly asked.

## 3) Repository boundaries / do-not-touch
- Do not modify files in `/db` except when explicitly instructed.
  - The schema backup file is a source artifact; treat it as read-only.
- Do not rename the project or introduce "trakt" naming anywhere.
  - Use "klug" for internal identifiers where needed.

## 4) Coding standards
- Prefer explicit, readable code over cleverness.
- Use type hints everywhere (public functions, models, DB access).
- Keep functions small. Avoid huge modules.
- Add docstrings to non-trivial functions and modules.

### Formatting & linting
- Use ruff for linting/formatting if present; otherwise keep formatting PEP8-clean.
- Do not reformat unrelated files in the same change.

## 5) Architecture conventions
- Keep the app modular:
  - `app/main.py` for FastAPI app creation
  - `app/api/` for routers/endpoints
  - `app/core/` for config, logging, security helpers
  - `app/db/` for engine/session, models, migrations hooks
  - `app/services/` for business logic (importers/sync/jobs)
  - `app/schemas/` for Pydantic request/response models
- Separate concerns:
  - Endpoints should be thin.
  - Business logic goes in `services/`.
  - DB access stays in `db/` or repository modules.

## 6) Database rules
- PostgreSQL is the source of truth.
- Enforce constraints in the DB when possible (FKs, uniques).
- Prefer UUID primary keys unless schema requires otherwise.
- All timestamps should be timezone-aware (UTC).

## 7) Safety rules for agent actions
- Before making large edits, summarize the plan and the files you will change.
- Prefer small diffs. If changes exceed ~300 lines, break into multiple steps.
- When running commands, explain what you are running and why.
- Never delete data or drop tables unless explicitly instructed.

## 8) “Done” definition for a task
A task is only "done" when:
- Code runs (or tests pass) locally with the documented commands.
- New endpoints include minimal request/response models.
- Errors are handled cleanly (no bare exceptions).
- Any new config values are documented in README (or a sample env file).
- You provide a short summary of what changed and how to verify it.

## 9) Default commands (update if repo differs)
- Create venv: `python -m venv .venv`
- Install: `pip install -r requirements.txt` (or use poetry/uv if configured)
- Run API: `uvicorn app.main:app --reload`
- Tests: `pytest -q`

## 10) Communication style
- Be concise and explicit.
- If a requirement is unclear, make a reasonable assumption and state it.
- When you add a new file, explain its purpose in one sentence.
