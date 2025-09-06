import os
import sys
from fastapi.testclient import TestClient

# Ensure project root is on sys.path for imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.main import app


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_query_empty_index():
    r = client.post("/query", json={"query": "payment failure timeout", "top_k": 3})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert isinstance(data["sources"], list)
    # With empty DB, should return zero sources
    assert len(data["sources"]) == 0
