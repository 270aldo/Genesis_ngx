"""Tests para a2a_server."""

import pytest
from fastapi.testclient import TestClient

from agents.shared.a2a_server import A2AServer


class TestAgent(A2AServer):
    """Agente de prueba."""

    def __init__(self):
        card = {
            "id": "test-agent",
            "version": "1.0.0",
            "capabilities": ["test", "echo"],
            "limits": {
                "max_input_tokens": 1000,
                "max_output_tokens": 500,
                "max_latency_ms": 1000,
                "max_cost_per_invoke": 0.01,
            },
            "privacy": {"pii": False, "phi": False},
            "auth": {"method": "none"},
        }
        super().__init__(card)

    async def handle_method(self, method: str, params: dict):
        if method == "echo":
            return {"message": params.get("message")}
        if method == "add":
            a = params.get("a", 0)
            b = params.get("b", 0)
            return {"result": a + b}
        return {"error": "unknown_method"}

    async def handle_stream(self, method: str, params: dict):
        if method == "count":
            max_n = params.get("max", 5)
            for i in range(max_n):
                yield str(i)


@pytest.fixture
def client():
    """Fixture para TestClient."""
    agent = TestAgent()
    return TestClient(agent.app)


class TestA2AServer:
    """Tests para A2AServer."""

    def test_get_card(self, client):
        """Test endpoint /card."""
        response = client.get("/card")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-agent"
        assert data["version"] == "1.0.0"
        assert "test" in data["capabilities"]

    def test_healthz(self, client):
        """Test endpoint /healthz."""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_negotiate_success(self, client):
        """Test /negotiate con capacidades válidas."""
        response = client.post(
            "/negotiate",
            json={"capabilities": ["test"], "budget_usd": 0.01},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["accepted"] is True

    def test_invoke_echo(self, client):
        """Test /invoke con método echo."""
        response = client.post(
            "/invoke",
            headers={"X-Request-ID": "test-123", "X-Budget-USD": "0.01"},
            json={
                "jsonrpc": "2.0",
                "method": "echo",
                "params": {"message": "hello"},
                "id": "1",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["result"]["message"] == "hello"
        assert data["id"] == "1"

    def test_invoke_add(self, client):
        """Test /invoke con método add."""
        response = client.post(
            "/invoke",
            headers={"X-Budget-USD": "0.01"},
            json={
                "jsonrpc": "2.0",
                "method": "add",
                "params": {"a": 5, "b": 3},
                "id": "2",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["result"] == 8

    def test_invoke_invalid_jsonrpc(self, client):
        """Test con JSON-RPC inválido."""
        response = client.post(
            "/invoke",
            headers={"X-Budget-USD": "0.01"},
            json={
                "jsonrpc": "1.0",  # Versión incorrecta
                "method": "echo",
                "params": {},
                "id": "3",
            },
        )
        assert response.status_code == 400

    def test_invoke_budget_exceeded(self, client):
        """Test cuando el presupuesto es insuficiente."""
        response = client.post(
            "/invoke",
            headers={"X-Budget-USD": "0.001"},  # Menor que max_cost_per_invoke
            json={
                "jsonrpc": "2.0",
                "method": "echo",
                "params": {"message": "test"},
                "id": "4",
            },
        )
        assert response.status_code == 402
        data = response.json()
        assert data["error"]["code"] == -32001
        assert data["error"]["data"]["reason"] == "BUDGET_EXCEEDED"

    def test_invoke_invalid_request(self, client):
        """Test con request mal formado."""
        response = client.post(
            "/invoke",
            headers={"X-Budget-USD": "0.01"},
            json={"invalid": "request"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == -32600
        assert data["error"]["data"]["reason"] == "VALIDATION_ERROR"

    def test_invoke_stream(self, client):
        """Test /invoke/stream."""
        response = client.post(
            "/invoke/stream",
            json={
                "jsonrpc": "2.0",
                "method": "count",
                "params": {"max": 3},
                "id": "5",
            },
        )
        assert response.status_code == 200

        # Leer eventos SSE
        lines = response.text.strip().split("\n")
        events = [line.replace("data: ", "") for line in lines if line.startswith("data: ")]
        assert len(events) == 3
        assert events == ["0", "1", "2"]
