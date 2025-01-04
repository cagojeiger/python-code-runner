# Testing

이 문서는 프로젝트의 테스트 전략과 테스트 코드 구조를 안내합니다. 
어떤 테스트 프레임워크를 사용하고, 어떻게 작성/실행/관리하는지 확인할 수 있습니다.

## 목차
1. [개요 (Overview)](#개요-overview)
2. [테스트 프레임워크 (Test Framework)](#테스트-프레임워크-test-framework)
3. [테스트 구조 (Directory & File Structure)](#테스트-구조-directory--file-structure)
4. [테스트 실행 방법 (How to Run Tests)](#테스트-실행-방법-how-to-run-tests)
5. [Mocking & Fixture (테스트 보조 기법)](#mocking--fixture-테스트-보조-기법)
6. [커버리지 (Coverage)](#커버리지-coverage)

---

## 1. 개요 (Overview)

- **목적**: 프로젝트 기능을 변경하거나 확장할 때, 기존 로직이 깨지지 않았음을 보장
- **원칙**: 테스트 코드는 최대한 가독성 높게, 독립적으로 작성
- **전략**:
  1. **단위 테스트 (Unit Tests)** – 함수/메서드 단위
  2. **통합 테스트 (Integration Tests)** – DB, 외부 서비스(Kafka, Redis 등) 통합 검증
  3. **API/엔드투엔드 테스트 (E2E)** – FastAPI 라우터를 직접 호출, 실제 시나리오 검증

---

## 2. 테스트 프레임워크 (Test Framework)

- **pytest**를 기본적으로 사용 (간결한 문법, 풍부한 플러그인, fixture 시스템 제공)
- (선택) unittest, nose2, behave(BDD) 등을 병행하거나, 팀 내 선호도에 따라 변경 가능

### 예:
```bash
pip install pytest
# 또는 poetry add --dev pytest
```

---

## 3. 테스트 구조 (Directory & File Structure)

### 일반적인 예시:
```plaintext
project/
 ├─ app/
 │   ├─ features/
 │   └─ core/
 ├─ tests/
 │   ├─ conftest.py             # pytest 전역 설정 & fixture
 │   ├─ features/
 │   │   ├─ code_execution/
 │   │   │   ├─ test_api.py
 │   │   │   ├─ test_services.py
 │   │   │   └─ ...
 │   │   └─ submissions/
 │   │       ├─ test_api.py
 │   │       ├─ test_services.py
 │   │       └─ ...
 │   └─ core/
 │       ├─ test_db.py
 │       ├─ test_security.py
 │       └─ ...
 └─ ...
```

1. **`tests/features/...`**: 기능별로 테스트 분류 (예: `code_execution`, `submissions` 등)
2. **`tests/core/...`**: 전역 로직(DB, 로깅, 보안 등) 테스트
3. **`conftest.py`**: pytest 특유의 fixture, 플러그인 설정, 공용 헬퍼 정의

**중요**: 테스트를 기능별로 나눠서 찾기 쉽게 배치합니다.

---

## 4. 테스트 실행 방법 (How to Run Tests)

1. **기본 명령** (pytest 예시):
   ```bash
   pytest
   ```
   - 프로젝트 루트에서 실행 시, `tests/` 폴더를 자동으로 스캔
   - `test_*.py` 또는 `*_test.py` 파일을 찾아 테스트

2. **특정 파일/폴더 테스트**:
   ```bash
   pytest tests/features/code_execution/test_api.py
   ```

3. **테스트 패턴 매칭**:
   ```bash
   pytest -k "test_something"
   ```
   - `"test_something"` 문자열이 들어간 함수만 실행

4. **(선택)** Makefile이나 `run_tests.sh`를 만들어 빠른 실행 지원

---

## 5. Mocking & Fixture (테스트 보조 기법)

### 1. Fixture
- `conftest.py` 또는 각 테스트 모듈에 fixture 정의:

```python
@pytest.fixture
def sample_user():
    return {"username": "tester", "email": "test@example.com"}
```

### 2. Mocking
- 외부 시스템(Kafka, S3, SMTP 등)이나 I/O를 직접 호출하지 않도록 `unittest.mock` 또는 `pytest-mock` 활용:

```python
from unittest.mock import patch

@patch("app.features.code_execution.infrastructure.kafka.produce_event")
def test_run_code(mock_produce, sample_user):
    # mock_produce는 가짜 함수
    ...
```

### 3. Database 세팅
- 테스트 전/후로 DB를 비우거나 테스트 전용 DB 스키마를 설정하는 fixture 운용

---

## 6. 커버리지 (Coverage)

- `Coverage.py`(pytest-cov) 플러그인으로 테스트 커버리지 측정:

```bash
pip install pytest-cov
pytest --cov=app --cov-report=term-missing
```

### 결과 예시:
```plaintext
Name                                           Stmts   Miss  Cover
--------------------------------------------------------------
app/features/code_execution/services.py         50     10    80%
app/features/code_execution/api.py             30      3    90%
...
TOTAL                                          200     25    87%
```

- CI 파이프라인에서 커버리지 임계값(예: 80% 미만 시 빌드 실패) 설정 가능