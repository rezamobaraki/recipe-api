FROM python:3.14-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    DATA_DIR=/app/data \
    SQLITE_DB_PATH=/app/data/recipes.db

COPY pyproject.toml uv.lock ./

FROM base AS dev

RUN uv sync --frozen --no-install-project

COPY src src
COPY tests tests
COPY data data

RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

FROM base AS prod

RUN uv sync --frozen --no-install-project --no-dev

COPY src src
COPY data data

RUN uv sync --frozen --no-dev

RUN addgroup --system app && adduser --system --ingroup app app && \
    chown -R app:app /app

USER app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

EXPOSE 8000

CMD ["uvicorn", "src.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
