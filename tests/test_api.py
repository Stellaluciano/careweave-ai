from fastapi.testclient import TestClient

from apps.api.main import app


client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ask() -> None:
    resp = client.post("/ask", json={"question": "How do randomized clinical trials reduce bias?", "top_k": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert "request_id" in body
    assert "answer" in body
    assert "trace" in body
