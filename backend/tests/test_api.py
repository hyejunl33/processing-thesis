import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DB_PATH = Path("/tmp/opencode/mathlens_test.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DB_PATH.unlink(missing_ok=True)
os.environ["DATABASE_PATH"] = str(DB_PATH)
os.environ["LLM_MODE"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert body["llm"]["mode"] == "mock"


def test_full_pipeline(client):
    text = "사과가 귤보다 3개 더 많습니다. 귤은 5개입니다. 사과는 몇 개일까요?"

    parsed = client.post("/api/problems/parse", json={"text": text})
    assert parsed.status_code == 200, parsed.text
    problem = parsed.json()
    assert problem["unknown"] == "q_unknown"

    built = client.post("/api/models/build", json=problem)
    assert built.status_code == 200, built.text
    model = built.json()
    assert model["unknown_bar"] == "q_unknown"
    unknown_bar = next(b for b in model["bars"] if b["id"] == "q_unknown")
    assert unknown_bar["value"] is None  # never leak the numeric answer
    assert sum(s["value"] for s in unknown_bar["segments"]) == 8

    hint = client.post(
        "/api/hints",
        json={"problem": problem, "model": model, "student_state": {"answer": 0}, "history": []},
    )
    assert hint.status_code == 200
    assert hint.json()["text"]
    assert "8" not in hint.json()["text"]

    check = client.post("/api/check", json={"problem": problem, "answer": 8})
    assert check.status_code == 200
    assert check.json()["correct"] is True

    event = client.post(
        "/api/events",
        json={
            "session_id": "test-session",
            "problem_id": problem["id"],
            "ts": 1763000000,
            "type": "check",
            "target": "q_unknown",
            "payload": {"answer": 8, "correct": True},
        },
    )
    assert event.status_code == 200

    report = client.get("/api/sessions/test-session/report")
    assert report.status_code == 200
    body = report.json()
    assert body["count"] == 1
    assert body["types"]["check"] == 1
