from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_forbidden_module_import() -> None:
    response = client.post("/v1/execute", json={"code": "import os\nprint('Hello')"})
    assert response.status_code == 400
    data = response.json()
    assert data["error_type"] == "security"
    assert "os" in data["forbidden_item"]


def test_forbidden_function() -> None:
    response = client.post("/v1/execute", json={"code": "eval('print(123)')"})
    assert response.status_code == 400
    data = response.json()
    assert data["error_type"] == "security"
    assert data["forbidden_item"] == "eval"


def test_syntax_error() -> None:
    response = client.post("/v1/execute", json={"code": "print('Hello' "})
    assert response.status_code == 400
    data = response.json()
    assert data["error_type"] == "syntax"


def test_runtime_error() -> None:
    response = client.post("/v1/execute", json={"code": "1/0"})
    assert response.status_code == 500
    data = response.json()
    assert data["error_type"] == "runtime"


def test_allowed_code() -> None:
    response = client.post("/v1/execute", json={"code": "print('Allowed')"})
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "Allowed\n"
