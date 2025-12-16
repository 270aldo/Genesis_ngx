"""Pytest fixtures for Gateway tests."""

from __future__ import annotations

import os
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# Set test environment before importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "test-anon-key"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-service-role-key"
os.environ["SUPABASE_JWT_SECRET"] = "test-jwt-secret-at-least-32-chars-long"


@pytest.fixture
def mock_settings():
    """Mock gateway settings."""
    from gateway.config import GatewaySettings

    return GatewaySettings(
        environment="test",
        debug=True,
        supabase_url="https://test.supabase.co",
        supabase_anon_key="test-anon-key",
        supabase_service_role_key="test-service-role-key",
        supabase_jwt_secret="test-jwt-secret-at-least-32-chars-long",
    )


@pytest.fixture
def mock_registry():
    """Mock Agent Engine Registry."""
    registry = MagicMock()
    registry.is_connected = False

    # Mock invoke method
    async def mock_invoke(*args, **kwargs):
        return MagicMock(
            agent_id="genesis_x",
            session_id="test-session",
            response="Mock response from genesis_x",
            tokens_used=100,
            cost_usd=0.001,
            latency_ms=150.0,
            status="success",
        )

    registry.invoke = AsyncMock(side_effect=mock_invoke)

    # Mock invoke_stream method
    async def mock_invoke_stream(*args, **kwargs):
        yield {"type": "chunk", "content": "Mock "}
        yield {"type": "chunk", "content": "streaming "}
        yield {"type": "chunk", "content": "response"}
        yield {"type": "done", "tokens_used": 50, "cost_usd": 0.0005}

    registry.invoke_stream = mock_invoke_stream

    return registry


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    client = MagicMock()

    # Mock RPC calls - updated to use gateway-specific RPCs
    def mock_rpc(name, params):
        result = MagicMock()
        if name == "user_create_conversation":
            result.data = "conv-123"
        elif name == "gateway_append_user_message":
            result.data = "msg-user-123"
        elif name == "gateway_append_agent_message":
            result.data = "msg-agent-123"
        elif name == "user_archive_conversation":
            result.data = True
        else:
            result.data = None
        result.execute = MagicMock(return_value=result)
        return result

    client.rpc = MagicMock(side_effect=mock_rpc)

    # Mock table queries
    def mock_table(name):
        table = MagicMock()
        table.select = MagicMock(return_value=table)
        table.eq = MagicMock(return_value=table)
        table.order = MagicMock(return_value=table)
        table.range = MagicMock(return_value=table)
        table.single = MagicMock(return_value=table)
        table.insert = MagicMock(return_value=table)
        table.update = MagicMock(return_value=table)

        result = MagicMock()
        result.data = []
        result.count = 0
        table.execute = MagicMock(return_value=result)
        return table

    client.table = MagicMock(side_effect=mock_table)

    return client


@pytest.fixture
def valid_jwt_token():
    """Generate a valid JWT token for testing."""
    import jwt
    from datetime import datetime, timedelta

    payload = {
        "sub": "user-123",
        "email": "test@example.com",
        "role": "authenticated",
        "aud": "authenticated",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "app_metadata": {"subscription_tier": "free"},
    }

    return jwt.encode(
        payload,
        "test-jwt-secret-at-least-32-chars-long",
        algorithm="HS256",
    )


@pytest.fixture
def auth_headers(valid_jwt_token):
    """Authorization headers with valid JWT."""
    return {"Authorization": f"Bearer {valid_jwt_token}"}


@pytest.fixture
def client(mock_registry, mock_supabase) -> Generator[TestClient, None, None]:
    """Create test client with mocked dependencies."""
    with patch("gateway.dependencies.get_agent_registry", return_value=mock_registry):
        with patch("supabase.create_client", return_value=mock_supabase):
            from gateway.main import app

            with TestClient(app) as test_client:
                yield test_client


@pytest.fixture
def async_client(mock_registry, mock_supabase):
    """Create async test client for async tests."""
    from httpx import ASGITransport, AsyncClient

    with patch("gateway.dependencies.get_agent_registry", return_value=mock_registry):
        with patch("supabase.create_client", return_value=mock_supabase):
            from gateway.main import app

            return AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            )
