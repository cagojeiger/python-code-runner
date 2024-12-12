# python-code-runner

A minimal starting point for a sandboxed code execution environment.

## Run Locally

1. Install dependencies:
```bash
poetry install
```
2.	Run server:
```bash
poetry run uvicorn app.main:app --reload
```
3.	Test:
```bash
curl -X POST http://127.0.0.1:8000/v1/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"print(\"Hello World!\")"}'
```
Expected:
```json
{"result":"Hello World!\n"}
```
