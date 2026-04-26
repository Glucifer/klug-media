#!/usr/bin/env sh
set -eu

if [ "${KLUG_RUN_MIGRATIONS:-true}" = "true" ] || [ "${KLUG_RUN_MIGRATIONS:-true}" = "1" ]; then
    alembic upgrade head
fi

exec uvicorn app.main:app \
    --host "${KLUG_HOST:-0.0.0.0}" \
    --port "${KLUG_PORT:-8010}"
