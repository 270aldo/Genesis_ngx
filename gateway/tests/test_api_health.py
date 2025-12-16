"""Tests for health check endpoints."""

import pytest


def test_health_check(client):
    """Test /health endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_readiness_check(client):
    """Test /ready endpoint returns ready status."""
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_version_info(client):
    """Test /version endpoint returns version info."""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "environment" in data
    assert data["version"] == "1.0.0"
    # Environment may be "test" or "development" depending on load order
    assert data["environment"] in ["test", "development"]
