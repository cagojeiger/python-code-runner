# Python Code Runner

FastAPI 기반의 Python 코드 샌드박스 예시 프로젝트입니다. 사용자가 전송한 Python 코드를 안전하게(`exec`) 실행하고 출력(표준 출력)을 반환합니다. 금지된 모듈과 함수(`os`, `sys`, `eval`, `exec` 등)를 AST 파싱을 통해 탐지하고, 발견 시 예외를 발생시키도록 구성되었습니다.

---

## 1. 주요 구조

```
app/
├─ api/
│  └─ v1/
│      └─ execute.py         # FastAPI 라우터 (POST /v1/execute)
├─ core/
│  ├─ config.py              # 환경 설정(현재 비어있음)
│  ├─ exceptions.py          # 샌드박스 예외 정의 (SecurityError, SyntaxError 등)
│  ├─ handlers.py            # FastAPI 예외 핸들러 등록
│  ├─ logging.py             # structlog 로깅 설정
│  ├─ middleware.py          # 요청 로깅 미들웨어
│  └─ security.py            # AST 파싱으로 금지 패턴 검사
├─ schemas/
│  └─ execution.py           # Pydantic 스키마(CodeRequest, ExecuteResponse, ErrorResponse)
├─ services/
│  └─ code_execution.py      # 비즈니스 로직(코드 실행, stdout 캡처 등)
├─ main.py                   # FastAPI 엔트리포인트(라우터, 미들웨어, 예외 핸들러 등록)
```

- **`api/`**: FastAPI 라우트 정의 (HTTP 경로/메서드)
- **`core/`**: 공통/핵심 로직 (보안 검사, 예외, 로깅, 미들웨어 등)
- **`schemas/`**: Pydantic 기반 요청/응답 모델(DTO)
- **`services/`**: 비즈니스 로직 (실행 로직, 보안 검사 호출 등)
- **`main.py`**: 앱 설정 진입점 (라우트/핸들러 등록)

---

## 2. 실행 방법

### 2.1 로컬 실행 (Poetry)

#### 2.1.1 레포지토리 클론
```bash
git clone https://github.com/your-username/python-code-runner.git
cd python-code-runner
```

#### 2.1.2 Poetry로 의존성 설치
```bash
poetry install
```

#### 2.1.3 개발 서버 실행
```bash
poetry run uvicorn app.main:app --reload
```
- 브라우저에서 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)로 API 문서 확인 가능

### 2.2 Docker 사용

#### 2.2.1 도커 이미지 빌드
```bash
docker build -t python-code-runner:latest .
```

#### 2.2.2 컨테이너 실행
```bash
docker run -p 8000:8000 python-code-runner:latest
```

#### 2.2.3 접속
- [http://localhost:8000/v1/execute](http://localhost:8000/v1/execute)

---

## 3. 테스트

### 3.1 테스트 코드 위치
- `tests/test_execute.py`

### 3.2 테스트 실행
```bash
poetry run pytest
```

---

## 4. 린트 및 포맷팅

이 프로젝트는 `flake8`, `black`, `isort` 등을 Poetry dev-dependencies로 설정해둘 수 있습니다.

### 4.1 Flake8 검사
```bash
poetry run flake8 .
```
- `.flake8` 설정 파일(`max-line-length = 88`, `ignore = E501` 등)에 따라 검사

### 4.2 Black(코드 포매팅)
```bash
poetry run black .
```

### 4.3 isort(임포트 순서 정리)
```bash
poetry run isort .
```
- 위 명령어는 `pyproject.toml` 내 설정에 따라 달라질 수 있음

---

## 5. API 사용 예시

### 5.1 요청
```bash
curl -X POST http://127.0.0.1:8000/v1/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"print(\"Hello Sandbox\")"}'
```

### 5.2 응답
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
