"""Tests for Agent Engine Registry.

These tests verify the registry functionality without requiring
an actual connection to Vertex AI Agent Engine.
"""

from __future__ import annotations

import pytest

from agents.shared.agent_engine_registry import (
    AGENT_CONFIGS,
    AgentEngineConfig,
    AgentEngineError,
    AgentEngineRegistry,
    AgentNotFoundError,
    InvocationResult,
    get_registry,
    reset_registry,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def config():
    """Create a test configuration."""
    return AgentEngineConfig(
        project_id="test-project",
        location="us-central1",
        environment="test",
        resource_prefix="genesis-ngx",
    )


@pytest.fixture
def registry(config):
    """Create a registry instance for testing."""
    reset_registry()
    return AgentEngineRegistry(config=config)


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up after each test."""
    yield
    reset_registry()


# =============================================================================
# AgentEngineConfig Tests
# =============================================================================


class TestAgentEngineConfig:
    """Tests for AgentEngineConfig."""

    def test_default_values(self):
        """Should use default values when not specified."""
        config = AgentEngineConfig()
        assert config.location == "us-central1"
        assert config.default_timeout_seconds == 30.0
        assert config.max_retries == 3

    def test_custom_values(self, config):
        """Should use custom values when specified."""
        assert config.project_id == "test-project"
        assert config.location == "us-central1"
        assert config.environment == "test"


# =============================================================================
# Agent Configuration Tests
# =============================================================================


class TestAgentConfigs:
    """Tests for agent configuration data."""

    def test_all_13_agents_registered(self):
        """Should have all 13 agents registered."""
        expected_agents = {
            "genesis_x",
            "blaze",
            "sage",
            "atlas",
            "tempo",
            "wave",
            "stella",
            "metabol",
            "macro",
            "spark",
            "nova",
            "luna",
            "logos",
        }
        assert set(AGENT_CONFIGS.keys()) == expected_agents

    def test_pro_agents_have_higher_limits(self):
        """Pro model agents should have higher cost limits."""
        pro_agents = ["genesis_x", "logos"]
        flash_agents = ["blaze", "sage", "atlas", "tempo", "wave"]

        for agent_id in pro_agents:
            config = AGENT_CONFIGS[agent_id]
            assert config["max_cost_per_invoke"] == 0.05
            assert config["max_latency_ms"] == 6000

        for agent_id in flash_agents:
            config = AGENT_CONFIGS[agent_id]
            assert config["max_cost_per_invoke"] == 0.01
            assert config["max_latency_ms"] == 2000

    def test_all_agents_have_required_fields(self):
        """All agents should have required configuration fields."""
        required_fields = {"model", "max_latency_ms", "max_cost_per_invoke", "description"}

        for agent_id, config in AGENT_CONFIGS.items():
            for field in required_fields:
                assert field in config, f"Agent {agent_id} missing field {field}"


# =============================================================================
# AgentEngineRegistry Tests
# =============================================================================


class TestAgentEngineRegistry:
    """Tests for AgentEngineRegistry."""

    def test_get_agent_ids(self, registry):
        """Should return list of all agent IDs."""
        ids = registry.get_agent_ids()
        assert len(ids) == 13
        assert "blaze" in ids
        assert "genesis_x" in ids

    def test_get_agent_config_valid(self, registry):
        """Should return config for valid agent."""
        config = registry.get_agent_config("blaze")
        assert config["model"] == "gemini-2.5-flash"
        assert config["description"] == "Strength and hypertrophy specialist"

    def test_get_agent_config_invalid(self, registry):
        """Should raise error for invalid agent."""
        with pytest.raises(AgentNotFoundError) as exc_info:
            registry.get_agent_config("nonexistent")
        assert "nonexistent" in str(exc_info.value)

    def test_get_resource_name_format(self, registry):
        """Should return correctly formatted resource name."""
        name = registry.get_resource_name("blaze")
        expected = (
            "projects/test-project/"
            "locations/us-central1/"
            "reasoningEngines/genesis-ngx-blaze"
        )
        assert name == expected

    def test_get_resource_name_invalid_agent(self, registry):
        """Should raise error for invalid agent."""
        with pytest.raises(AgentNotFoundError):
            registry.get_resource_name("invalid_agent")

    def test_get_resource_id(self, registry):
        """Should return just the resource ID."""
        resource_id = registry.get_resource_id("sage")
        assert resource_id == "genesis-ngx-sage"

    def test_is_not_connected_without_credentials(self, registry):
        """Should not be connected without Vertex AI credentials."""
        # In test environment, we don't have real credentials
        assert not registry.is_connected


class TestInitMockFallbackPolicy:
    """Tests for mock fallback policy during client init."""

    def test_production_refuses_mock_fallback_without_adc(self, monkeypatch):
        """Production should fail fast if ADC is missing."""
        monkeypatch.delenv("AGENT_ENGINE_ALLOW_MOCK", raising=False)

        import google.auth
        from google.auth.exceptions import DefaultCredentialsError

        def _raise_default_credentials_error(*args, **kwargs):
            raise DefaultCredentialsError("no ADC configured")

        monkeypatch.setattr(google.auth, "default", _raise_default_credentials_error)

        config = AgentEngineConfig(
            project_id="test-project",
            location="us-central1",
            environment="production",
            resource_prefix="genesis-ngx",
        )

        with pytest.raises(AgentEngineError):
            AgentEngineRegistry(config=config)

    def test_development_allows_mock_fallback_without_adc(self, monkeypatch):
        """Development may fall back to mock mode if ADC is missing."""
        monkeypatch.delenv("AGENT_ENGINE_ALLOW_MOCK", raising=False)

        import google.auth
        from google.auth.exceptions import DefaultCredentialsError

        def _raise_default_credentials_error(*args, **kwargs):
            raise DefaultCredentialsError("no ADC configured")

        monkeypatch.setattr(google.auth, "default", _raise_default_credentials_error)

        config = AgentEngineConfig(
            project_id="test-project",
            location="us-central1",
            environment="development",
            resource_prefix="genesis-ngx",
        )

        registry = AgentEngineRegistry(config=config)
        assert not registry.is_connected


# =============================================================================
# InvocationResult Tests
# =============================================================================


class TestInvocationResult:
    """Tests for InvocationResult dataclass."""

    def test_to_dict(self):
        """Should convert to dictionary correctly."""
        result = InvocationResult(
            agent_id="blaze",
            session_id="session-123",
            response="Workout created",
            tokens_used=150,
            cost_usd=0.005,
            latency_ms=250.5,
            status="success",
        )
        data = result.to_dict()

        assert data["agent_id"] == "blaze"
        assert data["session_id"] == "session-123"
        assert data["response"] == "Workout created"
        assert data["tokens_used"] == 150
        assert data["cost_usd"] == 0.005
        assert data["latency_ms"] == 250.5
        assert data["status"] == "success"

    def test_default_values(self):
        """Should have correct default values."""
        result = InvocationResult(
            agent_id="test",
            session_id="s1",
            response="response",
        )
        assert result.events == []
        assert result.tokens_used == 0
        assert result.cost_usd == 0.0
        assert result.latency_ms == 0.0
        assert result.status == "success"


# =============================================================================
# Mock Invocation Tests
# =============================================================================


class TestMockInvocation:
    """Tests for mock invocation (when not connected to Agent Engine)."""

    @pytest.mark.asyncio
    async def test_mock_invoke_returns_result(self, registry):
        """Mock invoke should return a valid result."""
        result = await registry.invoke(
            agent_id="blaze",
            message="Create a workout",
            user_id="test-user",
        )

        assert result.agent_id == "blaze"
        assert result.status == "success"
        assert "[MOCK]" in result.response
        assert result.session_id is not None

    @pytest.mark.asyncio
    async def test_mock_invoke_invalid_agent(self, registry):
        """Mock invoke should raise error for invalid agent."""
        with pytest.raises(AgentNotFoundError):
            await registry.invoke(
                agent_id="nonexistent",
                message="Test",
                user_id="test-user",
            )

    @pytest.mark.asyncio
    async def test_mock_invoke_with_session(self, registry):
        """Mock invoke should preserve session ID."""
        result = await registry.invoke(
            agent_id="sage",
            message="Create nutrition plan",
            session_id="my-session-123",
            user_id="test-user",
        )

        assert result.session_id == "my-session-123"

    @pytest.mark.asyncio
    async def test_mock_invoke_includes_events(self, registry):
        """Mock invoke should include events."""
        result = await registry.invoke(
            agent_id="logos",
            message="Explain protein synthesis",
            user_id="test-user",
        )

        assert len(result.events) > 0
        assert result.events[0]["type"] == "mock"


# =============================================================================
# Singleton Tests
# =============================================================================


class TestRegistrySingleton:
    """Tests for the global registry singleton."""

    def test_get_registry_returns_same_instance(self):
        """get_registry should return the same instance."""
        reset_registry()
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2

    def test_reset_registry_clears_instance(self):
        """reset_registry should clear the singleton."""
        r1 = get_registry()
        reset_registry()
        r2 = get_registry()
        assert r1 is not r2

    def test_get_registry_with_custom_config(self):
        """get_registry should use custom config on first call."""
        reset_registry()
        config = AgentEngineConfig(project_id="custom-project")
        registry = get_registry(config=config)
        assert registry.config.project_id == "custom-project"


# =============================================================================
# Streaming Tests
# =============================================================================


class TestStreamingInvocation:
    """Tests for streaming invocation."""

    @pytest.mark.asyncio
    async def test_invoke_stream_yields_events(self, registry):
        """invoke_stream should yield events."""
        events = []
        async for event in registry.invoke_stream(
            agent_id="blaze",
            message="Test",
            user_id="test-user",
        ):
            events.append(event)

        assert len(events) > 0
        # In mock mode, should have mock and done events
        assert any(e.get("type") == "mock" for e in events)

    @pytest.mark.asyncio
    async def test_invoke_stream_invalid_agent(self, registry):
        """invoke_stream should raise error for invalid agent."""
        with pytest.raises(AgentNotFoundError):
            async for _ in registry.invoke_stream(
                agent_id="invalid",
                message="Test",
                user_id="test-user",
            ):
                pass
