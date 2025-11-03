"""Configuración global de pytest y fixtures compartidos."""

import os
from typing import Generator

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> Generator[None, None, None]:
    """Configura el entorno de testing."""
    # Forzar modo test
    os.environ["TEST_MODE"] = "true"
    os.environ["ENVIRONMENT"] = "development"
    os.environ["DEBUG"] = "true"

    # Deshabilitar servicios externos por defecto
    os.environ.setdefault("MOCK_GEMINI", "true")
    os.environ.setdefault("MOCK_SUPABASE", "true")

    # Configurar variables mínimas requeridas
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "test-project")
    os.environ.setdefault("GEMINI_PROJECT_ID", "test-project")
    os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
    os.environ.setdefault("SUPABASE_ANON_KEY", "test-anon-key")
    os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
    os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-at-least-32-chars-long-for-security")

    # Logging silencioso en tests
    os.environ["LOG_LEVEL"] = "WARNING"

    yield

    # Cleanup después de todos los tests
    pass


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock de settings para tests."""
    from agents.shared.config import Environment, Settings

    test_settings = Settings(
        environment=Environment.DEVELOPMENT,
        google_cloud_project="test-project",
        debug=True,
        test_mode=True,
        mock_gemini=True,
        mock_supabase=True,
    )

    # Patchear get_settings
    monkeypatch.setattr("agents.shared.config.get_settings", lambda: test_settings)
    return test_settings


@pytest.fixture
def sample_agent_card():
    """Agent Card de ejemplo para tests."""
    return {
        "id": "test-agent",
        "version": "1.0.0",
        "capabilities": ["test", "mock"],
        "limits": {
            "max_input_tokens": 10000,
            "max_output_tokens": 2000,
            "max_latency_ms": 5000,
            "max_cost_per_invoke": 0.05,
        },
        "privacy": {
            "pii": False,
            "phi": False,
            "data_retention_days": 90,
        },
        "auth": {
            "method": "oidc",
            "audience": "test-agent",
        },
    }


@pytest.fixture
def sample_conversation_id():
    """UUID de conversación de ejemplo."""
    import uuid
    return uuid.uuid4()


@pytest.fixture
def sample_user_id():
    """UUID de usuario de ejemplo."""
    import uuid
    return uuid.uuid4()
