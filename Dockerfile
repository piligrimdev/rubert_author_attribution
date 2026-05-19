# syntax=docker/dockerfile:1
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.1.3 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY src/api/pyproject.cpu.toml ./pyproject.toml

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --only main --no-root --no-ansi \
    && find /app/.venv -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true \
    && find /app/.venv -name '*.pyc' -delete

# spacy model installs as a pip package into .venv, so it's included in the venv copy
RUN --mount=type=cache,target=/root/.cache/pip \
    .venv/bin/python -m spacy download ru_core_news_lg

# nltk data goes to a separate directory
RUN .venv/bin/python -m nltk.downloader -d /app/nltk_data punkt punkt_tab stopwords


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    NLTK_DATA=/app/nltk_data

WORKDIR /app/src/api

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/nltk_data /app/nltk_data
COPY src/api ./

EXPOSE 8080

CMD ["python", "run.py"]
