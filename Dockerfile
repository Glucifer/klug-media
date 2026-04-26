FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY alembic.ini ./
COPY app ./app
COPY docker ./docker

RUN uv sync --frozen --no-dev && \
    useradd --create-home --shell /usr/sbin/nologin klug && \
    chown -R klug:klug /app

USER klug

EXPOSE 8010

ENTRYPOINT ["sh", "/app/docker/entrypoint.sh"]
