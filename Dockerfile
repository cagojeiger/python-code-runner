# ---------------------
# 1단계: 빌드 스테이지
# ---------------------
FROM python:3.11-slim as builder

RUN apt-get update && apt-get install -y curl build-essential && apt-get clean

ENV POETRY_VERSION=1.5.1
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"
WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction --no-ansi

COPY app/ app/

# ---------------------
# 2단계: 런타임 스테이지
# ---------------------
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# uvicorn 포트
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]