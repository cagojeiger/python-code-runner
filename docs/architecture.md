# Architecture

이 문서는 프로젝트의 전반적인 **아키텍처 구조**와 **설계 철학**을 설명합니다. 디렉토리 구조, 레이어(계층), 의존성 규칙 등을 한눈에 파악할 수 있도록 정리했습니다.

## 목차
1. [개요 (Overview)](#개요-overview)
2. [디렉토리 구조 (Directory Structure)](#디렉토리-구조-directory-structure)
3. [레이어와 의존성 규칙 (Layers & Dependency Rules)](#레이어와-의존성-규칙-layers--dependency-rules)
4. [기능(Feature) 기반 폴더 구성](#기능feature-기반-폴더-구성)
5. [도메인 로직과 인프라 분리](#도메인-로직과-인프라-분리)
6. [확장 포인트 & 향후 계획](#확장-포인트--향후-계획)

## 개요 (Overview)

이 프로젝트는 **FastAPI**를 기반으로 개발되며, "____ 기능"을 핵심으로 합니다.

**주요 목표**:
- 유지보수가 용이한 구조
- 초보자도 쉽게 이해할 수 있는 폴더 구성
- 기능 확장 시 충돌 최소화

아키텍처 스타일은 "**기능(Feature) 기반**" 디렉토리 + 필요한 부분에서 **레이어드 아키텍처** 아이디어를 차용해 설계했습니다.

## 디렉토리 구조 (Directory Structure)

아래는 대표적인 디렉토리 및 파일만 나열한 예시입니다. 실제 프로젝트에서 파일이 늘어나면 상황에 맞춰 **폴더**를 추가할 수 있습니다.

```
project/
├─ app/
│   ├─ main.py                  # FastAPI 엔트리포인트
│   ├─ core/                    # 공통(공용) 기능(환경 설정, 로깅, 보안 등)
│   │   ├─ config.py
│   │   ├─ db.py
│   │   ├─ exceptions.py
│   │   ├─ logging.py
│   │   └─ security.py
│   ├─ features/                # 주요 기능(Feature) 모음
│   │   ├─ code_execution/
│   │   │   ├─ api.py           # FastAPI 라우터
│   │   │   ├─ schemas.py       # Pydantic 모델
│   │   │   ├─ services.py      # 비즈니스 로직
│   │   │   └─ infrastructure/  # DB, 메시징(Kafka), 워커 등 기술 연동
│   │   └─ submissions/
│   │       ├─ api.py
│   │       ├─ schemas.py
│   │       ├─ services.py
│   │       └─ infrastructure/
│   └─ ...
├─ docs/
│   └─ architecture.md          # (바로 이 문서)
├─ tests/
│   └─ ...                      # 테스트 코드
└─ ...
```

### 주요 폴더/파일 설명

**main.py**:
- FastAPI 애플리케이션을 생성하고, 라우터/미들웨어/예외 핸들러 등을 등록

**core/**:
- 프로젝트 공통(전역) 설정, DB 연결, 로깅, 보안(인증/인가) 등
- 여러 기능에서 재사용되는 로직이나 유틸리티를 모아둠

**features/**:
- "기능(Feature)" 중심으로 폴더를 나눠, 각 기능별로 API, 스키마, 서비스(비즈니스 로직), 인프라 연동 등을 관리

**tests/**:
- 테스트 코드. 기능별 혹은 모듈별로 구조를 맞춰 작성

## 레이어와 의존성 규칙 (Layers & Dependency Rules)

본 프로젝트는 **엄격한 레이어드 아키텍처**를 전부 구현하진 않으나, 핵심 규칙은 다음과 같습니다:

### 1. core 폴더
- 여러 기능에서 공유되는 전역 로직
- "`core`가 `features`를 임포트하는" 것은 필요 시 가능하되, 반대로 "`features`에서 `core`를 임포트"하는 경우가 더 잦을 것입니다
- 핵심은 **순환 의존성**(core ↔ features)이 생기지 않도록 유의해야 합니다

### 2. features 폴더
- 주된 업무 로직(비즈니스 로직)이 위치
- 각 기능(예: code_execution, submissions)은 **독립적인 하위 모듈**처럼 운영
- 다른 기능 모듈을 직접 참조하기보다, 필요 시 API/이벤트 등을 통해 느슨하게 연동하는 방식을 선호합니다

### 3. infrastructure 폴더(기능 하위)
- DB, 메시지 큐(Kafka, RabbitMQ), 비동기 워커(Celery, RQ 등) 등의 **기술적인 의존**이 위치
- 비즈니스 로직(services.py)에서 인프라 세부 사항을 몰라도 되도록, infrastructure/ 레이어에서 캡슐화합니다

### 4. main(엔트리포인트)
- "`main` → `features`" 방향 의존은 괜찮지만, "`features` → `main`"은 금지
- 즉, main.py는 라우터 등록, 앱 실행 등 상위 레벨의 역할만 담당

추후 **Import Linter** 같은 도구로 "어떤 디렉토리가 어느 디렉토리를 임포트할 수 있는지" 규칙을 CI에서 검사하여 **아키텍처 일관성**을 유지할 수 있습니다.

## 기능(Feature) 기반 폴더 구성

### 1. 기능별 디렉토리
- 예: code_execution/, submissions/, billing/, users/ 등
- 각 폴더 내부에서 api.py(FastAPI 라우터), schemas.py(Pydantic), services.py(비즈니스 로직), infrastructure/(DB/메시징)를 모아둡니다

### 2. API 라우터
- "`api.py`"에서 APIRouter를 정의하고, main.py에서 include_router로 붙임
- "/v1/execute", "/v1/submissions" 등 엔드포인트들이 이 곳에서 작성

### 3. 스키마(schemas.py)
- 요청/응답에 쓰이는 Pydantic 모델을 정의
- 비즈니스 로직(services)와의 결합을 최소화하기 위해, 필요하면 DTO(내부 전용)와 구분하기도 함

## 도메인 로직과 인프라 분리

### services.py
- 핵심 비즈니스 규칙과 유즈케이스(Use Case)가 들어가는 부분
- 예: "코드를 실행한다", "채점을 진행한다" 등
- 인프라 의존(예: DB, 메시징)이 직접 들어가면 **테스트가 어려워지고** 복잡해지므로, 가능한 한 인터페이스나 헬퍼 함수를 통해 우회

### infrastructure/
- 실제 DB, 메시지 큐, 외부 API 연동 등 **기술 세부 사항**을 구현하는 곳
- 예: "Docker 컨테이너에서 코드를 실행", "Kafka producer/consumer 설정", "SQLAlchemy 모델/쿼리" 등
- 비즈니스 로직에서 이 폴더를 직접 참조하기보다, 주로 서비스를 통해 호출하게 설계

## 확장 포인트 & 향후 계획

### 1. 새로운 기능(Feature) 추가
- 예: "billing/" 폴더를 만들어 결제/과금 기능을 구현하면, api.py, schemas.py, services.py, infrastructure/를 동일한 패턴으로 구성
- "유저 관리" 기능을 "users/"에 두고, 인증/인가 로직을 core/security.py와 연계

### 2. 버전 분리
- API 버전을 늘려나갈 때(v1, v2)는 "api/v1/router.py", "api/v2/router.py" 등으로 폴더/파일을 분리하거나, 파일명에 버전을 붙여 관리