FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY . .

RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"
