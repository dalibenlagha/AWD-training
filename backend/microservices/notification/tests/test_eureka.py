"""Tests of the Eureka bonus (GET /health and GET /api/notifications/candidates/{id}).

No Eureka server is needed: TestClient(app) is not used as a context manager, so the lifespan
(Eureka registration) does not run, and the Eureka client is replaced by a fake one when needed.
Run with: pytest
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app import eureka
from app.main import app

client = TestClient(app)


class FakeCandidat(BaseHTTPRequestHandler):
    """A tiny HTTP server that plays the role of the candidat microservice."""

    def do_GET(self):
        if self.path == "/api/candidates/1":
            status, body = 200, {"id": 1, "firstname": "Badia", "lastname": "Abouhdid"}
        else:
            status, body = 404, {"status": 404, "detail": "Candidate not found"}
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):  # keep the test output clean
        pass


@pytest.fixture
def candidat_in_eureka(monkeypatch):
    """Starts a fake candidat and a fake Eureka client whose registry contains it."""
    server = HTTPServer(("127.0.0.1", 0), FakeCandidat)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]

    instance = SimpleNamespace(ipAddr="127.0.0.1", port=SimpleNamespace(port=port), status="UP")
    application = SimpleNamespace(up_instances=[instance])
    fake_client = SimpleNamespace(applications=SimpleNamespace(get_application=lambda name: application))
    monkeypatch.setattr(eureka.eureka_client, "get_client", lambda: fake_client)

    yield f"http://127.0.0.1:{port}"
    server.shutdown()


def test_health_returns_up():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "UP"}


def test_no_candidat_in_eureka_returns_503():
    res = client.get("/api/notifications/candidates/1")
    assert res.status_code == 503
    assert "CANDIDAT" in res.json()["detail"]


def test_candidate_found_through_eureka(candidat_in_eureka):
    res = client.get("/api/notifications/candidates/1")
    assert res.status_code == 200
    assert res.json()["servedBy"] == candidat_in_eureka
    assert res.json()["candidate"]["id"] == 1


def test_unknown_candidate_returns_the_404_of_candidat(candidat_in_eureka):
    res = client.get("/api/notifications/candidates/2")
    assert res.status_code == 404


def test_invalid_id_returns_422():
    assert client.get("/api/notifications/candidates/abc").status_code == 422
