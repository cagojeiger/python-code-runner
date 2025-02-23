# ---------------------
# 1단계: 빌드 스테이지
# ---------------------
FROM python:3.11-bullseye AS builder

RUN apt-get update && apt-get install -y curl build-essential && apt-get clean

ENV POETRY_VERSION=1.5.1
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"
WORKDIR /app

COPY pyproject.toml poetry.lock ./

# Poetry 설정 변경 - 가상환경을 프로젝트 디렉토리 내에 생성
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-root --no-interaction --no-ansi

COPY app/ app/

# ---------------------
# 2단계: 런타임 스테이지
# ---------------------
FROM python:3.11-bullseye

# 비root 사용자 생성 (42000번 사용)
RUN groupadd -g 42000 appuser && \
    useradd -u 42000 -g appuser -s /bin/bash -m appuser

WORKDIR /app

# 필요한 디렉토리 생성 및 권한 설정
RUN mkdir -p /app && chown -R appuser:appuser /app

# 빌더 스테이지에서 필요한 파일들만 복사
COPY --from=builder --chown=appuser:appuser /app /app

# 환경 변수 설정 - Poetry 가상환경 경로 명시적 지정
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 사용자 전환
USER appuser

# uvicorn 포트
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]