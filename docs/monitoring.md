# Monitoring

이 문서는 프로젝트의 모니터링, 로깅, 트레이싱을 다루며, 장애 대응과 성능 분석을 위한 기본 설정 및 권장 패턴을 안내합니다.

## 목차
1. [개요 (Overview)](#개요-overview)
2. [로깅 (Logging)](#로깅-logging)
3. [메트릭 수집 (Metrics & Prometheus)](#메트릭-수집-metrics--prometheus)
4. [분산 트레이싱 (Distributed Tracing)](#분산-트레이싱-distributed-tracing)
5. [알림 및 대시보드 (Alerts & Dashboards)](#알림-및-대시보드-alerts--dashboards)
6. [장애 대응 & 모범 사례 (Incident Response)](#장애-대응--모범-사례-incident-response)

---

## 개요 (Overview)

### 왜 모니터링이 필요한가?
- 운영 환경에서 예기치 못한 오류, 성능 저하, 과부하 등이 발생할 수 있음
- 빠르게 감지하고 대응하려면 로그/메트릭/트레이싱이 필수

### 목표:
1. 장애 시 원인 추적과 회복을 신속히
2. 지표(메트릭)를 바탕으로 성능 튜닝
3. 이상 패턴(에러율 급증, 응답 지연 등) 발견 시 자동 알림

---

## 로깅 (Logging)

### 1. 로깅 라이브러리
- 파이썬 표준 `logging` 모듈 또는 `structlog`, `loguru` 등을 사용할 수 있음
- 구조화 로그(JSON 형태) 또는 최소한의 일관된 포맷으로 로그를 남기면 파싱/분석에 유리

### 2. 구조화 로그 예시

```python
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def log_event(event_name, data=None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_name,
        "data": data or {}
    }
    logger.info(json.dumps(log_entry))
```

- 실제 운영 환경에서 `logger.info(...)`가 stdout으로 출력되면, 이를 ELK(Elastic Stack), Splunk, Datadog 같은 로그 수집 시스템에 보낼 수 있음

### 3. 로컬 vs 운영 환경
- **로컬**: 콘솔에 로그 출력, DEBUG 레벨까지 표시
- **운영**: 파일 또는 stdout(컨테이너 환경), INFO 또는 WARNING 이상만 출력, 구조화 로그 활성화
- Docker/Kubernetes 환경에서는 stdout으로 출력된 로그를 로깅 시스템이 수집하는 패턴이 일반적

---

## 메트릭 수집 (Metrics & Prometheus)

### 1. Prometheus와 FastAPI
- Prometheus는 HTTP 엔드포인트(`/metrics`)에서 메트릭을 수집
- 예: `prometheus_client` 파이썬 라이브러리를 이용해 카운터/히스토그램/게이지를 정의

```python
from prometheus_client import Counter, Histogram

request_count = Counter("request_count", "Count of requests")
request_latency = Histogram("request_latency_seconds", "Request latency")

def track_request():
    request_count.inc()
    with request_latency.time():
        # do something
```

### 2. FastAPI 엔드포인트 연동
- 별도의 라우터(`/metrics`)를 만들어 Prometheus가 스크랩할 수 있도록 설정

```python
from fastapi import FastAPI
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

### 3. 메트릭 예시
- API 호출 횟수(Counter)
- API 응답 시간(Histogram)
- 에러 발생 횟수(Counter)
- 사용 중 메모리, CPU 사용률(Exporters, 노드 익스포터 등)

---

## 분산 트레이싱 (Distributed Tracing)

### 1. 개념
- 여러 마이크로서비스(또는 내부 워커, 외부 API) 간의 요청 흐름을 Trace 식별자로 연결
- 장애나 성능 문제 시 **“어느 지점에서 병목 발생?”**을 시각적으로 파악 가능

### 2. 툴 선택
- Jaeger, Zipkin, OpenTelemetry 등이 대표적
- FastAPI와 연동해 Request → Downstream Calls 추적

### 3. 예시 (OpenTelemetry)

```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi
```

- 간단히 `opentelemetry-instrument` 명령이나 앱 내부에서 Tracer 설정 후,
- 서비스 간 `traceparent` 헤더를 전달 받아 연결

---

## 알림 및 대시보드 (Alerts & Dashboards)

### 1. Alertmanager / Grafana Alerts
- 특정 메트릭이 임계값을 초과하면(예: 에러율 5% 이상), Alertmanager가 슬랙/이메일/페이지어듀티로 알림
- Grafana Alerting(내장 기능)을 써서 “CPU > 90% 5분간 지속 시 알림” 등 세부 정책 설정 가능

### 2. 로그 기반 알림
- 구조화 로그를 ELK로 모으고, Kibana에서 특정 조건(에러 레벨이 100회 이상 발생) 시 경고
- Datadog, Splunk 등 다른 서비스도 비슷한 설정 가능

### 3. 대시보드
- Grafana나 Kibana에서 각종 차트, 패널로 현재 서비스 상태(트래픽, 응답 시간, 에러 추이 등)를 한눈에 확인
- 팀원들이 공용 대시보드 URL을 즐겨찾기 해두면, 장애 발생 시 빠르게 확인 가능

---

## 장애 대응 & 모범 사례 (Incident Response)

### 1. 장애 감지
- 알림 채널(슬랙/이메일/SMS)로 알림 수신
- 대시보드에서 에러율 급등 확인

### 2. 로그 및 트레이싱 분석
- 특정 요청(Trace ID)이나 특정 시간대(로그 타임스탬프)부터 문제 스택 추적

### 3. 원인 파악 & 롤백/패치
- 새 버전에만 오류가 발생하면, 일단 이전 버전으로 롤백하고 원인 분석
- 재현 가능하면 로컬/스테이징 환경에서 테스트

### 4. 사후 분석 & 문서화
- 재발 방지 대책 정립
- 모니터링 지표/알림 개선(“왜 이번 장애를 더 빨리 못 잡았나?”)

---

## 마무리
- 모니터링은 단순히 로그 몇 줄, 메트릭 몇 개를 찍는 게 아니라, 장애 이전/이후 전체 흐름을 추적하고 성능 개선을 지속하는 과정입니다.
- 팀 전체가 “로그 → 메트릭 → 트레이싱 → 알림 → 대응” 프로세스를 숙지하고, 문서화와 도구 운영을 주기적으로 점검해야 합니다.

### 도입 추천:
- Prometheus/Grafana (메트릭 및 대시보드)
- ELK Stack or Datadog (로그 수집/분석)
- Jaeger/Zipkin/OpenTelemetry (분산 트레이싱)

**Tip**: 규모가 작더라도, 최소한 기본 로깅과 메트릭(에러율, 요청 속도)만큼은 미리 구축해 두면 장애 시 큰 차이를 만들어 낼 수 있습니다.
