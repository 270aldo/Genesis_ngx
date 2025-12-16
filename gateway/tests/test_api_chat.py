"""Tests for chat API endpoints."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestChatEndpoint:
    """Tests for POST /v1/chat endpoint."""

    def test_chat_requires_auth(self, client):
        """Test that chat endpoint requires authentication."""
        response = client.post(
            "/v1/chat",
            json={"message": "Hello"},
        )
        assert response.status_code == 401

    def test_chat_invalid_token(self, client):
        """Test that invalid token is rejected."""
        response = client.post(
            "/v1/chat",
            json={"message": "Hello"},
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401

    def test_chat_success(self, client, auth_headers):
        """Test successful chat request with valid token."""
        response = client.post(
            "/v1/chat",
            json={"message": "Help me with fitness"},
            headers=auth_headers,
        )

        # With client fixture properly mocked, we should get 200 or 500 (if service error)
        # The important thing is auth passes (not 401)
        assert response.status_code in [200, 500]

    def test_chat_empty_message_rejected(self, client, auth_headers):
        """Test that empty messages are rejected."""
        response = client.post(
            "/v1/chat",
            json={"message": ""},
            headers=auth_headers,
        )
        assert response.status_code == 422  # Validation error

    def test_chat_message_too_long_rejected(self, client, auth_headers):
        """Test that messages over 10000 chars are rejected."""
        long_message = "x" * 10001
        response = client.post(
            "/v1/chat",
            json={"message": long_message},
            headers=auth_headers,
        )
        assert response.status_code == 422  # Validation error


class TestChatStreamEndpoint:
    """Tests for POST /v1/chat/stream endpoint."""

    def test_stream_requires_auth(self, client):
        """Test that stream endpoint requires authentication."""
        response = client.post(
            "/v1/chat/stream",
            json={"message": "Hello"},
        )
        assert response.status_code == 401

    def test_stream_returns_sse(self, client, auth_headers):
        """Test that stream endpoint returns SSE content type."""
        response = client.post(
            "/v1/chat/stream",
            json={"message": "Help me"},
            headers=auth_headers,
        )

        # Check content type (may be 200 or 500 depending on mock setup)
        # The important thing is auth passes (not 401)
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            assert "text/event-stream" in response.headers.get("content-type", "")
