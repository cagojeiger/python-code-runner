# Python Code Runner

FastAPI 기반의 Python 코드 샌드박스 예시 프로젝트입니다. 사용자가 전송한 Python 코드를 안전하게(`exec`) 실행하고 출력(표준 출력)을 반환합니다. 금지된 모듈과 함수(`os`, `sys`, `eval`, `exec` 등)를 AST 파싱을 통해 탐지하고, 발견 시 예외를 발생시키도록 구성되었습니다.

---

## 1. 실행 방법

### 1.1 로컬 실행 (Poetry)

#### 1.1.1 레포지토리 클론
```bash
git clone https://github.com/your-username/python-code-runner.git
cd python-code-runner
```

#### 1.1.2 Poetry로 의존성 설치
```bash
poetry install
```

#### 1.1.3 개발 서버 실행
```bash
poetry run uvicorn app.main:app --reload
```
- 브라우저에서 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)로 API 문서 확인 가능

### 1.2 Docker 사용

#### 1.2.1 도커 이미지 빌드
```bash
docker build -t python-code-runner:latest .
```

#### 1.2.2 컨테이너 실행
```bash
docker run -p 8000:8000 python-code-runner:latest
```

#### 1.2.3 접속
- [http://localhost:8000/v1/execute](http://localhost:8000/v1/execute)

---

## 2. 테스트

### 2.1 테스트 코드 위치
- `tests/test_execute.py`

### 2.2 테스트 실행
```bash
poetry run pytest
```

---

## 3. 린트 및 포맷팅

이 프로젝트는 `flake8`, `black`, `isort` 등을 Poetry dev-dependencies로 설정해둘 수 있습니다.

### 3.1 Flake8 검사
```bash
poetry run flake8 .
```
- `.flake8` 설정 파일(`max-line-length = 88`, `ignore = E501` 등)에 따라 검사

### 3.2 Black(코드 포매팅)
```bash
poetry run black .
```

### 3.3 isort(임포트 순서 정리)
```bash
poetry run isort .
```
- 위 명령어는 `pyproject.toml` 내 설정에 따라 달라질 수 있음

---

## 4. API 사용 예시

### 4.1 요청
```bash
curl -X POST http://127.0.0.1:8000/v1/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"print(\"Hello Sandbox\")"}'
```

### 4.2 응답
```json
{
  "result": "Hello Sandbox\n"
}
```

- 금지된 모듈/함수를 사용하면 HTTP 400과 함께 다음과 같은 응답이 반환됩니다:
```json
{
  "error_type": "security",
  "detail": "...",
  "forbidden_item": "..."
}
```

---
